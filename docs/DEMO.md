# Three-minute demo

## Before recording

Use a clean checkout. Do not show credentials. For the full proof, ensure Docker is running and Python 3.10+ is active.

## 0:00–0:25 — the problem

Say:

> An AI agent says it consulted three sources. Its independent event record contains one. Launchpad turns this understandable failure into a first hands-on lesson with OmegaClaw.

## 0:25–1:10 — local evidence and human control

Run the staged commands or the compact demo:

```bash
python3 -m launchpad reflect demo --mission-id recorded-demo
```

Show `validation.md`: expected `3`, observed `1`, result `FAIL`. Show that the screen says `OMEGACLAW PROOF: PENDING`, because the local layer refuses to fake the runtime.

Explain:

> Ordinary code finds the objective mismatch. We do not spend an LLM call to count to three. The human remains responsible for approval.

## 1:10–2:15 — real OmegaClaw proof

With the prepared mission:

```bash
python3 -m launchpad reflect prove --mission-id recorded-demo
scripts/run-omegaclaw-proof.sh recorded-demo
```

Show the passing test steps:

1. OmegaClaw connects through WebSocket.
2. Verified facts enter the real loop.
3. The `metta` skill is observed.
4. The NAL `stv` appears in `LAST_SKILL_USE_RESULTS`.
5. The response returns through the OmegaClaw channel.
6. `omega-proof.json` is written as `verified`.

Say:

> The LLM side is deterministic, using OmegaClaw's Test provider. The agent loop, WebSocket transport, skill execution, and NAL result are real. No paid model or API key is required.

## 2:15–2:50 — decision and outcome

For the staged version, run:

```bash
python3 -m launchpad reflect review --mission-id recorded-demo
python3 -m launchpad reflect rerun --mission-id recorded-demo
python3 -m launchpad reflect receipt --mission-id recorded-demo
```

Choose `1`. Show the final receipt: first run `FAIL / 1`, rerun `PASS / 3`, human decision `APPROVED`, OmegaClaw proof `VERIFIED`.

## 2:50–3:00 — close

Say:

> This is one small stair, not a general self-improving agent. The reusable contribution is the mission, evidence, reflection, approval, and receipt contract. Future OpenClaw, Hermes, Codex, and Claude adapters can enter through that same boundary.

## Fallback disclosure

If the full proof is not passing, record only the local cycle and say:

> The instrumented mission and approval loop work locally. The real OmegaClaw end-to-end proof remains pending on this host.

Never use a saved or edited transcript as evidence of a live run.
