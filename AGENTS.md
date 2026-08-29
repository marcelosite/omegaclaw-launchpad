# Agent operating guide

This repository is an onboarding and evidence layer for OmegaClaw. It is not an autonomous action platform.

## Default workflow

1. Read `README.md`, `docs/STUDIO.md`, `docs/STUDIO_ARCHITECTURE.md`, `docs/PROOF.md`, `docs/STUDIO_V1_STATE.md`, and `docs/STUDIO_V2_FEYNMAN_JOURNEY.md` before changing the Studio.
2. Treat `docs/STUDIO_V1_STATE.md` as the continuity snapshot and `docs/STUDIO_V2_FEYNMAN_JOURNEY.md` as the approved direction for the next user experience. Where older P0 interface copy conflicts with the newer experience direction, stop and surface the conflict before implementation.
3. Run `scripts/studio-doctor.sh` before a local proof. Show blockers instead of bypassing them.
4. Use the deterministic `Test` provider for the first proof. Never request or store an LLM key for this path.
5. Run `scripts/run-factory-fault-proof.sh` for the synthetic factory-fault lesson. A lesson is verified only when its real `omega-proof.json` passes the evidence contract.
6. Keep facts, human rules, executable lesson scaffolds, runtime evidence, and receipts as separate files.
7. Preserve human approval. Do not execute an action because a lesson concludes `manual_inspection_recommended`.

## Experience language

- Explain the plain-language idea before introducing a technical term.
- Define the first use of each technical term in parentheses.
- Every command shown to a user must say where it runs: the user's computer, the VPS, or the temporary proof container.
- Describe Omega as a referee that applies a human-approved rule to recorded facts and produces a receipt. Do not describe it as the boss of agents or an autonomous action authority.
- Do not claim the current MCP supports arbitrary multi-agent disputes. That is a future bounded extension.

## Local files and formats

- First Reflection mission: `.launchpad/first-reflection/<mission-id>/`.
- Studio preflight: `.launchpad/studio/preflight.json`.
- Copied workspaces: `.launchpad/studio/workspaces/<lowercase-slug>/`.
- Real factory-fault proof: `.launchpad/studio/runs/factory-fault/omega-proof.json` and `receipt.md`.
- MCP receipts: `.launchpad/studio/runs/mcp/mcp-<32-hex>.json`.
- Browser artifact names are logical allowlisted IDs; never add an arbitrary path endpoint.

The `factory-fault` template contains fictional facts, a human-readable `rules.md`, an **Illustrative MeTTa lesson** in `rules.metta`, positive/negative `tests.json`, and a fixture receipt. The fixture is not runtime evidence.

## MCP v1

Start the local bridge with `scripts/studio-mcp.sh`. It is newline-delimited JSON-RPC over STDIO and exposes exactly two tools:

- `omega.reason({"workspace_id":"factory-fault","question":"..."})` consults the verified synthetic lesson and writes a receipt before returning.
- `omega.get_receipt({"receipt_id":"mcp-<32-hex>"})` returns one receipt created by the first tool.

The bridge does not run a provider, call OmegaClaw again, execute shell commands, read arbitrary files, invoke connectors, or authorize an external action. A useful response always carries `synthetic_only: true` and `human_approval_required: true`.

Use the MCP bridge as an audit-friendly consultation surface, not as a general agent executor. If a requested task needs external data, credentials, a connector, a channel, or a machine action, stop and ask the human for a separate design and approval.

## Agent boundaries

Codex, Claude Code, or another agent may inspect and propose edits to a copied workspace. They should preserve the disclaimer, run the positive and negative tests, and produce a receipt or diff for human review. They must not silently rewrite a failed proof as verified.

Do not access GitHub, Oracle, remote SSH, domains, firewalls, or MiniMax while working locally unless the human explicitly authorizes that separate operation. Do not expose port `8765`; Studio is loopback-only.

## Safe expansion direction

Future work can add versioned rulebooks, structured fact editing, receipt redaction, adapter contracts for other agent runtimes, and a stronger MCP service with authentication and policy enforcement. Those changes must retain immutable evidence, explicit human approval, least privilege, and a clear distinction between observation, inference, and action.
