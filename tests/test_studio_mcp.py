import io
import json
import tempfile
import unittest
from pathlib import Path

from launchpad.config import UPSTREAM_COMMIT
from launchpad.studio.mcp_server import LocalMCP, main


class LocalMCPTests(unittest.TestCase):
    _release_readiness_packet = {
        "case_id": "release-readiness-demo",
        "rulebook_id": "release-readiness-demo-r1",
        "claims": [
            {"agent_id": "build-agent", "position": "release_ready", "evidence_ids": ["unit-tests-2026-08-29"]},
            {"agent_id": "security-agent", "position": "release_not_ready", "evidence_ids": ["security-check-missing"]},
        ],
        "recorded_facts": [
            {"fact_id": "unit_tests", "status": "passed", "evidence_id": "unit-tests-2026-08-29"},
            {"fact_id": "required_security_check", "status": "missing", "evidence_id": "security-check-missing"},
        ],
        "forbidden_actions": ["deploy", "merge"],
    }

    def _proof(self, workspace: Path) -> None:
        root = workspace / ".launchpad" / "studio" / "runs" / "factory-fault"
        root.mkdir(parents=True)
        payload = {
            "status": "verified",
            "runtime": "OmegaClaw-Core v0.1.19-dirty",
            "provider": "Test",
            "channel": "websocket",
            "template": "factory-fault",
            "synthetic_only": True,
            "conclusion": "manual_inspection_recommended",
            "metta_skill_observed": True,
            "nal_stv_observed_in_loop": True,
            "human_approval_still_required": True,
            "upstream_base_commit": UPSTREAM_COMMIT,
            "facts": [{"predicate": "temperature_above_demo_threshold", "value": True}],
        }
        (root / "omega-proof.json").write_text(json.dumps(payload), encoding="utf-8")
        (root / "receipt.md").write_text("# Factory receipt", encoding="utf-8")
        (workspace / "templates" / "factory-fault").mkdir(parents=True)

    def test_only_two_tools_and_receipt_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._proof(root)
            bridge = LocalMCP(root)
            listing = bridge.dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
            self.assertEqual([tool["name"] for tool in listing["result"]["tools"]], ["omega.reason", "omega.get_receipt"])
            response = bridge.dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "omega.reason", "arguments": {"workspace_id": "factory-fault", "question": "What does this lesson conclude?"}}})
            result = response["result"]["structuredContent"]
            self.assertEqual(result["answer"], "manual_inspection_recommended")
            self.assertTrue(result["receipt_id"].startswith("mcp-"))
            self.assertNotIn(str(root), json.dumps(result))
            fetched = bridge.dispatch({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "omega.get_receipt", "arguments": {"receipt_id": result["receipt_id"]}}})
            self.assertEqual(fetched["result"]["structuredContent"]["receipt_id"], result["receipt_id"])

    def test_release_readiness_teaching_packet_records_auditable_trace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._proof(root)
            bridge = LocalMCP(root)
            response = bridge.dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "omega.reason", "arguments": {
                "workspace_id": "factory-fault",
                "question": "What should a human review before this release?",
                "conflict_packet": self._release_readiness_packet,
            }}})
            result = response["result"]["structuredContent"]
            self.assertEqual(result["answer"], "human_review_required")
            self.assertEqual(result["decision_trace"]["missing_information"], ["required_security_check result"])
            self.assertEqual(result["decision_trace"]["forbidden_actions"], ["deploy", "merge"])
            self.assertTrue(result["basis"]["synthetic_only"])
            self.assertTrue(result["basis"]["human_approval_required"])
            self.assertIn("does not run OmegaClaw again", result["limitations"][1])

    def test_release_readiness_packet_rejects_another_rulebook_or_unbounded_facts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._proof(root)
            bridge = LocalMCP(root)
            invalid_packet = json.loads(json.dumps(self._release_readiness_packet))
            invalid_packet["rulebook_id"] = "anything-else"
            response = bridge.dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "omega.reason", "arguments": {
                "workspace_id": "factory-fault",
                "question": "Can this tool decide a different case?",
                "conflict_packet": invalid_packet,
            }}})
            self.assertTrue(response["result"]["isError"])
            self.assertIn("limited to the release-readiness-demo", response["result"]["content"][0]["text"])

    def test_reason_requires_verified_proof_and_rejects_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = LocalMCP(Path(directory))
            response = bridge.dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "omega.reason", "arguments": {"workspace_id": "../bad", "question": "x"}}})
            self.assertTrue(response["result"]["isError"])

    def test_stdio_main_is_json_rpc_only(self):
        incoming = "\n".join([
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
        ]) + "\n"
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(main(["--workspace", directory], io.StringIO(incoming), output), 0)
        lines = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(lines[0]["result"]["serverInfo"]["name"], "omegaclaw-launchpad-local")
        self.assertEqual(len(lines[1]["result"]["tools"]), 2)


if __name__ == "__main__":
    unittest.main()
