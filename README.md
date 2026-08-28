# OmegaClaw Launchpad

An AI-native onboarding layer for taking a newcomer from zero to a first working [OmegaClaw](https://github.com/asi-alliance/OmegaClaw-Core) agent.

This is a BGI Commons HyperSprint #1, Track 2 project. It is intentionally an outer layer around the real OmegaClaw stack: Launchpad explains the architecture, checks readiness, creates a source-pinned launch handoff, and keeps credentials out of generated state.

## Quickstart

The offline proof needs only Python 3.9+:

```bash
python3 -m launchpad demo
```

Create a real launch handoff:

```bash
python3 -m launchpad onboard --provider Anthropic --channel irc
```

Then, on a machine ready for the upstream runtime:

```bash
export ANTHROPIC_API_KEY='your-key'
export OMEGACLAW_AUTH_SECRET='choose-a-local-secret'
.launchpad/run-omegaclaw.sh
```

Launchpad never writes the provider key. The generated launcher clones the pinned OmegaClaw-Core tag and delegates to its supported `scripts/omegaclaw` Docker launcher.

If you only want diagnostics:

```bash
python3 -m launchpad doctor
python3 -m launchpad doctor --json
```

## What the MVP does

- `demo` proves the onboarding journey offline.
- `doctor` checks Python, Git, Docker reachability, workspace writability, and provider-key readiness.
- `init` writes `.launchpad/config.json`, `.launchpad/run-omegaclaw.sh`, and a non-secret `.env.example`.
- `onboard` combines initialization, preflight, and the next recommended action.

The generated launch path is real, but it still requires the upstream prerequisites: Python 3.10+, Docker, an LLM provider key, and a configured communication channel. See [docs/DEMO.md](docs/DEMO.md) for the live handoff and [docs/MVP.md](docs/MVP.md) for the boundary.

## Verified architecture

OmegaClaw-Core is a MeTTa-based agent running on the OpenCog Hyperon stack. Its `run.metta` loads the core into the PeTTa runtime; `src/loop.metta` owns the recursive receive → prompt → LLM → skill dispatch → history loop; Python bridges provide providers, channels, embeddings, file I/O, and plugins. The core also exposes NAL/PLN reasoning and three main memory tiers.

Launchpad does not reimplement any of that. The evidence and implications are recorded in [docs/RESEARCH.md](docs/RESEARCH.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Development

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

No runtime dependencies are required for the Launchpad MVP. The upstream OmegaClaw dependencies are installed only when the generated handoff is used.

## Sprint materials

- [MVP scope and acceptance criteria](docs/MVP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Research snapshot](docs/RESEARCH.md)
- [Practical backlog](docs/BACKLOG.md)
- [Conversational coach contract](docs/COACH_CONTRACT.md)
- [Demo script](docs/DEMO.md)
- [BGI submission draft](docs/SUBMISSION.md)

## License

MIT. OmegaClaw-Core and Hyperon remain upstream projects with their own licenses and terms.
