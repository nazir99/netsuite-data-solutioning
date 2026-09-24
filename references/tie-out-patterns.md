# Tie-out patterns

A tie-out compares your rebuild to a figure you did not produce. It fails if the
two sides can agree for a reason other than both being right.

## Independent source

Pick NetSuite's own figure, pulled by a query that shares **none** of the rebuild's
filters, joins or date logic:

| Rebuilding | Tie to |
|---|---|
| Per-location cost or on-hand | `aggregateitemlocation` quantity and average |
| A GL account movement | The account balance by period, or the trial balance |
| A document's GL impact | That document's own `transactionaccountingline` rows |
| A report the user trusts | That report, exported, as-is |

**No production implementation?** Then there is no rebuild-vs-production column,
and the NetSuite figure is the only real check. Say so in the report.

**Plugs.** If untraced = control - traced, the equation foots by definition. The
evidence is in the control total's independence and in how small and explained
the untraced amount is, not in the footing.

Not independent: a `GROUP BY` of your own rows, a second query with the same
`WHERE`, the production module's output, a figure you tuned the rule to reach.

## Stratified sample

When the population is too large to run in full, sample on purpose:

- **latest N**: current behaviour, recent configuration
- **largest N**: where the money is
- **spread**: every k-th across history, for old behaviour
- **zero on hand**: resets and emptied pools
- **multi-location** (or multi-subsidiary, multi-currency): scope bugs
- any case the reviewer or the business rule names

Record why each row was sampled. Small populations: run all of them.

## The report

- Sample definition and counts.
- Matched, unmatched, and the tolerance for each (cents for money; state it for
  averages and quantities).
- Totals to the cent, and **untraced** as a named row: control total = rebuilt +
  untraced. A number that only ties in total can hide offsetting errors; tie at
  the grain the reader sees.
- Every unmatched row: explained, turned into a rule, turned into a test, or left
  as named untraced with its amount.
- Rebuild vs production as a separate column. Disagreement there is the
  production defect list.
- Account, environment (sandbox) and pull date.

## Checks by calculation type

| Calculation | Checks |
|---|---|
| Running average cost | Rebuilt average vs `aggregateitemlocation` within 0.0005; quantity difference under 0.01; flag posted value differences over one cent and over 0.1% |
| Revaluation impact | Pair debits = credits = the revaluation's own GL; zero unmatched pairs |
| Work order GL flow | WIP from the T-accounts = raw WIP account sum; each document balances; accounts net to zero apart from named exceptions; no unclassified lines; closed orders at zero or residue explained |
| Inventory subledger to GL | stock + in-flight + item-less postings + offsets = GL control within half a cent; every drill-down equals its parent; compare quantity across all stock accounts together |
| Unit cost decomposition | purchased leaves + labour and overhead + close variance and WIP + untraced = unit cost |
| COGS trace | traced + untraced + variance = posted COGS for the document |
