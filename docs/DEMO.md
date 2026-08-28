# Demo script

## 90-second offline proof

```bash
python3 -m launchpad demo
```

Say:

> OmegaClaw Launchpad is not replacing OmegaClaw. It removes the first-run ambiguity around the real stack. The offline proof shows the journey and the handoff contract without pretending that a fake local loop is OmegaClaw.

## 3-minute real handoff

On a machine with Python 3.10+, Docker, and an LLM provider key:

```bash
python3 -m launchpad onboard --provider Anthropic --channel irc
export ANTHROPIC_API_KEY='...'
export OMEGACLAW_AUTH_SECRET='a-local-secret'
.launchpad/run-omegaclaw.sh
```

The launcher clones the pinned upstream tag and delegates to its supported `scripts/omegaclaw` Docker path. The demo should show the upstream startup log, a channel message, and the first response.

Do not record credentials, and do not describe the offline proof as a live OmegaClaw run.
