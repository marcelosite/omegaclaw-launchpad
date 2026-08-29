#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PROOF_MODE="first-reflection"
if [[ "${1:-}" == "--community-care" ]]; then
  PROOF_MODE="community-care"
  shift
fi
MISSION_ID="${1:-source-audit-demo-001}"
MISSION_ROOT="${PROJECT_ROOT}/.launchpad/first-reflection/${MISSION_ID}"
COMMUNITY_RUN_ROOT="${PROJECT_ROOT}/.launchpad/studio/runs/community-care"
UPSTREAM_DIR="${PROJECT_ROOT}/.launchpad/omegaclaw-core-v0.1.19"
UPSTREAM_REF="v0.1.19"
UPSTREAM_COMMIT="642c53676cf795cb7a0030823b36018c029b1416"
PROOF_IMAGE="omegaclaw-launchpad-proof:v0.1.19"
WS_TOKEN="launchpad-local-proof-token"
CONTAINER_NAME="launchpad-omegaclaw-proof"
MEMORY_VOLUME="launchpad-omegaclaw-memory"

if ! command -v docker >/dev/null 2>&1 && \
  [[ -x "/Applications/Docker.app/Contents/Resources/bin/docker" ]]; then
  export PATH="/Applications/Docker.app/Contents/Resources/bin:${PATH}"
fi

if [[ "${PROOF_MODE}" == "first-reflection" ]]; then
  if [[ ! -f "${MISSION_ROOT}/03-reflection/reflection-context.json" ]]; then
    echo "Prepare the mission first: python3 -m launchpad reflect prepare" >&2
    exit 2
  fi
else
  for required in README.md facts.json rules.md rules.metta tests.json; do
    if [[ ! -f "${PROJECT_ROOT}/templates/community-care/${required}" ]]; then
      echo "Missing Community Hospital template file: ${required}" >&2
      exit 2
    fi
  done
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

if docker ps -a --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"; then
  echo "Refusing to touch existing Docker container: ${CONTAINER_NAME}" >&2
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

if git -C "${UPSTREAM_DIR}" apply --check \
  "${PROJECT_ROOT}/integrations/omegaclaw/isolated-container.patch" >/dev/null 2>&1; then
  git -C "${UPSTREAM_DIR}" apply \
    "${PROJECT_ROOT}/integrations/omegaclaw/isolated-container.patch"
fi

if ! git -C "${UPSTREAM_DIR}" diff --quiet -- scripts/omegaclaw; then
  EXPECTED_LAUNCHER_DIFF="$(git -C "${UPSTREAM_DIR}" diff -- scripts/omegaclaw)"
  if [[ "${EXPECTED_LAUNCHER_DIFF}" != *"LAUNCHPAD_CONTAINER_NAME"* || \
    "${EXPECTED_LAUNCHER_DIFF}" != *"LAUNCHPAD_MEMORY_VOLUME"* ]]; then
    echo "Refusing unexpected upstream launcher changes." >&2
    exit 2
  fi
fi

# Older proof checkouts may already contain the container-name patch but not
# the Linux host-network additions. Apply that incremental patch independently
# so retries remain safe and idempotent.
if ! grep -q -- 'LAUNCHPAD_NETWORK_MODE' "${UPSTREAM_DIR}/scripts/omegaclaw" || \
  ! grep -q -- 'LAUNCHPAD_SKIP_NGINX' "${UPSTREAM_DIR}/entrypoint.sh"; then
  (cd "${UPSTREAM_DIR}" && patch -p1 --forward --batch -r - \
    < "${PROJECT_ROOT}/integrations/omegaclaw/linux-host-network.patch") || true
fi

if ! grep -q -- 'LAUNCHPAD_NETWORK_MODE' "${UPSTREAM_DIR}/scripts/omegaclaw" || \
  ! grep -q -- 'LAUNCHPAD_SKIP_NGINX' "${UPSTREAM_DIR}/entrypoint.sh"; then
  echo "Refusing proof checkout without isolated Linux network patch." >&2
  exit 2
fi

# Oracle ARM hosts may expose Docker's legacy builder, which does not support
# COPY --chmod/--chown. Apply the equivalent explicit RUN steps only to this
# isolated proof checkout so the upstream source remains untouched elsewhere.
if grep -q -- '--chmod=' "${UPSTREAM_DIR}/Dockerfile" || \
  grep -q -- '<<PY' "${UPSTREAM_DIR}/Dockerfile"; then
  (cd "${UPSTREAM_DIR}" && patch -p1 --forward --batch \
    -r - < "${PROJECT_ROOT}/integrations/omegaclaw/legacy-builder.patch") || true
fi

if grep -q -- '--chmod=' "${UPSTREAM_DIR}/Dockerfile" || \
  grep -q -- '<<PY' "${UPSTREAM_DIR}/Dockerfile"; then
  echo "Refusing unsupported Dockerfile features in proof checkout." >&2
  exit 2
fi

DOCKER_BUILD_ARGS=(-t "${PROOF_IMAGE}")
if docker build --help 2>/dev/null | grep -q -- '--progress'; then
  DOCKER_BUILD_ARGS=(--progress=plain "${DOCKER_BUILD_ARGS[@]}")
fi
docker build "${DOCKER_BUILD_ARGS[@]}" "${UPSTREAM_DIR}"

if [[ "${PROOF_MODE}" == "first-reflection" ]]; then
  TEST_SOURCE="${PROJECT_ROOT}/integrations/omegaclaw/test_launchpad_first_reflection_ws_mock.py"
  TEST_TARGET="${UPSTREAM_DIR}/Autotests/mock_websocket/test_launchpad_first_reflection_ws_mock.py"
else
  TEST_SOURCE="${PROJECT_ROOT}/integrations/omegaclaw/test_launchpad_community_care_ws_mock.py"
  TEST_TARGET="${UPSTREAM_DIR}/Autotests/mock_websocket/test_launchpad_community_care_ws_mock.py"
fi
cp "${TEST_SOURCE}" "${TEST_TARGET}"

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
  Darwin)
    HOST_FROM_CONTAINER="host.docker.internal"
    NETWORK_MODE="bridge"
    SKIP_NGINX="0"
    ;;
  Linux)
    # Oracle's Docker bridge blocks container-to-host traffic. Host networking
    # keeps the proof harness reachable without publishing or claiming a port;
    # nginx is skipped so the container cannot contend with host port 8080.
    HOST_FROM_CONTAINER="127.0.0.1"
    NETWORK_MODE="host"
    SKIP_NGINX="1"
    ;;
  *) echo "Unsupported host for the proof runner: $(uname -s)" >&2; exit 2 ;;
esac

cleanup() {
  LAUNCHPAD_CONTAINER_NAME="${CONTAINER_NAME}" \
  LAUNCHPAD_MEMORY_VOLUME="${MEMORY_VOLUME}" \
    "${UPSTREAM_DIR}/scripts/omegaclaw" clean >/dev/null 2>&1 || true
}
trap cleanup EXIT

env \
  WS_URL="ws://${HOST_FROM_CONTAINER}:8770" \
  WS_TOKEN="${WS_TOKEN}" \
  TEST_SERVER_IP="${HOST_FROM_CONTAINER}" \
  LAUNCHPAD_CONTAINER_NAME="${CONTAINER_NAME}" \
  LAUNCHPAD_MEMORY_VOLUME="${MEMORY_VOLUME}" \
  LAUNCHPAD_NETWORK_MODE="${NETWORK_MODE}" \
  LAUNCHPAD_SKIP_NGINX="${SKIP_NGINX}" \
  "${UPSTREAM_DIR}/scripts/omegaclaw" start \
    -s 0000 -p Test -t websocket -d "${PROOF_IMAGE}"

if [[ ! -x "${UPSTREAM_DIR}/Autotests/venv/bin/python" ]]; then
  "${PYTHON_BIN}" -m venv "${UPSTREAM_DIR}/Autotests/venv"
fi
"${UPSTREAM_DIR}/Autotests/venv/bin/pip" install pytest websockets pyyaml

env \
  OMEGACLAW_CONTAINER="${CONTAINER_NAME}" \
  WS_MOCK_PORT=8770 \
  WS_TOKEN="${WS_TOKEN}" \
  LAUNCHPAD_MISSION_ROOT="${MISSION_ROOT}" \
  LAUNCHPAD_STUDIO_RUN_ROOT="${COMMUNITY_RUN_ROOT}" \
  "${UPSTREAM_DIR}/Autotests/venv/bin/pytest" -s -v \
    "${TEST_TARGET}"

if [[ "${PROOF_MODE}" == "first-reflection" ]]; then
  echo "Real OmegaClaw proof captured at ${MISSION_ROOT}/03-reflection/omega-proof.json"
else
  echo "Real OmegaClaw Community Hospital proof captured at ${COMMUNITY_RUN_ROOT}/omega-proof.json"
fi
