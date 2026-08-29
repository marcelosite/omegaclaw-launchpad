"""Safe, file-backed artifact discovery for the P0 Studio.

Only the small allowlist in :data:`ARTIFACT_SPECS` is readable through the
web server.  Callers never provide a filesystem path, so this module is not a
general local file browser.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from ..config import UPSTREAM_COMMIT, UPSTREAM_REF
from ..reflection import DEFAULT_MISSION_ID


MAX_ARTIFACT_BYTES = 512 * 1024
"""Avoid turning the dashboard into a way to serve unexpectedly large files."""

WORKSPACE_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,62}\Z")


@dataclass(frozen=True)
class ArtifactSpec:
    """A logical, public name for one fixed local artifact."""

    logical_name: str
    relative_path: tuple[str, ...]
    content_type: str


ARTIFACT_SPECS = {
    "preflight": ArtifactSpec("preflight", (".launchpad", "studio", "preflight.json"), "application/json"),
    "mcp-check": ArtifactSpec("mcp-check", (".launchpad", "studio", "mcp-check.json"), "application/json"),
    "reflection-context": ArtifactSpec(
        "reflection-context", ("03-reflection", "reflection-context.json"), "application/json"
    ),
    "omega-proof": ArtifactSpec("omega-proof", ("03-reflection", "omega-proof.json"), "application/json"),
    "receipt": ArtifactSpec("receipt", ("06-receipt", "final-receipt.md"), "text/markdown"),
    "template-readme": ArtifactSpec("template-readme", ("README.md",), "text/markdown"),
    "template-facts": ArtifactSpec("template-facts", ("facts.json",), "application/json"),
    "template-rules-md": ArtifactSpec("template-rules-md", ("rules.md",), "text/markdown"),
    "template-rules-metta": ArtifactSpec("template-rules-metta", ("rules.metta",), "text/plain"),
    "template-tests": ArtifactSpec("template-tests", ("tests.json",), "application/json"),
    "template-workspace": ArtifactSpec("template-workspace", ("workspace.json",), "application/json"),
    "template-receipt": ArtifactSpec("template-receipt", ("example-receipt.md",), "text/markdown"),
    "community-proof": ArtifactSpec(
        "community-proof", (".launchpad", "studio", "runs", "community-care", "omega-proof.json"), "application/json"
    ),
    "community-receipt": ArtifactSpec(
        "community-receipt", (".launchpad", "studio", "runs", "community-care", "receipt.md"), "text/markdown"
    ),
}


class ArtifactNotFound(FileNotFoundError):
    """Raised when an allowlisted artifact does not exist yet."""


class UnknownArtifact(ValueError):
    """Raised for any artifact name outside the fixed public allowlist."""


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _read_json(path: Path) -> Optional[Mapping[str, Any]]:
    """Read a JSON object only; malformed input remains an artifact failure."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


class StudioArtifacts:
    """Resolve only known Studio artifacts under one Launchpad workspace."""

    def __init__(self, workspace: Path):
        self.workspace = workspace.expanduser().resolve()
        self.launchpad_root = self.workspace / ".launchpad"
        self.template_root = self.workspace / "templates" / "community-care"

    @property
    def mission_root(self) -> Path:
        """Use the canonical First Reflection mission, never a user path."""
        return self.launchpad_root / "first-reflection" / DEFAULT_MISSION_ID

    def _path_for(self, logical_name: str) -> Path:
        try:
            spec = ARTIFACT_SPECS[logical_name]
        except KeyError as error:
            raise UnknownArtifact("unknown Studio artifact") from error
        if logical_name in {"preflight", "mcp-check"}:
            return self.workspace.joinpath(*spec.relative_path)
        if logical_name.startswith("template-"):
            return self.template_root.joinpath(*spec.relative_path)
        if logical_name.startswith("community-"):
            return self.workspace.joinpath(*spec.relative_path)
        return self.mission_root.joinpath(*spec.relative_path)

    def _safe_existing_file(self, candidate: Path, root: Path) -> Path:
        """Refuse missing files, symlinks, escapes, and oversized artifacts."""
        try:
            resolved_root = root.resolve(strict=True)
            resolved_candidate = candidate.resolve(strict=True)
        except OSError as error:
            raise ArtifactNotFound("artifact is not available") from error
        if not _inside(resolved_root, self.workspace) or not _inside(resolved_candidate, resolved_root):
            raise ArtifactNotFound("artifact is not available")
        # A symlink under the logical root makes a fixed route unexpectedly
        # depend on another path, even when it happens to resolve inside it.
        try:
            relative = candidate.relative_to(root)
        except ValueError as error:
            raise ArtifactNotFound("artifact is not available") from error
        current = root
        for part in relative.parts:
            if current.is_symlink():
                raise ArtifactNotFound("artifact is not available")
            current = current / part
        if current.is_symlink():
            raise ArtifactNotFound("artifact is not available")
        if not resolved_candidate.is_file() or resolved_candidate.stat().st_size > MAX_ARTIFACT_BYTES:
            raise ArtifactNotFound("artifact is not available")
        return resolved_candidate

    def artifact(self, logical_name: str) -> Dict[str, str]:
        """Return UTF-8 content and metadata for one allowlisted artifact."""
        candidate = self._path_for(logical_name)
        root = self.workspace if logical_name in ("preflight", "mcp-check", "community-proof", "community-receipt") else (
            self.template_root if logical_name.startswith("template-") else self.mission_root
        )
        path = self._safe_existing_file(candidate, root)
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise ArtifactNotFound("artifact is not available") from error
        return {
            "name": logical_name,
            "content_type": ARTIFACT_SPECS[logical_name].content_type,
            "content": content,
        }

    def workspace_tests(self, workspace_id: str) -> Dict[str, str]:
        """Return only the copied workspace's fixed tests file by logical ID."""
        if not isinstance(workspace_id, str) or WORKSPACE_ID.fullmatch(workspace_id) is None:
            raise ArtifactNotFound("workspace tests are not available")
        root = self.workspace / ".launchpad" / "studio" / "workspaces"
        candidate = root / workspace_id / "tests.json"
        path = self._safe_existing_file(candidate, root)
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise ArtifactNotFound("workspace tests are not available") from error
        return {
            "name": "workspace-tests",
            "workspace_id": workspace_id,
            "content_type": "application/json",
            "content": content,
        }

    def _preflight_state(self) -> Dict[str, Any]:
        path = self._path_for("preflight")
        try:
            safe_path = self._safe_existing_file(path, self.workspace)
        except ArtifactNotFound:
            return {"state": "pending", "detail": "No preflight artifact has been recorded."}
        payload = _read_json(safe_path)
        if payload is None:
            return {"state": "failed", "detail": "The preflight artifact is not valid JSON."}
        checks = payload.get("checks", payload.get("results", payload))
        if isinstance(checks, list) and checks:
            values = [item.get("ok") for item in checks if isinstance(item, Mapping) and "ok" in item]
            if values and len(values) == len(checks):
                return {
                    "state": "ready" if all(values) else "failed",
                    "detail": "All recorded checks passed." if all(values) else "One or more recorded checks failed.",
                }
        return {"state": "failed", "detail": "The preflight artifact has no usable checks."}

    def _mcp_state(self) -> Dict[str, Any]:
        try:
            safe_path = self._safe_existing_file(self._path_for("mcp-check"), self.workspace)
        except ArtifactNotFound:
            return {"state": "pending", "detail": "Run the local MCP check after registering an agent."}
        payload = _read_json(safe_path)
        expected_tools = ["omega.reason", "omega.get_receipt"]
        if payload is None:
            return {"state": "failed", "detail": "The MCP check artifact is not valid JSON."}
        if payload.get("transport") == "stdio" and payload.get("tools") == expected_tools and payload.get("proof") == "verified":
            return {"state": "ready", "detail": "The local bridge answered and exposed exactly two bounded tools."}
        return {"state": "failed", "detail": "The MCP check did not confirm the expected bridge and proof."}

    def _proof_state(self) -> Dict[str, Any]:
        path = self._path_for("omega-proof")
        try:
            safe_path = self._safe_existing_file(path, self.mission_root)
        except ArtifactNotFound:
            return {"state": "pending", "detail": "No real OmegaClaw proof artifact has been recorded."}
        payload = _read_json(safe_path)
        if payload is None:
            return {"state": "failed", "detail": "The proof artifact is not valid JSON."}
        recorded = payload.get("status")
        if recorded == "pending":
            return {"state": "pending", "detail": "The recorded proof is pending."}
        if recorded != "verified":
            return {"state": "failed", "detail": "The recorded proof did not verify."}
        requirements = {
            "upstream_base_commit": UPSTREAM_COMMIT,
            "provider": "Test",
            "channel": "websocket",
            "metta_skill_observed": True,
            "nal_stv_observed_in_loop": True,
            "human_approval_still_required": True,
        }
        response = payload.get("response")
        if (
            all(payload.get(key) == value for key, value in requirements.items())
            and payload.get("runtime") == "OmegaClaw-Core v0.1.19-dirty"
            and isinstance(response, str)
            and bool(response.strip())
        ):
            return {
                "state": "verified",
                "detail": "A pinned Test/WebSocket proof with observed MeTTa and NAL evidence is recorded.",
            }
        return {"state": "failed", "detail": "The proof artifact does not satisfy the required evidence contract."}

    def _receipt_state(self, proof_state: str) -> Dict[str, Any]:
        try:
            self.artifact("receipt")
        except ArtifactNotFound:
            return {"state": "pending", "detail": "No First Reflection receipt is available."}
        if proof_state == "verified":
            return {"state": "verified", "detail": "The receipt is accompanied by a verified proof artifact."}
        return {"state": "ready", "detail": "A local receipt is available; it does not itself prove OmegaClaw ran."}

    def _community_state(self) -> Dict[str, Any]:
        try:
            self.artifact("community-proof")
            self.artifact("community-receipt")
        except ArtifactNotFound:
            return {"state": "pending", "detail": "Run the real Community Hospital lesson and keep its receipt to unlock the Codex handoff."}
        payload = _read_json(self._path_for("community-proof"))
        requirements = {
            "status": "verified",
            "provider": "Test",
            "channel": "websocket",
            "template": "community-care",
            "synthetic_only": True,
            "conclusion": "human_review_required",
            "metta_skill_observed": True,
            "nal_stv_observed_in_loop": True,
            "human_approval_still_required": True,
        }
        if payload is not None and all(payload.get(key) == value for key, value in requirements.items()):
            return {"state": "verified", "detail": "The synthetic Community Hospital lesson ran through pinned OmegaClaw Test/WebSocket/MeTTa/NAL and wrote a receipt."}
        return {"state": "failed", "detail": "The Community Hospital proof artifact does not satisfy its real-runtime contract."}

    def status(self) -> Dict[str, Any]:
        """Return states derived exclusively from files that actually exist."""
        preflight = self._preflight_state()
        mcp = self._mcp_state()
        proof = self._proof_state()
        receipt = self._receipt_state(proof["state"])
        community = self._community_state()
        template_files: List[str] = []
        for name in (
            "template-readme",
            "template-facts",
            "template-rules-md",
            "template-rules-metta",
            "template-tests",
            "template-workspace",
            "template-receipt",
        ):
            try:
                self.artifact(name)
            except ArtifactNotFound:
                continue
            template_files.append(name)
        required_template_files = (
            "template-readme",
            "template-facts",
            "template-rules-md",
            "template-rules-metta",
            "template-tests",
            "template-workspace",
            "template-receipt",
        )
        return {
            "upstream": {"ref": UPSTREAM_REF, "commit": UPSTREAM_COMMIT},
            "preflight": preflight,
            "mcp": mcp,
            "proof": proof,
            "receipt": receipt,
            "community_care": community,
            "handoff": {
                "state": "ready" if community["state"] == "verified" else "pending",
                "detail": (
                    "The real Community Hospital lesson is verified. Your next step is to connect Codex through the local MCP bridge."
                    if community["state"] == "verified"
                    else "Run the safe Test/WebSocket Community Hospital lesson before connecting an agent."
                ),
            },
            "template": {
                "state": "ready" if len(template_files) == len(required_template_files) else "pending",
                "available_artifacts": template_files,
                "name": "community-care",
            },
        }
