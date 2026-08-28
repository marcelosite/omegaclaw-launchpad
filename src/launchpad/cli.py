"""Command-line interface for OmegaClaw Launchpad."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .config import CHANNELS, PROVIDERS
from .doctor import print_checks, run_checks
from .journey import load_config, next_action, write_onboarding_files


def _root(value: str) -> Path:
    return Path(value).expanduser().resolve()


def _add_workspace(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", default=".", type=_root, help="directory where onboarding files are created")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="omega-launchpad",
        description="Take a newcomer from zero to a first OmegaClaw launch handoff.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor", help="check local prerequisites without changing the system")
    _add_workspace(doctor)
    doctor.add_argument("--provider", choices=PROVIDERS, default="Anthropic")
    doctor.add_argument("--channel", choices=CHANNELS, default="irc")
    doctor.add_argument("--json", action="store_true", help="emit machine-readable results")

    init = commands.add_parser("init", help="write a secret-safe onboarding manifest and launch handoff")
    _add_workspace(init)
    init.add_argument("--provider", choices=PROVIDERS, default="Anthropic")
    init.add_argument("--channel", choices=CHANNELS, default="irc")
    init.add_argument("--irc-channel", default="##my-omegaclaw", help="IRC channel when --channel=irc")

    onboard = commands.add_parser("onboard", help="initialize the journey and show its next action")
    _add_workspace(onboard)
    onboard.add_argument("--provider", choices=PROVIDERS, default="Anthropic")
    onboard.add_argument("--channel", choices=CHANNELS, default="irc")
    onboard.add_argument("--irc-channel", default="##my-omegaclaw")

    demo = commands.add_parser("demo", help="run the offline onboarding proof; no Docker or API key needed")
    demo.add_argument("--json", action="store_true", help="emit the proof as JSON")
    return parser


def _init(args: argparse.Namespace) -> int:
    args.workspace.mkdir(parents=True, exist_ok=True)
    config = write_onboarding_files(args.workspace, args.provider, args.channel, args.irc_channel)
    print("Initialized OmegaClaw Launchpad in %s" % args.workspace)
    print("  manifest: %s" % (args.workspace / ".launchpad" / "config.json"))
    print("  launcher: %s" % (args.workspace / ".launchpad" / "run-omegaclaw.sh"))
    print("  provider key: %s (not stored)" % config["provider_env"])
    return 0


def _doctor(args: argparse.Namespace) -> int:
    if not args.json:
        print("OmegaClaw Launchpad preflight")
    return print_checks(run_checks(args.workspace, args.provider, args.channel), args.json)


def _onboard(args: argparse.Namespace) -> int:
    code = _init(args)
    if code:
        return code
    print("\nPreflight:")
    doctor_code = print_checks(run_checks(args.workspace, args.provider, args.channel))
    config = load_config(args.workspace)
    if doctor_code == 0:
        config["journey"]["preflight"] = "complete"
        (args.workspace / ".launchpad" / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print("\nNext action: %s" % next_action(config, docker_ready=False))
    return doctor_code


def _demo(args: argparse.Namespace) -> int:
    proof = {
        "mode": "offline-proof",
        "claims": [
            "Launchpad can explain the journey without an LLM key.",
            "Launchpad emits a secret-safe manifest and upstream handoff.",
            "Launchpad keeps the real OmegaClaw runtime in OmegaClaw-Core.",
        ],
        "steps": [
            {"step": "orientation", "result": "OmegaClaw is a MeTTa loop on Hyperon with Python bridges."},
            {"step": "preflight", "result": "offline mode is available; Docker and credentials are launch-time checks."},
            {"step": "configuration", "result": "provider/channel selected; no secret persisted."},
            {"step": "first agent", "result": "handoff is ready for the upstream scripts/omegaclaw launcher."},
        ],
    }
    if args.json:
        print(json.dumps(proof, indent=2))
    else:
        print("OmegaClaw Launchpad — offline proof")
        for item in proof["steps"]:
            print("[OK] %-14s %s" % (item["step"], item["result"]))
        print("\nThis proves the onboarding layer only; it does not pretend to run OmegaClaw without its runtime.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "doctor":
        return _doctor(args)
    if args.command == "init":
        return _init(args)
    if args.command == "onboard":
        return _onboard(args)
    if args.command == "demo":
        return _demo(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
