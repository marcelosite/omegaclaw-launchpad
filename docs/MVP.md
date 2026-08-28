# MVP scope and acceptance criteria

## In scope

- `omega-launchpad demo`: a no-network, no-key onboarding proof.
- `omega-launchpad doctor`: prerequisite checks with human and JSON output.
- `omega-launchpad init`: provider/channel selection and secret-safe generated artifacts.
- `omega-launchpad onboard`: init + preflight + contextual next action.
- A pinned OmegaClaw-Core ref and a generated launcher that delegates to `scripts/omegaclaw`.
- Research, architecture, backlog, demo, and submission documentation.

## Out of scope for the sprint

- Rewriting OmegaClaw core or its MeTTa loop.
- Building a hosted dashboard, account system, or multi-user service.
- Managing or storing API keys.
- Implementing a new channel or a new reasoning engine.
- Claiming that the offline proof is an actual OmegaClaw run.

## Acceptance criteria

- A contributor can clone this repository and run the offline proof on Python 3.9+.
- `init` creates a manifest and launcher without embedding a provider secret.
- `doctor --json` is suitable for future UI/agent consumption.
- On a machine with Docker and a provider key, the generated launcher can fetch the pinned upstream source and hand off to its supported Docker launcher.
- The README tells a newcomer exactly which path is offline, which path requires Docker/credentials, and where the upstream architecture is documented.
