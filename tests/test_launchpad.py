import contextlib
import io
import json
import stat
import tempfile
import unittest
from pathlib import Path

from launchpad.cli import main
from launchpad.config import build_config
from launchpad.journey import load_config
from launchpad.reflection import (
    create_receipt,
    execute_controlled_run,
    initialize_mission,
    prepare_reflection,
    record_decision,
    validate_run,
)
from launchpad.upstream import render_launch_command


class LaunchpadTests(unittest.TestCase):
    def test_init_writes_manifest_without_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(main(["init", "--workspace", str(root), "--provider", "OpenAI", "--channel", "irc"]), 0)
            manifest = load_config(root)
            self.assertEqual(manifest["provider_env"], "OPENAI_API_KEY")
            self.assertEqual(manifest["journey"]["configuration"], "complete")
            self.assertNotIn("replace-with", (root / ".launchpad" / "config.json").read_text().lower())
            script = root / ".launchpad" / "run-omegaclaw.sh"
            self.assertTrue(script.exists())
            self.assertTrue(stat.S_IMODE(script.stat().st_mode) & stat.S_IXUSR)
            env_example = (root / ".env.example").read_text()
            self.assertIn("OPENAI_API_KEY", env_example)
            self.assertIn("replace-with-your-provider-key", env_example)

    def test_launch_command_never_contains_provider_value(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = build_config(root, "Anthropic", "irc", "##demo")
            command = render_launch_command(config, root / ".launchpad" / "upstream")
            self.assertNotIn("ANTHROPIC_API_KEY", command)
            self.assertIn("${OMEGACLAW_AUTH_SECRET", command)
            self.assertIn("##demo", command)

    def test_offline_demo_is_deterministic(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["demo"]), 0)
        self.assertIn("offline proof", output.getvalue())
        self.assertIn("does not pretend", output.getvalue())

    def test_doctor_json_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                main(["doctor", "--workspace", directory, "--channel", "telegram", "--json"])
            payload = json.loads(output.getvalue())
            self.assertIsInstance(payload, list)
            names = {item["name"] for item in payload}
            self.assertTrue({"Python", "Git", "Docker", "Workspace", "Channel setting"} <= names)

    def test_reflection_cycle_detects_mismatch_and_requires_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = initialize_mission(Path(directory))
            execute_controlled_run(root)
            before = validate_run(root)
            self.assertEqual(before["status"], "fail")
            self.assertEqual(before["findings"][0]["observed"], 1)
            self.assertEqual(before["findings"][1]["declared"], 3)

            with self.assertRaises(FileNotFoundError):
                execute_controlled_run(root, rerun=True)

            prepare_reflection(root)
            record_decision(root, "approved")
            execute_controlled_run(root, rerun=True)
            after = validate_run(root, rerun=True)
            self.assertEqual(after["status"], "pass")
            self.assertEqual(after["findings"][0]["observed"], 3)
            receipt = create_receipt(root)
            self.assertEqual(receipt["before"]["status"], "fail")
            self.assertEqual(receipt["after"]["status"], "pass")

    def test_rejected_reflection_cannot_rerun(self):
        with tempfile.TemporaryDirectory() as directory:
            root = initialize_mission(Path(directory))
            execute_controlled_run(root)
            validate_run(root)
            prepare_reflection(root)
            record_decision(root, "rejected")
            with self.assertRaises(PermissionError):
                execute_controlled_run(root, rerun=True)

    def test_mission_id_cannot_escape_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                initialize_mission(Path(directory), "../../outside")

    def test_reflection_and_human_decision_are_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = initialize_mission(Path(directory))
            execute_controlled_run(root)
            validate_run(root)
            prepare_reflection(root)
            with self.assertRaises(FileExistsError):
                prepare_reflection(root)
            record_decision(root, "approved")
            with self.assertRaises(FileExistsError):
                record_decision(root, "rejected")

    def test_reflection_context_does_not_fake_omegaclaw(self):
        with tempfile.TemporaryDirectory() as directory:
            root = initialize_mission(Path(directory))
            execute_controlled_run(root)
            validate_run(root)
            context = prepare_reflection(root)
            self.assertEqual(context["omega_integration"]["status"], "pending")
            omega_output = (root / "03-reflection" / "omega-response.txt").read_text()
            self.assertIn("PENDING REAL OMEGACLAW RUN", omega_output)
            proposal = json.loads((root / "03-reflection" / "proposal.json").read_text())
            self.assertEqual(proposal["origin"], "controlled-fixture-not-omegaclaw")

    def test_reflection_cli_demo_writes_auditable_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main(["reflect", "demo", "--workspace", directory])
            self.assertEqual(result, 0)
            self.assertIn("OMEGACLAW PROOF: PENDING", output.getvalue())
            receipt = (
                Path(directory)
                / ".launchpad"
                / "first-reflection"
                / "source-audit-demo-001"
                / "06-receipt"
                / "final-receipt.md"
            )
            self.assertTrue(receipt.exists())


if __name__ == "__main__":
    unittest.main()
