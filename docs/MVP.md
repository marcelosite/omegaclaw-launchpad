# MVP scope and acceptance criteria

## Sprint outcome

The MVP is one governed learning loop, not a general agent platform:

> A controlled agent claims three sources, an independent recorder shows one, a deterministic validator proves the mismatch, OmegaClaw reasons over the verified facts using real MeTTa/NAL, a human decides, and a controlled rerun produces a before/after receipt.

## In scope

- One source-audit mission with a human-readable contract.
- Hash-linked JSONL events and explicit declarations.
- Deterministic validation; no LLM decides whether `3 == 1`.
- Frozen reflection context that distinguishes evidence, rule, and uncertainty.
- CLI approval/rejection with no automatic changes.
- Controlled rerun and receipt.
- Pinned OmegaClaw-Core WebSocket/Test-provider harness.
- A real `(metta ...)` NAL invocation recorded from the upstream loop.
- A three-minute reproducible demo.

## Out of scope

- Hosted dashboard, accounts, or database.
- General autonomous self-improvement.
- Applying code or policy changes proposed by a model.
- Production security claims for local hashes.
- OpenClaw, Hermes, Claude, Codex, or MCP adapters.
- A paid LLM as a demo requirement.
- Multiple mission templates.

## Acceptance criteria

### Local instrumented mission

- `python3 -m launchpad reflect demo` runs on Python 3.9+ without Docker or keys.
- The first run records one distinct source while declaring three.
- The validator deterministically returns `FAIL` with expected, observed, and evidence IDs.
- Rerun is impossible until a human decision is recorded as `approved`.
- An approved rerun records three sources and returns `PASS`.
- The receipt clearly says the OmegaClaw proof is pending when no runtime proof exists.

### Real OmegaClaw proof

- The runner verifies upstream commit `642c53676cf795cb7a0030823b36018c029b1416`.
- The Docker image is built locally from that commit; `latest` is not used.
- OmegaClaw runs with provider `Test` and channel `websocket`, so no LLM API key is needed.
- The test observes a real `metta` skill call containing the mission marker.
- A resulting `stv` appears in `LAST_SKILL_USE_RESULTS` in the real loop.
- The response returns through the real WebSocket channel.
- Only a successful test may write `omega-proof.json` with `status: verified`.

## Definition of honest failure

If Docker, Python 3.10+, the upstream build, or the end-to-end test fails, the submission must say the OmegaClaw proof is pending. The local mission remains useful but must not be presented as a live OmegaClaw run.
