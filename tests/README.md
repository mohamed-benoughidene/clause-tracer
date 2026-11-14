# tests

Integration and end-to-end tests only, plus the tests of the repo's own tooling.
Unit tests live beside each module, in `src/clause_tracer/<module>/tests/`.

| File | What it tests |
| --- | --- |
| `test_cli_end_to_end.py` | The command-line tool, run as a subprocess (the smoke test) |
| `test_copy_lint.py` | The copy lint in `scripts/copy_lint.py`, with small inline strings. A tooling test, not an app test |
| `fixtures/` | Sample contracts and saved AI replies for the tests above. Empty so far; see its README |
