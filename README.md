# netsuite-data-solutioning

Work in progress. An agent skill for the step after the data is pulled: designing
logic on NetSuite data, rebuilding it independently, tying it out, and having a
second model try to break it before a person sees it.

It is the link after [nsq](https://github.com/nazir99/nsq) (find, verify, store the
data) and before the build and the reader review.

## Planned

- Chaining and allocation patterns for documents, lots, work orders, BOMs and GL lines
- Independent rebuild in Python, with tie-outs that must foot and name what is untraced
- Automated second-model review (`review/`): a standard prompt, a findings schema,
  and a per-project manifest
- An output line a pipeline can gate on

## License

MIT
