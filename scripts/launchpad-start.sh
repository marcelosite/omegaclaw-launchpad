#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="foreground"

case "${1:-}" in
  "") ;;
  --background) MODE="background" ;;
  *)
    echo "Usage: scripts/launchpad-start.sh [--background]" >&2
    exit 2
    ;;
esac

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

if [[ "${MODE}" == "background" ]]; then
  RUNTIME_DIR="${PROJECT_ROOT}/.launchpad/studio"
  PID_FILE="${RUNTIME_DIR}/studio.pid"
  LOG_FILE="${RUNTIME_DIR}/studio.log"
  mkdir -p "${RUNTIME_DIR}"

  studio_healthy() {
    local status_json
    status_json="$(curl --fail --silent --max-time 2 http://127.0.0.1:8765/api/status 2>/dev/null)" || return 1
    printf '%s' "${status_json}" \
      | python3 -c 'import json, sys; d=json.load(sys.stdin); raise SystemExit(0 if all(d.get(k, {}).get("state") in {"ready", "verified"} for k in ("preflight", "lighthouse", "example", "mcp")) else 1)' 2>/dev/null
  }

  if studio_healthy; then
    echo "Studio is already responding on 127.0.0.1:8765."
  elif [[ -f "${PID_FILE}" ]] && kill -0 "$(<"${PID_FILE}")" 2>/dev/null; then
    echo "Studio is already running (pid $(<"${PID_FILE}"))."
  else
    nohup "${PROJECT_ROOT}/scripts/studio-start.sh" >"${LOG_FILE}" 2>&1 &
    echo "$!" >"${PID_FILE}"
    echo "Studio is starting in the background (pid $!)."
  fi

  ready=0
  for _ in {1..15}; do
    if curl --fail --silent --show-error --max-time 2 http://127.0.0.1:8765/api/status >/dev/null 2>&1; then
      ready=1
      break
    fi
    sleep 1
  done
  if [[ "${ready}" != "1" ]]; then
    echo "Studio did not become ready. Recent log:" >&2
    tail -40 "${LOG_FILE}" >&2 || true
    exit 1
  fi
  echo "Studio is ready and stays active after this terminal closes."
else
  echo "Opening the story-only Wizard at http://127.0.0.1:8765"
fi

if [[ -n "${SSH_CONNECTION:-}" ]]; then
  echo "This process is running on a VPS. On your own computer, run:"
  echo "  ssh -N -L 8876:127.0.0.1:8765 <your-vps-ssh-target>"
  echo "Then open: http://127.0.0.1:8876"
else
  echo "Open in this computer's browser: http://127.0.0.1:8765"
fi

if [[ "${MODE}" == "background" ]]; then
  exit 0
fi
exec "${PROJECT_ROOT}/scripts/studio-start.sh"
