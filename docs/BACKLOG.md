# Practical backlog

## P0 — sprint delivery

- [x] Initialize the public repository and Python package.
- [x] Research the real OmegaClaw/MeTTa/Hyperon stack.
- [x] Define the First Reflection mission and evidence contracts.
- [x] Implement the controlled first run and hash-linked recorder.
- [x] Implement deterministic mismatch validation.
- [x] Implement reflection-context generation without a fake OmegaClaw response.
- [x] Implement human approval/rejection and controlled rerun.
- [x] Implement the before/after receipt.
- [x] Add a pinned real OmegaClaw WebSocket/Test-provider proof runner.
- [x] Add the integration test contract for a real MeTTa/NAL result.
- [x] Install/start Docker and make the upstream image build pass on this Mac.
- [x] Run the end-to-end proof and capture `omega-proof.json`.
- [ ] Record the three-minute demo.
- [x] Add verified evidence screenshots to the README.
- [ ] Add the published video link to the README.
- [x] Fill and submit the BGI Commons project page.

## P1 — immediate credibility

- [ ] Add JSON Schema files for mission, events, validation, decision, and receipt.
- [ ] Add chain-integrity verification for event hashes.
- [x] Add CI for Python 3.9–3.13 local tests.
- [ ] Add a Linux CI job for the pinned OmegaClaw proof.
- [ ] Open an upstream issue for documented test dependency/cleanup discrepancies.
- [ ] Test the walkthrough with one newcomer and record time-to-first-reflection.

## Studio P0 — First Proof

- [x] Add a loopback-only, standard-library Studio artifact reader.
- [x] Show honest preflight, proof, receipt, and template states in a six-screen wizard with an explicit Finish handoff.
- [x] Add the synthetic `factory-fault` template with human-readable rules, an illustrative MeTTa lesson scaffold, and positive/negative fixtures.
- [x] Add safe CLI and browser-assisted copying into private local workspaces.
- [x] Add English installation, architecture, security, future-scope, and three-minute demo documentation.
- [x] Add local preflight, start, and SSH-tunnel instruction helpers.
- [x] Add the real-runtime `factory-fault` proof and local receipt.
- [x] Add a bounded local STDIO MCP bridge with only `omega.reason` and `omega.get_receipt`.
- [x] Document agent-facing inputs, outputs, and safe MCP usage.
- [ ] Validate the complete installation on a clean supported VPS after explicit infrastructure approval.
- [ ] Record and publish the Studio three-minute demo.

## P2 — traction adapters

- [ ] OpenClaw event adapter.
- [ ] Hermes event adapter.
- [ ] Codex/Claude Code JSONL adapter.
- [ ] Generic webhook/MCP adapter.
- [ ] Two additional mission templates: tool-use policy and citation provenance.
- [ ] Optional real-LLM reflection mode with evaluation and cost disclosure.

## P3 — later product work

- [x] Browser wizard consuming the same contracts (delivered as the local-only Studio P0 reader).
- [ ] Shareable redacted receipts.
- [ ] Mission template registry.
- [ ] Aggregate onboarding failure analytics with explicit consent.

The sprint should not pull P2/P3 work forward until one real OmegaClaw proof passes end to end.
