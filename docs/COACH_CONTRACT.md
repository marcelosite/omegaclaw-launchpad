# Conversational coach contract

The MVP intentionally keeps the first-run checks deterministic. This is the contract a later OmegaClaw-powered coach can consume without coupling itself to the CLI's presentation.

## Inputs

```json
{
  "manifest": ".launchpad/config.json",
  "doctor": "omega-launchpad doctor --json",
  "user_message": "Why can I run the demo but not the real agent?"
}
```

## Output

```json
{
  "answer": "The offline proof needs no Docker or provider key. A real run also needs Python 3.10+, Docker, a provider key, and a channel setting.",
  "next_command": "python3 -m launchpad doctor",
  "risk": "low",
  "requires_confirmation": false
}
```

## Safety rules

- The coach may explain checks and propose commands, but must not request or persist secrets.
- It must not claim that `demo` ran OmegaClaw; `demo` is an onboarding proof.
- It must not silently launch Docker, join a channel, send messages, or spend inference credits.
- Any future destructive or externally visible action needs explicit user confirmation.
