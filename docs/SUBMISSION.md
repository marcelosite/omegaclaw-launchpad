# BGI Commons submission draft

## Title

**OmegaClaw First Reflection — Instrumented Missions for Governed Agent Learning**

## One-line proposition

A CLI onboarding lab where a newcomer watches OmegaClaw reason over verified agent evidence and must approve any controlled learning step.

## Problem

OmegaClaw introduces several powerful ideas at once: a MeTTa agent loop, Hyperon/PeTTa, NAL reasoning, providers, channels, memory, and Docker. A newcomer can install components without understanding why OmegaClaw is different—or what safe agent learning looks like.

## Solution

First Reflection begins with one concrete failure: an agent declares three sources, while its event record shows one. Launchpad records the mission, proves the mismatch with deterministic code, sends only the verified facts into a pinned real OmegaClaw runtime, observes a real MeTTa/NAL call, asks a human to approve or reject the proposal, reruns the controlled fixture, and writes a before/after receipt.

## What shipped

- A dependency-free Python CLI and readable file contracts.
- Hash-linked mission events and deterministic validation.
- Explicit human approval/rejection.
- A controlled rerun and comparison receipt.
- A pinned WebSocket/Test-provider harness for OmegaClaw-Core `v0.1.19`.
- A test that requires a real `metta` skill call and NAL `stv` in the loop.
- Documentation, tests, demo script, and future adapter boundary.

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

This sprint demonstrates a controlled mission with a deterministic Test provider. It does not claim autonomous self-improvement, universal fact checking, production-grade tamper resistance, or existing integrations with OpenClaw/Hermes/Codex/Claude. Those are explicit follow-up adapters.

## Links to submit

- Repository: https://github.com/marcelosite/omegaclaw-launchpad
- Demo video: pending
- Reproduction evidence: https://github.com/marcelosite/omegaclaw-launchpad/blob/main/docs/PROOF.md
- Captured proof: https://github.com/marcelosite/omegaclaw-launchpad/blob/main/docs/evidence/omega-proof.json
