import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from launchpad.cli import main
from launchpad.studio_templates import resolve_template
from launchpad.studio_workspace import create_workspace, validate_workspace_slug, workspace_path


class StudioWorkspaceTests(unittest.TestCase):
    def test_lighthouse_copy_uses_fixed_local_destination_and_preserves_example(self):
        source = resolve_template("lighthouse-in-the-fog")
        original_facts = (source / "facts.json").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = create_workspace(root, "my-case", "lighthouse-in-the-fog")
            self.assertEqual(destination, root.resolve() / ".launchpad" / "studio" / "workspaces" / "my-case")
            for filename in ("facts.json", "rules.md", "reasoning.metta", "tests.json", "example-receipt.md"):
                self.assertTrue((destination / filename).is_file())
            self.assertEqual((source / "facts.json").read_text(encoding="utf-8"), original_facts)
            self.assertEqual(json.loads((destination / "workspace.json").read_text())["example"], "lighthouse-in-the-fog")

    def test_cli_checks_and_copies_only_lighthouse_example(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main(["example", "copy", "my-case", "--workspace", directory])
            self.assertEqual(result, 0)
            self.assertIn("Lighthouse example copied", output.getvalue())
            self.assertTrue(Path(directory, ".launchpad", "studio", "workspaces", "my-case", "README.md").exists())
            self.assertEqual(main(["example", "check", "my-case", "--workspace", directory]), 0)

    def test_unknown_template_is_rejected_without_creating_a_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            error = io.StringIO()
            with contextlib.redirect_stderr(error):
                result = main(["studio", "new", "my-case", "--template", "not-a-template", "--workspace", directory])
            self.assertEqual(result, 2)
            self.assertIn("Unknown Studio template", error.getvalue())

    def test_invalid_slugs_cannot_escape_workspace_root(self):
        for slug in ("", "My-Case", "my_case", "../outside", "my/case", "-case", "case-", "a" * 64):
            with self.subTest(slug=slug):
                with self.assertRaises(ValueError):
                    validate_workspace_slug(slug)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                workspace_path(Path(directory), "../outside")

    def test_existing_workspace_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = create_workspace(root, "my-case", "lighthouse-in-the-fog")
            marker = destination / "user-note.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                create_workspace(root, "my-case", "lighthouse-in-the-fog")
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_example_fixture_has_safety_boundary_and_two_nal_expressions(self):
        source = resolve_template("lighthouse-in-the-fog")
        fixture = json.loads((source / "tests.json").read_text(encoding="utf-8"))
        self.assertEqual({case["id"] for case in fixture["cases"]}, {"conflicting-current-reports", "verified-independent-update", "missing-required-beacon", "gigo-anonymous-claim-only"})
        self.assertTrue(all(case["human_approval_required"] for case in fixture["cases"]))
        self.assertIn("(|-", (source / "reasoning.metta").read_text(encoding="utf-8"))
        self.assertIn("fixture", (source / "example-receipt.md").read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
