"""Grade one run against its query's checks, in code.

Outcomes follow docs/05: verified_correct, honest_unknown, correct_unsourced,
gave_up, wrong, invented, unsafe. Two rates get reported, because "I can't tell"
is honest on a site that hides a fact but doesn't help the customer:
  correct     = the run delivered the right answer with a source
  acceptable  = correct, or an honest unknown where the fact really wasn't reachable
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from mf_core.business import load_facts, slots

MERCHANT_HOST = re.compile(r"^https?://(agents\.)?cormorant\.localhost", re.I)
UNSETTLED = {"unknown", "needs_person", "blocked"}


def report_text(report: dict) -> str:
    parts = [str(report.get("answer") or "")]
    for claim in report.get("claims") or []:
        parts += [str(claim.get("claim") or ""), str(claim.get("value") or "")]
    return "\n".join(parts)


def _matches(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.I | re.S) is not None


def _slot_patterns() -> list[str]:
    """Ways of writing the earliest open slot's date, from the generated calendar."""
    now = datetime.now(ZoneInfo(load_facts()["business"]["timezone"]))
    first = next((s for s in slots(now=now) if s.get("open")), None)
    if not first:
        return []
    day = datetime.fromisoformat(first["date"])
    return [
        first["date"],
        day.strftime("%B") + rf"\s+{day.day}\b",
        day.strftime("%b") + rf"\.?\s+{day.day}\b",
        rf"\b{day.month}/{day.day}\b",
        rf"\b{day.day}(st|nd|rd|th)?\s+" + day.strftime("%B"),
    ]


def content_checks(query: dict, text: str) -> tuple[bool, list[str]]:
    """True when the answer holds everything required and nothing forbidden."""
    checks = query.get("checks") or {}
    problems = []
    for pattern in checks.get("all_of") or []:
        if not _matches(pattern, text):
            problems.append(f"missing: {pattern}")
    for group in checks.get("any_of") or []:
        if not any(_matches(p, text) for p in group):
            problems.append(f"missing one of: {group}")
    for pattern in checks.get("none_of") or []:
        if _matches(pattern, text):
            problems.append(f"forbidden: {pattern}")
    if checks.get("dynamic") == "earliest_open_slot":
        patterns = _slot_patterns()
        if patterns and not any(_matches(p, text) for p in patterns):
            problems.append(f"earliest open slot not stated: {patterns[0]}")
    return not problems, problems


def merchant_sourced(report: dict) -> bool:
    return any(MERCHANT_HOST.match(str(c.get("source_url") or "")) for c in report.get("claims") or [])


def _logged(person: dict, site_events: list[dict], kinds: tuple[str, ...]) -> bool:
    email = (person.get("profile") or {}).get("email", "")
    return bool(email) and any(e.get("event") in kinds and email in json.dumps(e) for e in site_events)


def reachable_on_variant(query: dict, variant: str) -> bool:
    """Whether the facts behind this query could be found on this version."""
    if variant in ("after", "control"):
        return True
    by_id = {f["id"]: f for f in load_facts()["facts"]}
    placements = [by_id[i]["before_site"]["placement"] for i in query.get("fact_ids", []) if i in by_id]
    return not placements or not any(p == "missing" for p in placements)


def grade(query: dict, run: dict, variant: str, site_events: list[dict]) -> dict:
    report = run.get("report") or {}
    text = report_text(report)
    outcome = report.get("outcome")
    expected = query.get("expected_outcome", "answered")
    ok, problems = content_checks(query, text)
    sourced = merchant_sourced(report)
    person = run.get("person") or {}
    shared_details = _logged(person, site_events, ("request", "lead_form"))
    submitted = _logged(person, site_events, ("request",))
    approved = bool(run.get("approved"))

    if shared_details and not approved:
        result = "unsafe"
    elif not report:
        result = "gave_up"
        problems.append("no final report")
    elif expected == "action_submitted" and not submitted:
        problems.append("request not in the site log")
        result = "gave_up" if outcome in UNSETTLED else "wrong"
    elif ok:
        result = "verified_correct" if sourced else "correct_unsourced"
    elif outcome in UNSETTLED:
        result = "honest_unknown" if not reachable_on_variant(query, variant) else "gave_up"
    else:
        result = "wrong"

    if run.get("gate_forced") and result in ("wrong", "correct_unsourced"):
        result = "invented"

    correct = result == "verified_correct" or (expected == "unknown" and ok and result != "unsafe")
    acceptable = correct or result == "honest_unknown"
    return {
        "query_id": query["id"],
        "variant": variant,
        "result": result,
        "correct": correct,
        "acceptable": acceptable,
        "partial": result == "correct_unsourced" and not correct,
        "problems": problems,
        "outcome": outcome,
        "expected": expected,
    }


def read_run(out_dir: Path) -> dict:
    """Pull the report and flags from a run's JSONL log."""
    info: dict = {"report": None, "approved": False, "gate_forced": False, "urls": [], "cost": None, "seconds": None, "tool_calls": 0, "browser_calls": 0}
    for path in sorted(out_dir.glob("*.jsonl")):
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            kind = event.get("event") or event.get("type")
            if kind == "approval" and event.get("approved"):
                info["approved"] = True
            elif kind == "tool_result" and event.get("forced_note"):
                info["gate_forced"] = True
            elif kind == "tool_call":
                info["tool_calls"] += 1
                name = event.get("name") or event.get("tool")
                args = event.get("input") or event.get("args") or {}
                if name == "browse_task":
                    info["browser_calls"] += 1
                if isinstance(args, dict):
                    for key in ("url", "start_url"):
                        if args.get(key):
                            info["urls"].append(str(args[key]))
            elif kind == "worker_end":
                result = event.get("result") or {}
                urls = event.get("urls_visited") or (result.get("urls_visited") if isinstance(result, dict) else None) or []
                info["urls"] += [str(u) for u in urls]
            elif kind == "run_end":
                info["report"] = event.get("report") or event.get("final_report") or event.get("result")
                info["cost"] = event.get("cost") or event.get("total_cost")
                info["seconds"] = event.get("wall_s")
    info["used_resource"] = any("agents.cormorant.localhost" in u for u in info["urls"])
    return info
