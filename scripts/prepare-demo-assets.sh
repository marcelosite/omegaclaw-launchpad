#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
MISSION_ID="${1:-video-demo-001}"
MISSION_ROOT="${PROJECT_ROOT}/.launchpad/first-reflection/${MISSION_ID}"

cd "${PROJECT_ROOT}"

if [[ -e "${MISSION_ROOT}" ]]; then
  echo "Mission already exists: ${MISSION_ROOT}" >&2
  echo "Use a new identifier, for example: scripts/prepare-demo-assets.sh video-demo-002" >&2
  exit 2
fi

python3 -m launchpad reflect init --mission-id "${MISSION_ID}"
python3 -m launchpad reflect run --mission-id "${MISSION_ID}"
python3 -m launchpad reflect validate --mission-id "${MISSION_ID}"
python3 -m launchpad reflect prepare --mission-id "${MISSION_ID}"

echo
echo "Demo assets are ready: ${MISSION_ROOT}"
echo
echo "Open these files for inspection or recording:"
echo "  Mission:    ${MISSION_ROOT}/00-mission/mission.md"
echo "  Events:     ${MISSION_ROOT}/01-run-1/events.jsonl"
echo "  Validation: ${MISSION_ROOT}/02-validation/validation.md"
echo "  Context:    ${MISSION_ROOT}/03-reflection/reflection-context.json"
echo
echo "Next steps:"
echo "  python3 -m launchpad reflect prove --mission-id ${MISSION_ID}"
echo "  scripts/run-omegaclaw-proof.sh ${MISSION_ID}"
echo "  python3 -m launchpad reflect review --mission-id ${MISSION_ID}"
echo "  python3 -m launchpad reflect rerun --mission-id ${MISSION_ID}"
echo "  python3 -m launchpad reflect receipt --mission-id ${MISSION_ID}"
