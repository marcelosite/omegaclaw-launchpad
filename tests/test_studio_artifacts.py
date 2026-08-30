import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from launchpad.config import UPSTREAM_COMMIT
from launchpad.studio.artifacts import ArtifactNotFound, StudioArtifacts, UnknownArtifact


class StudioArtifactTests(unittest.TestCase):
    def _proof(self, workspace: Path, **changes: object) -> None:
        run = workspace / ".launchpad" / "studio" / "runs" / "lighthouse-in-the-fog"
        run.mkdir(parents=True, exist_ok=True)
        receipt = run / "receipt.md"
        receipt.write_text("# Lighthouse receipt\n", encoding="utf-8")
        payload = {
            "status": "verified", "runtime": "OmegaClaw-Core v0.1.19-dirty",
            "upstream_base_commit": UPSTREAM_COMMIT, "provider": "Test", "channel": "websocket",
            "scenario": "lighthouse-in-the-fog", "synthetic_only": True,
            "loop_observed": True, "remember_observed": True, "restart_observed": True,
            "query_after_restart_observed": True, "tool_skill_observed": True,
            "metta_skill_observed": True, "nal_stv_observed_in_loop": True,
            "response_observed": True, "human_approval_still_required": True,
            "external_actions": [], "conclusion": "human_review_required",
            "receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
        }
        payload.update(changes)
        (run / "omega-proof.json").write_text(json.dumps(payload), encoding="utf-8")

    def test_lighthouse_proof_requires_complete_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            reader = StudioArtifacts(workspace)
            self.assertEqual(reader.status()["lighthouse"]["state"], "pending")
            self._proof(workspace, provider="Not-Test")
            self.assertEqual(reader.status()["lighthouse"]["state"], "failed")
            self._proof(workspace)
            self.assertEqual(reader.status()["lighthouse"]["state"], "verified")

    def test_artifact_allowlist_rejects_traversal_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            reader = StudioArtifacts(workspace)
            with self.assertRaises(UnknownArtifact):
                reader.artifact("../../etc/passwd")
            example = workspace / "examples" / "lighthouse-in-the-fog"
            example.mkdir(parents=True)
            (example / "README.md").symlink_to("/etc/passwd")
            with self.assertRaises(ArtifactNotFound):
                reader.artifact("example-readme")

    def test_preflight_and_mcp_states_are_recorded_optional_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            studio = workspace / ".launchpad" / "studio"
            studio.mkdir(parents=True)
            reader = StudioArtifacts(workspace)
            self.assertEqual(reader.status()["preflight"]["state"], "pending")
            (studio / "preflight.json").write_text(json.dumps({"checks": [{"ok": True}]}))
            self.assertEqual(reader.status()["preflight"]["state"], "ready")
            self.assertEqual(reader.status()["mcp"]["state"], "optional")
            self._proof(workspace)
            (studio / "mcp-check.json").write_text(json.dumps({"transport": "stdio", "tools": ["omega.reason", "omega.get_receipt"]}))
            self.assertEqual(reader.status()["mcp"]["state"], "ready")

    def test_workspace_tests_use_logical_id_only(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            root = workspace / ".launchpad" / "studio" / "workspaces" / "my-case"
            root.mkdir(parents=True)
            (root / "tests.json").write_text('{"cases": []}', encoding="utf-8")
            result = StudioArtifacts(workspace).workspace_tests("my-case")
            self.assertEqual(result["workspace_id"], "my-case")
            with self.assertRaises(ArtifactNotFound):
                StudioArtifacts(workspace).workspace_tests("../outside")

    def test_artifact_content_is_data_not_html(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            run = workspace / ".launchpad" / "studio" / "runs" / "lighthouse-in-the-fog"
            run.mkdir(parents=True)
            content = "# Receipt\n<script>alert('not executable')</script>"
            (run / "receipt.md").write_text(content, encoding="utf-8")
            self.assertEqual(StudioArtifacts(workspace).artifact("lighthouse-receipt")["content"], content)


if __name__ == "__main__":
    unittest.main()
