# BGI Commons submission draft

## Project

OmegaClaw Launchpad — Track 2: Onboarding OmegaClaw

## One-line proposition

An AI-native onboarding layer that takes newcomers from zero to their first working OmegaClaw agent.

## What shipped

Launchpad is a small, open-source CLI that makes the real OmegaClaw architecture legible, checks the local environment, creates a source-pinned and secret-safe launch handoff, and provides an offline proof that can be run before Docker or API credentials are available.

## Why it matters

The upstream stack is powerful but crosses several conceptual and operational boundaries at once: PeTTa, Hyperon, MeTTa, Python bridges, plugins, providers, channels, Docker, and credentials. Launchpad turns those boundaries into explicit milestones and actionable diagnostics.

## BGI alignment

- It lowers the barrier to participation and contribution.
- It preserves user control over credentials and launch decisions.
- It favors transparent, deterministic checks over opaque setup magic.
- It points users to the upstream open-source runtime instead of creating a private fork.
- It creates a reusable building block for future tutorials, agents, and community education.

## Known limitation

The first sprint version is a CLI and launch handoff, not a hosted conversational coach. The manifest/JSON contract is the foundation for that next layer without making it a deadline risk.
