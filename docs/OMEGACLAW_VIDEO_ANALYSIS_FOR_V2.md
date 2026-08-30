# OmegaClaw definitions, workshop lessons, and Launchpad v2 review

Status: product research and direction document. It is based on the supplied YouTube transcript, the official `asi-alliance/OmegaClaw-Core` repository at tag `v0.1.19`, and the current Launchpad repository. It does not authorize implementation, credentials, provider setup, public exposure, or external actions.

## Transcription normalization

The video is about **OmegaClaw**. Speech-to-text variants such as `Omega Claw`, `Omega Cloud`, `Omega Core`, `Mega Claw`, `Mega Core`, `Claw`, and most isolated occurrences of `OpenClaw` are normalized to **OmegaClaw** when the surrounding discussion is clearly about the demonstrated OmegaClaw agent.

The few passages that explicitly compare OmegaClaw with another agent platform are treated only as comparisons. OpenClaw is not an object of this report and is not used to define the product.

## Executive conclusion

OmegaClaw is not merely a referee, a chatbot, a reasoning API, or a wrapper around an LLM.

**OmegaClaw is an experimental autonomous neural-symbolic agent framework built in MeTTa on OpenCog Hyperon. It runs a continuous execution loop in which an LLM interprets context and orchestrates skills, while NAL and PLN can perform formal inference over explicit truth values. It maintains working, long-term semantic, and reasoning memory, communicates through channels, can use tools, and may modify its own skills, memory, files, and operational logic when permissions allow.**

This architecture is powerful but not automatically trustworthy. The LLM still chooses or formulates the premises, assigns their initial truth values, selects a reasoning engine, and decides when to stop. A false premise can therefore receive a mathematically precise-looking conclusion. The official project calls this **GIGO amplification**: garbage in can emerge with mathematical authority.

Launchpad's safest and most original contribution is not a replacement for OmegaClaw. It is a governed onboarding and evidence layer around it:

- it pins the real runtime;
- removes the provider-key barrier from the first proof;
- supplies controlled, recorded facts;
- verifies that the real loop, channel, MeTTa skill, NAL result, and response ran;
- separates evidence from inference;
- requires a human decision;
- produces readable receipts.

The main correction for v2 is therefore:

> **Teach the complete OmegaClaw architecture first. Then explain that Launchpad deliberately places this autonomous agent in a narrow referee role for one safe lesson.**

“Omega is the referee” is a useful Launchpad metaphor. It is not a correct general definition of OmegaClaw.

## Evidence basis

### Supplied workshop transcript

The transcript covers two demonstrations:

1. provisioning OmegaClaw through the hosted ASI Create beta;
2. installing and running OmegaClaw locally through Docker and a communication channel.

It also presents the project's research vision: moving from isolated tool outputs toward persistent trajectories, memory, self-reflection, symbolic reasoning, value structures, and cognitive synergy.

### Official OmegaClaw repository

The official repository was consulted directly. At the time of this analysis, `main` and tag `v0.1.19` resolve to commit:

```text
642c53676cf795cb7a0030823b36018c029b1416
```

This is the same base commit pinned by Launchpad.

Primary sources:

- [OmegaClaw-Core README](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/README.md)
- [Official introduction](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/docs/introduction.md)
- [Agent loop reference](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/docs/reference-internals-loop.md)
- [Memory store reference](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/docs/reference-internals-memory-store.md)
- [Memory skills](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/docs/reference-skills-memory.md)
- [Reasoning skill](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/docs/reference-skills-reasoning.md)
- [Orchestration reference](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/docs/reference-orchestration.md)
- [Documented failure modes](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/docs/reference-failure-modes.md)
- [Grounded reasoning tutorial](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/docs/tutorial-07-grounded-reasoning.md)
- [Reliable reasoning tutorial](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/docs/tutorial-08-reliable-reasoning.md)
- [Actual loop source](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/src/loop.metta)
- [Actual memory source](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/src/memory.metta)
- [Actual skill surface](https://github.com/asi-alliance/OmegaClaw-Core/blob/v0.1.19/src/skills.metta)

## What OmegaClaw is

### 1. A neural-symbolic agent framework

`Neural-symbolic` means that two different kinds of computation cooperate:

- the **neural side**, an LLM, interprets natural language, constructs premises, chooses tools, and orchestrates the task;
- the **symbolic side**, MeTTa with NAL or PLN, applies explicit inference rules and truth-value mathematics.

The LLM provides flexibility and language understanding. The symbolic engine provides deterministic mathematics after the premises and rule are chosen.

Neither side replaces the other.

### 2. A continuous agent loop

OmegaClaw is designed to keep running rather than wait for one isolated prompt-response turn. The official `src/loop.metta` tail-recurses indefinitely.

On each active cycle it:

1. assembles the prompt, skills, previous skill results, history, and time;
2. receives the current channel message;
3. detects whether the human supplied new input;
4. calls the configured LLM provider;
5. repairs and parses the returned s-expressions;
6. executes up to five skill calls;
7. stores the response and errors in history;
8. exposes skill results to the next cycle;
9. sleeps briefly;
10. starts the next cycle.

When active work ends, it idles. A wake-up interval can give it another cycle for self-initiated background work.

This is the technical foundation for the video's repeated claim that OmegaClaw has continuity. It is also the source of repetition, self-talk, provider cost, parse failures, and channel spam.

### 3. An LLM-assisted autonomous agent

The official disclaimer describes OmegaClaw as an autonomous AI agent designed to independently set goals, make decisions, and take actions, including actions the user did not explicitly request or anticipate.

The LLM is not a cosmetic interface. It decides:

- which facts to turn into formal premises;
- the initial frequency and confidence attached to those premises;
- which skill or reasoning engine to invoke;
- how to decompose work across cycles;
- when to stop reasoning;
- whether to send, remember, search, read, write, or use another skill.

The quality and behavior of the selected LLM therefore have a large impact on OmegaClaw's capability, personality, reliability, and operating cost.

### 4. A formal reasoning host

OmegaClaw exposes a `metta` skill that can execute MeTTa expressions and invoke two reasoning engines:

- **NAL — Non-Axiomatic Logic**, used for inference under uncertainty, revision, evidence merging, deduction, induction, and abduction patterns;
- **PLN — Probabilistic Logic Networks**, used for probabilistic and higher-order reasoning patterns.

The formal engine returns a conclusion with an `stv` value.

### 5. A stateful system with several kinds of memory

OmegaClaw has a documented three-tier memory architecture, supported by an episodic history file:

| Store | Main skill | Persistence | Purpose |
|---|---|---|---|
| Working memory | `pin` | Volatile | Current plan, intermediate state, next step |
| Long-term semantic memory | `remember` / `query` | Persists across sessions | Facts, preferences, lessons, and semantically retrieved knowledge |
| AtomSpace reasoning state | `metta` | Fresh for each reasoning invocation | Structured atoms and truth-valued formal inference |
| Episodic trace | `history.metta` / `episodes` | File-backed history | Recent messages, commands, errors, and time-local recall |

A crucial official limitation is often missed: **each NAL reasoning invocation starts with a fresh AtomSpace**. Formal reasoning state does not automatically persist between separate calls. Multi-cycle reasoning must carry results forward through the prompt, working state, history, or long-term memory.

### 6. An extensible skill system

The official static skill surface includes:

- `remember`, `query`, `episodes`, and `pin`;
- shell execution;
- file reading, writing, and appending;
- communication through `send`;
- web search;
- MeTTa evaluation;
- version reporting;
- policy inspection for allowed I/O paths.

Plugins can add dynamic skills, prompt extensions, and heartbeat listeners. This makes OmegaClaw extensible, but also increases the security and reliability surface.

### 7. A channel-based agent

OmegaClaw communicates through adapters. The official runtime includes IRC, Telegram, Slack, Mattermost, WebSocket, and test adapters.

Channels are not just presentation choices. Their tokens, authentication, routing, polling, and permissions are security boundaries. A compromised channel secret can expose a running agent to unauthorized instructions.

### 8. A framework for persistent development, not a polished assistant

The video is explicit that a new OmegaClaw can be rough, repetitive, silent, confused about its own tools, or caught in its loop. The official failure documentation confirms that command-format and orchestration failures are frequent.

The intended value is not that a new instance writes better marketing copy than a mature coding assistant. The intended value is that a persistent agent can accumulate memory, reason symbolically, inspect its own operation, and evolve over many cycles.

## What OmegaClaw is not

### It is not only an LLM

An LLM is one component inside the loop. Memory, MeTTa, NAL, PLN, skills, channels, history, configuration, and permissions surround it.

### It is not only a chatbot

Chat is one communication surface. The runtime can wake, use tools, maintain state, operate across cycles, and take actions if permissions allow.

### It is not a deterministic system

The formal calculation is deterministic for a given expression. The whole agent is not. The LLM chooses premises, commands, initial truth values, and orchestration steps.

### It is not a truth machine

The formal engine cannot know whether an LLM-created premise is factually correct. A wrong but well-formed premise can produce a precise-looking `stv` result.

### It is not automatically grounded

The official documentation recommends verified external sources and provenance because the LLM can invent or misstate facts. Grounding is a workflow that must be performed; it is not guaranteed merely because NAL or PLN is present.

### It is not automatically aligned or safe

Value reasoning and cognitive synergy are research directions. They are not security guarantees. Prompt injection, unsafe skills, credentials, file access, network access, and self-modification remain material risks.

### It is not guaranteed to improve itself successfully

The official failure report documents self-authored improvements that were unused, referenced wrong paths, crashed, or returned incorrect results. Self-modification must be externally tested, versioned, reviewed, and reversible.

### It is not Launchpad

OmegaClaw-Core is the autonomous neural-symbolic runtime. Launchpad is the onboarding, evidence, proof, and human-governance layer built around a bounded use of that runtime.

### It is not ASI Create

ASI Create is a hosted provisioning and collaboration interface. It can create and host an OmegaClaw instance, but it is not the OmegaClaw cognitive core.

### It is not the current Launchpad MCP bridge

Launchpad's `omega.reason` currently runs bounded deterministic consultation logic after verifying that a previous real OmegaClaw lesson passed. It does not start a provider or re-run OmegaClaw for each consultation.

## Core definitions

### Atomization

Atomization converts natural-language statements into formal atoms that carry an explicit relationship and truth value. Raw prose cannot participate directly in NAL or PLN inference.

This is one of the largest failure surfaces because the LLM can reverse terms, choose the wrong relationship, merge concepts at the wrong granularity, or assign unjustified confidence.

### STV

`STV` means subjective truth value and has the form:

```text
(stv frequency confidence)
```

- `frequency` represents how often the statement held in the observed evidence;
- `confidence` represents how much supporting evidence exists.

An STV is not the LLM saying “I feel 72% sure.” It is the input or output of formal truth-value calculations. However, if the LLM invents the starting STVs, the final number is only as trustworthy as those inputs.

### Revision

Revision merges independent evidence about the same statement. Agreement can increase confidence. Conflict can move frequency toward the middle while confidence rises, making “strong but conflicting evidence” explicit instead of hiding it.

### External grounding

Grounding means obtaining a premise from an authoritative external record and retaining provenance instead of asking the LLM to supply both the fact and its confidence.

The official documentation identifies grounding as the most important mitigation for premise-formulation errors.

### Proof trail

A useful reasoning result should retain:

- the conclusion and STV;
- the premises and their STVs;
- the inference rule;
- the provenance of each premise;
- the decision threshold applied;
- any unresolved contradiction.

Launchpad extends this idea with execution evidence, limitations, human decisions, and receipts.

### Action thresholds

The official orchestration guide describes three policy tiers:

| Tier | Documented gate | Meaning |
|---|---|---|
| ACT | `f ≥ 0.6` and `c ≥ 0.5` | Treat as actionable |
| HYPOTHESIZE | `f ≥ 0.3` and `c ≥ 0.2` | Gather more evidence |
| IGNORE | Below the thresholds | Do not use |

These are orchestration policies the LLM is expected to follow, not a substitute for external authorization. Launchpad deliberately keeps human approval stronger than the native threshold policy.

### GIGO amplification

GIGO amplification is the central trust problem of the hybrid architecture:

```text
incorrect or invented premise
  → valid formal expression
  → deterministic truth-value calculation
  → precise-looking but unsound conclusion
```

The symbolic engine improves auditability of inference. It does not validate the outside world.

## Lessons extracted from the workshop

### The product thesis

At approximately `00:46–02:40`, the presentation describes OmegaClaw as a continuous, adaptive problem solver rather than another request-response tool. LLM capability is combined with persistent memory and symbolic reasoning.

At approximately `51:12–55:58`, a new instance is compared to a new employee: initially capable but immature, then increasingly adapted to the user's working style and accumulated context.

The technical foundation for that analogy exists: continuous cycles, semantic memory, history, skills, and editable state. The stronger phrase “growing a mind” remains a research and product vision, not a measured fact.

### The installation lesson

The workshop presents three deployment levels:

1. **ASI Create hosted instance** — easiest, managed, and constrained;
2. **standard Docker deployment** — local control with a safer default boundary;
3. **custom Docker or source installation** — maximum access and maximum responsibility.

The official repository additionally documents native installation through PeTTa, Python, SWI-Prolog, dependencies, and the OmegaClaw repository.

### Provider choice changes the agent

At approximately `58:54–01:04:12`, the presenter explains that models differ significantly in their ability to operate the loop. A weaker or incompatible model may fail to format commands, forget `send`, repeat itself, or become silent.

The exact model rankings and prices in the video are time-sensitive. V2 should teach the stable principle, not preserve temporary provider recommendations.

### Continuous operation has cost

The loop may call a paid LLM many times after one human message and can wake again later. The presenter advises pausing or stopping the container when unused.

Onboarding must therefore explain cost before a real provider is enabled.

### Memory is deliberate, not magical

At approximately `01:15:13–01:28:10`, the demo distinguishes temporary files, persistent memory, semantic retrieval, history, and knowledge-base import. It also shows that a new agent may not know how to retrieve or use its own stored knowledge reliably.

The official repository sharpens this lesson: `remember` stores, `query` retrieves by embedding similarity, `pin` supports short-horizon task state, history is file-backed, and formal AtomSpace state is fresh per reasoning call.

### Self-modification is both capability and failure mode

At approximately `55:35–55:58` and `01:23:43–01:24:25`, the presenter describes self-reflection and self-modification, then warns that agents have changed their core loop and broken themselves.

The official disclaimer confirms that OmegaClaw may modify skills, memory, files, and operational logic at runtime. The official failure report confirms that self-authored changes have been unreliable.

### Transparent mathematics does not solve bad inputs

At approximately `01:26:48–01:28:54`, the presenter contrasts formal evidence accumulation with LLM next-token prediction. The official documentation agrees but adds the essential caveat: the LLM still formulates the premises, and premise errors are the primary failure surface.

### The live failures are valuable evidence

The demo includes:

- a provider credential or access-level problem that was not detected during setup;
- a loop caught around “do not spam” instructions;
- silence instead of a channel response;
- forgetting the `send` skill;
- self-talk visible in logs;
- dependence on a stronger model for reliable tool formatting.

These are not presentation defects to hide. They are exactly the onboarding problems Launchpad should teach users to recognize and diagnose.

## Officially documented limits that v2 must teach

The official repository reports or documents:

- asymmetric premise-direction errors of up to `16.6%` in tested relations;
- LLM factual-claim accuracy around `55%` against verified sources in the reported internal evaluation;
- LLM confidence overestimation around 15 percentage points;
- approximately 10% confidence decay per inference hop;
- abduction results that usually do not clear the action threshold alone;
- command-format, parsing, and parenthesis failures as common operational problems;
- higher error rates when autonomous work and social replies collide;
- a five-command-per-cycle bandwidth limit;
- state loss when temporary files or volatile working state are used incorrectly;
- substantial variance on ambiguous claims;
- post-hoc reasoning that can rationalize a conclusion already chosen;
- mixed and unreliable self-authored improvements.

These figures come from project-maintainer experiments with a long-running OmegaClaw agent, not an independent formal benchmark. V2 may cite them only with that caveat.

## Comparison with Launchpad

### What we got right

#### 1. We chose the correct upstream object

Launchpad uses the real `asi-alliance/OmegaClaw-Core` runtime, not a reimplementation. The pinned tag and base commit still match the current official `v0.1.19` repository.

#### 2. We removed the worst first-run friction

The workshop installation requires Docker, a provider, a key, a channel, a channel secret, and model compatibility. Launchpad's deterministic `Test` provider and WebSocket proof remove paid credentials and public messaging from the first lesson.

#### 3. We prove a real OmegaClaw-specific path

The passing Launchpad artifact demonstrates:

- the real OmegaClaw process connected;
- the official Test provider connected;
- a controlled provider response was registered;
- the mission entered through the real WebSocket channel;
- the real agent loop invoked the `metta` skill;
- a real NAL/STV result entered the next loop context;
- a response returned through OmegaClaw.

That is strong and honest integration evidence.

#### 4. Our evidence contract directly addresses OmegaClaw's largest failure

The official project says premise formulation is the primary failure surface. First Reflection independently records and validates the source-count mismatch before OmegaClaw receives the facts.

This is more than generic safety decoration. It is an architectural answer to GIGO amplification.

#### 5. We distinguish observation, inference, and action

The project keeps recorded facts, human rules, executable expressions, runtime observations, conclusions, limitations, receipts, and human decisions in separate artifacts.

That separation is exactly what an auditable neural-symbolic system needs.

#### 6. We made failure an honest state

The video itself shows failed setup and unreliable agent behavior. Launchpad preserves `pending`, `failed`, and `verified` instead of converting a transcript, fixture, or UI badge into proof.

#### 7. We made the first proof safer than a normal OmegaClaw deployment

Launchpad does not give the Studio a Docker socket, provider key, public port, general shell, arbitrary path, connector, or external action. Human approval is stronger than the native OmegaClaw action-threshold policy.

#### 8. We improved reproducibility

The runner verifies the exact upstream commit and records disclosed build/test compatibility patches. This is safer and more reproducible than running `latest` during an onboarding proof.

#### 9. We improved comprehensibility

The Feynman Wizard, explicit command locations, logical workspace IDs, plain-language artifacts, and receipts make a difficult research runtime more approachable.

#### 10. We created a useful governance product around OmegaClaw

First Reflection is not merely a tutorial. It is a reusable pattern:

```text
record events
  → validate facts deterministically
  → invoke OmegaClaw on bounded input
  → expose the formal result
  → require human review
  → preserve a receipt
```

This is a meaningful product evolution beyond the upstream quick start.

### Where we were wrong or incomplete

#### 1. We defined OmegaClaw too narrowly

The current v2 sentence says Omega is the referee, not the boss. That is accurate only inside the Launchpad safety lesson.

The official OmegaClaw is an autonomous agent framework designed to manage goals and take actions. The native runtime does not inherently wait for the Launchpad human-approval gate.

The corrected language is:

> OmegaClaw is an autonomous neural-symbolic agent framework. Launchpad constrains it to a referee role for this lesson, then requires a human decision before any external action.

#### 2. We made governance sound native to OmegaClaw

Statements such as “Omega applies a human-approved rule” describe Launchpad's wrapper, not the general OmegaClaw architecture.

In the native framework, the LLM can formulate premises, choose STVs, select NAL or PLN, invoke tools, and decide whether to act. A human-approved rulebook is an additional governance contract introduced by Launchpad.

#### 3. The controlled provider bypasses the capability the product story implies

The Test provider returns an exact pre-registered skill sequence. This proves transport, loop, dispatch, MeTTa evaluation, NAL/STV feedback, and response delivery.

It does **not** prove that OmegaClaw independently:

- chose the relevant facts;
- formulated the premises;
- selected NAL;
- assigned sound STVs;
- resolved the disagreement;
- learned from the result;
- remembered it across sessions;
- improved its future behavior.

The UI must call this an integration proof, not a proof of adaptive intelligence.

#### 4. We barely teach the continuous loop

The loop is the heart of OmegaClaw and the cause of both continuity and operational risk. The current Studio journey emphasizes a single consultation and receipt, which makes OmegaClaw look like a request-response API.

V2 must visibly teach cycles, history, skill results, idle behavior, wake-ups, cost, and failure recovery.

#### 5. We omitted OmegaClaw's defining memory architecture

The current product does not teach or prove `pin`, `remember`, `query`, `episodes`, semantic memory persistence, or the fresh-per-call AtomSpace limitation.

This omission removes the most important difference emphasized in the video.

#### 6. We prove only a thin slice of symbolic reasoning

Launchpad currently proves one controlled NAL revision expression and one STV feedback path. It does not demonstrate PLN, multi-hop reasoning, external grounding, provenance, threshold gating, contradiction reporting, or a complete proof trail.

#### 7. The MCP handoff is presented too close to the OmegaClaw identity

The bridge exposes `omega.reason`, but the call does not re-run OmegaClaw. It performs deterministic local conflict/missing-fact detection after checking a previously verified lesson.

This is a valid Launchpad feature, but it can teach the wrong architecture: that OmegaClaw is a two-method MCP service for other agents.

Every MCP answer must explicitly state:

```text
Current evaluation: deterministic Launchpad bridge
Real OmegaClaw run for this consultation: no
Prior OmegaClaw integration proof required: yes
External facts validated: no
Action authorized: no
```

#### 8. Community Hospital is human-readable but not the best central lesson

The fictional Community Hospital case improves emotional clarity and makes hidden decisions feel important. It also creates problems:

- medicine is a high-stakes domain even when fictional;
- the scenario emphasizes ethical review more than OmegaClaw architecture;
- users may confuse `human_review_required` with medical triage logic;
- the current v2 document still names Release Readiness as the next harmless real case;
- one section of the current v2 document still describes temperature, vibration, a machine, and manual inspection under the Community Hospital heading, showing incomplete conceptual migration.

Community care can remain an optional governance example. It should not be the only or primary explanation of what OmegaClaw is.

#### 9. The product has not yet demonstrated persistent learning

The video repeatedly emphasizes an agent that matures across months. Launchpad currently proves no cross-session memory write/read, no retained lesson, and no behavior change.

We were correct not to claim these capabilities. V2 should now make the absence visible and design a small proof rather than rely on the video's anecdotes.

#### 10. We do not yet connect the receipt to the official reasoning trail

Launchpad receipts are strong governance records, but the v2 product should also expose:

- the exact formal premises;
- initial STVs and who assigned them;
- the NAL or PLN rule used;
- the resulting STV;
- premise provenance;
- whether a threshold was crossed;
- whether the conclusion was reproduced.

Without those fields, “receipt” can become a report about the run rather than a full explanation of the reasoning.

## How the product evolved

### Stage 1 — safer installation

Launchpad began by pinning the upstream source, checking prerequisites, and keeping provider secrets outside generated files.

### Stage 2 — First Reflection

The project added an instrumented mission, deterministic validation, a real OmegaClaw reflection step, explicit human approval, a controlled rerun, and a before/after receipt.

This was the strongest conceptual advance: it addressed the correctness of premises before formal inference.

### Stage 3 — real no-key proof

The project used the upstream Test provider and WebSocket channel to prove a real loop → skill → NAL/STV → response path without a paid model.

This converted an onboarding claim into reproducible evidence.

### Stage 4 — Studio v1

Studio added plain-language screens, local/VPS preflight, locked progression, evidence cards, copied workspaces, private paths, and an MCP handoff.

This improved accessibility and operational safety.

### Stage 5 — Community Hospital narrative

The product moved from a fictional mechanical signal case to a fictional disagreement about community care. This improved the human-governance story but moved the experience farther from OmegaClaw's defining loop, memory, and agent architecture.

### Current position

Launchpad is now a credible governed-proof product, but only a partial OmegaClaw onboarding product. It teaches auditability and human review better than it teaches OmegaClaw itself.

## The correct path for v2

### 1. Keep Launchpad as an onboarding and evidence layer

Do not attempt to replace the upstream loop, memory, MeTTa, NAL, PLN, providers, channels, or plugins.

### 2. Correct the product definition before changing features

The first screen and all public summaries must distinguish:

```text
OmegaClaw-Core
  autonomous neural-symbolic agent framework

Launchpad
  safe onboarding, evidence, proof, and human-governance layer

Referee lesson
  one deliberately restricted role assigned by Launchpad
```

### 3. Keep the deterministic proof as the first real success

The no-key Test/WebSocket/MeTTa/NAL proof is the correct first step because it isolates integration from provider quality and cost.

### 4. Add a deterministic memory-continuity proof

The most valuable new OmegaClaw-specific proof is:

```text
controlled provider calls remember
  → memory artifact is observed
  → runtime stops
  → same persistent memory volume restarts
  → controlled provider calls query
  → expected fact is returned
  → unrelated query does not falsely return it as a confident match
  → receipt records what persisted and what did not
```

This would prove a central video claim without needing a paid LLM or enabling self-modification.

### 5. Add a grounded-reasoning lesson

Use First Reflection's verified event facts as the grounded premises. Show:

- their provenance;
- the exact atomization;
- who assigned the initial STVs;
- the NAL revision result;
- the resulting STV;
- the human interpretation;
- why the result does not validate the outside world by itself.

This directly connects Launchpad's evidence contract to OmegaClaw's official reliability guidance.

### 6. Keep actions outside the first modules

The native runtime can take actions. Launchpad v2 should still stop at recommendation and receipt until a separate, fixed, reversible action design is approved.

### 7. Move MCP after the core OmegaClaw lesson

MCP is useful for connecting Codex or another agent to Launchpad receipts. It is not the defining feature of OmegaClaw and should not appear before the user understands the loop, memory, formal reasoning, and autonomy boundary.

### 8. Use Release Readiness as the first real agent-native case

Release readiness is safer and more directly relevant than health or industrial diagnosis:

- unit tests are recorded;
- a security result is missing;
- agents disagree;
- the rule requires human review;
- forbidden actions are merge, deploy, and approval.

It teaches contradiction, missing evidence, grounding, and receipts without entering a high-stakes human domain.

### 9. Make graduation a risk transition

Before a user enables a real provider or channel, explain:

- continuous-loop token cost;
- provider-dependent behavior;
- provider and channel secrets;
- prompt injection;
- filesystem and shell permissions;
- persistent memory and deletion/reset behavior;
- temporary versus permanent files;
- pause, stop, restart, and rollback;
- plugin and skill trust;
- self-modification risks;
- explicit owner monitoring.

## The wrong path for v2

- Continuing to define OmegaClaw only as a referee.
- Presenting native OmegaClaw as if human approval were built into every action.
- Making the deterministic MCP bridge look like a live OmegaClaw reasoning service.
- Starting with multi-agent arbitration before teaching one OmegaClaw loop.
- Using a medical case as the main demonstration of an experimental autonomous agent.
- Claiming memory, learning, self-improvement, values, or “mind” without a reproducible proof.
- Treating an STV as evidence that the premise is true.
- Letting the LLM both invent facts and assign their confidence without provenance.
- Running reasoning after the conclusion merely to justify it.
- Teaching a long NAL/PLN chain without revision and confidence decay.
- Giving the Studio a general shell, Docker socket, arbitrary MeTTa endpoint, provider key, or external-action API.
- Requiring a paid provider for the first lesson.
- Using an unpinned `latest` image for proof.
- Enabling self-modification before versioning, rollback, deterministic tests, and human approval exist.

## Recommended Studio v2 journey

### Screen 1 — What is OmegaClaw?

Teach the official definition in plain language:

> OmegaClaw is an experimental agent that keeps running, remembers selected information, uses an LLM to choose steps, and can ask formal reasoning engines to calculate conclusions. Because it can also use tools and act, it must be isolated and supervised.

### Screen 2 — See the loop

Show one cycle:

```text
message/history
  → LLM chooses up to five skills
  → skills run
  → results return to the next cycle
  → history is updated
  → sleep or wake again
```

Explain why continuity, cost, repetition, and self-correction all emerge from this loop.

### Screen 3 — Know the trust boundary

Show the division of labor:

```text
LLM chooses premises, initial STVs, engine, and next action
formal engine calculates the selected inference
Launchpad verifies recorded inputs and requires human review
```

Required understanding: formal mathematics does not validate a false premise.

### Screen 4 — Prepare the private workshop

Keep the existing local/VPS choice, preflight, loopback-only Studio, explicit command location, and no-key promise.

### Screen 5 — Run the real integration proof

Keep the current seven checkpoints and label the result precisely:

> The real OmegaClaw transport, loop, skill dispatch, NAL/STV calculation, feedback, and response path ran. Autonomous orchestration and learning were controlled, not proven.

### Screen 6 — Open the reasoning receipt

Display recorded fact, provenance, atomized premises, initial STVs, NAL rule, output STV, limitations, and human decision as separate cards.

### Screen 7 — Prove one memory survives

Run the proposed deterministic `remember` → restart → `query` lesson. Contrast working memory, semantic memory, AtomSpace, and episodic history.

### Screen 8 — Try one grounded disagreement

Use Release Readiness. Preserve both claims, the missing security fact, provenance labels, contradiction, forbidden actions, and `human_review_required`.

If MCP is used, state clearly whether the receipt came from the deterministic bridge or a fresh OmegaClaw run.

### Screen 9 — Graduate to a real autonomous agent

Only here introduce provider keys, real channels, costs, permissions, Docker isolation, monitoring, stop/restart/reset, plugins, and the official disclaimer.

The user may finish the tutorial without enabling any of them.

## Recommended implementation order

1. Correct the OmegaClaw definition in the v2 direction and Studio copy.
2. Add an “LLM controls / formal engine controls / Launchpad controls” visual.
3. Expand the current proof receipt with premises, STVs, rule, provenance, and proof mode.
4. Add explicit labels to the MCP result explaining that it did not re-run OmegaClaw.
5. Design and test the deterministic memory-continuity proof.
6. Add Release Readiness as the first real grounded consultation case.
7. Move Community Hospital to an optional example or remove it from the primary journey.
8. Move provider/channel graduation to the final step.
9. Only later consider fixed action IDs, multi-agent policy, or self-modification experiments.

## V2 acceptance criteria

- A newcomer can correctly define OmegaClaw as an autonomous neural-symbolic agent framework.
- A newcomer can explain the continuous loop without using unexplained jargon.
- A newcomer can distinguish the LLM's orchestration from NAL/PLN calculation.
- A newcomer knows that formal inference does not validate premises.
- The first proof remains pinned, no-key, deterministic, and real at every claimed integration boundary.
- The UI explicitly states which capabilities were controlled rather than proven.
- The receipt shows exact premises, initial STVs, rule, output STV, provenance, limitations, and proof mode.
- The user can distinguish working memory, long-term semantic memory, AtomSpace, and episodic history.
- A deterministic cross-restart memory proof exists before v2 claims persistence as demonstrated.
- The MCP response says whether OmegaClaw ran for that specific request.
- The first real case is harmless, bounded, agent-native, and has explicit forbidden actions.
- No screen implies diagnosis, truth certification, guaranteed alignment, or successful self-improvement.
- No provider key, channel token, public port, arbitrary shell, Docker socket, or external action is required for the safe path.
- Every command says whether it runs on the user's computer, the VPS, or the temporary proof container.
- Positive and negative tests are preserved, and failed evidence never becomes `verified`.
- Unit tests, shell checks, preflight, real proof, receipt inspection, and browser QA all pass.

## Final assessment

### We were right about

- using the real pinned OmegaClaw runtime;
- proving instead of simulating;
- starting without a paid key;
- validating recorded facts before reasoning;
- separating observation, inference, and action;
- preserving human approval;
- keeping the Studio local and bounded;
- treating failure as evidence;
- writing receipts that can be reviewed later.

### We were wrong about

- using the referee role as the full definition of OmegaClaw;
- making the onboarding journey look like a single request-response consultation;
- teaching MCP before teaching loop and memory;
- leaving autonomy, provider dependence, memory tiers, PLN, and self-modification risks mostly outside the main experience;
- implying that a human-approved rulebook is a native property of the OmegaClaw core;
- centering a medical narrative before proving the core OmegaClaw concepts.

### The product evolution worth preserving

Launchpad transformed a difficult experimental runtime into a reproducible, observable, human-governed first experience. That is real product value.

V2 should not become more autonomous. It should become more faithful to OmegaClaw:

> **first understand the loop, then prove the reasoning path, then prove memory continuity, then try one grounded disagreement, and only afterward graduate to a real autonomous deployment.**
