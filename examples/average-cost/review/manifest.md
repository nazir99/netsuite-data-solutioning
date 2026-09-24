# Review manifest

## Business rule
`README.md`, section "Business rule".

## SuiteQL
None in this example; `data/events.csv` stands in for the extract.

## Production logic
- `src/cost_pool.js`

## Python rebuild
- `tieout/rebuild.py`
- Tests: `tieout/test_rebuild.py`

## Tie-out report
- `tieout/report.md` (3 of 3 pools sampled; rebuild matched NetSuite on all 3; production differs on 2)

## Data
- `data/events.csv`, `data/netsuite_aggregateitemlocation.csv`, `data/gl_inventory_balance.csv`
- Synthetic. The NetSuite figures follow the business rule by construction.

## Known limits
- The 25.00 untraced GL difference is a deliberate item-less journal in the synthetic data.
- Negative on-hand pools are not present in the data.
