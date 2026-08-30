# The Lighthouse in the Fog

A boat needs a route through fog. One source says north is clear, another
reports an obstacle, and the south beacon is silent.

```text
Receive → Remember → Verify → Reason → Explain
```

Omega compares the recorded evidence, asks for better information when the
sources conflict, and explains why a later verified update changes the result.
It never steers the boat. A person decides.

## Run the verified example

Run from the repository root on the computer or VPS that holds this project:

```bash
scripts/studio-doctor.sh
scripts/run-lighthouse-proof.sh
```

The first script records readiness. The second uses the pinned OmegaClaw-Core
runtime, the deterministic Test provider, WebSocket, and a real MeTTa/NAL call.
No LLM key is required.

## Files

- `story.md` — the short human story.
- `claims.json` — conflicting self-reported claims.
- `facts.json` — recorded facts and provenance.
- `verified-update.json` — a controlled local bulletin used by the lesson.
- `runtime-bulletin.txt` — a one-line projection of that bulletin for the
  OmegaClaw file-skill proof.
- `rules.md` — the human-owned rule and action boundary.
- `reasoning.metta` — the exact teaching expressions.
- `tests.json` — conflict, verified-update, missing-fact, and GIGO cases.
- `example-receipt.md` — a fixture, never runtime evidence.
- `AGENTS.md` — instructions for Codex and compatible coding agents.
- `CLAUDE.md` — the Claude Code entry point for the same safe contract.

## Honest boundary

This example demonstrates a controlled core path. It does not demonstrate every
OmegaClaw provider, channel, skill, PLN/ONA behavior, web search, unrestricted
shell access, self-improvement, or production autonomy.

MCP is optional. Learn and verify the example before adding integrations.
