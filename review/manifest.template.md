# Review manifest

Copy to `review/manifest.md` in the project being reviewed and fill in each path.

## Business rule
<!-- Plain words: what the number means, who uses it, and what it must tie to. -->

## SuiteQL
- `queries/<name>.sql`

## Production logic
- `src/<file>.js`

## Python rebuild
- `tieout/<module>.py`
- Tests: `tieout/test_<module>.py`

## Tie-out report
- `tieout/report.md`
<!-- Sample definition (latest N, largest N, spread), matched, unmatched, totals. -->

## Data
- `data/<extract>.json`
<!-- Local extracts only. Gitignored. Note the account and pull date. -->

## Known limits
<!-- Scenarios already known to be out of scope, so the reviewer does not re-report them. -->
