# Coding-agent guide

This repository is an onboarding and evidence layer for OmegaClaw. It is not an autonomous action platform.

## First run

Run **on the user's computer or private VPS, from the repository root**:

```sh
scripts/launchpad-start.sh
```

The script checks Docker, validates the example, runs the pinned real proof, and starts Studio only after the proof is verified. A coding agent must not skip a failed check or rewrite a proof artifact.

## The one example

Read `examples/lighthouse-in-the-fog/AGENTS.md` (or `CLAUDE.md`) before editing. The directory is the canonical, synthetic lesson and contains:

- `claims.json` — reports with provenance;
- `facts.json` and `verified-update.json` — recorded facts and one identified update;
- `rules.md` — the human rule in plain language;
- `reasoning.metta` — illustrative MeTTa/NAL expressions;
- `tests.json` — conflict, verified update, missing beacon, and GIGO (garbage in, garbage out) cases;
- `example-receipt.md` — a clearly labelled fixture, not runtime evidence.

Validate it **on the user's computer/VPS**:

```sh
PYTHONPATH=src python3 -m launchpad example check lighthouse-in-the-fog
PYTHONPATH=src python3 -m launchpad example copy my-case
```

Copying creates `.launchpad/studio/workspaces/my-case/` and never overwrites an existing workspace. Keep claims, facts, human rules, executable lesson scaffolds, runtime evidence, and receipts as separate files.

## Safe agent task

Ask Codex or Claude Code to explain the story, run the example check, inspect the tests, and propose one small change. It may edit a copied workspace, but must preserve provenance, `human_approval_required`, and `external_actions: []`. It must never add credentials, call a connector, steer a vehicle, or silently convert a fixture into proof.

## MCP (optional)

MCP is a standard plug that lets an agent call approved tools. It is not required for the Wizard or the Docker proof. Start **in a terminal on the same computer/VPS** only after the proof is verified:

```sh
scripts/studio-mcp.sh
```

The bridge exposes exactly two tools:

- `omega.reason` — consults the verified Lighthouse evidence through a deterministic local evaluator and writes a receipt;
- `omega.get_receipt` — reads one receipt returned by the first tool.

The bridge does not rerun OmegaClaw, start a provider, execute shell commands, read arbitrary paths, validate external facts, or authorize an action. It labels its consultation `synthetic_only: true` and `human_approval_required: true`. Its inputs are self-reported; conflicts or missing facts produce `human_review_required`.

Registering the bridge with an agent is a separate, manual decision. Do not describe this v1 bridge as arbitrary multi-agent arbitration or as an agent router.

## Provider keys

The Test proof needs no key. Never place a MiniMax or ASI key in Git, examples, receipts, `.env` committed to the project, or chat. Direct MiniMax uses upstream `OpenAIAPI`/`OPENAIAPI_API_KEY`; ASI Cloud uses `ASICloud`/`ASI_API_KEY`. See [PROVIDERS.md](PROVIDERS.md).
