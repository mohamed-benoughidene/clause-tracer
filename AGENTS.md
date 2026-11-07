# AGENTS.md

This repo is **Clause Tracer**: a local-first desktop app that checks a contract against the user's own playbook and shows the evidence for every label. The repo is named `clause-tracer`. [README.md](README.md) is the overview.

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install --no-cache-dir uv   # first time only
.venv/bin/uv sync                          # install or update every package from uv.lock
.venv/bin/uv add <package>                 # add a dependency (updates pyproject.toml and uv.lock)
scripts/check.sh                           # lint, format, types, import rules, tests
.venv/bin/uv run python -m clause_tracer.ingest   # run one module alone (any module name)
```

Everything stays inside the repo: packages in `.venv/`, uv's cache in `.cache/uv/` (both git-ignored), and the system Python. Use `.venv/bin/uv`, not a global `uv`, and commit `uv.lock` with any dependency change.

Run `scripts/check.sh` before you call a code change done. It must pass with no errors. CI runs the same script on every push.

## Where the project stands

The design is done. The code is an empty skeleton: every module exists, runs alone and passes its smoke test, but no feature is built yet. The repo holds:

- `src/clause_tracer/`: the Python package. [Its README](src/clause_tracer/README.md) maps the modules. [ADR 0004](docs/adr/0004-code-layout.md) explains the layout.
- `tests/`: integration and end-to-end tests only. Unit tests live beside each module, in `src/clause_tracer/<module>/tests/`.
- `docs/`: the spec and the design, copy and brand docs. [`docs/spec.md`](docs/spec.md) is the source of truth for what the app does.
- `prototype/`: a clickable HTML prototype, with one page per screen.
- `assets/`: the logo master files.
- `reports/`: research reports on how to build the app. [The architecture report](reports/Clause%20Tracer%20pipeline%20architecture.md) is the build design; read it before planning a build stage.

The build plan in Spec section 9 is a Python command-line tool first, which is then wrapped as a desktop app. The decisions in Spec section 13 are still open (the desktop shell, how Presidio is bundled, which models to use). Bring those to the user as a question. Don't pick one yourself.

## Before you write code

Read [Constitution.md](Constitution.md) before you write, move or split any code. It is binding: standalone modules, raw data kept unchanged, and side effects kept at the edges. Its rules have IDs (B1, D1, S1 and so on). Cite them when they shaped a choice.

- **Commits and branches.** Follow [GIT_CONVENTIONS.md](GIT_CONVENTIONS.md) when you commit or name a branch.
- **Work inside one module.** Each module folder holds its code, its `tests/`, its `samples/` and a README with its input and output shapes. When a shape changes, update that README in the same change (Constitution S3).
- **Keep the import rules.** `core` imports nothing else. Pipeline modules import only `core`. Adapters are passed in, never imported. Only `cli` wires modules together. `lint-imports` enforces this. When a rule blocks you, put the shared shape in `core` or ask the user. Leave the contracts in `pyproject.toml` as they are.
- **Test with fakes.** Unit tests use fake adapters and saved AI replies from `samples/` or `tests/fixtures/`. They run with no network, no API key and no cost.
- Put complex conditions into well-named boolean variables.

## Before you change docs or the prototype

- **Docs:** when a change affects what the app does, says or promises, update the docs in the same change. [WRITING_DOCS.md](WRITING_DOCS.md) section 2 says which files to update, and section 9 is the checklist.
- **Prototype:** follow the rules in [prototype/README.md](prototype/README.md). Start from `home.html`, use only the classes in `styles.css` and the data attributes in `app.js`, and add every new state to `states.html`. To preview it, run the `prototype` server in `.claude/launch.json` (http://localhost:8767).
- **Words on screen:** take them from [docs/ux-copy.md](docs/ux-copy.md). If a page and the copy deck disagree, fix both.

## Rules the files don't state

- **Red means walk-away.** In the interface, oxblood `#A91207` belongs to the walk-away label and the logo (ADR 0003). Nav markers, progress bars, focus rings and decoration use ink or another accent. A walk-away is also marked by its ✕ icon and its word, so it still reads in greyscale.
- **Dashed means pencilled.** Only labels the AI judged from the wording are dashed (ADR 0002).
- **Write British English** in docs and in the app. The licence's name and the `LICENSE` file name keep their US spelling.
- **The app speaks in the third person.** "This one is a walk-away." Only the user's own words use "I" and "my".
- **Say "source available"** for the licence (FSL-1.1-ALv2). Keep `LICENSE` as the exact official text.
- **Treat contracts as untrusted.** A contract or an imported playbook may contain hidden instructions. Code checks every quote and number, and code picks labels wherever it can (Spec section 8.4).
- **Keep the repo free of real data.** Use the sample contract and the names from Spec 14.5, and invented placeholders for keys.
- **Logo changes start outside the repo.** The build scripts are in `/home/mo/lab/Prototyping/logo/final/`. Copy the results into `assets/` and `prototype/` (see [assets/README.md](assets/README.md)).
