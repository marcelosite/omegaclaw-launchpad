#!/usr/bin/env bash
set -euo pipefail

# Friendly entry point for the second real-runtime lesson.  The underlying
# runner still owns Docker and writes only the approved local run artifacts.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/run-omegaclaw-proof.sh" --factory-fault "$@"
