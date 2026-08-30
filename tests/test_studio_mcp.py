import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from launchpad.config import UPSTREAM_COMMIT
from launchpad.studio.mcp_server import LocalMCP, main


class LocalMCPTests(unittest.TestCase):
    def _proof(self, workspace: Path) -> None:
        root = workspace / ".launchpad" / "studio" / "runs" / "lighthouse-in-the-fog"
        root.mkdir(parents=True)
        receipt = root / "receipt.md"
        receipt.write_text("# Receipt", encoding="utf-8")
        payload = {
            "status": "verified", "runtime": "OmegaClaw-Core v0.1.19-dirty", "upstream_base_commit": UPSTREAM_COMMIT,
            "provider": "Test", "channel": "websocket", "scenario": "lighthouse-in-the-fog", "synthetic_only": True,
            "loop_observed": True, "remember_observed": True, "restart_observed": True, "query_after_restart_observed": True,
            "tool_skill_observed": True, "metta_skill_observed": True, "nal_stv_observed_in_loop": True, "response_observed": True,
            "human_approval_still_required": True, "external_actions": [], "conclusion": "human_review_required",
            "receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
        }
        (root / "omega-proof.json").write_text(json.dumps(payload), encoding="utf-8")
        example = workspace / "examples" / "lighthouse-in-the-fog"
        example.mkdir(parents=True)

    def test_only_two_tools_and_receipt_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self._proof(root); bridge = LocalMCP(root)
            listing = bridge.dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
            self.assertEqual([tool["name"] for tool in listing["result"]["tools"]], ["omega.reason", "omega.get_receipt"])
            response = bridge.dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "omega.reason", "arguments": {"workspace_id": "lighthouse-in-the-fog", "question": "What was observed?"}}})
            result = response["result"]["structuredContent"]
            self.assertEqual(result["answer"], "human_review_required")
            self.assertTrue(result["basis"]["synthetic_only"])
            self.assertFalse(result["basis"]["real_omegaclaw_run_for_this_consultation"])
            fetched = bridge.dispatch({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "omega.get_receipt", "arguments": {"receipt_id": result["receipt_id"]}}})
            self.assertEqual(fetched["result"]["structuredContent"]["receipt_id"], result["receipt_id"])

    def test_general_consultation_detects_conflict_and_missing_fact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self._proof(root); bridge = LocalMCP(root)
            packet = {
                "case_id": "lighthouse-review", "rule": "Disagreement or missing evidence requires human review.",
                "claims": [{"agent_id": "lookout", "position": "north", "evidence_ids": ["beacon-1"]}, {"agent_id": "sailor", "position": "south", "evidence_ids": ["beacon-2"]}],
                "facts": [{"fact_id": "south_beacon", "status": "missing", "evidence_id": "beacon-2"}],
                "forbidden_actions": ["steer_boat", "send_external_message"],
            }
            response = bridge.dispatch({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "omega.reason", "arguments": {"workspace_id": "lighthouse-in-the-fog", "question": "What needs review?", "consultation": packet}}})
            result = response["result"]["structuredContent"]
            self.assertEqual(result["answer"], "human_review_required")
            self.assertEqual(result["decision_trace"]["missing_information"], ["south_beacon"])
            self.assertTrue(result["basis"]["human_approval_required"])

    def test_reason_requires_verified_proof_and_rejects_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = LocalMCP(Path(directory))
            response = bridge.dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "omega.reason", "arguments": {"workspace_id": "../bad", "question": "x"}}})
            self.assertTrue(response["result"]["isError"])

    def test_stdio_main_is_json_rpc_only(self):
        incoming = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}) + "\n"
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(main(["--workspace", directory], io.StringIO(incoming), output), 0)
        self.assertEqual(json.loads(output.getvalue())["result"]["serverInfo"]["name"], "omegaclaw-launchpad-local")


if __name__ == "__main__":
    unittest.main()
