"""Journey state and generated onboarding artifacts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from .config import build_config
from .upstream import render_bootstrap_script, render_launch_command


def write_onboarding_files(root: Path, provider: str, channel: str, irc_channel: str) -> Dict[str, Any]:
    root = root.resolve()
    launchpad_dir = root / ".launchpad"
    launchpad_dir.mkdir(parents=True, exist_ok=True)
    config = build_config(root, provider, channel, irc_channel)
    config["journey"].update({
        "orientation": "complete",
        "preflight": "pending",
        "configuration": "complete",
    })

    (launchpad_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    (root / ".env.example").write_text(
        "# Copy values into your shell; do not commit real credentials.\n"
        "# The Launchpad never writes provider keys.\n"
        "OMEGACLAW_AUTH_SECRET=choose-a-local-channel-secret\n"
        "%s=replace-with-your-provider-key\n" % config["provider_env"]
        + (("%s=replace-with-your-channel-token-or-url\n" % config["channel_env"])
           if config["channel_env"] else ""),
        encoding="utf-8",
    )
    (launchpad_dir / "run-omegaclaw.sh").write_text(
        render_bootstrap_script(config, root), encoding="utf-8"
    )
    os.chmod(launchpad_dir / "run-omegaclaw.sh", 0o755)
    return config


def load_config(root: Path) -> Dict[str, Any]:
    path = root.resolve() / ".launchpad" / "config.json"
    return json.loads(path.read_text(encoding="utf-8"))


def next_action(config: Dict[str, Any], docker_ready: bool = False) -> str:
    journey = config["journey"]
    if journey["preflight"] != "complete":
        return "Run `python -m launchpad doctor` and resolve the hard blockers."
    if journey["first_run"] != "complete":
        if docker_ready:
            return "Run `.launchpad/run-omegaclaw.sh` after exporting the provider key and channel secret."
        return "Install/start Docker and export the provider key, then run `.launchpad/run-omegaclaw.sh`."
    return "Read the next-step tutorial and build a small skill or channel adapter."
