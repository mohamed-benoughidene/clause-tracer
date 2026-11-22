# Samples

`developer-agreement.privacy.json` is the `ingest` output, the `links` terms and
the typed party details for
`src/clause_tracer/ingest/samples/developer-agreement.txt`, in the `privacy`
fixture format.

Write it only with
`.venv/bin/uv run pytest tests/test_privacy_sample.py --update-goldens`, and
never edit it by hand. The drift test in `tests/test_privacy_sample.py` rebuilds
it from `ingest` and `links` and compares.
