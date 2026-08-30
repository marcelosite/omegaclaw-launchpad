"""Story-first English interface for the local OmegaClaw Studio."""

PAGE = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#f8f5ef">
  <title>OmegaClaw Launchpad — The Lighthouse in the Fog</title>
  <style>
    :root{
      color-scheme:light;
      --paper:#f8f5ef;--white:#fffdfa;--ink:#1b0a39;--body:#292b35;
      --cyan:#00a7c8;--cyan-soft:#def5f7;--gold:#ffcc62;--gold-soft:#fff1c9;
      --pink:#f3dede;--navy:#102538;--line:#d8d3ca;--muted:#6c6b72;
      --serif:Iowan Old Style,Palatino Linotype,Book Antiqua,Palatino,Georgia,serif;
      --sans:Inter,Avenir Next,Avenir,Helvetica Neue,Arial,sans-serif;
    }
    *{box-sizing:border-box}
    html{background:var(--paper)}
    body{margin:0;min-height:100vh;background:
      linear-gradient(180deg,transparent 78%,var(--pink) 78%,var(--pink) 82%,transparent 82%),
      radial-gradient(circle at 96% 8%,#fff1d8 0,transparent 28%),var(--paper);
      color:var(--body);font:17px/1.55 var(--sans);-webkit-font-smoothing:antialiased}
    button{font:inherit}
    .app{width:min(1500px,100%);min-height:100vh;margin:auto;padding:28px 48px 42px}
    .topbar{display:flex;align-items:center;justify-content:space-between;gap:24px;margin-bottom:22px}
    .brand{color:var(--cyan);font-size:.82rem;font-weight:850;letter-spacing:.08em;text-transform:uppercase}
    .journey{display:flex;align-items:center;gap:14px;color:var(--muted);font-size:.78rem;font-weight:760;letter-spacing:.06em;text-transform:uppercase}
    .track{width:150px;height:3px;background:#ddd8cf;border-radius:99px;overflow:hidden}
    .track span{display:block;width:12.5%;height:100%;background:var(--cyan);transition:width .25s ease}
    .screen{display:none;min-height:calc(100vh - 120px);animation:enter .32s ease both}
    .screen.active{display:block}
    @keyframes enter{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
    h1,h2,h3,p{margin-top:0}
    h1,h2{font-family:var(--serif);color:var(--ink);font-weight:760;letter-spacing:-.045em}
    h1[tabindex]:focus,h2[tabindex]:focus{outline:none}
    h1{font-size:clamp(3.2rem,6.6vw,7.4rem);line-height:.9;margin-bottom:30px}
    h2{font-size:clamp(2.4rem,4.5vw,5.2rem);line-height:.96;margin-bottom:24px}
    .eyebrow{margin-bottom:22px;color:var(--cyan);font-size:.84rem;font-weight:850;letter-spacing:.1em;text-transform:uppercase}
    .lead{max-width:760px;font-size:clamp(1.08rem,1.5vw,1.42rem);line-height:1.55}
    .primary{display:inline-flex;align-items:center;justify-content:center;gap:12px;min-height:52px;border:0;border-radius:12px;padding:14px 23px;background:var(--gold);color:var(--ink);font-weight:850;cursor:pointer;box-shadow:0 8px 0 #1b0a3912;transition:transform .16s,box-shadow .16s}
    .primary:hover{transform:translateY(-2px);box-shadow:0 10px 0 #1b0a3912}
    .primary:focus-visible,.back:focus-visible{outline:3px solid var(--cyan);outline-offset:4px}
    .primary:disabled{cursor:default;opacity:.72;transform:none}
    .arrow{font-size:1.25em}
    .cover{display:grid;grid-template-columns:minmax(0,1.08fr) minmax(420px,.72fr);gap:clamp(48px,7vw,120px);align-items:center;min-height:calc(100vh - 150px)}
    .cover-copy{padding:50px 0 80px}
    .cover-copy .lead{max-width:690px;margin-bottom:36px}
    .cover-visual{position:relative;align-self:stretch;min-height:650px;max-height:850px}
    .cover-visual img{width:100%;height:100%;min-height:650px;object-fit:cover;object-position:56% center;display:block}
    .float-word{position:absolute;z-index:2;color:white;font-size:clamp(1.2rem,2.2vw,2.2rem);font-weight:850;letter-spacing:.02em;white-space:nowrap;pointer-events:none;text-shadow:0 2px 14px #071829,0 1px 2px #071829}
    .float-word.gold{color:var(--gold);top:7%;left:-12%}
    .float-word.white{top:56%;right:5%;padding:.08em .28em;background:#071829b8;color:#fff}
    .float-word.ink{left:50%;bottom:4%;transform:translateX(-50%);color:#fff}
    .cover-visual:after{content:"";position:absolute;inset:auto auto -24px -34px;width:62%;height:80px;background:var(--cyan-soft);z-index:-1}
    .proof-pill{display:inline-flex;align-items:center;gap:9px;margin-bottom:22px;padding:7px 11px;border:1px solid #d7d1c7;border-radius:999px;background:#fff9;color:var(--muted);font-size:.76rem;font-weight:800;letter-spacing:.04em;text-transform:uppercase}
    .proof-pill:before{content:"";width:8px;height:8px;border-radius:50%;background:var(--gold)}
    .proof-pill.verified:before{background:var(--cyan)}
    .lesson{display:grid;grid-template-columns:minmax(0,1.18fr) minmax(390px,.82fr);grid-template-areas:"story tech" "nav tech";grid-template-rows:1fr auto;gap:0 clamp(34px,5vw,80px);align-items:stretch;min-height:calc(100vh - 112px);padding:4px 0 18px}
    .story-side{grid-area:story;display:flex;flex-direction:column;min-width:0;padding:12px 0}
    .scene{position:relative;height:132px;margin:0 0 20px;overflow:hidden;background:var(--navy)}
    .scene img{width:100%;height:100%;object-fit:cover;object-position:center 56%;filter:saturate(.92);display:block}
    .scene:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,#09203866,transparent 62%)}
    .scene-word{position:absolute;z-index:1;left:28px;bottom:18px;color:white;font-size:clamp(1.5rem,3vw,3rem);font-weight:850;letter-spacing:.02em;text-transform:uppercase}
    .story-copy{max-width:850px;font-family:var(--serif);color:var(--ink);font-size:clamp(1.3rem,1.75vw,1.75rem);line-height:1.32}
    mark{padding:0 .08em;background:linear-gradient(transparent 58%,var(--gold) 58%);color:inherit}
    mark.cyan{background:linear-gradient(transparent 58%,#8be0ec 58%)}
    .story-note{margin-top:auto;padding-top:12px;color:var(--muted);font-size:.86rem}
    .tech-side{grid-area:tech;position:relative;display:flex;flex-direction:column;justify-content:center;padding:clamp(24px,3vw,42px);background:var(--white);border:1px solid var(--line);box-shadow:20px 22px 0 var(--cyan-soft)}
    .tech-side:before{content:"";position:absolute;right:28px;top:27px;width:9px;height:9px;border-radius:50%;background:var(--gold);box-shadow:-22px 0 0 var(--cyan)}
    .part-label{color:var(--cyan);font-size:.75rem;font-weight:850;letter-spacing:.11em;text-transform:uppercase}
    .tech-side h3{margin:10px 0 13px;color:var(--ink);font-size:clamp(1.65rem,2.35vw,2.45rem);line-height:1.03}
    .plain{font-size:.96rem}
    .mapping{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:12px;margin:16px 0;padding:13px;background:var(--gold-soft);font-size:.82rem}
    .mapping span{display:block}.mapping small{display:block;color:var(--muted);font-size:.68rem;font-weight:800;letter-spacing:.07em;text-transform:uppercase}.mapping b{color:var(--ink)}
    .mapping .map-arrow{color:var(--cyan);font-size:1.4rem;font-weight:900}
    pre{max-width:100%;overflow:auto;margin:0;padding:13px 15px;border-radius:8px;background:var(--navy);color:#f8f4ed;font:12px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:pre-wrap}
    .micro-proof{display:flex;align-items:flex-start;gap:10px;margin-top:14px;padding-top:13px;border-top:1px solid var(--line);color:var(--muted);font-size:.78rem}
    .micro-proof:before{content:"✓";display:grid;place-items:center;flex:0 0 22px;height:22px;border-radius:50%;background:var(--cyan-soft);color:#007a91;font-weight:900}
    .navrow{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-top:16px}
    .lesson-nav{grid-area:nav}
    .back{border:0;padding:12px 0;background:transparent;color:var(--muted);font-weight:750;cursor:pointer}
    .back[hidden]{display:block;visibility:hidden}
    .summary{min-height:calc(100vh - 112px);padding:8px 0 18px}
    .summary-head{display:grid;grid-template-columns:1fr .55fr;gap:48px;align-items:end;margin-bottom:18px}
    .summary-head h2{margin-bottom:0;font-size:clamp(2.3rem,3.7vw,4.15rem)}.summary-head p{margin-bottom:4px;font-size:1.04rem}
    .map-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
    .map-card{min-height:116px;padding:16px 18px;background:var(--white);border:1px solid var(--line)}
    .map-card:nth-child(2),.map-card:nth-child(5){background:var(--cyan-soft)}
    .map-card:nth-child(3),.map-card:nth-child(6){background:var(--gold-soft)}
    .map-card .event{color:var(--muted);font-size:.8rem}.map-card .component{display:block;margin:8px 0 3px;color:var(--ink);font-size:1.17rem;font-weight:850}.map-card .why{font-size:.84rem}
    .understand-row{display:flex;justify-content:flex-end;margin-top:14px}
    .play{display:grid;grid-template-columns:minmax(0,.8fr) minmax(520px,1.2fr);gap:clamp(36px,6vw,90px);align-items:center;min-height:calc(100vh - 150px);padding:35px 0 70px}
    .play h2{font-size:clamp(3rem,5vw,6rem)}
    .prompt-card{position:relative;padding:28px;background:var(--white);border:1px solid var(--line);box-shadow:22px 22px 0 var(--pink)}
    .prompt-card .part-label{margin-bottom:12px}
    .prompt-card pre{max-height:390px;background:#13263a;color:#fffdf6;font-size:.84rem}
    .copy-row{display:flex;align-items:center;justify-content:space-between;gap:18px;margin-top:20px}
    .copy-status{margin:0;color:#007c91;font-size:.85rem;font-weight:750}
    .scope{margin-top:28px;padding-left:16px;border-left:3px solid var(--gold);color:var(--muted);font-size:.88rem}
    @media(max-width:980px){
      .app{padding:22px 24px 36px}.cover{grid-template-columns:1fr .68fr;gap:36px}.cover-visual{min-height:560px}.cover-visual img{min-height:560px}
      .lesson{grid-template-columns:1fr;grid-template-areas:"story" "tech" "nav";gap:24px}.scene{height:220px}.tech-side{box-shadow:12px 12px 0 var(--cyan-soft)}.story-note{margin-top:18px}
      .summary-head{grid-template-columns:1fr}.map-grid{grid-template-columns:repeat(2,1fr)}.play{grid-template-columns:1fr}.prompt-card{box-shadow:12px 12px 0 var(--pink)}
    }
    @media(max-width:680px){
      body{font-size:16px}.app{padding:18px 16px 30px}.topbar{align-items:flex-start}.journey{display:block;text-align:right}.track{width:100px;margin:7px 0 0 auto}
      .screen{min-height:auto}.cover{display:flex;flex-direction:column;min-height:auto}.cover-copy{padding:40px 0 6px}.cover-visual{width:100%;min-height:390px;height:54vh;max-height:540px}.cover-visual img{min-height:390px}.float-word.gold{left:5%}.float-word.white{top:54%;right:4%}.float-word.ink{left:50%;bottom:5%;color:white}
      .lesson{padding-top:5px;gap:24px}.scene{height:150px;margin-bottom:25px}.scene-word{left:18px;bottom:13px}.tech-side{padding:25px 20px}.mapping{grid-template-columns:1fr;gap:6px}.mapping .map-arrow{transform:rotate(90deg);justify-self:center}.navrow{margin-top:0}.primary{width:100%}
      .summary{padding-top:20px}.summary-head{gap:18px}.map-grid{grid-template-columns:1fr}.understand-row{display:block}.play{padding-top:15px}.prompt-card{padding:20px 16px}.copy-row{display:block}.copy-status{margin-top:12px}
    }
    @media(prefers-reduced-motion:reduce){.screen{animation:none}.primary,.track span{transition:none}}
  </style>
</head>
<body>
<div class="app">
  <header class="topbar">
    <div class="brand">OmegaClaw Launchpad</div>
    <div class="journey"><span id="position">Intro · 01 / 08</span><div class="track" aria-hidden="true"><span id="progress-bar"></span></div></div>
  </header>

  <main>
    <section class="screen active" data-name="Intro">
      <div class="cover">
        <div class="cover-copy">
          <div class="eyebrow">One story. The whole system.</div>
          <div class="proof-pill" data-proof-state>Checking the real Docker proof</div>
          <h1 tabindex="-1">The Lighthouse<br>in the Fog</h1>
          <p class="lead">A boat needs a safe harbor, but the reports do not agree. Follow the story to see how <strong>OmegaClaw's parts fit together</strong> — from the first message to a recommendation a human can review.</p>
          <button class="primary" data-primary data-next>Next: enter the fog <span class="arrow">→</span></button>
        </div>
        <div class="cover-visual" aria-label="A lighthouse shining through ocean fog">
          <img src="/assets/lighthouse-hero.png" alt="A lighthouse casting a warm beam through dark ocean fog">
          <span class="float-word gold">EXPLORE</span><span class="float-word white">PROVE</span><span class="float-word ink">CONNECT</span>
        </div>
      </div>
    </section>

    <section class="screen" data-name="Input">
      <div class="lesson">
        <article class="story-side">
          <div class="scene"><img src="/assets/lighthouse-story-wide.png" alt="The lighthouse beam crossing dense fog"><span class="scene-word">Receive</span></div>
          <div class="eyebrow">01 · The reports arrive</div>
          <h2 tabindex="-1">The fog hides the route.</h2>
          <p class="story-copy">A boat is looking for the harbor. The north beacon says <mark>the route is clear</mark>. A sailor reports <mark class="cyan">an obstacle</mark>. The south beacon says nothing. Three reports arrive, but they do not agree.</p>
          <p class="story-note">The story problem: receiving information is not the same as knowing it is true.</p>
        </article>
        <aside class="tech-side">
          <div class="part-label">OmegaClaw part · Input</div><h3>WebSocket channel</h3>
          <p class="plain">OmegaClaw receives each report through a live message channel and keeps its loop running. It records a claim before deciding what that claim means.</p>
          <div class="mapping"><span><small>In the story</small><b>Reports arrive</b></span><span class="map-arrow">→</span><span><small>In OmegaClaw</small><b>Messages become inputs</b></span></div>
          <pre>report_1 = "north route is clear"
report_2 = "obstacle ahead"</pre>
          <div class="micro-proof"><span><b data-field="channel">WebSocket</b> channel and continuous loop <b data-check="loop_observed">checking</b>.</span></div>
        </aside>
        <div class="navrow lesson-nav"><button class="back" data-back>← Back</button><button class="primary" data-primary data-next>Next <span class="arrow">→</span></button></div>
      </div>
    </section>

    <section class="screen" data-name="Memory">
      <div class="lesson">
        <article class="story-side">
          <div class="scene"><img src="/assets/lighthouse-story-wide.png" alt="The lighthouse above a dark sea"><span class="scene-word">Remember</span></div>
          <div class="eyebrow">02 · Yesterday's logbook</div>
          <h2 tabindex="-1">The earlier warning still matters.</h2>
          <p class="story-copy">The lighthouse keeper opens yesterday's logbook. It says <mark>driftwood was seen near the north route</mark>. Even after the lighthouse system restarts, OmegaClaw can find that saved note again.</p>
          <p class="story-note">The story problem: useful context should not disappear when the runtime restarts.</p>
        </article>
        <aside class="tech-side">
          <div class="part-label">OmegaClaw part · Memory</div><h3>Remember + query</h3>
          <p class="plain">OmegaClaw saves a memory, restarts, and then searches for it. Memory keeps context available; it does not magically make the memory correct.</p>
          <div class="mapping"><span><small>In the story</small><b>The logbook survives</b></span><span class="map-arrow">→</span><span><small>In OmegaClaw</small><b>Persistent memory</b></span></div>
          <pre>remember("driftwood near north route")
query("driftwood north route")</pre>
          <div class="micro-proof"><span>Remember <b data-check="remember_observed">checking</b>, restart <b data-check="restart_observed">checking</b>, recall <b data-check="query_after_restart_observed">checking</b>.</span></div>
        </aside>
        <div class="navrow lesson-nav"><button class="back" data-back>← Back</button><button class="primary" data-primary data-next>Next <span class="arrow">→</span></button></div>
      </div>
    </section>

    <section class="screen" data-name="Verify">
      <div class="lesson">
        <article class="story-side">
          <div class="scene"><img src="/assets/lighthouse-story-wide.png" alt="A warm lighthouse beam illuminating fog"><span class="scene-word">Verify</span></div>
          <div class="eyebrow">03 · The harbor bulletin</div>
          <h2 tabindex="-1">An identified source adds evidence.</h2>
          <p class="story-copy">A controlled harbor bulletin reports that <mark>the north buoy is operational</mark>. The bulletin keeps its source and time, so the keeper knows where this new fact came from.</p>
          <p class="story-note">The story problem: a fact without its source is hard to inspect or trust.</p>
        </article>
        <aside class="tech-side">
          <div class="part-label">OmegaClaw part · Tool use</div><h3>Read file + provenance</h3>
          <p class="plain">OmegaClaw uses a controlled file-reading tool. The source stays attached to the observation. This demo verifies the tool path, not the outside world.</p>
          <div class="mapping"><span><small>In the story</small><b>The bulletin is inspected</b></span><span class="map-arrow">→</span><span><small>In OmegaClaw</small><b>A tool reads evidence</b></span></div>
          <pre>(read-file "runtime-bulletin.txt")
source = "harbor-control"</pre>
          <div class="micro-proof"><span>Controlled file tool <b data-check="tool_skill_observed">checking</b>. Source: <b data-field="tool_source">checking</b>.</span></div>
        </aside>
        <div class="navrow lesson-nav"><button class="back" data-back>← Back</button><button class="primary" data-primary data-next>Next <span class="arrow">→</span></button></div>
      </div>
    </section>

    <section class="screen" data-name="Reason">
      <div class="lesson">
        <article class="story-side">
          <div class="scene"><img src="/assets/lighthouse-story-wide.png" alt="Network lines crossing the lighthouse and sea"><span class="scene-word">Reason</span></div>
          <div class="eyebrow">04 · The evidence changes</div>
          <h2 tabindex="-1">OmegaClaw does not defend its first answer.</h2>
          <p class="story-copy">The old reports conflict. The identified bulletin adds stronger evidence. OmegaClaw <mark>keeps the disagreement visible</mark> and recalculates instead of pretending the first answer was certain.</p>
          <p class="story-note">The story problem: new evidence should change the result without erasing uncertainty.</p>
        </article>
        <aside class="tech-side">
          <div class="part-label">OmegaClaw part · Reasoning</div><h3>MeTTa + NAL/STV</h3>
          <p class="plain">MeTTa runs the reasoning expression. NAL/STV represents evidence with strength and confidence, allowing a conclusion to be revised when better evidence arrives.</p>
          <div class="mapping"><span><small>In the story</small><b>The balance changes</b></span><span class="map-arrow">→</span><span><small>In OmegaClaw</small><b>Evidence is recalculated</b></span></div>
          <pre>evidence = (stv 1.0 0.90)
result = "supported for human review"</pre>
          <div class="micro-proof"><span>MeTTa <b data-check="metta_skill_observed">checking</b>; NAL/STV <b data-check="nal_stv_observed_in_loop">checking</b>.</span></div>
        </aside>
        <div class="navrow lesson-nav"><button class="back" data-back>← Back</button><button class="primary" data-primary data-next>Next <span class="arrow">→</span></button></div>
      </div>
    </section>

    <section class="screen" data-name="Explain">
      <div class="lesson">
        <article class="story-side">
          <div class="scene"><img src="/assets/lighthouse-story-wide.png" alt="The lighthouse beam opening a path through fog"><span class="scene-word">Explain</span></div>
          <div class="eyebrow">05 · The keeper receives a report</div>
          <h2 tabindex="-1">A recommendation is not an order.</h2>
          <p class="story-copy">OmegaClaw reports: <mark>the north route is supported for human review</mark>. It records the sources, reasoning, unknowns, and result. It does not steer the boat. <mark class="cyan">The keeper decides.</mark></p>
          <p class="story-note">The story problem: a useful answer must be explainable, reviewable, and bounded.</p>
        </article>
        <aside class="tech-side">
          <div class="part-label">OmegaClaw part · Output</div><h3>Response + receipt</h3>
          <p class="plain">OmegaClaw returns a supervised conclusion and leaves an auditable receipt. The receipt shows what happened; it does not authorize an external action.</p>
          <div class="mapping"><span><small>In the story</small><b>The keeper gets a report</b></span><span class="map-arrow">→</span><span><small>In OmegaClaw</small><b>Explainable output</b></span></div>
          <pre>conclusion = "human_review"
external_actions = []
human_decides = true</pre>
          <div class="micro-proof"><span>Response <b data-check="response_observed">checking</b>; receipt <b data-check="receipt_observed">checking</b>; actions: <b data-field="external_actions">checking</b>.</span></div>
        </aside>
        <div class="navrow lesson-nav"><button class="back" data-back>← Back</button><button class="primary" data-primary data-next>Next: see the whole system <span class="arrow">→</span></button></div>
      </div>
    </section>

    <section class="screen" data-name="Understand">
      <div class="summary">
        <div class="summary-head"><div><div class="eyebrow">The whole story, in one glance</div><h2 tabindex="-1">Every story event reveals one OmegaClaw part.</h2></div><p class="lead">The lighthouse is the metaphor. The proof behind it is real, local, synthetic, and designed for human review.</p></div>
        <div class="map-grid">
          <div class="map-card"><span class="event">Conflicting reports arrive</span><span class="component">Input</span><span class="why">WebSocket + continuous loop</span></div>
          <div class="map-card"><span class="event">Yesterday's note returns</span><span class="component">Memory</span><span class="why">Remember + restart + query</span></div>
          <div class="map-card"><span class="event">A bulletin is inspected</span><span class="component">Tool use</span><span class="why">Controlled file + source</span></div>
          <div class="map-card"><span class="event">New evidence changes the balance</span><span class="component">Reasoning</span><span class="why">MeTTa + NAL/STV</span></div>
          <div class="map-card"><span class="event">The keeper receives the reason</span><span class="component">Explanation</span><span class="why">Response + receipt</span></div>
          <div class="map-card"><span class="event">The boat is never steered</span><span class="component">Human control</span><span class="why">No external action</span></div>
        </div>
        <div class="navrow"><button class="back" data-back>← Back</button><button class="primary" data-primary data-next>I understand the story and the problems it solves <span class="arrow">→</span></button></div>
      </div>
    </section>

    <section class="screen" data-name="Play">
      <div class="play">
        <div>
          <div class="eyebrow">Your turn</div><h2 tabindex="-1">I want to play with OmegaClaw.</h2>
          <p class="lead">You do not need to invent the first task. Give this prompt to the LLM already inside Codex, Claude Code, or another coding agent while it is open in this repository.</p>
          <p class="scope"><strong>Safe starting point:</strong> synthetic facts, local files, positive and negative tests, no credentials, no connectors, and no external actions.</p>
          <div class="navrow"><button class="back" data-back>← Back</button></div>
        </div>
        <div class="prompt-card">
          <div class="part-label">Ready-to-copy prompt for your LLM</div>
          <pre id="agent-prompt">You are inside the OmegaClaw Launchpad repository.

Read examples/lighthouse-in-the-fog/AGENTS.md and README.md.

First, explain the story and map each story event to the OmegaClaw part it demonstrates. Then run the example check, copy the example to a private workspace named my-first-omega-test, and propose one small experiment using only synthetic facts.

Run its positive and negative tests. Do not add credentials, connectors, or external actions. Stop and show me the diff and receipt for human approval.</pre>
          <div class="copy-row"><button id="copy-prompt" class="primary" data-primary>Copy prompt for my LLM</button><p id="copy-status" class="copy-status" aria-live="polite"></p></div>
        </div>
      </div>
    </section>
  </main>
</div>
<script>
  const screens=[...document.querySelectorAll('.screen')];
  let active=0,proof={};
  const observed=value=>value===true?'observed in the real proof':'not observed';
  function show(next,focus=true){
    active=Math.max(0,Math.min(screens.length-1,next));
    screens.forEach((screen,index)=>screen.classList.toggle('active',index===active));
    const number=String(active+1).padStart(2,'0');
    document.getElementById('position').textContent=screens[active].dataset.name+' · '+number+' / '+String(screens.length).padStart(2,'0');
    document.getElementById('progress-bar').style.width=((active+1)/screens.length*100)+'%';
    if(focus){const heading=screens[active].querySelector('h1,h2');if(heading)heading.focus();window.scrollTo({top:0,behavior:'smooth'});}
  }
  function render(){
    document.querySelectorAll('[data-proof-state]').forEach(element=>{
      const ok=proof.state==='verified';
      element.textContent=ok?'Real Docker proof verified':proof.state==='failed'?'Proof failed':'Proof not ready';
      element.classList.toggle('verified',ok);
    });
    document.querySelectorAll('[data-check]').forEach(element=>{const value=proof[element.dataset.check];element.textContent=observed(value);});
    document.querySelectorAll('[data-field]').forEach(element=>{
      const value=proof[element.dataset.field];
      element.textContent=Array.isArray(value)?(value.length?value.join(', '):'none'):value??'not recorded';
    });
  }
  document.querySelectorAll('[data-next]').forEach(button=>button.addEventListener('click',()=>show(active+1)));
  document.querySelectorAll('[data-back]').forEach(button=>button.addEventListener('click',()=>show(active-1)));
  function legacyCopy(text){
    const area=document.createElement('textarea');
    area.value=text;area.setAttribute('readonly','');area.style.position='fixed';area.style.opacity='0';
    document.body.appendChild(area);area.select();
    let copied=false;try{copied=document.execCommand('copy');}catch(error){copied=false;}area.remove();return copied;
  }
  document.getElementById('copy-prompt').addEventListener('click',async event=>{
    const button=event.currentTarget;
    const text=document.getElementById('agent-prompt').textContent;
    const status=document.getElementById('copy-status');
    let copied=legacyCopy(text);
    if(!copied&&navigator.clipboard){
      try{copied=await Promise.race([
        navigator.clipboard.writeText(text).then(()=>true).catch(()=>false),
        new Promise(resolve=>setTimeout(()=>resolve(false),800))
      ]);}catch(error){copied=false;}
    }
    if(copied){button.textContent='Prompt copied';button.disabled=true;status.textContent='Paste it into your coding agent.';}
    else{status.textContent='Select the prompt above and copy it manually.';}
  });
  fetch('/api/status').then(response=>response.json()).then(status=>{proof=status.lighthouse||{};render();}).catch(()=>render());
  show(0,false);window.scrollTo({top:0,left:0,behavior:'auto'});
</script>
</body>
</html>'''
