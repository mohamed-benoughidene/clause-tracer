# scripts

Scripts that check or run the repo itself. They are not part of the app.

Run `scripts/check.sh` before you finish a change: it runs every check below, in order, and stops at the first failure.

| File | What it is |
| --- | --- |
| `check.sh` | The one command for agents and CI: the owner-table guard, ruff, format, mypy, import rules, the copy lint, then the tests under `coverage`, with a 95% branch-coverage floor for `core` and an 85% floor for `ingest` and `links`. |
| `check_owner_tables.py` | The owner-table guard (Constitution T11): fails a change that edits code and an owner table together, so expected answers are never written in the same step as the code that must match them. With no argument it checks the working tree as one change; with `--commits BASE` it checks each commit since `BASE` on its own and skips one whose message carries the line `Owner-Approved-Tables: yes`. Exit code 1 means a change failed. Standard library only; its tests are `tests/test_check_owner_tables.py`. |
| `copy_lint.py` | Lints the fixed copy and the look of the prototype: the on-screen strings of `docs/ux-copy.md`, the text of `prototype/*.html`, and the CSS. Run it with `python scripts/copy_lint.py` (`--quiet` prints failures only, `--warnings-as-errors` fails on a warning too). Exit code 1 means a FAIL. The checks are listed in `docs/ux-copy.md` section 1.1. Standard library only; its tests are `tests/test_copy_lint.py`. |
| `copy_lint_allow.txt` | The allow-list of `copy_lint.py`: `code \| file or * \| exact text or re:regex \| reason`. A line with no reason fails; a line that matches nothing warns. |

Rules for adding to it:

- A script is pure functions plus a thin `main()` that reads files and prints (Constitution T1, T2), with a test in `tests/`.
- No new dependency: use the standard library. mypy checks `scripts/` in strict mode, like `src/`.
- Wire a new check into `check.sh` as its own line.
