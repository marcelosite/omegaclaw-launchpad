#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
MISSION_ID="${1:-source-audit-demo-001}"
MISSION_ROOT="${PROJECT_ROOT}/.launchpad/first-reflection/${MISSION_ID}"
UPSTREAM_DIR="${PROJECT_ROOT}/.launchpad/omegaclaw-core-v0.1.19"
UPSTREAM_REF="v0.1.19"
UPSTREAM_COMMIT="642c53676cf795cb7a0030823b36018c029b1416"
PROOF_IMAGE="omegaclaw-launchpad-proof:v0.1.19"
WS_TOKEN="launchpad-local-proof-token"

if ! command -v docker >/dev/null 2>&1 && \
  [[ -x "/Applications/Docker.app/Contents/Resources/bin/docker" ]]; then
  export PATH="/Applications/Docker.app/Contents/Resources/bin:${PATH}"
fi

if [[ ! -f "${MISSION_ROOT}/03-reflection/reflection-context.json" ]]; then
  echo "Prepare the mission first: python3 -m launchpad reflect prepare" >&2
  exit 2
fi

for command in git docker; do
  if ! command -v "${command}" >/dev/null 2>&1; then
    echo "Missing prerequisite: ${command}" >&2
    exit 2
  fi
done

PYTHON_BIN=""
for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "${candidate}" >/dev/null 2>&1 && \
    "${candidate}" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
    PYTHON_BIN="$(command -v "${candidate}")"
    break
  fi
done
if [[ -z "${PYTHON_BIN}" ]]; then
  echo "OmegaClaw proof requires Python 3.10+." >&2
  exit 2
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but its engine is not running." >&2
  exit 2
fi

if [[ ! -d "${UPSTREAM_DIR}/.git" ]]; then
  git clone --depth 1 --branch "${UPSTREAM_REF}" \
    https://github.com/asi-alliance/OmegaClaw-Core.git "${UPSTREAM_DIR}"
fi

ACTUAL_COMMIT="$(git -C "${UPSTREAM_DIR}" rev-parse HEAD)"
if [[ "${ACTUAL_COMMIT}" != "${UPSTREAM_COMMIT}" ]]; then
  echo "Refusing to run an unverified upstream commit: ${ACTUAL_COMMIT}" >&2
  exit 2
fi

if git -C "${UPSTREAM_DIR}" apply --check \
  "${PROJECT_ROOT}/integrations/omegaclaw/low-memory-build.patch" >/dev/null 2>&1; then
  git -C "${UPSTREAM_DIR}" apply \
    "${PROJECT_ROOT}/integrations/omegaclaw/low-memory-build.patch"
fi

if ! git -C "${UPSTREAM_DIR}" diff --quiet -- Dockerfile; then
  EXPECTED_DIFF="$(git -C "${UPSTREAM_DIR}" diff -- Dockerfile)"
  if [[ "${EXPECTED_DIFF}" != *"--parallel 2"* ]]; then
    echo "Refusing unexpected upstream Dockerfile changes." >&2
    exit 2
  fi
fi

docker build --progress=plain -t "${PROOF_IMAGE}" "${UPSTREAM_DIR}"

cp "${PROJECT_ROOT}/integrations/omegaclaw/test_launchpad_first_reflection_ws_mock.py" \
  "${UPSTREAM_DIR}/Autotests/mock_websocket/test_launchpad_first_reflection_ws_mock.py"

if git -C "${UPSTREAM_DIR}" apply --check \
  "${PROJECT_ROOT}/integrations/omegaclaw/macos-test-harness.patch" >/dev/null 2>&1; then
  git -C "${UPSTREAM_DIR}" apply \
    "${PROJECT_ROOT}/integrations/omegaclaw/macos-test-harness.patch"
fi

if ! git -C "${UPSTREAM_DIR}" diff --quiet -- Autotests/mock/rpc.py; then
  EXPECTED_RPC_DIFF="$(git -C "${UPSTREAM_DIR}" diff -- Autotests/mock/rpc.py)"
  if [[ "${EXPECTED_RPC_DIFF}" != *"POLLRDHUP is Linux-specific"* ]]; then
    echo "Refusing unexpected upstream test-harness changes." >&2
    exit 2
  fi
fi

case "$(uname -s)" in
  Darwin) HOST_FROM_CONTAINER="host.docker.internal" ;;
  Linux) HOST_FROM_CONTAINER="172.17.0.1" ;;
  *) echo "Unsupported host for the proof runner: $(uname -s)" >&2; exit 2 ;;
esac

cleanup() {
  "${UPSTREAM_DIR}/scripts/omegaclaw" clean >/dev/null 2>&1 || true
}
trap cleanup EXIT

env \
  WS_URL="ws://${HOST_FROM_CONTAINER}:8770" \
  WS_TOKEN="${WS_TOKEN}" \
  TEST_SERVER_IP="${HOST_FROM_CONTAINER}" \
  "${UPSTREAM_DIR}/scripts/omegaclaw" start \
    -s 0000 -p Test -t websocket -d "${PROOF_IMAGE}"

if [[ ! -x "${UPSTREAM_DIR}/Autotests/venv/bin/python" ]]; then
  "${PYTHON_BIN}" -m venv "${UPSTREAM_DIR}/Autotests/venv"
fi
"${UPSTREAM_DIR}/Autotests/venv/bin/pip" install pytest websockets pyyaml

env \
  OMEGACLAW_CONTAINER=omegaclaw \
  WS_MOCK_PORT=8770 \
  WS_TOKEN="${WS_TOKEN}" \
  LAUNCHPAD_MISSION_ROOT="${MISSION_ROOT}" \
  "${UPSTREAM_DIR}/Autotests/venv/bin/pytest" -s -v \
    "${UPSTREAM_DIR}/Autotests/mock_websocket/test_launchpad_first_reflection_ws_mock.py"

echo "Real OmegaClaw proof captured at ${MISSION_ROOT}/03-reflection/omega-proof.json"
