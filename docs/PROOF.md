# Real OmegaClaw proof

## Result

The end-to-end proof passed on 2026-08-28 on Apple Silicon:

```text
OmegaClaw connection                     PASS
Test provider connection                 PASS
Controlled response registration         PASS
WebSocket mission delivery               PASS
Real metta skill invocation              PASS
NAL stv result in LAST_SKILL_USE_RESULTS PASS
OmegaClaw WebSocket response              PASS

[PASS] 7/7 checks passed
1 passed in 31.14s
```

The captured machine-readable result is committed at [`docs/evidence/omega-proof.json`](evidence/omega-proof.json).

## What ran

- OmegaClaw-Core base tag: `v0.1.19`
- Verified base commit: `642c53676cf795cb7a0030823b36018c029b1416`
- Provider: upstream deterministic `Test` provider
- Channel: upstream WebSocket channel
- Reasoning path: OmegaClaw loop → `metta` skill → PeTTa/NAL → `stv` result → next loop context
- Governance: response required human review; Launchpad did not execute a change

The runtime reports `v0.1.19-dirty` because the reproducibility runner applies two disclosed patches: FAISS compilation is limited to two jobs to avoid out-of-memory failure, and the host-side RPC test controller maps Linux-only `POLLRDHUP` to `POLLHUP` on macOS. Neither patch changes OmegaClaw's agent loop, MeTTa skill, NAL behavior, or WebSocket channel.

## Reproduce

```bash
python3 -m launchpad reflect demo
python3 -m launchpad reflect prove
scripts/run-omegaclaw-proof.sh
python3 -m launchpad reflect receipt
```

The proof runner verifies the upstream commit before patching and refuses unexpected changes. It writes `omega-proof.json` only after every assertion passes. The local proof artifact is ignored by Git; the committed JSON is a captured example from the successful run.

## Honest boundary

The controlled Test provider supplies a deterministic tool-use sequence. Therefore this demonstrates real OmegaClaw integration and real NAL execution, not independent intelligence or autonomous self-improvement. The mismatch itself is established by deterministic event validation before OmegaClaw receives the facts.
