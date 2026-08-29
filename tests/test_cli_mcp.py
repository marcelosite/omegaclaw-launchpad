import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from launchpad.cli import main
from launchpad.config import UPSTREAM_COMMIT


class MCPCLITests(unittest.TestCase):
    def _proof(self, workspace: Path) -> None:
        root = workspace / ".launchpad" / "studio" / "runs" / "factory-fault"
        root.mkdir(parents=True)
        payload = {
            "status": "verified",
            "runtime": "OmegaClaw-Core v0.1.19-dirty",
            "upstream_base_commit": UPSTREAM_COMMIT,
            "provider": "Test",
            "channel": "websocket",
            "template": "factory-fault",
            "synthetic_only": True,
            "conclusion": "manual_inspection_recommended",
            "metta_skill_observed": True,
            "nal_stv_observed_in_loop": True,
            "human_approval_still_required": True,
            "facts": [],
        }
        (root / "omega-proof.json").write_text(json.dumps(payload), encoding="utf-8")
        (root / "receipt.md").write_text("# Receipt", encoding="utf-8")
        (workspace / "templates" / "factory-fault").mkdir(parents=True)

    def test_mcp_check_and_general_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            self._proof(workspace)
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["mcp", "check", "--workspace", directory, "--json"]), 0)
            payload = json.loads(output.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["tools"], ["omega.reason", "omega.get_receipt"])
            check = json.loads((workspace / ".launchpad" / "studio" / "mcp-check.json").read_text(encoding="utf-8"))
            self.assertTrue(check["ok"])

            packet = workspace / "packet.json"
            packet.write_text(json.dumps({
                "case_id": "small-test",
                "rule": "Missing facts require a human review.",
                "claims": [{"agent_id": "one", "position": "yes", "evidence_ids": ["e1"]}],
                "facts": [{"fact_id": "approval", "status": "missing", "evidence_id": "e2"}],
                "forbidden_actions": ["send"],
            }), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["mcp", "reason", "--workspace", directory, "--packet-file", str(packet), "--question", "What now?", "--json"]), 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["answer"], "human_review_required")


if __name__ == "__main__":
    unittest.main()
