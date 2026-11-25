import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.export_orders import export_rows

UTC = timezone.utc
NOW = datetime(2026, 11, 25, 8, 0, tzinfo=UTC)
ROOT = Path(__file__).resolve().parents[1]


def test_export_without_operator_raises():
    with pytest.raises(SystemExit, match="--operator is required"):
        export_rows(None, None, None, NOW)


def test_cli_without_operator_exits_2():
    p = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "export_orders.py"), "--now", NOW.isoformat()],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert p.returncode == 2
    assert "--operator is required" in p.stderr
    assert p.stdout == ""


def test_default_window_is_last_24_hours():
    operator, start, end, rows = export_rows("cron", None, None, NOW)
    assert operator == "cron"
    assert start == datetime(2026, 11, 24, 8, 0, tzinfo=UTC)
    assert end == NOW
    ids = [r.order_id for r in rows]
    assert ids == ["ord_1001", "ord_1002"]
    assert sum(r.amount_cents for r in rows) == 12800 + 5600


def test_explicit_range_can_include_older_orders():
    _, _, _, rows = export_rows("finance", "2026-10-01", "2026-11-25T08:00:00+00:00", NOW)
    assert [r.order_id for r in rows] == ["ord_1001", "ord_1002", "ord_1003", "ord_1004"]
