# OmegaClaw Launchpad Studio — post-P0 roadmap

This document preserves the broader proposal. The bounded local MCP handoff is implemented; every other item below remains future work and needs a separate decision.

## P1 — agent use (bounded bridge implemented locally)

### Minimal MCP bridge

The local handoff now exposes exactly two tools after the real community-care proof is verified:

```text
omega.reason
omega.get_receipt
```

The STDIO bridge accepts only known internal IDs, references the verified synthetic lesson, and persists a receipt before returning. It has no shell, provider, connectors, administrative operations, external actions, or arbitrary MeTTa. It is not a general OmegaClaw executor.

### More guided workspaces

- guided editing of structured facts;
- workspace test execution;
- versioned Markdown/JSON receipts;
- visual comparison of facts, rules, and results.

## P2 — rules and runtime

### Restricted rulebook compiler

A canonical structured source, for example `rules.yaml`, may be compiled into:

```text
rules.md
rules.metta
tests.json
```

The compiler must accept only an explicitly documented subset of predicates, conjunctions, conclusions, and STVs. It must reject imports, skills, commands, and arbitrary MeTTa.

### Change proposals

An LLM may eventually suggest a rule in draft mode. It must never activate the rule. A human reviews the diff, runs the tests, and publishes a new rulebook version.

### Isolated executor

Before a web button starts a real proof, create and prove an executor that preserves the existing harness checkpoints without giving the dashboard a Docker socket. This is not simple repackaging: the current proof runner starts and observes containers through Docker on the host.

## P3 — connectivity and production

- the pinned v0.1.19 upstream configuration documents MiniMax through the `ASICloud` provider, but any real use still requires a fresh check of the endpoint, model, tool-call format, authentication, data policy, and effective runtime behavior;
- reproduced matrix on `linux/arm64` and `linux/amd64`;
- pinned images and Linux CI for the proof;
- public exposure only with reverse proxy, TLS, authentication, rate limiting, updates, and backups;
- connectors, plugins, and additional templates;
- multi-user dashboards and stronger storage only if real demand justifies them.

## Risks to resolve before each phase

### Oracle Free Tier

Do not assume that a free A1/ARM or x86 machine supports the build. Confirm architecture, RAM, disk, Docker Engine, and the real proof on the target. The installer should fail early with a diagnosis; it must not create swap, open a firewall, or provision resources automatically.

### LLM providers

The `Test` provider is the only already-proven no-credential path in Launchpad. No key may appear in chat, Git, UI, receipts, or logs. The pinned upstream v0.1.19 README and installer list MiniMax through `ASICloud`; Launchpad has not exercised that credentialed path, so it must be rechecked and explicitly approved before use rather than inferred from generic OpenAI compatibility.

### Product limits

The Studio is an onboarding and integration lab. It must not present itself as an autonomous decision engine, safety diagnosis system, truth certifier, or compliance validator.
