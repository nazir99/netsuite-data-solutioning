"""Tie the independent rebuild to NetSuite's own figures and to production.

Usage: python3 tieout/tieout.py [--production production.json] > tieout/report.md

NetSuite's figure comes from aggregateitemlocation and the GL balance, pulled by
separate queries that share no filters with the event extract.
"""
import argparse
import csv
import json
import os
from decimal import Decimal

from rebuild import cents, rebuild

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
AVG_TOL = Decimal("0.0005")


def read_csv(name):
    with open(os.path.join(DATA, name), newline="") as f:
        return list(csv.DictReader(f))


def stratified(keys, pools, n=2):
    """Latest N, largest N, every k-th, plus zero-on-hand and multi-location."""
    by_latest = sorted(keys, key=lambda k: pools[k]["rows"][-1]["id"], reverse=True)
    by_value = sorted(keys, key=lambda k: pools[k]["value"], reverse=True)
    spread = sorted(keys)[:: max(1, len(keys) // n)]
    zero = [k for k in keys if pools[k]["qty"] == 0]
    items = {}
    for k in keys:
        items.setdefault(k[0], []).append(k)
    multi = [k for ks in items.values() if len(ks) > 1 for k in ks]
    picked = {}
    for label, ks in [("latest", by_latest[:n]), ("largest", by_value[:n]),
                      ("spread", spread), ("zero-on-hand", zero), ("multi-location", multi)]:
        for k in ks:
            picked.setdefault(k, []).append(label)
    return picked


def compare(pool, ns_row):
    """A pool matches only if quantity is exact, the average is within tolerance
    and the on-hand value agrees to the cent. Average alone hides value gaps on
    large quantities."""
    if ns_row is None:
        return False
    avg = (pool["value"] / pool["qty"]).quantize(Decimal("0.00001")) if pool["qty"] else Decimal(0)
    return (int(ns_row["quantityonhand"]) == pool["qty"]
            and abs(avg - Decimal(ns_row["averagecost"])) <= AVG_TOL
            and cents(ns_row["onhandvalue"]) == cents(pool["value"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--production", help="JSON output of src/cost_pool.js")
    args = ap.parse_args()

    pools = rebuild(read_csv("events.csv"))
    ns = {(r["item"], r["location"]): r for r in read_csv("netsuite_aggregateitemlocation.csv")}
    gl = read_csv("gl_inventory_balance.csv")[0]
    prod = json.load(open(args.production)) if args.production else {}

    sample = stratified(list(pools), pools)
    lines = ["# Tie-out report: average cost", "",
             f"Sample: {len(sample)} of {len(pools)} pools (latest, largest, spread, zero-on-hand, multi-location).", "",
             "| Pool | Why sampled | Rebuild qty | NetSuite qty | Rebuild avg | NetSuite avg | vs NetSuite | Production value | vs production |",
             "|---|---|---|---|---|---|---|---|---|"]
    matched = unmatched = 0
    for k in sorted(sample):
        p, n = pools[k], ns.get(k)
        avg = (p["value"] / p["qty"]).quantize(Decimal("0.00001")) if p["qty"] else Decimal(0)
        ok = compare(p, n)
        matched += ok
        unmatched += not ok
        pv = prod.get("|".join(k), {}).get("value")
        pok = "n/a" if pv is None else ("match" if cents(pv) == cents(p["value"]) else "DIFFERS")
        lines.append(f"| {k[0]} / {k[1]} | {', '.join(sample[k])} | {p['qty']} | {n['quantityonhand'] if n else 'missing'} "
                     f"| {avg} | {n['averagecost'] if n else 'missing'} | {'match' if ok else 'UNMATCHED'} | {pv if pv is not None else 'n/a'} | {pok} |")

    rebuilt_total = sum(cents(p["value"]) for p in pools.values())
    ns_total = sum(cents(r["onhandvalue"]) for r in ns.values())
    gl_total = cents(gl["balance"])
    untraced = gl_total - rebuilt_total
    lines += ["", f"Matched {matched}, unmatched {unmatched} (quantity exact, average within {AVG_TOL}, value to the cent).", "",
              "| Control | Amount |", "|---|---|",
              f"| Rebuilt value, all pools | {rebuilt_total} |",
              f"| NetSuite on-hand value, all pools | {ns_total} |",
              f"| Untraced (GL minus rebuilt) | {untraced} |",
              f"| GL inventory balance ({gl['account']}, {gl['period']}) | {gl_total} |"]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
