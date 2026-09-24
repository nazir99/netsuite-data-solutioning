# Writing an independent rebuild

The rebuild exists to disagree with production when production is wrong. It can
only do that if it did not come from production.

## Independence rules

- **Source is the written business rule.** Write it first (SKILL.md step 1). Do not
  open the production SuiteQL or SuiteScript while writing the rebuild.
- **Input is raw rows**, the extracts nsq stored, not production's intermediate
  output and not a query that already aggregates.
- **Different shape on purpose.** If production loops event by event, the rebuild
  can group by pool first; if production joins in SQL, join in Python. Shared
  structure lets shared mistakes through.
- **If you already read the production code**, say so in the manifest and have the
  reviewer judge independence. Do not claim it.
- **A rule found by searching until it matched** (an ordering, a rounding mode) is
  fitted. Confirm it in documentation or the UI, or fit on one slice and tie out
  on another.
- **A rule chosen in advance that the data cannot tell apart from alternatives**
  (several orderings all tie) is not confirmed by the tie-out. Keep it, list it as
  unconfirmed with the one sandbox transaction that would settle it, and say which
  alternatives also tie.

## Mechanics

- Python 3 standard library is enough: `csv`, `json`, `decimal`, `unittest`.
- Money in `Decimal`, rounded half-up to the cent at the point NetSuite posts, not
  at the end.
- Averages kept unrounded internally; compare with a stated tolerance.
- Keep the ledger rows, not just the ending figure, so the tie-out and the reader
  can see the path.
- Deterministic ordering: a full sort key with a final tie-break (usually id).

## Tests

- Hand-worked cases, one per rule in the business rule: expected values worked on
  paper, never produced by running either implementation.
- One test per reviewer finding (see `review-loop.md`).
- Run with `python3 -m unittest`.

See `examples/average-cost/tieout/` for a complete rebuild, tests and tie-out.
