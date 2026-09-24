---
name: netsuite-data-solutioning
description: Use when designing or checking logic built on NetSuite data (cost ledgers, COGS traces, allocations, roll-ups, reconciliations, GL tie-outs), when asked to prove a NetSuite calculation is right, sign off or validate one, or when a harness, Suitelet or report "matches NetSuite" and someone wants to ship it.
---

# NetSuite data solutioning: prove the logic before anyone sees it

The step after the data is pulled. You design logic on NetSuite data, rebuild it
independently in Python, tie it out against NetSuite's own figures, and have a
second model try to break it. Starts only after nsq reported `NSQ: VERIFIED`;
getting the data is nsq's job, not this skill's.

**Violating the letter of these rules is violating the spirit of them.**

## Guardrails (non-negotiable)

1. **The rebuild comes from the business rule, never from the code.** Write the
   rule down in plain words first, then write Python from the rule. Do not read the
   production SuiteQL or SuiteScript while writing it. A harness that runs the
   production module is a **regression test, not a tie-out**, however many records
   pass.
2. **Never fit the rule to the figure you tie to.** If you discover a rule (an
   ordering, a rounding, a split) by searching until it matches NetSuite, that
   match is not evidence. Confirm the rule from documentation or the NetSuite UI,
   or fit it on one slice and tie out on a different slice you did not look at.
3. **Tie to NetSuite's own figure, from a query that shares none of your filters,**
   over a stratified sample. Report matched, unmatched and totals to the cent, with
   anything you cannot explain as a named **untraced** row. An untraced amount
   computed as "control minus traced" makes the footing true by construction; it
   only counts if the control total is independent. If you cannot show where the
   tie figure came from, the result is `NOT TIED`. Details:
   `references/tie-out-patterns.md`.
4. **A second model reviews before you call anything tied.** Run the review loop
   in `references/review-loop.md`: Codex read-only, or a fresh subagent if Codex
   is not installed or fails (usage limit, error). Every finding becomes a test. No reviewer available means
   `UNREVIEWED`, not tied.
5. **Sandbox only, read-only, through nsq.** Never production data for this work.
   Nothing you build here writes to NetSuite.

| Excuse | Reality |
|---|---|
| "200/200 ok against NetSuite's numbers" | If the harness called production code, it proved the code agrees with itself. |
| "A corrected version matches all of them" | A version you tuned until it matched was fitted, not tested. Hold out a slice. |
| "I worked the rule out from this data" | Then the data cannot also prove it. Confirm in docs or the UI. |
| "No independent reviewer, as instructed" | Nobody instructs that. The review is part of the job, not an extra. |
| "Don't gold-plate it, they need it this afternoon" | Then report `UNREVIEWED` or `NOT TIED`. Fast and labelled beats fast and wrong. |
| "The Python is a separate version, so it's independent" | Separate files by the same author in the same pass, after reading the code, is a translation. |
| "Every row foots, so it's tied" | If untraced is the plug, it foots by definition. Is the control figure independent? |
| "Codex is out of credits, so it's unreviewed" | Use the fresh-subagent reviewer. `UNREVIEWED` is for when no reviewer can run at all. |
| "The total ties" | Location errors cancel in a total. Tie at the grain the reader will see. |

## Workflow

1. **Write the business rule** in plain words: what the number means, its grain,
   what it must tie to, and each judgement call (who decided it). Anything you
   cannot confirm, such as a unit or an ordering, is marked unconfirmed with how
   to check it in the NetSuite UI.
2. **Design the chain and allocations** with `references/chaining-and-allocation.md`
   when the logic crosses records (invoice to lot to work order, BOM roll-up, GL
   line to source).
3. **Rebuild in Python** from step 1 with `references/python-rebuild.md`: raw
   extracts in, `Decimal` money, hand-worked unit tests whose expected values come
   from paper, not from running either implementation. A runnable example lives
   in `examples/average-cost/`.
4. **Tie out** (guardrail 3). Compare rebuild to NetSuite, and rebuild to
   production. Every unmatched row is explained or becomes a rule, a test or a
   named untraced amount.
5. **Review** (guardrail 4) with `review/`. At most two rounds. Write
   `review/response.md`: each finding fixed, documented or open.
6. Only then build the Suitelet, feed or deliverable. Keep the tie-out report and
   the response as its evidence.

## Output contract

End every solutioning task with one line a pipeline can read:

```
SOLUTION: TIED | NOT TIED <n unmatched | no tie-out> | UNREVIEWED <reason>
```

`TIED` requires an independent rebuild, a tie-out with zero unexplained unmatched
rows, and a finished review loop with no open high findings. Anything less is
`NOT TIED` or `UNREVIEWED`, and a sign-off note must say which. No independent
tie-out at all (only a harness, or no data) is `NOT TIED no tie-out`, even when a
review ran; `UNREVIEWED` means the tie-out exists but the review loop does not.
An extract row that NetSuite's figure does not reflect counts as unmatched, the
same as a pool that differs.

## References (load when needed)

- `references/chaining-and-allocation.md`: walking document chains, allocating fan-outs, roll-up rules
- `references/tie-out-patterns.md`: independent sources, stratified samples, the report, checks per calculation type
- `references/python-rebuild.md`: how to write a rebuild that is actually independent
- `references/review-loop.md`: running Codex or a subagent reviewer, findings to tests, the response doc
- `review/`: the reviewer prompt, findings schema, manifest and response templates
