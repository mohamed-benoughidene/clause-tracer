# clause_tracer: module map

Each module has one purpose, a README with its input and output shapes, its own tests in `<module>/tests/`, and a way to run it alone (`.venv/bin/uv run python -m clause_tracer.<module>`).

| Module | Purpose |
| --- | --- |
| `core` | Pure rules: playbook and review models, and picking labels (Spec 5, and 6.1 step 8). |
| `ingest` | Read the file, split into clauses (6.1 steps 1-2). |
| `privacy` | Find personal data, make placeholders (steps 3-4). |
| `links` | Cross-references, defined terms, override clauses (step 5). |
| `checking` | Match, extract, quote check, judge, explain, summarise (steps 6a–7 and 9–11). Calls `core` to pick labels (step 8). |
| `writing` | Rewrite a clause (step 12). |
| `outputs` | The message and the report (steps 13-14). |
| `adapters` | The edge: `openrouter`, `presidio`, `storage`, `keyring`. |
| `cli` | Command-line entry point. Wires everything together. |

## Allowed dependency direction

- `core` <- pipeline modules (`ingest`, `privacy`, `links`, `checking`, `writing`, `outputs`) <- `cli`
- `adapters` -> `core`
- `cli` -> everything.
- Pipeline modules never import `adapters`, `cli` or each other. Adapters are passed in by `cli` (dependency injection).

These rules are enforced by `[tool.importlinter]` in `pyproject.toml` (run `lint-imports`).

## How modules pass data (Constitution S4)

Plain function calls through each module's public API in its `__init__.py` (`__all__`), using typed, frozen dataclasses defined in `core`. No files, network or shared state between modules.

Recorded in `docs/adr/0004-code-layout.md`.
