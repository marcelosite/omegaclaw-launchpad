# Install and open Studio with Codex

This guide is a human-approved instruction boundary for Codex. It describes local repository work and a loopback-only Studio. It does not authorize GitHub changes, Oracle provisioning, remote SSH, domain setup, firewall changes, or MiniMax configuration.

## Copyable prompt

Give Codex this prompt from the repository root:

```text
Install OmegaClaw Launchpad Studio locally from this checked-out repository.

First run only the read-only preflight:
  scripts/studio-doctor.sh

Show me the report and stop if Python, Docker, architecture, memory, or disk is blocked. Do not install packages, ask for credentials, access GitHub, access Oracle, open SSH connections, change the firewall, configure a domain, or configure MiniMax.

If I explicitly approve starting the local interface, run:
  scripts/studio-start.sh

Keep it in the foreground on 127.0.0.1:8765. Do not use systemd, a daemon, Docker-in-Docker, or a Docker socket. I will open the URL locally, or I will run scripts/studio-open.sh myself to print an SSH tunnel command.

The first proof must use the existing terminal/Codex runner and provider Test. Never claim verified unless the real omega-proof.json exists.
```

## Local steps

From the repository root:

```bash
scripts/studio-doctor.sh
scripts/studio-start.sh
```

The doctor writes exactly one approved persistent artifact:

```text
.launchpad/studio/preflight.json
```

It does not write credentials or a shell history file. It does not install or alter anything on the host. The start helper runs in the foreground and listens only on loopback.

## VPS tunnel

On the local computer, print the command:

```bash
scripts/studio-open.sh ubuntu@VPS_IP
```

Then, after checking the displayed target yourself, run the printed SSH command in your own terminal:

```bash
ssh -N -L 8765:127.0.0.1:8765 ubuntu@VPS_IP
```

Open `http://127.0.0.1:8765`. `studio-open.sh` never performs SSH itself. Do not publish port 8765 or add a firewall rule for it.

## First proof

The Studio's First Proof screen is an artifact view. The actual proof remains a terminal/Codex operation:

```bash
python3 -m launchpad reflect prepare
scripts/run-omegaclaw-proof.sh
```

Use the mission and workspace options required by [PROOF.md](PROOF.md). The proof uses the pinned OmegaClaw-Core runtime and `Test`; no paid provider key is needed. A missing or failed artifact must remain `pending` or `failed`.

## Template copy

The template screen includes the copy action. The equivalent CLI command is:

```bash
python3 -m launchpad studio new my-case --template community-care
```

Use a lowercase, path-safe slug. The copy is local and preserves the source template. Keep the synthetic-data disclaimer in any adapted workspace.

## Finish and local MCP

The final Wizard screen is a handoff, not an automatic agent connection. First run the real synthetic lesson proof:

```bash
scripts/run-community-care-proof.sh
```

When Studio shows the Community Hospital proof as verified, start the local bridge in a separate foreground terminal:

```bash
scripts/studio-mcp.sh
```

The bridge is STDIO and local-only. It exposes only `omega.reason` and `omega.get_receipt`; it cannot execute shell commands, call a provider, read arbitrary files, or perform an external action. Add it to Codex manually after reviewing the local project configuration. Keep tool approvals explicit and narrow.

## Stop and ask for a human decision

Stop before any request to:

- push, clone from, or modify GitHub;
- create or change an Oracle resource;
- connect to a remote host over SSH;
- configure a domain or reverse proxy;
- modify firewall or security-group rules;
- provide, store, or test an API key;
- configure MiniMax or another paid provider.

These actions are outside the P0 installation boundary and require a separate explicit human approval.

## Troubleshooting

If the doctor reports a blocker, show the report and fix the host manually. Do not bypass a blocker by marking JSON fields, changing the bind address, or substituting a saved proof. If the Studio does not start, confirm that port 8765 is free and that the command is being run from the repository root.
