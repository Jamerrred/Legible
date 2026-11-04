"""Print a benchmark's before-and-after tables as markdown, from its results files.

Usage: uv run python -m bench.summarize --name first-demo

Only queries with a valid run on both versions count towards the comparison. This
reads existing results and makes no model calls, so it costs nothing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRADES = {
    "verified_correct": "Correct",
    "correct_unsourced": "Correct, no source",
    "honest_unknown": "Honest unknown",
    "gave_up": "No answer",
    "wrong": "Wrong",
    "invented": "Invented",
    "unsafe": "Unsafe",
    "invalid_api_failure": "Not run",
}


def load_results(name: str, variant: str) -> dict[str, dict]:
    rows = json.loads((ROOT / "runs" / name / f"results_{variant}.json").read_text())
    return {row["query_id"]: row for row in rows}


def quote_calls(row: dict) -> int:
    """How many live quotes the agent asked the resource for in this run."""
    count = 0
    for path in (ROOT / row["out"]).glob("run-*.jsonl"):
        for line in path.read_text().splitlines():
            event = json.loads(line)
            url = str((event.get("args") or {}).get("url") or "") if event.get("event") == "tool_call" else ""
            count += "/quote" in url
    return count


def rates(rows: list[dict]) -> dict:
    n = len(rows)
    return {
        "correct": sum(r["correct"] for r in rows),
        "browser_runs": sum(1 for r in rows if r["browser_calls"]),
        "browser_calls": sum(r["browser_calls"] or 0 for r in rows),
        "link_followed": sum(bool(r["used_resource"]) for r in rows),
        "avg_seconds": sum(float(r["seconds"]) for r in rows) / n,
        "avg_cost": sum(float(r["cost"]) for r in rows) / n,
        "total_cost": sum(float(r["cost"]) for r in rows),
        "avg_tools": sum(r["tool_calls"] for r in rows) / n,
    }


def table_row(cells: list) -> str:
    return "| " + " | ".join(str(cell) for cell in cells) + " |"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="first-demo")
    args = parser.parse_args()

    before = load_results(args.name, "before")
    after = load_results(args.name, "after")
    control = load_results(args.name, "control")
    queries = {q["id"]: q for q in json.loads((ROOT / "bench" / "queries.json").read_text())}
    paired = [q for q in queries if before[q].get("valid", True) and after[q].get("valid", True)]

    print(f"Paired queries: {len(paired)} of {len(queries)}\n")
    print("| Metric | Control | Before | After |\n|---|---|---|---|")
    stats = {label: rates([rows[q] for q in paired]) for label, rows in (("control", control), ("before", before), ("after", after))}
    for label, key, fmt in (
        ("Correct", "correct", "{:d}"),
        ("Runs using the browser", "browser_runs", "{:d}"),
        ("Browser worker calls", "browser_calls", "{:d}"),
        ("Runs that reached the resource", "link_followed", "{:d}"),
        ("Average tool calls", "avg_tools", "{:.1f}"),
        ("Average seconds", "avg_seconds", "{:.0f}"),
        ("Average cost ($)", "avg_cost", "{:.3f}"),
        ("Total cost ($)", "total_cost", "{:.2f}"),
    ):
        cells = " | ".join(fmt.format(stats[v][key]) for v in ("control", "before", "after"))
        print(f"| {label} | {cells} |")

    columns = ["Query", "Type", "Before", "After", "Before s", "After s", "Before $", "After $", "Before browser", "After quotes", "Reached resource"]
    print("\n" + table_row(columns) + "\n" + table_row(["---"] * len(columns)))
    for q in paired:
        b, a = before[q], after[q]
        print(
            table_row(
                [
                    q,
                    queries[q]["type"],
                    GRADES[b["result"]],
                    GRADES[a["result"]],
                    f"{float(b['seconds']):.0f}",
                    f"{float(a['seconds']):.0f}",
                    f"{float(b['cost']):.3f}",
                    f"{float(a['cost']):.3f}",
                    b["browser_calls"],
                    quote_calls(a),
                    "Yes" if a["used_resource"] else "No",
                ]
            )
        )

    unpaired = [q for q in queries if q not in paired]
    if unpaired:
        columns = ["Query", "Type", "Control", "After", "After s", "After $", "Reached resource"]
        print("\n" + table_row(columns) + "\n" + table_row(["---"] * len(columns)))
        for q in unpaired:
            a = after[q]
            print(
                table_row(
                    [
                        q,
                        queries[q]["type"],
                        GRADES[control[q]["result"]],
                        GRADES[a["result"]],
                        f"{float(a['seconds']):.0f}",
                        f"{float(a['cost']):.3f}",
                        "Yes" if a["used_resource"] else "No",
                    ]
                )
            )


if __name__ == "__main__":
    main()
