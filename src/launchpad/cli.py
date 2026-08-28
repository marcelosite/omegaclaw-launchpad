"""Command-line interface for OmegaClaw Launchpad."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, Sequence

from . import __version__
from .config import CHANNELS, PROVIDERS
from .doctor import print_checks, run_checks
from .journey import load_config, next_action, write_onboarding_files
from .proof import proof_checks
from .reflection import (
    DEFAULT_MISSION_ID,
    create_receipt,
    execute_controlled_run,
    initialize_mission,
    mission_root,
    prepare_reflection,
    record_decision,
    validate_run,
)


def _root(value: str) -> Path:
    return Path(value).expanduser().resolve()


def _add_workspace(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", default=".", type=_root, help="directory where onboarding files are created")


def _add_reflection_location(parser: argparse.ArgumentParser) -> None:
    _add_workspace(parser)
    parser.add_argument("--mission-id", default=DEFAULT_MISSION_ID)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="omega-launchpad",
        description="Guide a newcomer through a first governed OmegaClaw reflection.",
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

    reflect = commands.add_parser("reflect", help="run the instrumented First Reflection mission")
    reflect_commands = reflect.add_subparsers(dest="reflect_command", required=True)

    reflect_init = reflect_commands.add_parser("init", help="create the mission contract")
    _add_reflection_location(reflect_init)

    reflect_run = reflect_commands.add_parser("run", help="execute the intentionally flawed controlled run")
    _add_reflection_location(reflect_run)

    reflect_validate = reflect_commands.add_parser("validate", help="validate claims against recorded events")
    _add_reflection_location(reflect_validate)

    reflect_prepare = reflect_commands.add_parser(
        "prepare", help="freeze verified facts for a real OmegaClaw reflection"
    )
    _add_reflection_location(reflect_prepare)

    reflect_prove = reflect_commands.add_parser(
        "prove", help="check readiness for the pinned real OmegaClaw proof harness"
    )
    _add_reflection_location(reflect_prove)
    reflect_prove.add_argument("--json", action="store_true")

    reflect_review = reflect_commands.add_parser("review", help="approve or reject the proposed rerun")
    _add_reflection_location(reflect_review)
    reflect_review.add_argument(
        "--decision", choices=("approved", "rejected"), help="non-interactive human decision"
    )

    reflect_rerun = reflect_commands.add_parser("rerun", help="repeat the fixture after explicit approval")
    _add_reflection_location(reflect_rerun)

    reflect_receipt = reflect_commands.add_parser("receipt", help="write the before/after receipt")
    _add_reflection_location(reflect_receipt)

    reflect_demo = reflect_commands.add_parser(
        "demo", help="run the local controlled cycle; clearly excludes the pending OmegaClaw proof"
    )
    _add_reflection_location(reflect_demo)
    reflect_demo.add_argument(
        "--decision", choices=("approved", "rejected"), default="approved"
    )
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


def _reflection_path(args: argparse.Namespace) -> Path:
    return mission_root(args.workspace, args.mission_id)


def _print_validation(result: dict) -> None:
    finding = result["findings"][0]
    declaration = result["findings"][1]
    print("Expected: %s distinct sources" % finding["expected"])
    print("Observed: %s distinct sources" % finding["observed"])
    print("Declared: %s sources" % declaration["declared"])
    print("Result: %s" % result["status"].upper())


def _interactive_decision(root: Path) -> Optional[str]:
    proposal = json.loads((root / "03-reflection" / "proposal.json").read_text(encoding="utf-8"))
    while True:
        print("\nREFLECTION REVIEW")
        print("\nVerified failure: the report declared 3 sources; the recorder observed 1.")
        print("\nControlled proposal: %s" % proposal["summary"])
        print("Origin: %s" % proposal["origin"])
        print("\n1. Approve and allow the controlled rerun")
        print("2. Show the complete reflection context")
        print("3. Reject")
        print("4. Exit without a decision")
        choice = input("\nChoose: ").strip()
        if choice == "1":
            return "approved"
        if choice == "2":
            print("\n%s" % (root / "03-reflection" / "reflection-context.json").read_text(encoding="utf-8"))
            continue
        if choice == "3":
            return "rejected"
        if choice == "4":
            return None
        print("Choose 1, 2, 3, or 4.")


def _reflect(args: argparse.Namespace) -> int:
    root = _reflection_path(args)
    if args.reflect_command == "init":
        created = initialize_mission(args.workspace, args.mission_id)
        print("Mission created: %s" % created)
        return 0
    if args.reflect_command == "run":
        run_dir = execute_controlled_run(root)
        print("Controlled first run recorded: %s" % run_dir)
        return 0
    if args.reflect_command == "validate":
        _print_validation(validate_run(root))
        return 0
    if args.reflect_command == "prepare":
        prepare_reflection(root)
        print("Reflection context prepared: %s" % (root / "03-reflection" / "reflection-context.json"))
        print("OmegaClaw status: PENDING — no runtime response was fabricated.")
        return 0
    if args.reflect_command == "prove":
        project_root = Path(__file__).resolve().parents[2]
        checks = proof_checks(project_root, root)
        if args.json:
            print(json.dumps(checks, indent=2))
        else:
            print("Real OmegaClaw proof readiness")
            for check in checks:
                print("[%s] %-16s %s" % ("OK" if check["ok"] else "BLOCKED", check["name"], check["detail"]))
            if all(check["ok"] for check in checks):
                print("\nReady: scripts/run-omegaclaw-proof.sh %s" % args.mission_id)
            else:
                print("\nNo OmegaClaw proof was claimed or simulated.")
        return 0 if all(check["ok"] for check in checks) else 1
    if args.reflect_command == "review":
        decision = args.decision or _interactive_decision(root)
        if decision is None:
            print("No decision recorded.")
            return 0
        record_decision(root, decision)
        print("Human decision recorded: %s" % decision.upper())
        return 0
    if args.reflect_command == "rerun":
        execute_controlled_run(root, rerun=True)
        result = validate_run(root, rerun=True)
        _print_validation(result)
        return 0
    if args.reflect_command == "receipt":
        create_receipt(root)
        print("Receipt written: %s" % (root / "06-receipt" / "final-receipt.md"))
        return 0
    if args.reflect_command == "demo":
        initialize_mission(args.workspace, args.mission_id)
        execute_controlled_run(root)
        print("\nFIRST RUN")
        _print_validation(validate_run(root))
        prepare_reflection(root)
        print("\nOMEGACLAW PROOF: PENDING (not simulated)")
        record_decision(root, args.decision)
        print("HUMAN DECISION: %s" % args.decision.upper())
        if args.decision == "approved":
            execute_controlled_run(root, rerun=True)
            print("\nCONTROLLED RERUN")
            _print_validation(validate_run(root, rerun=True))
            create_receipt(root)
            print("\nReceipt: %s" % (root / "06-receipt" / "final-receipt.md"))
        return 0
    return 2


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
    if args.command == "reflect":
        return _reflect(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
