# BGI Commons submission draft

## Title

**OmegaClaw Launchpad — First Reflection and Studio**

## One-line proposition

A self-hosted, no-key onboarding lab that lets a newcomer understand and verify the real OmegaClaw reasoning path, then hand a bounded receipt to an agent through MCP.

## Problem

OmegaClaw introduces several powerful ideas at once: a MeTTa agent loop, Hyperon/PeTTa, NAL reasoning, providers, channels, memory, and Docker. A newcomer can install components without understanding why OmegaClaw is different—or what safe agent learning looks like.

## Solution

OmegaClaw Launchpad turns the learning curve into small, verifiable missions. Its first working module, First Reflection, begins with one concrete failure: an agent declares three sources, while its event record shows one. Launchpad records the mission, proves the mismatch with deterministic code, sends only the verified facts into a pinned real OmegaClaw runtime, observes a real MeTTa/NAL call, asks a human to approve or reject the proposal, reruns the controlled fixture, and writes a before/after receipt.

Launchpad Studio extends that path for a nontechnical user: its human-first Wizard explains the referee story in plain language, blocks each Next step until the required evidence exists, labels where every command runs, offers the synthetic `factory-fault` lesson, copies a readable workspace, and provides a bounded local MCP handoff with only `omega.reason` and `omega.get_receipt`. The MCP also includes one closed release-readiness teaching packet so an agent can submit a structured disagreement without turning the bridge into an unrestricted multi-agent service.

## What shipped

- A dependency-free Python CLI and readable file contracts.
- Hash-linked mission events and deterministic validation.
- Explicit human approval/rejection.
- A controlled rerun and comparison receipt.
- A pinned WebSocket/Test-provider harness for OmegaClaw-Core `v0.1.19`.
- A test that requires a real `metta` skill call and NAL `stv` in the loop.
- Documentation, tests, demo script, and future adapter boundary.
- Launchpad Studio human-first Wizard with evidence blockers, explicit command locations, Finish handoff, and MCP setup guidance.
- Real pinned-runtime factory-fault lesson proof using Test/WebSocket/MeTTa/NAL.
- Local STDIO MCP bridge with logical receipts, one closed Conflict Packet teaching test, and no external actions.

## Why OmegaClaw is central

The mismatch itself is intentionally detected without AI. OmegaClaw is central to the learning experience: the newcomer sends grounded evidence through its real channel and loop, invokes MeTTa/NAL, observes uncertainty propagation, and sees the result stop at a human governance gate. The project teaches capabilities specific to OmegaClaw instead of placing its logo over a generic validator.

## BGI alignment

- **Beneficial systems:** proposals do not become changes without human approval.
- **Epistemic humility:** observation, inference, confidence, and claims remain separate.
- **Transparency:** every stage produces human-readable and machine-readable evidence.
- **Openness:** the project extends the public upstream runtime without a private replacement.
- **Reusable commons:** future agent ecosystems can emit the same mission/event contract.
- **Accessible onboarding:** a nontechnical person can understand the failure before learning the vocabulary.

## Demonstrated result

Local demonstrated result:

```text
before: expected 3 / observed 1 / FAIL
decision: human-approved
after: expected 3 / observed 3 / PASS
```

Full demonstrated result:

```text
OmegaClaw v0.1.19 commit verified
WebSocket round trip verified
metta skill invocation verified
NAL stv in real loop verified
7/7 harness checks; pytest 1 passed
```

## Honest limitation

This sprint demonstrates controlled missions with a deterministic Test provider. The Studio MCP bridge is consultative and synthetic; it does not claim autonomous self-improvement, universal fact checking, production-grade tamper resistance, or a credentialed integration with OpenClaw/Hermes/Codex/Claude. Those are explicit follow-up adapters.

## Links to submit

- Repository: https://github.com/marcelosite/omegaclaw-launchpad
- Demo video: pending — to be produced as a separate deliverable
- Reproduction evidence: https://github.com/marcelosite/omegaclaw-launchpad/blob/main/docs/PROOF.md
- Captured proof: https://github.com/marcelosite/omegaclaw-launchpad/blob/main/docs/evidence/omega-proof.json
