"""Real pinned-runtime proof for the synthetic Community Hospital lesson.

This file is copied into the pinned OmegaClaw-Core checkout by the
run-omegaclaw-proof.sh --community-care mode. The facts and conclusion are
fictional; the proof only establishes that the real Test/WebSocket/MeTTa/NAL
path processed this controlled lesson and returned a receipt.
"""

import json
import os
import subprocess
import time
from pathlib import Path

from helpers import Checker, make_prompt, wait_for_skill_call
from ws_helpers import ws_send_prompt


CONTAINER = os.environ.get("OMEGACLAW_CONTAINER", "omegaclaw")
RUN_ROOT = Path(os.environ["LAUNCHPAD_STUDIO_RUN_ROOT"])


def _docker_logs():
    result = subprocess.run(
        ["docker", "logs", CONTAINER], capture_output=True, text=True, check=False
    )
    return (result.stdout or "") + (result.stderr or "")


def _wait_for_reply(ws, needle, timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        _client_seq, text = ws.pop_agent_reply(timeout=max(1, int(deadline - time.time())))
        if text is None:
            break
        if needle in text:
            return text
    return None


def _wait_for_nal_result(marker, timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        lines = [
            line
            for line in _docker_logs().splitlines()
            if "CHARS_SENT:" in line
            and "LAST_SKILL_USE_RESULTS:" in line
            and marker in line
            and "stv" in line
        ]
        if lines:
            return lines[-1]
        time.sleep(2)
    return None


def _write_receipt(run_id, response, nal_log):
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    proof = {
        "schema_version": 1,
        "status": "verified",
        "runtime": "OmegaClaw-Core v0.1.19-dirty",
        "upstream_base_commit": "642c53676cf795cb7a0030823b36018c029b1416",
        "controlled_patches": [
            "limit FAISS build parallelism to 2 (build only)",
            "map Linux POLLRDHUP to POLLHUP on macOS (test harness only)",
        ],
        "provider": "Test",
        "channel": "websocket",
        "template": "community-care",
        "synthetic_only": True,
        "facts": [
            "triage_capacity=observed",
            "patient_consent=missing",
        ],
        "conclusion": "human_review_required",
        "metta_skill_observed": True,
        "nal_stv_observed_in_loop": True,
        "human_approval_still_required": True,
        "response": response,
        "nal_log_excerpt": nal_log[-800:],
    }
    (RUN_ROOT / "omega-proof.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    (RUN_ROOT / "receipt.md").write_text(
        "# Community Hospital receipt - real runtime, synthetic lesson\n\n"
        "**Status:** verified pinned OmegaClaw runtime path; fictional facts only\n\n"
        "## Evidence\n\n"
        "- Provider: Test\n"
        "- Channel: WebSocket\n"
        "- MeTTa skill: observed\n"
        "- NAL/STV in loop: observed\n"
        "- Human approval: still required\n\n"
        "## Synthetic input\n\n"
        "The lesson supplied an observed triage-capacity note, a missing "
        "consent record, and two fictional agent positions.\n\n"
        "## Result\n\n"
        "human_review_required\n\n"
        "The runtime path was real; the data, rule meaning, and conclusion are "
        "not medical advice, a diagnosis, external-data validation, or "
        "authorization for an action.\n\n"
        "## Captured response\n\n"
        "Captured response:\n\n%s\n" % response,
        encoding="utf-8",
    )


def test_launchpad_community_care_uses_real_nal(llm, ws):
    with Checker("Launchpad Community Hospital lesson via real OmegaClaw") as check:
        marker = "launchpad_community_care_%s" % check.run_id
        reply_token = "OMEGACLAW-COMMUNITY-CARE-%s" % check.run_id

        check.step("wait for OmegaClaw WebSocket connection")
        if not ws.wait_for_connection(timeout=60):
            check.fail("connection", "OmegaClaw did not connect to the local WebSocket harness")
        check.ok("connection")
        ws.clear()

        check.step("wait for the OmegaClaw Test provider to connect")
        if not llm.ping(timeout=60):
            check.fail("Test provider", "OmegaClaw did not connect to the local LLM controller")
        check.ok("Test provider")

        prompt = make_prompt(
            check.run_id,
            "Run the Community Hospital teaching lesson using only these fictional facts: "
            "triage_capacity=observed, patient_consent=missing, and two agents "
            "disagree about care routing. Apply the illustrative rule "
            "that derives human_review_required. Use the metta skill "
            "with NAL revision, then send exactly one short response that says "
            "the result is synthetic and still requires human approval.",
        )
        metta_expression = (
            "(|- ((--> %s human_review_required) (stv 1.0 0.9)) "
            "((--> %s human_review_required) (stv 1.0 0.9)))"
            % (marker, marker)
        )
        check.step("register the controlled provider response")
        answer_registered = llm.set_answer(
            prompt,
            '(metta "%s") (send "%s: human_review_required; synthetic facts only; human approval required.")'
            % (metta_expression, reply_token),
        )
        if not answer_registered:
            check.fail("mock answer", "the controlled lesson response was not registered")
        check.ok("mock answer", "controlled lesson response registered")

        check.step("deliver fictional facts through the real WebSocket channel")
        ws_send_prompt(ws, prompt)
        check.ok("delivered")

        check.step("verify OmegaClaw invoked the real metta skill")
        metta_arg = wait_for_skill_call(check.run_id, "metta", timeout=60, arg_substr=marker)
        if metta_arg is None:
            check.fail("metta invoked", "no matching metta skill call was recorded")
        check.ok("metta invoked", metta_arg[:100])

        check.step("verify the NAL/STV result entered the next loop context")
        nal_log = _wait_for_nal_result(marker)
        if nal_log is None:
            check.fail("NAL result", "no stv result reached LAST_SKILL_USE_RESULTS")
        check.ok("NAL result", "stv result captured in the real loop")

        check.step("verify the synthetic result returned through OmegaClaw")
        response = _wait_for_reply(ws, reply_token)
        if response is None:
            check.fail("response", "no OmegaClaw response returned through WebSocket")
        check.ok("response", response)

        _write_receipt(check.run_id, response, nal_log)
        check.done()
