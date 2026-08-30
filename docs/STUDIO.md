# Studio V2

Studio is the local, loopback-only teaching surface for OmegaClaw. It starts only after Docker preflight, the canonical example check, and the real Lighthouse proof have passed.

Run **on the user's computer or private VPS, from the repository root**:

```sh
scripts/launchpad-start.sh
```

That command runs `scripts/studio-doctor.sh`, validates `examples/lighthouse-in-the-fog/`, runs `scripts/run-lighthouse-proof.sh`, checks the evidence contract, and opens `http://127.0.0.1:8765`. The browser never receives Docker access and never creates a proof.

For a private VPS, run `scripts/launchpad-start.sh --background` in the VPS
terminal. Then run `scripts/studio-open.sh <your-vps-ssh-target>` in a terminal
on the user's computer and open the printed local URL (normally
`http://127.0.0.1:8876`). The tunnel is created on the user's computer; the
VPS remains loopback-only.

## Eight-moment story journey

The linear Wizard begins with the story, then keeps the plain-English scene on the left and the matching OmegaClaw part on the right. It uses one idea and one primary action per screen:

1. Intro — meet the boat, the fog, and the learning goal.
2. Input — reports are inputs, not truth.
3. Memory — memory survives a container restart.
4. Verify — a tool reads one identified local bulletin.
5. Reason — MeTTa and NAL/STV preserve conflict and update confidence.
6. Explain — Omega returns a reason and a receipt; a human still decides.
7. Understand — map every story event to one OmegaClaw part.
8. Play — copy one safe prompt into Codex, Claude Code, or another coding agent.

No screen contains setup commands, checkboxes, a clickable progress shortcut, or an MCP gate. Setup belongs to the terminal before the Wizard.

## What is demonstrated

The proof uses pinned OmegaClaw-Core v0.1.19, Docker, WebSocket, `Test`, a real loop, `remember`/`query` across restart, a file tool, MeTTa, NAL/STV, a response, and a hashed receipt. It is synthetic and local. It does not steer a boat, call a connector, validate outside facts, or authorize an action.

## Optional MCP

MCP is a standard plug for an agent, not the product's core. The local bridge is started **in a terminal on the same computer/VPS** with `scripts/studio-mcp.sh`. It exposes only `omega.reason` and `omega.get_receipt`, requires the verified proof, writes local receipts, and does not rerun OmegaClaw, call a provider, run shell, or perform an external action. It is optional and outside the main Wizard.

## Troubleshooting

- If preflight fails, fix the host and rerun the doctor; do not edit JSON to claim success.
- Disk checking is phase-aware: the first proof build needs more headroom than a rerun with the pinned proof image already cached.
- If the proof is pending or failed, preserve its logs and rerun the documented Docker proof.
- If the browser cannot open, use the loopback URL and confirm port `8765` is free. Never expose it publicly.
