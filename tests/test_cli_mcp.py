import hashlib
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
        root = workspace / ".launchpad" / "studio" / "runs" / "lighthouse-in-the-fog"
        root.mkdir(parents=True)
        receipt = root / "receipt.md"; receipt.write_text("# Receipt", encoding="utf-8")
        payload = {"status": "verified", "runtime": "OmegaClaw-Core v0.1.19-dirty", "upstream_base_commit": UPSTREAM_COMMIT, "provider": "Test", "channel": "websocket", "scenario": "lighthouse-in-the-fog", "synthetic_only": True, "loop_observed": True, "remember_observed": True, "restart_observed": True, "query_after_restart_observed": True, "tool_skill_observed": True, "metta_skill_observed": True, "nal_stv_observed_in_loop": True, "response_observed": True, "human_approval_still_required": True, "external_actions": [], "conclusion": "human_review_required", "receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest()}
        (root / "omega-proof.json").write_text(json.dumps(payload), encoding="utf-8")
        (workspace / "examples" / "lighthouse-in-the-fog").mkdir(parents=True)

    def test_mcp_check_and_general_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory); self._proof(workspace)
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["mcp", "check", "--workspace", directory, "--json"]), 0)
            payload = json.loads(output.getvalue())
            self.assertTrue(payload["ok"])
            packet = workspace / "packet.json"
            packet.write_text(json.dumps({"case_id": "small-test", "rule": "Missing facts require human review.", "claims": [{"agent_id": "one", "position": "yes", "evidence_ids": ["e1"]}], "facts": [{"fact_id": "approval", "status": "missing", "evidence_id": "e2"}], "forbidden_actions": ["send"]}), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["mcp", "reason", "--workspace", directory, "--packet-file", str(packet), "--question", "What now?", "--json"]), 0)
            self.assertEqual(json.loads(output.getvalue())["answer"], "human_review_required")


if __name__ == "__main__":
    unittest.main()
