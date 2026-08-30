"""Pinned-runtime proof for The Lighthouse in the Fog.

The LLM response is deterministic, but the OmegaClaw loop, WebSocket channel,
memory skills, controlled file read, MeTTa skill, NAL result, restart, and
response path are real.
"""

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

from helpers import Checker, find_skill_calls, make_prompt, wait_for_skill_call
from ws_helpers import ws_send_prompt


CONTAINER = os.environ.get("OMEGACLAW_CONTAINER", "omegaclaw")
RUN_ROOT = Path(os.environ["LAUNCHPAD_STUDIO_RUN_ROOT"])
EXAMPLE_ROOT = Path(os.environ["LAUNCHPAD_LIGHTHOUSE_EXAMPLE_ROOT"])
BULLETIN_CONTAINER_PATH = "/PeTTa/repos/OmegaClaw-Core/memory/launchpad-lighthouse-bulletin.txt"


def _docker(*args):
    return subprocess.run(["docker", *args], capture_output=True, text=True, check=False)


def _docker_logs():
    result = _docker("logs", CONTAINER)
    return (result.stdout or "") + (result.stderr or "")


def _wait_for_reply(ws, needle, timeout=90):
    deadline = time.time() + timeout
    while time.time() < deadline:
        _client_seq, text = ws.pop_agent_reply(timeout=max(1, int(deadline - time.time())))
        if text is None:
            break
        if needle in text:
            return text
    return None


def _wait_for_result(needle, *, require_stv=False, timeout=90):
    deadline = time.time() + timeout
    while time.time() < deadline:
        lines = [
            line for line in _docker_logs().splitlines()
            if "LAST_SKILL_USE_RESULTS:" in line and needle in line
        ]
        if require_stv:
            lines = [line for line in lines if "stv" in line]
        if lines:
            return lines[-1]
        time.sleep(2)
    return None


def _copy_bulletin():
    source = EXAMPLE_ROOT / "runtime-bulletin.txt"
    return _docker("cp", str(source), "%s:%s" % (CONTAINER, BULLETIN_CONTAINER_PATH))


def _acknowledge_delivered_messages(ws):
    """Keep the mock server from replaying an already-processed prompt.

    The real chat service would retire an acknowledged input. The upstream
    test driver intentionally keeps every sent frame so it can exercise
    reconnect/dedup behaviour, but a container restart resets the channel's
    in-memory ``last_seen_seq``. Clearing only the driver's delivered-frame
    list after the observed remember call prevents an artificial reseed and
    makes the post-restart query a genuine persistence check.
    """
    with ws._lock:
        ws._sent.clear()


def _write_evidence(response, initial_log, revised_log, reasoning_hash):
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    receipt = (
        "# The Lighthouse in the Fog — verified runtime receipt\n\n"
        "**Status:** verified pinned OmegaClaw runtime path; fictional facts only\n\n"
        "## Observed path\n\n"
        "- Test provider and WebSocket channel\n"
        "- continuous OmegaClaw loop\n"
        "- remember, container restart, and query using the same memory volume\n"
        "- controlled read-file of the local harbor bulletin\n"
        "- MeTTa skill and NAL/STV result in the next loop context\n"
        "- response returned through the real channel\n\n"
        "## Result\n\n"
        "`north_route_supported_for_human_review`\n\n"
        "No route was activated, no boat was steered, and no external message was sent. "
        "A person still decides. The fixture does not validate the outside world.\n\n"
        "## Captured response\n\n%s\n" % response
    )
    receipt_path = RUN_ROOT / "receipt.md"
    receipt_path.write_text(receipt, encoding="utf-8")
    receipt_hash = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    proof = {
        "schema_version": 2,
        "status": "verified",
        "runtime": "OmegaClaw-Core v0.1.19-dirty",
        "upstream_base_commit": "642c53676cf795cb7a0030823b36018c029b1416",
        "provider": "Test",
        "channel": "websocket",
        "scenario": "lighthouse-in-the-fog",
        "synthetic_only": True,
        "loop_observed": True,
        "remember_observed": True,
        "restart_observed": True,
        "query_after_restart_observed": True,
        "tool_skill_observed": True,
        "tool_source": "controlled-local-read-only-file:runtime-bulletin.txt",
        "reasoning_sha256": reasoning_hash,
        "metta_skill_observed": True,
        "nal_stv_observed_in_loop": True,
        "initial_stv_log_excerpt": initial_log[-700:],
        "revised_stv_log_excerpt": revised_log[-700:],
        "conclusion": "north_route_supported_for_human_review",
        "response_observed": True,
        "response": response,
        "human_approval_still_required": True,
        "external_actions": [],
        "receipt_sha256": receipt_hash,
    }
    (RUN_ROOT / "omega-proof.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")


def test_launchpad_lighthouse_core_path(llm, ws):
    with Checker("Launchpad Lighthouse via real OmegaClaw") as check:
        marker = "LIGHTHOUSE-%s" % check.run_id
        check.add_cleanup_marker(marker)

        check.step("wait for OmegaClaw WebSocket and Test provider")
        if not ws.wait_for_connection(timeout=90):
            check.fail("connection", "OmegaClaw did not connect")
        if not llm.ping(timeout=90):
            check.fail("Test provider", "OmegaClaw did not connect to the Test controller")
        check.ok("connection and loop")
        ws.clear()

        seed_id = check.run_id
        seed_prompt = make_prompt(seed_id, "Remember yesterday's Lighthouse driftwood report exactly.")
        llm.set_answer(seed_prompt, '(pin "%s current goal: verify the harbor route") (remember "%s yesterday: driftwood was reported near the north route") (send "Lighthouse log saved.")' % (marker, marker))
        check.step("deliver and observe working plus persistent memory")
        ws_send_prompt(ws, seed_prompt)
        if wait_for_skill_call(seed_id, "remember", timeout=90, arg_substr=marker) is None:
            check.fail("remember", "the remember skill was not observed")
        if wait_for_skill_call(seed_id, "pin", timeout=90, arg_substr=marker) is None:
            check.fail("pin", "the pin skill was not observed")
        check.ok("remember and pin")
        time.sleep(8)
        _acknowledge_delivered_messages(ws)

        check.step("restart the same OmegaClaw container and memory volume")
        ws.clear()
        resume_before = ws.resume_count()
        restarted = _docker("restart", CONTAINER)
        if restarted.returncode != 0:
            check.fail("restart", restarted.stderr[-300:])
        if not ws.wait_for_connection(timeout=120):
            check.fail("restart connection", "OmegaClaw did not reconnect after restart")
        ws.wait_for_resume(min_count=resume_before + 1, timeout=120)
        if ws.resume_count() < resume_before + 1:
            check.fail("restart resume", "OmegaClaw did not send a fresh resume frame after restart")
        if not llm.ping(timeout=120):
            check.fail("restart provider", "Test provider did not reconnect after restart")
        check.ok("restart", "same named container and memory volume")

        recall_id = check.run_id + 1
        recall_prompt = make_prompt(recall_id, "Use query to recall yesterday's Lighthouse driftwood report.")
        llm.set_answer(recall_prompt, '(query "%s driftwood north route") (send "I queried the saved Lighthouse log.")' % marker)
        check.step("query memory after restart")
        ws_send_prompt(ws, recall_prompt)
        if wait_for_skill_call(recall_id, "query", timeout=90, arg_substr=marker) is None:
            check.fail("query", "the query skill was not observed after restart")
        if _wait_for_result(marker, timeout=120) is None:
            check.fail("query result", "the remembered marker did not return to the loop context")
        check.ok("query after restart")

        check.step("copy and read the controlled harbor bulletin")
        copied = _copy_bulletin()
        if copied.returncode != 0:
            check.fail("bulletin copy", (copied.stdout + copied.stderr)[-500:])
        readable = _docker(
            "exec", CONTAINER, "grep", "-F",
            "observation=north_buoy_operational", BULLETIN_CONTAINER_PATH,
        )
        if readable.returncode != 0:
            detail = (readable.stdout + readable.stderr).strip() or "no output"
            check.fail("bulletin copy", "controlled runtime bulletin unreadable: %s" % detail[-500:])
        tool_id = check.run_id + 2
        tool_prompt = make_prompt(tool_id, "Read the controlled Lighthouse harbor bulletin.")
        llm.set_answer(tool_prompt, '(read-file "%s") (send "Controlled harbor bulletin read.")' % BULLETIN_CONTAINER_PATH)
        ws_send_prompt(ws, tool_prompt)
        if wait_for_skill_call(tool_id, "read-file", timeout=90, arg_substr="lighthouse-bulletin") is None:
            check.fail("read-file", "the controlled file skill was not observed")
        if _wait_for_result("north_buoy_operational", timeout=120) is None:
            check.fail("bulletin result", "the bulletin did not return to the loop context")
        check.ok("controlled file tool")

        initial_atom = "%s_initial" % marker.replace("-", "_")
        initial_id = check.run_id + 3
        initial_prompt = make_prompt(initial_id, "Use NAL revision on the two conflicting north-route reports.")
        initial_expr = "(|- ((--> %s clear) (stv 0.95 0.75)) ((--> %s clear) (stv 0.15 0.75)))" % (initial_atom, initial_atom)
        llm.set_answer(initial_prompt, '(metta "%s") (send "Initial evidence conflicts; gather more evidence.")' % initial_expr)
        check.step("run the initial conflicting NAL calculation")
        ws_send_prompt(ws, initial_prompt)
        if wait_for_skill_call(initial_id, "metta", timeout=90, arg_substr=initial_atom) is None:
            check.fail("initial metta", "the initial MeTTa call was not observed")
        initial_log = _wait_for_result(initial_atom, require_stv=True, timeout=120)
        if initial_log is None:
            check.fail("initial STV", "the initial STV did not reach the next loop context")
        check.ok("initial NAL/STV")

        revised_atom = "%s_revised" % marker.replace("-", "_")
        revised_id = check.run_id + 4
        reply_token = "OMEGACLAW-LIGHTHOUSE-%s" % check.run_id
        revised_prompt = make_prompt(revised_id, "Add the two current identified confirmations, recalculate with NAL, and explain the supervised result.")
        revised_expr = "(|- ((--> %s clear) (stv 1.0 0.95)) ((--> %s clear) (stv 1.0 0.90)))" % (revised_atom, revised_atom)
        llm.set_answer(revised_prompt, '(metta "%s") (send "%s: north_route_supported_for_human_review; sources recorded; no route activated; human decides.")' % (revised_expr, reply_token))
        check.step("run the revised NAL calculation and return the explanation")
        ws_send_prompt(ws, revised_prompt)
        if wait_for_skill_call(revised_id, "metta", timeout=90, arg_substr=revised_atom) is None:
            check.fail("revised metta", "the revised MeTTa call was not observed")
        revised_log = _wait_for_result(revised_atom, require_stv=True, timeout=120)
        if revised_log is None:
            check.fail("revised STV", "the revised STV did not reach the next loop context")
        response = _wait_for_reply(ws, reply_token, timeout=120)
        if response is None:
            calls = find_skill_calls(revised_id, "send") or []
            check.fail("response", "no matching WebSocket response; send calls=%r" % calls[:2])
        check.ok("response", response)

        reasoning_hash = hashlib.sha256((EXAMPLE_ROOT / "reasoning.metta").read_bytes()).hexdigest()
        _write_evidence(response, initial_log, revised_log, reasoning_hash)
        check.done()
