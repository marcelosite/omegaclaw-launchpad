# OmegaClaw Launchpad

Launchpad is a Docker-only onboarding and evidence layer for [OmegaClaw](https://github.com/asi-alliance/OmegaClaw-Core). It tells one short story — **The Lighthouse in the Fog** — and proves the core path with the real pinned OmegaClaw runtime, the deterministic `Test` provider, a WebSocket channel, memory across restart, a file tool, MeTTa, NAL/STV, a response, and a receipt.

It is not an autonomous action platform. OmegaClaw can reason and return a recommendation; a person decides. The proof is synthetic and local, and deliberately performs no external action.

## Project links

- [Open the repository](https://github.com/marcelosite/omegaclaw-launchpad)
- [Download the V2 presentation (PDF)](https://github.com/marcelosite/omegaclaw-launchpad/releases/download/v0.3.0/omegaclaw-launchpad-pitch.pdf)
- [Read the presentation in this repository](deliverables/omegaclaw-launchpad-pitch.pdf)
- [Visit the official OmegaClaw Core repository](https://github.com/asi-alliance/OmegaClaw-Core)
- [View the OmegaClaw Launchpad project on BGI Commons](https://bgicommons.org/teams/55)
- [Visit BGI Commons HyperSprint #1: OmegaClaw](https://bgicommons.org/hackathons/hypersprint-1-omegaclaw)

## Fast path

Codex starts with [`AGENTS.md`](AGENTS.md). Claude Code starts with
[`CLAUDE.md`](CLAUDE.md). Both guides lead to the same verified and
human-supervised workflow.

Run these commands **on the user's computer or private VPS, from this repository root**:

```sh
scripts/launchpad-start.sh
```

The launcher runs the host preflight, validates the example, runs the real Docker proof, verifies its receipt, and only then opens the loopback Studio at `http://127.0.0.1:8765`. The story-first Wizard has eight short moments: Intro → Input → Memory → Verify → Reason → Explain → Understand → Play. Each lesson keeps the story on the left and the matching OmegaClaw part on the right.

For a private VPS, run `scripts/launchpad-start.sh --background` in the VPS
terminal. Then, on the user's computer, run
`ssh -N -L 8876:127.0.0.1:8765 <your-vps-ssh-target>` and open
`http://127.0.0.1:8876`. The VPS stays loopback-only.

To validate or copy the only approved example without Docker:

```sh
PYTHONPATH=src python3 -m launchpad example check lighthouse-in-the-fog
PYTHONPATH=src python3 -m launchpad example copy my-case
```

Read [the story](docs/THE_LIGHTHOUSE_IN_THE_FOG.md), [the runnable example](examples/lighthouse-in-the-fog/README.md), [the coding-agent guide](docs/AGENT_GUIDE.md), and [the proof contract](docs/PROOF.md).

## Providers and keys

The first proof uses `Test`; it needs no LLM key. Never commit a key or put one in an example, receipt, or chat. A direct MiniMax key is a future optional provider configuration (`OPENAIAPI_API_KEY` with the upstream `OpenAIAPI` provider), not the ASI Alliance `ASI_API_KEY` path. See [PROVIDERS.md](docs/PROVIDERS.md).

## Optional MCP

The local STDIO bridge is an optional receipt/teaching interface, not a new OmegaClaw executor. It exposes exactly `omega.reason` and `omega.get_receipt`, requires the verified Lighthouse proof, does not call a provider or run shell commands, and never authorizes an action. See [AGENT_GUIDE.md](docs/AGENT_GUIDE.md#mcp-optional).

## Development checks

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
git diff --check
```

The complete evidence contract and Docker proof procedure are in [PROOF.md](docs/PROOF.md). The architecture and safety boundaries are in [STUDIO_ARCHITECTURE.md](docs/STUDIO_ARCHITECTURE.md).
