#!/usr/bin/env bash
set -euo pipefail

REMOTE="${1:-ubuntu@VPS_IP}"
LOCAL_PORT="8765"
REMOTE_PORT="8765"

if [[ ! "${REMOTE}" =~ ^[A-Za-z0-9._@:-]+$ ]]; then
  echo "The SSH target contains unsupported characters." >&2
  exit 2
fi

echo "Run this SSH tunnel in your own terminal after checking the host:"
echo "ssh -N -L ${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT} ${REMOTE}"
echo
echo "Then open: http://127.0.0.1:${LOCAL_PORT}"
echo "This helper only prints instructions; it does not make an SSH connection."
