# Studio P0 — three-minute demo

This script demonstrates onboarding honestly. It assumes the Studio is already running locally or is open through an SSH tunnel. Do not use a saved transcript to claim a live proof.

## 0:00–0:20 — frame the product

Say:

> OmegaClaw Launchpad Studio is a self-hosted onboarding lab. It teaches the real OmegaClaw loop with the no-key Test provider, keeps the evidence readable, and does not claim industrial diagnosis or autonomous action.

Point out the `No LLM key` message and the loopback URL.

## 0:20–1:10 — show First Proof

Open **First real proof** and show the seven real checkpoints from the saved proof artifact:

1. OmegaClaw container is reachable.
2. The WebSocket test channel is connected.
3. The controlled `Test` provider returns the expected response.
4. The response is delivered through the real channel.
5. The real loop dispatches the `metta` skill.
6. NAL/STV appears in the observed loop result.
7. The final response returns through the channel and is recorded.

Say:

> This green state comes from `omega-proof.json` produced by the harness. If that file is absent, the Studio shows `pending`; it never simulates `verified`.

If running live, the terminal/Codex runner is the thing executing the proof. The dashboard is observing artifacts, not controlling Docker.

## 1:10–1:40 — explain the evidence chain

Open **Learn** and follow:

```text
agent/Test → frozen facts → MeTTa/NAL → STV → response → receipt.md
```

Open one artifact from each card. Emphasize that the Test provider is deterministic and is not a measurement of intelligence, while the runtime and NAL path are real when the proof passes.

## 1:40–2:15 — open the template

Open **community-care**. Show:

- fictional facts;
- the human-readable `rules.md`;
- the illustrative `rules.metta` lesson scaffold, which Studio P0 does not run in the real OmegaClaw runtime;
- positive and negative tests;
- the fixture receipt and disclaimer.

Say:

> This example recommends human review when two fictional care agents disagree or consent is missing. It does not provide medical advice, diagnose a person, validate external data, or change a record.

## 2:15–2:40 — finish the Wizard

Open **Finish**. The screen names the next step instead of leaving the user at a dead end: review the copied files, run the real community-care lesson proof, and only then connect the local MCP bridge. The final button reads **Done** and is intentionally disabled; the Wizard has completed its job.

If the proof is verified, show the bounded local command:

```bash
scripts/studio-mcp.sh
```

Explain that `omega.reason` consults the published synthetic lesson and creates a logical receipt ID, while `omega.get_receipt` retrieves that receipt. The bridge cannot run shell commands, providers, connectors, or external actions.

## 2:40–2:55 — copy a workspace

Use **Create my workspace** and create `my-case`, or show the equivalent safe command:

```bash
python3 -m launchpad studio new my-case --template community-care
```

Show that the original template is unchanged and that the copy is a local, readable workspace for Codex-assisted study.

Open the copied workspace's example receipt and point out its fixture label and synthetic-data disclaimer. Explain that the local MCP bridge is consultative only; dashboard execution and public exposure remain future decisions, not hidden features.

Point to **Graduate to Real Omega**. Explain the boundary: finish the safe Studio/Test lesson, read the official risk disclaimer, then use the official Quick Start only after human approval. MiniMax belongs on the documented `ASICloud` provider path; credentials stay outside Studio, the channel stays private and owner-controlled, and the runtime receives only minimum permissions.

## 2:55–3:00 — final line

Say:

> Launchpad turns OmegaClaw's first lesson into a verifiable local path: inspect the proof, understand the artifacts, copy a safe example, and keep human authority explicit.

## Failure-safe variant

If the real proof is unavailable, show the `pending` screen and the exact terminal command. This is a valid demo of the honest boundary. Do not replace the state with a fixture, rename a failed file, or call a historical receipt a live proof.
