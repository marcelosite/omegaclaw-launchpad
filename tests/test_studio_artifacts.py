import json
import tempfile
import unittest
from pathlib import Path

from launchpad.config import UPSTREAM_COMMIT
from launchpad.reflection import DEFAULT_MISSION_ID
from launchpad.studio.artifacts import ArtifactNotFound, StudioArtifacts, UnknownArtifact


class StudioArtifactTests(unittest.TestCase):
    def _mission(self, workspace: Path) -> Path:
        root = workspace / ".launchpad" / "first-reflection" / DEFAULT_MISSION_ID
        (root / "03-reflection").mkdir(parents=True)
        (root / "06-receipt").mkdir()
        return root

    def _proof(self, root: Path, **changes: object) -> None:
        payload = {
            "status": "verified",
            "runtime": "OmegaClaw-Core v0.1.19-dirty",
            "upstream_base_commit": UPSTREAM_COMMIT,
            "provider": "Test",
            "channel": "websocket",
            "metta_skill_observed": True,
            "nal_stv_observed_in_loop": True,
            "human_approval_still_required": True,
            "response": "A recorded response.",
        }
        payload.update(changes)
        (root / "03-reflection" / "omega-proof.json").write_text(json.dumps(payload), encoding="utf-8")

    def test_status_never_verifies_without_the_complete_proof_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            root = self._mission(workspace)
            reader = StudioArtifacts(workspace)
            self.assertEqual(reader.status()["proof"]["state"], "pending")
            self._proof(root, provider="Not-Test")
            self.assertEqual(reader.status()["proof"]["state"], "failed")
            self._proof(root, runtime="OmegaClaw-Core v0.1.19")
            self.assertEqual(reader.status()["proof"]["state"], "failed")
            self._proof(root, response="")
            self.assertEqual(reader.status()["proof"]["state"], "failed")
            self._proof(root)
            self.assertEqual(reader.status()["proof"]["state"], "verified")

    def test_artifact_allowlist_rejects_traversal_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            reader = StudioArtifacts(workspace)
            with self.assertRaises(UnknownArtifact):
                reader.artifact("../../etc/passwd")
            studio_dir = workspace / ".launchpad" / "studio"
            studio_dir.mkdir(parents=True)
            (studio_dir / "preflight.json").symlink_to("/etc/passwd")
            with self.assertRaises(ArtifactNotFound):
                reader.artifact("preflight")

    def test_preflight_uses_recorded_check_results_only(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            studio_dir = workspace / ".launchpad" / "studio"
            studio_dir.mkdir(parents=True)
            reader = StudioArtifacts(workspace)
            self.assertEqual(reader.status()["preflight"]["state"], "pending")
            (studio_dir / "preflight.json").write_text(json.dumps({"checks": [{"ok": True}, {"ok": False}]}))
            self.assertEqual(reader.status()["preflight"]["state"], "failed")
            (studio_dir / "preflight.json").write_text(json.dumps({"checks": [{"ok": True}]}))
            self.assertEqual(reader.status()["preflight"]["state"], "ready")

    def test_factory_proof_requires_its_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            run_root = workspace / ".launchpad" / "studio" / "runs" / "factory-fault"
            run_root.mkdir(parents=True)
            payload = {
                "status": "verified",
                "provider": "Test",
                "channel": "websocket",
                "template": "factory-fault",
                "synthetic_only": True,
                "conclusion": "manual_inspection_recommended",
                "metta_skill_observed": True,
                "nal_stv_observed_in_loop": True,
                "human_approval_still_required": True,
            }
            (run_root / "omega-proof.json").write_text(json.dumps(payload), encoding="utf-8")
            reader = StudioArtifacts(workspace)
            self.assertEqual(reader.status()["factory_fault"]["state"], "pending")
            (run_root / "receipt.md").write_text("# Receipt", encoding="utf-8")
            self.assertEqual(reader.status()["factory_fault"]["state"], "verified")

    def test_workspace_tests_are_read_by_logical_id_only(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            tests_root = workspace / ".launchpad" / "studio" / "workspaces" / "my-case"
            tests_root.mkdir(parents=True)
            (tests_root / "tests.json").write_text("{\"cases\": []}", encoding="utf-8")
            reader = StudioArtifacts(workspace)
            result = reader.workspace_tests("my-case")
            self.assertEqual(result["workspace_id"], "my-case")
            self.assertEqual(result["content"], "{\"cases\": []}")
            with self.assertRaises(ArtifactNotFound):
                reader.workspace_tests("../outside")

    def test_artifact_content_is_returned_as_data_not_html(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            root = self._mission(workspace)
            content = "# Receipt\n\n<script>alert('not executable')</script>"
            (root / "06-receipt" / "final-receipt.md").write_text(content, encoding="utf-8")
            artifact = StudioArtifacts(workspace).artifact("receipt")
            self.assertEqual(artifact["content"], content)
            self.assertEqual(artifact["content_type"], "text/markdown")

    def test_template_example_receipt_and_workspace_contract_are_allowlisted(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            template = workspace / "templates" / "factory-fault"
            template.mkdir(parents=True)
            (template / "example-receipt.md").write_text("# Fixture receipt", encoding="utf-8")
            (template / "workspace.json").write_text("{}", encoding="utf-8")
            reader = StudioArtifacts(workspace)
            self.assertEqual(reader.artifact("template-receipt")["content"], "# Fixture receipt")
            self.assertEqual(reader.artifact("template-workspace")["content"], "{}")


if __name__ == "__main__":
    unittest.main()
