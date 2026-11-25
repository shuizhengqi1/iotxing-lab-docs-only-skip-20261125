#!/usr/bin/env python3
"""Export orders to CSV for the nightly reconciliation job.

Production cron must pass --operator and a date range. The default range is
the last 24 hours, so a typo in the wrapper cannot dump the full ledger.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.orders import list_orders  # noqa: E402

UTC = timezone.utc


def parse_when(value: str) -> datetime:
    if len(value) == 10:
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Export orders to CSV")
    p.add_argument("--operator", default=os.environ.get("EXPORT_OPERATOR"), help="name of the person or job running the export")
    p.add_argument("--from", dest="from_ts", default=None, help="inclusive start (UTC)")
    p.add_argument("--to", dest="to_ts", default=None, help="inclusive end (UTC)")
    p.add_argument("--out", default="-", help="output path, or - for stdout")
    p.add_argument("--now", default=None, help="override current time for tests (ISO UTC)")
    return p


def default_window(now: datetime) -> tuple[datetime, datetime]:
    return now - timedelta(hours=24), now


def export_rows(operator: str | None, from_ts: str | None, to_ts: str | None, now: datetime):
    if not operator:
        raise SystemExit("error: --operator is required")
    start, end = default_window(now)
    if from_ts:
        start = parse_when(from_ts)
    if to_ts:
        end = parse_when(to_ts)
    rows = [o for o in list_orders() if start <= o.created_at <= end]
    return operator, start, end, rows


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    now = parse_when(args.now) if args.now else datetime.now(UTC)
    try:
        operator, start, end, rows = export_rows(args.operator, args.from_ts, args.to_ts, now)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2
    fieldnames = ["order_id", "email", "amount_cents", "card_last4", "created_at", "exported_by"]
    out_fp = sys.stdout if args.out == "-" else open(args.out, "w", newline="")
    close = args.out != "-"
    try:
        w = csv.DictWriter(out_fp, fieldnames=fieldnames)
        w.writeheader()
        for o in rows:
            w.writerow(
                {
                    "order_id": o.order_id,
                    "email": o.email,
                    "amount_cents": o.amount_cents,
                    "card_last4": o.card_last4,
                    "created_at": o.created_at.isoformat(),
                    "exported_by": operator,
                }
            )
    finally:
        if close:
            out_fp.close()
    print("exported %d orders for %s from %s to %s" % (len(rows), operator, start.isoformat(), end.isoformat()), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
