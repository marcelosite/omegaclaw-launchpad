# Testing V2

Run unit and contract tests **on the user's computer**:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
git diff --check
```

Run the host checks and real integration proof **on the user's computer or private VPS**:

```sh
bash scripts/studio-doctor.sh
scripts/run-lighthouse-proof.sh
```

The proof is verified only when its real `omega-proof.json` satisfies the contract in [PROOF.md](PROOF.md), including receipt hash, restart memory query, tool, MeTTa, NAL/STV, response, no external actions, and human approval.

For human-centered QA, read the Wizard in order at `http://127.0.0.1:8765`: one card at a time, one primary button, no skipped steps, no setup commands inside the story, and no MCP requirement. At the final screen a reader must know the example path and the exact safe next prompt for a coding agent.

Never use a saved transcript or fixture receipt as runtime evidence. Never display or persist provider credentials.
