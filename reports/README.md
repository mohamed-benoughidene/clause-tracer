# Reports

This folder holds research reports that inform design and build decisions. Each report is dated and starts with a short summary.

## What's in it

| File | What it is |
| --- | --- |
| [Clause Tracer pipeline architecture.md](Clause%20Tracer%20pipeline%20architecture.md) | The build design: a fixed pipeline of standalone modules that code polices. |
| [Clause Tracer pipeline seams.md](Clause%20Tracer%20pipeline%20seams.md) | The three hand-overs between steps where mistakes slip through, and how to close them. |
| [Clause Tracer v1 design decisions.md](Clause%20Tracer%20v1%20design%20decisions.md) | 11 Nov 2026. A recommendation, a runner-up and the evidence for each open decision: testing, architecture, privacy, the desktop shell, models, product wording and protection. It also corrects the architecture report. |
| [Privacy finder design choices.md](Privacy%20finder%20design%20choices.md) | 21 Nov 2026. A verdict, the evidence and the exact plan edit for each of the 17 open questions in the stage 4 plan, with the defects found in the plan text. |
| [Stage 5 reader design choices.md](Stage%205%20reader%20design%20choices.md) | 23 Nov 2026. A verdict, the evidence and the plan changes for questions 1 to 5 of the stage 5 plan: the child process, page rendering, hidden text in later modules, Word list numbers, and Word comments, notes and headers. |
| [Stage 5 reader checks and limits.md](Stage%205%20reader%20checks%20and%20limits.md) | 26 Nov 2026. A verdict, the evidence and the plan changes for questions 6 to 21 of the stage 5 plan: Unicode checks, CI and tools, hidden-text thresholds, hostile-file limits, PDF text layout, PDFium facts, and the Word reader. Builds on the report on questions 1 to 5. |
| [Edits to source documents 2026-11-11.md](Edits%20to%20source%20documents%202026-11-11.md) | The record of every change made to the Constitution, the spec, the earlier reports and the doc guides on 11 Nov 2026, with the reason for each. |

## Rules

- Every new report gets a row in this table.
- When a report drives a decision, link it from the ADR or the spec that records that decision.
- Keep one report per topic.
