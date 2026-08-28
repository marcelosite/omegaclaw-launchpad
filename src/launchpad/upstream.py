"""Translate a Launchpad manifest into a safe upstream launch handoff."""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Dict, Any


def render_launch_command(config: Dict[str, Any], upstream_dir: Path) -> str:
    """Return a copy/pasteable command without interpolating any secret."""
    provider = config["provider"]
    channel = config["channel"]
    args = [
        "OMEGACLAW_AUTH_SECRET=\"${OMEGACLAW_AUTH_SECRET:?set a local channel secret}\"",
        shlex.quote(str(upstream_dir / "scripts" / "omegaclaw")),
        "start",
        "-p", shlex.quote(provider),
        "-t", shlex.quote(channel),
        "-d", shlex.quote(config["upstream"]["image"]),
    ]
    if channel == "irc":
        args.extend(["-c", shlex.quote(config["irc_channel"])])
    return " ".join(args)


def render_bootstrap_script(config: Dict[str, Any], root: Path) -> str:
    """Create a real launcher that clones the pinned upstream source on demand."""
    upstream_dir = root / ".launchpad" / "upstream"
    repo = config["upstream"]["repository"]
    ref = config["upstream"]["ref"]
    commit = config["upstream"]["commit"]
    image = config["upstream"]["image"]
    command = render_launch_command(config, upstream_dir)
    return """#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM_DIR="${ROOT}/.launchpad/upstream"

if [[ ! -x "${UPSTREAM_DIR}/scripts/omegaclaw" ]]; then
  mkdir -p "${ROOT}/.launchpad"
  if [[ -e "${UPSTREAM_DIR}" ]]; then
    echo "Launchpad found an incomplete upstream checkout at ${UPSTREAM_DIR}." >&2
    exit 1
  fi
  echo "Fetching OmegaClaw-Core %s..."
  git clone --depth 1 --branch %s %s "${UPSTREAM_DIR}"
fi

ACTUAL_COMMIT="$(git -C "${UPSTREAM_DIR}" rev-parse HEAD)"
if [[ "${ACTUAL_COMMIT}" != "%s" ]]; then
  echo "Refusing unverified upstream commit: ${ACTUAL_COMMIT}" >&2
  exit 1
fi

if ! docker image inspect %s >/dev/null 2>&1; then
  echo "Building the pinned OmegaClaw image %s..."
  docker build -t %s "${UPSTREAM_DIR}"
fi

echo "Handing off to the upstream OmegaClaw launcher."
echo "Credential variables are read from your shell and are not stored by Launchpad."
%s
""" % (
        ref,
        ref,
        shlex.quote(repo),
        commit,
        shlex.quote(image),
        image,
        shlex.quote(image),
        command.replace(str(upstream_dir), '"${UPSTREAM_DIR}"'),
    )
