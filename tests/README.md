# tests

Integration and end-to-end tests only, plus the tests of the repo's own tooling.
Unit tests live beside each module, in `src/clause_tracer/<module>/tests/`.

| File | What it tests |
| --- | --- |
| `contracts/` | One behaviour suite per port, run against each fake now and each real adapter from stage 6 |
| `test_cli_end_to_end.py` | The command-line tool, run as a subprocess (the smoke test) |
| `test_copy_lint.py` | The copy lint in `scripts/copy_lint.py`, with small inline strings. A tooling test, not an app test |
| `test_golden_helper.py` | The golden-file helper in the root `conftest.py`, including the missing-file message and line endings |
| `test_check_owner_tables.py` | The owner-table guard in `scripts/check_owner_tables.py`, including its git behaviour |
| `test_links_sample.py` | The `links` clause fixture against `ingest`, and the sample from text to link map |
| `test_privacy_sample.py` | The `privacy` fixture against `ingest` and `links`, and the sample from text to placeholder text |
| `fixtures/` | Sample contracts and saved AI replies for the tests above. Empty so far; see its README |
