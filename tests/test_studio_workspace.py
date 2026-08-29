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
    def test_community_care_copy_uses_fixed_local_destination_and_preserves_template(self):
        source = resolve_template("community-care")
        original_facts = (source / "facts.json").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = create_workspace(root, "my-case", "community-care")

            self.assertEqual(destination, root.resolve() / ".launchpad" / "studio" / "workspaces" / "my-case")
            self.assertTrue((destination / "facts.json").is_file())
            self.assertTrue((destination / "rules.md").is_file())
            self.assertTrue((destination / "rules.metta").is_file())
            self.assertTrue((destination / "tests.json").is_file())
            self.assertTrue((destination / "example-receipt.md").is_file())
            self.assertEqual((source / "facts.json").read_text(encoding="utf-8"), original_facts)
            self.assertEqual(json.loads((destination / "workspace.json").read_text())["template"], "community-care")

    def test_cli_copies_the_only_approved_template(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main(["studio", "new", "my-case", "--template", "community-care", "--workspace", directory])
            self.assertEqual(result, 0)
            self.assertIn("Studio workspace created", output.getvalue())
            self.assertTrue(Path(directory, ".launchpad", "studio", "workspaces", "my-case", "README.md").exists())

    def test_unknown_template_is_rejected_without_creating_a_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            error = io.StringIO()
            with contextlib.redirect_stderr(error):
                result = main(["studio", "new", "my-case", "--template", "not-a-template", "--workspace", directory])
            self.assertEqual(result, 2)
            self.assertIn("Unknown Studio template", error.getvalue())
            self.assertFalse(Path(directory, ".launchpad", "studio", "workspaces", "my-case").exists())

    def test_invalid_slugs_cannot_escape_the_workspace_root(self):
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
            destination = create_workspace(root, "my-case", "community-care")
            marker = destination / "user-note.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                create_workspace(root, "my-case", "community-care")
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_workspace_root_rejects_symbolic_links(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as target:
            root = Path(directory)
            (root / ".launchpad").symlink_to(Path(target), target_is_directory=True)
            with self.assertRaises(ValueError):
                create_workspace(root, "my-case", "community-care")

    def test_fixture_has_a_positive_and_negative_case_and_no_diagnostic_conclusion(self):
        source = resolve_template("community-care")
        fixture = json.loads((source / "tests.json").read_text(encoding="utf-8"))
        conclusions = {case["expected_conclusion"] for case in fixture["cases"]}
        self.assertEqual(conclusions, {"human_review_required", None})
        self.assertIn("human_review_required", (source / "rules.metta").read_text(encoding="utf-8"))
        self.assertIn("illustrative", (source / "rules.metta").read_text(encoding="utf-8").lower())
        self.assertIn("synthetic", (source / "README.md").read_text(encoding="utf-8").lower())
        self.assertIn("fixture", (source / "example-receipt.md").read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
