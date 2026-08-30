#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="127.0.0.1"
PORT="8765"

if [[ "${HOST}" != "127.0.0.1" ]]; then
  echo "Refusing to start Studio outside loopback." >&2
  exit 2
fi

if [[ "${LAUNCHPAD_STUDIO_DEV:-0}" != "1" ]]; then
  PYTHONPATH="${PROJECT_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}" python3 - "${PROJECT_ROOT}" <<'PY'
import sys
from pathlib import Path
from launchpad.studio.artifacts import StudioArtifacts

status = StudioArtifacts(Path(sys.argv[1])).status()
if status["preflight"]["state"] != "ready" or status["lighthouse"]["state"] != "verified":
    raise SystemExit("Studio is not ready. Run scripts/launchpad-start.sh so setup and proof finish before the Wizard.")
PY
fi

echo "Starting OmegaClaw Launchpad Studio on http://${HOST}:${PORT}"
echo "Foreground mode: press Ctrl+C to stop."
echo "The dashboard is read-only with respect to proof execution and has no Docker socket."
echo "Setup and the Lighthouse proof must be completed before this low-level server is useful."

cd -- "${PROJECT_ROOT}"
export PYTHONPATH="${PROJECT_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 - "${PROJECT_ROOT}" <<'PY'
import sys
from pathlib import Path

from launchpad.studio import serve
from launchpad.studio_workspace import create_workspace

project_root = Path(sys.argv[1])
serve(
    project_root,
    copy_template=lambda name: create_workspace(project_root, name, "lighthouse-in-the-fog"),
)
PY
