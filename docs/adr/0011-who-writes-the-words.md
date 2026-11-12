# ADR-0011: Code writes the message and the not-covered headings; AI wording is opt-in and labelled

**Status:** Accepted (12 Nov 2026)
**Date:** 2026-11-11
**Deciders:** Project owner

## Context
[Spec 4.7](../spec.md) item 3 says "The AI writes the message", with `[TO]` and `[FROM]` markers that code fills in. Spec 6.1 step 11 has the AI write one plain sentence for each not-covered clause, and step 13 writes the message. Spec 8.4 treats the contract as untrusted: it may hold hidden instructions.

The [pipeline seams report](../../reports/Clause%20Tracer%20pipeline%20seams.md) listed these as owner decisions 5 and 6, plus the "Written with AI" mark. [The v1 design decisions report](../../reports/Clause%20Tracer%20v1%20design%20decisions.md) gave a recommendation for each. Its evidence here is thin: most items were seen only in search summaries, and no study tests any of these screens. Where evidence was thin, the tie-break favours the best experience for non-technical freelancers. [ADR 0002](0002-label-look-split-stamp.md) reserves dashed lines for pencilled labels.

## Decision
The project owner accepted three changes on 12 Nov 2026. The spec, the copy deck and the prototype were updated the same day.

1. **The message.** Code builds it from templates by default, one paragraph per ticked item, per kind and tone. An opt-in "Rewrite with AI" button shows the AI's version as a diff the user reads. Code re-checks every quote, number and name in it.
2. **Not-covered clauses.** The model picks a clause type from a closed list of 20 to 30 plain-English types `[Assumption]`, plus "Something else". The project owns the list. Code shows the heading, and the app shows the first line of the clause.
3. **The disclosure line.** One fixed line that says what was checked: "Every quote and number was checked against the contract; the wording was written by AI." It stays distinct from the dashed pencilled style.

## Options Considered

### Option A: Templates by default, opt-in rewrite, closed type list, fixed line (chosen)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med: template sets per item kind and tone, a diff view, a type list |
| Cost | No AI call for the default message: free, offline, the same every time |
| Scalability | Single user, not a scale question |
| Team familiarity | High: templates are plain Python and copy-deck text |

**Pros:** planted contract text reaches the message only as a quote code inserts. A wrong heading is probably less harmful than a wrong sentence (judgement). The fixed line tells the reader what to check.
**Cons:** templates may read stiffly; the cost in tone is unmeasured. The type list needs upkeep.

### Option B: AI writes connecting words around code facts
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med: slot forms and scans |
| Cost | One AI call per message |
| Scalability | Single user, not a scale question |
| Team familiarity | Med |

**Pros:** warmer tone, with facts locked by code.
**Cons:** its benefit over the opt-in rewrite is unmeasured.

### Option C: AI-written message and summaries, with scans (the Spec before this decision)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med |
| Cost | One AI call per message and per not-covered clause |
| Scalability | Single user, not a scale question |
| Team familiarity | Med |

**Pros:** closest to the Spec as it was. More helpful for unusual clauses.
**Cons:** keeps the most risk, and no evidence shows it is needed. A free AI sentence adds an injection route.

### Option D: A bare "AI wrote this" label
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low |
| Cost | None |
| Scalability | Single user, not a scale question |
| Team familiarity | High |

**Pros:** simple.
**Cons:** tells the reader nothing to check. One study, seen only as a search summary, found labels can lower trust in accurate text.

## Trade-off Analysis
All three recommendations are judgement. Template systems made fewer semantic errors in a 2024 study ([INLG 2024](https://aclanthology.org/2024.inlg-main.47.pdf), search summary only). OWASP says no known fool-proof injection defence exists ([OWASP LLM01](https://genai.owasp.org/llmrisk/llm01-prompt-injection/), search summary only). Zero-shot models trailed fine-tuned ones on LEDGAR themes by up to 19.2 micro-F1 points, but in 2023 models ([NLLP 2023](https://aclanthology.org/2023.nllp-1.22.pdf), search summary only). Reliance interventions cut overreliance but generally did not improve appropriate reliance ([arXiv 2412.15584](https://arxiv.org/abs/2412.15584)).

Gaps carried over: no study compares templated and AI-written outbound messages, and there is no data on user preference. No 2026 accuracy figure exists for clause-type picking. CUAD's 41 types describe what to extract, not a covering list, and no shared freelancer taxonomy was found. No study tests a fixed label on text in a decision tool. The EU AI Act Article 50 position is open and needs legal advice ([ADR 0014](0014-protection-and-release-integrity.md)). What is known about Article 50 is thin: the Commission's final guidelines were not opened and are known only through search summaries and law-firm alerts; how they treat tools that use the user's own key, and AI rewrites of the user's own wording, was not found; later amendments were not checked; and a date of 2 Dec 2026 is reported for machine-readable marking by systems already on the market. Meanwhile, the fixed line and a plain metadata note on exported AI text are the report's interim answer.

## Consequences
- Easier: the default message cannot be steered by planted text, works offline and costs nothing.
- Easier: users get one consistent AI mark that says what was checked.
- Harder: someone must write and review the templates and the type list, and keep both in the copy deck.
- Revisit if users find the template message too stiff, or if the golden set shows clause-type picking is often wrong. Measure type accuracy on the golden set.

## Action Items
1. [ ] Draft the closed clause-type list (20 to 30 types plus "Something else") and measure it on the golden set.
2. [ ] Write the message templates per item kind and tone, and the re-check for the rewrite diff.
3. [ ] Take legal advice on Article 50 before stating anything about it in the docs.
4. [x] Change Spec 4.7 item 3 and Spec 6.1 steps 11 and 13 (done 12 Nov 2026).
5. [x] Update `docs/ux-copy.md` and add the new states to the prototype's `states.html` (done 12 Nov 2026; `ux-copy.md` section 6.8 records it).
