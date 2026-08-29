import json
import http.client
import tempfile
import threading
import unittest
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path

from launchpad.studio.artifacts import StudioArtifacts
from launchpad.studio.server import HOST, PORT, WORKSPACE_SLUG, _handler_class, _page, require_loopback


class StudioServerTests(unittest.TestCase):
    def test_loopback_is_fixed(self):
        require_loopback(HOST)
        with self.assertRaises(ValueError):
            require_loopback("0.0.0.0")
        self.assertEqual(PORT, 8765)

    def test_page_has_nine_wizard_screens_and_safe_artifact_rendering(self):
        page = _page()
        self.assertEqual(page.count('class="screen'), 9)
        self.assertIn("textContent", page)
        self.assertNotIn("innerHTML", page)
        self.assertIn("/api/templates/factory-fault/copy", page)
        self.assertIn('id="wizard-back"', page)
        self.assertIn('id="wizard-next"', page)
        self.assertIn("function show(n)", page)
        self.assertIn("Illustrative MeTTa lesson", page)
        self.assertIn("MCP", page)
        self.assertIn("Finish", page)
        self.assertIn("omega.reason", page)
        self.assertIn("omega.get_receipt", page)
        self.assertIn("Create my workspace", page)
        self.assertIn("Blocked:", page)
        self.assertIn("name=\"decision\"", page)
        self.assertIn("confirm-preflight", page)
        self.assertIn("confirm-proof", page)
        self.assertIn("confirm-tests", page)
        self.assertIn("confirm-mcp", page)
        self.assertIn("Check my result", page)
        self.assertIn("Check my proof", page)
        self.assertIn("Open the receipt", page)
        self.assertIn("Complete the step above", page)
        self.assertIn("if(n<active)show(n)", page)
        self.assertIn("codex mcp add omegaclaw-launchpad", page)
        self.assertNotIn("Reviewed MeTTa", page)
        self.assertIn("data-place-label", page)
        self.assertIn("cannot prove who ran the command", page)
        self.assertIn("This page does not run them", page)
        self.assertIn("Studio does not connect my agent", page)
        self.assertIn("Fictional facts → human rule → real OmegaClaw", page)

    def test_workspace_slug_disallows_paths_and_uppercase(self):
        self.assertIsNotNone(WORKSPACE_SLUG.fullmatch("my-case-2"))
        for value in ("../outside", "my_case", "My-case", "", "a/b"):
            self.assertIsNone(WORKSPACE_SLUG.fullmatch(value))

    def test_json_errors_do_not_reflect_request_content_as_html(self):
        payload = {"error": "Unknown Studio route."}
        encoded = json.dumps(payload).encode("utf-8")
        self.assertEqual(json.loads(encoded.decode("utf-8"))["error"], "Unknown Studio route.")
        self.assertEqual(HTTPStatus.NOT_FOUND.value, 404)

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
                    "POST", "/api/templates/factory-fault/copy", body, {"Content-Type": "application/json"}
                )
                self.assertEqual(status, HTTPStatus.CREATED)
                self.assertEqual(payload, {"workspace_id": "my-case"})
                self.assertNotIn(str(workspace), json.dumps(payload))
                self.assertEqual(copied, ["my-case"])

                status, _payload = request(
                    "POST",
                    "/api/templates/factory-fault/copy",
                    json.dumps({"name": "../bad"}),
                    {"Content-Type": "application/json"},
                )
                self.assertEqual(status, HTTPStatus.BAD_REQUEST)
                self.assertEqual(copied, ["my-case"])

                status, _payload = request(
                    "POST",
                    "/api/templates/factory-fault/copy",
                    json.dumps({"name": "another-case"}),
                    {"Content-Type": "text/plain"},
                )
                self.assertEqual(status, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
                self.assertEqual(copied, ["my-case"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join()


if __name__ == "__main__":
    unittest.main()
