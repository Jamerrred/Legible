# Run logs

This is the raw evidence behind the [benchmark report](../reports/first-demo-benchmark.md). Don't edit these by hand.

| Folder | What's in it |
|---|---|
| `first-demo/before`, `after`, `control` | One folder per valid run, with its JSONL log and the fake person it acted for |
| `first-demo/results_*.json` | Graded results for each version, which the report's numbers come from |
| `first-demo/site-logs/` | What each server logged during the benchmark. A re-grade reads these |
| `first-demo/console_*.txt` | Each version's printed summary from the final grading |
| `first-demo/attempt-1-credit-failure/` | Results from the first attempt, which hit OpenRouter's credit limit. Not used in any number |
| `first-demo/invalid-runs/` | Logs of "before" runs the API refused. Not used in any number |
| `pre-freeze-control-check/` | Sample-query runs on the control page, used to find general agent bugs before the freeze. Not part of the benchmark |

Each run's contact details are fake, and browser histories are git-ignored.
