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

If the repository is on a private VPS, run this instead **in the VPS terminal**:

```sh
scripts/launchpad-start.sh --background
```

The command prints a success message and leaves Studio running after the agent
session closes. Then run this **in a separate terminal on the user's own
computer**, replacing the target with the SSH name used for that VPS:

```sh
ssh -N -L 8876:127.0.0.1:8765 <your-vps-ssh-target>
```

Keep that tunnel terminal open and open `http://127.0.0.1:8876` in the local
browser. The VPS address `127.0.0.1:8765` is intentionally not directly
reachable from the user's computer.

The agent's first safe task is:

> Explain `examples/lighthouse-in-the-fog/`, run its validator and tests, copy it to a private workspace, and propose one small change. Preserve provenance, `human_approval_required`, and `external_actions: []`. Do not add credentials or external actions.

The optional MCP bridge is separate and manual. It is a local STDIO consultation surface with exactly `omega.reason` and `omega.get_receipt`; it does not rerun OmegaClaw or authorize actions. See [AGENT_GUIDE.md](AGENT_GUIDE.md#mcp-optional).

Never paste a MiniMax key into the repository or chat. Direct MiniMax and ASI Cloud use different upstream providers and environment variables; see [PROVIDERS.md](PROVIDERS.md).
