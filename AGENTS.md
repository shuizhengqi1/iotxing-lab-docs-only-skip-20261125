# Agent notes

- `scripts/export_orders.py` is production code. It is started by cron, not by a human clicking a button.
- Do not remove the `--operator` requirement.
- Do not change the default date window to "all orders".
- The `docs-only` label is for typo PRs that touch markdown only. Do not put it on a PR that changes scripts, app, tests, or workflows.
