# Testing and recording guide

This guide provides three levels of proof. Use a new mission identifier for every attempt; Launchpad deliberately refuses to overwrite existing evidence.

## Level 1 — one-minute local check

Requirements: Python 3.9+ and Git. No Docker, LLM, or API key is required.

```bash
git clone https://github.com/marcelosite/omegaclaw-launchpad.git
cd omegaclaw-launchpad
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m launchpad reflect demo --mission-id quick-test-001
```

Expected result:

```text
FIRST RUN
Expected: 3 distinct sources
Observed: 1 distinct sources
Result: FAIL

OMEGACLAW PROOF: PENDING (not simulated)
HUMAN DECISION: APPROVED

CONTROLLED RERUN
Expected: 3 distinct sources
Observed: 3 distinct sources
Result: PASS
```

This level proves the instrumented mission, deterministic validator, approval gate, rerun, and receipt. It honestly does not claim that OmegaClaw ran.

## Level 2 — staged human walkthrough

Prepare the readable assets without making the decision:

```bash
scripts/prepare-demo-assets.sh video-demo-001
```

Review the proposal:

```bash
python3 -m launchpad reflect review --mission-id video-demo-001
```

Choose `2` to display the complete reflection context. The menu returns; choose `1` to approve the controlled rerun. Then finish:

```bash
python3 -m launchpad reflect rerun --mission-id video-demo-001
python3 -m launchpad reflect receipt --mission-id video-demo-001
```

## Level 3 — real OmegaClaw integration proof

Requirements: Docker engine, Git, Python 3.10+, and the prepared mission from Level 2. No paid LLM or API key is required.

Check readiness:

```bash
python3 -m launchpad reflect prove --mission-id video-demo-001
```

Run the pinned upstream proof before approving the rerun:

```bash
scripts/run-omegaclaw-proof.sh video-demo-001
```

A passing run must display:

```text
[PASS] 7/7 checks passed
1 passed
```

Now make the human decision and create the final receipt:

```bash
python3 -m launchpad reflect review --mission-id video-demo-001
python3 -m launchpad reflect rerun --mission-id video-demo-001
python3 -m launchpad reflect receipt --mission-id video-demo-001
```

The final receipt must say `Before: FAIL`, `After approved rerun: PASS`, `Human decision: APPROVED`, and `OmegaClaw proof status: VERIFIED`.

## Recording and screenshot assets

A prepared four-frame evidence kit is available in [`docs/assets/video/`](assets/video/README.md). It contains three 1600×900 video cards, the original macOS Terminal review capture, and the editable HTML source used to render the cards.

For mission `video-demo-001`, all generated evidence is under:

```text
.launchpad/first-reflection/video-demo-001/
```

Capture these assets in order:

1. `00-mission/mission.md` — the objective and rule.
2. `01-run-1/events.jsonl` — one observed `source.opened` event.
3. `02-validation/validation.md` — expected 3, observed 1, `FAIL`.
4. `03-reflection/reflection-context.json` — grounded facts and the no-auto-apply constraint.
5. The proof terminal — WebSocket, `metta`, NAL `stv`, and `7/7` checks.
6. `03-reflection/omega-proof.json` — machine-readable real-runtime evidence.
7. The review menu — options to inspect, approve, reject, or exit.
8. `06-receipt/final-receipt.md` — before/after result and verified proof status.

On macOS, open an asset with:

```bash
open .launchpad/first-reflection/video-demo-001/02-validation/validation.md
```

For a terminal recording, enlarge the text, hide unrelated windows, and never show credentials. The real proof uses the deterministic Test provider, so there is no API key to display.

## Interpretation boundary

- The validator proves a mismatch in recorded events; it does not prove universal truth.
- The Test provider controls the tool-use sequence; it does not measure independent LLM intelligence.
- The OmegaClaw loop, WebSocket channel, `metta` skill dispatch, PeTTa/NAL execution, and returned `stv` are real.
- The human approval remains a required governance boundary.
