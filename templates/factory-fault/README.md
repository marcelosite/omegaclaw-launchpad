# factory-fault

`factory-fault` is a self-contained learning fixture for OmegaClaw Launchpad Studio.

## Important limitation

Every fact, signal, threshold, asset identifier, test, and receipt in this template is synthetic. The template does not diagnose equipment, establish causality, validate external data, or trigger an action. Its only possible example conclusion is `manual_inspection_recommended`, which remains subject to human judgment.

## Files

- `facts.json` contains the synthetic facts used by the example.
- `rules.md` is the human-readable illustrative learning rule.
- `rules.metta` is an illustrative MeTTa lesson scaffold. Studio P0 does not execute it in the real OmegaClaw runtime.
- `tests.json` includes one positive and one negative fixture case.
- `example-receipt.md` is clearly marked as a fixture, not a runtime proof.
- `workspace.json` identifies the fixed local files in this workspace.

Copy this template with:

```bash
python3 -m launchpad studio new my-case --template factory-fault
```

Then ask Codex to help adapt facts, rules, and tests while preserving the disclaimer and human review boundaries.
