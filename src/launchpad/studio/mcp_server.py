"""Optional, bounded STDIO MCP bridge for Launchpad receipts.

This bridge is deliberately not a fresh OmegaClaw executor. It is a local
consultation surface that requires the verified Lighthouse proof first.
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
MAX_TEXT = 500
MAX_ID = 96
STATUSES = {"observed", "missing", "unknown"}


def _error(code: int, message: str, request_id: Any = None) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _ok(result: Any, request_id: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _tools() -> list[Dict[str, Any]]:
    return [
        {
            "name": "omega.reason",
            "description": "Consult the verified Lighthouse teaching evidence through a deterministic local Launchpad evaluator. This does not run OmegaClaw again or authorize an action.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string", "description": "The Lighthouse workspace slug."},
                    "question": {"type": "string", "description": "A bounded question about the recorded lesson."},
                    "consultation": {"type": "object", "description": "Optional self-reported claims/facts packet for deterministic conflict and missing-fact checks."},
                },
                "required": ["workspace_id", "question"],
                "additionalProperties": False,
            },
        },
        {
            "name": "omega.get_receipt",
            "description": "Read one receipt previously created by omega.reason using its logical receipt ID.",
            "inputSchema": {"type": "object", "properties": {"receipt_id": {"type": "string"}}, "required": ["receipt_id"], "additionalProperties": False},
        },
    ]


class LocalMCP:
    def __init__(self, project_root: Path):
        self.project_root = project_root.expanduser().resolve()
        self.artifacts = StudioArtifacts(self.project_root)
        self.receipts_root = self.project_root / ".launchpad" / "studio" / "runs" / "mcp"

    def _verified_proof(self) -> Dict[str, Any]:
        status = self.artifacts.status()
        if status.get("lighthouse", {}).get("state") != "verified":
            raise ValueError("A verified Lighthouse proof is required before using the optional bridge.")
        payload = json.loads(self.artifacts.artifact("lighthouse-proof")["content"])
        if not isinstance(payload, dict):
            raise ValueError("The Lighthouse proof artifact is invalid.")
        return payload

    def _workspace(self, workspace_id: str) -> Path:
        if workspace_id == "lighthouse-in-the-fog":
            return self.project_root / "examples" / "lighthouse-in-the-fog"
        if SLUG_PATTERN.fullmatch(workspace_id) is None:
            raise ValueError("workspace_id must be a lowercase local slug.")
        root = self.project_root / ".launchpad" / "studio" / "workspaces"
        destination = root / workspace_id
        if destination.parent != root or not destination.is_dir() or destination.is_symlink():
            raise ValueError("The requested local workspace does not exist.")
        return destination

    @staticmethod
    def _text(value: Any, field: str, maximum: int = MAX_TEXT) -> str:
        if not isinstance(value, str) or not value.strip() or len(value) > maximum or any(ord(char) < 32 for char in value):
            raise ValueError("%s must be a non-empty printable string of at most %d characters." % (field, maximum))
        return value

    def _trace(self, packet: Any) -> Dict[str, Any]:
        if not isinstance(packet, dict) or set(packet) != {"case_id", "rule", "claims", "facts", "forbidden_actions"}:
            raise ValueError("consultation must contain only case_id, rule, claims, facts, and forbidden_actions.")
        case_id = self._text(packet["case_id"], "case_id")
        if SLUG_PATTERN.fullmatch(case_id) is None:
            raise ValueError("case_id must be a lowercase local slug.")
        rule = self._text(packet["rule"], "rule")
        claims = packet["claims"]
        if not isinstance(claims, list) or not 1 <= len(claims) <= 8:
            raise ValueError("claims must contain one to eight entries.")
        normalized_claims = []
        positions = set()
        for claim in claims:
            if not isinstance(claim, dict) or set(claim) != {"agent_id", "position", "evidence_ids"}:
                raise ValueError("Each claim must contain agent_id, position, and evidence_ids.")
            agent = self._text(claim["agent_id"], "claim.agent_id", 64)
            position = self._text(claim["position"], "claim.position", 64)
            evidence = claim["evidence_ids"]
            if not isinstance(evidence, list) or not 1 <= len(evidence) <= 8:
                raise ValueError("claim.evidence_ids must contain one to eight IDs.")
            evidence_ids = [self._text(item, "evidence_id", MAX_ID) for item in evidence]
            normalized_claims.append({"agent_id": agent, "position": position, "evidence_ids": evidence_ids})
            positions.add(position)
        facts = packet["facts"]
        if not isinstance(facts, list) or len(facts) > 16:
            raise ValueError("facts must contain zero to sixteen entries.")
        normalized_facts = []
        missing = []
        seen = set()
        for fact in facts:
            if not isinstance(fact, dict) or set(fact) != {"fact_id", "status", "evidence_id"}:
                raise ValueError("Each fact must contain fact_id, status, and evidence_id.")
            fact_id = self._text(fact["fact_id"], "fact_id")
            if fact_id in seen or fact["status"] not in STATUSES:
                raise ValueError("Facts must use unique IDs and observed, missing, or unknown status.")
            seen.add(fact_id)
            evidence_id = self._text(fact["evidence_id"], "evidence_id", MAX_ID)
            normalized_facts.append({"fact_id": fact_id, "status": fact["status"], "evidence_id": evidence_id})
            if fact["status"] in {"missing", "unknown"}:
                missing.append(fact_id)
        actions = packet["forbidden_actions"]
        if not isinstance(actions, list) or len(actions) > 8:
            raise ValueError("forbidden_actions must contain zero to eight entries.")
        normalized_actions = [self._text(item, "forbidden_action", 64) for item in actions]
        conflicts = ["recorded positions disagree: " + " versus ".join(sorted(positions))] if len(positions) > 1 else []
        recommendation = "human_review_required" if conflicts or missing else "recorded_observation"
        return {
            "mode": "bounded_general_consultation",
            "case_id": case_id,
            "rulebook": {"id": case_id, "human_rule": rule, "executable_evaluation": "deterministic conflict and missing-fact checks only"},
            "recorded_claims": normalized_claims,
            "recorded_facts": normalized_facts,
            "conflicts": conflicts,
            "missing_information": missing,
            "recommendation": recommendation,
            "forbidden_actions": normalized_actions,
        }

    def reason(self, arguments: Any) -> Dict[str, Any]:
        if not isinstance(arguments, dict) or set(arguments) - {"workspace_id", "question", "consultation"} or not {"workspace_id", "question"}.issubset(arguments):
            raise ValueError("omega.reason requires workspace_id and question.")
        workspace_id = self._text(arguments["workspace_id"], "workspace_id", 63)
        question = self._text(arguments["question"], "question", MAX_QUESTION_LENGTH)
        self._workspace(workspace_id)
        proof = self._verified_proof()
        trace = self._trace(arguments["consultation"]) if "consultation" in arguments else None
        receipt_id = "mcp-" + uuid.uuid4().hex
        self.receipts_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.receipts_root.chmod(0o700)
        receipt = {
            "receipt_id": receipt_id,
            "workspace_id": workspace_id,
            "question": question,
            "answer": trace["recommendation"] if trace else proof.get("conclusion"),
            "basis": {
                "current_evaluation": "deterministic local Launchpad bridge",
                "real_omegaclaw_run_for_this_consultation": False,
                "prior_omegaclaw_integration_proof_required": True,
                "external_facts_validated": False,
                "synthetic_only": True,
                "human_approval_required": True,
            },
            "limitations": [
                "Claims and facts are self-reported local input; this bridge does not validate them externally.",
                "This bridge does not start a provider, rerun OmegaClaw, execute shell, or authorize an action.",
            ],
        }
        if trace:
            receipt["decision_trace"] = trace
        path = self.receipts_root / (receipt_id + ".json")
        with path.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
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
        payload = json.loads(path.read_text(encoding="utf-8"))
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
            return None
        if method == "initialize":
            return _ok({"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "omegaclaw-launchpad-local", "version": "0.3.0"}}, request_id)
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
    parser = argparse.ArgumentParser(description="Run the optional local Launchpad MCP bridge over STDIO.")
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
