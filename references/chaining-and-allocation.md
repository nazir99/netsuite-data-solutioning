# Chaining and allocation

How to walk from one NetSuite record to the next and how to split amounts when
the chain fans out. Join keys and query syntax are nsq's references; this file
is about the logic you build on the rows.

## Walking a chain

1. **Walk by frontier.** One `IN`-list query per level, not one query per record.
   Keep a visited set at the natural grain: item for a BOM, lot and item for lot
   genealogy, work order for supply.
2. **`transactionline.createdfrom` is the spine.** `nexttransactionlink` is the
   header-level fallback (work order to revaluation, invoice to payment).
   **Measure the keyed share first**: count lines with and without the link for
   the type you rely on. Then fall back to matching on item + location + quantity
   + direction + date, and check for ambiguity (two candidates, same quantity).
3. **Lot detail joins on both keys** (document and line). Negative quantity means
   consumed, positive means created. The maker of a lot is the completion's
   mainline; its `createdfrom` is the work order.
4. **Money comes from `transactionaccountingline`**: posting only, one accounting
   book, period by end date, joined to lines on `transactionline.id`.
5. **Fetch rows first, then history for the survivors.** Pick the latest value on
   or before a date in code, not in a correlated subquery.
6. **When SuiteQL refuses a shape, flatten and join in code.** Put fragile columns
   in their own guarded query.
7. **Bound everything and say so.** Return rows, total and a truncated flag, and
   show them.
8. **Batch ids safely**: dedupe, validate, bind, chunk around 500, skip empty lists.
9. **Guard every recursion against cycles.** Memoize only on a key that fully
   determines the result.
10. **Pick one version deterministically.** BOM: location default, then master,
    then lowest id. Revision: latest effective start, then highest id. Use the work
    order's own BOM revision for actuals and the as-of revision for should-cost.
11. **Normalize units at every hop** from the right source (stock, purchase,
    consumption unit). Refuse a conversion across unit families.

## Allocating fan-outs

**Fan-outs are allocated, never repeated.** If one amount joins to N rows, split it
across them; do not attach the whole amount to each.

- A lot made by several work orders: split its consumption across the makers by
  quantity made (equal shares only if quantity is unknown, and say so).
- A shared link row: 1/N to each side.
- A child tree in a roll-up: weight by its share of supply.
- Express everything per top unit, then multiply once.
- An allocation is an estimate, not a trace. Label it as one.

## Terminal and fallback states are data

Opening-balance lots, revaluations with no link, items with no routing, receipts
that are sourced but not proven: each becomes a flagged row with a reason and an
amount, never a silent zero and never dropped.

## Roll-up and costing rules that recur

Confirm each against the NetSuite UI or documentation for your account before
relying on it.

- **Running average pool:** inbound adds its own amount (rounded to the cent);
  outbound leaves at the running average; a quantity-0 row changes value only;
  the pool resets when quantity reaches 0; negative on-hand costs at the last
  positive average, and the receipt that crosses back absorbs the negative units
  at its own cost. Same-day order: stock-in adjustments, then work order documents,
  receipts, transfer fulfillments and builds by created time, then ordinary
  outbound, customer returns last.
- **Assembly build cost** = all debits on the completion minus absorption credits.
- **Lot cost per unit** = total completion cost / total quantity completed across
  the lot's builds.
- **Work order close** reverses completions at the close-date average, which can
  strand drift in WIP. Residue = completion gap + issue gap (including
  revaluation) + routing gap.
- **In-flight WIP** = issued - completed + revaluation + journals. Leave out
  revaluation and the residual is noise.
- **Revaluation pairs:** lines post as adjacent credit/debit pairs. Link to the
  work order by `createdfrom` first, then quantity + direction in date order,
  then `nexttransactionlink`.
- **Budgeted cost roll-up:** purchased = quantity per x base cost x unit rate;
  sub-assembly = quantity per x unit rate x sub-assembly unit cost; routing step =
  ((run time per unit + setup time / costing quantity) / 60) x rate per hour +
  fixed cost.
  **Unconfirmed:** whether the routing step's run rate field is minutes per unit or
  units per hour. Implementations disagree. Check it in the NetSuite UI on a
  routing you know before you rely on either.

## Every chain ends in a tie-out that must foot

With untraced as a named row:

- parts + conversion + close + untraced = unit cost
- posted COGS = traced + untraced + variance
- debits = credits, per document
- account balance = sum of drill-down rows
- rebuilt pool = NetSuite on-hand quantity and average
