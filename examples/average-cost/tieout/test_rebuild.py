"""Hand-worked cases for the rebuild. Expected values come from the business
rule worked on paper, not from running either implementation."""
import unittest
from decimal import Decimal

from rebuild import rebuild


def ev(i, typ, qty, amount="", date="2026-03-01", created=None):
    return {"id": str(i), "item": "X", "location": "L", "trandate": date,
            "created": created or date + "T09:00:00", "type": typ,
            "quantity": str(qty), "amount": amount}


class RebuildTest(unittest.TestCase):
    def pool(self, events):
        return rebuild(events)[("X", "L")]

    def test_outbound_leaves_at_running_average(self):
        p = self.pool([ev(1, "ItemRcpt", 100, "1000.00"), ev(2, "ItemShip", -40, date="2026-03-02")])
        self.assertEqual((p["qty"], p["value"]), (60, Decimal("600.00")))

    def test_value_only_row_moves_average_not_quantity(self):
        p = self.pool([ev(1, "ItemRcpt", 100, "1000.00"), ev(2, "LandedCost", 0, "60.00", date="2026-03-02")])
        self.assertEqual((p["qty"], p["value"]), (100, Decimal("1060.00")))

    def test_same_day_receipt_before_shipment_even_if_created_later(self):
        p = self.pool([
            ev(1, "ItemRcpt", 10, "100.00"),
            ev(2, "ItemShip", -5, date="2026-03-02", created="2026-03-02T08:00:00"),
            ev(3, "ItemRcpt", 10, "200.00", date="2026-03-02", created="2026-03-02T17:00:00"),
        ])
        # receipt first: 20 units for 300.00 (avg 15), then 5 out at 15 = 75.00
        self.assertEqual((p["qty"], p["value"]), (15, Decimal("225.00")))

    def test_pool_resets_when_empty(self):
        p = self.pool([ev(1, "InvAdjst", 20, "220.00"), ev(2, "ItemShip", -20, date="2026-03-02"),
                       ev(3, "ItemRcpt", 30, "390.00", date="2026-03-03")])
        self.assertEqual((p["qty"], p["value"]), (30, Decimal("390.00")))

    def test_customer_return_comes_back_at_running_average(self):
        p = self.pool([ev(1, "ItemRcpt", 10, "120.00"), ev(2, "RtnAuth", 2, date="2026-03-02")])
        self.assertEqual((p["qty"], p["value"]), (12, Decimal("144.00")))


if __name__ == "__main__":
    unittest.main()
