"""File-backed, auditable contracts for the First Reflection mission.

The deterministic parts in this module deliberately do not pretend to be
OmegaClaw.  They prepare evidence for the real runtime and keep every human
decision explicit.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_MISSION_ID = "source-audit-demo-001"
SCHEMA_VERSION = 1


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def mission_root(workspace: Path, mission_id: str = DEFAULT_MISSION_ID) -> Path:
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", mission_id) is None:
        raise ValueError("mission_id must contain only letters, numbers, dots, dashes, or underscores")
    return workspace.resolve() / ".launchpad" / "first-reflection" / mission_id


def initialize_mission(workspace: Path, mission_id: str = DEFAULT_MISSION_ID) -> Path:
    """Create the mission contract. Existing evidence is never overwritten."""
    root = mission_root(workspace, mission_id)
    mission_path = root / "00-mission" / "mission.json"
    if mission_path.exists():
        raise FileExistsError("mission already exists: %s" % root)

    mission = {
        "schema_version": SCHEMA_VERSION,
        "mission_id": mission_id,
        "title": "Audit a source-backed report",
        "objective": "Produce a report supported by at least three distinct sources.",
        "executor": {"kind": "controlled-fixture", "version": "1"},
        "rules": [
            {
                "id": "minimum-distinct-sources",
                "type": "event-count",
                "event_type": "source.opened",
                "minimum_distinct": 3,
            },
            {
                "id": "declaration-must-match-observation",
                "type": "declaration-match",
                "declaration_field": "claimed_source_count",
            },
        ],
        "limits": {
            "auto_apply_changes": False,
            "external_network": False,
            "workspace_scope": "mission-directory-only",
        },
        "approval": {"required": True, "roles": ["human-owner"]},
        "created_at": _now(),
    }
    _write_json(mission_path, mission)
    (root / "00-mission" / "mission.md").write_text(
        "# Source audit mission\n\n"
        "Produce a report supported by at least three distinct sources.\n\n"
        "The controlled first run intentionally violates this rule so the "
        "audit and reflection path can be demonstrated.\n",
        encoding="utf-8",
    )
    return root


def _hash_event(event: Dict[str, Any]) -> str:
    canonical = json.dumps(event, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _events(run_id: str, source_ids: Iterable[str], claimed: int) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    previous: Optional[str] = None
    sequence = 1
    for source_id in source_ids:
        event = {
            "schema_version": SCHEMA_VERSION,
            "event_id": "%s-evt-%03d" % (run_id, sequence),
            "sequence": sequence,
            "run_id": run_id,
            "type": "source.opened",
            "producer": "controlled-fixture",
            "at": _now(),
            "data": {"source_id": source_id, "uri": "fixture://%s" % source_id},
            "previous_event_sha256": previous,
        }
        events.append(event)
        previous = _hash_event(event)
        sequence += 1
    completed = {
        "schema_version": SCHEMA_VERSION,
        "event_id": "%s-evt-%03d" % (run_id, sequence),
        "sequence": sequence,
        "run_id": run_id,
        "type": "report.completed",
        "producer": "controlled-fixture",
        "at": _now(),
        "data": {"claimed_source_count": claimed},
        "previous_event_sha256": previous,
    }
    events.append(completed)
    return events


def _write_events(path: Path, events: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(item, sort_keys=True) + "\n" for item in events),
        encoding="utf-8",
    )


def execute_controlled_run(root: Path, rerun: bool = False) -> Path:
    """Run the transparent fixture used by the sprint demonstration."""
    _read_json(root / "00-mission" / "mission.json")
    run_id = "run-2" if rerun else "run-1"
    run_dir = root / ("05-rerun" if rerun else "01-run-1")
    if (run_dir / "events.jsonl").exists():
        raise FileExistsError("run evidence already exists: %s" % run_dir)
    if rerun:
        decision = _read_json(root / "04-review" / "decision.json")
        if decision.get("decision") != "approved":
            raise PermissionError("rerun requires an explicit approved decision")
        source_ids = ["source-a", "source-b", "source-c"]
    else:
        source_ids = ["source-a"]
    claimed = 3
    _write_events(run_dir / "events.jsonl", _events(run_id, source_ids, claimed))
    _write_json(
        run_dir / "declarations.json",
        {"schema_version": SCHEMA_VERSION, "run_id": run_id, "claimed_source_count": claimed},
    )
    (run_dir / "report.md").write_text(
        "# Controlled report\n\n"
        "This fixture claims it consulted **%d sources**. The independent event "
        "record is the evidence used by the validator.\n" % claimed,
        encoding="utf-8",
    )
    return run_dir


def _load_events(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def validate_run(root: Path, rerun: bool = False) -> Dict[str, Any]:
    mission = _read_json(root / "00-mission" / "mission.json")
    run_id = "run-2" if rerun else "run-1"
    run_dir = root / ("05-rerun" if rerun else "01-run-1")
    events = _load_events(run_dir / "events.jsonl")
    declarations = _read_json(run_dir / "declarations.json")
    distinct = sorted(
        {item["data"]["source_id"] for item in events if item.get("type") == "source.opened"}
    )
    claimed = int(declarations["claimed_source_count"])
    expected = int(mission["rules"][0]["minimum_distinct"])
    findings = [
        {
            "rule_id": "minimum-distinct-sources",
            "status": "pass" if len(distinct) >= expected else "fail",
            "expected": expected,
            "observed": len(distinct),
            "evidence_event_ids": [
                item["event_id"] for item in events if item.get("type") == "source.opened"
            ],
        },
        {
            "rule_id": "declaration-must-match-observation",
            "status": "pass" if claimed == len(distinct) else "fail",
            "declared": claimed,
            "observed": len(distinct),
        },
    ]
    status = "pass" if all(item["status"] == "pass" for item in findings) else "fail"
    result = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "validator": "deterministic-event-audit-v1",
        "findings": findings,
    }
    output_dir = root / ("05-rerun" if rerun else "02-validation")
    filename = "validation-rerun.json" if rerun else "validation.json"
    _write_json(output_dir / filename, result)
    md_name = "validation-rerun.md" if rerun else "validation.md"
    (output_dir / md_name).write_text(
        "# Validation: %s\n\nExpected sources: **%d**  \nObserved sources: **%d**  \n"
        "Declared sources: **%d**  \nResult: **%s**\n"
        % (run_id, expected, len(distinct), claimed, status.upper()),
        encoding="utf-8",
    )
    return result


def prepare_reflection(root: Path) -> Dict[str, Any]:
    """Freeze verified facts for a future real OmegaClaw invocation."""
    reflection_dir = root / "03-reflection"
    if (reflection_dir / "reflection-context.json").exists():
        raise FileExistsError("reflection evidence already exists: %s" % reflection_dir)
    validation = _read_json(root / "02-validation" / "validation.json")
    if validation["status"] != "fail":
        raise ValueError("reflection is only prepared for a failed first run")
    finding = validation["findings"][0]
    context = {
        "schema_version": SCHEMA_VERSION,
        "mission_id": _read_json(root / "00-mission" / "mission.json")["mission_id"],
        "run_id": "run-1",
        "validated_findings": [finding],
        "evidence": [
            {
                "source": "executor-declaration",
                "claim": "three-sources-consulted",
                "stv": {"frequency": 1.0, "confidence": 0.45},
            },
            {
                "source": "event-recorder-audit",
                "claim": "three-sources-consulted",
                "stv": {"frequency": 0.0, "confidence": 0.9},
            },
        ],
        "constraints": {
            "must_not_apply_changes": True,
            "must_distinguish_observation_from_inference": True,
        },
        "omega_integration": {
            "status": "pending",
            "required_runtime": "OmegaClaw-Core v0.1.19 built locally",
            "provider": "Test",
            "channel": "websocket",
            "required_capability": "real (metta ...) skill invocation with NAL result",
        },
    }
    _write_json(reflection_dir / "reflection-context.json", context)
    (reflection_dir / "omega-response.txt").write_text(
        "PENDING REAL OMEGACLAW RUN\n"
        "No OmegaClaw response has been fabricated. Run the upstream proof harness "
        "and replace this file only with captured runtime output.\n",
        encoding="utf-8",
    )
    proposal = {
        "schema_version": SCHEMA_VERSION,
        "id": "derive-source-count-from-recorder",
        "origin": "controlled-fixture-not-omegaclaw",
        "summary": "Derive the source count from recorded events before concluding the mission.",
        "scope": "rerun-only",
        "auto_apply": False,
    }
    _write_json(reflection_dir / "proposal.json", proposal)
    return context


def record_decision(root: Path, decision: str) -> Dict[str, Any]:
    if decision not in {"approved", "rejected"}:
        raise ValueError("decision must be approved or rejected")
    decision_path = root / "04-review" / "decision.json"
    if decision_path.exists():
        raise FileExistsError("human decision already exists: %s" % decision_path)
    proposal = _read_json(root / "03-reflection" / "proposal.json")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "decision": decision,
        "decided_by": "human-owner",
        "approved_change": proposal if decision == "approved" else None,
        "at": _now(),
    }
    review_dir = root / "04-review"
    _write_json(decision_path, payload)
    (review_dir / "decision.md").write_text(
        "# Human decision\n\nDecision: **%s**\n\nNo automatic change was permitted.\n"
        % decision.upper(),
        encoding="utf-8",
    )
    return payload


def create_receipt(root: Path) -> Dict[str, Any]:
    before = _read_json(root / "02-validation" / "validation.json")
    after_path = root / "05-rerun" / "validation-rerun.json"
    after = _read_json(after_path)
    decision = _read_json(root / "04-review" / "decision.json")
    omega_proof_path = root / "03-reflection" / "omega-proof.json"
    if omega_proof_path.exists():
        omega_proof = _read_json(omega_proof_path)
    else:
        omega_proof = {
            "status": "pending",
            "claim": "This local receipt does not claim an OmegaClaw run occurred.",
        }
    payload = {
        "schema_version": SCHEMA_VERSION,
        "mission_id": _read_json(root / "00-mission" / "mission.json")["mission_id"],
        "before": {"status": before["status"], "observed_sources": before["findings"][0]["observed"]},
        "human_decision": decision["decision"],
        "after": {"status": after["status"], "observed_sources": after["findings"][0]["observed"]},
        "omega_proof": omega_proof,
    }
    receipt_dir = root / "06-receipt"
    _write_json(receipt_dir / "comparison.json", payload)
    (receipt_dir / "final-receipt.md").write_text(
        "# First Reflection receipt\n\n"
        "| Stage | Result | Observed sources |\n"
        "|---|---:|---:|\n"
        "| Before | %s | %d |\n"
        "| After approved rerun | %s | %d |\n\n"
        "Human decision: **%s**\n\n"
        "> OmegaClaw proof status: **%s**. When pending, this receipt proves only "
        "the local instrumented mission, deterministic audit, approval gate, and rerun.\n"
        % (
            before["status"].upper(),
            before["findings"][0]["observed"],
            after["status"].upper(),
            after["findings"][0]["observed"],
            decision["decision"].upper(),
            omega_proof["status"].upper(),
        ),
        encoding="utf-8",
    )
    return payload
