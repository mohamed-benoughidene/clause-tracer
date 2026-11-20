# Samples

`developer-agreement.clauses.json` is the `ingest` output for
`src/clause_tracer/ingest/samples/developer-agreement.txt`: the document and its
65 clauses, in the `links` clause fixture format.

Write it only with
`.venv/bin/uv run pytest tests/test_links_sample.py --update-goldens`, and never
edit it by hand. The drift test in `tests/test_links_sample.py` rebuilds it from
`ingest` and compares.
