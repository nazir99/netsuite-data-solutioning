# netsuite-data-solutioning

An agent skill for the step after NetSuite data is pulled: design logic on the
data, rebuild it independently in Python, tie it out against NetSuite's own
figures, and have a second model try to break it before a person sees it.

It is one link in a [software factory](https://github.com/nazir99/software-factory):

```
nsq  ->  netsuite-data-solutioning  ->  build  ->  reader-walkthrough
```

It starts only after [nsq](https://github.com/nazir99/nsq) reports `NSQ: VERIFIED`,
and ends with a line a pipeline can gate on:

```
SOLUTION: TIED | NOT TIED <n> | UNREVIEWED <reason>
```

`TIED` needs both an independent tie-out and a finished review loop.

## Why

A harness that runs the production code against NetSuite and reports "200/200 ok"
proves the code agrees with itself. The rules here exist because agents, left
alone, do three things: they check the code against its own output, they tune a
rule until it matches the figure they then tie to, and they skip the second
review when told to hurry. The skill blocks each one.

## What is in it

| Path | What it is |
|---|---|
| `SKILL.md` | Guardrails, workflow and the output contract |
| `references/chaining-and-allocation.md` | Walking document chains, allocating fan-outs, recurring cost rules |
| `references/tie-out-patterns.md` | Independent sources, stratified samples, the report, checks by calculation |
| `references/python-rebuild.md` | Writing a rebuild that is actually independent |
| `references/review-loop.md` | Running the reviewer, findings to tests, the response doc |
| `review/` | Reviewer prompt, findings JSON schema, manifest and response templates |
| `examples/average-cost/` | A runnable example on synthetic data, including a real review run |

## Requires

- **nsq** skill and CLI: https://github.com/nazir99/nsq
- Python 3 (standard library only)
- Optional: [Codex CLI](https://github.com/openai/codex) for the second-model
  review. Without it, the skill uses a fresh subagent as the reviewer.

## Install

```bash
git clone https://github.com/nazir99/netsuite-data-solutioning ~/.claude/skills/netsuite-data-solutioning
```

Or install the whole chain with the software-factory `install.sh`.

## Try the example

```bash
cd examples/average-cost
(cd tieout && python3 -m unittest test_rebuild test_findings)
node src/cost_pool.js data/events.csv > /tmp/production.json
python3 tieout/tieout.py --production /tmp/production.json
```

## License

MIT
