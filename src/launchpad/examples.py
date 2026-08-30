"""Fast, deterministic checks for the canonical Lighthouse example."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


REQUIRED_FILES = (
    "README.md", "story.md", "claims.json", "facts.json",
    "verified-update.json", "runtime-bulletin.txt", "rules.md", "reasoning.metta", "tests.json",
    "workspace.json", "example-receipt.md", "AGENTS.md", "CLAUDE.md",
)


def validate_example(root: Path) -> List[str]:
    """Return human-readable failures without modifying the example."""
    errors: List[str] = []
    root = root.resolve()
    for name in REQUIRED_FILES:
        path = root / name
        if not path.is_file() or path.is_symlink():
            errors.append("missing or unsafe file: %s" % name)
    if errors:
        return errors
    try:
        manifest = json.loads((root / "workspace.json").read_text(encoding="utf-8"))
        facts = json.loads((root / "facts.json").read_text(encoding="utf-8"))
        claims = json.loads((root / "claims.json").read_text(encoding="utf-8"))
        tests = json.loads((root / "tests.json").read_text(encoding="utf-8"))
        update = json.loads((root / "verified-update.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return ["JSON could not be read: %s" % error]
    if manifest.get("schema_version") != 2 or manifest.get("example") != "lighthouse-in-the-fog":
        errors.append("workspace.json must identify Lighthouse schema version 2")
    if manifest.get("runtime_bulletin") != "runtime-bulletin.txt":
        errors.append("workspace.json must identify the one-line runtime bulletin")
    if facts.get("scenario_id") != "lighthouse-in-the-fog" or claims.get("scenario_id") != "lighthouse-in-the-fog":
        errors.append("facts and claims must use the Lighthouse scenario id")
    forbidden = set(facts.get("forbidden_actions") or [])
    if forbidden != {"steer_boat", "activate_navigation_signal", "send_external_message"}:
        errors.append("the fixed external-action boundary changed")
    case_by_id = {case.get("id"): case for case in tests.get("cases", []) if isinstance(case, dict)}
    expected = {
        "conflicting-current-reports", "verified-independent-update",
        "missing-required-beacon", "gigo-anonymous-claim-only",
    }
    if set(case_by_id) != expected:
        errors.append("tests.json must contain conflict, update, missing, and GIGO cases")
    for case in case_by_id.values():
        if case.get("human_approval_required") is not True or case.get("external_actions") != []:
            errors.append("every case must require a human and execute no external action")
            break
    if update.get("provenance") != "controlled-local-read-only-file":
        errors.append("the controlled bulletin provenance changed")
    runtime_bulletin = (root / "runtime-bulletin.txt").read_text(encoding="utf-8").strip()
    if "source=harbor-control" not in runtime_bulletin or "observation=north_buoy_operational" not in runtime_bulletin:
        errors.append("the runtime bulletin must project the identified source and observation")
    reasoning = (root / "reasoning.metta").read_text(encoding="utf-8")
    if reasoning.count("(|-") != 2 or "stv" not in reasoning:
        errors.append("reasoning.metta must contain the two NAL/STV teaching expressions")
    receipt = (root / "example-receipt.md").read_text(encoding="utf-8").lower()
    if "did not run" not in receipt or "never runtime evidence" not in receipt:
        errors.append("the fixture receipt must say OmegaClaw did not run")
    return errors
