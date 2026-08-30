"""Loopback-only Studio server for the story-first OmegaClaw journey."""

from __future__ import annotations

import json
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Optional, Type
from urllib.parse import urlparse

from .artifacts import ArtifactNotFound, StudioArtifacts, UnknownArtifact
from .ui import PAGE


HOST = "127.0.0.1"
PORT = 8765
MAX_REQUEST_BYTES = 4096
MAX_IMAGE_BYTES = 8 * 1024 * 1024
WORKSPACE_SLUG = re.compile(r"[a-z0-9][a-z0-9-]{0,62}\Z")
CopyTemplate = Callable[[str], Path]
STATIC_IMAGES = {
    "/assets/lighthouse-hero.png": "omegaclaw-lighthouse-hero.png",
    "/assets/lighthouse-story-wide.png": "omegaclaw-lighthouse-story-wide.png",
}


def require_loopback(host: str) -> None:
    """Studio never supports public or LAN binds."""
    if host != HOST:
        raise ValueError("Studio only binds to 127.0.0.1")


def _safe_json(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")


def _page() -> str:
    """Return the English, story-first Wizard."""
    return PAGE


def _static_image(workspace: Path, filename: str) -> bytes:
    """Read one fixed project image without exposing a path endpoint."""
    workspace = workspace.resolve(strict=True)
    asset_root = workspace / "deliverables" / "assets"
    candidate = asset_root / filename
    try:
        resolved_root = asset_root.resolve(strict=True)
        resolved_candidate = candidate.resolve(strict=True)
        resolved_root.relative_to(workspace)
        resolved_candidate.relative_to(resolved_root)
    except (OSError, ValueError) as error:
        raise FileNotFoundError("Studio image is not available") from error
    if asset_root.is_symlink() or candidate.is_symlink() or not resolved_candidate.is_file():
        raise FileNotFoundError("Studio image is not available")
    if resolved_candidate.stat().st_size > MAX_IMAGE_BYTES:
        raise FileNotFoundError("Studio image is not available")
    return resolved_candidate.read_bytes()


def _handler_class(artifacts: StudioArtifacts, copy_template: Optional[CopyTemplate]) -> Type[BaseHTTPRequestHandler]:
    class StudioHandler(BaseHTTPRequestHandler):
        server_version = "OmegaClawLaunchpadStudio/0.3"

        def log_message(self, format: str, *args: Any) -> None:
            """Do not echo request contents to terminal logs."""

        def _send(self, status: HTTPStatus, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
                "img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; "
                "frame-ancestors 'none'",
            )
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status: HTTPStatus, payload: Any) -> None:
            self._send(status, "application/json; charset=utf-8", _safe_json(payload))

        def _error(self, status: HTTPStatus, message: str) -> None:
            self._json(status, {"error": message})

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/":
                self._send(HTTPStatus.OK, "text/html; charset=utf-8", _page().encode("utf-8"))
                return
            if path in STATIC_IMAGES:
                try:
                    body = _static_image(artifacts.workspace, STATIC_IMAGES[path])
                except FileNotFoundError:
                    self._error(HTTPStatus.NOT_FOUND, "Studio image is not available.")
                    return
                self._send(HTTPStatus.OK, "image/png", body)
                return
            if path == "/api/status":
                self._json(HTTPStatus.OK, artifacts.status())
                return
            workspace_prefix = "/api/workspaces/"
            if path.startswith(workspace_prefix) and path.endswith("/tests"):
                workspace_id = path[len(workspace_prefix):-len("/tests")].strip("/")
                if not workspace_id or "/" in workspace_id:
                    self._error(HTTPStatus.NOT_FOUND, "Unknown Studio route.")
                    return
                try:
                    self._json(HTTPStatus.OK, artifacts.workspace_tests(workspace_id))
                except ArtifactNotFound:
                    self._error(HTTPStatus.NOT_FOUND, "Workspace tests are not available yet.")
                return
            prefix = "/api/artifacts/"
            if path.startswith(prefix):
                name = path[len(prefix):]
                if not name or "/" in name:
                    self._error(HTTPStatus.NOT_FOUND, "Unknown Studio route.")
                    return
                try:
                    self._json(HTTPStatus.OK, artifacts.artifact(name))
                except UnknownArtifact:
                    self._error(HTTPStatus.NOT_FOUND, "Unknown Studio artifact.")
                except ArtifactNotFound:
                    self._error(HTTPStatus.NOT_FOUND, "This artifact is not available yet.")
                return
            self._error(HTTPStatus.NOT_FOUND, "Unknown Studio route.")

        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/api/examples/lighthouse-in-the-fog/copy":
                self._error(HTTPStatus.NOT_FOUND, "Unknown Studio route.")
                return
            if copy_template is None:
                self._error(HTTPStatus.SERVICE_UNAVAILABLE, "Example copy is not available in this server process.")
                return
            if self.headers.get_content_type() != "application/json":
                self._error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "The copy request must use application/json.")
                return
            try:
                length = int(self.headers.get("Content-Length") or "-1")
            except ValueError:
                length = -1
            if length < 1 or length > MAX_REQUEST_BYTES:
                self._error(HTTPStatus.BAD_REQUEST, "The copy request is invalid.")
                return
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._error(HTTPStatus.BAD_REQUEST, "The copy request must be JSON.")
                return
            name = payload.get("name") if isinstance(payload, dict) else None
            if not isinstance(name, str) or WORKSPACE_SLUG.fullmatch(name) is None:
                self._error(HTTPStatus.BAD_REQUEST, "Workspace names use lowercase letters, numbers, and dashes only.")
                return
            try:
                copy_template(name)
            except (FileExistsError, ValueError, OSError):
                self._error(HTTPStatus.CONFLICT, "The workspace could not be copied.")
                return
            self._json(HTTPStatus.CREATED, {"workspace_id": name})

        def do_PUT(self) -> None:  # noqa: N802
            self._error(HTTPStatus.METHOD_NOT_ALLOWED, "Studio does not support this method.")

        def do_DELETE(self) -> None:  # noqa: N802
            self._error(HTTPStatus.METHOD_NOT_ALLOWED, "Studio does not support this method.")

    return StudioHandler


def create_server(
    workspace: Path, *, host: str = HOST, copy_template: Optional[CopyTemplate] = None
) -> ThreadingHTTPServer:
    require_loopback(host)
    return ThreadingHTTPServer((HOST, PORT), _handler_class(StudioArtifacts(workspace), copy_template))


def serve(workspace: Path, *, host: str = HOST, copy_template: Optional[CopyTemplate] = None) -> None:
    server = create_server(workspace, host=host, copy_template=copy_template)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
