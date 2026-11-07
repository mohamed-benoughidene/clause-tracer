---
status: accepted
date: 2026-11-07
---

# Code layout: one package, a pure core, pipeline modules and adapters

The code lives in one Python package, `src/clause_tracer/`, in the src layout. It is split into a pure `core`, six pipeline modules that follow Spec section 6.1, an `adapters` package for everything that talks to the outside world, and a `cli` that wires them together. Each module runs alone, has its own tests and documents its input and output shapes, as the Constitution (S1–S3) requires. Modules pass data to each other through plain function calls on each module's public API, using typed, frozen dataclasses defined in `core` (Constitution S4).

| Module | Does | Spec 6.1 steps |
| --- | --- | --- |
| `core` | The playbook and review models, and the labelling rules. Pure: no files, network, clock or AI. | 8 (and section 5) |
| `ingest` | Read the file, split it into clauses | 1–2 |
| `privacy` | Find personal data, make placeholders | 3–4 |
| `links` | Cross-references, defined terms, overrides | 5 |
| `checking` | Match, extract, quote check, judge, explain, summarise | 6a–11 |
| `writing` | Rewrite a clause | 12 |
| `outputs` | The message and the report | 13–14 |
| `adapters` | OpenRouter, Presidio, storage, the system password store | The edges |
| `cli` | The command-line tool. The only place that wires modules together | Section 9 |

The allowed imports are `core` ← pipeline modules ← `cli`, and `adapters` → `core`. Pipeline modules never import each other or the adapters: the adapters they need are passed in. `import-linter` checks these rules in `scripts/check.sh` and in CI, so a break fails the build.

We chose this because AI agents will write most of the code, and agents are weakest at keeping architectural boundaries. A study found they solved only 4.3% of dependency-control tasks ([Needle in the Repo, 2026](https://scispace.com/papers/needle-in-the-repo-a-benchmark-for-maintainability-in-ai-rsjdq5toer7q)). Rules that a machine checks hold up. Rules that are only written down drift.

## Considered options

- **One module per pipeline step (14 modules).** It maps one-to-one to the spec, but many modules would be shallow, and some steps must be called in order. That goes against the Constitution's B5 (prefer deep modules).
- **Layers (`interface`, `logic`, `data`).** It's simple, but the work is a one-way flow of steps, which the Constitution's P2 says is a pipeline, not layers. A layered layout also scatters one feature across three folders, so an agent has to open all three to change it.
- **Flat layout (the package at the repo root).** It's quicker to start, but the Python Packaging Guide recommends the src layout for anything installed or published, because tests then run against the installed package.

## Consequences

- An agent changing one stage of the pipeline works inside one folder: its code, tests, samples and shape README.
- The independence rule between pipeline modules may prove too strict. The first known case: a rewrite (step 12) re-runs the checking steps (6b–10) on the new wording. Handle it by having `cli` call `writing`, then pass the result to `checking`. Put any data shapes both modules need in `core`. If that proves awkward, amend this ADR and add a narrow `ignore_imports` exception to the contract in `pyproject.toml`. Don't loosen the contract silently.
- The desktop shell (Tauri or Electron, Spec section 13) isn't decided. It will get its own top-level folder and an ADR when it is.
- Unit tests live beside each module (`src/clause_tracer/<module>/tests/`). The root `tests/` holds only integration and end-to-end tests.
