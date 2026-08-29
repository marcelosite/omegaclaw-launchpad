# Agent integration guide

This guide tells Codex, Claude Code, and other preferred agents how to use OmegaClaw Launchpad Studio without confusing a teaching fixture with a real-world claim.

## What the v1 product provides

```text
local preflight
  → real OmegaClaw Test/WebSocket proof
  → readable facts/rules/MeTTa/NAL/result/receipt
  → synthetic factory-fault workspace
  → explicit Finish handoff
  → bounded local MCP consultation
```

The v1 proof is integration evidence: pinned OmegaClaw-Core `v0.1.19`, a real loop, a real `metta` skill call, and an observed NAL/STV result. The provider response and factory-fault data are controlled and fictional. This is not autonomous intelligence, industrial diagnosis, causal discovery, source validation, or action authorization.

## Installation and local use

From the repository root:

```bash
scripts/studio-doctor.sh
scripts/studio-start.sh
```

Open `http://127.0.0.1:8765`. The Studio does not run Docker from the browser. Run proofs in the terminal:

```bash
python3 -m launchpad reflect prepare
scripts/run-omegaclaw-proof.sh
scripts/run-factory-fault-proof.sh
```

The factory-fault proof is safe because it uses the deterministic `Test` provider and fictional facts. It writes evidence only after the WebSocket, MeTTa, NAL/STV, and response assertions pass.

Copy a case either from the Wizard or with:

```bash
python3 -m launchpad studio new my-case --template factory-fault
```

The API and CLI expose `my-case` as a logical ID. They do not return an absolute workspace path.

## Workspace contract

```json
{
  "template": "factory-fault",
  "facts": "facts.json",
  "rules": {"human": "rules.md", "metta": "rules.metta"},
  "tests": "tests.json"
}
```

`facts.json` and `tests.json` are synthetic fixture inputs. `rules.md` is the human source of intent. `rules.metta` is an **Illustrative MeTTa lesson** and must not be described as reviewed or production-ready merely because it exists.

## MCP v1 contract

Start it locally:

```bash
scripts/studio-mcp.sh
```

The transport is JSON-RPC 2.0 over newline-delimited STDIO. Initialization and tool discovery are standard MCP messages. The only callable tools are:

### `omega.reason`

Input:

```json
{"workspace_id":"factory-fault","question":"What does this synthetic lesson conclude?"}
```

The workspace ID is `factory-fault` or a lowercase slug for an existing copied Studio workspace. The bridge requires a verified local factory-fault proof. A successful result contains:

```json
{
  "receipt_id":"mcp-0123456789abcdef0123456789abcdef",
  "workspace_id":"factory-fault",
  "answer":"manual_inspection_recommended",
  "basis":{"template":"factory-fault","provider":"Test","synthetic_only":true,"human_approval_required":true},
  "disclaimer":"This is a synthetic lesson result, not a diagnosis, causal claim, external-data validation, or action authorization."
}
```

The bridge persists the receipt before returning. It does not re-run OmegaClaw and does not infer a new conclusion from arbitrary text.

### `omega.get_receipt`

Input:

```json
{"receipt_id":"mcp-0123456789abcdef0123456789abcdef"}
```

The ID is an opaque logical ID returned by `omega.reason`. Absolute paths, traversal segments, and arbitrary filenames are rejected.

## How agents should reason with it

1. Ask for the smallest question that can be answered by the published lesson.
2. Read the returned `basis` and `disclaimer` before summarizing the answer.
3. Preserve the receipt ID in the human-facing report.
4. Separate `facts`, `rule`, `runtime_observations`, `inference`, and `human_decision` in any proposed next step.
5. Stop before external data, credentials, connectors, or actions.

For complex multi-agent systems, use Launchpad as the evidence and governance layer around an agent runtime. Have workers emit bounded observations and declarations, validate them deterministically, let OmegaClaw/MeTTa/NAL process only verified facts, and require a human decision before any change. Do not turn `omega.reason` into an unrestricted router or action tool.

## Future robust MCP direction

The next safe increments are versioned rulebook IDs, receipt redaction, replayable deterministic tests, per-workspace authorization, signed or hash-linked receipt chains, bounded timeouts, rate limits, and explicit tool approval policies. A production bridge would also need authentication, audit retention, process isolation, resource limits, and a threat model for multi-user VPS deployment. None of those are silently implied by v1.
