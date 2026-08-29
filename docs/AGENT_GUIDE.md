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

Minimum input:

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

### Bounded general consultation

For a first real test with several agents, send a small `consultation` packet. Each agent contributes a claim; the caller records the facts and evidence labels. The bridge only detects disagreement and missing/unknown facts. It does not decide whether the rule is true, validate evidence, or execute any action.

```json
{
  "case_id": "community-clinic",
  "rule": "If agents disagree or a required fact is missing, ask a human to review.",
  "claims": [
    {"agent_id": "triage-agent", "position": "route_to_clinic", "evidence_ids": ["queue-1"]},
    {"agent_id": "records-agent", "position": "request_more_info", "evidence_ids": ["record-2"]}
  ],
  "facts": [
    {"fact_id": "patient_consent", "status": "missing", "evidence_id": "consent-unknown"}
  ],
  "forbidden_actions": ["send_message", "change_record"]
}
```

Pass that object as `consultation` alongside the required `workspace_id` and `question`. The recommendation is `human_review_required` when positions differ or any fact is `missing`/`unknown`; otherwise it is `recorded_observation`. Every call writes a logical receipt that includes the submitted claims, facts, rule, limitations, and forbidden actions.

The CLI offers the same safe path without an agent UI:

```bash
scripts/studio-mcp-check.sh
python3 -m launchpad mcp reason --workspace . --workspace-id factory-fault --question "What should a human review?" --packet-file packet.json --json
python3 -m launchpad mcp receipt --workspace . mcp-<receipt-id>
```

The check command verifies the STDIO handshake, the exact two tools, and the verified factory proof. It does not start Docker or contact the network.

### First structured disagreement test

The same `omega.reason` tool accepts one deliberately closed **Conflict Packet** (a small, named envelope for recorded disagreement). It is a teaching test for release readiness, not a general way to submit arbitrary multi-agent debates. Run it **on the computer or VPS that holds the repository**, through the locally configured MCP process:

```json
{
  "workspace_id": "factory-fault",
  "question": "What must a human review before this release?",
  "conflict_packet": {
    "case_id": "release-readiness-demo",
    "rulebook_id": "release-readiness-demo-r1",
    "claims": [
      {"agent_id": "build-agent", "position": "release_ready", "evidence_ids": ["unit-tests-2026-08-29"]},
      {"agent_id": "security-agent", "position": "release_not_ready", "evidence_ids": ["security-check-missing"]}
    ],
    "recorded_facts": [
      {"fact_id": "unit_tests", "status": "passed", "evidence_id": "unit-tests-2026-08-29"},
      {"fact_id": "required_security_check", "status": "missing", "evidence_id": "security-check-missing"}
    ],
    "forbidden_actions": ["deploy", "merge"]
  }
}
```

The returned receipt contains a **decision trace** (the recorded claims and facts, rule, detected conflict, missing information, recommendation, and prohibited actions). It returns `human_review_required`. The packet is deterministic local teaching logic: its IDs and fact vocabulary are fixed, its entries are not externally validated, it does not re-run OmegaClaw, and it cannot deploy, merge, or approve a release.

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
4. For the fixed Conflict Packet only, show the `decision_trace`, limitations, and receipt ID to the human rather than presenting it as a release decision.
5. Separate `facts`, `rule`, `runtime_observations`, `inference`, and `human_decision` in any proposed next step.
6. Stop before external data, credentials, connectors, or actions.

For complex multi-agent systems, use Launchpad as the evidence and governance layer around an agent runtime. Have workers emit bounded observations and declarations, validate them deterministically, let OmegaClaw/MeTTa/NAL process only verified facts, and require a human decision before any change. Agents do not chat through MCP: each agent submits a bounded claim, and a coordinator asks Omega for one auditable consultation. Do not turn `omega.reason` into an unrestricted router or action tool. The packets above are first teaching tests, not evidence that v1 validates real-world claims.

## Future robust MCP direction

The next safe increments are versioned rulebook IDs, receipt redaction, replayable deterministic tests, per-workspace authorization, signed or hash-linked receipt chains, bounded timeouts, rate limits, and explicit tool approval policies. A production bridge would also need authentication, audit retention, process isolation, resource limits, and a threat model for multi-user VPS deployment. None of those are silently implied by v1.
