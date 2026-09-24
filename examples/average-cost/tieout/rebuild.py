"""Independent rebuild of a per-location running average cost.

Written from the business rule in ../README.md, not from src/cost_pool.js.
If you find yourself reading the production code to write this file, stop:
agreement between two copies of one idea proves nothing.
"""
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")

# Same-day order: stock in first, then receipts and builds, then outbound,
# customer returns last. Ties break on the created timestamp, then id.
DAY_ORDER = {"InvAdjst": 1, "ItemRcpt": 2, "Build": 2, "LandedCost": 2, "ItemShip": 3, "RtnAuth": 4}


def cents(x):
    return Decimal(x).quantize(CENT, ROUND_HALF_UP)


def sort_key(e):
    return (e["trandate"], DAY_ORDER[e["type"]], e["created"], int(e["id"]))


def rebuild(events):
    """Return {(item, location): {"qty", "value", "rows"}} from raw events."""
    by_pool = defaultdict(list)
    for e in events:
        by_pool[(e["item"], e["location"])].append(e)

    pools = {}
    for key, evs in by_pool.items():
        qty, value, last_avg, rows = 0, Decimal(0), Decimal(0), []
        for e in sorted(evs, key=sort_key):
            q = int(e["quantity"])
            avg = value / qty if qty > 0 else last_avg
            if q > 0 and e["type"] != "RtnAuth":
                change = cents(e["amount"])          # inbound at its own cost
            elif q == 0:
                change = cents(e["amount"])          # value-only row (landed cost)
            else:
                change = cents(q * avg)              # outbound and returns at running average
            qty += q
            value += change
            if qty == 0:
                value = Decimal(0)                   # pool resets when empty
            if qty > 0:
                last_avg = value / qty
            rows.append({"id": e["id"], "qty": qty, "value": value})
        pools[key] = {"qty": qty, "value": value, "rows": rows}
    return pools
