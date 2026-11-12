# ADR-0010: Start testing with Claude Sonnet 5.5, compared against GPT-6.1 Terra and DeepSeek V4.1 Flash

**Status:** Accepted (12 Nov 2026)
**Date:** 2026-11-11
**Deciders:** Project owner

## Context
[Spec 13](../spec.md) asks which 2 or 3 models to start testing with, from OpenRouter's zero-retention list, and whether Jev beats an AI model on steps 6a and 9. Spec 6.2 says one model serves every step by default, and recommended models come from test-set scores. Spec 8.2 turns private mode on by default.

[The v1 design decisions report](../../reports/Clause%20Tracer%20v1%20design%20decisions.md) queried the [ZDR endpoints API](https://openrouter.ai/api/v1/endpoints/zdr) and the [models API](https://openrouter.ai/api/v1/models) on 11 Nov 2026. The ZDR list had 1,078 endpoints. 151 models had a live non-Safety-Retention endpoint, strict structured outputs, 128k context and a cached-input price. Gemini models are out of private mode, because Google requires Safety Retention on Vertex from 18 Oct 2026. The top LegalBench models, Claude Fable 5 and 5.1, have no ZDR endpoint ([Vals AI LegalBench](https://www.vals.ai/benchmarks/legal_bench)). Under strict schemas, Claude routes only to Vertex and GPT-6.x only to Azure.

## Decision
The project owner accepted the following on 12 Nov 2026. One known limit: the paid-test budget is about $10.76 in total ([`testing-strategy.md`](../testing-strategy.md) section 7.5), so most paid testing runs on cheap models. The Sonnet default gets one pass of the ten test contracts at most, and is less tested than the release gates intend until more budget exists.

- **Default:** `anthropic/claude-sonnet-5.5`. 1M context, explicit caching, one fixed ZDR provider.
- **Comparisons:** GPT-6.1 Terra (another vendor family, about half the price), and DeepSeek V4.1 Flash pinned to one fp8 host (about 20 times cheaper, 25+ ZDR hosts).
- **One extra run** of `z-ai/glm-5.3-flashx-legal`.
- **Jev** stays an experiment behind the golden set. v1 is not built on it.
- **Self-consistency sampling** is not a default until the golden set measures the real disagreement rate. If used later, vary the prompt or model family between samples, and treat any disagreement as unsure.
- **Operating rules:** read cached-token counts on every call and warn when caching misses. Pin one provider and one quantisation for open-weight models. Test strict-schema enforcement per endpoint.

Cost per review, from prices fetched on 11 Nov 2026. The figures are the report's estimates, not measured runs.

| Model | 10,000-word review | 50,000-word review |
|-------|--------------------|--------------------|
| Claude Sonnet 5.5, caching works | about $0.28 | about $0.82 |
| Claude Sonnet 5.5, caching fails | not given | about $3.77 |

## Options Considered

### Option A: Claude Sonnet 5.5 as default, two comparisons (chosen)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low: one model for every step |
| Cost | About $0.28 per 10,000-word review (estimate) |
| Scalability | One ZDR provider means no fallback when Vertex is down |
| Team familiarity | High: standard OpenRouter chat requests |

**Pros:** one fixed zero-retention provider, so runs differ less (though no live reply can be pinned), and a known cache-write price. The comparisons cover another vendor and a cheap open-weight model.
**Cons:** no published benchmark exists for the 5.5 and 6.x models on contract tasks. If Vertex is down, the app must show "no private model available".

### Option B: GPT-6.1 Sol as default
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low |
| Cost | The same as Sonnet 5.5 |
| Scalability | Azure only under strict schemas |
| Team familiarity | High |

**Pros:** same price.
**Cons:** lost on the fixed-provider point and on cache-write price clarity. The report calls this close.

### Option C: Jev (TypeSafe) for steps 6a and 9
| Dimension | Assessment |
|-----------|------------|
| Complexity | High: an alpha route with a different request shape |
| Cost | Not given |
| Scalability | Single user, not a scale question |
| Team familiarity | Low |

**Pros:** typed answers with probabilities ([Decisions API](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request)).
**Cons:** alpha route, no quote returned, no independent evaluation. Whether `provider.zdr` is honoured there is undocumented.

Mistral Large 4 and open-weight mid-tier models lost because they add runs without a clear question.

## Trade-off Analysis
Prices are verified. Cost per review is the researcher's estimate. The model choices are judgement. LegalBench scores in the candidate set span only about 83% to 87%, too narrow to choose on. So the golden set ([ADR 0013](0013-test-layers-and-release-gates.md)) must decide, not a public leaderboard.

Caching is not decoration: a miss raises Sonnet 5.5 from $0.82 to $3.77 on a 50,000-word contract. That is why every call reads cached-token counts. Whether each endpoint truly enforces `strict: true` is not stated in the API, so it must be tested per endpoint. The GLM legal model's match to the Vals "GLM Legal" entry is judgement. Its price differs between Vals and OpenRouter, and it was nine days old with one host when checked. Self-consistency sampling may look safe while catching little, because `temperature` is unavailable and samples may be too alike. No accuracy-at-coverage figure exists for three samples on contract classification.

## Consequences
- Easier: one default model keeps the first golden runs cheap and comparable.
- Easier: a caching warning catches the most expensive failure early.
- Harder: a single ZDR provider for the default means a clear "no private model" path is required.
- Revisit after the first paid run: measured cost, reasoning-token volume, cache hit rate, strict-schema enforcement and sample disagreement. Re-query prices before any budget.

## Action Items
1. [ ] Re-query the ZDR list and model prices before the first paid run. Prices change.
2. [ ] Test strict-schema enforcement on each chosen endpoint with a prompt that invites a schema break, and save the replies as fixtures.
3. [ ] Record the provider per call and compare it with the ZDR list, flagging any `safety_retention: true` endpoint. That ZDR-list call is a fourth kind of OpenRouter request, so Spec 8.1 must list it.
4. [ ] Measure the golden-set disagreement rate before deciding on self-consistency sampling.
5. [x] Tick the models item in Spec 13 (done 12 Nov 2026).
6. [ ] Add the typical review cost to the key guide in `docs/ux-copy.md`, once measured.
