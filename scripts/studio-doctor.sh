#!/usr/bin/env bash
set -euo pipefail
umask 077

# Read-only Studio preflight. The only persistent output is preflight.json.
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACT_DIR="${PROJECT_ROOT}/.launchpad/studio"
ARTIFACT_PATH="${ARTIFACT_DIR}/preflight.json"
mkdir -p -- "${ARTIFACT_DIR}"

PYTHON_WRITER=""
for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "${candidate}" >/dev/null 2>&1; then
    PYTHON_WRITER="$(command -v "${candidate}")"
    break
  fi
done
if [[ -z "${PYTHON_WRITER}" ]]; then
  echo "[BLOCKED] python: no Python 3 interpreter is available; Studio requires Python 3.10 or newer." >&2
  exit 1
fi

repo_version="unknown"
repo_commit="unknown"
if command -v git >/dev/null 2>&1 && git -C "${PROJECT_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  repo_version="$(git -C "${PROJECT_ROOT}" describe --tags --always --dirty 2>/dev/null || true)"
  repo_commit="$(git -C "${PROJECT_ROOT}" rev-parse HEAD 2>/dev/null || true)"
fi

upstream_repository="https://github.com/asi-alliance/OmegaClaw-Core.git"
upstream_ref="v0.1.19"
upstream_commit="642c53676cf795cb7a0030823b36018c029b1416"

python_version="unavailable"
python_command="unavailable"
python_ok=false
for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "${candidate}" >/dev/null 2>&1 && \
    "${candidate}" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
    python_command="$(command -v "${candidate}")"
    python_version="$("${candidate}" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')"
    python_ok=true
    break
  fi
done
if [[ "${python_ok}" != true ]]; then
  python_command="${PYTHON_WRITER}"
  python_version="$("${PYTHON_WRITER}" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null || true)"
fi

docker_client_version="unavailable"
docker_server_version="unavailable"
docker_ok=false
if command -v docker >/dev/null 2>&1; then
  docker_client_version="$(docker --version 2>/dev/null || true)"
  docker_server_version="$(docker info --format '{{.ServerVersion}}' 2>/dev/null || true)"
  docker_client_version="${docker_client_version:-unavailable}"
  docker_server_version="${docker_server_version:-unavailable}"
  [[ "${docker_server_version}" != "unavailable" ]] && docker_ok=true
fi

architecture="$(uname -m 2>/dev/null || printf 'unknown')"
case "${architecture}" in
  arm64|aarch64) architecture_family="arm64"; architecture_ok=true ;;
  x86_64|amd64) architecture_family="amd64"; architecture_ok=true ;;
  *) architecture_family="unknown"; architecture_ok=false ;;
esac

memory_bytes=0
if [[ "$(uname -s 2>/dev/null || true)" == "Darwin" ]]; then
  memory_bytes="$(sysctl -n hw.memsize 2>/dev/null || printf '0')"
elif [[ -r /proc/meminfo ]]; then
  memory_bytes="$(awk '/^MemTotal:/ { print $2 * 1024; exit }' /proc/meminfo 2>/dev/null || printf '0')"
fi
[[ "${memory_bytes}" =~ ^[0-9]+$ ]] || memory_bytes=0

disk_bytes="$(df -Pk "${PROJECT_ROOT}" 2>/dev/null | awk 'NR == 2 { print $4 * 1024; exit }' || printf '0')"
[[ "${disk_bytes}" =~ ^[0-9]+$ ]] || disk_bytes=0

"${PYTHON_WRITER}" - "${ARTIFACT_PATH}" "${repo_version}" "${repo_commit}" \
  "${upstream_repository}" "${upstream_ref}" "${upstream_commit}" \
  "${python_command}" "${python_version}" "${python_ok}" "${docker_client_version}" \
  "${docker_server_version}" "${docker_ok}" "${architecture}" \
  "${architecture_family}" "${architecture_ok}" "${memory_bytes}" "${disk_bytes}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

(path, repo_version, repo_commit, upstream_repository, upstream_ref,
 upstream_commit, python_command, python_version, python_ok, docker_client, docker_server,
 docker_ok, architecture, architecture_family, architecture_ok, memory,
 disk) = sys.argv[1:]
python_ok = python_ok == "true"
docker_ok = docker_ok == "true"
architecture_ok = architecture_ok == "true"
memory = int(memory)
disk = int(disk)

def check(name, ok, detail):
    return {"name": name, "ok": ok, "detail": detail}

checks = [
    check("repository", repo_commit != "unknown", f"version={repo_version}; commit={repo_commit}"),
    check("upstream", True, "expected commit recorded locally; no network lookup performed"),
    check("python", python_ok, f"{python_version} at {python_command}; requires Python 3.10+"),
    check("docker", docker_ok, f"client={docker_client}; server={docker_server}"),
    check("architecture", architecture_ok, f"{architecture} ({architecture_family})"),
    check("memory", memory >= 2 * 1024**3, f"{memory} bytes detected; 4 GiB is recommended"),
    check("disk", disk >= 10 * 1024**3, f"{disk} bytes available; 25 GiB is recommended"),
]
overall = "ready" if all(item["ok"] for item in checks) else "blocked"
document = {
    "schema_version": 1,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "project_root": str(Path(path).parents[2]),
    "overall": overall,
    "checks": checks,
    "upstream": {"repository": upstream_repository, "ref": upstream_ref, "commit": upstream_commit},
    "secrets_recorded": False,
    "write_policy": "Only .launchpad/studio/preflight.json is written by studio-doctor.sh.",
}
Path(path).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
print("OmegaClaw Launchpad Studio preflight")
for item in checks:
    print(f"[{('ready' if item['ok'] else 'blocked').upper():7}] {item['name']}: {item['detail']}")
print(f"Overall: {overall.upper()}")
print(f"Report: {path}")
raise SystemExit(0 if overall == "ready" else 1)
PY
