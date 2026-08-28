# Launchpad architecture

## Boundary

```text
newcomer
   |
   v
OmegaClaw Launchpad CLI
   |-- journey manifest (.launchpad/config.json)
   |-- preflight doctor (Python/Git/Docker/key readiness)
   |-- offline proof (no credentials, no Docker)
   `-- generated launcher (clone pinned tag, delegate to upstream)
                                      |
                                      v
                       OmegaClaw-Core / PeTTa / Hyperon
                       MeTTa loop + plugins + providers + channels
```

## Why this is the smallest valid architecture

1. The Launchpad adds no second agent loop. OmegaClaw remains the runtime of record.
2. The manifest is the stable integration contract: source repository/ref, provider, channel, journey status, and next action.
3. `doctor` is deterministic. It can explain a missing prerequisite without consuming an LLM call.
4. Credentials are never written into the manifest or generated launcher. The generated command reads them from the user's shell because the upstream Docker launcher already expects that model.
5. The offline proof is explicitly labeled as an onboarding proof, not as a fake OmegaClaw runtime.

## Extension points after MVP

- Add a conversational `coach` mode that uses an OmegaClaw skill or a local LLM only after the deterministic journey is stable.
- Add a local WebSocket chat fixture for a true first-message smoke test.
- Add versioned compatibility checks against OmegaClaw-Core releases.
- Publish the journey manifest and checks as a reusable BGI Commons onboarding package.
