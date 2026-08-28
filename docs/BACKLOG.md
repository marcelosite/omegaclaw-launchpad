# Practical backlog

These are intentionally small issues that can be implemented independently.

## P0 — sprint MVP

- [x] Initialize the repository with a Python package and tests.
- [x] Add source-pinned manifest and secret-safe launcher generation.
- [x] Add prerequisite doctor with JSON output.
- [x] Add offline onboarding proof.
- [x] Document the verified upstream architecture and MVP boundary.
- [ ] Run the generated launcher on Linux/macOS with Docker and record a real first-message transcript.
- [ ] Add one contributor walkthrough from `clone` to `first response`.

## P1 — reusable follow-up

- [ ] Add a local WebSocket fixture and an end-to-end smoke test.
- [ ] Add `launchpad verify` to parse startup logs and detect the first successful agent turn.
- [ ] Add version compatibility metadata for OmegaClaw-Core tags.
- [ ] Add an optional conversational coach that consumes the JSON journey state.
- [ ] Add translations for the first-run guide.

## P2 — later ecosystem work

- [ ] Publish a reusable onboarding skill/plugin for OmegaClaw.
- [ ] Add browser-based onboarding built from the same manifest/check contract.
- [ ] Measure time-to-first-agent and failure reasons across new contributors.
