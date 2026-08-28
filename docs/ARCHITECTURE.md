# Architecture

## Smallest technically valid flow

```text
Human
  │ objective + rule + limits
  ▼
Mission contract
  ▼
Controlled executor ──► Recorder ──► events.jsonl
                                        │
                                        ▼
                              Deterministic validator
                                        │ verified facts
                                        ▼
                              Real OmegaClaw adapter
                       WebSocket → loop → metta/NAL → result
                                        │
                                        ▼
                              Human approve/reject
                                        │ approval only
                                        ▼
                              Controlled rerun + receipt
```

## Responsibility boundary

| Component | Responsibility | Explicit non-responsibility |
|---|---|---|
| Human | Defines objective, rules, limits, and decision | Does not need to program |
| Executor | Performs the controlled source-audit fixture | Does not judge its own honesty |
| Recorder | Writes observed events with a hash chain | Does not claim external-world truth |
| Validator | Compares declarations and observed events | Does not use AI or make moral judgments |
| OmegaClaw | Runs its real loop and MeTTa/NAL over verified facts | Does not discover the original mismatch or apply changes |
| Launchpad | Orchestrates contracts, review, proof, and receipt | Does not reimplement or impersonate OmegaClaw |

## State on disk

```text
.launchpad/first-reflection/<mission-id>/
├── 00-mission/
│   ├── mission.json
│   └── mission.md
├── 01-run-1/
│   ├── events.jsonl
│   ├── declarations.json
│   └── report.md
├── 02-validation/
│   ├── validation.json
│   └── validation.md
├── 03-reflection/
│   ├── reflection-context.json
│   ├── proposal.json
│   ├── omega-response.txt
│   └── omega-proof.json       # exists only after a passing live proof
├── 04-review/
│   ├── decision.json
│   └── decision.md
├── 05-rerun/
│   ├── events.jsonl
│   ├── declarations.json
│   ├── validation-rerun.json
│   └── validation-rerun.md
└── 06-receipt/
    ├── comparison.json
    └── final-receipt.md
```

## Real OmegaClaw boundary

The proof runner uses upstream OmegaClaw-Core `v0.1.19` at commit `642c536…`:

```text
Launchpad reflection-context.json
        │
        ▼
upstream WebSocket mock server
        │ user_message
        ▼
OmegaClaw channel + src/loop.metta
        │
        ▼
provider=Test returns a controlled skill sequence
        │
        ▼
(metta "(|- ...)") executes NAL in PeTTa
        │
        ▼
LAST_SKILL_USE_RESULTS + WebSocket response
        │
        ▼
omega-proof.json written only after assertions pass
```

The Test provider controls the proposed skill call, which makes the proof deterministic. The loop, transport, skill dispatch, PeTTa execution, and NAL result are real. This proves integration, not autonomous intelligence.

On low-memory Apple Silicon hosts, the runner applies the committed `low-memory-build.patch`, changing only FAISS compilation from unrestricted parallelism to two jobs. It verifies the upstream commit before applying this build-only patch and refuses unexpected Dockerfile changes.

The upstream mock RPC controller also assumes Linux `select.POLLRDHUP`. The committed `macos-test-harness.patch` aliases it to portable `POLLHUP` on macOS; this affects only the host-side test controller, not OmegaClaw runtime behavior.

## Safety properties

- No API key is needed for the proof.
- Reflection context contains facts, not executable host commands.
- OmegaClaw output is never executed as code by Launchpad.
- The proposal is scoped to the controlled rerun.
- Approval is explicit and stored.
- Existing mission evidence is not silently overwritten.
- Hash links reveal later event editing but do not prove that an external source was truthful.

## Future adapter contract

OpenClaw, Hermes, Codex, Claude Code, or another agent can later replace the controlled executor by emitting the same event and declaration contracts. That is the traction path, not part of the first sprint proof.
