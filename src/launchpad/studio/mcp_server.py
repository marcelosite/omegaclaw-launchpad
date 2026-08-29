"""A bounded, local STDIO MCP bridge for the Studio evidence.

The bridge is deliberately not an OmegaClaw executor.  It consults the
verified, synthetic factory-fault lesson and returns a new local receipt.  It
has no shell, network, provider, or arbitrary-file capability.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any, IO, Dict, Optional

from .artifacts import StudioArtifacts


SLUG_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,62}\Z")
RECEIPT_PATTERN = re.compile(r"mcp-[0-9a-f]{32}\Z")
MAX_QUESTION_LENGTH = 1000
MAX_AGENT_ID_LENGTH = 64
MAX_EVIDENCE_ID_LENGTH = 96

# This is intentionally a *single*, closed teaching packet.  It demonstrates
# the shape of a useful agent disagreement without turning the local bridge
# into a general multi-agent decision service.
RELEASE_READINESS_CASE_ID = "release-readiness-demo"
RELEASE_READINESS_RULEBOOK_ID = "release-readiness-demo-r1"
RELEASE_READINESS_FACTS = {"unit_tests", "required_security_check"}
RELEASE_READINESS_STATUSES = {"passed", "missing", "failed", "unknown"}
RELEASE_POSITIONS = {"release_ready", "release_not_ready"}
FORBIDDEN_RELEASE_ACTIONS = {"deploy", "merge", "approve_release"}
CONSULTATION_STATUSES = {"observed", "missing", "unknown"}


def _error(code: int, message: str, request_id: Any = None) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _ok(result: Any, request_id: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _tools() -> list[Dict[str, Any]]:
    return [
        {
            "name": "omega.reason",
            "description": "Consult the verified synthetic factory-fault lesson and record a local receipt. This never runs an external action.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string", "description": "A local Studio workspace slug, or factory-fault."},
                    "question": {"type": "string", "description": "A question about the published lesson or the bounded release-readiness teaching packet."},
                    "conflict_packet": {
                        "type": "object",
                        "description": "Optional closed teaching packet for one release-readiness disagreement. It is not a general multi-agent input API and does not validate external evidence.",
                        "properties": {
                            "case_id": {"const": RELEASE_READINESS_CASE_ID},
                            "rulebook_id": {"const": RELEASE_READINESS_RULEBOOK_ID},
                            "claims": {
                                "type": "array",
                                "minItems": 2,
                                "maxItems": 4,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {"type": "string", "maxLength": MAX_AGENT_ID_LENGTH},
                                        "position": {"enum": sorted(RELEASE_POSITIONS)},
                                        "evidence_ids": {"type": "array", "minItems": 1, "maxItems": 8, "items": {"type": "string", "maxLength": MAX_EVIDENCE_ID_LENGTH}},
                                    },
                                    "required": ["agent_id", "position", "evidence_ids"],
                                    "additionalProperties": False,
                                },
                            },
                            "recorded_facts": {
                                "type": "array",
                                "minItems": 2,
                                "maxItems": 2,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "fact_id": {"enum": sorted(RELEASE_READINESS_FACTS)},
                                        "status": {"enum": sorted(RELEASE_READINESS_STATUSES)},
                                        "evidence_id": {"type": "string", "maxLength": MAX_EVIDENCE_ID_LENGTH},
                                    },
                                    "required": ["fact_id", "status", "evidence_id"],
                                    "additionalProperties": False,
                                },
                            },
                            "forbidden_actions": {"type": "array", "minItems": 1, "maxItems": 3, "items": {"enum": sorted(FORBIDDEN_RELEASE_ACTIONS)}},
                        },
                        "required": ["case_id", "rulebook_id", "claims", "recorded_facts", "forbidden_actions"],
                        "additionalProperties": False,
                    },
                    "consultation": {
                        "type": "object",
                        "description": "A bounded general consultation packet for local tests. Values are self-reported and never externally validated.",
                        "properties": {
                            "case_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{0,62}$"},
                            "rule": {"type": "string", "maxLength": 500},
                            "claims": {
                                "type": "array",
                                "minItems": 1,
                                "maxItems": 8,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {"type": "string", "maxLength": MAX_AGENT_ID_LENGTH},
                                        "position": {"type": "string", "maxLength": 64},
                                        "evidence_ids": {"type": "array", "minItems": 1, "maxItems": 8, "items": {"type": "string", "maxLength": MAX_EVIDENCE_ID_LENGTH}},
                                    },
                                    "required": ["agent_id", "position", "evidence_ids"],
                                    "additionalProperties": False,
                                },
                            },
                            "facts": {
                                "type": "array",
                                "maxItems": 16,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "fact_id": {"type": "string", "maxLength": 96},
                                        "status": {"enum": sorted(CONSULTATION_STATUSES)},
                                        "evidence_id": {"type": "string", "maxLength": MAX_EVIDENCE_ID_LENGTH},
                                    },
                                    "required": ["fact_id", "status", "evidence_id"],
                                    "additionalProperties": False,
                                },
                            },
                            "forbidden_actions": {"type": "array", "maxItems": 8, "items": {"type": "string", "maxLength": 64}},
                        },
                        "required": ["case_id", "rule", "claims", "facts", "forbidden_actions"],
                        "additionalProperties": False,
                    },
                },
                "required": ["workspace_id", "question"],
                "additionalProperties": False,
            },
        },
        {
            "name": "omega.get_receipt",
            "description": "Read one receipt previously created by omega.reason using its logical receipt ID.",
            "inputSchema": {
                "type": "object",
                "properties": {"receipt_id": {"type": "string"}},
                "required": ["receipt_id"],
                "additionalProperties": False,
            },
        },
    ]


class LocalMCP:
    def __init__(self, project_root: Path):
        self.project_root = project_root.expanduser().resolve()
        self.artifacts = StudioArtifacts(self.project_root)
        self.receipts_root = self.project_root / ".launchpad" / "studio" / "runs" / "mcp"

    def _verified_factory_proof(self) -> Dict[str, Any]:
        state = self.artifacts.status()["factory_fault"]
        if state["state"] != "verified":
            raise ValueError("The factory-fault lesson has no verified local OmegaClaw proof yet.")
        try:
            payload = json.loads(self.artifacts.artifact("factory-proof")["content"])
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError) as error:
            raise ValueError("The factory-fault proof artifact is unavailable.") from error
        if not isinstance(payload, dict):
            raise ValueError("The factory-fault proof artifact is invalid.")
        return payload

    def _workspace(self, workspace_id: str) -> Path:
        if workspace_id == "factory-fault":
            return self.project_root / "templates" / "factory-fault"
        if SLUG_PATTERN.fullmatch(workspace_id) is None:
            raise ValueError("workspace_id must be a lowercase local Studio slug.")
        root = self.project_root / ".launchpad" / "studio" / "workspaces"
        destination = root / workspace_id
        if destination.parent != root or not destination.is_dir() or destination.is_symlink():
            raise ValueError("The requested local Studio workspace does not exist.")
        return destination

    @staticmethod
    def _bounded_string(value: Any, field: str, maximum: int) -> str:
        if not isinstance(value, str) or not value.strip() or len(value) > maximum or any(ord(char) < 32 for char in value):
            raise ValueError(f"{field} must be a non-empty printable string of at most {maximum} characters.")
        return value

    def _release_readiness_trace(self, packet: Any) -> Dict[str, Any]:
        """Validate and evaluate one fixed, deterministic teaching packet.

        The validation is intentionally closed: callers cannot select a new
        rulebook, fact vocabulary, or action.  Values are preserved as a
        receipt of the submitted consultation, but they are not independently
        verified and never trigger a provider or external activity.
        """
        required = {"case_id", "rulebook_id", "claims", "recorded_facts", "forbidden_actions"}
        if not isinstance(packet, dict) or set(packet) != required:
            raise ValueError("conflict_packet must contain only the fixed release-readiness teaching fields.")
        if packet["case_id"] != RELEASE_READINESS_CASE_ID or packet["rulebook_id"] != RELEASE_READINESS_RULEBOOK_ID:
            raise ValueError("conflict_packet is limited to the release-readiness-demo rulebook.")

        claims = packet["claims"]
        if not isinstance(claims, list) or not 2 <= len(claims) <= 4:
            raise ValueError("conflict_packet.claims must contain two to four recorded agent claims.")
        normalized_claims = []
        positions = set()
        for claim in claims:
            if not isinstance(claim, dict) or set(claim) != {"agent_id", "position", "evidence_ids"}:
                raise ValueError("Each claim must contain only agent_id, position, and evidence_ids.")
            agent_id = self._bounded_string(claim["agent_id"], "claim.agent_id", MAX_AGENT_ID_LENGTH)
            position = claim["position"]
            evidence_ids = claim["evidence_ids"]
            if position not in RELEASE_POSITIONS:
                raise ValueError("claim.position is not allowed by the release-readiness teaching packet.")
            if not isinstance(evidence_ids, list) or not 1 <= len(evidence_ids) <= 8:
                raise ValueError("claim.evidence_ids must contain one to eight logical evidence labels.")
            normalized_evidence_ids = [self._bounded_string(item, "claim.evidence_ids item", MAX_EVIDENCE_ID_LENGTH) for item in evidence_ids]
            normalized_claims.append({"agent_id": agent_id, "position": position, "evidence_ids": normalized_evidence_ids})
            positions.add(position)
        if positions != RELEASE_POSITIONS:
            raise ValueError("The teaching packet needs recorded claims on both sides of the release decision.")

        facts = packet["recorded_facts"]
        if not isinstance(facts, list) or len(facts) != 2:
            raise ValueError("conflict_packet.recorded_facts must contain the two fixed release-readiness facts.")
        normalized_facts = []
        statuses: Dict[str, str] = {}
        for fact in facts:
            if not isinstance(fact, dict) or set(fact) != {"fact_id", "status", "evidence_id"}:
                raise ValueError("Each recorded fact must contain only fact_id, status, and evidence_id.")
            fact_id, status = fact["fact_id"], fact["status"]
            if fact_id not in RELEASE_READINESS_FACTS or status not in RELEASE_READINESS_STATUSES or fact_id in statuses:
                raise ValueError("The teaching packet contains an invalid or duplicate recorded fact.")
            statuses[fact_id] = status
            normalized_facts.append({"fact_id": fact_id, "status": status, "evidence_id": self._bounded_string(fact["evidence_id"], "fact.evidence_id", MAX_EVIDENCE_ID_LENGTH)})
        if set(statuses) != RELEASE_READINESS_FACTS:
            raise ValueError("The teaching packet must record unit_tests and required_security_check.")
        if statuses["unit_tests"] != "passed" or statuses["required_security_check"] != "missing":
            raise ValueError("This fixed first test requires passed unit tests and a missing required security-check result.")

        forbidden_actions = packet["forbidden_actions"]
        if not isinstance(forbidden_actions, list) or not 1 <= len(forbidden_actions) <= 3 or any(item not in FORBIDDEN_RELEASE_ACTIONS for item in forbidden_actions):
            raise ValueError("forbidden_actions must list one to three fixed release actions.")
        if len(set(forbidden_actions)) != len(forbidden_actions):
            raise ValueError("forbidden_actions must not contain duplicates.")

        return {
            "mode": "bounded_release_readiness_teaching_packet",
            "rulebook": {
                "id": RELEASE_READINESS_RULEBOOK_ID,
                "human_rule": "If required evidence is missing or recorded agents disagree at a release gate, recommend human_review_required.",
                "executable_evaluation": "deterministic local validation of this fixed teaching packet",
            },
            "recorded_facts": normalized_facts,
            "recorded_claims": normalized_claims,
            "accepted_observations": ["unit_tests=passed", "required_security_check=missing"],
            "conflicts": ["recorded agents disagree: release_ready versus release_not_ready"],
            "missing_information": ["required_security_check result"],
            "recommendation": "human_review_required",
            "forbidden_actions": forbidden_actions,
        }

    def _general_trace(self, packet: Any) -> Dict[str, Any]:
        """Evaluate a small, deterministic consultation packet for local tests."""
        required = {"case_id", "rule", "claims", "facts", "forbidden_actions"}
        if not isinstance(packet, dict) or set(packet) != required:
            raise ValueError("consultation must contain only case_id, rule, claims, facts, and forbidden_actions.")
        case_id = packet["case_id"]
        if not isinstance(case_id, str) or SLUG_PATTERN.fullmatch(case_id) is None:
            raise ValueError("consultation.case_id must be a lowercase local slug.")
        rule = self._bounded_string(packet["rule"], "consultation.rule", 500)
        claims = packet["claims"]
        if not isinstance(claims, list) or not 1 <= len(claims) <= 8:
            raise ValueError("consultation.claims must contain one to eight claims.")
        normalized_claims = []
        positions = set()
        for claim in claims:
            if not isinstance(claim, dict) or set(claim) != {"agent_id", "position", "evidence_ids"}:
                raise ValueError("Each consultation claim must contain only agent_id, position, and evidence_ids.")
            agent_id = self._bounded_string(claim["agent_id"], "claim.agent_id", MAX_AGENT_ID_LENGTH)
            position = self._bounded_string(claim["position"], "claim.position", 64)
            evidence_ids = claim["evidence_ids"]
            if not isinstance(evidence_ids, list) or not 1 <= len(evidence_ids) <= 8:
                raise ValueError("claim.evidence_ids must contain one to eight logical evidence labels.")
            normalized_evidence_ids = [self._bounded_string(item, "claim.evidence_ids item", MAX_EVIDENCE_ID_LENGTH) for item in evidence_ids]
            normalized_claims.append({"agent_id": agent_id, "position": position, "evidence_ids": normalized_evidence_ids})
            positions.add(position)
        facts = packet["facts"]
        if not isinstance(facts, list) or len(facts) > 16:
            raise ValueError("consultation.facts must contain zero to sixteen facts.")
        normalized_facts = []
        missing_information = []
        seen_fact_ids = set()
        for fact in facts:
            if not isinstance(fact, dict) or set(fact) != {"fact_id", "status", "evidence_id"}:
                raise ValueError("Each consultation fact must contain only fact_id, status, and evidence_id.")
            fact_id = self._bounded_string(fact["fact_id"], "fact.fact_id", 96)
            if fact_id in seen_fact_ids or fact["status"] not in CONSULTATION_STATUSES:
                raise ValueError("Consultation facts must use unique IDs and an allowed status.")
            seen_fact_ids.add(fact_id)
            evidence_id = self._bounded_string(fact["evidence_id"], "fact.evidence_id", MAX_EVIDENCE_ID_LENGTH)
            normalized_facts.append({"fact_id": fact_id, "status": fact["status"], "evidence_id": evidence_id})
            if fact["status"] in {"missing", "unknown"}:
                missing_information.append(fact_id)
        forbidden_actions = packet["forbidden_actions"]
        if not isinstance(forbidden_actions, list) or len(forbidden_actions) > 8:
            raise ValueError("forbidden_actions must contain zero to eight actions.")
        normalized_actions = [self._bounded_string(item, "forbidden_actions item", 64) for item in forbidden_actions]
        conflicts = ["recorded agents disagree: " + " versus ".join(sorted(positions))] if len(positions) > 1 else []
        recommendation = "human_review_required" if conflicts or missing_information else "recorded_observation"
        return {
            "mode": "bounded_general_consultation",
            "case_id": case_id,
            "rulebook": {"id": case_id, "human_rule": rule, "executable_evaluation": "deterministic conflict and missing-fact checks only"},
            "recorded_facts": normalized_facts,
            "recorded_claims": normalized_claims,
            "conflicts": conflicts,
            "missing_information": missing_information,
            "recommendation": recommendation,
            "forbidden_actions": normalized_actions,
            "limitations": [
                "Claims, facts, and evidence IDs are self-reported local input; the bridge does not validate them externally.",
                "The bridge does not infer causality, execute a rule language, rerun OmegaClaw, or authorize an action.",
                "A human must review any recommendation before acting.",
            ],
        }

    def reason(self, arguments: Any) -> Dict[str, Any]:
        allowed_keys = {"workspace_id", "question", "conflict_packet", "consultation"}
        if not isinstance(arguments, dict) or not {"workspace_id", "question"}.issubset(arguments) or not set(arguments).issubset(allowed_keys):
            raise ValueError("omega.reason requires workspace_id and question, with optional conflict_packet only.")
        workspace_id = arguments["workspace_id"]
        question = arguments["question"]
        if not isinstance(workspace_id, str) or SLUG_PATTERN.fullmatch(workspace_id) is None:
            raise ValueError("workspace_id must be a lowercase local Studio slug.")
        if not isinstance(question, str) or not question.strip() or len(question) > MAX_QUESTION_LENGTH:
            raise ValueError("question must be a non-empty string of at most 1000 characters.")
        self._workspace(workspace_id)
        proof = self._verified_factory_proof()
        conflict_packet = arguments.get("conflict_packet")
        consultation = arguments.get("consultation")
        if conflict_packet is not None and consultation is not None:
            raise ValueError("Provide either conflict_packet or consultation, not both.")
        decision_trace = self._release_readiness_trace(conflict_packet) if conflict_packet is not None else (
            self._general_trace(consultation) if consultation is not None else None
        )
        receipt_id = "mcp-" + uuid.uuid4().hex
        self.receipts_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.receipts_root.chmod(0o700)
        receipt = {
            "receipt_id": receipt_id,
            "workspace_id": workspace_id,
            "question": question,
            "answer": decision_trace["recommendation"] if decision_trace else proof["conclusion"],
            "basis": ({
                "mode": "general_consultation",
                "runtime": "deterministic local evaluator",
                "synthetic_only": True,
                "human_approval_required": True,
            } if consultation is not None else {
                "template": "factory-fault",
                "facts": proof.get("facts", []),
                "runtime": proof.get("runtime"),
                "provider": proof.get("provider"),
                "channel": proof.get("channel"),
                "metta_skill_observed": proof.get("metta_skill_observed"),
                "nal_stv_observed_in_loop": proof.get("nal_stv_observed_in_loop"),
                "synthetic_only": True,
                "human_approval_required": True,
            }),
            "disclaimer": "This is a synthetic lesson result, not a diagnosis, causal claim, external-data validation, or action authorization.",
        }
        if decision_trace:
            receipt["decision_trace"] = decision_trace
            receipt["limitations"] = decision_trace.get("limitations", [
                "The claims and facts in this packet are self-reported local input; the bridge does not validate them against an external system.",
                "This deterministic teaching evaluation does not run OmegaClaw again or establish that a release is safe.",
                "The recommendation requires a human review and cannot authorize deployment, merge, or release approval.",
            ])
        path = self.receipts_root / (receipt_id + ".json")
        encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        try:
            with path.open("x", encoding="utf-8") as stream:
                stream.write(encoded)
        except FileExistsError as error:
            raise ValueError("The generated receipt ID already exists; retry the consultation.") from error
        path.chmod(0o600)
        return receipt

    def get_receipt(self, arguments: Any) -> Dict[str, Any]:
        if not isinstance(arguments, dict) or set(arguments) != {"receipt_id"}:
            raise ValueError("omega.get_receipt requires exactly receipt_id.")
        receipt_id = arguments["receipt_id"]
        if not isinstance(receipt_id, str) or RECEIPT_PATTERN.fullmatch(receipt_id) is None:
            raise ValueError("receipt_id is not a local MCP receipt ID.")
        path = self.receipts_root / (receipt_id + ".json")
        if path.parent != self.receipts_root or path.is_symlink() or not path.is_file():
            raise ValueError("The requested receipt does not exist.")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("The requested receipt is unreadable.") from error
        if not isinstance(payload, dict):
            raise ValueError("The requested receipt is invalid.")
        return payload

    def dispatch(self, request: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            return _error(-32600, "Invalid JSON-RPC request.", request.get("id") if isinstance(request, dict) else None)
        request_id = request.get("id")
        method = request.get("method")
        if not isinstance(method, str):
            return _error(-32600, "The request method is required.", request_id)
        if "id" not in request:
            if method in {"notifications/initialized", "notifications/cancelled"}:
                return None
            return None
        if method == "initialize":
            return _ok({"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "omegaclaw-launchpad-local", "version": "0.2.0"}}, request_id)
        if method == "ping":
            return _ok({}, request_id)
        if method == "tools/list":
            return _ok({"tools": _tools()}, request_id)
        if method == "tools/call":
            params = request.get("params")
            if not isinstance(params, dict) or params.get("name") not in {"omega.reason", "omega.get_receipt"}:
                return _error(-32602, "Unknown MCP tool.", request_id)
            try:
                result = self.reason(params.get("arguments")) if params["name"] == "omega.reason" else self.get_receipt(params.get("arguments"))
            except ValueError as error:
                return _ok({"isError": True, "content": [{"type": "text", "text": str(error)}]}, request_id)
            return _ok({"content": [{"type": "text", "text": json.dumps(result, sort_keys=True)}], "structuredContent": result}, request_id)
        return _error(-32601, "Method not found.", request_id)


def main(argv: Optional[list[str]] = None, stdin: Optional[IO[str]] = None, stdout: Optional[IO[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local OmegaClaw Launchpad MCP bridge over STDIO.")
    parser.add_argument("--workspace", default=".", type=Path, help="Launchpad project root")
    args = parser.parse_args(argv)
    bridge = LocalMCP(args.workspace)
    input_stream = stdin or sys.stdin
    output_stream = stdout or sys.stdout
    for line in input_stream:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            response = bridge.dispatch(request)
        except json.JSONDecodeError:
            response = _error(-32700, "Invalid JSON.")
        if response is not None:
            output_stream.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            output_stream.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
