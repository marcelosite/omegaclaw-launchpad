"""Environment checks for the onboarding journey.

The checks deliberately distinguish hard blockers for a real launch from
non-blocking omissions that still allow the offline demo and documentation
journey to work.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .config import PROVIDER_ENV


@dataclass
class Check:
    name: str
    status: str
    detail: str
    fix: Optional[str] = None


def _command_version(command: str) -> Optional[str]:
    try:
        result = subprocess.run(
            [command, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = (result.stdout or result.stderr).strip()
    return output or None


def run_checks(workspace: Path, provider: str, channel: str = "irc") -> List[Check]:
    checks: List[Check] = []

    if sys.version_info >= (3, 10):
        checks.append(Check("Python", "pass", "%d.%d available" % sys.version_info[:2]))
    else:
        checks.append(Check(
            "Python", "fail", "%d.%d detected; OmegaClaw documents Python 3.10+" % sys.version_info[:2],
            "Install Python 3.10 or newer for a real OmegaClaw run.",
        ))

    git_version = _command_version("git")
    checks.append(Check("Git", "pass", git_version or "available") if git_version else Check(
        "Git", "fail", "git was not found", "Install Git and retry."
    ))

    docker = shutil.which("docker")
    if not docker:
        checks.append(Check(
            "Docker", "warn", "not found; offline onboarding still works",
            "Install Docker Desktop/Engine before the real launch step.",
        ))
    else:
        try:
            result = subprocess.run([docker, "info"], check=False, capture_output=True, timeout=8)
        except (OSError, subprocess.TimeoutExpired):
            result = None
        if result is not None and result.returncode == 0:
            checks.append(Check("Docker", "pass", "installed and daemon is reachable"))
        else:
            checks.append(Check(
                "Docker", "warn", "installed but daemon is not reachable",
                "Start Docker before the real launch step.",
            ))

    if workspace.exists() and os.access(str(workspace), os.W_OK):
        checks.append(Check("Workspace", "pass", str(workspace.resolve())))
    else:
        checks.append(Check(
            "Workspace", "fail", "%s is missing or not writable" % workspace,
            "Choose a writable workspace directory.",
        ))

    env_name = PROVIDER_ENV[provider]
    if os.environ.get(env_name):
        checks.append(Check("LLM credential", "pass", "%s is set" % env_name))
    else:
        checks.append(Check(
            "LLM credential", "warn", "%s is not set; real launch will stop here" % env_name,
            "Export the provider key only when you are ready to launch. It is never written by Launchpad.",
        ))

    channel_env = {
        "telegram": "TG_BOT_TOKEN",
        "slack": "SL_BOT_TOKEN",
        "websocket": "WS_URL",
        "mattermost": "MM_BOT_TOKEN",
    }.get(channel)
    if channel_env:
        if os.environ.get(channel_env):
            checks.append(Check("Channel setting", "pass", "%s is set" % channel_env))
        else:
            checks.append(Check(
                "Channel setting", "warn", "%s is not set; real launch will need it" % channel_env,
                "Export the channel token/URL only when you are ready to launch.",
            ))

    return checks


def print_checks(checks: List[Check], as_json: bool = False) -> int:
    if as_json:
        import json
        print(json.dumps([check.__dict__ for check in checks], indent=2))
    else:
        symbols = {"pass": "OK", "warn": "!!", "fail": "XX"}
        for check in checks:
            print("[%s] %-18s %s" % (symbols[check.status], check.name, check.detail))
            if check.fix:
                print("     next: %s" % check.fix)
    return 1 if any(check.status == "fail" for check in checks) else 0
