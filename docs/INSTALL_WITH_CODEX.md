# Install with a coding agent

Point Codex or Claude Code at this repository. Codex reads `AGENTS.md`; Claude
Code reads `CLAUDE.md`, which delegates to the same canonical rules. Both
agents should also read `docs/AGENT_GUIDE.md`. Before adapting the example,
Codex reads `examples/lighthouse-in-the-fog/AGENTS.md` and Claude Code reads
`examples/lighthouse-in-the-fog/CLAUDE.md`.

Run **on the user's computer or private VPS, from the repository root**:

```sh
scripts/launchpad-start.sh
```

The script performs Docker preflight, checks the example, runs the pinned Test-provider proof, verifies the receipt, and starts the loopback Wizard. No LLM key is required for this path.

The agent's first safe task is:

> Explain `examples/lighthouse-in-the-fog/`, run its validator and tests, copy it to a private workspace, and propose one small change. Preserve provenance, `human_approval_required`, and `external_actions: []`. Do not add credentials or external actions.

The optional MCP bridge is separate and manual. It is a local STDIO consultation surface with exactly `omega.reason` and `omega.get_receipt`; it does not rerun OmegaClaw or authorize actions. See [AGENT_GUIDE.md](AGENT_GUIDE.md#mcp-optional).

Never paste a MiniMax key into the repository or chat. Direct MiniMax and ASI Cloud use different upstream providers and environment variables; see [PROVIDERS.md](PROVIDERS.md).
