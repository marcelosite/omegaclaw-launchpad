"""A deliberately small loopback-only HTTP reader for Studio P0."""

from __future__ import annotations

import json
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Optional, Type
from urllib.parse import urlparse

from .artifacts import ArtifactNotFound, StudioArtifacts, UnknownArtifact


HOST = "127.0.0.1"
PORT = 8765
MAX_REQUEST_BYTES = 4096
WORKSPACE_SLUG = re.compile(r"[a-z0-9][a-z0-9-]{0,62}\Z")
CopyTemplate = Callable[[str], Path]


def require_loopback(host: str) -> None:
    """P0 never supports public or LAN binds."""
    if host != HOST:
        raise ValueError("Studio P0 only binds to 127.0.0.1")


def _safe_json(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")


def _page() -> str:
    """Return static HTML; runtime artifact text is inserted only by JS textContent."""
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>OmegaClaw Launchpad Studio</title>
<style>
:root { color-scheme: dark; --ink:#eaf0ff; --muted:#aab7d2; --line:#31405e; --panel:#111a2d; --accent:#73d9b0; --warn:#f0be62; --bad:#ff8a96; }
* { box-sizing:border-box; } body { max-width:960px; margin:0 auto; padding:24px 24px 104px; background:#090e1b; color:var(--ink); font:16px/1.5 system-ui,sans-serif; }
header { border-bottom:1px solid var(--line); margin-bottom:20px; } h1 { margin:0; font-size:1.65rem; } .sub { color:var(--muted); margin-top:4px; }
nav { display:flex; gap:8px; flex-wrap:wrap; margin:20px 0; } button, input { font:inherit; } button { cursor:pointer; border:1px solid var(--line); border-radius:7px; padding:8px 12px; background:#15213a; color:var(--ink); }
button:hover { border-color:var(--accent); } input { width:min(100%,340px); padding:8px; border:1px solid var(--line); border-radius:7px; background:#0b1222; color:var(--ink); }
a { color:#8dc6ff; } a:visited { color:#c2a7ff; }
.screen { display:none; } .screen.active { display:block; } .card { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:18px; margin:14px 0; }
.status { font-weight:700; text-transform:uppercase; } .verified { color:var(--accent); } .ready { color:#8dc6ff; } .pending { color:var(--warn); } .failed { color:var(--bad); }
pre { white-space:pre-wrap; overflow-wrap:anywhere; margin:12px 0 0; padding:12px; border-radius:7px; background:#080d19; border:1px solid var(--line); color:#d8e4fc; }
.pipeline { display:flex; flex-wrap:wrap; gap:8px; align-items:center; color:var(--muted); } .pipeline b { color:var(--ink); } .note { color:var(--muted); }
.wizard-controls { position:fixed; z-index:10; left:0; right:0; bottom:0; display:flex; justify-content:center; padding:12px 24px; border-top:1px solid var(--line); background:rgba(9,14,27,.96); backdrop-filter:blur(10px); } .wizard-controls-inner { width:min(912px,100%); display:flex; align-items:center; justify-content:space-between; gap:12px; } .wizard-position { color:var(--muted); font-size:.9rem; } button:disabled { cursor:not-allowed; opacity:.45; } .primary { background:#1d6b50; border-color:#48b685; }
@media (max-width:600px) { body { padding:16px 16px 112px; } .wizard-controls { padding:10px 16px; } .wizard-position { display:none; } }
</style></head><body>
<header><h1>OmegaClaw Launchpad Studio</h1><p class="sub">A local, read-only First Proof laboratory. No API key. No remote exposure.</p></header>
<nav aria-label="Studio steps"><button data-screen="welcome">1 Welcome</button><button data-screen="preflight">2 Preflight</button><button data-screen="proof">3 First proof</button><button data-screen="learn">4 Learn</button><button data-screen="template">5 Factory-fault</button></nav>
<main>
<section id="welcome" class="screen active"><div class="card"><h2>Welcome</h2><p>Studio reads evidence produced by the existing First Reflection workflow. It does not run Docker, change rules, execute actions, or claim that a fixture proves anything about the outside world.</p><p>Use the steps above to inspect the local preflight, proof, and receipt.</p></div></section>
<section id="preflight" class="screen"><h2>Preflight</h2><div id="preflight-card" class="card"></div><button data-artifact="preflight">Open preflight artifact</button><pre id="preflight-output" hidden></pre></section>
<section id="proof" class="screen"><h2>First real proof</h2><div id="proof-card" class="card"></div><p class="note">The known runner remains outside this dashboard. On a clean workspace, run these exact commands in a terminal; Studio will only read the resulting artifacts.</p><pre>python3 -m launchpad reflect demo
scripts/run-omegaclaw-proof.sh
python3 -m launchpad reflect receipt</pre><button data-artifact="reflection-context">Open frozen facts</button> <button data-artifact="omega-proof">Open proof artifact</button> <button data-artifact="receipt">Open receipt</button><pre id="proof-output" hidden></pre></section>
<section id="learn" class="screen"><h2>Learn from the recorded chain</h2><div class="card"><div class="pipeline"><b>agent/Test</b><span>→</span><b>frozen facts</b><span>→</span><b>MeTTa/NAL</b><span>→</span><b>STV</b><span>→</span><b>channel response</b><span>→</span><b>receipt</b></div><p class="note">Each link is evidence, not a claim of external truth. A verified proof requires the recorded pinned Test/WebSocket contract, observed MeTTa use, and NAL/STV in the loop.</p></div><button data-artifact="reflection-context">Frozen facts</button> <button data-artifact="omega-proof">Proof</button> <button data-artifact="receipt">Receipt</button><pre id="learn-output" hidden></pre></section>
<section id="template" class="screen"><h2>Factory-fault template</h2><div id="template-card" class="card"></div><p>This tutorial is fully synthetic. It may derive <code>manual_inspection_recommended</code> when two synthetic signals coexist. It does not diagnose equipment, identify a cause, validate external data, or issue a machine command. Its MeTTa file is an illustrative lesson scaffold; Studio P0 does not run it in the real OmegaClaw runtime.</p><p><button data-artifact="template-readme">README</button> <button data-artifact="template-workspace">Workspace contract</button> <button data-artifact="template-facts">Facts</button> <button data-artifact="template-rules-md">Human rules</button> <button data-artifact="template-rules-metta">Illustrative MeTTa lesson</button> <button data-artifact="template-tests">Tests</button> <button data-artifact="template-receipt">Fixture receipt</button></p><label for="workspace-name">Copy to workspace</label><br><input id="workspace-name" autocomplete="off" placeholder="my-case" pattern="[a-z0-9][a-z0-9-]{0,62}"><button id="copy-template">Copy factory-fault</button><p id="copy-result" class="note" aria-live="polite"></p><pre id="template-output" hidden></pre><div class="card"><h3>Graduate to Real Omega</h3><p>Graduate only after the safe Studio/Test path is understood and a human approves the change in risk.</p><ol><li>Read the official OmegaClaw risk disclaimer before enabling an autonomous runtime.</li><li>Follow the official pinned Quick Start instead of copying credentials into Studio.</li><li>For MiniMax, use the documented <code>ASICloud</code> provider path and verify the current provider contract before supplying any key.</li><li>Use a private, owner-controlled channel, keep its authentication secret outside Studio and receipts, and grant only the minimum permissions needed.</li></ol><p><a href="https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/README.md#run-omegaclaw-in-docker" target="_blank" rel="noreferrer noopener">Official OmegaClaw Quick Start (v0.1.19)</a> · <a href="https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/README.md#disclaimer" target="_blank" rel="noreferrer noopener">Read the official risk disclaimer</a></p><p class="note">This section is guidance only. Studio does not collect keys, configure a provider, open a channel, or grant permissions.</p></div></section>
</main>
<footer class="wizard-controls" aria-label="Wizard navigation"><div class="wizard-controls-inner"><button id="wizard-back" type="button" disabled>Back</button><span id="wizard-position" class="wizard-position" aria-live="polite">Step 1 of 5</span><button id="wizard-next" class="primary" type="button">Next</button></div></footer>
<script>
const outputFor = {preflight:'preflight-output', proof:'proof-output', learn:'learn-output', template:'template-output'};
const screens = ['welcome','preflight','proof','learn','template'];
let activeScreen = 0;
function selectedScreen(button) { return button.closest('.screen')?.id || 'proof'; }
function setText(id, value) { const el=document.getElementById(id); el.textContent=value; el.hidden=false; }
function stateCard(id, label, item) { const el=document.getElementById(id); el.replaceChildren(); const heading=document.createElement('p'); const state=document.createElement('span'); state.className='status '+item.state; state.textContent=item.state; heading.append(label+': ', state); const detail=document.createElement('p'); detail.textContent=item.detail || ''; el.append(heading, detail); }
function showScreen(index) { activeScreen=Math.max(0,Math.min(index,screens.length-1)); document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active')); document.getElementById(screens[activeScreen]).classList.add('active'); document.getElementById('wizard-back').disabled=activeScreen===0; document.getElementById('wizard-next').disabled=activeScreen===screens.length-1; document.getElementById('wizard-position').textContent='Step '+(activeScreen+1)+' of '+screens.length; }
async function artifact(name, screen) { const response=await fetch('/api/artifacts/'+encodeURIComponent(name)); const payload=await response.json(); setText(outputFor[screen], response.ok ? payload.content : payload.error); }
async function refresh() { const response=await fetch('/api/status'); const status=await response.json(); stateCard('preflight-card','Preflight',status.preflight); stateCard('proof-card','Proof',status.proof); const template={state:status.template.state, detail:status.template.available_artifacts.length ? 'Available artifacts: '+status.template.available_artifacts.join(', ') : 'The template is not available.'}; stateCard('template-card','Template',template); }
document.querySelectorAll('[data-screen]').forEach(button => button.addEventListener('click', () => showScreen(screens.indexOf(button.dataset.screen))));
document.getElementById('wizard-back').addEventListener('click', () => showScreen(activeScreen-1));
document.getElementById('wizard-next').addEventListener('click', () => showScreen(activeScreen+1));
document.querySelectorAll('[data-artifact]').forEach(button => button.addEventListener('click', () => artifact(button.dataset.artifact, selectedScreen(button))));
document.getElementById('copy-template').addEventListener('click', async () => { const name=document.getElementById('workspace-name').value; const result=document.getElementById('copy-result'); const response=await fetch('/api/templates/factory-fault/copy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name})}); const payload=await response.json(); result.textContent=response.ok ? 'Workspace copied: '+payload.workspace_id : payload.error; });
refresh().catch(() => { document.getElementById('proof-card').textContent='Studio could not read its local status.'; });
</script></body></html>"""


def _handler_class(artifacts: StudioArtifacts, copy_template: Optional[CopyTemplate]) -> Type[BaseHTTPRequestHandler]:
    class StudioHandler(BaseHTTPRequestHandler):
        server_version = "OmegaClawLaunchpadStudio/0.1"

        def log_message(self, format: str, *args: Any) -> None:
            """Do not echo request contents to a terminal log."""

        def _send(self, status: HTTPStatus, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status: HTTPStatus, payload: Any) -> None:
            self._send(status, "application/json; charset=utf-8", _safe_json(payload))

        def _error(self, status: HTTPStatus, message: str) -> None:
            self._json(status, {"error": message})

        def do_GET(self) -> None:  # noqa: N802 - required stdlib hook name
            path = urlparse(self.path).path
            if path == "/":
                self._send(HTTPStatus.OK, "text/html; charset=utf-8", _page().encode("utf-8"))
                return
            if path == "/api/status":
                self._json(HTTPStatus.OK, artifacts.status())
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

        def do_POST(self) -> None:  # noqa: N802 - required stdlib hook name
            if urlparse(self.path).path != "/api/templates/factory-fault/copy":
                self._error(HTTPStatus.NOT_FOUND, "Unknown Studio route.")
                return
            if copy_template is None:
                self._error(HTTPStatus.SERVICE_UNAVAILABLE, "Template copy is not available in this server process.")
                return
            if self.headers.get_content_type() != "application/json":
                self._error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "The copy request must use application/json.")
                return
            length_header = self.headers.get("Content-Length")
            try:
                length = int(length_header or "-1")
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
            except Exception:
                self._error(HTTPStatus.INTERNAL_SERVER_ERROR, "The workspace copy did not complete.")
                return
            self._json(HTTPStatus.CREATED, {"workspace_id": name})

        def do_PUT(self) -> None:  # noqa: N802
            self._error(HTTPStatus.METHOD_NOT_ALLOWED, "Studio P0 does not support this method.")

        def do_DELETE(self) -> None:  # noqa: N802
            self._error(HTTPStatus.METHOD_NOT_ALLOWED, "Studio P0 does not support this method.")

    return StudioHandler


def create_server(workspace: Path, *, host: str = HOST, copy_template: Optional[CopyTemplate] = None) -> ThreadingHTTPServer:
    """Create the fixed local-only server.  Port and host are not configurable."""
    require_loopback(host)
    return ThreadingHTTPServer((HOST, PORT), _handler_class(StudioArtifacts(workspace), copy_template))


def serve(workspace: Path, *, host: str = HOST, copy_template: Optional[CopyTemplate] = None) -> None:
    """Serve until the foreground process receives an interrupt."""
    server = create_server(workspace, host=host, copy_template=copy_template)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
