# ADR-0013: Test in five layers on saved replies, with one paid layer and hard per-case gates

**Status:** Proposed
**Date:** 2026-11-11
**Deciders:** Project owner

## Context
[Spec 11](../spec.md) sets the acceptance tests: every planted walk-away found, at least 90% of numbers and labels right, no made-up quote ever. The test set runs after every change to prompts, models or labelling code. The [Constitution](../../Constitution.md) asks for fakes over mocks (T3), tests around the model with a fake (T7), and a small paid set of real examples run apart from the fast tests (T8). AI agents write most of the code, and their tests are a known weak spot.

Live replies cannot be pinned. The chosen endpoints do not accept `temperature`, and Claude endpoints list no `seed` ([OpenRouter ZDR endpoints API](https://openrouter.ai/api/v1/endpoints/zdr)). Even at temperature 0, output varies because of server-side kernel behaviour ([Thinking Machines](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)). Only replay makes an AI-dependent test repeatable. [The v1 design decisions report](../../reports/Clause%20Tracer%20v1%20design%20decisions.md) confirmed the five layers of the [pipeline architecture report](../../reports/Clause%20Tracer%20pipeline%20architecture.md), with changes in tools and targets. The full plan is in [the testing strategy](../testing-strategy.md).

## Decision
We recommend the following. It awaits the owner's decision.

- **Five layers.** Four run free on saved replies and one runs against the real model. They include Hypothesis property tests for the seven offset invariants, contract tests that run one suite against each fake and its real adapter, golden-file tests on each module's `samples/`, end-to-end replay tests and visual tests on Linux. [The testing strategy](../testing-strategy.md) names each layer.
- **Replay fake.** A hand-written fake behind the AI port, keyed on a content hash (model id, schema id, normalised prompt, step version). It raises `UnrecordedRequest` on a miss and exposes `unused_keys()`, which a fixture asserts empty.
- **Paid run.** A `@pytest.mark.golden` marker, deselected in `scripts/check.sh` and CI, plus a small `golden_report.py`. Run only by hand or on a labelled change, never on push.
- **Coverage.** Branch coverage per package: `core` 95%, pipeline modules 85%, adapters 70%, `cli` 60%, plus 90% on changed lines. These targets are `[Assumption]`.
- **Mutation.** mutmut on `core` and the pure rule modules, as a scheduled or pre-release report.
- **Agent guard.** Human-owned acceptance tables in CSV or TOML. Agents may write the loader but may not change expected values in the same change as the code. A named command, `--update-goldens`, regenerates golden files.
- **Gates.** Hard, zero-tolerance gates per case: every planted walk-away found in all three runs, no fabricated quote ever, zero dangerous false-Missings on built cases. Rates are reported, not gated: number accuracy and label match at or above 90%, and overall false-Missing, each with an exact interval.
- **Budget.** Two tiers: the 100-case set on every prompt, model or labelling change (about $34 on Sonnet); the full 300-case set before a release or model switch (about $67).

## Options Considered

### Option A: Hand-written replay fake, pytest marker, own gates (recommended)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low to Med: a fake, a marker and a report script |
| Cost | Free on every push; paid tier as estimated above |
| Scalability | Every paid run adds fixtures, so the free suite grows |
| Team familiarity | High: plain pytest |

**Pros:** fail-on-unrecorded and fail-on-unused catch drift both ways. No telemetry. No secrets in fixtures.
**Cons:** the project owns the fake and the report script.

### Option B: VCR.py with pytest-recording
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med |
| Cost | Free |
| Scalability | Duplicates fixtures |
| Team familiarity | Med |

**Pros:** a known library ([pytest-recording](https://github.com/kiwicom/pytest-recording)).
**Cons:** stores headers, a secret risk. Needs body matching for a single POST endpoint anyway.

### Option C: An eval framework (Inspect AI, DeepEval, promptfoo)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med to High |
| Cost | Free to install |
| Scalability | Good for multi-model comparison |
| Team familiarity | Low |

**Pros:** Inspect AI is MIT and the only framework found with no default telemetry. It stays the upgrade path.
**Cons:** DeepEval has telemetry on unless opted out ([DeepEval](https://deepeval.com/docs/environment-variables)). promptfoo is Node, sends telemetry, and had an opt-out leak reported on 4 Jul 2026.

### Option D: A local stub server for the adapter contract test
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med: a port and a thread |
| Cost | Free |
| Scalability | Single user, not a scale question |
| Team familiarity | Med |

**Pros:** language-neutral.
**Cons:** no gain over respx or pytest-httpx when the HTTP library is httpx-based. Note that bare `@respx.mock` disables the unused-route check.

## Trade-off Analysis
The statistics drive the gates. With zero failures in n independent cases, the 95% upper bound on the failure rate is about 3/n: 3.7% at 80 cases, 3.0% at 100 and 1.0% at 300 (one-sided exact). The unit is the case, not the run. Clustered standard errors can be over three times the naive ones ([Anthropic](https://www.anthropic.com/research/statistical-approach-to-model-evals)). So ten contracts are ten clusters, and rate claims need 20 to 50 small built cases per kind. "pass^3" is reported beside per-run accuracy, because a user gets one run.

The gate numbers are the project's own. No published release threshold exists, so they must never be presented as an industry norm. The coverage targets are judgement, anchored on Google's 60, 75 and 90 per cent guidance (headline numbers only). LLM-written tests peak at a 0.546 mutation score against 0.690 for human tests ([arXiv 2511.21382](https://arxiv.org/html/2511.21382v1)), so coverage is a floor. The budget figures are the researcher's estimates; the 20% small-case factor and reasoning-token volume are unknown until the first paid run. A spend cap at about double the table figure is judgement `[Assumption]`. Other gaps: the pytest-httpx licence was not re-checked; Inspect AI was not audited for network calls; pytest-gremlins was not checked; the test-quality evidence is mostly Java.

## Consequences
- Easier: the keyless suite runs on every pull request at no cost, with sockets blocked suite-wide.
- Easier: agents cannot quietly move the answer key.
- Harder: built cases and a fixture redaction check must be written before rate claims mean anything.
- Revisit after the first paid run: case correlation, reasoning-token cost, cache hits and real per-case cost.

## Action Items
1. [ ] Build the replay fake in `core` test support, with `UnrecordedRequest` and `unused_keys()`.
2. [ ] Add the `golden` marker, deselect it in `scripts/check.sh`, and add the CI check that guards the acceptance tables.
3. [ ] Check the pytest-httpx licence and audit Inspect AI for network calls before any use.
4. [ ] Re-query prices and set the spend cap before the first paid run.
5. [ ] If accepted, rewrite Spec 11 to state hard gates per case and reported rates with exact intervals.
