# OmegaClaw Launchpad Studio

OmegaClaw Launchpad Studio is a small, self-hosted onboarding lab for the first real OmegaClaw proof. Its nine-step Wizard uses one question, one action, and one proof per screen. A newcomer moves from a local or VPS preflight to the pinned factory-fault proof, reads what the result means, copies one synthetic template, checks both fixtures, and finishes with a bounded MCP handoff.

## Scope

P0 is intentionally small:

- the `Test` provider is the only no-key path;
- the dashboard reads and explains artifacts;
- the real proof remains a terminal/Codex operation through `scripts/run-factory-fault-proof.sh` (the separate First Reflection proof remains available through `scripts/run-omegaclaw-proof.sh`);
- the `factory-fault` project uses fictional data only;
- all artifacts remain local files.

The dashboard does not run shell commands, control Docker, receive a Docker socket, accept uploads, validate outside sources, diagnose equipment, or perform external actions.

## Prerequisites

- a checked-out Launchpad repository;
- Python 3.10 or newer for the real proof;
- Git for the existing proof runner;
- Docker Engine/Desktop only when running the real proof;
- an SSH account on the VPS when using a remote host.

No LLM key is required for the First Proof path. Do not paste credentials into the dashboard, a workspace, a receipt, or a chat transcript.

## Start locally

From the repository root:

```bash
scripts/studio-doctor.sh
scripts/studio-start.sh
```

`studio-start.sh` stays in the foreground and binds only to `127.0.0.1:8765`. Stop it with `Ctrl+C`. It does not install software, create a daemon, use systemd, open a firewall port, or connect to a remote host.

Open the local interface:

```text
http://127.0.0.1:8765
```

For a VPS, use the printed tunnel command from:

```bash
scripts/studio-open.sh ubuntu@VPS_IP
```

That helper only prints instructions. It never opens an SSH connection.

## The nine screens

1. **Who decides?** — the referee story and the recommendation/action boundary.
2. **Where?** — whether commands run on the computer or a private VPS.
3. **Is it ready?** — run and confirm the read-only preflight report.
4. **Real proof** — run and confirm the pinned factory-fault Test/WebSocket/MeTTa/NAL proof.
5. **What does green mean?** — open the receipt and answer the honest interpretation question.
6. **My case** — copy the synthetic case into a logical local workspace ID.
7. **My tests** — open and confirm the positive and negative fixtures.
8. **One agent** — confirm the local MCP bridge exposes exactly two consultation tools.
9. **Finish** — a clear next prompt and handoff to the local MCP bridge.

The dashboard does not replace the proof runner. To run the first Studio proof, use this fixed terminal command from the repository root:

```bash
scripts/run-factory-fault-proof.sh
```

Until the real artifact exists, the Studio must show `pending`. A failed run remains `failed` or `pending`; it must never be presented as verified. The factory-fault lesson is a scaffold until `scripts/run-factory-fault-proof.sh` writes its pinned-runtime proof and receipt.

## Local artifacts

The Studio stores its preflight and private workspace copies below `.launchpad/studio/` and reads the existing First Reflection tree below `.launchpad/first-reflection/`. Evidence remains in readable JSON, JSONL, text, and Markdown files rather than a database. The dashboard never modifies proof or receipt artifacts.

The exact paths and allowed file types are described in [STUDIO_ARCHITECTURE.md](STUDIO_ARCHITECTURE.md). The browser receives logical IDs, not arbitrary filesystem paths.

## factory-fault limits

`factory-fault` is a teaching fixture. Its signals, thresholds, timestamps, and outcome are fictional. Its only derived statement is `manual_inspection_recommended` when the two example signals coexist. It does not claim a fault, identify a cause, validate telemetry, or command a machine to stop.

Its `rules.metta` file is an **Illustrative MeTTa lesson**, not a reviewed real-runtime rule. Studio P0 does not execute that scaffold in OmegaClaw, so the template is not evidence that the rule runs in the pinned runtime.

Copy it with:

```bash
python3 -m launchpad studio new my-case --template factory-fault
```

Then ask Codex to adapt the local facts and tests while preserving the disclaimer and human review boundary. The P0 web screen does not edit executable rules.

## Local MCP handoff

After the factory-fault proof is verified, run the bounded bridge from the repository root:

```bash
scripts/studio-mcp.sh
```

Check the bridge and its first two tools from a second terminal:

```bash
scripts/studio-mcp-check.sh
```

The check is a real local JSON-RPC handshake. It records only `.launchpad/studio/mcp-check.json` and requires the verified factory-fault proof. The Wizard waits for this check before its final MCP confirmation. Register one agent manually with `codex mcp add omegaclaw-launchpad -- scripts/studio-mcp.sh`, then verify that the agent lists exactly `omega.reason` and `omega.get_receipt`.

Register that local STDIO command in Codex only after reviewing the project-local configuration. It exposes exactly `omega.reason` and `omega.get_receipt`. `omega.reason` consults the verified synthetic lesson and writes a local receipt; it does not run a provider, shell command, connector, or external action. It supports the fixed release-readiness teaching packet and a bounded general consultation packet for local tests. A general packet records claims, evidence labels, a human rule, missing/unknown facts, conflicts, and forbidden actions; its deterministic result is `human_review_required` when a conflict or missing fact exists, otherwise `recorded_observation`. Inputs are self-reported and never externally validated. `omega.get_receipt` accepts only a logical receipt ID returned by the first tool. No absolute workspace path is returned by the API. See [the agent guide](AGENT_GUIDE.md#bounded-general-consultation) for the copyable shape.

### Use the MCP from a VPS without opening a public port

The bridge is a STDIO process, not a public HTTP service. A local agent can reach a VPS bridge through an SSH command that carries STDIO over the encrypted connection:

```bash
codex mcp add omegaclaw-vps -- ssh <your-vps-alias> 'cd /path/to/omegaclaw-launchpad && scripts/studio-mcp.sh'
```

Run this on the computer where Codex is installed. The VPS keeps Studio and the MCP bridge on loopback; no firewall rule or public port is needed. For a shared public service, stop and design authentication, TLS, rate limits, per-workspace authorization, and retention first.

## Graduate to Real Omega

Graduate only after completing and understanding the safe Studio/Test path. Real OmegaClaw is autonomous software with a different risk profile; read the [official risk disclaimer](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/README.md#disclaimer) and obtain explicit human approval before adding credentials, a communication channel, or broader permissions.

Then follow the [official OmegaClaw Quick Start for the pinned v0.1.19 runtime](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/README.md#run-omegaclaw-in-docker). Its provider table documents `ASICloud` for MiniMax through the ASI Alliance inference endpoint. Reconfirm that provider contract at the time of use, keep the API key outside Studio, Git, logs, receipts, and chat, and stop if the current documentation or runtime differs.

Use a private, owner-controlled channel with a unique authentication secret. Start with an isolated runtime, no unneeded skills or connectors, and only the minimum filesystem, network, channel, and command permissions required for the approved case. Studio does not perform any of these graduation steps.

## Troubleshooting

**The preflight says Docker is unavailable.** The offline reader and template remain useful. Start Docker before attempting the real proof; the doctor never starts it for you.

**The browser cannot connect.** Confirm that `studio-start.sh` is still running and that the browser uses `http://127.0.0.1:8765`. On a VPS, keep the SSH tunnel open in a separate terminal.

**The proof is pending.** This is an honest state, not an error in the dashboard. Follow [PROOF.md](PROOF.md) and run the existing proof runner from the terminal.

**The proof fails.** Preserve the failure artifacts and environment details. Do not rename a failed artifact to `omega-proof.json` or manually mark it verified.

**A template copy is rejected.** Use a simple lowercase slug such as `my-case`; paths, `..`, absolute paths, and unknown template names are intentionally rejected.

## Security boundary

P0 assumes one human using their own local browser and SSH session. Do not publish port 8765 directly, add a domain, or expose the Studio to the internet. Public exposure, authentication, TLS, and other operational controls require a separate future decision.
