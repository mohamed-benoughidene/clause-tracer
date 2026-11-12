# ADR-0012: Show silent negatives, turn disagreement into unsure, and keep labels whose quote can't be placed

**Status:** Accepted (12 Nov 2026)
**Date:** 2026-11-11
**Deciders:** Project owner

## Context
[Spec 5](../spec.md) Rule 7 says a position with no matching text gets its missing level, and appears in the Missing list unless that level is preferred. So a false-Missing on, say, the non-compete (missing level preferred) leaves no trace at all. Rule 3 makes a failed quote unsure. Rule 9 makes values on hidden text unsure. Spec 6.1 step 1 finds tracked changes, but no rule says which view of a Word file is the contract.

The [pipeline seams report](../../reports/Clause%20Tracer%20pipeline%20seams.md) found these holes and listed them as owner decisions 1 to 4. The [pipeline architecture report](../../reports/Clause%20Tracer%20pipeline%20architecture.md) added tracked changes. [The v1 design decisions report](../../reports/Clause%20Tracer%20v1%20design%20decisions.md) recommended an answer for each. All are judgement, and most supporting sources were seen only in search summaries. The tie-break favours non-technical freelancers: unsure results say what to read, not "the tool gave up".

## Decision
The project owner accepted four rules on 12 Nov 2026.

1. **The Rule 7 hole.** Show "searched, nothing found" positions in a collapsed list where each row can be checked. Keep them out of the walk-away and unsure counts. Each row opens a panel headed "Where it was searched". (The research called it "show where I looked"; the app never says "I".)
2. **Disagreeing search passes.** When a search pass found a candidate but the pair check said no, the position becomes unsure with reason code `MATCH_UNCONFIRMED`. It names a clause to read ("read this clause") and what to look for. Unsure counts are reported separately.
3. **Quote found but not placeable.** If code confirms the quote in the text but cannot place it on the page, the label stays. The app says the quote could not be placed and shows the quote text in a panel. It warns or blocks when the share of undecodable font characters passes a threshold set from the golden set.
4. **Tracked changes in Word.** The accepted (final) view is the contract. A notice names the count of changes and their authors, and offers a check of the original view. If time is short, warn or refuse and ask the user to accept or reject the changes first. Deleted text is never silently treated as hidden text.

## Options Considered

### Option A: The four rules above (chosen)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med: one new list, one reason code, one panel, one notice |
| Cost | No extra AI calls |
| Scalability | Single user. More unsure items mean more checking work |
| Team familiarity | High: pure rules in `core`, copy and screens |

**Pros:** no silent negatives. Uses the existing four labels, so no fifth label ripples through the Spec. A PDF fault does not look like a contract doubt.
**Cons:** more rows and more unsure items for the user to read.

### Option B: Hide silent results and keep Missing with a note
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low |
| Cost | None |
| Scalability | Single user, not a scale question |
| Team familiarity | High |

**Pros:** a calmer screen.
**Cons:** a hidden null set nobody samples is the set-up for omission errors. Missing plus a note is the silent miss by another route.

### Option C: Make unplaceable quotes unsure
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low |
| Cost | None |
| Scalability | Single user, not a scale question |
| Team familiarity | High |

**Pros:** stricter.
**Cons:** makes a PDF fault look like a contract doubt, and users learn to ignore flags that cry wolf.

### Option D: Check one Word view silently
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low |
| Cost | None |
| Scalability | Single user, not a scale question |
| Team familiarity | High |

**Pros:** simplest reader.
**Cons:** a quote could match deleted or not-yet-in-force text.

## Trade-off Analysis
Every recommendation here is judgement. For the Rule 7 hole, three strands agree a silent negative is dangerous: e-discovery null-set sampling and omission-error research (both search summary only), and ContractEval's "laziness" finding ([arXiv 2508.03080](https://arxiv.org/abs/2508.03080)). For disagreement, one study found that telling clinicians an AI abstained raised false negatives while overall automation-bias harm fell ([arXiv 2508.07617](https://arxiv.org/abs/2508.07617), search summary and secondary source). Showing sources reduced reliance on wrong answers ([arXiv 2502.08554](https://arxiv.org/abs/2502.08554v1)). Tiered fallbacks for citations are published practice, but only in vendor and project posts seen in search summaries. Word's "No Markup" view is the accepted view (search summary only).

Gaps carried over: no study tests these exact screens. How many rows users will open is unknown. No tolerance threshold for abstentions exists, and the abstention study is of clinicians. Nothing covers undecodable or custom-encoded font text. There is no bar or law-society guidance on which Word view counts. The Missing text must never say "verified absent", because absence cannot be proved.

## Consequences
- Easier: every false-Missing leaves a visible, checkable trace, and the golden set can count dangerous false-Missings.
- Easier: a quote that cannot be placed still shows its real words.
- Harder: more unsure items, so a target unsure share must be set from the golden set.
- Revisit when the golden set gives the real disagreement rate, the unsure share and the undecodable-character distribution.

## Action Items
1. [ ] Add `MATCH_UNCONFIRMED` to `core`'s reason codes, with separate result types for "nothing found" and "call failed".
2. [ ] Set the undecodable-character threshold from the golden set. Until then it is `[Assumption]`.
3. [ ] Build Word tracked-change fixtures: insertions, deletions, several authors.
4. [x] Change Spec 5 Rule 7, add the unplaceable-quote case beside Rule 3, update Spec 4.3 (the Missing tab), and add the tracked-changes rule to Spec 6.1 step 1 and Spec 9 (done 12 Nov 2026).
5. [ ] Extend Rule 9 for text that can't be decoded, once the test set gives a threshold (Spec 13 lists this as open).
6. [x] Add copy to `docs/ux-copy.md` and new states to the prototype's `states.html`: the searched-nothing-found list, the clause to read when searches disagree, the quote panel and the tracked-changes notice (done 12 Nov 2026).
7. [ ] Still without copy or a prototype state: the warning for text that can't be decoded, and a way to check a Word file's earlier wording inside the app.

## Amendment (12 Nov 2026): text that can't be decoded, and the list of tracked changes

The owner accepted two additions on 12 Nov 2026. They close action items 5 and 7.

1. **Text that can't be decoded.** A value whose quote includes text the app can't decode becomes unsure, exactly as Rule 9 does for hidden text. No new label is needed. A page where more than 1 in 20 characters can't be decoded `[Assumption]` gets a warning at the contract check, which names the page. The extreme case needs no new rule: a page with fewer than 50 readable characters already counts as scanned and blocks (Spec 9). Tune the 1-in-20 level on the test set.
2. **Tracked changes are listed.** The contract check lists every tracked change with its earlier and new wording and who made it. The user sees the earlier wording there, so no second review is needed. The accepted view is still the contract. Removed words are not part of it and are never sent to the AI.

The spec (Rule 9 and section 9), the copy deck and the prototype were updated the same day.
