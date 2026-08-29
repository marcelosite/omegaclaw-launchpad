# OmegaClaw Launchpad Studio — approved P0

## Product decision

**OmegaClaw Launchpad Studio — First Proof** is the next stage of Launchpad.

It is a self-hosted onboarding lab: a person installs the kit on their own VPS, opens a web interface through an SSH tunnel, runs or reviews a real OmegaClaw proof with the `Test` provider, walks through the real execution artifacts, and copies a safe template to study facts, rules, and receipts.

P0 is **not** an enterprise decision platform, industrial agent, internet-facing service, or generic MeTTa editor.

## Honest claim

The Studio demonstrates the capabilities already proved by this repository:

```text
pinned OmegaClaw-Core
→ real WebSocket
→ controlled Test provider
→ real loop
→ skill (metta ...)
→ NAL/STV observed in the loop
→ response through the channel
→ readable artifacts and receipt
```

It does not claim that:

- the Test provider measures intelligence;
- a conclusion is true in the outside world;
- the factory template diagnoses equipment;
- OmegaClaw changes rules, executes actions, or improves itself autonomously;
- the dashboard validates corporate sources or business decisions.

## User and outcome

Target user: someone curious about VPSs, Docker, Codex, and/or agents, but with no prior OmegaClaw experience.

Expected result in a first session:

1. The person opens the Studio in their own browser.
2. They see whether the VPS is ready for the proof.
3. They see artifacts from a real proof without supplying an LLM key.
4. They understand `facts → MeTTa/NAL → result → receipt`.
5. They copy a learning template to a local workspace and ask Codex to adapt it.

## Web interface access

The server runs only on the VPS loopback interface:

```text
127.0.0.1:8765
```

The user's browser opens the interface through an SSH tunnel:

```bash
ssh -N -L 8765:127.0.0.1:8765 ubuntu@VPS_IP
```

Then open `http://127.0.0.1:8765` on the local computer. No Studio, test WebSocket, or worker port is published to the internet in P0.

## Wizard journey

### 1. Welcome

Explains in plain language what the session proves and its limits.

### 2. Preflight

Shows read-only checks for repository version, expected upstream commit, Python, Docker, architecture, memory, and disk. It does not install packages, change the firewall, or ask for credentials.

### 3. First real proof

Shows First Reflection artifacts and their real checkpoints. Execution remains in the known runner at `scripts/run-omegaclaw-proof.sh`; the dashboard does not receive Docker-socket access and does not execute arbitrary commands.

If the proof has not run, the screen shows the exact command and `pending`. If it fails, it shows `failed` or `pending`; it never shows `verified` without the real `omega-proof.json` produced by the harness.

### 4. Learn

Shows the chain below with links to generated artifacts:

```text
agent/Test → frozen facts → MeTTa/NAL expression → STV → response → receipt.md
```

### 5. `factory-fault` template

Opens a fully synthetic case containing:

- `facts.json`;
- `rules.md`, the human explanation of the rules;
- `rules.metta`, an illustrative MeTTa lesson scaffold that P0 does not run in the real OmegaClaw runtime;
- `tests.json`, with positive and negative cases;
- `README.md`, with an explicit disclaimer;
- an example receipt.

The case derives only `manual_inspection_recommended` when two synthetic signals coexist. It never produces a diagnosis, causal claim, or machine-stop command.

The **Copy to workspace** action is part of this template screen. The user creates a copy with a safe CLI command:

```bash
python3 -m launchpad studio new my-case --template factory-fault
```

The Studio displays only the created logical workspace ID and instructions for Codex to adapt facts, rules, and tests. Its copy API never exposes an absolute server path. The first version does not edit rules in the web interface.

## P0 architecture

```text
User computer
  browser ── SSH tunnel ──► Studio at 127.0.0.1:8765 on the VPS
                                  │
                                  ├── reads Launchpad artifacts
                                  ├── creates copies of allowed templates
                                  └── reads local workspaces/runs

Terminal/Codex on the VPS
  └── existing runner ──► Docker Engine ──► pinned OmegaClaw-Core
                                        └── real artifacts for the Studio
```

The dashboard is deliberately an artifact reader and explainer. It does not control the Docker Engine. This preserves the existing proof's fidelity and avoids giving the web service a Docker socket.

## Mandatory minimum security

- Fixed bind at `127.0.0.1:8765`; reject `0.0.0.0`.
- No LLM key, OAuth, provider token, or web login in P0.
- The dashboard accepts no shell commands, arbitrary paths, free-form MeTTa expressions, or uploads.
- Routes resolve only known logical IDs and internal paths; traversal attempts are rejected.
- Markdown, JSON, and file names are escaped before appearing in HTML.
- `studio-data/`, `workspaces/`, and `runs/` are private and ignored by Git.
- The P0 threat model is one person accessing their own session through SSH; domain exposure is explicitly future work.

## P0 deliverables

```text
docs/STUDIO.md                 user guide
docs/STUDIO_ARCHITECTURE.md    boundaries and data flow
docs/STUDIO_DEMO.md            three-minute script
docs/INSTALL_WITH_CODEX.md     copyable Codex installation instructions

scripts/studio-doctor.sh       read-only preflight
scripts/studio-start.sh        starts only the local interface
scripts/studio-open.sh         prints the SSH tunnel command and URL

src/launchpad/studio/           web server and safe artifact reader
templates/factory-fault/        copyable synthetic tutorial
tests/test_studio_*.py          contracts, routes, and security
```

The Docker composition file enters P0 only if it can reuse the current proof without changing it. The dashboard does not depend on Docker Compose to serve artifacts; Docker remains a requirement only for the real proof.

## Implementation slices

### Slice 1 — contracts and template

1. Create `templates/factory-fault/` with synthetic data, human rules, an illustrative MeTTa lesson scaffold, tests, and disclaimers.
2. Create a minimal workspace schema and a `studio new` command that duplicates only known templates.
3. Test that copying does not change the original template and that invalid slugs/paths fail.

### Slice 2 — safe artifact reading

1. Create discovery functions for Launchpad state, proof state, and receipts.
2. Expose only logical names and previously allowed content.
3. Generate an example receipt for the template, clearly marked as a fixture.
4. Test for traversal, overwrites, and unescaped HTML.

### Slice 3 — Studio interface

1. Create a minimal Python server with simple HTML/CSS/JS; use neither a SPA nor a database.
2. Implement the five wizard screens in read-only mode.
3. Show `ready`, `pending`, `failed`, and `verified` directly from artifacts.
4. Add the limited action to copy a template by validated slug.

### Slice 4 — installation and demo

1. Create `studio-doctor`, `studio-start`, and `studio-open`.
2. Write `INSTALL_WITH_CODEX.md` with authority boundaries and troubleshooting steps.
3. Run existing and new Python tests.
4. Run the real proof in a compatible environment and record the three-minute demo.

## P0 acceptance criteria

- All existing tests continue to pass.
- On a compatible clean machine, preflight reports clear blockers and writes no secrets.
- The Studio listens only on loopback.
- The wizard displays real artifacts and never simulates `verified`.
- Missing real proof is shown as `pending`.
- The `factory-fault` template is explicitly synthetic, copyable, and has at least one positive and one negative case.
- Copying preserves the original template and rejects invalid paths/slugs.
- Every item shown by the browser is escaped.
- The guide lets a person open the Studio through an SSH tunnel and follow First Reflection.

## Outside P0

The following are recorded in [STUDIO_FUTURE.md](STUDIO_FUTURE.md): MCP, dashboard execution, an isolated worker, a rule editor/compiler, LLM-proposed rules, paid providers, MiniMax, public deployment, authentication, and connectors.
