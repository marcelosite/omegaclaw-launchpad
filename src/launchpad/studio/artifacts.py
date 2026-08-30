"""Safe, allowlisted artifact discovery for Studio V2."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from ..config import UPSTREAM_COMMIT


MAX_ARTIFACT_BYTES = 512 * 1024
WORKSPACE_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,62}\Z")


@dataclass(frozen=True)
class ArtifactSpec:
    logical_name: str
    relative_path: tuple[str, ...]
    content_type: str
    root: str


ARTIFACT_SPECS = {
    "preflight": ArtifactSpec("preflight", (".launchpad", "studio", "preflight.json"), "application/json", "workspace"),
    "mcp-check": ArtifactSpec("mcp-check", (".launchpad", "studio", "mcp-check.json"), "application/json", "workspace"),
    "lighthouse-proof": ArtifactSpec("lighthouse-proof", ("omega-proof.json",), "application/json", "run"),
    "lighthouse-receipt": ArtifactSpec("lighthouse-receipt", ("receipt.md",), "text/markdown", "run"),
    "example-readme": ArtifactSpec("example-readme", ("README.md",), "text/markdown", "example"),
    "example-story": ArtifactSpec("example-story", ("story.md",), "text/markdown", "example"),
    "example-claims": ArtifactSpec("example-claims", ("claims.json",), "application/json", "example"),
    "example-facts": ArtifactSpec("example-facts", ("facts.json",), "application/json", "example"),
    "example-update": ArtifactSpec("example-update", ("verified-update.json",), "application/json", "example"),
    "example-runtime-bulletin": ArtifactSpec("example-runtime-bulletin", ("runtime-bulletin.txt",), "text/plain", "example"),
    "example-rules": ArtifactSpec("example-rules", ("rules.md",), "text/markdown", "example"),
    "example-reasoning": ArtifactSpec("example-reasoning", ("reasoning.metta",), "text/plain", "example"),
    "example-tests": ArtifactSpec("example-tests", ("tests.json",), "application/json", "example"),
    "example-receipt": ArtifactSpec("example-receipt", ("example-receipt.md",), "text/markdown", "example"),
    "example-workspace": ArtifactSpec("example-workspace", ("workspace.json",), "application/json", "example"),
}


class ArtifactNotFound(FileNotFoundError):
    pass


class UnknownArtifact(ValueError):
    pass


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _read_json(path: Path) -> Optional[Mapping[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


class StudioArtifacts:
    """Resolve only known Studio artifacts under one repository checkout."""

    def __init__(self, workspace: Path):
        self.workspace = workspace.expanduser().resolve()
        self.example_root = self.workspace / "examples" / "lighthouse-in-the-fog"
        self.run_root = self.workspace / ".launchpad" / "studio" / "runs" / "lighthouse-in-the-fog"

    def _root(self, name: str) -> Path:
        spec = ARTIFACT_SPECS[name]
        return {"workspace": self.workspace, "example": self.example_root, "run": self.run_root}[spec.root]

    def _path_for(self, logical_name: str) -> Path:
        try:
            spec = ARTIFACT_SPECS[logical_name]
        except KeyError as error:
            raise UnknownArtifact("unknown Studio artifact") from error
        return self._root(logical_name).joinpath(*spec.relative_path)

    def _safe_existing_file(self, candidate: Path, root: Path) -> Path:
        try:
            resolved_root = root.resolve(strict=True)
            resolved_candidate = candidate.resolve(strict=True)
        except OSError as error:
            raise ArtifactNotFound("artifact is not available") from error
        if not _inside(resolved_root, self.workspace) or not _inside(resolved_candidate, resolved_root):
            raise ArtifactNotFound("artifact is not available")
        try:
            relative = candidate.relative_to(root)
        except ValueError as error:
            raise ArtifactNotFound("artifact is not available") from error
        current = root
        for part in relative.parts:
            if current.is_symlink():
                raise ArtifactNotFound("artifact is not available")
            current = current / part
        if current.is_symlink() or not resolved_candidate.is_file():
            raise ArtifactNotFound("artifact is not available")
        if resolved_candidate.stat().st_size > MAX_ARTIFACT_BYTES:
            raise ArtifactNotFound("artifact is not available")
        return resolved_candidate

    def artifact(self, logical_name: str) -> Dict[str, str]:
        path = self._safe_existing_file(self._path_for(logical_name), self._root(logical_name))
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise ArtifactNotFound("artifact is not available") from error
        return {"name": logical_name, "content_type": ARTIFACT_SPECS[logical_name].content_type, "content": content}

    def workspace_tests(self, workspace_id: str) -> Dict[str, str]:
        if not isinstance(workspace_id, str) or WORKSPACE_ID.fullmatch(workspace_id) is None:
            raise ArtifactNotFound("workspace tests are not available")
        root = self.workspace / ".launchpad" / "studio" / "workspaces"
        path = self._safe_existing_file(root / workspace_id / "tests.json", root)
        return {"name": "workspace-tests", "workspace_id": workspace_id, "content_type": "application/json", "content": path.read_text(encoding="utf-8")}

    def _preflight_state(self) -> Dict[str, Any]:
        try:
            path = self._safe_existing_file(self._path_for("preflight"), self.workspace)
        except ArtifactNotFound:
            return {"state": "pending", "detail": "Run scripts/studio-doctor.sh before starting Studio."}
        payload = _read_json(path)
        checks = payload.get("checks") if payload else None
        if not isinstance(checks, list) or not checks:
            return {"state": "failed", "detail": "The preflight artifact has no usable checks."}
        values = [item.get("ok") for item in checks if isinstance(item, Mapping) and "ok" in item]
        if len(values) != len(checks):
            return {"state": "failed", "detail": "The preflight artifact is incomplete."}
        return {"state": "ready" if all(values) else "failed", "detail": "All recorded checks passed." if all(values) else "One recorded check failed."}

    def _mcp_state(self) -> Dict[str, Any]:
        if self._lighthouse_state().get("state") != "verified":
            return {"state": "optional", "detail": "MCP becomes available only after the Lighthouse proof is verified."}
        try:
            path = self._safe_existing_file(self._path_for("mcp-check"), self.workspace)
        except ArtifactNotFound:
            return {"state": "optional", "detail": "MCP is not required for the Lighthouse journey."}
        payload = _read_json(path)
        if payload and payload.get("transport") == "stdio" and payload.get("tools") == ["omega.reason", "omega.get_receipt"]:
            return {"state": "ready", "detail": "The optional deterministic Launchpad bridge answered."}
        return {"state": "failed", "detail": "The optional MCP check is not valid."}

    def _example_state(self) -> Dict[str, Any]:
        required = (
            "example-readme", "example-story", "example-claims", "example-facts",
            "example-update", "example-runtime-bulletin", "example-rules", "example-reasoning", "example-tests",
            "example-receipt", "example-workspace",
        )
        try:
            for name in required:
                self.artifact(name)
        except ArtifactNotFound:
            return {"state": "failed", "detail": "The canonical Lighthouse example is incomplete."}
        return {"state": "ready", "detail": "The canonical Lighthouse example is complete."}

    def _lighthouse_state(self) -> Dict[str, Any]:
        try:
            proof_path = self._safe_existing_file(self._path_for("lighthouse-proof"), self.run_root)
            receipt_path = self._safe_existing_file(self._path_for("lighthouse-receipt"), self.run_root)
        except ArtifactNotFound:
            return {"state": "pending", "detail": "Run scripts/run-lighthouse-proof.sh before starting Studio."}
        payload = _read_json(proof_path)
        if payload is None:
            return {"state": "failed", "detail": "The Lighthouse proof is not valid JSON."}
        receipt_hash = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
        required = {
            "status": "verified",
            "runtime": "OmegaClaw-Core v0.1.19-dirty",
            "upstream_base_commit": UPSTREAM_COMMIT,
            "provider": "Test",
            "channel": "websocket",
            "scenario": "lighthouse-in-the-fog",
            "synthetic_only": True,
            "loop_observed": True,
            "remember_observed": True,
            "restart_observed": True,
            "query_after_restart_observed": True,
            "tool_skill_observed": True,
            "metta_skill_observed": True,
            "nal_stv_observed_in_loop": True,
            "response_observed": True,
            "human_approval_still_required": True,
            "external_actions": [],
            "receipt_sha256": receipt_hash,
        }
        if not all(payload.get(key) == value for key, value in required.items()):
            return {"state": "failed", "detail": "The proof does not satisfy the complete Lighthouse evidence contract."}
        safe = {
            "state": "verified",
            "detail": "The pinned Docker/Test Lighthouse proof satisfies every recorded checkpoint.",
            "channel": payload.get("channel"),
            "tool_source": payload.get("tool_source"),
            "conclusion": payload.get("conclusion"),
            "external_actions": payload.get("external_actions"),
        }
        for key in (
            "loop_observed", "remember_observed", "restart_observed",
            "query_after_restart_observed", "tool_skill_observed",
            "metta_skill_observed", "nal_stv_observed_in_loop",
            "response_observed",
        ):
            safe[key] = payload.get(key) is True
        safe["receipt_observed"] = True
        return safe

    def status(self) -> Dict[str, Any]:
        return {
            "preflight": self._preflight_state(),
            "lighthouse": self._lighthouse_state(),
            "example": self._example_state(),
            "mcp": self._mcp_state(),
        }
