# OmegaClaw Launchpad Studio

OmegaClaw Launchpad Studio is a small, self-hosted onboarding lab for the first real OmegaClaw proof. It gives a newcomer a readable path from a VPS preflight to the existing First Reflection artifacts, then provides one synthetic template to copy and study.

## Scope

P0 is intentionally small:

- the `Test` provider is the only no-key path;
- the dashboard reads and explains artifacts;
- the real proof remains a terminal/Codex operation through `scripts/run-omegaclaw-proof.sh`;
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

## The six screens

1. **Welcome** — the proof's purpose and its limits.
2. **Preflight** — read-only repository, upstream, Python, Docker, architecture, memory, and disk checks.
3. **First real proof** — actual First Reflection status and artifacts. `verified` is shown only when the real harness wrote `omega-proof.json`.
4. **Learn** — the visual chain `agent/Test → frozen facts → MeTTa/NAL → STV → response → receipt.md`.
5. **Your case** — the synthetic case, its rules and tests, plus **Create my workspace** inside the same screen.
6. **Finish** — a clear handoff: review the local files, then connect Codex through the bounded local MCP bridge only after the factory-fault proof is verified.

The dashboard does not replace the proof runner. To run the real proof, prepare the existing mission and use the terminal command documented in [PROOF.md](PROOF.md):

```bash
scripts/run-omegaclaw-proof.sh
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

Register that local STDIO command in Codex only after reviewing the project-local configuration. It exposes exactly `omega.reason` and `omega.get_receipt`. `omega.reason` consults the verified synthetic lesson and writes a local receipt; it does not run a provider, shell command, connector, or external action. It also has one fixed release-readiness teaching packet: two recorded positions, a passed unit-test record, a missing security-check record, and a `human_review_required` receipt. That packet is deterministic local teaching logic, not an externally validated or newly executed OmegaClaw decision. `omega.get_receipt` accepts only a logical receipt ID returned by the first tool. No absolute workspace path is returned by the API. See [the agent guide](AGENT_GUIDE.md#first-structured-disagreement-test) for the copyable packet.

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
