# Studio V2 architecture

Studio is an evidence reader and explainer, not an execution control plane.

```text
terminal (user computer/VPS)
  └─ launchpad-start.sh
      ├─ studio-doctor.sh
      ├─ example check
      └─ run-lighthouse-proof.sh ── Docker ── pinned OmegaClaw-Core
                                      └─ omega-proof.json + receipt.md
browser ── loopback 127.0.0.1:8765 ── reads allowlisted artifacts only
optional agent ── STDIO MCP ── local deterministic consultation + receipt
```

The server has no Docker socket, shell endpoint, connector endpoint, arbitrary path endpoint, or external-action endpoint. It binds only to `127.0.0.1`.

## Evidence layout

```text
examples/lighthouse-in-the-fog/        # immutable teaching example
.launchpad/studio/preflight.json       # host checks
.launchpad/studio/runs/lighthouse-in-the-fog/
  omega-proof.json                     # real runtime evidence
  receipt.md                            # human-readable receipt
.launchpad/studio/runs/mcp/             # optional bridge receipts
```

The artifact reader uses logical IDs and a fixed allowlist. The two presentation-style Lighthouse images are also served through exact, non-parameterized allowlisted routes. The server rejects traversal, symlinks, malformed JSON, and oversized files. Proof state is derived from the complete evidence contract and receipt hash; the UI cannot manufacture `verified`.

## Safety boundary

OmegaClaw is the real neural-symbolic runtime under test. The Lighthouse scenario constrains the lesson: facts are synthetic, the rule is human-readable, the reasoning lesson is illustrative MeTTa, and every outcome keeps `human_approval_required: true` and `external_actions: []`. The result is evidence of an integration path, not a claim that every OmegaClaw capability or production autonomy is safe.

The optional MCP bridge is deliberately not a fresh OmegaClaw executor. It requires a prior verified proof, accepts only bounded local inputs, records self-reported claims and missing facts, and returns a receipt without validating the outside world or authorizing an action.
