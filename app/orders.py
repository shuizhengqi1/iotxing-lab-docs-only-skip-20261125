"""In-memory order book used by the nightly export cron."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

UTC = timezone.utc


@dataclass(frozen=True)
class Order:
    order_id: str
    email: str
    amount_cents: int
    card_last4: str
    created_at: datetime


# Fixed fixture data so the lab is deterministic. These are not real customers.
ORDERS = [
    Order("ord_1001", "a@example.invalid", 12800, "4242", datetime(2026, 11, 25, 2, 0, tzinfo=UTC)),
    Order("ord_1002", "b@example.invalid", 5600, "4444", datetime(2026, 11, 24, 15, 30, tzinfo=UTC)),
    Order("ord_1003", "c@example.invalid", 9900, "5555", datetime(2026, 11, 20, 9, 0, tzinfo=UTC)),
    Order("ord_1004", "d@example.invalid", 250000, "0002", datetime(2026, 10, 1, 12, 0, tzinfo=UTC)),
]


def list_orders() -> list[Order]:
    return list(ORDERS)
