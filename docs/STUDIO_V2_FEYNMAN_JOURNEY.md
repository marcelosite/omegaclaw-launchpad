# Studio v2 experience direction — explain first, then prove

Status: product direction approved for documentation and discussion only. This document does not authorize implementation, provider configuration, public exposure, or external actions.

## The one-sentence mental model

**Omega is not the boss of the agents. Omega is the referee: agents bring claims and recorded facts, Omega applies a human-approved rule, and the human receives a readable receipt before deciding what happens next.**

## The Feynman rule for every screen

Every screen must be understandable by a person who has never used OmegaClaw, MeTTa, NAL, Docker, SSH, or MCP.

The screen must answer, in this order:

1. What are we trying to learn?
2. Why does it matter?
3. What will happen now?
4. Where will it happen: the user's computer or the VPS?
5. What exact command or fixed action will run?
6. What evidence proves that it worked?
7. What is still not proven?
8. What must the human do next?

Technical terms appear only after the plain-language idea. The first occurrence must include a short parenthetical definition. Example: `MCP (a standard plug that lets an agent call approved tools)`.

## Three teaching parables

### The referee

Two players disagree about whether the ball crossed the line. The referee does not invent a new camera angle and does not kick the ball. The referee receives the available observations, applies the agreed rule, and reports the decision and its basis.

In Launchpad:

- agents are the players;
- recorded facts are the camera angles;
- `rules.md` is the rule agreed by the human;
- OmegaClaw plus MeTTa/NAL is the referee's reasoning path;
- the receipt is the match report;
- the human remains the competition authority.

### The doctor, not the repair robot

A fever and a cough may justify a medical examination. They do not prove a specific disease and do not authorize surgery.

The community-care lesson uses the same distinction. A fictional high-temperature signal and a fictional high-vibration signal may derive `human_review_required`. That means “a human should inspect this fictional machine.” It does not mean “the machine is broken,” “we found the cause,” or “stop the machine.”

### The locked workshop

The Studio on a VPS is a private workshop. An SSH tunnel (a temporary encrypted corridor from the user's computer to the VPS) lets the browser visit the workshop without opening its door to the public internet.

Every command must visibly say where it runs:

- **Run on your computer**;
- **Run on the VPS**;
- **Runs inside the temporary OmegaClaw proof container**.

Never show a command without its execution location.

## Honest product stages

The product must distinguish three stages instead of presenting them as one finished capability.

### Stage A — what works today

- a no-key, real OmegaClaw `Test`/WebSocket/MeTTa/NAL proof;
- readable proof artifacts and Markdown receipts;
- a fully synthetic community-care teaching lesson;
- copied local workspaces;
- a bounded local STDIO MCP bridge with only `omega.reason` and `omega.get_receipt`;
- an MCP answer limited to the already verified teaching workspace plus a bounded local consultation packet.

The current MCP accepts structured claims from a small, bounded local packet, but it does not run a new OmegaClaw decision, validate external evidence, or authorize an action.

### Stage B — the next useful real case

Before telling users to connect all their agents, build one harmless, agent-native case: **Agent Disagreement — Release Readiness**.

Example:

- Agent A claims that a release is ready because unit tests passed.
- Agent B claims that it is not ready because a required security check is missing.
- Recorded facts say: unit tests passed; security check has no result; the agents disagree.
- The human rule says: if required evidence is missing or agents disagree on a release gate, derive `human_review_required`.
- Omega returns the recommendation and a receipt.
- Omega does not deploy, merge, approve, or reject the release.

This is a real use because it helps organize a real disagreement, while remaining safe because the output is only a review recommendation.

### Stage C — future multi-agent use

After Stage B is proven, preferred agents may use the MCP whenever a bounded policy says a disagreement requires consultation. A future robust bridge will need structured claims, evidence references, a versioned rulebook, deterministic tests, per-workspace authorization, timeouts, authentication, and receipt retention.

The future should preserve the two simple user-facing tools if possible:

- `omega.reason` — submit a bounded question with structured facts and claims, then return a receipt ID;
- `omega.get_receipt` — retrieve that receipt by logical ID.

Expanding the input contract is future work. The current v1 contract must not be described as if it already supports multi-agent disputes.

## Proposed human-first Wizard

### Screen 1 — Meet Omega

Title: **Meet your referee**

Plain-language promise:

> Your agents may disagree or make claims that are hard to audit. Omega helps them slow down: collect the recorded facts, apply a rule you approved, and leave you a receipt. Omega does not take the final action.

Required understanding before Next:

- checkbox: `I understand that Omega recommends and records; it does not act for me.`

### Screen 2 — Where is the workshop?

The user chooses or confirms:

- this computer; or
- a private VPS.

The page explains `VPS (a rented computer that stays online elsewhere)` and `SSH tunnel (a private corridor from this browser to the VPS)`.

Every command card contains:

- **Run this on:** `Your Mac` or `Your VPS`;
- **Purpose:** one sentence;
- the exact command;
- `Copy command`;
- `Ask Codex to run this`;
- an optional fixed `Run` button only when a safe action runner exists.

Next is blocked until the Studio can read a successful preflight artifact.

### Screen 3 — Is the workshop ready?

Replace raw infrastructure terminology with a checklist:

- `Repository found` — “The project files are here.”
- `Python ready` — “The small Studio server can run.”
- `Docker ready` — “The temporary OmegaClaw machine can be built.”
- `Enough memory` — “The proof is unlikely to run out of working space.”
- `Enough disk` — “The large local model and image can fit.”
- `Supported architecture` — “This machine type was recognized.”

On failure, show one sentence explaining the blocker and one next action. Never show only an error code.

Next is blocked until all required checks are ready.

### Screen 4 — Watch one real proof

Tell the story before showing the terms:

1. A controlled agent receives fictional facts.
2. The agent calls the real OmegaClaw reasoning skill.
3. Omega combines the statements according to the lesson.
4. The result returns through the real channel.
5. Launchpad saves a receipt.

Then reveal the technical labels:

- `Test provider` — a predictable actor used instead of a paid LLM;
- `WebSocket` — a two-way message connection;
- `MeTTa` — the language used to express the reasoning statement;
- `NAL` — a reasoning system that can represent evidence strength;
- `STV` — the numeric truth-strength/confidence pair returned by the reasoning step.

The community-care diagram must show every boundary:

```text
FICTIONAL OBSERVATIONS
  temperature is above the lesson threshold
  vibration is above the lesson threshold
          ↓
HUMAN-WRITTEN LESSON RULE
  if both are present, recommend a manual inspection
          ↓
REAL OMEGACLAW PATH
  Test agent → WebSocket → MeTTa skill → NAL/STV
          ↓
SAFE RESULT
  human review required
          ↓
NOT PROVEN
  no diagnosis, no cause, no validated sensor, no machine action
          ↓
RECEIPT
  what went in, what rule was used, what came out, what remains human
```

The page exposes seven human-readable checkpoints. Next is blocked until all seven are verified by the real proof artifact.

### Screen 5 — Open the evidence box

Use a parcel analogy: the result is not trustworthy because a green badge exists; it is reviewable because the parcel contains labeled items.

Show separate cards for:

- facts;
- human rule;
- executable expression used by the proof;
- runtime observations;
- conclusion;
- limitations;
- receipt.

Required understanding before Next:

- checkbox: `I understand that the data is fictional and the result is a recommendation, not a diagnosis or action.`

### Screen 6 — Create your own safe question

Do not begin with files or MeTTa. Ask six plain questions:

1. What decision do you want help reviewing?
2. What facts can be recorded without guessing?
3. What claims disagree?
4. What rule has a human already approved?
5. What safe recommendation may Omega return?
6. What must Omega never do?

The first recommended case is `Agent Disagreement — Release Readiness`. The factory lesson remains available as the mechanical teaching example.

Studio creates a workspace draft containing readable facts, rules, tests, and limitations. The user sees the logical workspace ID, never an absolute server path.

Next is blocked until the workspace exists and its positive and negative tests pass.

### Screen 7 — Connect one agent

Explain MCP with a wall-socket analogy:

> MCP is a standard socket. Codex and Claude can plug into the same approved tools without learning a different private protocol for each project.

The user selects an agent:

- Codex;
- Claude Code;
- generic MCP-compatible agent.

The page must show:

- where the configuration file lives;
- whether the MCP process runs on the user's computer or the VPS;
- the exact command the agent will start;
- the two tools the agent will receive;
- what the tools cannot do;
- a `Test connection` action;
- the returned tool list.

Next is blocked until the selected agent can list exactly `omega.reason` and `omega.get_receipt`, or the user explicitly chooses `Finish tutorial without connecting an agent`.

### Screen 8 — Teach the agent when to consult Omega

Provide a copyable policy, not an unexplained configuration fragment:

> When agents disagree about a claim that affects a human decision, stop. Preserve each claim and its evidence. Do not ask Omega to invent missing facts. Consult the approved Omega workspace, retain the receipt ID, and show the disagreement, rule, recommendation, limitations, and receipt to the human. Never execute an external action from the recommendation alone.

The current v1 MCP can ingest the bounded consultation shape for a first local test. It must still label every claim and fact as self-reported and keep the policy as a human-owned workflow, not autonomous arbitration.

### Screen 9 — Finish with a real next step

Finish is a destination, not a dead end. It shows:

- what was installed;
- what was proven;
- the workspace created;
- whether an agent is connected;
- one safe question the user can ask now;
- the receipt location expressed as a logical ID;
- what remains unavailable;
- the next recommended module.

Suggested final prompt:

> Ask your connected agent: “Explain what Omega can prove in this workspace, what it cannot prove, and create one consultation receipt without taking an action.”

## Safe command execution from the dashboard

A real `Run` button is possible, but the dashboard must never become a general shell.

The safe design is a small action runner with fixed action IDs, for example:

- `studio.preflight`;
- `proof.community_care`;
- `workspace.test`;
- `mcp.connection_test`.

For every action, the UI must show before execution:

- execution location;
- exact fixed command;
- files that may be written;
- ports and containers that may be used;
- estimated time and disk impact;
- a confirmation button.

The runner must reject arbitrary commands and arguments, use exclusive container names and checked free ports, stream readable progress, save an execution receipt, and expose a cancel operation that affects only its own process. A proof action should remain isolated from the web server and must not give the web process unrestricted Docker access.

Until that runner exists, the honest buttons are `Copy command` and `Ask Codex to run this`. A fake `Run` button must not be displayed.

## Blocking rules

Each Next button is enabled only by evidence, not by clicks alone:

| From | Required evidence |
|---|---|
| Meet Omega | Human acknowledges recommendation/action boundary |
| Location | Valid local or VPS access context selected |
| Preflight | Required checks are `ready` |
| Real proof | Seven proof checkpoints are `verified` |
| Evidence | Human acknowledges synthetic/limited claim |
| Own case | Workspace exists and tests pass |
| Connect agent | Exact MCP tool list verified, or explicit tutorial-only exit |
| Agent policy | Policy copied or acknowledged |

When blocked, the interface says exactly one missing requirement and provides the next available action.

## Language rules

- Prefer “recorded fact” over “evidence contract” on the first explanation.
- Prefer “reasoning rule” over “MeTTa expression” on the first explanation.
- Prefer “receipt” over “artifact” on the first explanation.
- Prefer “private corridor” before “SSH tunnel”.
- Prefer “standard agent plug” before “MCP”.
- Prefer “temporary OmegaClaw machine” before “Docker container”.
- Never use `pending`, `verified`, `provider`, `runtime`, `STDIO`, or `JSON-RPC` without a plain-language sentence nearby.
- Never imply that a green status proves an outside-world fact.

## Product decision: the best next implementation

Do not connect every agent to the current teaching MCP yet. The next implementation should be:

1. redesign the Wizard copy and blockers using this document;
2. make command location explicit everywhere;
3. preserve terminal/Codex execution until the fixed action runner is designed;
4. add the `Agent Disagreement — Release Readiness` workspace and deterministic tests;
5. extend the bounded reasoning contract only after that case has a real proof;
6. add guided MCP setup and a connection test for one agent at a time;
7. only then document a policy for several agents to consult Omega on disagreement.

This sequence gives the user one honest, useful success before introducing multi-agent architecture.
