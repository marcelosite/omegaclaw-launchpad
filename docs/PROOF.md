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

## Community Hospital Studio lesson

The Studio lesson has its own real-runtime harness. It uses the same pinned
OmegaClaw-Core checkout and controlled `Test`/WebSocket path, but sends only
fictional community-care facts. Reproduce it locally with:

```bash
scripts/run-community-care-proof.sh
```

The harness passed 7/7 checks on Apple Silicon: connection, Test provider,
controlled response, WebSocket delivery, real `metta` invocation, NAL/STV in
the next loop context, and the returned response. It writes:

```text
.launchpad/studio/runs/community-care/omega-proof.json
.launchpad/studio/runs/community-care/receipt.md
```

The proof marks `synthetic_only: true` and keeps
`human_approval_still_required: true`. Its conclusion
`human_review_required` is a lesson result only; it is not medical advice,
a diagnosis, causal finding, external-data validation, or action
authorization. The template's `rules.metta` remains an **Illustrative MeTTa
lesson** scaffold; the proof verifies the real runtime path and the explicit
controlled expression used by the harness, not a production rulebook.
