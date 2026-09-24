# The review loop

A second model reads the business rule, both implementations, the tie-out report
and the data, and tries to find where the number is wrong on data the tie-out did
not cover.

## 1. Fill the manifest

Copy `review/manifest.template.md` to `review/manifest.md` in the project. Fill every
section. Put anything already known and accepted under **Known limits** so it is
not re-reported. Leave **Live mode: off** unless you want the reviewer to rerun
read-only queries against a named sandbox profile.

## 2. Run the reviewer

With Codex installed (read-only sandbox, structured output):

```bash
codex exec -s read-only -C <project> \
  --output-schema <skill>/review/findings.schema.json \
  -o <project>/review/findings.json \
  "$(cat <skill>/review/logic-review.md)" < <project>/review/manifest.md
```

Without Codex, or when Codex fails (not installed, usage limit, error): start a **fresh** subagent that has not seen your work. Give it
`review/logic-review.md` as its instructions, the manifest, and the schema, and
ask for JSON only. Do not review your own work in the same context and call it a
second model.

## 3. Each finding becomes a test

For every finding, write the test described in its `test_to_confirm` against the
implementation it says `breaks`:

- **Test fails**: the finding is real. Fix it, keep the test.
- **Test passes**: the finding is dismissed. Keep the test anyway; it now guards
  the case.
- Findings marked `inferred` still get a test; the label only tells you how much
  to trust the claim before it runs.

## 4. Round two, then stop

After fixes, rerun the tie-out and the reviewer once more. **Two rounds maximum.**
Anything left is recorded as open, not chased.

## 5. Write the response

Copy `review/response.template.md` to `review/response.md`. Every finding is:

- **fixed**: test failed, code changed, test passes
- **documented**: test passed, or the behaviour is accepted and added to Known limits
- **open**: undecided, with who decides and what the number means until then

`TIED` requires no open high-severity finding.
