import json
import http.client
import tempfile
import threading
import unittest
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path

from launchpad.studio.artifacts import StudioArtifacts
from launchpad.studio.server import (
    HOST, PORT, STATIC_IMAGES, WORKSPACE_SLUG, _handler_class, _page,
    require_loopback,
)


class StudioServerTests(unittest.TestCase):
    def test_loopback_is_fixed(self):
        require_loopback(HOST)
        with self.assertRaises(ValueError):
            require_loopback("0.0.0.0")
        self.assertEqual(PORT, 8765)

    def test_page_is_story_first_english_journey(self):
        page = _page()
        self.assertEqual(page.count('class="screen'), 8)
        self.assertIn("The Lighthouse in the Fog", page)
        for label in ("Intro", "Input", "Memory", "Verify", "Reason", "Explain", "Understand", "Play"):
            self.assertIn(label, page)
        self.assertIn("Follow the story to see how", page)
        self.assertIn("I understand the story and the problems it solves", page)
        self.assertIn("I want to play with OmegaClaw", page)
        self.assertIn("Copy prompt for my LLM", page)
        self.assertIn("The keeper decides", page)
        self.assertIn("/assets/lighthouse-hero.png", page)
        self.assertIn("/assets/lighthouse-story-wide.png", page)
        self.assertIn("data-primary", page)
        self.assertIn("textContent", page)
        self.assertNotIn("innerHTML", page)
        self.assertNotIn("O Farol", page)
        self.assertNotIn("Hospital", page)
        self.assertNotIn("Factory", page)
        self.assertNotIn("Community", page)
        self.assertNotIn("scripts/run-community-care-proof.sh", page)
        self.assertNotIn("codex mcp add", page)
        self.assertIn("Checking the real Docker proof", page)

    def test_each_screen_has_one_primary_action_and_progress_is_not_clickable(self):
        page = _page()
        self.assertEqual(page.count("data-primary"), 8)
        self.assertIn("progress-bar", page)
        self.assertNotIn("onclick=\"show", page)

    def test_allowlisted_story_images_exist_and_are_png(self):
        workspace = Path(__file__).resolve().parents[1]
        server = ThreadingHTTPServer((HOST, 0), _handler_class(StudioArtifacts(workspace), None))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for route in STATIC_IMAGES:
                connection = http.client.HTTPConnection(HOST, server.server_port, timeout=2)
                try:
                    connection.request("GET", route)
                    response = connection.getresponse()
                    body = response.read()
                    self.assertEqual(response.status, HTTPStatus.OK)
                    self.assertEqual(response.getheader("Content-Type"), "image/png")
                    self.assertTrue(body.startswith(b"\x89PNG\r\n\x1a\n"))
                finally:
                    connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_workspace_slug_disallows_paths_and_uppercase(self):
        self.assertIsNotNone(WORKSPACE_SLUG.fullmatch("my-case-2"))
        for value in ("../outside", "my_case", "My-case", "", "a/b"):
            self.assertIsNone(WORKSPACE_SLUG.fullmatch(value))

    def test_http_allowlist_and_copy_callback(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            copied = []

            def copy_template(name: str) -> Path:
                copied.append(name)
                return workspace / ".launchpad" / "studio" / "workspaces" / name

            server = ThreadingHTTPServer((HOST, 0), _handler_class(StudioArtifacts(workspace), copy_template))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                def request(method, path, body=None, headers=None):
                    connection = http.client.HTTPConnection(HOST, server.server_port, timeout=2)
                    try:
                        connection.request(method, path, body, headers or {})
                        response = connection.getresponse()
                        return response.status, json.loads(response.read())
                    finally:
                        connection.close()

                status, payload = request("GET", "/api/artifacts/../../etc/passwd")
                self.assertEqual(status, HTTPStatus.NOT_FOUND)
                self.assertEqual(payload["error"], "Unknown Studio route.")

                body = json.dumps({"name": "my-case"})
                status, payload = request(
                    "POST", "/api/examples/lighthouse-in-the-fog/copy", body, {"Content-Type": "application/json"}
                )
                self.assertEqual(status, HTTPStatus.CREATED)
                self.assertEqual(payload, {"workspace_id": "my-case"})
                self.assertEqual(copied, ["my-case"])

                status, _payload = request(
                    "POST", "/api/examples/lighthouse-in-the-fog/copy", json.dumps({"name": "../bad"}), {"Content-Type": "application/json"}
                )
                self.assertEqual(status, HTTPStatus.BAD_REQUEST)
                self.assertEqual(copied, ["my-case"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join()


if __name__ == "__main__":
    unittest.main()
