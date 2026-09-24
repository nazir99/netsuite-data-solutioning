"""One test per finding in review/findings.json. A failing test confirms the
finding; a passing one dismisses it. See review/response.md."""
import csv
import io
import json
import os
import subprocess
import unittest
from decimal import Decimal

from rebuild import rebuild
from tieout import compare

HERE = os.path.dirname(os.path.abspath(__file__))
COLS = ["id", "item", "location", "trandate", "created", "type", "quantity", "amount"]


def ev(i, typ, qty, amount, date):
    return dict(zip(COLS, [str(i), "X", "L", date, date + "T09:00:00", typ, str(qty), amount]))


def production(events):
    """Run src/cost_pool.js on the events and return the X/L pool."""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(events)
    path = os.path.join(HERE, "_findings_events.csv")
    with open(path, "w") as f:
        f.write(buf.getvalue())
    try:
        out = subprocess.run(["node", os.path.join(HERE, "..", "src", "cost_pool.js"), path],
                             capture_output=True, text=True, check=True).stdout
    finally:
        os.remove(path)
    return json.loads(out)["X|L"]


class Findings(unittest.TestCase):
    @unittest.expectedFailure  # confirmed production defect, left in on purpose for the example
    def test_f1_negative_half_cent_rounds_away_from_zero(self):
        events = [ev(1, "ItemRcpt", 2, "2.01", "2026-03-01"), ev(2, "ItemShip", -1, "", "2026-03-02")]
        self.assertEqual(rebuild(events)[("X", "L")]["value"], Decimal("1.00"))
        self.assertEqual(production(events)["value"], 1.00)  # production gives 1.01: confirmed

    def test_f2_return_into_emptied_pool_uses_last_positive_average(self):
        events = [ev(1, "ItemRcpt", 10, "100.00", "2026-03-01"), ev(2, "ItemShip", -10, "", "2026-03-02"),
                  ev(3, "RtnAuth", 2, "", "2026-03-03")]
        p = rebuild(events)[("X", "L")]
        self.assertEqual((p["qty"], p["value"]), (2, Decimal("20.00")))

    def test_f3_value_gap_is_unmatched_even_when_average_is_within_tolerance(self):
        pool = {"qty": 100000, "value": Decimal("1000000.00")}
        ns = {"quantityonhand": "100000", "averagecost": "10.00049", "onhandvalue": "1000049.00"}
        self.assertFalse(compare(pool, ns))


if __name__ == "__main__":
    unittest.main()
