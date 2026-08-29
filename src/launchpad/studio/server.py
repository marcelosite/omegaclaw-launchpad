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
    return _page_v2()
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



def _page_v2() -> str:
    """Return the human-first, loopback-only Studio Wizard."""
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>OmegaClaw Launchpad Studio</title>
<style>
:root { color-scheme: dark; --ink:#f3f6ff; --muted:#aebbd4; --line:#2b3a59; --panel:#111b31; --panel2:#17243e; --accent:#79e0b5; --blue:#8dc6ff; --warn:#f4c56e; --bad:#ff8e9a; }
* { box-sizing:border-box; } body { margin:0; min-height:100vh; background:radial-gradient(circle at 10% -10%,#22365d 0,transparent 36%),#090e1b; color:var(--ink); font:16px/1.6 ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
.shell { width:min(1120px,100%); margin:0 auto; padding:32px 28px 132px; } header { display:flex; justify-content:space-between; gap:24px; padding-bottom:24px; border-bottom:1px solid var(--line); } .eyebrow,.kicker { color:var(--accent); font-size:.78rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; } h1 { max-width:700px; margin:6px 0 8px; font-size:clamp(2rem,5vw,3.35rem); line-height:1.04; letter-spacing:-.035em; } h2 { margin:0 0 8px; font-size:clamp(1.55rem,3vw,2.25rem); line-height:1.12; letter-spacing:-.02em; } h3 { margin:0 0 8px; } p { max-width:75ch; } .lede { color:var(--muted); font-size:1.08rem; } .badge { white-space:nowrap; align-self:flex-start; border:1px solid #3f5a82; border-radius:999px; padding:7px 11px; color:var(--blue); font-size:.82rem; }
.steps { display:grid; grid-template-columns:repeat(9,1fr); gap:6px; margin:24px 0 28px; } .step { min-width:0; color:var(--muted); text-align:center; font-size:.72rem; cursor:pointer; } .step .dot { width:30px; height:30px; display:grid; place-items:center; margin:0 auto 6px; border:1px solid var(--line); border-radius:50%; background:#0d1528; font-weight:800; } .step.active,.step.done { color:var(--ink); } .step.active .dot { border-color:var(--accent); background:#1d6b50; box-shadow:0 0 0 4px rgba(121,224,181,.12); } .step.done .dot { border-color:#477fa4; color:var(--blue); }
.screen { display:none; animation:rise .22s ease-out; } .screen.active { display:block; } @keyframes rise { from { opacity:0; transform:translateY(5px); } to { opacity:1; transform:none; } } .card { background:linear-gradient(145deg,var(--panel),#0e1729); border:1px solid var(--line); border-radius:16px; padding:24px; margin:16px 0; box-shadow:0 18px 50px rgba(0,0,0,.22); } .card.soft { background:var(--panel2); box-shadow:none; } .card.success { border-color:#3d916f; } .story { border-left:4px solid var(--accent); padding-left:18px; } .story strong { color:var(--accent); } .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; margin:18px 0; } .grid .card { margin:0; } .two { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; } .muted,.note { color:var(--muted); } .small { font-size:.9rem; } .status { font-weight:800; text-transform:uppercase; letter-spacing:.05em; } .verified,.ready { color:var(--accent); } .pending { color:var(--warn); } .failed { color:var(--bad); }
.pipeline { display:grid; grid-template-columns:repeat(6,1fr); gap:8px; margin:20px 0; } .pipeline > div { min-height:82px; display:grid; place-items:center; padding:11px 7px; border:1px solid #3a5276; border-radius:12px; background:#0d172a; text-align:center; font-weight:700; } .checklist { display:grid; gap:9px; margin:16px 0; } .check { display:flex; gap:10px; align-items:flex-start; padding:12px 14px; border:1px solid var(--line); border-radius:11px; background:#0d172a; } .check input { margin-top:5px; accent-color:var(--accent); } .check strong { display:block; } .check span { color:var(--muted); font-size:.92rem; } .check > span:first-of-type { color:var(--ink); }
button,input { font:inherit; } button { cursor:pointer; border:1px solid #3d5277; border-radius:10px; padding:10px 15px; background:#162541; color:var(--ink); transition:.15s ease; } button:hover:not(:disabled) { border-color:var(--accent); transform:translateY(-1px); } button:disabled { cursor:not-allowed; opacity:.42; } button.primary { background:#1d6b50; border-color:#58c99b; } button.ghost { background:transparent; } button.small-btn { padding:7px 10px; font-size:.9rem; } input[type=text] { width:min(100%,360px); padding:10px 12px; border:1px solid #3d5277; border-radius:10px; background:#0a1222; color:var(--ink); } label { font-weight:700; } a { color:var(--blue); } a:visited { color:#c5b4ff; } ol,ul { padding-left:1.25rem; } li { margin:.5rem 0; } pre { margin:12px 0 0; padding:15px; overflow:auto; white-space:pre-wrap; overflow-wrap:anywhere; border:1px solid var(--line); border-radius:11px; background:#080d18; color:#dce9ff; font:14px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace; } code { color:#c7dcff; }
.command-head { display:flex; justify-content:space-between; align-items:center; gap:12px; } .where { color:var(--blue); font-size:.88rem; font-weight:800; } .inline-actions { display:flex; flex-wrap:wrap; gap:9px; margin-top:12px; } .sr-status { min-height:1.5em; color:var(--muted); } .hidden { display:none !important; } .wizard-bar { position:fixed; z-index:20; left:0; right:0; bottom:0; display:flex; justify-content:center; padding:14px 28px; background:rgba(8,13,25,.94); border-top:1px solid var(--line); backdrop-filter:blur(14px); } .wizard-bar-inner { width:min(1064px,100%); display:flex; align-items:center; justify-content:space-between; gap:16px; } .wizard-position { color:var(--muted); font-size:.92rem; }
@media (max-width:760px) { .shell { padding:22px 16px 132px; } header { display:block; } .badge { display:inline-block; margin-top:12px; } .steps { grid-template-columns:repeat(9,minmax(52px,1fr)); overflow:auto; scrollbar-width:none; padding-bottom:4px; } .steps::-webkit-scrollbar { display:none; } .step { font-size:.63rem; } .pipeline { grid-template-columns:repeat(2,1fr); } .wizard-bar { padding:11px 16px; } }
</style></head><body><div class="shell">
<header><div><div class="eyebrow">OmegaClaw / Launchpad Studio</div><h1>Meet your reasoning referee.</h1><p class="lede">A calm, local Wizard that shows what your agents said, what was actually recorded, what rule a human approved, and what still needs a human decision.</p></div><div class="badge">No key · loopback only · files you can read</div></header>
<nav class="steps" aria-label="Studio steps"><div class="step active" data-step="0"><div class="dot">1</div>Meet Omega</div><div class="step" data-step="1"><div class="dot">2</div>Choose place</div><div class="step" data-step="2"><div class="dot">3</div>Ready?</div><div class="step" data-step="3"><div class="dot">4</div>Real proof</div><div class="step" data-step="4"><div class="dot">5</div>Evidence</div><div class="step" data-step="5"><div class="dot">6</div>Your case</div><div class="step" data-step="6"><div class="dot">7</div>Connect agent</div><div class="step" data-step="7"><div class="dot">8</div>Teach agent</div><div class="step" data-step="8"><div class="dot">9</div>Finish</div></nav>
<main>
<section id="meet" class="screen active"><div class="card story"><div class="kicker">The idea in one minute</div><h2>Omega is the referee, not the boss.</h2><p>Imagine two players arguing about whether the ball crossed the line. The referee does not invent a camera angle or kick the ball. The referee keeps the observations, applies the rule agreed before the match, and writes the match report.</p><p>Here, your agents bring claims. Omega receives recorded facts, follows a human-written rule, and returns a recommendation with a receipt. You still decide what happens.</p><div class="grid"><div class="card soft"><strong>Agents</strong><br><span class="muted">Players who make claims.</span></div><div class="card soft"><strong>Facts</strong><br><span class="muted">The camera angles we can point to.</span></div><div class="card soft"><strong>Receipt</strong><br><span class="muted">A match report another person can read.</span></div></div><label class="check"><input id="ack-boundary" type="checkbox"><span><strong>I understand the boundary.</strong> Omega recommends and records; it does not take the final action for me.</span></label></div></section>
<section id="place" class="screen"><div class="card"><div class="kicker">Step 2 · Where is the workshop?</div><h2>Pick the computer that holds your project.</h2><p>A <strong>VPS</strong> (a rented computer that stays online elsewhere) is useful later. An <strong>SSH tunnel</strong> (a private encrypted corridor) lets your own browser visit it without opening Studio to the public internet.</p><div class="two"><label class="check"><input name="place" type="radio" value="computer" checked><span><strong>My computer</strong><br>Commands run in your local terminal.</span></label><label class="check"><input name="place" type="radio" value="vps"><span><strong>My private VPS</strong><br>Commands run in the VPS terminal; the browser uses a tunnel.</span></label></div><p class="note">For this tutorial, both places use the same files and the same safe, loopback-only server.</p></div><div class="card command"><div class="command-head\"><span class="where\">Run on: your computer or VPS</span><button class="small-btn ghost\" data-copy=\"scripts/studio-doctor.sh\">Copy command</button></div><h3>Check the workshop</h3><p>Ask Codex to run this fixed check. It only writes <code>.launchpad/studio/preflight.json</code>; it does not install software or contact the internet.</p><pre>scripts/studio-doctor.sh</pre><p id="copy-place" class="sr-status" aria-live="polite"></p></div></section>
<section id="ready" class="screen"><div class="card"><div class="kicker">Step 3 · Is the workshop ready?</div><h2>We need proof that the room is safe to use.</h2><p>These are friendly checks, not a technical exam. Green means the recorded check passed. Red tells you what to fix next.</p><div id="preflight-card" class="checklist\"></div><button class="ghost" data-artifact="preflight">Read the check report</button><pre id="preflight-output" class="hidden\"></pre></div></section>
<section id="proof" class="screen"><div class="card"><div class="kicker">Step 4 · Watch one real proof</div><h2>Now watch the real OmegaClaw path.</h2><p>A temporary test actor receives fictional facts, sends them through a real WebSocket (a two-way message connection), invokes the real MeTTa skill (the reasoning language), observes NAL/STV (evidence strength and confidence), and leaves a receipt. No paid LLM and no key are needed.</p><div id="proof-card" class="checklist\"></div><div class="grid\"><div class="card soft\"><strong>Test provider</strong><br><span class="muted\">A predictable actor used for a safe rehearsal.</span></div><div class="card soft\"><strong>Human gate</strong><br><span class="muted\">A recommendation never becomes an action automatically.</span></div></div><p class="note">The dashboard reads the result; it does not run Docker from a web button.</p></div><div class="card command\"><div class="command-head\"><span class="where\">Run on: your computer or VPS</span><button class="small-btn ghost\" data-copy=\"scripts/run-factory-fault-proof.sh\">Copy command</button></div><h3>Run the pinned factory-fault proof</h3><p>Ask Codex to run this fixed command in the repository root.</p><pre>python3 -m launchpad reflect prepare
scripts/run-factory-fault-proof.sh</pre><p id="copy-proof" class="sr-status" aria-live="polite"></p></div></section>
<section id="evidence" class="screen"><div class="card"><div class="kicker">Step 5 · Open the evidence box</div><h2>Do not trust a green badge. Open the parcel.</h2><p>Each item answers a different question: what went in, what a human wrote, what the runtime saw, what came out, and what remains unknown.</p><div class="pipeline"><div>Recorded facts</div><div>Human rule</div><div>MeTTa / NAL</div><div>Result</div><div>Limitations</div><div>Receipt</div></div><div class="inline-actions\"><button data-artifact=\"reflection-context\">Facts</button><button data-artifact=\"omega-proof\">Proof</button><button data-artifact=\"receipt\">Receipt</button></div><pre id="evidence-output" class="hidden\"></pre><label class="check\"><input id="ack-synthetic" type="checkbox"><span><strong>I understand this lesson is fictional.</strong> It is a recommendation, not a diagnosis, causal claim, outside-world validation, or machine action.</span></label></div></section>
<section id="case" class="screen"><div class="card"><div class="kicker">Step 6 · Create a safe question</div><h2>Start with a question, not with jargon.</h2><p>The recommended first real use is <strong>Agent Disagreement — Release Readiness</strong>: one agent says “ready”, another says “not ready”, and a required security check has no result. Omega can recommend human review. It cannot merge, deploy, or approve the release.</p><div class="grid"><div class="card soft\"><strong>What do you want reviewed?</strong><br><span class="muted\">A bounded decision, not “do everything”.</span></div><div class="card soft\"><strong>What is recorded?</strong><br><span class="muted\">Facts and evidence labels, without guessing.</span></div><div class="card soft\"><strong>What must never happen?</strong><br><span class="muted\">Write the forbidden action before the test.</span></div></div><label for="workspace-name">Choose a local workspace ID</label><br><input id="workspace-name" type="text" autocomplete="off" placeholder="my-case" pattern=\"[a-z0-9][a-z0-9-]{0,62}\"> <button id="copy-template" class="primary">Create my workspace</button><p id="copy-result" class="sr-status" aria-live="polite"></p><div id="template-card" class="checklist"></div><div class="inline-actions\"><button data-artifact=\"template-readme\">Why this lesson</button><button data-artifact=\"template-rules-md\">Human rules</button><button data-artifact=\"template-tests\">Tests</button></div><pre id="case-output" class="hidden\"></pre></div><div class="card soft\"><h3>Illustrative MeTTa lesson</h3><p>This is a study scaffold, not a reviewed production rule. The sample factory-fault facts are fictional and do not prove a real fault or cause.</p></div></section>
<section id="connect" class="screen"><div class="card"><div class="kicker">Step 7 · Connect one agent</div><h2>Think of MCP as a standard wall socket.</h2><p><strong>MCP</strong> (a standard plug that lets an agent call approved tools) lets Codex, Claude Code, or another compatible agent consult the same local bridge. It does not give the agent a shell, a password, Docker, or permission to act.</p><div class="command\"><div class="command-head\"><span class="where\">Runs on: the computer or VPS holding this repository</span><button class="small-btn ghost\" data-copy=\"scripts/studio-mcp.sh\">Copy command</button></div><h3>Start the bridge</h3><pre>scripts/studio-mcp.sh</pre></div><div class="command\"><div class="command-head\"><span class="where\">Run on: your computer</span><button class="small-btn ghost\" data-copy=\"codex mcp add omegaclaw-launchpad -- scripts/studio-mcp.sh\">Copy command</button></div><h3>Register it with Codex</h3><pre>codex mcp add omegaclaw-launchpad -- scripts/studio-mcp.sh</pre></div><p class="note\">The bridge exposes exactly two tools: <code>omega.reason</code> and <code>omega.get_receipt</code>. It requires the verified factory-fault proof and stores logical receipt IDs under the project.</p><label class="check\"><input id="ack-connect" type="checkbox\"><span><strong>I know what is being connected.</strong> One local, bounded bridge with two consult tools and no external action.</span></label></div></section>
<section id="policy" class="screen"><div class="card\"><div class="kicker">Step 8 · Teach the agent when to ask</div><h2>Give your agent one simple rule.</h2><p>Copy this policy into the agent instructions for your project:</p><pre id="agent-policy">When agents disagree about a claim that affects a human decision, stop. Preserve each claim and its evidence. Do not ask Omega to invent missing facts. Consult the approved Omega workspace, retain the receipt ID, and show the disagreement, rule, recommendation, limitations, and receipt to the human. Never execute an external action from the recommendation alone.</pre><button class="small-btn\" data-copy=\"When agents disagree about a claim that affects a human decision, stop. Preserve each claim and its evidence. Do not ask Omega to invent missing facts. Consult the approved Omega workspace, retain the receipt ID, and show the disagreement, rule, recommendation, limitations, and receipt to the human. Never execute an external action from the recommendation alone.\">Copy agent policy</button><label class="check\"><input id="ack-policy" type="checkbox\"><span><strong>I will keep this human gate.</strong> The current bridge is a first teaching test, not general multi-agent arbitration.</span></label></div></section>
<section id="finish" class="screen"><div class="card success\"><div class="kicker">Step 9 · Finish</div><h2>You reached a useful starting line.</h2><div id="finish-card"></div><p>Next, ask your connected agent:</p><pre>Explain what Omega can prove in this workspace, what it cannot prove, and create one consultation receipt without taking an action.</pre></div><div class="card\"><h3>Your handoff</h3><ul><li>Run the real proof before trusting a consultation.</li><li>Keep the copied workspace and receipt files local and reviewable.</li><li>For the first structured disagreement, use the closed <code>release-readiness-demo</code> Conflict Packet documented in <a href=\"https://github.com/marcelosite/omegaclaw-launchpad/blob/main/docs/AGENT_GUIDE.md\" target=\"_blank\" rel=\"noreferrer noopener\">the Agent Guide</a>.</li><li>Only after this safe path is understood, read <a href=\"https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/README.md#disclaimer\" target=\"_blank\" rel=\"noreferrer noopener\">the official risk disclaimer</a> and <a href=\"https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/README.md#run-omegaclaw-in-docker\" target=\"_blank\" rel=\"noreferrer noopener\">Quick Start</a> before changing provider, channel, or permissions.</li></ul><p class=\"note\">Studio never collects a key, opens a public port, validates outside data, or performs an action. It leaves you with a clear, human-owned next step.</p></div></section>
</main></div><footer class="wizard-bar\"><div class="wizard-bar-inner\"><button id="wizard-back" class="ghost" type="button" disabled>Back</button><span id="wizard-position" class="wizard-position" aria-live="polite\">Step 1 of 9</span><button id="wizard-next" class="primary" type="button\">Start with the idea</button></div></footer>
<script>
const screens=['meet','place','ready','proof','evidence','case','connect','policy','finish']; const labels=['Start with the idea','Choose this place','Check the workshop','Watch the proof','Open the evidence','Create my case','Connect one agent','Save the rule','Finish']; let active=0; let status={}; let workspaceCreated=false;
const outputFor={ready:'preflight-output',evidence:'evidence-output',case:'case-output'};
function setOutput(id,value){const el=document.getElementById(id);if(!el)return;el.textContent=String(value??'');el.classList.remove('hidden');}
function stateRow(label,item){const row=document.createElement('div');row.className='check';const icon=document.createElement('span');icon.textContent=item.state==='ready'||item.state==='verified'?'✓':item.state==='failed'?'!':'…';icon.className=item.state;const copy=document.createElement('span');const title=document.createElement('strong');title.textContent=label+' — '+item.state;const detail=document.createElement('span');detail.textContent=item.detail||'';copy.append(title,detail);row.append(icon,copy);return row;}
function cardList(id,items){const el=document.getElementById(id);if(!el)return;el.replaceChildren(...items.map(([label,item])=>stateRow(label,item)));}
function canNext(){return [document.getElementById('ack-boundary')?.checked,true,status.preflight?.state==='ready',status.factory_fault?.state==='verified',document.getElementById('ack-synthetic')?.checked,workspaceCreated,document.getElementById('ack-connect')?.checked,document.getElementById('ack-policy')?.checked][active]!==false;}
function show(index){active=Math.max(0,Math.min(index,screens.length-1));document.querySelectorAll('.screen').forEach(el=>el.classList.toggle('active',el.id===screens[active]));document.querySelectorAll('.step').forEach(el=>{const n=Number(el.dataset.step);el.classList.toggle('active',n===active);el.classList.toggle('done',n<active);});document.getElementById('wizard-back').disabled=active===0;const next=document.getElementById('wizard-next');next.disabled=active===screens.length-1;next.textContent=labels[active];document.getElementById('wizard-position').textContent='Step '+(active+1)+' of '+screens.length;}
function showBlocker(){const messages=['Tick the one-sentence boundary so we know the referee idea is clear.','Choose where your project lives.','Run studio-doctor.sh and wait for every required check to be ready.','Run the pinned real proof and wait for all required evidence.','Tick the fictional-lesson acknowledgement after opening the evidence.','Create a workspace and keep its positive and negative tests.','Acknowledge the two-tool local bridge, or finish the proof first.','Copy or acknowledge the agent policy so the human gate stays explicit.'];const el=document.getElementById('wizard-position');el.textContent='Blocked: '+messages[active];setTimeout(()=>{el.textContent='Step '+(active+1)+' of '+screens.length;},3500);}
async function refresh(){const response=await fetch('/api/status');status=await response.json();cardList('preflight-card',[['Workshop checks',status.preflight],['Pinned proof',status.proof],['First receipt',status.receipt]]);cardList('proof-card',[['Workshop preflight',status.preflight],['Real factory-fault proof',status.factory_fault],['First Reflection (optional)',status.proof]]);cardList('template-card',[['Template files',status.template]]);const finish=document.getElementById('finish-card');finish.replaceChildren();finish.append(stateRow('Current handoff',status.handoff));}
document.getElementById('wizard-next').addEventListener('click',()=>{if(active<screens.length-1){if(!canNext()){showBlocker();return;}show(active+1);}});document.getElementById('wizard-back').addEventListener('click',()=>show(active-1));document.querySelectorAll('[data-step]').forEach(el=>el.addEventListener('click',()=>{const n=Number(el.dataset.step);if(n<=active)show(n);else showBlocker();}));
document.querySelectorAll('[data-artifact]').forEach(btn=>btn.addEventListener('click',async()=>{const name=btn.dataset.artifact;const target=outputFor[screens[active]]||'evidence-output';const res=await fetch('/api/artifacts/'+encodeURIComponent(name));const payload=await res.json();setOutput(target,res.ok?payload.content:payload.error);}));
document.querySelectorAll('[data-copy]').forEach(btn=>btn.addEventListener('click',async()=>{const value=btn.dataset.copy;try{await navigator.clipboard.writeText(value);btn.textContent='Copied';setTimeout(()=>btn.textContent=btn.dataset.copy.includes('policy')?'Copy agent policy':btn.dataset.copy.includes('proof')?'Copy commands':'Copy command',1200);}catch(_){const statusEl=btn.closest('.command')?.querySelector('.sr-status');if(statusEl)statusEl.textContent='Select and copy the command from the box below.';} }));
document.getElementById('copy-template').addEventListener('click',async()=>{const name=document.getElementById('workspace-name').value.trim();const result=document.getElementById('copy-result');const response=await fetch('/api/templates/factory-fault/copy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name})});const payload=await response.json();if(response.ok){workspaceCreated=true;result.textContent='Created logical workspace: '+payload.workspace_id+'. The files stay in your project; no absolute path is exposed.';result.className='sr-status verified';}else{result.textContent=payload.error||'The workspace was not created.';result.className='sr-status pending';}});
refresh().catch(()=>{document.getElementById('finish-card').textContent='Studio could not read local status yet.';});
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
