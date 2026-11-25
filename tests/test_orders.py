from app.orders import list_orders


def test_fixture_has_four_orders():
    assert len(list_orders()) == 4


def test_total_amount_cents():
    assert sum(o.amount_cents for o in list_orders()) == 12800 + 5600 + 9900 + 250000
