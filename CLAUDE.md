# Claude Code guide

Read and follow [`AGENTS.md`](AGENTS.md) before changing or running this
repository. It is the canonical safety and product contract for every coding
agent.

For the first successful experience:

1. Read `README.md`, `docs/INSTALL_WITH_CODEX.md`, and
   `docs/AGENT_GUIDE.md`.
2. Run `scripts/launchpad-start.sh` from the repository root on the user's
   computer or private VPS.
3. Use the deterministic `Test` provider. Do not request an LLM key.
4. Do not bypass preflight, proof, receipt, or human-approval checks.
5. Keep Studio on `127.0.0.1:8765`; never expose it publicly.
6. Before adapting the example, read
   `examples/lighthouse-in-the-fog/CLAUDE.md` and work only in a private copy.

The optional MCP bridge is bounded and consultative. It does not rerun
OmegaClaw, validate external facts, execute actions, or authorize decisions.
