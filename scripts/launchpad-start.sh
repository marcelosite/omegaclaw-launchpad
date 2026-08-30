#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

echo "OmegaClaw Launchpad V2"
echo "Step 1/3: check this computer or VPS."
"${PROJECT_ROOT}/scripts/studio-doctor.sh"
PYTHONPATH="${PROJECT_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}" python3 -m launchpad example check lighthouse-in-the-fog --workspace "${PROJECT_ROOT}"

echo "Step 2/3: run the pinned real OmegaClaw Lighthouse proof in Docker."
"${PROJECT_ROOT}/scripts/run-lighthouse-proof.sh"

echo "Step 3/3: validate the saved proof before opening the Wizard."
PYTHONPATH="${PROJECT_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}" python3 - "${PROJECT_ROOT}" <<'PY'
import sys
from pathlib import Path
from launchpad.studio.artifacts import StudioArtifacts

status = StudioArtifacts(Path(sys.argv[1])).status()
if status["preflight"]["state"] != "ready":
    raise SystemExit("BLOCKED: setup report is not ready. Run scripts/studio-doctor.sh and fix its one failing check.")
if status["lighthouse"]["state"] != "verified":
    raise SystemExit("BLOCKED: Lighthouse proof is not verified. Inspect .launchpad/studio/runs/lighthouse-in-the-fog/.")
if status["example"]["state"] != "ready":
    raise SystemExit("BLOCKED: canonical Lighthouse example is incomplete. Restore examples/lighthouse-in-the-fog/.")
print("Verified: setup, real OmegaClaw proof, and canonical example.")
PY

echo "Opening the story-only Wizard at http://127.0.0.1:8765"
exec "${PROJECT_ROOT}/scripts/studio-start.sh"
