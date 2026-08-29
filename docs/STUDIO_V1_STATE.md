# Studio v1 state and continuity record

Updated: 2026-08-29

This file is the continuity snapshot for future Codex chats. Read it together with `STUDIO_V2_FEYNMAN_JOURNEY.md` before planning or changing the Studio.

## Product language

- Repository artifacts, UI copy, documentation, receipts, prompts, and generated output are English.
- Portuguese is used only in the private working conversation with the human owner.
- The product remains Track 2 onboarding. It is not an enterprise platform, truth certifier, industrial diagnosis system, or autonomous action layer.

## What v1 contains

- First Reflection mission and deterministic evidence validation;
- explicit human approval and before/after Markdown receipt;
- pinned OmegaClaw-Core `v0.1.19` proof through WebSocket, Test provider, real loop, MeTTa skill, and NAL/STV;
- loopback-only Studio Wizard;
- synthetic `factory-fault` template;
- private workspace copying by logical slug;
- local readable JSON/Markdown artifacts;
- bounded local STDIO MCP with exactly `omega.reason` and `omega.get_receipt`;
- functional `scripts/studio-mcp-check.sh` handshake gate before the first-agent handoff;
- bounded general consultation packets for local multi-agent tests, with deterministic conflict/missing-fact detection;
- English installation, architecture, demo, future, and agent guides.

## Verified local state

- Python unit suite: 37 tests passed.
- Shell syntax checks passed.
- Apple Silicon factory-fault real proof passed 7/7.
- Browser QA covered desktop and mobile layout, locked forward navigation, explicit post-script confirmations, receipt comprehension, logical workspace copying, fixture inspection, Finish handoff, and MCP command guidance.
- MCP handshake and the closed release-readiness Conflict Packet were tested locally.
- The untracked local `tmp/` directory belongs to the human and must remain untouched.

## Git state at this snapshot

- Latest committed implementation: `55651cb Make MCP bridge functional for local agent tests`.
- GitHub repository: `https://github.com/marcelosite/omegaclaw-launchpad`.
- GitHub description and topics were updated for Studio, MCP, and auditability.

## VPS state at this snapshot

- SSH alias used from the owner's Mac: `oracle-fabrica`.
- Repository path on the VPS: `/home/ubuntu/omegaclaw-launchpad`.
- VPS repository currently follows GitHub `main` at `55651cb`.
- Host: Ubuntu 22.04, `aarch64`/ARM64, approximately 24 GiB RAM.
- Studio runs in tmux session `launchpad-studio`.
- Studio binds only to VPS loopback: `127.0.0.1:8765`.
- The owner reaches it from the Mac with a local tunnel such as:

```bash
ssh -N -L 8876:127.0.0.1:8765 oracle-fabrica
```

- That SSH command runs on the owner's Mac, not inside the VPS.
- The remote dashboard is then opened on the Mac at `http://127.0.0.1:8876`.
- The existing local Studio remains at `http://127.0.0.1:8765`.
- The ARM64 factory-fault proof passed 7/7 on the VPS.
- Remote proof artifacts exist under `.launchpad/studio/runs/factory-fault/`.
- Remote MCP initialization and the exact two-tool list were verified.
- Remote Studio now serves the nine-step Wizard and reports the factory-fault handoff as ready.
- Remote Studio was restarted after the locked-gate UX update; the existing tmux session and all other containers remain untouched.
- Remote repository tests pass: 37 tests.
- The proof container and proof volume were cleaned after the run.

## VPS isolation decisions

- Existing apps and containers were not removed or reconfigured.
- Existing containers observed after installation: `n8n`, `open-webui`, `postgresql`, `postiz`, `postiz-postgres`, `postiz-redis`, `umami`, and `umami-db`.
- Studio uses the previously free loopback port `8765`.
- The proof harness uses temporary ports only during the proof.
- The Linux proof uses isolated host networking because the Oracle Docker bridge blocked container-to-host traffic.
- The proof skips its internal nginx while using host networking, so it cannot contend with an existing host service on port `8080`.
- Proof Docker resources use exclusive `launchpad-*` names.
- No domain, public firewall rule, public Studio port, MiniMax configuration, API key, or remote MCP endpoint was created.

## ARM64 compatibility work recorded in the runner

- FAISS compilation is limited to two jobs.
- Legacy Docker builders are supported without `COPY --chmod`.
- The local embedding model is embedded into the proof image so runtime does not require an API key.
- The proof launcher supports exclusive container and volume names.
- Linux host networking and nginx skipping are limited to the controlled proof path.
- Patch application is idempotent across retries and validates required markers before execution.

## Honest status distinction

- `factory_fault` is verified on the VPS.
- The separate First Reflection proof artifact is still pending on the VPS.
- The current MCP can consult the verified teaching lesson and accept only the fixed release-readiness teaching packet. It cannot accept arbitrary claims from several agents or run a new real-world decision.
- The Studio process is held by tmux and is not configured to restart after a VPS reboot.

The local Mac proof image was removed after the final 7/7 run. The local doctor may still report `disk: BLOCKED` when fewer than 25 GiB are available; this is an honest resource gate, not a proof result. The Oracle VPS preflight is ready.

## Current human feedback

The Studio UI now uses the approved Feynman method: one short question, one action, one proof per numbered step. Future steps are not clickable; the primary button stays disabled until the required answer, status check, receipt, workspace, or human confirmation exists. The factory-fault lesson remains explicitly synthetic and illustrative. The fixed release-readiness packet is a first teaching test, not general arbitration.

The full product direction is in `docs/STUDIO_V2_FEYNMAN_JOURNEY.md`.

## Actions requiring a new explicit human decision

- adding a fixed web action runner;
- running the separate First Reflection proof on the VPS;
- configuring automatic restart/systemd;
- extending the bounded MCP contract beyond the fixed release-readiness teaching packet;
- connecting Codex, Claude Code, or other agents to a new real workspace;
- MiniMax/ASICloud compatibility work or credentials;
- domain, TLS, authentication, reverse proxy, public firewall, or public exposure;
- public sprint-page editing is complete: the authenticated BGI Commons submission now presents the Studio scope, GitHub repository, Studio guide, and real-proof links.
