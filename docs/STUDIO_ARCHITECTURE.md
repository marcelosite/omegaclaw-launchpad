# Studio P0 architecture

## Boundary

The Studio is a local artifact reader and explainer. It is not an execution control plane. The current proof remains a terminal/Codex workflow:

```text
browser ── SSH tunnel ──► Studio (127.0.0.1:8765)
                              │
                              └── reads approved local artifacts

terminal/Codex ──► scripts/run-omegaclaw-proof.sh ──► Docker Engine
                                                        │
                                                        └── pinned OmegaClaw-Core
```

The dashboard has no Docker socket, no shell execution API, no arbitrary path API, and no external-action API. Docker Compose is not required to serve existing artifacts; Docker is required by the real proof runner.

## Components

### Studio server

The P0 server is a minimal Python web server with simple HTML/CSS/JS. It binds to `127.0.0.1:8765` only. It serves a locked nine-step Wizard and a constrained template-copy action. Each step has one primary action, a visible gate, and a human confirmation; future steps cannot be opened by clicking ahead. The ninth screen is an explicit Finish handoff to the local MCP bridge.

### Existing proof runner

`scripts/run-omegaclaw-proof.sh` remains the authority for the real proof. It pins OmegaClaw-Core `v0.1.19`, uses the controlled `Test` provider and WebSocket channel, and records the real harness result. The dashboard reads the result; it does not start or supervise the runner.

### Local file store

All Studio-owned state is below:

```text
.launchpad/studio/
├── preflight.json
├── mcp-check.json
├── workspaces/
│   └── <validated-workspace-slug>/
└── runs/
    ├── community-care/
    │   ├── omega-proof.json
    │   └── receipt.md
    └── mcp/
        └── mcp-<logical-receipt-id>.json
```

The existing mission and proof remain below:

```text
.launchpad/first-reflection/<mission-id>/
├── 00-mission/
├── 01-run-1/
├── 02-validation/
├── 03-reflection/
├── 04-review/
├── 05-rerun/
└── 06-receipt/
```

Only validated logical IDs resolve into these roots. The server must reject absolute paths, `..`, symlinks escaping a root, unknown filenames, and overwrite attempts.

## Artifact flow

```text
read-only preflight
  → .launchpad/studio/preflight.json

existing terminal proof
  → First Reflection artifacts
  → omega-proof.json
  → Studio status and evidence cards

community-care template
  → validated copy under workspaces/<slug>/
  → local human-readable facts/rules/tests
  → fixture receipt, clearly labeled

verified community-care lesson
  → local STDIO MCP bridge
  → omega.reason
  → logical receipt ID
  → omega.get_receipt
```

The browser should display content only after HTML escaping. Markdown is presented as escaped text or a deliberately constrained renderer; it is never treated as trusted HTML.

The template-copy API returns only the validated logical workspace ID, for example `{"workspace_id":"my-case"}`. It never returns the server's absolute workspace path. The server resolves that ID internally beneath the fixed workspace root.

The MCP bridge accepts only logical workspace and receipt IDs. It does not expose a filesystem path. `omega.reason` consults the verified synthetic community-care proof and persists a receipt before returning; it accepts the closed `community-care-first-review` packet and a bounded general consultation packet for local tests. The deterministic general evaluator only detects conflicting positions and missing/unknown facts; it does not execute arbitrary rules, validate outside data, or authorize an action. `omega.get_receipt` reads only receipts created by that bridge. `scripts/studio-mcp-check.sh` performs the real STDIO handshake and writes the local `mcp-check.json` status artifact.

## Status semantics

- `ready`: prerequisites or an artifact are available.
- `pending`: the proof has not produced the required artifact yet.
- `failed`: a recorded execution failed or timed out.
- `verified`: and only when the real `omega-proof.json` exists and its required checkpoints pass.

The UI must derive these states from files. It must not create a synthetic verified status, reuse a transcript as proof, or turn a template fixture into a real run.

## Security properties

- bind is fixed to loopback; `0.0.0.0` is rejected;
- no credentials are collected or persisted;
- no Docker socket is mounted into the dashboard;
- no shell, upload, arbitrary MeTTa, or external-action endpoint exists;
- the MCP STDIO bridge has exactly two bounded tools and no shell, provider, connector, or arbitrary-file operation;
- file names, Markdown, JSON, and user-visible values are escaped;
- workspace slugs and template names are allowlisted;
- state files are private, and the dashboard never overwrites proof or receipt artifacts;
- P0 assumes a single human through their own SSH session.

Do not expose this service through a domain or firewall rule in P0. A future public deployment needs its own authentication, TLS, rate limiting, update, backup, and threat-model decision.

## Why this boundary matters

The proof's fidelity comes from the existing harness and pinned runtime, not from a web label. Keeping execution in the terminal/Codex path makes that boundary visible and avoids giving a web process authority over Docker or host actions.
