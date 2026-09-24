# Example: per-location running average cost

A small, runnable example of the skill's loop on synthetic data. Nothing here
comes from a real NetSuite account.

## Business rule

For each item and location, keep a running pool of quantity and value from
posting inventory asset lines, and derive the average cost from it.

- A receipt, build or stock-in adjustment adds its own amount.
- A shipment leaves at the running average, rounded to the cent.
- A customer return comes back at the running average; into an empty pool, at
  the last positive average.
- A value-only row (quantity 0, such as landed cost) changes value, not quantity.
- When quantity reaches 0 the pool resets to 0 value.
- Same-day order: stock-in adjustments, then receipts and builds, then
  shipments, then customer returns. Ties break on the created timestamp.
- The ending pool must equal NetSuite's `aggregateitemlocation` quantity and
  average, and the sum of all pools must tie to the inventory GL balance, with
  any gap shown as a named untraced row.

## Files

| Path | What it is |
|---|---|
| `data/events.csv` | The extract (in real work: pulled by nsq, gitignored) |
| `data/netsuite_aggregateitemlocation.csv` | NetSuite's own figure, from a separate query |
| `data/gl_inventory_balance.csv` | The GL control total |
| `src/cost_pool.js` | Production logic under review (it has defects on purpose) |
| `tieout/rebuild.py` | Independent rebuild, written from the rule above |
| `tieout/test_rebuild.py` | Hand-worked cases for the rebuild |
| `tieout/test_findings.py` | One test per reviewer finding |
| `tieout/tieout.py` | Stratified tie-out: rebuild vs NetSuite, rebuild vs production, controls |
| `tieout/report.md` | The report it produced |
| `review/manifest.md` | Inputs for the second-model review |
| `review/findings.json` | What the reviewer returned |
| `review/response.md` | Each finding: fixed, documented or open |

## Run it

```bash
cd tieout && python3 -m unittest test_rebuild test_findings && cd ..
node src/cost_pool.js data/events.csv > /tmp/production.json
python3 tieout/tieout.py --production /tmp/production.json > tieout/report.md
```

The report shows the rebuild matching NetSuite on every sampled pool while the
production logic differs on two of them: the tie-out found the defects, the
production code did not agree with itself into a false pass.
