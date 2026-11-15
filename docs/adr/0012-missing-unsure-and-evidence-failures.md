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

## Amendment (14 Nov 2026): the fourth match result, Rule 10's input, and the last check

The project owner answered three points from the stage 1 task plan on 14 Nov 2026.

1. **A fourth match result type.** "Match not confirmed" (decision 2 above) is its own result, `MatchUnconfirmed`, beside "found", "nothing found" and "call failed". It holds the position and the clauses to read.
2. **Rule 10's input in stage 1.** The rule takes the documents not loaded that the label's evidence reaches. Which module builds the evidence trail is settled before build stage 8.
3. **The last check before drawing.** The text half always runs, using the quote-check fold of Spec section 2, written in `core`. The page-box half runs only when the document has glyphs, so text, Markdown, pasted and Word documents skip it. A quote that cannot be placed still keeps its label (decision 3 above).

Also decided for Rule 5: in stage 1, a value that already carries the "other start point" reason becomes unsure. How the start point is compared is settled before build stage 8. [The system design](../system-design.md) sections 3.4 and 15.8 hold the details.

The owner also answered the label and scan edge cases of the stage 1 plan on 14 Nov 2026, under one principle: when code can't be sure, the label is unsure, the reason is named, and the user is shown the clause. It never guesses in either direction (Spec 5 holds the rules).

4. **Edge cases of the label rules.** A number with no unit is read in the position's unit. A found clause with no confirmed quote is unsure ("quote not confirmed"). A found clause with no value or no answer is unsure ("no value found"). An AI answer of "unsure" on a words position is unsure ("the AI could not judge it"), with no second call. A deposit amount and a percentage are compared rounded half up to a whole percent. "Different values" means readable values that differ after conversion, clause by clause. A walk-away keeps the reasons of every value. A walk-away found in a clause stays walk-away under Rule 10, while a Missing walk-away becomes unsure. Only a label the AI actually judged is written by AI.
5. **"Unlimited."** For a position where lower is better, unlimited is walk-away. For one where higher is better, unlimited is unsure with the new reason code `UNLIMITED_UNCLEAR`, because the word can be good or bad for the user.
6. **Edge cases of the scans.** Listed words match as whole words or phrases in any letter case, with curly apostrophes made straight. Numbers written in words are not checked in build stage 1. A number that is both an acceptable limit and an allowed number is flagged as an acceptable limit. A label word used as ordinary English is flagged. A web address is `http://`, `https://`, `www.`, or a bare name ending in a listed domain. The acceptable-limit scan covers every kind of AI text.

Later on 14 Nov 2026 the owner added two points, after a review of the copy for machine-made text.

7. **Five style scans on AI text, built in stage 1.** Beside the scans above, code fails AI text that holds a first-person word ("I", "we", "my", "our" and their contractions) outside the "Rewrite with AI" message; a listed filler phrase or an exclamation mark; a listed evaluating word; a reason with neither a clause number nor a quoted word from its own quote; or a rewrite with more sentences than its source (for a clause rewrite, only when the user gave no instruction). They take the same route as the other scans: one regeneration, then the template text. The word lists are owner tables (Constitution T11), matched under the rule in item 6. The scans catch signs, not a fluent sentence that is wrong, so the owner also reads the AI text of each paid run (Spec 6.2, [testing strategy](../testing-strategy.md) section 7.5). Two details are open as question 18 of the [stage 1 plan](../plans/stage-01-core.md).
8. **Unsure and Missing labels get words from code.** A label a rule turned unsure, and every Missing label, has its panel written from templates. The one exception is a value unsure because of vague wording: the AI writes its two readings and question, and code writes the rest ([ADR 0011](0011-who-writes-the-words.md), amendment of 14 Nov 2026).
