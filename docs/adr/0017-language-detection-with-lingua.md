# ADR-0017: Detect a contract's language with Lingua

**Status:** Accepted (17 Nov 2026)
**Date:** 2026-11-17
**Deciders:** Project owner

## Context
[Spec 9](../spec.md#9-running-the-app) asks for a warning when a contract is mostly not English. The user can still continue. [System design 15.2](../system-design.md#152-stage-2-ingest-for-text-markdown-and-pasted-text) left the method open, and no decision record named a method or a library. The [stage 2 plan](../plans/stage-02-ingest.md), question 1, put two routes to the owner:
- a share of 40 common English words, with no new dependency;
- a language-detection library.

The owner wants room to support Arabic, French and other languages later. A library that names the language serves that future. A share of English words can only say "not English".

## Decision
The owner chose Lingua on 17 Nov 2026, knowing its size.

- **Library.** `lingua-language-detector` 2.2.0 (Apache-2.0, a Rust core with Python bindings, ships `py.typed`). It is pinned to one version, because the warning depends on its models.
- **How it is built.** `LanguageDetectorBuilder.from_all_languages().build()`, built once and reused. The models load on first use.
- **The rule.** Count the words: runs of letters, `[^\W\d_]+`. A text with fewer than 10 words is too short to tell, and gets no warning. Otherwise the text is warned when `detect_language_of(text)` returns a language other than English. When Lingua names no language, there is no warning. The 10 is `[Assumption]`, tuned in testing.
- **Where it lives.** Only `src/clause_tracer/ingest/language.py` imports `lingua`, so the library can be swapped behind one function (Constitution B4).

## Options Considered

### Option A: Lingua (chosen)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low: one call |
| Cost | Large. Measured on 17 Nov 2026 on Linux x86-64: each wheel is about 170 MB to download and 292 MB once installed. Peak memory was about 207 MB in a run that judged a 41,000-word text and seven short texts with every language enabled |
| Determinism | The same text gave the same answer on every call in the test |
| Future | Names about 75 languages, Arabic and French among them |

**Pros:** names the language, which a later stage needs for languages other than English. Short texts are judged well: a 17-word French sentence is caught.
**Cons:** the installer grows by about 290 MB, which makes Lingua the largest dependency in the app.

### Option B: share of 40 English words
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low |
| Cost | None: no dependency |
| Determinism | Same answer every time, and a person can see why it warned |
| Future | Says only "not English" |

**Pros:** small, and its reasons are readable.
**Cons:** it cannot judge texts under 50 words, and it must be replaced when other languages arrive.

## Trade-off Analysis
Option B is smaller now. Option A costs about 290 MB, but avoids a second change of method when the app supports more languages. The owner put the multilingual future first.

## Consequences
- The packaged app grows by about 290 MB, far more than the 31.9 MB spaCy model of [ADR 0008](0008-personal-data-detection-bundle.md). No installer size budget is set yet. Stage 12 measures the installer ([ADR 0009](0009-desktop-shell-protocol-and-packaging.md)), and ADR 0008 action item 6 states the download size in Spec 9 once it is measured.
- The third-party licences page lists Lingua under Apache-2.0 ([Spec 8.4](../spec.md#84-security)).
- The not-English owner table (`ingest/tests/tables/not_english.toml`) holds the answers a reader expects, not Lingua's output. A row that Lingua gets wrong is a finding for the owner, not a row to change.

## Action Items
1. [ ] Stage 2, task S2-M1-T6: add the pinned dependency.
2. [ ] Stage 12: check the installer size with Lingua inside, and whether limiting the languages built in shrinks it.
