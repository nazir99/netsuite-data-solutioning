# Response to review

Reviewer: codex (`codex exec -s read-only`, prompt `review/logic-review.md`)  Round: 1  Findings file: `review/findings.json`

| Finding | Claim | Test | Result | Outcome |
|---|---|---|---|---|
| F1 | Production rounds negative half cents toward zero | `tieout/test_findings.py::test_f1_negative_half_cent_rounds_away_from_zero` | failed on production | open (deliberate) |
| F2 | Rebuild values a return into an emptied pool at the old average | `tieout/test_findings.py::test_f2_return_into_emptied_pool_uses_last_positive_average` | passed | documented |
| F3 | Tie-out matches on quantity and average while value differs | `tieout/test_findings.py::test_f3_value_gap_is_unmatched_even_when_average_is_within_tolerance` | failed before the change, passes after | fixed |

## Fixed
- **F3.** `tieout/tieout.py` now requires the on-hand value to agree to the cent,
  in addition to exact quantity and average within 0.0005 (`compare()`).

## Documented
- **F2.** The rebuild's behaviour is the intended rule: a return into an empty pool
  comes back at the last positive average. The business rule in `README.md` now
  says so. The reviewer was right that the rule did not state it.

## Open
- **F1.** Confirmed defect in `src/cost_pool.js`, kept on purpose so the example has
  something for the tie-out and review to find, alongside the created-time sort and
  the skipped quantity-0 rows. In real work this is fixed before release.

## Status

The rebuild ties to NetSuite on 3 of 3 pools. The production logic does not:

```
SOLUTION: NOT TIED 2
```
