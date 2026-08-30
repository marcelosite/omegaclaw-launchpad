# Claude Code guide

Read and follow [`AGENTS.md`](AGENTS.md) before changing or running this
repository. It is the canonical safety and product contract for every coding
agent.

For the first successful experience:

1. Read `README.md`, `docs/INSTALL_WITH_CODEX.md`, and
   `docs/AGENT_GUIDE.md`.
2. Run `scripts/launchpad-start.sh` from the repository root on the user's
   computer. On a private VPS, run `scripts/launchpad-start.sh --background`
   so the Wizard survives the agent terminal session.
3. Use the deterministic `Test` provider. Do not request an LLM key.
4. Do not bypass preflight, proof, receipt, or human-approval checks.
5. Keep Studio on `127.0.0.1:8765`; never expose it publicly.
6. Before adapting the example, read
   `examples/lighthouse-in-the-fog/CLAUDE.md` and work only in a private copy.

When the host is a VPS, tell the user to run this command in a terminal on
their own computer, replacing the target with the SSH name they use for that
VPS:

```sh
ssh -N -L 8876:127.0.0.1:8765 <your-vps-ssh-target>
```

Then they open `http://127.0.0.1:8876`. Never claim that the VPS loopback URL
is directly reachable from the user's computer, and never expose Studio on a
public interface.

The optional MCP bridge is bounded and consultative. It does not rerun
OmegaClaw, validate external facts, execute actions, or authorize decisions.
