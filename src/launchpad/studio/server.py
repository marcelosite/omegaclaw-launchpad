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
.status { font-weight:700; text-transform:uppercase; } .verified { color:var(--accent); } .ready { color:#8dc6ff; } .pending { color:var(--warn); } .failed { color:var(--bad); } .step-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:10px; margin:14px 0; } .step-grid .card { margin:0; } .callout { border-left:3px solid var(--accent); padding-left:14px; } .success { border-color:var(--accent); }
pre { white-space:pre-wrap; overflow-wrap:anywhere; margin:12px 0 0; padding:12px; border-radius:7px; background:#080d19; border:1px solid var(--line); color:#d8e4fc; }
.pipeline { display:flex; flex-wrap:wrap; gap:8px; align-items:center; color:var(--muted); } .pipeline b { color:var(--ink); } .note { color:var(--muted); }
.wizard-controls { position:fixed; z-index:10; left:0; right:0; bottom:0; display:flex; justify-content:center; padding:12px 24px; border-top:1px solid var(--line); background:rgba(9,14,27,.96); backdrop-filter:blur(10px); } .wizard-controls-inner { width:min(912px,100%); display:flex; align-items:center; justify-content:space-between; gap:12px; } .wizard-position { color:var(--muted); font-size:.9rem; } button:disabled { cursor:not-allowed; opacity:.45; } .primary { background:#1d6b50; border-color:#48b685; }
@media (max-width:600px) { body { padding:16px 16px 112px; } .wizard-controls { padding:10px 16px; } .wizard-position { display:none; } }
</style></head><body>
<header><h1>OmegaClaw Launchpad Studio</h1><p class="sub">A guided local path from a safe Test proof to your first governed OmegaClaw case.</p></header>
<nav aria-label="Studio steps"><button data-screen="welcome">1 Welcome</button><button data-screen="preflight">2 System check</button><button data-screen="proof">3 First proof</button><button data-screen="learn">4 Understand</button><button data-screen="template">5 Your case</button><button data-screen="finish">6 Finish</button></nav>
<main>
<section id="welcome" class="screen active"><div class="card"><h2>Welcome</h2><p>In six short steps you will verify a real OmegaClaw Test/WebSocket proof, understand the evidence chain, create a safe local case, and see the next handoff to Codex.</p><div class="callout"><p><strong>What you will have at the end:</strong> a verified runtime receipt, a readable workspace, and a clear decision about what happens next.</p></div><p>Studio never asks for an LLM key, opens a public port, edits rules, or performs an external action.</p></div></section>
<section id="preflight" class="screen"><h2>System check</h2><div id="preflight-card" class="card"></div><p>These checks answer one question: can this machine run the pinned first proof safely?</p><button data-artifact="preflight">Read the check report</button><pre id="preflight-output" hidden></pre></section>
<section id="proof" class="screen"><h2>First real proof</h2><div id="proof-card" class="card"></div><p class="note">The Codex/terminal runner performs the proof; Studio reads its evidence. This keeps Docker authority out of the browser.</p><div class="step-grid"><div class="card"><strong>1. Runtime</strong><br>OmegaClaw v0.1.19 starts.</div><div class="card"><strong>2. Channel</strong><br>Private test WebSocket connects.</div><div class="card"><strong>3. Provider</strong><br>Deterministic Test response returns.</div><div class="card"><strong>4. Reasoning</strong><br>MeTTa and NAL/STV are observed.</div><div class="card"><strong>5. Receipt</strong><br>The result is recorded for review.</div></div><p>On a clean workspace, ask Codex to run these exact commands:</p><pre>python3 -m launchpad reflect demo
scripts/run-omegaclaw-proof.sh
python3 -m launchpad reflect receipt</pre><button data-artifact="reflection-context">Open frozen facts</button> <button data-artifact="omega-proof">Open proof artifact</button> <button data-artifact="receipt">Open receipt</button><pre id="proof-output" hidden></pre></section>
<section id="learn" class="screen"><h2>Understand the evidence chain</h2><div class="card"><div class="pipeline"><b>agent request</b><span>→</span><b>frozen facts</b><span>→</span><b>human rule</b><span>→</span><b>MeTTa/NAL</b><span>→</span><b>result</b><span>→</span><b>receipt</b></div><div class="step-grid"><div class="card"><strong>Facts</strong><br>What Omega was allowed to use.</div><div class="card"><strong>Rules</strong><br>What a human wrote down first.</div><div class="card"><strong>Runtime</strong><br>What MeTTa/NAL actually processed.</div><div class="card"><strong>Receipt</strong><br>What another person can verify.</div></div><p class="note">Evidence is not external truth. A verified proof means the pinned Test/WebSocket contract, real MeTTa skill, and NAL/STV loop were observed.</p></div><button data-artifact="reflection-context">Frozen facts</button> <button data-artifact="omega-proof">Proof</button> <button data-artifact="receipt">Receipt</button><pre id="learn-output" hidden></pre></section>
<section id="template" class="screen"><h2>Your first governed case</h2><div id="template-card" class="card"></div><p>Start with the factory-fault lesson, then copy it into your own workspace. This tutorial is fully synthetic. It may derive <code>manual_inspection_recommended</code> when two synthetic signals coexist. It does not diagnose equipment, identify a cause, validate external data, or issue a machine command. Its MeTTa file is an illustrative lesson scaffold until the separate real-runtime proof is run.</p><p><button data-artifact="template-readme">Why this lesson</button> <button data-artifact="template-workspace">Workspace contract</button> <button data-artifact="template-facts">Facts</button> <button data-artifact="template-rules-md">Human rules</button> <button data-artifact="template-rules-metta">Illustrative MeTTa lesson</button> <button data-artifact="template-tests">Expected tests</button> <button data-artifact="template-receipt">Fixture receipt</button></p><label for="workspace-name">Choose a local workspace ID</label><br><input id="workspace-name" autocomplete="off" placeholder="my-case" pattern="[a-z0-9][a-z0-9-]{0,62}"><button id="copy-template">Create my workspace</button><p id="copy-result" class="note" aria-live="polite"></p><pre id="template-output" hidden></pre><div class="card"><h3>Graduate to Real Omega</h3><p>Graduate only after the safe Studio/Test path is understood and a human approves the change in risk.</p><ol><li>Read the official OmegaClaw risk disclaimer before enabling an autonomous runtime.</li><li>Follow the official pinned Quick Start instead of copying credentials into Studio.</li><li>For MiniMax, use the documented <code>ASICloud</code> provider path and verify the current provider contract before supplying any key.</li><li>Use a private, owner-controlled channel, keep its authentication secret outside Studio and receipts, and grant only the minimum permissions needed.</li></ol><p><a href="https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/README.md#run-omegaclaw-in-docker" target="_blank" rel="noreferrer noopener">Official OmegaClaw Quick Start (v0.1.19)</a> · <a href="https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/README.md#disclaimer" target="_blank" rel="noreferrer noopener">Read the official risk disclaimer</a></p><p class="note">This section is guidance only. Studio does not collect keys, configure a provider, open a channel, or grant permissions.</p></div></section>
<section id="finish" class="screen"><h2>Finish</h2><div id="finish-card" class="card success"></div><div class="card"><h3>What you can do next</h3><ol><li>Ask Codex to adapt the copied workspace while preserving the human rule and tests.</li><li>Review the generated files and receipt before treating any result as meaningful.</li><li>When the real factory-fault proof is verified, connect Codex through the local Launchpad MCP.</li></ol><p class="note">The MCP bridge is intentionally not enabled by this Wizard yet. It will expose only <code>omega.reason</code> and <code>omega.get_receipt</code>, with no shell, connectors, or external actions.</p></div><p><button data-artifact="factory-proof">Open factory proof</button> <button data-artifact="factory-receipt">Open factory receipt</button><pre id="finish-output" hidden></pre></section>
</main>
<footer class="wizard-controls" aria-label="Wizard navigation"><div class="wizard-controls-inner"><button id="wizard-back" type="button" disabled>Back</button><span id="wizard-position" class="wizard-position" aria-live="polite">Step 1 of 6</span><button id="wizard-next" class="primary" type="button">Next</button></div></footer>
<script>
const outputFor = {preflight:'preflight-output', proof:'proof-output', learn:'learn-output', template:'template-output', finish:'finish-output'};
const screens = ['welcome','preflight','proof','learn','template','finish'];
const nextLabels = ['Start setup','Check system','Understand the proof','Try a guided case','Finish','Done'];
let activeScreen = 0;
function selectedScreen(button) { return button.closest('.screen')?.id || 'proof'; }
function setText(id, value) { const el=document.getElementById(id); el.textContent=value; el.hidden=false; }
function stateCard(id, label, item) { const el=document.getElementById(id); el.replaceChildren(); const heading=document.createElement('p'); const state=document.createElement('span'); state.className='status '+item.state; state.textContent=item.state; heading.append(label+': ', state); const detail=document.createElement('p'); detail.textContent=item.detail || ''; el.append(heading, detail); }
function showScreen(index) { activeScreen=Math.max(0,Math.min(index,screens.length-1)); document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active')); document.getElementById(screens[activeScreen]).classList.add('active'); document.getElementById('wizard-back').disabled=activeScreen===0; document.getElementById('wizard-next').disabled=activeScreen===screens.length-1; document.getElementById('wizard-next').textContent=nextLabels[activeScreen]; document.getElementById('wizard-position').textContent='Step '+(activeScreen+1)+' of '+screens.length; }
async function artifact(name, screen) { const response=await fetch('/api/artifacts/'+encodeURIComponent(name)); const payload=await response.json(); setText(outputFor[screen], response.ok ? payload.content : payload.error); }
async function refresh() { const response=await fetch('/api/status'); const status=await response.json(); stateCard('preflight-card','System check',status.preflight); stateCard('proof-card','First proof',status.proof); const template={state:status.template.state, detail:status.template.available_artifacts.length ? 'Lesson files ready. Copy one into your own workspace.' : 'The template is not available.'}; stateCard('template-card','Factory-fault lesson',template); const finish=document.getElementById('finish-card'); finish.replaceChildren(); const heading=document.createElement('p'); heading.append('Current handoff: ', Object.assign(document.createElement('span'), {className:'status '+status.handoff.state, textContent:status.handoff.state})); const detail=document.createElement('p'); detail.textContent=status.handoff.detail; finish.append(heading,detail); }
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
