#!/usr/bin/env bash
set -euo pipefail

REMOTE="${1:-}"
# Keep the VPS tunnel separate from a local Studio that normally uses 8765.
LOCAL_PORT="${STUDIO_LOCAL_PORT:-8876}"
REMOTE_PORT="8765"

if [[ -n "${REMOTE}" && ! "${REMOTE}" =~ ^[A-Za-z0-9._@:-]+$ ]]; then
  echo "The SSH target contains unsupported characters." >&2
  exit 2
fi

echo "Run this SSH tunnel in your own terminal after checking the host:"
if [[ -n "${REMOTE}" ]]; then
  echo "ssh -N -L ${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT} ${REMOTE}"
else
  echo "ssh -N -L ${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT} <your-vps-ssh-target>"
fi
echo
echo "Then open: http://127.0.0.1:${LOCAL_PORT}"
echo "Keep the SSH tunnel terminal open while using the Wizard."
echo "This helper only prints instructions; it does not make an SSH connection."
