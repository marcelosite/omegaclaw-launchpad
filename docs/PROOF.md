# Real OmegaClaw proof

The acceptance proof is Docker-only and uses the pinned OmegaClaw-Core v0.1.19 base commit (`642c53676cf795cb7a0030823b36018c029b1416`) with the deterministic `Test` provider and WebSocket channel.

Run **on the user's computer or private VPS, from this repository root**:

```sh
scripts/run-lighthouse-proof.sh
```

The temporary proof container runs the actual OmegaClaw loop and records these checkpoints:

1. WebSocket connection and loop.
2. `remember` and `pin` a marker.
3. Docker restart, then `query` the marker from persisted memory.
4. Read the identified local harbor bulletin through the file tool.
5. Execute illustrative MeTTa reasoning with NAL/STV evidence, including a conflicting and a revised expression.
6. Observe a response and write a receipt.

Only after all assertions pass does the runner write `.launchpad/studio/runs/lighthouse-in-the-fog/omega-proof.json` with `status: verified`. The adjacent `receipt.md` is hashed into that JSON. `external_actions` must remain an empty list and `human_approval_still_required` must remain true.

This is real runtime integration evidence, but the data and provider are synthetic. It does not validate outside sources, diagnose a machine, steer a boat, call connectors, or authorize an action. A fixture receipt in the example folder is never treated as runtime evidence.

For the complete human-readable lesson, see [THE_LIGHTHOUSE_IN_THE_FOG.md](THE_LIGHTHOUSE_IN_THE_FOG.md) and [the example](../examples/lighthouse-in-the-fog/README.md).
