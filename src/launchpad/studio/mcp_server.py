"""A bounded, local STDIO MCP bridge for the Studio evidence.

The bridge is deliberately not an OmegaClaw executor.  It consults the
verified, synthetic factory-fault lesson and returns a new local receipt.  It
has no shell, network, provider, or arbitrary-file capability.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any, IO, Dict, Optional

from .artifacts import StudioArtifacts


SLUG_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,62}\Z")
RECEIPT_PATTERN = re.compile(r"mcp-[0-9a-f]{32}\Z")
MAX_QUESTION_LENGTH = 1000


def _error(code: int, message: str, request_id: Any = None) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _ok(result: Any, request_id: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _tools() -> list[Dict[str, Any]]:
    return [
        {
            "name": "omega.reason",
            "description": "Consult the verified synthetic factory-fault lesson and record a local receipt. This never runs an external action.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string", "description": "A local Studio workspace slug, or factory-fault."},
                    "question": {"type": "string", "description": "A question about the published lesson."},
                },
                "required": ["workspace_id", "question"],
                "additionalProperties": False,
            },
        },
        {
            "name": "omega.get_receipt",
            "description": "Read one receipt previously created by omega.reason using its logical receipt ID.",
            "inputSchema": {
                "type": "object",
                "properties": {"receipt_id": {"type": "string"}},
                "required": ["receipt_id"],
                "additionalProperties": False,
            },
        },
    ]


class LocalMCP:
    def __init__(self, project_root: Path):
        self.project_root = project_root.expanduser().resolve()
        self.artifacts = StudioArtifacts(self.project_root)
        self.receipts_root = self.project_root / ".launchpad" / "studio" / "runs" / "mcp"

    def _verified_factory_proof(self) -> Dict[str, Any]:
        state = self.artifacts.status()["factory_fault"]
        if state["state"] != "verified":
            raise ValueError("The factory-fault lesson has no verified local OmegaClaw proof yet.")
        try:
            payload = json.loads(self.artifacts.artifact("factory-proof")["content"])
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError) as error:
            raise ValueError("The factory-fault proof artifact is unavailable.") from error
        if not isinstance(payload, dict):
            raise ValueError("The factory-fault proof artifact is invalid.")
        return payload

    def _workspace(self, workspace_id: str) -> Path:
        if workspace_id == "factory-fault":
            return self.project_root / "templates" / "factory-fault"
        if SLUG_PATTERN.fullmatch(workspace_id) is None:
            raise ValueError("workspace_id must be a lowercase local Studio slug.")
        root = self.project_root / ".launchpad" / "studio" / "workspaces"
        destination = root / workspace_id
        if destination.parent != root or not destination.is_dir() or destination.is_symlink():
            raise ValueError("The requested local Studio workspace does not exist.")
        return destination

    def reason(self, arguments: Any) -> Dict[str, Any]:
        if not isinstance(arguments, dict) or set(arguments) != {"workspace_id", "question"}:
            raise ValueError("omega.reason requires exactly workspace_id and question.")
        workspace_id = arguments["workspace_id"]
        question = arguments["question"]
        if not isinstance(workspace_id, str) or SLUG_PATTERN.fullmatch(workspace_id) is None:
            raise ValueError("workspace_id must be a lowercase local Studio slug.")
        if not isinstance(question, str) or not question.strip() or len(question) > MAX_QUESTION_LENGTH:
            raise ValueError("question must be a non-empty string of at most 1000 characters.")
        self._workspace(workspace_id)
        proof = self._verified_factory_proof()
        receipt_id = "mcp-" + uuid.uuid4().hex
        self.receipts_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.receipts_root.chmod(0o700)
        receipt = {
            "receipt_id": receipt_id,
            "workspace_id": workspace_id,
            "question": question,
            "answer": proof["conclusion"],
            "basis": {
                "template": "factory-fault",
                "facts": proof.get("facts", []),
                "runtime": proof.get("runtime"),
                "provider": proof.get("provider"),
                "channel": proof.get("channel"),
                "metta_skill_observed": proof.get("metta_skill_observed"),
                "nal_stv_observed_in_loop": proof.get("nal_stv_observed_in_loop"),
                "synthetic_only": True,
                "human_approval_required": True,
            },
            "disclaimer": "This is a synthetic lesson result, not a diagnosis, causal claim, external-data validation, or action authorization.",
        }
        path = self.receipts_root / (receipt_id + ".json")
        encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        try:
            with path.open("x", encoding="utf-8") as stream:
                stream.write(encoded)
        except FileExistsError as error:
            raise ValueError("The generated receipt ID already exists; retry the consultation.") from error
        path.chmod(0o600)
        return receipt

    def get_receipt(self, arguments: Any) -> Dict[str, Any]:
        if not isinstance(arguments, dict) or set(arguments) != {"receipt_id"}:
            raise ValueError("omega.get_receipt requires exactly receipt_id.")
        receipt_id = arguments["receipt_id"]
        if not isinstance(receipt_id, str) or RECEIPT_PATTERN.fullmatch(receipt_id) is None:
            raise ValueError("receipt_id is not a local MCP receipt ID.")
        path = self.receipts_root / (receipt_id + ".json")
        if path.parent != self.receipts_root or path.is_symlink() or not path.is_file():
            raise ValueError("The requested receipt does not exist.")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("The requested receipt is unreadable.") from error
        if not isinstance(payload, dict):
            raise ValueError("The requested receipt is invalid.")
        return payload

    def dispatch(self, request: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            return _error(-32600, "Invalid JSON-RPC request.", request.get("id") if isinstance(request, dict) else None)
        request_id = request.get("id")
        method = request.get("method")
        if not isinstance(method, str):
            return _error(-32600, "The request method is required.", request_id)
        if "id" not in request:
            if method in {"notifications/initialized", "notifications/cancelled"}:
                return None
            return None
        if method == "initialize":
            return _ok({"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "omegaclaw-launchpad-local", "version": "0.2.0"}}, request_id)
        if method == "ping":
            return _ok({}, request_id)
        if method == "tools/list":
            return _ok({"tools": _tools()}, request_id)
        if method == "tools/call":
            params = request.get("params")
            if not isinstance(params, dict) or params.get("name") not in {"omega.reason", "omega.get_receipt"}:
                return _error(-32602, "Unknown MCP tool.", request_id)
            try:
                result = self.reason(params.get("arguments")) if params["name"] == "omega.reason" else self.get_receipt(params.get("arguments"))
            except ValueError as error:
                return _ok({"isError": True, "content": [{"type": "text", "text": str(error)}]}, request_id)
            return _ok({"content": [{"type": "text", "text": json.dumps(result, sort_keys=True)}], "structuredContent": result}, request_id)
        return _error(-32601, "Method not found.", request_id)


def main(argv: Optional[list[str]] = None, stdin: Optional[IO[str]] = None, stdout: Optional[IO[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local OmegaClaw Launchpad MCP bridge over STDIO.")
    parser.add_argument("--workspace", default=".", type=Path, help="Launchpad project root")
    args = parser.parse_args(argv)
    bridge = LocalMCP(args.workspace)
    input_stream = stdin or sys.stdin
    output_stream = stdout or sys.stdout
    for line in input_stream:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            response = bridge.dispatch(request)
        except json.JSONDecodeError:
            response = _error(-32700, "Invalid JSON.")
        if response is not None:
            output_stream.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            output_stream.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
