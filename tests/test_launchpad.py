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


if __name__ == "__main__":
    unittest.main()
