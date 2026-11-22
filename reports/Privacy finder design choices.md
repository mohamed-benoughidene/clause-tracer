# Privacy finder design choices: what to change in the stage 4 plan

**Revised 22 Nov 2026 (third): decisions recorded and the plan updated.** This revision records what happened after the second revision, so that the report matches the repository. What changed:

- **The owner answered all 26 questions of section 6 of the plan** on 21 and 22 Nov 2026. "Owner decisions" is now the full record, as a table.
- **The stage 4 plan carries the answers.** It has 43 tasks and 442 tests, and its checker reports no findings. Its status is still Draft: "Accepted on" reads "Not yet". Question 24 was reversed to this report's version, so four more patterns are built in stage 4 (S4-M2-T12). Question 25 (the hybrid at the place) and question 26 (the card kind) are new.
- **Other files were edited** (uncommitted, as `git status` shows): Spec 4.2 and a new Spec 13 line, an ADR 0008 amendment of 22 Nov 2026, system design 15.4, 15.7 and 15.8, the testing strategy `privacy` row, the stage 1 plan (task S1-M6-T8), the plans README, the WRITING_DOCS promise table and `prototype/privacy-check.html`.
- **Each entry Q1 to Q17 now ends with "Status (22 Nov 2026)".** The line says how it was decided and where it lives, by plan task id. Five verdicts moved because of a decision: Q9 (hybrid at the place), Q15 (four patterns built), Q14 (closed list in Spec 4.2), Q10 (keep) and Q5 (value-only). The evidence text above each status line is unchanged.
- **"Where each change belongs" is now a done list.** "Test results" has a new subsection for the plan simulations and checks. "Open owner questions", "Evidence quality and gaps", "Links between questions" and "Next steps" match the repository.
- **First revision (evidence check), in one line:** four evidence notes were read and no verdict changed.
- **Second revision (21 Nov), in one line:** six test tracks, four nearby-field notes and five owner decisions were added; Q15 phones, Q9 union and Q17 layer 3 were corrected; several errors of the first revision were fixed.
- **Where the numbers live.** The folder `research_notes/` is git-ignored (checked with `git check-ignore`). The test numbers therefore exist only in this report. Real contracts stayed outside the repo; only counts are reported, and no contract text, party name or person name from them appears here.

**Scope.** This report tests the 17 first questions of section 6 of `docs/plans/stage-04-privacy.md` (the plan now has 26) against five sets of research notes, four evidence-check notes, six test tracks and four nearby-field notes. It recommends. It does not decide beyond the owner decisions below, and it edits no plan, table or word list (Constitution T11: the owner writes expected answers and word lists). Nothing here is legal advice and no lawyer was consulted. The output of the privacy step is pseudonymised text with a local map, never "anonymous" (ADR 0016 working position, Spec 4.2).

**Task IDs.** The plan's tasks are written in full (S4-M2-T7 is task 7 of milestone 2). The plan's own question numbers (1 to 26) are the numbers of section 6 of the plan. For questions 1 to 17 the report number and the plan number are the same.

<a id="owner-decisions-of-21-nov-2026"></a>

## Owner decisions of 21 and 22 Nov 2026

The owner gave these decisions in chat. Plan questions 5, 9, 10, 14, 18, 25 and 26 were answered one by one. Questions 1, 4, 12 and 17 were answered in a batch. All other questions were answered "as recommended", which is the plan as written. The second revision of this report numbered its own open questions; four of them became plan questions: old 1 is plan 24, old 9 is plan 21, old 10 is plan 25 and old 18 is plan 23. The decision numbers 1 to 6 are the ones that the plan cites.

| # | Decision | Question (report; plan) | Where it lives now |
|---|---|---|---|
| 1 | The governing-law place uses a closed list of five categories: a country, a UK nation, a US state, a Canadian province, an Australian state. "England and Wales" is one entry. A place outside the list is not kept: a finder's flag on it stays and the text is replaced. Stage 4 shows no "unsure" mark for it | Q14; plan 14, 19, 20 | Spec 4.2 (Kept line) and the new Spec 13 line; ADR 0008 amendment of 22 Nov 2026; WRITING_DOCS promise row; plan tasks S4-M3-T3 (`places.py`) and S4-M2-T11 (the owner writes `_place_list.py`; not yet written) |
| 2 | Keep the token form `⟦ ⟧`, with no ADR. Every prompt that carries placeholders says "write each placeholder exactly as it appears". This is stage 8 work, not stage 4 work | Q10, Q6; plan 10, 6 | System design 15.8 ("Placeholders in prompts", stage 8); plan section 9; ADR 0008 amendment; the escape in S4-M4-T1 and S4-M4-T2. `core/enums.py` is unchanged |
| 3 | Doubts come later (option B). The shape is task S1-M6-T8 of the stage 1 plan. Stage 4 produces no doubts. The code that fills the shape is built where the user first sees suggestions: stage 6 settles how the command-line tool does the privacy check (system design 15.6), and stage 12 builds the screen | Q17, Q1; no plan question (a change-log row of 21 Nov) | Stage 1 plan, S1-M6-T8 and its change-log row; stage 4 plan sections 8 and 9. The `core` code and the system design 3.4 rows are not built |
| 4 | ID and bank spans hold the value only. "Company number" stays readable and only `09876543` becomes `ID 1` | Q5; plan 5, 22 | S4-M2-T2 (value-only spans); S4-M3-T4 (`TIE_RANK`, so ID and BANK beat PHONE on identical spans); `prototype/privacy-check.html`; ADR 0008 amendment. The run-on of an ID value is a known limit (plan 22) |
| 5 | The union of overlapping spans is for `NER` spans only. `RULE` and `PATTERN` spans are not joined | Q9; plan 9, 21 | S4-M3-T4 (`union_ner`) |
| 6 | Hybrid at the governing-law place: a `PERSON` or `COMPANY` span that touches the kept place stays whole, and every other kind is cut at the place. The AI cannot read the governing law in that one clause, so the label turns unsure and the user sees it. Reason: a leak is worse than an ugly output, and code cannot know whether the place word belongs to the name. In 510 real contracts no finder span touched a kept place | Q14, Q9; plan 25 | Spec 4.2 (Kept line); ADR 0008 amendment; S4-M3-T3 (`cut_in_places`, 46 tests), S4-M3-T6 (one expected span), S4-M3-T11 (property P12) |
| 7 | `pat` stays in the layer 3 word list, and both tests that depend on it stay | Q17, Q1; plan 18 | S4-M2-T1 (`COMMON_WORD_NAMES`); S4-M2-T7 (`test_name_before_a_job_title` and `test_layer3_pat_at_a_sentence_start_is_left`) |
| 8 | Every property test runs 1,000 examples, including the properties of S4-M4-T6 | Q9, Q7, Q8; plan sections 5 and 8 | S4-M3-T11 (the `SETTINGS` object); S4-M4-T6 uses the same object; plan section 8 rows of 21 Nov |
| 9 | Plan questions 1, 4, 12 and 17 as recommended (one batch) | Q1, Q4, Q12, Q17; plan 1, 4, 12, 17 | S4-M2-T7; S4-M2-T1 and S4-M2-T4; S4-M3-T7; S4-M1-T6, S4-M2-T1, S4-M2-T4 and S4-M2-T7. Where this report recommended more than the plan holds, the status lines say so |
| 10 | Every other open plan question as recommended | Q2, Q3, Q6, Q7, Q8, Q11, Q13, Q15, Q16; plan 2, 3, 6, 7, 8, 11, 13, 15, 16, 19, 20, 21, 22 | The tasks named in the third column of section 6 of the plan (plan question 23 was answered differently: row 14) |
| 11 | Plan question 24 reversed to this report's version: four more patterns are built in stage 4 (NINO, Luhn card, bare GB VAT, company prefixes) | Q15; plan 24, 15 | S4-M2-T12 (35 tests); Spec 13 line; ADR 0008 amendment; plan section 6 rows 15 and 24, the known limits of S4-M5-T4, section 7 |
| 12 | A card number gets the kind `BANK`. The gate is the Luhn check, 13 to 19 digits, and a cue word within 40 characters before or a first digit of 3, 4, 5 or 6 | Q15; plan 26 | S4-M2-T12 (`card_is_valid`) |
| 13 | M3 tasks T7 to T10, M4 and M5 are not simulated by a cheap implementer, by the owner's choice | none; plan section 8 | Plan section 8 (rows of 21 Nov 2026) |
| 14 | Over-long address: truncated chain, decided 22 Nov 2026 | Q3; plan 23 | S4-M2-T6 (`_truncated_start`) |

None of this is legal advice or a legal position. The privacy step still produces pseudonymised text with a local map (ADR 0016).

**Historical note on decision 3.** The second revision of this report sketched the doubt list as appended stage 1 tasks, with five codes (`SHORT_NAME`, `NEAR_DUPLICATE`, `TWO_KINDS`, `SKIPPED_COMMON`, `NO_CUE_RUN`). The owner chose option B, and S1-M6-T8 carries that shape. The sketch is no longer a proposal and is not repeated here.

## Executive summary

The plan's architecture holds: cue-driven finding, variants found everywhere, source-priority overlaps, whole-text detector call, exact-match restore, and the `⟦ ⟧` marker with escape. Research found no reason to replace any of these. It did find **real defects in the exact rules and regexes of section 6 and of the tasks S4-M2-T1 to S4-M2-T7 and S4-M3-T1 to S4-M3-T7 that would leak or mis-label**. Track A2 reproduced all eight defects it tested (22 plan tests fail, 42 pass). Track A1 measured them on 367 invented snippets: the plan's rules cover 68.9% of reachable spans and leak 979 letters and digits, against 98.6% and 25 for the replacement rules. That corpus is an upper bound. Track B1 on 510 real contracts is a floor: party names are mostly not found by cue rules alone (Test results, "A ceiling and a floor").

**Verdicts at a glance** (details in the entries; the status after the owner's answers is the last line of each entry):

| # | Question | Verdict | One-line reason |
|---|---|---|---|
| 1 | Find a person name by code | CHANGE | `CAP` truncates real names (A1: hard-name group 26 of 97 covered, against 97 of 97); all-caps signatures, labels and contact lines are missed |
| 9 | Overlap order, cut not drop | KEEP + 2 amendments | Source-priority-then-cut is sound (A3: properties pass). Union for NER only (decided by the owner). Cut instead of drop at the governing-law place (A3 P11: a real defect); a PERSON or COMPANY span that touches the place stays whole (owner, 21 Nov) |
| 17 | Months and common words | CHANGE (partial) | Base rule is a floor; add a legal-word veto and a strong-cue bypass; layer 3 now recommended, layer 4 off; the owner chooses the leak trade |
| 2 | Company or person | CHANGE | Three reproduced false positives (A2) and 8 of 8 `Limited Warranty`-type hits in A1; suffix list too short |
| 3 | How far an address runs | CHANGE | A1: plan 18 of 46 address spans covered, replacement 46 of 46; postcodes and unit prefixes leak |
| 4 | Name variants, defined-term short names | CHANGE (additions) | Add initial, surname-first, suffix, hyphen and particle forms with guards; keep the short-name rule. Not measured in A1 (no typed-party path) |
| 5 | ID span includes keyword | DECIDED by the owner: value-only | A1: same recall and leaks, 286 fewer over-masked characters; the kind-order trap is still untested |
| 6 | What "restore" means | KEEP | Three jobs, three rules; strict exact match is right. B2: the explicit instruction removed every mutilation (0 of 152 replies) |
| 7 | One detector call | KEEP + contract | Whole text at the port; fail-closed; A2 and A3 show the offset gaps |
| 8 | Span across a sentence start | KEEP | Cut and keep both pieces (A3: split properties pass 5000 examples each) |
| 10 | Escape form | KEEP (decided by the owner) | Token form `⟦ ⟧` stays. B2: +3.65 tokens per placeholder on a Claude model; copy instruction needed |
| 11 | Defined term and allow-list | CHANGE | A2 reproduces the leak for a non-typed party such as `Mercury Logistics Ltd ("Mercury")` |
| 12 | Short form fitting two people | KEEP + clarify | Own placeholder is right; decide by "who generates this form", not by token subset. Not measured |
| 13 | Position text is stage 8 | KEEP + note | Fine for sequencing; record the shared-replacer contract now; case rule conflicts with Q17 |
| 14 | Governing-law place kept | DECIDED by the owner: closed list | A1: plan regex drops a person name in 6 of 12 over-capture cases; B1: 134 places kept in 128 contracts, against 22 in 22 (437 contracts have a governing-law annotation) |
| 15 | Which patterns | CHANGE (adopted; scope widened by the owner on 22 Nov; phones changed) | Bracketed phones: plan 0 of 6, replacement 6 of 6. No cue gate for spaced national numbers. NINO, card, GB VAT and company prefixes are built in S4-M2-T12 |
| 16 | Who owns word lists | KEEP | Small owner-owned code constants; do not vendor SSA or Census lists in stage 4 (rule conflict flagged) |

**Leaks and defects found in the plan text before the 21 Nov 2026 revision (most serious first; the revised plan carries a fix for each, see the status lines).** Items 1, 2, 3, 4 (partly), 5 and 6 are reproduced in A2. Item 7 is untested.

1. **`drop_in_places` (S4-M3-T3) drops a whole span** that touches the kept place. A RULE address next to "England and Wales" loses its masking entirely. A3 property P11 finds it independently on random input. A2 reproduced it only with an injected span (caveat in "Test results").
2. **`GOVERNING_LAW` (S4-M3-T3) over-captures.** `governed by the laws of England Sarah Jones signs` captures `England Sarah Jones`, and `drop_in_places` then removes the RULE person hit on "Sarah Jones" (A2: reproduced; A1: 6 of 12 such spans leak, 60 letters). It also under-captures: `the laws of the State of Delaware` gives no match.
3. **`CAP` truncates names (S4-M2-T7).** `Signed by Sean O'Brien` gives `Sean O'`; `Ann McDonald` gives `Ann Mc`; `SARAH JONES` gives nothing (A2: 6 of 6 name subcases fail). The truncated seed leaves `Brien` or `Donald` in the sent text.
4. **Detector failure and bad offsets.** The port says "Raises: None" and `trim_suggestions` (S4-M3-T1) does not reject reversed or bool offsets (A2: confirmed for reversed, start past text and bool). A failed detector can be read as "nothing found". Fail-closed is required.
5. **Q11 leak.** A defined term for a name that no typed party carries stays allowed, so a later detector flag on it is silently dropped (A2: reproduced).
6. **ADDRESS and COMPANY regexes** (S4-M2-T6, S4-M2-T5) leave postcodes, units and US ZIP codes outside the span, and match "Provider Limited Warranty" as a company (A2: 4 of 4 and 3 of 3 subcases fail).
7. **Kind order trap (my finding, from `core/enums.py`).** `PlaceholderKind` runs PERSON, COMPANY, ADDRESS, EMAIL, PHONE, ID, BANK. With value-only ID spans (decided), an ID and a PHONE hit on the same digits have equal length and the kind index lets PHONE win. A1 never put two kinds in competition on the same characters, so this is reasoning, not a measurement.
8. **One-word forms skipped silently (Q17).** A stop-listed word in a typed party's name (`May Lee`, `Will Price`) is never masked on its own. A1 measured it: a bare `Contact Will` leaks 25 letters across 6 spans in every rule set. It is a deliberate trade in the plan, but it is a leak direction and the owner should see it as one.

## Entries, biggest first: questions 1, 9 and 17

### Q1. How code alone finds a person name like Sarah Jones

**(a) Plan's current choice (S6 row 1).** "Three rules: an honorific and one or two capitalised words ('Ms Jones'); a capitalised name of two or three words after 'by' in a sentence that starts with 'Signed' or 'Executed'; a capitalised name of two or three words before a comma and a job title (Director, Manager and the others in `TITLE_WORDS`). Each name found also gives its variants, found everywhere in the text." A name that is a company gives no person.

**(b) Verdict: CHANGE.** Keep the architecture (cue finds a seed, seed expands to variants). Replace the name-token fragment and add cues.

**(c) Evidence.**
- Real tools do not offer a rule-only person recogniser. Presidio takes PERSON from a trained NLP model and uses regex plus context words only for structured items ([Presidio entities](https://presidio.dataprivacystack.org/supported_entities/), [customising the analyzer](https://presidio.dataprivacystack.org/samples/python/customizing_presidio_analyzer/)). scrubadub delegates names to Stanford NER, spaCy or TextBlob ([scrubadub names](https://scrubadub.readthedocs.io/en/stable/names.html)).
- The nearest rule-and-list system, Philter, reached recall 99.46% and 99.92% but precision about 78% on two clinical corpora ([Philter paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC7156708/)). An independent test on Australian GP notes found its name recall was 87% and its aggregate recall 67%, so the 99% does not travel ([El-Hayek et al. 2023](https://pubmed.ncbi.nlm.nih.gov/36870249/)). Lesson: name lists used as detectors cost precision. A cue-first design with lists only as vetoes is the sound response, and this is why the plan's shape is right (the researcher's agreement with the plan rests on this, not on anchoring).
- A legal-anonymisation review says one person must be linked across forms ("Doe" and "John D.") and that NER alone is "not enough" ([Symmetry 2021](https://www.mdpi.com/2073-8994/13/8/1490)).
- Re-run by me, plan fragments: `Signed by Sean O'Brien` gives `Sean O'`; `Ann McDonald` gives `Ann Mc`; `SARAH JONES` gives nothing. The researcher's replacement fragment matched all of `Sean O'Brien`, `Ann McDonald`, `Ana Smith-Jones`, `Sarah J. Jones`, `Mohamed ben Ali`, `Jean de la Cruz`, `Karim Benali`, `Ted DeSouza`, `Anna Maria Smith` (re-run, all whole) and not `the Board`.
- Re-run caveat: `Signed by Pat Kelly Director` gives `Pat Kelly Director` with the new fragment, so a trailing-title trim is needed (as the researcher said).
- Nearest real numbers, from newswire and not legal text: in Mikheev, Moens and Grover (EACL 1999, MUC-7), rules that fire only with a cue gave PERSON recall 40 and precision 99 (Fig. 3). Later stages with partial matches, a model and a first-name list reached recall 95 and precision 97. List lookup alone gave recall 26 to 47 and precision 81 to 92 (Fig. 1). With full gazetteers PERSON scored recall 96 and precision 98; with none, 90 and 95 (Fig. 4), so gazetteers added about 6 points of recall ([ACL E99-1001](https://aclanthology.org/E99-1001.pdf)). Reading: a cue-gated rule has high precision and low recall, and the plan's typed-party exact match is the higher-recall mechanism. Mikheev also applies "known first name plus unknown capitalised word" late, after trying the run as a company (section 3.5), which fits the plan's order in Q2.
- Legal filings: a dictionary-lookup baseline on E-NER (52 SEC filings, one annotator, all entity types merged) scored micro-F1 0.491 in-domain and 0.136 when trained on CoNLL-2003. A feature-based CRF without lexicons scored 0.902 in-domain and 0.216 cross-domain (Table 3, [arXiv 2212.09306](https://arxiv.org/abs/2212.09306)). No person-only split is given.
- Clinical rule and dictionary systems: PhysioNet deid reached PHI recall 0.943 on 1,836 nursing notes (development set: recall 0.967, precision 0.749) and missed no patient names ([PMC2526997](https://pmc.ncbi.nlm.nih.gov/articles/PMC2526997/)). Its frequent false positives include "will".
- TAB (ECHR cases) has no rule-only baseline. Table 7: neural NER direct-identifier recall 0.940 with precision 0.441; default Presidio 0.460, mainly because it missed case numbers ([arXiv 2202.00443](https://arxiv.org/abs/2202.00443)). TAB supports one design point: report direct-identifier recall apart from mention-level recall.
- scrubadub's `TextBlobNameDetector` (off by default) takes every word tagged as a proper noun and finds it everywhere. It has the same seed-then-find-everywhere shape as the plan but no cue, so any proper noun becomes a name ([text_blob.py](https://raw.githubusercontent.com/LeapBeyond/scrubadub/master/scrubadub/detectors/text_blob.py)).
- Weak sources only: a 2026 regex-versus-Presidio preprint (vendor-employed authors, 100 synthetic resumes) found a regex-only redactor missed all 100 reference names, and the authors did not test an "any two capitalised words" rule ([arXiv 2611.07633](https://arxiv.org/abs/2611.07633), Table 3 and section 7.1). Garat and Wonsever (2019) report 84 percent of legal documents hold a name that tested NER tools miss; the abstract was the only text read ([SciSpace record](https://scispace.com/papers/towards-de-identification-of-legal-texts-44oxx0gk5b)).
- Confirmed absent: no paper, benchmark or tool report evaluates a rule-only person-name finder on contracts, and no contract corpus (CUAD, ContractNLI, LEDGAR) has person-name annotations. A first measurement on real contracts now exists for party names only (B1, in 'Test results'); person-name recall is still unmeasured. Still open from the earlier pass: Presidio's registry code not read line by line.
- **Test evidence (A1, A2, B1).** On the 97 reachable spans of seven hard-name groups (O'Brien, McDonald, Smith-Jones, capitals, de la Cruz, ben Ali, Sarah J. Jones) the plan covers 26 and leaks 491 letters; the replacement covers 97 of 97 with 0 leaks. A2 reproduces all six name subcases. The trailing-title trim removes the plan's `Mei Varga President` over-mask (47 characters, plus 6 hits on a bare `President` elsewhere): the replacement has 0 and 0. The lead-word trim helps only for listed verbs (`Send Elif Osei`: 28 over-masked characters to 0); for unlisted ones (`Attention`, `Dear`, `Forward`) both rule sets over-mask 40 characters. Neither rule set fixes bare names with no cue (0 of 24 spans, 233 letters), the first name after a surname-only cue (0 of 25 spans; 185 letters leaked by the plan, 138 by the replacement), or `Jones, Sarah` with no cue. On 510 real contracts the replacement rules predict 2,805 PERSON spans (10.46 per 100 KB) against 1,256 (4.68) for the plan. That is density, not precision. The replacement still fully covers only 16.1% of annotated party answers, so cue rules alone do not find most parties (see 'A ceiling and a floor' in 'Test results').

**(d) Exact plan edit (S4-M2-T7, `_patterns.py`, `people.py`).**

Replace `CAP` and `NAME_RUN` for names (keep the old `CAP` for addresses if S4-M2-T6 needs it, but see Q3). With `H = [ \t]`:

```text
PART  = (?:van|von|der|den|de|la|le|da|di|del|bin|ibn|bint|ben|ould|dos|du|al|el)
TOK   = (?:[A-Z](?:['’][A-Z])?[a-z]+(?:[A-Z][a-z]+)*(?:-[A-Z]?[a-z]+)*)
INIT  = (?:[A-Z]\.)
NAME_RUN = TOK(?:H+(?:INIT H+|PART H+)*TOK){1,3}   # last token is always a TOK
```

Do not put `UK`, `USA`, `UAE` in a name token. Then add these rules, in this order, each returning a seed and a RULE PERSON span:

1. Honorific plus `TOK` (one or two tokens). The honorific is case-insensitive (`MS JONES`). Cue list adds `Prof, Sir, Lady, Lord, Rev, Hon` (cue only, not generated as forms unless the owner wants it).
2. `Signed|Executed ... by NAME_RUN` (existing, with the new fragment), plus an all-caps form: `(?i:signed|executed)\b[^.\n]*?\b(?i:by)H+(CAPS_RUN)` with `CAPS_TOK = [A-Z]{2,}(?:['’-][A-Z]+)*` and `CAPS_RUN = CAPS_TOK(?:H+CAPS_TOK){1,2}`; and `/s/ NAME_RUN`.
3. Label line: `(?im)^[ \t]*(?:Name|Print name|Full name|Signatory|Authorised signatory|Witness|Attention|Attn|FAO|For the attention of|Contact)[ \t]*[:\-][ \t]*(NAME_RUN)`.
4. Name before a title with a comma (existing).
5. Name followed by contact detail: `(NAME_RUN)H*[,(<]H*(?:EMAIL|PHONE)` and `(NAME_RUN)H*,H*\d+[A-Za-z]?H+TOK`.
6. Individual-party cue: `(NAME_RUN)H*,?H*(?:an individual|a sole trader|trading as|of \d|residing at|whose address)`.

Post-match code rule for every run: drop trailing tokens in `TITLE_WORDS` or `LEGAL_STOP`, drop leading tokens in `LEAD_STOP` ("The", "This", "Each"), then require two tokens (one after an honorific). Run the veto on every token, because `SIGNED BY AGREEMENT PARTY` matches the all-caps rule (researcher-tested). A seed whose tokens are all in `LEGAL_STOP` is rejected even with a cue. Months and days are handled by a date veto, not by this rule: a month or day token is not a name when the previous token is a digit, or the next token is a digit, a four-digit year, `of`, or a comma and a digit. So `Ms May` is kept and `1 May 2026` is not a name. (The first revision said months were vetoed even with a cue, which contradicted `Ms May`. A1 vetoed only all-legal-word seeds. The date veto comes from the court note and was not run.)

Owner-optional (Tier 2, only in the opening preamble, first 1,500 characters): `(?:between|and)H+(NAME_RUN)H*(?:\(|,|of\b)` and a run directly before a definition bracket `(NAME_RUN)H*\(H*(?:the\H+)?["“‘]`. Not recommended: a bare capitalised pair whose first word is in a first-name list ("Sarah Jones said"). That is the stage 7 detector's job, and if ever added it must report "unsure".

Tests to add to the owner's `finders.toml` (S4-M2-T8), values written by the owner: `Signed by Sean O'Brien`, `Ann McDonald`, `Ana Smith-Jones`, `SIGNED BY SARAH JONES`, `Signed by Pat Kelly Director` (gives `Pat Kelly`), `Name: Sarah J. Jones`, `Sarah Jones <sarah@x.example>`, `Signed by Party Schedule` (nothing), `MS JONES`, `14 Oak Dr Leeds` (address, not "Dr Leeds"). Re-run the sample: the plan states it finds exactly Sarah Jones, Ms Jones and Karim Benali and nothing else, so the owner must re-confirm that after the changes.

Note on `Dr` as "Drive": the plan's order (equal priority, then longer first) already lets the longer address beat a contained `Dr Leeds`. It needs a test row, not a new priority.

**(e) Risk if the owner picks the other option.** Keeping `CAP` leaves the tail of any apostrophe, `Mc`, hyphenated or particle name in the sent text, and misses upper-case signature blocks, which are common. This is a direct leak. Over-widening instead (adding the weak cues or a first-name list) buys recall at about the Philter precision cost and breaks checking.

**Status (22 Nov 2026):** Decided as the plan carries it (plan question 1, as recommended; decision 9). S4-M2-T7 builds three cue rules: an honorific (also in capitals), `Signed` or `Executed ... by` (also in capitals), and a name before a comma and a job title. It has a name token that keeps `O'Brien`, `McDonald`, `Smith-Jones` and `al-Rahman` whole, and trims for lead words, trailing job titles and legal words (`LEGAL_STOP_WORDS`). Not in the tasks: label lines, the contact-detail and individual-party cues, `/s/`, a separate date veto, the preamble cues and the orphan run. The owner writes the expected values (S4-M2-T8). The CUAD floor stays open (see 'Open owner questions').

### Q9. Overlap order, and cutting a lower span instead of dropping it

**(a) Plan's current choice (S6 row 9).** "The order is USER, PARTY_DETAILS, PATTERN, RULE, NER, then the longer span, then the earlier start. A lower span is cut to the parts outside every kept span, and a part with no letter or digit is dropped." The other way, dropping the lower span whole, "leaves such a fragment".

**(b) Verdict: KEEP, with two amendments.** Amendment 1 (union, for NER spans only) and amendment 2 (cut at the place, hybrid for PERSON and COMPANY spans) are decided by the owner and written into the plan (see the status line).

**(c) Evidence.**
- Presidio's anonymizer offers `REMOVE_INTERSECTIONS`, which trims the lower-scored of two partly overlapping results to the part outside the higher one and drops only results trimmed to nothing. It trims only partial overlaps: a contained result is dropped earlier, before any trimming, so it never splits a container around a contained span (read in source) ([Presidio anonymizer API](https://presidio.dataprivacystack.org/api/anonymizer_python/), [source](https://github.com/microsoft/presidio/blob/main/presidio-anonymizer/presidio_anonymizer/anonymizer_engine.py)). Its default strategy merges same-type intersections (any score), then drops any result contained in another of any type, so a higher-scored contained span loses to a lower-scored container. Issue 1156 documents this, is still open, and PR 2287 (an opt-in strategy to keep a higher-scored contained entity) is open too ([issue 1156](https://github.com/data-privacy-stack/presidio/issues/1156), [anonymizer_engine.py](https://raw.githubusercontent.com/microsoft/presidio/main/presidio-anonymizer/presidio_anonymizer/anonymizer_engine.py)). The analyzer's own `remove_duplicates` compares same-type spans only, and the default `merge_entities_with_spaces` also merges same-type results separated only by spaces, so "Sarah Jones Tom Jones" would become one span. Presidio ranks by score; this app has no score on `PiiSuggestion`, so source priority is the correct replacement key (researcher's inference; I agree, scores from a checksum, a regex and an NER model are not comparable).
- scrubadub unions every overlap into one filth, regardless of type (verified in source; touching spans merge too, only a strictly positive gap keeps them apart, whereas the plan keeps touching spans separate) ([scrubbers.py](https://github.com/LeapBeyond/scrubadub/blob/master/scrubadub/scrubbers.py)). spaCy `filter_spans` keeps the first longest span and drops the rest whole, but it is built for annotation, not redaction ([spaCy util](https://github.com/explosion/spaCy/blob/master/spacy/util.py)).
- DeidSharp (a 2026 single-author preprint, built with an AI coding assistant, so a design reference only) replaces the union of all detectors and counts a gold span as found if any prediction touches it, because an untouched span is leaked ([arXiv 2611.12709](https://arxiv.org/abs/2611.12709)).
- Presidio's own source records two real defects a property test would catch: merging unsorted results left text in the clear, and sorting by start only left shorter results unresolved.
- The plan's sort key (priority, then negative length, then start, then kind index) is a total order, so output does not depend on input order (researcher's reasoning, which holds on the plan's key at plan line 415).
- DeidSharp's union of all spans and its lenient "any prediction touches the gold span" recall are confirmed (Sec. 3 p3, Sec. 3.5 p5); the paper itself calls that metric lenient next to strict matching (Limitations p11).
- Presidio's keys are score-based with order as tie-break, so they are no model for the plan's source-priority key. Presidio's union is by type regardless of source; the plan's same-kind, same-source union is a design choice, not Presidio behaviour.
- Gaps: Philter's precedence is **unverified**. The only extract came from a model extraction of `philter.py`; it suggested that config order decides, the first filter to claim a span wins, and `regex_context` filters override the opposite map. Re-read the file before quoting. Presidio's handling of touching spans was not read, and its merge of different-type partial overlaps was read in source, not run. No paper compares overlap rules for de-identification output.
- **Test evidence (A3).** Hypothesis properties P1 to P9 pass 5000 examples each on the plan's resolver (disjoint and sorted; no letter or digit lost; no invention; priority; idempotent; order-independent; monotone; identity on clean input; split keeps kind and source). One real defect: P11, the composed pipeline. A detector span that runs into the governing-law place is dropped whole, and the part outside the place leaks (shrunk case: a NER PERSON span over `governed by the laws of England`, place `England and Wales`). With the place cut instead of dropped, P11 passes 5000 examples. The union step passes the same properties and changes 5 of 5000 random cases for NER and 8 of 5000 for NER, RULE and PATTERN together. It fixes the note's example (`Sarah Jo` and `ah Jones` become one span, where the plan gives `Sarah Jo` and `nes`).

**(d) Exact plan edit.**

1. **Decided by the owner and written into the plan (S4-M3-T4, `union_ner`).** S4-M3-T4 `resolve_overlaps`, add a first step before sorting: for source `NER` only, union every group of suggestions that has the same `kind` and whose spans overlap (`a.start < b.end and b.start < a.end`; touching spans stay separate). Never for `USER` or `PARTY_DETAILS`. Cross-kind and cross-source spans are untouched. The companies note argued the same for RULE address spans (street-only and postcode chain overlapping partially); that variant stays optional and undecided. My first revision recommended all three sources. A3 shows the extra step changes little (8 of 5000 cases, against 5 for NER alone), so I now recommend NER only for stage 4, and a second look if the new address chain ever leaves a split span.
2. S4-M3-T3 `drop_in_places`: replace "drop whole" by "cut", using the same helper as `resolve_overlaps` (subtract the place spans, keep remainders that contain a letter or digit). Exception, my synthesis and not researched: if the overlapping suggestion is kind PERSON or COMPANY, keep it whole and let the place lose the overlap, because a name that touches the place is safer masked in full. A3's diagnostic cut applied to all kinds and passed P11; the PERSON and COMPANY exception was not run. **Decided by the owner on 21 Nov 2026 (hybrid, decision 6): the exception is adopted for `PERSON` and `COMPANY` spans; every other kind is cut.**
3. Add the testable invariant to the plan: every alphanumeric character covered by any input span is covered by exactly one output span; resolution only changes which label covers it.
4. Add the eleven Hypothesis properties of the overlaps note, written as invariants, not expected answers (disjoint and sorted; no leak; no invention; priority; idempotent; order-independent; monotone; identity on clean input; split keeps parent kind and source; validator raises exactly on bad spans; composed pipeline loses nothing). Add example cases: three sources on identical spans, three-level nesting, a chain of partial overlaps, a word-tail remainder, a combining-mark remainder, a punctuation-only user span.

**(e) Risk if the owner picks the other option.** Drop-whole leaves "Sarah" in the text (the plan's own example). Longest-wins lets a long NER guess swallow and relabel a user mark. Union-everything (scrubadub) is safest for coverage but loses which party or user mark a span is, which entity grouping needs. Skipping amendment 1 yields two adjacent placeholders for one person or address. Skipping amendment 2 leaks the part of a span outside the place.

**Status (22 Nov 2026):** KEEP, with both amendments decided and written into the plan. Source priority, then the cut: S4-M3-T4 (`resolve_overlaps`, `SOURCE_PRIORITY`). Union for `NER` spans only: S4-M3-T4 (`union_ner`; decision 5; plan questions 9 and 21). A union for `RULE` and `PATTERN` spans is not built. The verdict changed at the governing-law place to the hybrid: `cut_in_places` (S4-M3-T3) keeps a `PERSON` or `COMPANY` span whole where it touches the place and cuts every other kind (decision 6; plan question 25; Spec 4.2 holds the clause). The properties P11 and P12 are in S4-M3-T11; the planner ran them on the reference code at 5,000 examples with no failure.

### Q17. Months and common words are not names

**(a) Plan's current choice (S6 row 17).** "A one-word form counts only where its first letter is a capital in the contract... It is also skipped when it is in a stop list of month names, day names and these words: will, mark, grant, bill, page, price. Forms of two or more words ignore case. The owner may add words to the list."

**(b) Verdict: CHANGE (partial).** The base rule is sound as a floor. Add a veto for legal words and a bypass for strong cues. The further layers are a choice between privacy and checking and need the owner. After A1 I recommend layer 3 and keep layer 4 off.

**(c) Evidence.**
- Philter found 16,095 census or SSA names that are also medical terms or common English words and removed 855 from its blacklist to recover precision ([Philter paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC7156708/)). Mikheev (2002) puts about 20 percent of named entities in ambiguous capitalised positions (sentence start, after a colon or quote, titles, list entries) and resolves them with repeats of the same word elsewhere in the document plus local cues ([ACL Anthology J02-3002](https://aclanthology.org/J02-3002.pdf); the introduction was read, the evaluation tables were not, so no error rates are quoted). Mikheev et al. (1999) treat a gazetteer first name as "likely", not certain, and check the context ([E99-1001](https://aclanthology.org/E99-1001.pdf)). PhysioNet deid lists "will" among its top false positives (5 in the development notes) and leaves common words alone unless a name cue or a neighbouring potential name is present ([PMC2526997](https://pmc.ncbi.nlm.nih.gov/articles/PMC2526997/)). The 2026 regex-versus-Presidio preprint says its test names did not probe names that are also common words ([arXiv 2611.07633](https://arxiv.org/abs/2611.07633), section 8).
- Context cues (`Mr`, `Signed by`, `Name:`) are the standard way to raise confidence for a weak match ([Presidio context enhancer](https://presidio.dataprivacystack.org/samples/python/customizing_presidio_analyzer/)).
- Confirmed absent: no source gives a false-positive rate per word (Will, Mark, Grant, Bill, Page, Price, months) or any precision or recall for capitalisation or document-evidence rules on contracts. A stop list of months and a few common words stays a design choice. The cue-first order has support (Mikheev's stage 1 on newswire: recall 40, precision 99), but not on contracts. The `COMMON_WORD_NAMES` and `LEGAL_STOP` seeds come from general knowledge, not a cited list.
- **Test evidence (A1, B1).** Months at sentence starts, `Ms May` and `May Lee`: 0 leaks and 0 false hits in every rule set (HONMAY 6 of 6 spans with 14 month distractors, MAYLEE 12 of 12 with 10, MONTH_START 5 of 5 with 21). `Will Price`, `Grant Mills`, `Mark Page`, `Bill Rowe`: the two-word forms are found, but a bare `Contact Will`, `Contact Grant` or `Contact Bill` leaks (6 spans, 25 letters) in every rule set. That is the stop list's price, and the numbers do not support removing those words from it. `Rose Hope`, `Frank Day`, `Art Lane`: a bare sentence-initial `Hope`, `Frank` or `Lane` is masked as a person in 6 of 6 cases (25 over-masked characters); layer 3 cuts that to 2 of 6 (8 characters) with no new leak, but the layer 3 word list overlaps the test words, so the gain is an upper bound. On 510 real contracts, PERSON predictions whose first token is in the month, day, legal-word or common-word list: 4 of 1,256 for the plan (all `frank`) and 12 of 2,805 for the replacement (`mark` 8, `frank` 4). Counts cannot show whether those are real names, so this is not a win for either rule set.

My check of the reasoning: the researcher's four layers are a design judgement, not a result. Layers 3 and 4 **reduce** masking, and the project rule is that leaks are worse than over-masking. A typed party "Will Price" would then leave a sentence-initial "Price" in the text. The researcher states the trade openly ("a leak is possible for a bare May") and leaves it to the owner, which is right.

**(d) Exact plan edit (S4-M2-T1 for `NAME_STOP_WORDS`, S4-M2-T4 for the one-word forms of typed parties, S4-M2-T7 for cue-found seeds).**

Adopt now (low risk, mostly vetoes):
1. Layer 1, strong cue bypass. A seed from an honorific, signature, label, name-before-title, contact or individual-party cue is accepted even when a token is in a stop list (`Ms May`, `Signed by Will Price`). A seed whose every token is in `LEGAL_STOP` is rejected even with a cue. Months and days are vetoed by the date veto of Q1 (a month or day next to a digit or a year), so `Ms May` stays accepted.
2. `LEGAL_STOP` veto on every token of every cue-found run, and for trimming (seed list in Q16). **Do not merge `LEGAL_STOP` into `NAME_STOP_WORDS` for forms made from a typed party or from a defined-term short name**, or a party called `Agency Ltd` or a short name like "Studio" loses its one-word form (see Links, Q4/Q11/Q17).
3. Layer 2, hard list: keep the plan's `NAME_STOP_WORDS`; add abbreviated months only when followed by a digit or a full stop, and keep `Jun`, `Mar` in a separate set that vetoes one-word forms only.
4. Replace the unit test row "stop list" by a row per seed word, each with one sentence-initial and one mid-sentence use.

Owner decision (apply only if the owner accepts the leak trade; after A1 I recommend layer 3, with layer 4 off):
5. Layer 3. For words in `COMMON_WORD_NAMES` only, a capitalised one-word form counts only when it is not the first word of a sentence or after a clause number, and the line is not a heading, unless followed by `'s` or `’s` or preceded by an honorific.
6. Layer 4. If the same folded word occurs in lower case elsewhere in the document, treat it as a common word and apply layer 3's stricter rule. Recommended default: off. It adds a pass and reduces masking. Its only support is Mikheev's document-evidence method on newswire (evaluation tables not read), not contracts.
7. Add one `ambiguous_name_policy` constant so the owner can move a word between the hard list and the soft list without code change.
8. Whenever a form is skipped by layers 2 to 4, the design should call the case unsure, not clean. `PiiSuggestion` has no confidence field, so how to surface it is an owner design question (stage 12 screen or a note on the privacy screen). The doubt list in 'Owner decisions' (code `SKIPPED_COMMON`) would carry the fact; it does not decide the display.
9. Inference, not measured: move `will`, `mark`, `grant` and `bill` from the hard list to the layer 3 list. A capitalised mid-sentence `Contact Will` is then masked, and `Will the Supplier pay?` is still skipped. That would close the 25-letter leak A1 measured, at the price of masking some capitalised mid-sentence uses of the word. The plan did not take this (see the status line).

Test rows (owner writes the values): `1 May 2026 and 5 June 2026.` gives no person; `Ms May signs on 1 May 2026.` gives only `Ms May`; party `Will Price` with `The price will be paid. Will Price signs. Contact Will.`; party `Rose Hope` with `Hope is not a term.` and `Contact Hope.`; a `Price and Payment` heading; `Signed by Party Schedule`; `SIGNED BY SARAH JONES`.

**(e) Risk if the owner picks the other option.** Keeping only the plan's list leaves `Rose`, `Hope`, `Frank`, `Art`, `Ray` and the legal-word collisions untreated, so months and roles can become names, which breaks the checks the Spec 4.2 keep-list exists for. Adding layers 3 and 4 fixes that at the price of leaking a surname at a sentence start. Neither is free; the choice is the owner's.

**Status (22 Nov 2026):** Decided as the plan carries it (plan question 17, as recommended; question 18 for `pat`). Layer 2 (the hard list `NAME_STOP_WORDS`) and layer 3 (`COMMON_WORD_NAMES`, with evidence of a name) are built in S4-M1-T6, S4-M2-T1 and S4-M2-T4. Layer 4 is off. `LEGAL_STOP_WORDS` vetoes and trims cue-found runs (S4-M2-T7). This report's recommendation to move `will`, `mark`, `grant` and `bill` to layer 3 was not taken: they stay in the hard list, and a bare `Contact Will` stays readable as a known limit in the plan. `pat` stays in layer 3 (decision 7).

## Entries, the rest in order

### Q2. How code tells a company from a person

**(a) Plan.** A party is a company when its last word, without a final full stop or comma, is in: ltd, limited, llc, llp, plc, inc, corp, gmbh, ag, sarl, sas, bv, nv, pty, co. Every other party is a person. The same list drives the company rule in capitalised spellings.

**(b) Verdict: CHANGE.**

**(c) Evidence.**
- GLEIF's ISO 20275 list has over 3,600 legal forms in 200+ jurisdictions and says a form only has meaning under local law; it gives no short UK or US list ([GLEIF](https://www.gleif.org/en/lei-data/code-lists/iso-20275-entity-legal-forms-code-list)). So a short closed list is a design choice, not a standard.
- Organisation versus person is a known hard point: Google DLP's `ORGANIZATION_NAME` is ML-backed, AWS Comprehend files "John Doe Organization" as an organisation ([Google infoTypes](https://docs.cloud.google.com/sensitive-data-protection/docs/infotypes-reference), [AWS Comprehend](https://docs.aws.amazon.com/comprehend/latest/dg/how-pii.html)). Presidio has no organisation recogniser ([Presidio entities](https://presidio.dataprivacystack.org/supported_entities/)).
- Researcher-reproduced false positives of the plan's `COMPANY` regex: `Provider Limited Warranty` matches `Provider Limited`; `The Co-operative Bank Co-operation` matches `The Co-operative Bank Co`; `Pay Acme Ltd now` matches `Pay Acme Ltd`; `GmbH & Co. KG` stops before `KG`; `Smith and Sons Ltd` needs `and` as a connector.
- Gaps: OpenCorporates normalisation not fetched; Welsh `Cyf` unverified; no false-positive rates on real contracts.

- **Test evidence (A1, A2, B1).** 56 company spans: the plan covers 48 (25 letters leaked, 7 truncations); the replacement covers 56 with 0 leaks. Plan failures: `Bar GmbH & Co. KG` gives `Bar GmbH & Co` (6 of 6, leaks `KG`), `Smith and Sons Ltd` gives `Sons Ltd`, `Foo S.A.` is not found. Look-alikes: `Provider Limited Warranty` and its siblings hit 8 of 8 (125 over-masked characters), `Co-operative Bank Co-operation` 5 of 5 (90 characters); the replacement hits 0 of 13. A2 reproduces three of these. The contract-verb list is worth little: for six unlisted verbs (`Forward`, `Remit`) both rule sets over-mask 40 characters, and the typed-party path already covers real parties. On 510 real contracts the company density is 6.86 spans per 100 KB for the plan and 8.76 for the replacement (density, not precision).

**(d) Plan edit (S4-M2-T5, `_patterns.py`, with the suffix list it uses).**
- Tier A suffixes (case-sensitive, capitalised or upper-case): add to the plan's list `LP, Corporation, Incorporated, SRL, SpA, Oy, KG, UG, Pte` and dotted `S.A., S.A.R.L., L.L.C., L.L.P., P.L.C., N.V., B.V.`. Keep `SA`, `AB`, `AS`, `SE`, `Ltda`, `Pvt`, `Bhd` out (Tier B, dotted or all-caps only). Never a suffix: `Company, Group, Holdings, Partners, Associates, Bank, Services`.
- Replace the regex with the researcher-tested form: `COMPANY = (?<![\w])(?:WORD)(?:H+(?:WORD|&|of|and)){0,5}H+SUF`, with `WORD = [A-Z][A-Za-z0-9'’&-]*`, a `SUF` that ends in `(?![-\w])` and, for `Limited`, a lookahead refusing `Liability|Warranty|Partnership|Licen[cs]e`, and an optional ` KG` after `Co\.?`. Include the full stop only for dotted abbreviations, never for `Ltd.`, `Inc.`, `Co.`.
- Add contract verbs and nouns to `COMPANY_LEAD_WORDS`: `Pay, Payment, Notice, Invoice, Deliver, Send, Contact, Between, Agreement, Services, Client, Customer` (owner list, Q16).
- Add two cues, RULE source, lower priority than a suffix match: `for and on behalf of X` / `on behalf of X` (capitalised run up to a comma, `(` or line end), and `X (a company registered|incorporated in ...)` / `X, a company ...`. `Name:` and `Signed by` values stay persons.

**(e) Risk.** Keeping the 15-word list and the old regex mislabels "Provider Limited Warranty" and "Pay Acme Ltd". A bigger or looser list adds false companies. One further consequence for the owner: a typed party with no suffix (`Brightline Studio`) is treated as a person, so `Studio` alone becomes a person form. That over-masks, which is safe, but a `kind` on `Party` would be cleaner and changes system design 3.4 (not done: plan question 2 was answered as recommended).

**Status (22 Nov 2026):** CHANGE, adopted (plan question 2, as recommended). S4-M2-T5 carries the revised company rule. A typed party is a company by the 15 suffixes of `COMPANY_SUFFIXES` only. `EXTENDED_COMPANY_SUFFIXES` (adds `lp`, `corporation`, `incorporated`, `srl`, `spa`, `oy`, `kg`, `ug`, `pte`) reads a company name that a rule found (S4-M2-T1, `is_company_seed`). A `kind` on `Party` is not added, so a typed party with no suffix stays a person and over-masks.

### Q3. How far an address runs

**(a) Plan.** "An address runs from the house number to the last town, postcode or country, joined by commas, as the prototype shows. The typed address also gives its first line as a variant."

**(b) Verdict: CHANGE.**

**(c) Evidence.**
- The standard approach is a postal-code anchor with a look at text on both sides ([address patent summary](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9558295); secondary). A 2022 paper found strict formatting rules give few false positives but many false negatives ([arXiv 2202.03103](https://arxiv.org/pdf/2202.03103)). AWS Comprehend's address example runs from house number through ZIP ([AWS Comprehend](https://docs.aws.amazon.com/comprehend/latest/dg/how-pii.html)). scrubadub excluded only a Bermuda postcode sub-pattern for false positives and still autoloads its GB postcode regex (corrected on reading the source, [postalcode.py](https://raw.githubusercontent.com/LeapBeyond/scrubadub/master/scrubadub/detectors/postalcode.py)).
- Researcher-tested defects of the plan regex: `at 5 Way of life` gives `5 Way`; `within 2 Court days` gives `2 Court`; `12 High Road, Leeds, LS1 4AB` stops at `Leeds`, so the postcode leaks; `Springfield, IL 62704` loses the ZIP; `Flat 2, 12 High Road` starts at the second number; `Unit 4, Alpha Park, Leeds, LS1 4AB` is missed.
- Gaps: no published false-positive rate for postcode-anchored regexes on contracts; libpostal not read.

- **Test evidence (A1, A2).** 46 address spans: the plan covers 18 (246 letters and digits leaked, 21 truncations); the replacement covers 46 with 0 leaks. The plan leaks the postcode after a comma (7 of 7), state plus ZIP (7 of 7), `Flat 2,` and `Suite 400,` prefixes (8 of 8) and a bare postcode (5 of 5). On 8 address look-alikes the plan hits 5 (`2 Court days`, `5 Way of life`) and the replacement 0. One cost: with a capitalised word and a number before the address, the chain starts too early in 3 of 6 adversarial cases (22 over-masked characters, no leak). `27 Rue Didouche Mourad, Algiers 16000, Algeria` works in both (4 of 4). A2 reproduces four subcases. Not generated: `Dr` as a street word and long address lists.

**(d) Plan edit (S4-M2-T6, `addresses.py`).** Keep the tightened street rule (for `Way, Place, Court, Row, Hill, Close, Drive, Square` require at least one capitalised word between number and street word) and add a postcode-anchored chain:
1. Anchors: UK postcode `UKPC`, US ZIP with state code required (`USZIP`), Canadian postcode (`CAPOST`); the exact regexes are in the researcher's note (companies_addresses_patterns, Q3). Four-to-six-digit EU codes are not anchors; they count only inside a chain that already has a house number (the plan's `POST` branch).
2. Take the 120 characters before the anchor; cut at the last hard stop (`; : ( ) [ ] "`, curly quotes, line break, or a sentence end not after `St`, `Rd`, `Ave`); split on commas; keep at most the last 5 segments.
3. Start token, in the first kept segment the last match and in later ones the first: `Flat|Unit|Suite|Floor|Room|Building|House + word`, `PO Box + number`, or a house number followed by a capitalised non-month word (this removes "1 May 2026"). A cue (`registered office at`, `address is`, `located at`, `whose address`) can set the start.
4. No start found: replace the postcode alone as ADDRESS; never guess a start.
5. End: the anchor, plus an optional `,? (?:United Kingdom|UK|England|Scotland|Wales|Northern Ireland|USA|United States|Canada)`.
6. Test rows (researcher-tested outputs): `Send to 14 Harbour Street, Leeds LS1 4AB.` gives `14 Harbour Street, Leeds LS1 4AB`; `Flat 2, 12 High Road, Leeds, LS1 4AB, United Kingdom` gives the whole string; `Suite 400, 1 Main St, Springfield, IL 62704, USA` gives the whole string; `Within 30 days of 1 May 2026, ship to LS1 4AB` gives the postcode only; `Pay 5 apples to Bob. He lives at 5 High St, Leeds LS1 4AB` gives `5 High St, Leeds LS1 4AB`; `27 Rue Didouche Mourad, Algiers 16000, Algeria` still works via the `LEAD_WORD` branch.
7. Over-length: the researcher wrote "cut at the earlier limit and keep it" yet also "a long unreplaced tail leaks". The plan must say which: recommended, when the chain would exceed the cap, take the whole run to the anchor and flag it long; do not leave a tail.

Because both rules are RULE ADDRESS and may overlap partially, Q9 amendment 1 (union of same-kind same-source spans) should apply.

**(e) Risk.** Keeping the plan regex leaves a postcode or "Flat 2" in the sent text, which is a direct identifier. The anchored chain is more code and more false hits on postcodes in non-address text, which over-masks and is safe.

**Status (22 Nov 2026):** CHANGE, adopted (plan questions 3 and 23, as recommended). S4-M2-T6 builds the tightened street pattern and the chain back from a postcode, with a cap of 5 comma segments and 120 characters. This report recommended taking the whole run when the chain is too long. The owner decided on 22 Nov 2026 (plan question 23, decision 14) to keep a truncated chain instead of the postcode alone: the span starts at the earliest comma segment that keeps the chain within 5 segments and 120 characters, so the nearest part of the address is hidden; with no start token at all, or when the nearest segment alone is longer than 120 characters, the postcode alone is the span. S4-M2-T6 builds it (`_truncated_start`), and its tests carry the values.

### Q4. Exact name variants and short names from defined terms

**(a) Plan.** Person: full name; first and last when three or more words; first alone and last alone when 3 or more letters; honorific (mr, mrs, ms, miss, mx, dr) with or without a full stop before the last name. Company: with `Ltd` and `Limited`, and without the suffix. A defined term is a short name of a party when its words are all in the party's name (without suffix or honorific) and its defining sentence holds the full name. Possessives need no form. Case, curly quotes, soft hyphens and line breaks do not matter.

**(b) Verdict: CHANGE (additions only; keep the short-name rule).**

**(c) Evidence.** No published standard list of name variants exists, so this is design. Anonymisation must link "Doe" and "John D." ([Symmetry 2021](https://www.mdpi.com/2073-8994/13/8/1490)), and Presidio's PERSON covers first names, middle names, initials and last names ([Presidio entities](https://presidio.dataprivacystack.org/supported_entities/)). The researcher verified the short-name rule against the plan, and I agree: it correctly refuses `"Services" means ...` and role terms. Gaps: no name-order evidence for non-English names (the sample has `Karim Benali`); `nameparser` not checked.

- **Test evidence.** A1 exercised variants of cue-found seeds only (`Mr McDonald`, a bare `Sarah` after `Sarah J. Jones`). The typed-party path and the forms of S4-M2-T1 were not run, so every form below is untested. 'Ideas from nearby fields' adds a generation-suffix guard, an initial-compatibility check and a nickname rule that uses only the contract text.

**(d) Plan edit (S4-M2-T1 `name_forms`).** Add, each with its guard:

| Form | Rule | Guard |
|---|---|---|
| Initial plus last | `S Jones`, `S. Jones`, `Jones, S.` | Upper-case letter in the contract only; never for `A` or `I` without a full stop; matched case-sensitively, not on folded text |
| Surname first | `Jones, Sarah` | both tokens 3+ letters |
| Suffix handling | strip `Jr, Sr, II, III, PhD, Esq` before forming; add `Name Jr` | keeps `III` from becoming a last name |
| Hyphenated surname | `Smith-Jones` also gives `Smith`, `Jones` | each part 4+ letters and not in a stop list |
| Particles | `Jean de la Cruz`: last = `de la cruz` and `cruz`; never `de` or `la` | none |
| Titled form | all six honorifics | a titled form is a strong cue and bypasses stop words (`Ms May`) |

Do not generate initials only (`SJ`). Add test rows: `Sarah J. Jones` gives `sarah j. jones`, `sarah jones`, `sarah`, `jones`, `s jones`, `s. jones`; `Sean O'Brien` gives one-word `O’Brien`; `I a Jones saw` does not match the initial form; `S. Jones` does; `Karim Benali ("the Developer")` gives no `Developer`; `Brightline Studio Ltd ("Brightline")` gives `Brightline` only where capitalised.

Owner minor point: the 3-letter minimum leaves two-letter names (for example `Li`, `Ng`) unmasked alone. Over-masking them is costly (many ordinary words); the owner should confirm that leaving them is accepted.

**(e) Risk.** Keeping only the plan's forms misses `Jones, Sarah` and `S. Jones` in notice blocks. Every added form raises the chance that one short form fits two people, which feeds Q12.

**Status (22 Nov 2026):** The plan's forms stand (plan question 4, as recommended; decision 9). S4-M2-T1 (`name_forms`) and S4-M2-T4 (typed parties and the short-name rule) build them. The additions of this report (initial plus last, surname first, suffix handling, hyphen parts, particles, nickname from text) are not in the tasks. The 3-letter minimum stays.

### Q5. Does an ID span include its keyword?

**(a) Plan.** "Yes, as the prototype shows. The text then reads 'with ⟦ID 1⟧' and the AI never sees the words 'company number'."

**(b) Verdict: DECIDED by the owner on 21 Nov 2026: value-only spans. Written into S4-M2-T2, S4-M3-T4 and the prototype.** Before the decision my verdict was CHANGE as an owner decision: value-only spans are better on the evidence, but they contradict the prototype (`prototype/privacy-check.html` shows the ID value as `company number 09876543`) and need doc edits.

**(c) Evidence.**
- Presidio's IBAN recogniser returns the value only; context words only raise the score ([iban_recognizer.py](https://raw.githubusercontent.com/microsoft/presidio/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/iban_recognizer.py)); credit-card and UK NINO recognisers work the same way ([credit card](https://raw.githubusercontent.com/microsoft/presidio/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/credit_card_recognizer.py), [NINO](https://raw.githubusercontent.com/microsoft/presidio/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/uk/uk_nino_recognizer.py)). AWS Comprehend's example span is the 19-character number only ([AWS Comprehend](https://docs.aws.amazon.com/comprehend/latest/dg/how-pii.html)).
- Reasons (researcher inference): the keyword is public and tells the AI what the clause is about; restore is identical either way; the same number without its keyword groups with the same entity; a value span cannot overlap a name span.
- My reasoning check, extra points the researcher did not state. (1) With a keyword-inclusive span, a USER mark on the digits cuts the PATTERN span, and the remainder `company number ` has letters, so it survives as a second ID placeholder. Value-only removes this. (2) The kind-order trap in Executive summary point 7.
- Gaps: Google DLP span rules and scrubadub span construction not verified.
- **Test evidence (A1).** The same replacement rules with keyword-inclusive spans give identical recall and leaks (415 of 421 spans, 25 letters, the same 6 misses). Over-masked characters rise from 225 to 511, so value-only masks 286 fewer characters (`company number`, `VAT number`, `sort code`, `account number`). The plan's 3 missed VAT numbers are a regex problem, not a span-shape effect. Bare IDs with no keyword (`SC123456`, `AB123456C`, `GB 333289454`) are missed 5 of 5 by every rule set (44 letters and digits leak). What the AI sees, grouping and restore were not measured. A1 never put two kinds in competition on the same characters, so the kind-order trap below is untested.

**(d) Plan edit (S4-M2-T2).** Put the value in a named group and use `m.span("v")`:
`ID = (?i:company (?:registration )?(?:number|no\.?)|registered (?:number|no\.?)|registration (?:number|no\.?)|vat (?:registration )?(?:number|no\.?)|tax id)[ \t]*(?:is|:|of)?[ \t]*(?P<v>(?:GB[ ]?)?[A-Z]{0,2}\d[\d ]{3,12}\d)`; sort code `(?i:sort[ ]code)[ \t]*:?[ \t]*(?P<v>\d{2}-?\d{2}-?\d{2})(?!\d)`. Changed expected values (owner writes): `Our VAT number: GB123456789 and company no. 1234567.` gives 16 to 27 and 44 to 51; `company number 09876543 Agency` gives 15 to 23; `sort code 12-34-56 and account number 12345678.` gives 10 to 18 and 38 to 46. Docs to change in the same change (group B): `prototype/privacy-check.html`, where the ID row shows the keyword in the value. A grep of Spec 4.2 and `docs/ux-copy.md` found no mention of the keyword, so they need no edit for this.

Also required, in two parts. (i) Inside `privacy` (group A): in S4-M3-T4 give `resolve_overlaps` a local rank so that, on identical spans from the same source, ID and BANK beat PHONE. `PiiSuggestion` carries no pattern name, so the rank can only use `kind`. It changes the plan's sort key and so changes expected values. (ii) Reordering `PlaceholderKind` in `core/enums.py` would touch an accepted shape (system design 3.4) and needs the owner (group B). I recommend (i).

**(e) Risk.** Keeping keyword spans hides what kind of number it is from the AI and gives the USER-mark fragment above. Switching without the kind-order fix lets a bare PHONE label an ID.

**Status (22 Nov 2026):** DECIDED, value-only spans (decision 4; plan questions 5 and 22). Written into S4-M2-T2. The kind-order trap is closed inside `privacy`: `TIE_RANK` in S4-M3-T4 puts BANK and ID before PHONE, and `PlaceholderKind` in `core` is unchanged. The prototype ID row is edited (`prototype/privacy-check.html`). The run-on of a keyword ID value (`company no. 1234567 5 days notice`) is accepted as a known limit.

### Q6. What "restore" means

**(a) Plan.** Build three calls: `restore_text` (whole text, copy parts read from the sent text), `restore_reply` (token comes back as the text of the entity's first place; unknown token raises), `map_to_original` (an edge inside a placeholder snaps out to the whole name).

**(b) Verdict: KEEP.** Optional additions go to the owner.

**(c) Evidence.** The researcher agreed with the plan, and the reasoning is real, not anchoring: it rests on Spec 8.4 ("exactly match", unknown counts as broken) and on reading tool source.
- Presidio keeps no placeholder map and no session ([Presidio anonymizer docs](https://microsoft.github.io/presidio/anonymizer/)). LLM Guard's `Deanonymize` offers exact, case-insensitive, fuzzy and combined modes; its fuzzy default distance of 3 could swap `PERSON_1` and `PERSON_2`, and its case-insensitive mode passes the placeholder to `re.sub` as a regex ([deanonymize.py](https://raw.githubusercontent.com/protectai/llm-guard/main/llm_guard/output_scanners/deanonymize.py); the failure modes are the researcher's reading, not run). Do not copy fuzzy matching.
- One preprint (single author, synthetic data, run on two small local models, qwen3.5:9b and gemma4:12b at temperature 0) reports models altering tags: square brackets for angle brackets, words added inside brackets, a dropped closing slash, invented placeholders (verified, App. C p20, App. D pp21-22, Sec. 4.3 p10; [arXiv 2610.34012](https://arxiv.org/html/2610.34012v1)).
    - **"99 of 101 and 29 of 29" is exact** (App. D p22) but applies to one tool's own strict parser. The 101 are 101 of 5,099 tag occurrences, concentrated in 9 of 127 answers; plain placeholders were altered 1 of 8,099 times on that set and 4 of 8,382 on the other. The paper does "not claim" that XML-style tags are altered more often than plain ones, and says format, prompt and restorer were confounded (App. C p20).
    - Mis-restores were mostly inflection: Russian name restoration reached 94.6%, and of 199 failures on one model most were wrong surname forms, but 11 were an engine bug, 82 occurrences were wrongly stored names and 8 were evaluator errors (p9, Table 6). UK English restored at least 99% (p1).
    - Invented placeholders occurred (85 and 0 on Russian answers, set 7; mostly `[ORG_2]`). This supports the plan's rule that an unknown token raises and stays visible.
- Veil-then-Reveal (different design: realistic surrogates, not tokens, small models of 2 to 3 billion parameters) shows that repeated identical values share one surrogate (p14). It describes no grouping of name variants, and does not say they are not grouped. Under a plain prompt its model refused 22 of 40 sanitised prompts, against 19 of 40 unprotected ones, so refusal partly stems from the request; a system prompt telling the model to repeat the values exactly raised repeats from 31 of 137 to 52 of 137 (App. B.1 p12). That is measured support, on a small model only, for the plan's "copy each `⟦…⟧` exactly" prompt line. Its own limitation is that values "omitted, modified, or paraphrased" cannot be restored exactly (p9), which is the same failure in a looser form ([arXiv 2610.22800](https://arxiv.org/html/2610.22800)).
- Why numbered, unique tokens: in Deußer et al. (single run, temperature 0, GPT-4o mini only, three benchmarks only), MuSR scored 0.73 original, 0.70 pseudonymised with unique placeholders, 0.58 generalised and 0.52 redacted (Sec. 4.2 p9, Fig. 4 p11). On MedQA, pseudonymisation and redaction tie at 0.83; on RGB the scores are 0.34 and 0.12 ([arXiv 2609.11335](https://arxiv.org/abs/2609.11335)). Treat it as support for unique tokens on that model, not as a general result.
- Tools: Presidio's anonymizer keeps no map and `deanonymize` needs the caller's entity list with positions (verified). LLM Guard indexes placeholders by exact, case-sensitive value, so "Sarah Jones" and "sarah jones" get different indexes; its Vault is a plain list with no session key; exact restore cannot confuse `_1` with `_10` because `]` is part of the search string. Its case-insensitive mode builds a regex from the placeholder (so the brackets act as a character class), and its fuzzy mode (distance 3) would probably let `_2` match `_1` first (both inferred from source, not run) ([anonymize.py](https://raw.githubusercontent.com/protectai/llm-guard/main/llm_guard/input_scanners/anonymize.py), [deanonymize.py](https://raw.githubusercontent.com/protectai/llm-guard/main/llm_guard/output_scanners/deanonymize.py), [vault.py](https://raw.githubusercontent.com/protectai/llm-guard/main/llm_guard/vault.py)). Tolerant restorers in the field (llmveil, maskrelay) are indirect evidence that alteration happens.
- **Test evidence (B2).** On two Claude models (a small and a mid-size one, through OpenRouter, invented text only): 0 of 544 calls gave a dangerous failure (an invented token or a changed id), but only 353 of the 544 returned a non-empty reply; the small model's reasoning used the whole token limit in the rest. Mutilated tokens (a changed bracket, a lone opener) appeared only when the prompt did not tell the model to copy the tokens exactly: 28 replies without the instruction, 0 of 152 non-empty replies with it. The tolerant matcher that B2 describes would have recovered all 28, because label and number were always right, but the plan's exact match plus one retry also works. Details are in 'Test results'.
- Confirmed absent before B2: no measured alteration or copy rate for a frontier hosted model. The only hosted-model item is a Swedish master's thesis of about 60 interactions with GPT-4o, Gemini 2.0 and DeepSeek, which reports bracketed placeholders kept without being told, with no rates ([DiVA thesis](https://www.diva-portal.org/smash/get/diva2:1980696/FULLTEXT01.pdf)). Private AI documentation was not reachable.
- The observed alteration modes (bracket swap, added words inside brackets, case and spacing, dropped slash) are mostly those inside-marker folding (addition iii) would absorb. A bracket-style swap would not be absorbed: `[Person 1]` stays unchanged, by the plan's rule, and the reply is flagged.

**Rules for stage 6 and later (recommended).** (1) Send the explicit copy instruction in every prompt that carries placeholders (adopted by the owner, decision 2). (2) After each reply, compare the tokens found with the tokens sent as multisets, never as sets: an extra token breaks the reply and nothing is restored; a missing token is recorded as dropped. (3) Restore only exact members of the set of tokens sent; never pick the nearest id. (4) Allow one retry that quotes the exact missing and extra tokens; if it fails, show the reply unrestored. (5) Never add a missing token back at the end: for a name, a dropped token means the reply says nothing about that person. These rules are the researchers' own proposals (see 'Ideas from nearby fields'), not published practice, and they are not stage 4 work.

**(d) Plan edit.** None required for stage 4. Additions to propose to the owner (all optional): (i) a test that a lone `⟦` with no close in a reply is flagged, because the plan leaves it untouched and no scan sees it as a token; (ii) a code-only check that a bare `Person 1` or `[Person 1]` outside markers, not present in the sent text, marks the reply broken; (iii) inside-marker folding of case and repeated spaces (`⟦person  1⟧`), which needs an edit to Spec 8.4 wording. Test rows: `⟦Person 1⟧` restores; `⟦Person⟧ 1` and `⟦Person 3⟧` with two entities raise; `[Person 1]` unchanged; `⟦Person 1⟧⟦Person 2⟧` both restore; a contract's own `⟦Person 2⟧` goes out as `[Person 2]` and never restores. Restored text must never be re-sent without a new replacement pass (the loop in Spec step 12).

**(e) Risk.** Strict exact match costs retries on altered tokens, and each paid retry spends the roughly $10 budget. Any tolerance outside the markers can restore a real name where the model wrote a bare label, which is worse than an ugly token.

**Status (22 Nov 2026):** KEEP, decided (plan question 6, as recommended). `restore_text`, `restore_reply` and `map_to_original` are S4-M4-T3, S4-M4-T4 and S4-M4-T5. An unknown token raises, a lone `⟦` is left as it is, and a name comes back as its first place. The copy instruction is recorded as in Q10. Rules 2 to 5 above (multiset parity, a closed id set, one retry, no re-adding) are written in no document yet and belong to stage 6 and later. The optional additions (d) (i) to (iii) are not built.

### Q7. One detector call on the whole text

**(a) Plan.** "One call with the whole `Document.text`. The adapter chooses how it works through long text. The result is validated once (S4-M3-T1)."

**(b) Verdict: KEEP, and write the fail-closed contract.**

**(c) Evidence.** Presidio chunks inside the recogniser with overlapping windows broken at a space or newline only (the chunker and the GLiNER recogniser both default to 250 characters with 50 overlap; the earlier "400 with 60" came from a sample page that was not read) and merges same-type duplicates that overlap by more than half the shorter span ([chunker](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/chunkers/character_based_text_chunker.py), [dedup](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/chunkers/base_chunker.py), [GLiNER sample](https://presidio.dataprivacystack.org/samples/python/gliner/)); a silent-truncation bug was real: issue 1571 was closed as fixed by PR 1805, "Fix gliner truncates text", in release 2.2.361 ([issue 1571](https://github.com/data-privacy-stack/presidio/issues/1571)). DeidSharp uses 2,000-character chunks with 200 overlap, locates model strings by whole-word search, and fails the run if any detector fails, so a failure is never read as "nothing found" (confirmed, Sec. 3.1 p3 and abstract p1; preprint caveat above). The same paper's LLM asked to check its own findings discarded about a quarter of true PHI (24.6 points of recall, Sec. 4.1 p7). In scrubadub, a detector exception propagates and `clean()` fails (only `NotImplementedError` is caught), while invalid filth is skipped silently ([scrubbers.py](https://raw.githubusercontent.com/LeapBeyond/scrubadub/master/scrubadub/scrubbers.py)). Presidio skips invalid spans with a warning, but only when a text normaliser changed the text; with the default no-op normaliser no span check runs ([analyzer_engine.py](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/analyzer_engine.py)); the researcher argues raising is safer because a bad offset suggests other in-range spans are shifted. The plan's whole-text call also keeps `FakePiiDetector` keyed on exact text. Gaps: no measured accuracy difference between whole-text and per-clause calls; no latency figures; spaCy limits not checked; the PR 1805 diff was not read.

**Test evidence (A2, A3).** A2 tested six offset cases against the plan. It confirmed three defects: a reversed span returns `()` without raising, a start past the text with an end inside it returns `()` (this is also a reversed span), and a bool start is accepted as an int. Three others already raise: an end past the text (`ValueError`), a `None` start and a float start (both raise `TypeError` by accident, from `None < 0` and `text[1.0]`, not from a check). A3 agrees. P10 passes on the plan's own validator definition (raise for `start < 0` or `end > len`). P10b, the stricter note definition (a reversed span must raise), fails: shrunk case, text `''` with the span 0 to -1. P10c (non-integer offsets) was a mistaken property for empty spans, but it exposes the bool gap and the `TypeError` against the `privacy:` `ValueError`. So the plan text is not wrong; it is looser than this report asks for.

**(d) Plan edit.**
- S4-M3-T1 `trim_suggestions`: raise `ValueError` (message starts `privacy: `, no contract text) for `end < start`, `start > len(text)`, and any non-`int` value (including `bool`, `float`, `None`); validate every span before processing any; keep empty and whitespace-only spans as a silent drop. Test rows: `(-1,3)`, `(0,len+1)`, `(5,2)`, `(len+1,len+1)`, `(3,3)` dropped, `(True,3)`, `(0.0,3)`, `(None,3)`, a valid span followed by a bad one still raises.
- S4-M3-T6: `find_personal_data` must not catch detector exceptions. Add a test with a detector that raises, asserting the error propagates and no code-finders-only result is returned as if complete. The port docstring "Raises: None" must change at stage 7, with a named error type (Constitution I5, I6, I7).
- Record the adapter contract in the S4-M5-T4 note: offsets in code points of the exact text passed (test with non-BMP and accented text); overlapping windows broken at whitespace with duplicates removed inside the adapter; never truncate silently, raise if the text cannot be covered; return spans and kinds only, never copied text; locate LLM-returned strings by whole-word search and drop invented ones.

**(e) Risk.** Per-clause calls would put offset shifting and model limits into `privacy` and break the fake. Treating a failed detector as "nothing found" shows the user a result that looks clean and is not. The caller must show "the detector failed", never a code-finders-only result presented as complete.

**Status (22 Nov 2026):** KEEP with the contract, decided (plan question 7, as recommended). S4-M3-T1 raises `ValueError` (message starting `privacy: `) for non-integer, bool, out-of-range and reversed offsets, and checks every span before it trims any. S4-M3-T6 never catches a detector error (`test_a_detector_error_is_not_caught`). The stage 7 adapter contract is in system design 15.7 and in section 9 of the plan. The change to the `PiiDetector` docstring ("Raises: None") is a stage 7 `core` task and is not done.

### Q8. A detector span across a sentence start is cut, never dropped

**(a) Plan.** "Cut it at the sentence start and keep each piece. A dropped span would leak."

**(b) Verdict: KEEP.**

**(c) Evidence.** Presidio keeps detections that touch a chunk edge and prefers the neighbouring chunk's whole prediction ([base_chunker.py](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/chunkers/base_chunker.py)); non-overlapping segmentation fragments multi-token entities ([arXiv 2609.29682](https://arxiv.org/abs/2609.29682); small experiment on one Marathi model with six synthetic documents; macro F1 across window sizes spans only 0.8789 to 0.8902, and the results tables read show no non-windowed baseline, so the fragmentation claim is motivation, not a measurement; its overlap merge is "later window wins", not a union; weak evidence for window size and acceptable for the boundary point). The reasoning is real: dropping leaks; extending needs `privacy` to change spans that `ingest` owns and the import wall forbids it; flagging adds a prompt and `PiiSuggestion` has no field. No tool was found that handles this exact case; chunk edges are the closest analogue. How often real contract names cross sentence boundaries was not measured.

**Test evidence (A3).** Properties P9a and P9b (no sentence start inside a piece; every letter and digit still covered; kind and source kept; a span with no start inside is unchanged; the split is idempotent) pass 5000 Hypothesis examples each. The reference `split_at` returns pieces in input order, while S4-M3-T5 says to return through `unique_sorted`. The gap is in the reference code and the plan text is right. Fix the reference code before any expected value is recomputed. The tests feed it sorted resolver output, so the difference was not exercised.

**(d) Plan edit.** None to the rule. Add the testable invariant: after the split no output span contains a sentence start strictly inside it, every alphanumeric character is still covered, and each piece keeps the parent's kind and source. Edge tests: cut exactly at the span start or end (no cut); span covering only inter-sentence whitespace (dropped after trim); several starts inside one span; a span crossing a clause start; a span in a heading outside any sentence. Do not trim trailing punctuation (it is part of `Ltd.`); the cosmetic question of masking a sentence-final full stop is the owner's.

**(e) Risk.** Drop leaks the whole span. Extend breaks module boundaries. A real name that crosses a boundary gets two placeholders, but that case is rare and over-masking is safe; stage 12 "Same person" is the place to merge, never the cut.

**Status (22 Nov 2026):** KEEP, decided (plan question 8, as recommended). S4-M3-T5 builds `split_at_sentences`, returns through `unique_sorted`, and carries two added tests. The properties of the resolve step are in S4-M3-T11.

### Q10. The escape form (⟦ becomes [)

**(a) Plan.** "Each `⟦` and each `⟧` of the contract is its own `escape` segment and is sent as `[` and `]`. Then `⟦` and `⟧` occur in the sent text only inside real placeholders... and offsets do not move."

**(b) Verdict: KEEP, decided by the owner on 21 Nov 2026 (no ADR). The status line says what the plan took from (d).**

**(c) Evidence.** A local Unicode check by the researcher: U+27E6 and U+27E7 are unchanged by NFC, NFD, NFKC and NFKD and nothing else folds into them; fullwidth brackets fold to ASCII under NFKC, so they are not markers; private-use characters can appear in PDF and Word extraction, so reject them. Practitioner tools use ASCII forms (`[REDACTED_PERSON_1]`, `<PERSON_1>`, `[PERSON_1]`) ([LLM Guard](https://raw.githubusercontent.com/protectai/llm-guard/main/llm_guard/input_scanners/anonymize.py), [WSO2](https://wso2.com/api-platform/learn/pii-redaction-llm/)). The only comparison study found parser and prompt mattered more than bracket style, with confounds ([arXiv 2610.34012](https://arxiv.org/html/2610.34012v1)). Researcher's reasoning, which I find sound: contracts already hold ASCII `[insert date]`, `[●]` and `<Party>`, so an ASCII token cannot be one that "ordinary contract text can't contain" (Spec 4.2). Look-alike brackets in replies are not scanned.

**Tokenisation and copy rate (first-revision evidence, from before A4 and B2; the measurements follow below).** U+27E6 is UTF-8 `E2 9F A6` and U+27E7 is `E2 9F A7`: 3 bytes each, against 1 byte for ASCII `[ ]`. No source measured either character in any tokeniser, and no copy-rate figure for `⟦ ⟧` against ASCII exists (both confirmed absent). General evidence: byte-level BPE and byte-fallback tokenisers spell an unseen character as bytes, so a rare 3-byte character with no vocabulary entry can cost up to 3 tokens ([Zero to Frontier](https://zerotofrontier.app/tokenization/byte-level), [The Next Token](https://thenexttoken.net/posts/why-token-counts-differ)). Whether `⟦` has a merge in o200k_base, Llama 3, Gemini or Claude is unknown, and Anthropic publishes no tokeniser for current models. If it has none, `⟦Person 1⟧` costs up to 6 tokens for the two brackets against 2: small in cost, and a hypothesis that a split opening marker is copied less reliably, which no source tests.

**Format precedent.** Every tool and sample found uses ASCII: `[PERSON_1]`, `<PERSON_1>`, `<<PERSON_1>>` (piighost chose double angle brackets so the model does not take a token for an XML tag) and `[REDACTED_PERSON_1]`. A Microsoft sample uses `<Person_0>` with a system-prompt line to retain placeholders exactly ([Azure AI Landing Zones](https://azure.github.io/AI-Landing-Zones/ai-gateway-landing-zone/security/pii-masking/)). OpenAI, Anthropic and Google give no format guidance (confirmed absent); the Google DLP page was not fetched and Private AI's was unreachable. Nobody recommends a rare Unicode bracket, so there is no outside precedent either way.

**Spoofing in practice.** No research write-up on placeholder spoofing exists (confirmed absent), but the collision class shows up as bugs and design notes. LiteLLM's Presidio masking could restore a user's own `<PERSON_1>` to an unrelated value; the open fix reserves tokens already in the input before numbering ([PR 48334](https://github.com/BerriAI/litellm/pull/48334), fixing issue 48029). piighost neutralises placeholder-shaped input with a zero-width space (the invisible character survives copy and paste) and refuses model-invented well-formed placeholders ([piighost decisions](https://docs.piighost.dev/en/domain/reference/decisions/)). LLM Guard's shared Vault has no scoping, and a model that emits `[REDACTED_PERSON_1]` gets another request's value (a secondary write-up; the code shows an in-memory list). The plan's escape of `⟦` to `[` on the original text matches piighost's defence without an invisible character. Whether a model repeats a fake `⟦Person 7⟧` from a document, and whether `⟦` occurs in real PDF or Word extraction, are untested.

**(d) Plan edit.** None to the rule. Add: the escape applies to the original text only, after any folding, never to the match key; tests `a ⟦b⟧ c` gives `a [b] c` with two ESCAPE segments; `⟦Sam` with an entity over `Sam` gives `[⟦Person 1⟧`; an entity over `x⟦y` replaces the marker whole; a property that every `⟦` in the sent text starts a real token matching `PLACEHOLDER_PATTERN`; NFKC of the sent text leaves the markers unchanged. In step prompts that carry placeholders, tell the model to copy each `⟦…⟧` exactly and never invent one (owner decision 2: stage 6 and later). Before sending, assert that the outgoing text holds exactly one `⟦` per real token and fail the run if not.

**Test evidence (A4, B2): the free count and the paid run are done.**

- **Token cost on a Claude model (B2).** The provider's prompt-token counts were identical for the small and the mid-size model. Against plain invented names, `⟦Person n⟧` costs +3.65 tokens per placeholder, `[PERSON_n]` +0.20, `<PERSON_n>` +0.38, and `[Person n]` is 2.17 cheaper. On the test text (40 placeholders in 514 words, five kinds) `⟦Person n⟧` adds 146 tokens to about 1,000, about 14%. That density is high; a contract with fewer placeholders per word pays proportionally less. The per-placeholder figure is approximate, because the baseline also swaps dates and amounts; the ranking between forms is exact.
- **OpenAI-style and GPT-2 vocabularies (A4, not Claude).** `⟦` is three byte tokens in o200k_base and GPT-2 (two in cl100k_base). `⟦Person 1⟧` costs 9 tokens in o200k_base against 5 for `[Person 1]`. In a 596-word paragraph with 20 placeholders `⟦Person n⟧` adds 11.98% (o200k_base), 6.45% (cl100k_base) and 12.22% (GPT-2) over `[Person n]`. The closing `]` merges with a following `.`, `,`, `;`, `)` or `:`; `⟧` never does.
- **Copy rate (B2).** Replies with a mutilated token, without the copy instruction: `⟦ ⟧` 11 of 51, `[Person n]` 8 of 49, `<PERSON_n>` 9 of 54, `[PERSON_n]` 0 of 47. With the instruction: 0 of 152 across all four forms. No dangerous failure in any cell. The gap between the first three forms is within noise.
- **Spoof (B2).** A fake `Person 9` typed by the contract author was re-created in its unescaped style in 5 of 27 replies for the three ASCII forms without the instruction (all 5 from the small model), and in 0 of 9 for `⟦ ⟧`. With the instruction the small model re-created it 0 of 24 times. The difference is not significant; the upper bound for `⟦ ⟧` is about 33%.

Reading. On cost and copy rate alone `[PERSON_n]` looked better: +0.20 tokens and 0 of 47 mutilated replies. The owner kept `⟦ ⟧`. The reason that remains is the collision argument: ASCII brackets already occur in contracts, so an ASCII token cannot be one that ordinary contract text can't contain (Spec 4.2). The price is about 3.5 extra tokens per placeholder on a Claude model. The format is one constant in `core/enums.py`, so the choice is cheap to reverse. The lever that mattered is the explicit copy instruction (owner decision 2). Samples are small, and 'Evidence quality and gaps' lists the limits.

**(e) Risk.** If hosted models copy `⟦ ⟧` poorly, replies are broken more often. The format is one constant in `core/enums.py`, so changing it later is cheap. An ASCII token would collide with template brackets now.

**Status (22 Nov 2026):** KEEP, decided (decision 2; plan question 10). `⟦ ⟧` stays with no ADR. The escape is built in S4-M4-T1 and S4-M4-T2 (tests `a ⟦b⟧ c`, `⟦Sam` and `x⟦y`). The rule "write each placeholder exactly as it appears" is recorded in system design 15.8 (stage 8) and in section 9 of the plan. It is not stage 4 work.

### Q11. Which matches remove a defined term from the allow-list

**(a) Plan.** "A term is dropped only when a `PARTY_DETAILS` suggestion, or a `RULE` suggestion of kind `PERSON` or `COMPANY`, has the same text (without 'the' and ''s'). A detector match never drops a term."

**(b) Verdict: CHANGE.**

**(c) Evidence.** No surveyed tool separates a role from a name: Presidio's allow-list is a plain string test (verified in source). Exact mode is a case-sensitive whole-span membership check with no folding of case or "the". Regex mode joins the entries with `|` and uses an unanchored, case-insensitive search, so an entry `Ann` also allows `Annabel Jones`. It runs after de-duplication ([analyzer_engine.py](https://raw.githubusercontent.com/microsoft/presidio/main/presidio-analyzer/presidio_analyzer/analyzer_engine.py)). The earlier "documented back-reference bug" ([issue 2433](https://github.com/microsoft/presidio/issues/2433)) was not fetched and is **unverified**; source shows a plain join, so a numbered back-reference would shift by position (inferred). Separately, Google DLP exclusion rules offer overlap precedence ([DLP rules](https://docs.cloud.google.com/sensitive-data-protection/docs/creating-custom-infotypes-rules)). The Text Anonymization Benchmark treats all variants as one entity and lets generic role words go ([TAB guidelines](https://github.com/NorskRegnesentral/text-anonymization-benchmark/blob/master/guidelines.md)). The researcher traced a gap by hand from the plan text: `Mercury Logistics Ltd ("Mercury")`, not a typed party, gives a RULE COMPANY `mercury logistics ltd`, which is not equal to `mercury`, so `mercury` stays allowed. Q4's short-name rule does not apply (not typed), so no finder masks a bare `Mercury`, and from stage 7 a detector flag on it is silently dropped. The trace was not run as code, and the researcher says so. The refusal to let the detector decide is correct: it flags roles such as "Agency" as organisations.

**Test evidence (A2).** Reproduced as code: with `Mercury Logistics Ltd ("Mercury") will carry the goods.` and a detector hit on the bare `Mercury`, the plan allows `mercury` and the hit is dropped, so it leaks. A control with no defined terms keeps the hit, so the allow-list causes the drop. The role word `Agency` stays readable under both the plan and the fix. A1 did not run the allow-list. 'Ideas from nearby fields' adds two ideas: a role lexicon, and kept words never restored inside a longer masked span.

**(d) Plan edit (S4-M3-T2).** Keep the equal-text rule and add rule 2b: a defined term T is a name, not allowed, when the sentence that holds its definition also holds a PARTY_DETAILS span or a RULE PERSON/COMPANY span S, and the folded words of T (punctuation stripped, "the" removed) are a non-empty subset of the core words of S (without suffix or honorific). The detector never adds or removes a term. Test rows (invented names): `Brightline Studio Ltd (the "Agency")` keeps `Agency`; `Mercury Logistics Ltd ("Mercury")` untyped makes `Mercury` a name; `Apple Inc. ("Apple")` name; `Apple Inc. (the "Company")` keeps `Company`; `Jane Smith ("Jane")` name; a detector flag on `Agency` still leaves the term allowed; a detector hit alone decides nothing for `Mercury`; curly quotes, possessive and `The` prefix normalise to one key.

**(e) Risk.** Skipping 2b leaves the Mercury leak. 2b also makes `("the Studio")` a name when the sentence holds `Brightline Studio Ltd`, which treats a possible role as a name: that is the safe direction but over-masks; the plan takes the safe direction (plan question 11, answered as recommended). A residual risk stays when no finder finds the full name at all.

**Status (22 Nov 2026):** CHANGE, adopted (plan question 11, as recommended). The Mercury rule is in S4-M3-T2: `allowed_term_texts` takes the `DefinedTerm`s, and a term that is a short form of a name found by `PARTY_DETAILS` or by a `RULE` `PERSON` or `COMPANY` is no longer allowed. A detector match never drops a term. A short form that no finder reaches stays readable, which the plan states as a limit. The role lexicon and the kept-words order of 'Ideas from nearby fields' are not built.

### Q12. A short form that fits two people gets its own placeholder

**(a) Plan.** "A short form that fits one full name joins it... A short form that fits two or more full names gets a placeholder of its own: code never guesses. The user's split and merge are built in stage 12."

**(b) Verdict: KEEP, with a clarification.**

**(c) Evidence.** The one tool that studied it designs so that different people never share a placeholder, and an ambiguous mention gets its own (verified: Sec. 5 p10 says resolution is "designed so that different people do not share a placeholder" and an ambiguous mention gets its own; [arXiv 2610.34012](https://arxiv.org/html/2610.34012v1); its engine uses Russian-specific gender and patronymic logic that does not apply here). Its App. C p20 records the opposite design as a development bug: people sharing a surname got one placeholder, a landlord and a tenant became one party, and the paper calls this "worse than a leak" because a user is unlikely to notice it and its restoration metric would not detect it. It is a fixed bug, not a measured rate, in a single-author synthetic study, but it is a primary-source statement of the asymmetry that carries this verdict. LLM Guard indexes by exact, case-sensitive value and does no variant grouping; Veil-then-Reveal shares one surrogate for identical values and describes no variant grouping ([LLM Guard](https://raw.githubusercontent.com/protectai/llm-guard/main/llm_guard/input_scanners/anonymize.py), [arXiv 2610.22800](https://arxiv.org/html/2610.22800), p14). The reasoning that carries the verdict is the asymmetry: wrongly merging two people loses a fact the checker needs; splitting one person costs clutter the user can merge. That is independent of the paper. Gaps: no benchmark of merge versus split errors in contract review.

**Test evidence.** None: no track ran the typed-party path or the grouping step. The nearby-field note supports the form-set map and adds two guards: a gendered honorific from the contract must not join an entity whose own cue honorific is of the other gender, and entities that differ only in a generation marker (`Jr`, `Sr`, `II`) stay separate. See 'Ideas from nearby fields'.

**(d) Plan edit (S4-M3-T7).**
- Decide ambiguity by form generation, not token subset: build a map from each distinct form string to the set of entities whose `name_forms` produce it. One entity: the form joins it. Two or more: the form gets its own entity. This keeps the rule correct for the Q4 forms (`S Jones`, `Smith` from `Smith-Jones`, a shared first name).
- Recommended: one shared placeholder per distinct ambiguous short form, so every "Ms Jones" shares one Person N. The plan's word-set clusters give this (see the status line).
- Numbering per kind in order of first appearance of the entity's earliest span; no gaps.
- Properties: no entity id is shared by two different full names; per-kind numbers run 1 to n in order of first span start. Test: parties `Sarah Jones` and `Tom Jones`, text `Ms Jones agrees.` gives `Ms Jones` its own Person; `Jones signs. Sarah Jones and Tom Jones agree.` gives `Jones` its own Person numbered 1.
- Note: numbers can change when the document gets a second Jones, which matters if stage 6 caches entities.

**(e) Risk.** Merging on a guess changes who owes what. Never merging at all leaves clutter and more placeholders for the AI.

**Status (22 Nov 2026):** KEEP, decided (plan question 12, as recommended; decision 9). S4-M3-T7 groups by word sets: a set that two or more larger sets contain becomes its own entity, and forms with the same word set share it. The form-set map, the gender guard and the generation-suffix guard of this report are not built.

### Q13. Replacing known names in position text is stage 8

**(a) Plan.** "Stage 8. Stage 4 leaves `PlaceholderEntity.spans` and `restore_reply` ready for it."

**(b) Verdict: KEEP, with a recorded contract.**

**(c) Evidence.** Session-wide vaults are the standard design ([LLM Guard](https://raw.githubusercontent.com/protectai/llm-guard/main/llm_guard/input_scanners/anonymize.py), [arXiv 2610.22800](https://arxiv.org/html/2610.22800)); "restore or refuse" is practitioner guidance ([MLflow](https://mlflow.org/articles/pii-redaction-llm/)); a multi-turn framework, CAMP, re-masks the whole history retroactively once a risk threshold is crossed, with a session-wide registry and a local pseudonym map (verified against the full text, Sec. III.E, IV.B, IV.D; [arXiv 2604.16521](https://arxiv.org/html/2604.16521v1)). Caveats: a sole author, four synthetic scenarios, Presidio and one LLM; messages below the threshold go out unmodified, so early turns (triggers at turns 2 to 5) reach the model unmasked; SSN, card and bank types become `[BLOCKED]` and are not restored. It masks late where the plan masks from the start, so it is a precedent for a session-wide map only. LiteLLM's open fix reserves tokens already in the input before numbering ([PR 48334](https://github.com/BerriAI/litellm/pull/48334)), the same one-numbering idea. The sequencing argument is real: nothing sends position text before stage 8. But the import wall means stage 8 cannot import `privacy`, so a second copy of the matcher would drift and leak. ADR 0008 promises the replacement, so under Constitution T13 the promise needs a test when it is built.

**(d) Plan edit.** None to the tasks. In section 9 notes, record: the free-text replacer lives either in `privacy`, wired by `cli`, or in `core`; one map and one numbering for every source in a prompt; the canary check runs on the final request body; restored text is never re-sent without a new pass; stage 8 test rows (full name, lowercase short form and possessive each go out as tokens; the reply token restores via `restore_reply`; the request body holds no entity string). Group B in 'Where each change belongs' lists the shared replacer and the import wall.

**(e) Risk.** Two matcher copies would leak. The free-text case rule (match one-word forms without regard to case, since typed text is unreliably capitalised) conflicts with Q17: case-insensitive `will` or `price` for a party `Will Price` would mask ordinary words, while keeping the stop list leaks `jones` style entries. It is a stage 8 decision; flag it as an owner question there.

**Status (22 Nov 2026):** KEEP, decided (plan question 13, as recommended). Stage 8 builds it. The contract is in system design 15.8 ("Known names in free text": one function that `privacy` exports and `cli` passes in, or `core`; one-word forms match without regard to case there) and in section 9 of the plan. `PlaceholderEntity.spans` and `restore_reply` stay ready (S4-M4-T4). The conflict with the capital rule of Q17 is for the stage 8 plan.

### Q14. The governing-law place is kept

**(a) Plan.** "Yes, as a small rule: the words after 'governed by (and construed in accordance with) the law(s) of' are a kept place, and no detector or rule suggestion may overlap it." The regex takes an unbounded run of capitalised words.

**(b) Verdict: DECIDED by the owner on 21 Nov 2026: a closed list. Spec 4.2 and the stage 4 plan carry the closed list, and a person or company span that touches the place stays whole (decision 6).** Before the decision my verdict was CHANGE: keeping the place is reasonable; the plan's regex is not safe.

**(c) Evidence.**
- Keeping a bare jurisdiction is low risk. GDPR Recital 26 judges identifiability by all means reasonably likely, and pseudonymised data attributable by additional information stays personal data ([Recital 26](https://gdpr-info.eu/recitals/no-26/); [EDPB Guidelines 01/2025](https://www.edpb.europa.eu/system/files/2025-01/edpb_guidelines_202501_pseudonymisation_en.pdf)). The ICO applies a motivated-intruder test ([ICO](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/anonymisation/how-do-we-ensure-anonymisation-is-effective/)). The Text Anonymization Benchmark says only very general values, such as a country, may be left, depending on the other quasi-identifiers ([TAB guidelines](https://github.com/NorskRegnesentral/text-anonymization-benchmark/blob/master/guidelines.md)). The researcher's k-anonymity argument is reasoning, not a figure. So the app must keep saying "pseudonymised, replaced on this computer", never "anonymous".
- LLMs can infer location from free text (verified): on real Reddit data (520 profiles, 5,814 comments) GPT-4 reached 86.2% location accuracy (Table 2 p7), and after Azure-based anonymisation of locations, persons and organisations location accuracy was still about 55% (Sec. 6). In that data, style cues, not a kept jurisdiction, are the main leak ([Staab et al., ICLR 2024](https://arxiv.org/abs/2310.07298)). The paper tests no contracts; "a contract's style adds little beyond a bare jurisdiction" is this report's own inference.
- Presidio's default spaCy NER flags US states as LOCATION and durations as DATE_TIME ([Stackademic example](https://blog.stackademic.com/presidio-in-action-detecting-and-securing-pii-in-text-451711e3c544), secondary), so stage 7's detector configuration must ignore those or Spec 4.2's keep-list breaks.
- Re-run by me: `governed by the laws of England Sarah Jones signs` captures `England Sarah Jones`; `the laws of the State of Delaware` gives no match; `England and Wales.` captures correctly. With the over-capture, `drop_in_places` drops the RULE person on "Sarah Jones" (only USER and PARTY_DETAILS survive), a leak from untrusted contract text (Spec 8.4).
- **Test evidence (A1, A2, A3, B1).** A2 reproduces both regex defects: `laws of England Sarah Jones signs` keeps `England Sarah Jones`, and the RULE person on the first `Sarah Jones` is dropped; `the State of Delaware` and `the Republic of Ireland` give no place (the fix keeps `Ireland`, not `Republic of Ireland`; owner to confirm). A1, with one simulated detector flag on each of 27 place spans: the plan leaves 10 of 27 flags standing (every `State of ...` and `Republic/Kingdom of ...`), the replacement 5. Those 5 are `Switzerland`, `Japan`, `Brazil`, `India` and `Kenya`, which A1's own gazetteer (about 29 countries and regions, plus US states) left out. They are countries, so under the owner's list they would be kept. The cost of the owner's list therefore does not show in A1. It falls on places outside the five categories (for example territories, crown dependencies and Hong Kong), which stay flagged. In the over-capture case the plan leaks `Sarah Jones` in 6 of 12 spans (60 letters); the replacement leaks 0. A3 P11 finds the drop-whole defect on random input and passes once the place is cut. B1, on 510 real contracts (437 with a governing-law annotation): the plan's regex keeps 22 places in 22 contracts; the closed list keeps 134 places in 128 contracts. The unit is places, with contracts beside it. A kept place shares a word with a PERSON or COMPANY span somewhere in the same contract for 2 places (plan) and 4 places (closed list); no kept place overlaps a raw PERSON or COMPANY span before the cut. A1's and B1's lists were the researchers' own, not the owner's.
- Gaps: confirmed absent: no with-and-without study of name redaction on LLM contract review (arXiv 2609.11335 covers eleven general benchmarks, none legal; its MuSR figures, once taken from a vendor blog, are now confirmed in the paper: see Q6); no jurisdiction k-anonymity figure; EDPB paragraph text read in excerpt; no lawyer consulted (ADR 0016).

**(d) Plan edit (S4-M3-T3, `places.py`).**
- Replace the shape regex by a closed gazetteer constant owned by the owner (same status as other lists, Q16), with the decided categories only: countries (with common short forms such as "United States" and "United Kingdom"), UK nations ("England", "Wales", "Scotland", "Northern Ireland", and the pair "England and Wales", which the sample uses), US states (as "State of X", "Commonwealth of X" or bare), Canadian provinces and Australian states. Not in the list, so not kept: DC, US and Australian territories, Canadian territories, crown dependencies and Hong Kong. My first revision added some of these on my own. Whether to add a short list of them is for the owner, who writes the list (S4-M2-T11).
- Match only after `(?i:governed by(?: and construed in accordance with)? the laws? of)` plus an optional `the` and an optional `State|Commonwealth|Republic|Kingdom of`, take the longest gazetteer member (allowing a fixed ` and ` between two members), and stop at its end. Anything outside the gazetteer is not kept and the detector flag stays; the place is shown as unsure, as decided (the wording of the reason is a stage 8 display matter).
- Apply the kept place only inside the governing-law phrase. Do not keep court cities by default ("courts of Leeds"); a city is a smaller-population quasi-identifier.
- `drop_in_places` becomes a cut (see Q9 edit 2).
- Test rows (invented text): `England and Wales.` kept exactly; `the State of Delaware, USA.` keeps `State of Delaware`; `laws of England Sarah Jones signs` keeps `England` only and `Sarah Jones` stays masked; `laws of Narnia` keeps nothing; `laws of Jersey` keeps nothing (not in the decided list); a typed party whose name holds a listed place, with that place in the clause: the party span wins where they overlap; a detector ADDRESS flag on `England and Wales` inside the clause is dropped; `courts of Leeds` stays flagged; two governing-law clauses both kept; lower case, curly apostrophe, `Laws` and `law` match.
- Optional paid or local test: a replay on the sample with and without the place, owner-approved with a spend cap, only after the owner agrees the budget.

**(e) Risk.** Keeping the plan's regex leaks an untyped name that follows the place and breaks the check on `State of Delaware`. A closed list misses a rare jurisdiction, which is over-masking and safe; hiding the place entirely would blind the checks that read the governing law. The decided cost: a place outside the five categories stays flagged and shows as unsure.

**Status (22 Nov 2026):** DECIDED, closed list (decision 1; plan questions 14, 19, 20 and 25). Spec 4.2 carries the five categories ("England and Wales" counts as one) and the hybrid clause. ADR 0008 has the amendment of 22 Nov 2026. S4-M3-T3 builds `places.py` and `cut_in_places`. The owner writes the list file, S4-M2-T11 (`_place_list.py`), which is not written yet. A US state is kept only as `State of X`: the switches `US_STATE_BARE` and `US_COMMONWEALTH` are off (plan question 19). A place outside the list is not kept and its flag stays; stage 4 shows no "unsure" mark for it. The planner's draft list also holds territories, and the owner's file decides.

### Q15. Which patterns stage 4 builds

**(a) Plan.** Email; phone (international, and UK national with spaces or dashes); an ID number after a keyword; a bank number after "sort code" or "account number"; IBAN with the mod-97 check. Everything else is left to the detector in stage 7.

**(b) Verdict: CHANGE (scope, an owner decision; plus fixes that apply whatever the scope).** Phones changed in this revision: no cue gate for spaced national numbers.

**(c) Evidence.** Presidio builds CREDIT_CARD with pattern plus checksum, IBAN with context plus checksum, and UK NINO, UK postcode and US SSN with pattern plus context ([Presidio entities](https://presidio.dataprivacystack.org/supported_entities/)); the IBAN trailing-group handling is in its source (cited above). GB VAT checksum rules are in [python-stdnum](https://raw.githubusercontent.com/arthurdejong/python-stdnum/master/stdnum/gb/vat.py); UK company number prefixes are in [Companies House guidance](https://assets.publishing.service.gov.uk/media/5d08c0f340f0b6094a379078/uniformResourceIdentifiersCustomerGuide.pdf). Google treats a date of birth as personal only with a cue ([infoTypes](https://docs.cloud.google.com/sensitive-data-protection/docs/infotypes-reference)). Researcher-tested pitfalls: the plan's phone pattern matches `ref 0123 456 7890` and misses `(020) 7946 0958` and `07700900123`; about 1 in 10 random 16-digit strings pass Luhn, so Luhn alone is weak on long references. No published false-positive rates on contract text were found.

**Test evidence (A1, B1).** Bracketed phones (`(020) 7946 0958`): the plan finds 0 of 6 (66 letters and digits leaked), the replacement 6 of 6. Unspaced `07700900123`: the plan 0 of 6; the replacement finds 3 of 6 when a cue word is present, and the other 3 have no cue and are not reachable. The shape check of my first revision does not remove the false positive `ref 0123 456 7890`: 6 of 6 references still match, because UK shapes cannot tell them from phones. Gating spaced national numbers on a cue word removes all 6 false hits but leaks 4 of 4 bare numbers (`Our line is 020 7946 0958`, 44 letters and digits). On a privacy tool that favours no gate. The shape regex as I wrote it, `0[1-3]\d{2,3}`, rejects `020 7946 0958`; A1 used `0(?:[1-3]\d{1,3}|7\d{3}|[58]00)`, which the plan edit below now carries. The unspaced 11-digit form without a cue gate was not measured, so that trade stays open. Bare IDs with no keyword (`SC123456`, `AB123456C`, `GB 333289454`) are missed 5 of 5 (44 letters and digits leak). Neither rule set has a finder for them, so this sizes the leak that NINO, GB VAT and company-prefix patterns would close, not their precision. IBAN, email, sort code and account number: 100% in both, nothing to change. B1 on 510 real contracts (counts only): the plan finds 91 phone-like spans and the replacement 76. The share with no cue word within 40 characters and under 11 digits is 20.9% (19 of 91) for the plan and 6.6% (5 of 76) for the replacement; that is a proxy, not precision. A four-group dotted-number regex matches 548 times, all with valid octets, so an octet check alone rejects none. 99 of them (18.1%) follow a clause, section, article, schedule or exhibit cue within 12 characters. Stage 4 has no IP finder, so this only matters if one is added.

My reasoning check: the plan leaves NINO, cards and similar to the detector, but the detector is a model that can miss them and may be absent at first, and the project rule is that leaks are worse than over-masking. The additions below are cheap and nearly free of false positives. Note that `PlaceholderKind` has no URL, DOB or card kind: card maps to BANK and NINO to ID; URL and DOB need an owner decision on the kind (a Spec 4.2 change).

**(d) Plan edit (S4-M2-T2 and S4-M2-T3, patterns).**
- Add, if the owner accepts the scope: UK NINO (prefix rules, kind ID), card number with Luhn and 13 to 19 digits plus a cue (`card|visa|mastercard|amex` within 40 characters before, or first digit 3, 4, 5 or 6; kind BANK), bare GB VAT with checksum (the keyword form is taken regardless), UK company numbers by prefix (`SC|NI|OC|SO|NC|LP|SL|NL|FC|R0|IP|SP|RS|CE|NP` plus 6 digits), date of birth by cue only (value-only span), URL with scheme or `www.` (trailing `.,;:` stripped). Defer IP addresses (clause references collide) and US SSN (optional, dashed only). The researcher's regexes and test rows are in companies_addresses_patterns, Q15.
- Fixes that apply regardless: phone gets a bracketed UK form `\(0\d{2,4}\)[ -]?\d{3,4}[ -]?\d{3,4}` and a shape check on national numbers, written `0(?:[1-3]\d{1,3}|7\d{3}|[58]00)` (the first revision's form rejected `020 7946 0958`). Do not gate spaced national numbers on a cue. For the unspaced `0\d{10}` form, a cue gate finds 3 of 6 test numbers and the no-gate option was not measured; the owner may prefer no gate and accept false hits on 11-digit references. Accept that `ref 0123 456 7890` is masked as a phone: A1 counts it as 66 over-masked characters and no leak. IBAN keeps the plan's check.
- Overlap rule: a checksum or keyword pattern outranks a bare PHONE (see Q5, kind order).
- Test rows (published test numbers): `GB 333289454` one span; `GB123456789` none bare but `VAT number GB123456789` one; `AB 12 34 56 C` one; `BG123456C` none; `Card 4111 1111 1111 1111 expires` one; `Ref 1234 5678 9012 3456` none; `Born on 1st May 1990` value `1st May 1990`; `Effective 5 November 2026` none; `Clause 12.3.4` none; `SC123456` one; `FC12345` none.

**(e) Risk.** Staying with the plan's five patterns leaves identifiers that code could have caught entirely to the detector. Adding more patterns raises test rows, golden-file churn and the owner's reading load; it also raises false hits on numbers, which over-mask.

**Status (22 Nov 2026):** CHANGE, adopted and widened. Phones: S4-M2-T2 has four forms (international, UK national with spaces or dashes, bracketed area code, 11 unseparated digits that start with 0) and no cue gate, so `0123 456 7890` is masked as a phone (a known limit). IBAN: S4-M2-T3. The verdict on the four extra patterns changed: the owner reversed plan question 24 on 22 Nov, so S4-M2-T12 builds a NINO, a GB VAT number with its checksum and a UK company number with a prefix (kind `ID`), and a Luhn-checked card number (kind `BANK`, plan question 26). URL, date of birth, IP address and US SSN are not built.

### Q16. Who owns the word lists

**(a) Plan.** "The lists are code constants in this plan, and the owner reads them with the plan. The finders table (S4-M2-T8) fixes their effect. A change to a list is a change to code and to the table, in two commits (Constitution T11)."

**(b) Verdict: KEEP.**

**(c) Evidence.** The researcher's reasoning is real, not anchored: Philter's gazetteer approach cost precision, and 16,095 of its names were also common words ([Philter paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC7156708/)). Sources that exist if a gazetteer is ever wanted: SSA baby names (CC0 appears only as the data.gov catalogue licence field; the SSA pages give no licence text and the zip readme was not opened; about 7 MB zip; SSA excludes names with fewer than 5 occurrences in any area and asks users to acknowledge eight data caveats, a request and not a licence condition) ([data.gov](https://catalog.data.gov/dataset/baby-names-from-social-security-card-applications-national-data), [SSA](https://www.ssa.gov/oact/babynames/limits.html)); the 2010 Census surname file (162,253 names with 100 or more occurrences, confirmed on the page; the page states no licence, and the only governing text found is policy DS027, which says works by Census employees are generally not copyrighted in the US; the citation page asks for a source credit, a request) ([Census](https://www.census.gov/topics/population/genealogy/data/2010_surnames.html)); Wikidata names under CC0 (confirmed: Wikidata:Licensing releases structured data under CC0; the repo README also warns that its family-names set is incomplete, which again says a list cannot be a required gate; its LICENSE file was not read) ([wikidata-names](https://github.com/commenthol/wikidata-names)); ONS baby names (the site terms put most content under the Open Government Licence v3.0, but the dataset page names no licence; OGL v3.0 requires an attribution statement and exempts personal data and third-party rights; [OGL v3](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)) ([ONS](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/datasets/babynamesinenglandandwalesfrom1996)). The sample's own `Benali` shows a US list cannot be a required gate. Gaps: there is no Census licence text, only the policy statement; the ONS dataset page names no licence (site-wide OGL only); the SSA and Census zips, the wikidata-names LICENSE and the Philter LICENSE were not read; the derived file sizes (25 to 60 KB) are estimates; no permissive common-word list (SCOWL, wordfreq) was examined.

**Test evidence and build gate.** B1's list check is neutral (see Q17). The nearby-field note suggests a gate for the lists: three stop sets (seed, form, trim), one reason per word, one test row per word, and a benign-corpus hit-rate script. See 'Ideas from nearby fields'.

**Rule conflict flagged for the owner.** AGENTS.md says "Keep the repo free of real data". Vendoring a name list derived from SSA or Census records is public statistical data about names, not about identifiable people, and the researcher judged it does not break the rule. The rule's literal wording is the owner's to interpret. The evidence note reads all four sources as published aggregates of names with counts, not records of identifiable people. If an ONS-derived list ever ships, the OGL attribution text must travel with it; a Census-derived list needs a provenance line; SSA and Wikidata data (CC0 as catalogued) need no attribution by licence. The report does not decide it, and recommends stage 4 does not vendor any such list.

**(d) Plan edit.** None to the ownership rule. Add the seed lists for the owner to review, as first drafts from general knowledge, not from a cited source: `LEGAL_STOP` (Agreement, Party, Parties, Schedule, Clause, Section, Annex, Appendix, Exhibit, Services, Service, Client, Customer, Supplier, Contractor, Consultant, Developer, Agency, Company, Employer, Employee, Licensor, Licensee, Buyer, Seller, Landlord, Tenant, Charges, Deliverables, Milestone, Effective, Date, Term, Confidential, Information, Intellectual, Property, Governing, Law, Force, Majeure, Termination, Payment, Fees, Notice, Notices, Director, Manager, Partner, Owner, Secretary) and `COMMON_WORD_NAMES` (the researcher's draft of about 60 words, in the person_names note, Q16). One module with a one-line reason per word; a test that every seed word has a `finders.toml` row; a test that any later gazetteer file has no entry in `LEGAL_STOP`. Seed `LEGAL_STOP` from the sample's `LinkMap.terms`.

**(e) Risk.** A vendored gazetteer adds an accuracy risk, a maintenance burden for a cheap implementer, a licence check and a possible rule conflict. A tiny curated list misses rare collisions; the document evidence rule (if the owner accepts it) and the detector back it up.

**Status (22 Nov 2026):** KEEP, decided (plan question 16, as recommended). The lists are code constants that the owner reads with the plan: `names.py` (S4-M2-T1) and `people.py` (S4-M2-T7). The owner writes the place list (S4-M2-T11). No SSA, Census, ONS or Wikidata list is vendored. How AGENTS.md ("Keep the repo free of real data") reads for such a list stays the owner's call.

## Links between questions

**Q5 and Q9: keyword in the span, and unions.**
- Keyword-inclusive spans are longer, so they beat a bare PHONE; a USER mark on the digits cuts them and leaves `company number ` as a nonsense ID fragment.
- Value-only spans are identical in length to a PHONE or BANK hit, so the kind index decides, and PHONE precedes ID and BANK in `PlaceholderKind`. Q5 is decided, and the local rank is built: `TIE_RANK` in S4-M3-T4 puts BANK and ID before PHONE, and `core` is unchanged. A1 never tested two kinds on the same characters.
- Same-source overlaps: the overlaps researcher proposed a union for NER of the same kind; the companies researcher raised the same need for RULE address spans. The owner decided NER only (21 Nov 2026) and answered plan question 21 as recommended: RULE and PATTERN are not joined. A3 measured the difference at 3 more cases in 5000. Presidio's own union is by type only (any score, any source), so the same-source limit is a design choice. Never for USER or PARTY_DETAILS.

**Q1, Q4, Q11, Q17: one name system.**
- `LEGAL_STOP` (Q17) vetoes cue-found runs and trims them. It must **not** feed forms generated from a typed party or from a defined-term short name, or a party named with a role word loses its one-word form. Conversely Q11 rule 2b makes a subset term a name, but if a stop list blocks the code finder, only the detector can mask a bare `Studio`; state this limit in the plan.
- A role word is not a name (Q4, Q11), yet a real surname can equal a role (`Agency`, `Owner`). The veto applies only to cue-found seeds with no honorific; an honorific, signature or label cue overrides it unless every token is a legal word.
- A strong cue bypasses stop lists (Q17 layer 1), consistent with Q1's cue tiers and Q4's titled form.
- Q17 layers 3 and 4 reduce masking and interact with Q4's new forms (more one-word forms means more skips). Decide Q17's layers before accepting Q4's hyphen and initial forms.
- `COMMON_WORD_NAMES` words that also serve as defined terms (`Grant` for a grant of rights) are allow-listed anyway by the plan; keep the single `ambiguous_name_policy` constant.

**Q6 and Q10: token form, restore and escape.** Both stand together on `⟦Kind N⟧`. If the format ever changes, `PLACEHOLDER_OPEN` and `PLACEHOLDER_CLOSE` in `core/enums.py`, `PLACEHOLDER_PATTERN`, the escape rule (escape whatever the new markers are, on the original text) and `restore_reply` change together, and golden files are regenerated with the named command and read by the owner (T11). Inside-marker folding in Q6 is safe only because Q10 guarantees `⟦` never appears outside real tokens. A4 and B2 now measure both: on a Claude model `⟦Person n⟧` costs +3.65 tokens per placeholder, and with the explicit copy instruction no form was mutilated in 152 replies. The owner kept `⟦ ⟧` (decision 2). The escape rule matches the defence shipped by piighost.

**Q4 and Q12: variants and ambiguity.** Every new form in Q4 (initial plus last, hyphen parts, first name alone) can fit two people. Ambiguity must be decided by the set of entities that generate a form (Q12 edit), not by token subset, or `S Jones` would join the wrong person. This is the exact failure 2610.34012 App. C p20 records (a landlord and a tenant merged by surname, "worse than a leak"), so the form-set rule is not a refinement but the main guard.

**Q14 and Q9: drop versus cut at the place.** The first plan dropped a whole span that touches the place (leak); the researchers' principle is to cut. The owner decided the hybrid (decision 6): cut every kind except PERSON and COMPANY, which stay whole and let the place lose the overlap (S4-M3-T3). With the closed list of Q14 true overlaps become rare, but the cut rule must still exist. A3 P11 confirms the leak on random input and passes with the cut.

**Q7 and the stage 7 adapter contract.** Whole-text call at the port means the adapter owns windowing, offsets in code points, no silent truncation, no copied text in errors, and a named error. The stage 4 side is fail-closed validation and no exception swallowing (S4-M3-T1, S4-M3-T6), and the contract is in system design 15.7. A flaky adapter will then stop runs, so stage 7 should give the app a way to show "the detector failed" and not a code-only result as complete.

**Q13 and Q17.** The free-text replacer is stage 8, but the capital-letter rule differs by source (contract text is capitalised, typed text is not). System design 15.8 says one-word forms match without regard to case there; the stage 8 plan must still state the stop-list treatment.

## Test results

Six test tracks ran after the first revision. The researchers wrote their own scratch code outside the repo, and no repo file changed. I copied the numbers below from the result files and checked each against them. I did not re-run the tests. Real contracts stayed outside the repo and only counts are reported. The tests used invented text except B1, and the only invented names used here are those in the test files.

| Track | What it tested | Size and data | Cost |
|---|---|---|---|
| A1 | The plan's rules against the replacement rules of the research notes | 367 invented snippets, 470 true spans, 714 distractor spans | Free |
| A2 | Eight defects named in this report, reproduced as code | 64 tests (22 fail, 42 pass), invented text | Free |
| A3 | Hypothesis properties of the overlap step and the union amendment | 5000 examples per property | Free |
| A4 | Token counts of placeholder forms in OpenAI and GPT-2 vocabularies | One 596-word paragraph, 20 placeholders per form | Free |
| B1 | The rules on real contracts, counts only | 510 contracts, 26.82 MB of text | Free |
| B2 | A paid run on Claude haiku and sonnet models through OpenRouter | 544 copy-rate calls, 60 spoof calls, token counts, invented text | $0.812 |

### A1: the plan's rules against the replacement rules

"Plan" is the reference code of the plan, unchanged. "Replacement" is the set of fragments in the research notes. Both ran the same pipeline: finders, trim, governing-law step, overlap resolution. A1 measures spans a cue rule can reach (421 of 470). A detector was simulated only for the governing-law place.

| Measure (421 reachable spans) | Plan | Replacement |
|---|---|---|
| Span recall (every letter and digit covered) | 290 of 421 (68.9%) | 415 of 421 (98.6%) |
| Character recall | 3573 of 4552 (78.5%) | 4527 of 4552 (99.5%) |
| Leaked letters and digits | 979 | 25 |
| Spans with any leak | 131 | 6 |
| Truncations (union definition) | 60 | 0 |
| Truncations (one predicted span must cover it) | 64 | 4 |
| Spans missed outright | 71 | 6 |
| Over-masked characters | 978 | 225 |
| Over-masked characters, ID and bank keywords counted as neutral | 727 | 225 |
| False-positive spans (touch no true span) | 46 | 17 |
| Distractor spans hit | 46 of 714 | 17 of 714 |
| Hard-name group (7 groups, 97 spans): covered | 26 of 97 | 97 of 97 |
| Hard-name group: letters leaked | 491 | 0 |

The 4 literal truncations of the replacement are all `Jones, Sarah`, covered by two spans with no letter left out. The 25 leaked letters are one cause: a bare `Will`, `Grant`, `Mark` or `Bill` after `Contact`, which the stop list skips on purpose.

| Kind | Spans | Plan span recall | Replacement span recall | Plan letters leaked | Replacement letters leaked |
|---|---|---|---|---|---|
| Person | 256 | 173 (67.6%) | 250 (97.7%) | 576 | 25 |
| Company | 56 | 48 (85.7%) | 56 (100.0%) | 25 | 0 |
| Address | 46 | 18 (39.1%) | 46 (100.0%) | 246 | 0 |
| Email | 12 | 12 (100.0%) | 12 (100.0%) | 0 | 0 |
| Phone | 21 | 12 (57.1%) | 21 (100.0%) | 99 | 0 |
| ID | 12 | 9 (75.0%) | 12 (100.0%) | 33 | 0 |
| Bank | 18 | 18 (100.0%) | 18 (100.0%) | 0 | 0 |
| Total | 421 | 290 (68.9%) | 415 (98.6%) | 979 | 25 |

| Spans no cue rule can reach | Plan | Replacement |
|---|---|---|
| Bare names and numbers, no cue anywhere: span recall | 0 of 24 | 0 of 24 |
| Same spans: letters leaked | 233 | 233 |
| Full name after a surname-only cue: span recall | 0 of 25 | 0 of 25 |
| Same spans: letters leaked (first names) | 185 | 138 |
| All 470 spans: span recall | 290 (61.7%) | 415 (88.3%) |
| All 470 spans: character recall | 72.4% | 92.2% |
| All 470 spans: letters leaked | 1397 | 396 |

Per-question variants (letters and digits unless stated):

| Question | Group | Plan | Replacement or variant |
|---|---|---|---|
| Q2 | Company spans | 48 of 56, 25 leaked | 56 of 56, 0 leaked |
| Q2 | `Limited Warranty` family and `Co-operative` look-alikes | 13 of 13 hit (125 and 90 over-masked characters) | 0 of 13 hit |
| Q3 | Address spans | 18 of 46, 246 leaked | 46 of 46, 0 leaked |
| Q3 | Address look-alikes (`5 Way of life`) | 5 of 8 hit | 0 of 8 hit |
| Q3 | Adversarial chain start (capitalised word and number before the address) | not measured | 3 of 6 start too early, 22 over-masked characters, no leak |
| Q5 | Over-masked characters, value-only against keyword in span (same recall, 415 of 421) | 978 | 225 value-only; 511 with the keyword in the span |
| Q14 | Detector flags left standing on 27 place spans | 10 of 27 | 5 of 27 (all outside A1's own list) |
| Q14 | `laws of England Sarah Jones signs`: person leaked | 6 of 12 spans, 60 leaked | 0 of 12 |
| Q15 | Bracketed phones | 0 of 6, 66 leaked | 6 of 6 |
| Q15 | Unspaced phones | 0 of 6 | 3 of 6 (the others have no cue) |
| Q15 | `ref 0123 456 7890` false hits | 6 of 6 | 6 of 6; 0 with a cue gate, which leaks 44 on 4 of 4 bare numbers |
| Q17 | Months, `Ms May`, `May Lee` | 0 leaked, 0 false hits | 0 leaked, 0 false hits |
| Q17 | Bare `Contact Will`, `Contact Grant`, `Contact Bill` | 25 leaked (6 spans) | 25 leaked (6 spans) |
| Q17 | Bare sentence-initial `Hope`, `Frank`, `Lane` | 6 of 6 hit, 25 over-masked | 6 of 6 hit; layer 3: 2 of 6 hit, 8 over-masked, no new leak |

What to distrust in A1:

- **The corpus is an upper bound.** It was built around the failures the notes list, and the replacement rules were written from the same notes. The size of the gap per group is real for those shapes. The level (98.6%) is not an estimate for real contracts.
- **The tester relabelled after seeing results.** Surname-only-cue mentions became `partial`, bare numbers became `nocue`, and one phone wording changed. That moved the headline denominator from 429 to 421. It is the same for both rule sets. The tester also added the groups `ADDR_ADV`, `LEADVERB_UNLISTED`, `PAY_UNLISTED`, `GL_OUT` and `PHONE_BARE` after the first run, to look for costs of the replacement rules.
- **Regular templates and small groups.** Groups have 4 to 30 spans, so a figure such as 15 of 15 against 4 of 15 is a clear sign with no useful interval. One generator seed (20261121), no cross-validation.
- **Choices the tester made where the notes were open.** The lead-word list gained `Please` and `Notify`. The phone shape regex was changed because the notes' form rejects `020 7946 0958`. `07700900123` is accepted only after a cue word. `Ms May` is kept, because only seeds made entirely of legal words are vetoed. The place list is the tester's own, about 29 countries and regions plus US states, and it contains the places the corpus uses, except five.
- **The layer 3 word list overlaps the test words**, so its gain is an upper bound.
- **Not run:** the typed-party path, the defined-term allow-list, a real detector, the sample contract, held-out shapes. The right-kind recall equals the any-kind recall in every row, because no case put two kinds on the same characters, so kind labelling and the kind-order trap were not tested. `Clause 1.2.3.4` read as an IP address was not tested, because neither rule set has an IP finder.

### A2: eight defects reproduced as code

All eight defects reproduce. 22 plan tests fail and 42 pass (the 42 include the fix versions, guards, controls and subcases where the plan is right).

| Defect | Plan result | Fix result | Caveat |
|---|---|---|---|
| 1. Name fragments cut names | 6 of 6 fail (`Sean O'`, `Ann Mc`, `Ana Smith-`, and no match for `SARAH JONES`, `Sarah J. Jones`, `Maria de la Cruz`) | 6 of 6 pass | None |
| 2. Governing-law over-capture | 2 of 2 fail (`England Sarah Jones` kept; the person on the first `Sarah Jones` dropped) | 2 of 2 pass | None |
| 3. Governing-law under-capture | 2 of 2 fail (no place for `State of Delaware`, `Republic of Ireland`) | 2 of 2 pass | The fix keeps `Ireland`, not `Republic of Ireland`; the owner should confirm |
| 4. `drop_in_places` drops a whole span | 1 of 1 fails (`Hall Road` not kept) | 1 of 1 passes | Reproduced only with an injected span, because the plan's own address regex cannot find `Hall Road, England`. A real path with a house number was not run |
| 5. Allow-list leak for an untyped party | 1 of 1 fails (bare `Mercury` not covered); `Agency` stays readable | 2 of 2 pass | None |
| 6. Offset validation | 3 of 6 fail (reversed, start past text, bool) | 6 of 6 pass | Only partly confirmed: an end past the text, `None` and a float already raise (the last two by accident, as `TypeError`) |
| 7. Company false positives | 3 of 3 fail (`Provider Limited`, `Co-operative Bank Co`, `Pay Acme Ltd`) | 3 of 3 pass | None |
| 8. Postcodes and bare street words | 4 of 4 fail (postcode and ZIP dropped, `5 Way`, `2 Court`) | 4 of 4 pass | The start-token rule for `Suite` is the tester's reading of the note |

The fixes are the tester's own code from the notes, with a short place list (about 18 names) and simplified lead-word and address-window logic. They are evidence that the defects are real, not code to reuse.

### A3: Hypothesis properties of the overlap step

The tester ran 11 properties at 5000 examples each against the plan's resolver, and against the union amendment for NER and for NER, RULE and PATTERN together.

| Property | Plan | Union (NER) | Union (all three) | Reading |
|---|---|---|---|---|
| P1 to P6: disjoint and sorted; no letter or digit lost; no invention; priority; idempotent; order-independent | Pass | Pass | Pass | The plan's rule is sound |
| P7: one extra suggestion never removes cover (revised after the first run) | Pass | Pass | Pass | The first version drew empty extras about 20% of the time |
| P8: identity on clean input (revised, no `assume`) | Pass | Pass | Pass | The first version discarded about 3000 inputs per 5000 |
| P9a and P9b: split keeps cover, kind and source; no start inside a piece; idempotent | Pass | Pass | Pass | Supports Q8 |
| P10: validator raises for `start < 0` or `end > len` (the plan's own definition) | Pass | Not applicable | Not applicable | The plan matches its own text |
| P10b: validator also raises for a reversed span (the stricter note definition) | Fail | Not applicable | Not applicable | A gap in the plan text, not a defect in the rule |
| P10c: non-integer offsets raise | Fail | Not applicable | Not applicable | The property was mistaken for empty spans; it still exposes bool offsets accepted and `TypeError` instead of `ValueError` |
| P11: composed pipeline keeps every letter a detector flagged, outside the place | Fail | Fail | Fail | A real defect: a span that runs into the place is dropped whole |
| P11 with the place cut instead of dropped (diagnostic) | Pass | Not run | Not run | The cut fixes it |

So 10 of the 11 properties pass. P10 passes on the plan's own definition, and P10b and P10c are variants that fail as gaps, not as defects of the rule. P11 is the one real defect. An earlier version of P11 was itself mistaken, because it did not exempt the place that Spec 4.2 keeps on purpose.

Other findings:

- **The union amendment** changes 5 of 5000 random cases for NER and 8 of 5000 for the three sources together. Output span counts are 5741 (plan), 5737 and 5735. Touching or overlapping same-kind, same-source pairs left in the output: 30, 29 and 28. It fixes the note's example (`Sarah Jo` and `ah Jones` become one span; the plan gives `Sarah Jo` and `nes`). The ten example tests of S4-M3-T4 and the note's case pass under all three (the tester transcribed them, because the repo's test file does not exist yet).
- **`split_at`:** the reference code returns pieces in input order. S4-M3-T5 says to return through `unique_sorted`. The gap is in the reference code, not in the plan text.
- **Offsets:** `trim_all` checks only `start < 0` and `end > len`. A reversed in-range span is dropped silently; a bool offset is accepted; a non-empty float or `None` raises `TypeError`.
- **Unexplained:** Hypothesis discarded some generated inputs as invalid, and the tester did not investigate why.

### A4: token counts in local vocabularies

These are OpenAI and GPT-2 vocabularies. They do not give Claude's token use (B2 does).

| Form | Standalone, o200k_base | Standalone, cl100k_base | Standalone, GPT-2 |
|---|---|---|---|
| `⟦Person 1⟧` | 9 | 7 | 8 |
| `[Person 1]` | 5 | 5 | 4 |
| `[PERSON_1]` | 5 | 5 | 6 |
| `<PERSON_1>` | 5 | 5 | 6 |

| Form (paragraph of 596 words, 20 placeholders) | o200k_base | cl100k_base | GPT-2 |
|---|---|---|---|
| Baseline (every slot is `Zed`) | 673 | 676 | 659 |
| `⟦Person n⟧` | 813 | 776 | 799 |
| `[Person n]` | 726 | 729 | 712 |
| `[PERSON_n]` | 733 | 736 | 765 |
| `<PERSON_n>` | 733 | 736 | 765 |
| Overhead of `⟦ ⟧` over `[ ]` | 11.98% | 6.45% | 12.22% |

The opening `⟦` is three byte tokens in o200k_base and GPT-2, and two in cl100k_base. The closing `]` merges with a following `.`, `,`, `;`, `)` or `:`; `⟧` never merges. The extra cost of `⟦ ⟧` over `[ ]` in context is 4.35 tokens per placeholder in o200k_base and GPT-2, and 2.35 in cl100k_base.

### B2: a paid run on Claude haiku and sonnet models

All text was invented. The run cost **$0.812** of a $2.00 key, which is 1.2 cents over the tester's own $0.80 cap: calls stopped at $0.77, and 8 in-flight sonnet calls finished after that. About $1.19 of the key is left. The pilot (3 calls) cost $0.0069. No key or authorisation header is kept in this report or in the repo.

Prompt tokens (identical for both models, so the tokeniser is the same). Fixed overhead of 11 tokens is subtracted. The test text holds 40 placeholders in 514 words, five kinds. The per-placeholder figure is approximate, because the plain-name baseline also swaps dates and amounts. The ranking between forms is exact. The density is high, so the 14% below is specific to it.

| Form | Prompt tokens, overhead removed | Difference from plain names | Per placeholder |
|---|---|---|---|
| Plain invented names | 1007 | 0 | 0 |
| `⟦Person n⟧` | 1153 | +146 (about 14%) | +3.65 |
| `[Person n]` | 920 | -87 | -2.17 |
| `[PERSON_n]` | 1015 | +8 | +0.20 |
| `<PERSON_n>` | 1022 | +15 | +0.38 |

Copy rate. A reply is mutilated when a token has a changed bracket or a lone opener. "Dangerous" means an invented token or a changed id.

| Form | No instruction: mutilated of non-empty | With the copy instruction: mutilated of non-empty | Dangerous failures |
|---|---|---|---|
| `⟦Person n⟧` | 11 of 51 | 0 of 29 | 0 |
| `[Person n]` | 8 of 49 | 0 of 36 | 0 |
| `[PERSON_n]` | 0 of 47 | 0 of 39 | 0 |
| `<PERSON_n>` | 9 of 54 | 0 of 48 | 0 |
| All forms | 28 of 201 | 0 of 152 | 0 |

| Model | Instruction | Non-empty of total | Mutilated replies |
|---|---|---|---|
| Haiku | No | 146 of 216 | 21 |
| Haiku | Yes | 98 of 216 | 0 |
| Sonnet | No | 55 of 56 | 7 |
| Sonnet | Yes | 54 of 56 | 0 |

- **0 of 544 calls produced a dangerous failure, but only 353 of the 544 returned a non-empty reply** (146, 98, 55 and 54). The file's bound of about 0.6% divides by 544. On the 353 replies that could fail, the same rule of three gives about 0.8% (my arithmetic). For any single form and instruction cell the bound is about 4%.
- **The instruction removed every mutilation:** 0 of 152 replies, an upper bound of about 2%. Caveat: with the instruction haiku returned more empty replies (118 of 216 against 70 of 216), so part of the effect may come from which replies finished. Sonnet, with almost no empty replies, shows the same effect (7 of 55 mutilated without, 0 of 54 with).
- **Empty replies:** haiku returned an empty reply in 188 of 480 calls (M2 and spoof together) and sonnet in 3 of 124. Reasoning is on by default and took a mean of 398 of the 500 allowed tokens for haiku. The cap stopped a re-run with a larger limit.
- **Cut by the cap:** sonnet got 112 of 216 planned copy-rate calls, and the spoof test without the instruction only (12 of 24).
- **Sample sizes:** sonnet has 12 to 15 replies per form and instruction; haiku 54 calls per cell but about 40% empty; the spoof test 3 to 6 replies per cell.

Spoof test. The contract author types a fake `Person 9`. The escape rule sends it in another style. "Re-created" means the reply wrote the fake back in its original style.

| Form | Haiku, no instruction | Haiku, with instruction | Sonnet, no instruction |
|---|---|---|---|
| `⟦Person n⟧` | 0 of 6 | 0 of 6 | 0 of 3 |
| `[Person n]` | 2 of 6 | 0 of 6 | 0 of 3 |
| `[PERSON_n]` | 2 of 6 | 0 of 6 | 0 of 3 |
| `<PERSON_n>` | 1 of 6 | 0 of 6 | 0 of 3 |

The three ASCII forms re-created the fake in 5 of 27 replies without the instruction, against 0 of 9 for `⟦ ⟧`. That is not significant (the upper bound for `⟦ ⟧` is about 33%). Sonnet was not run with the instruction. The escape styles for the three ASCII forms were the tester's own choice. The fake's number (9) was never sent, so a check against the closed set of ids would catch it; a check on the label alone would not.

### B1: the rules on 510 real contracts (counts only)

CUAD_v1, 510 contracts, 26,807,133 characters. The data stayed outside the repo, and only counts left the scratch folder. No contract text, party name or person name appears here. "Covered" means every letter and digit of an annotated party answer lies inside a predicted COMPANY or PERSON span. 509 contracts have at least one party answer.

| Group | Answers | Plan fully covered | Replacement fully covered |
|---|---|---|---|
| Companies (a legal-suffix token in the answer) | 1287 | 215 (16.7%) | 313 (24.3%) |
| Other parties | 1259 | 60 (4.8%) | 96 (7.6%) |
| All party answers | 2546 | 275 (10.8%) | 409 (16.1%) |
| Characters covered (all answers) | 50,382 | 6500 (12.9%) | 9427 (18.7%) |

| Kind | Plan spans | Plan per 100 KB | Replacement spans | Replacement per 100 KB |
|---|---|---|---|---|
| Person | 1256 | 4.68 | 2805 | 10.46 |
| Company | 1839 | 6.86 | 2349 | 8.76 |
| Address | 993 | 3.70 | 1459 | 5.44 |
| Email | 339 | 1.26 | 339 | 1.26 |
| Phone | 91 | 0.34 | 76 | 0.28 |
| ID | 11 | 0.04 | 11 | 0.04 |
| Bank | 1 | 0.00 | 1 | 0.00 |
| All | 4530 | 16.89 | 7040 | 26.25 |

These densities are not precision. No labelled ground truth exists for false positives.

| Other measure | Plan | Replacement |
|---|---|---|
| PERSON predictions whose first token is in the month, day, legal-word or common-word list | 4 of 1256 (0.32%) | 12 of 2805 (0.43%) |
| Governing-law places kept (unit: places) | 22 | 134 |
| Contracts with a kept place (437 have a governing-law annotation) | 22 | 128 |
| Kept places that share a word with a PERSON or COMPANY span in the same contract | 2 | 4 |
| Phone spans with no cue word within 40 characters and under 11 digits | 19 of 91 (20.9%) | 5 of 76 (6.6%) |
| Four-group dotted numbers (one regex for both) | 548 matches, all with valid octets, 99 after a clause-type cue (18.1%) | same |
| Run time over 26.82 MB | 36.4 s (1.36 s per MB) | 40.3 s (1.50 s per MB) |

The replacement's 12 first tokens are `mark` 8 and `frank` 4; the plan's 4 are all `frank`. Counts cannot show whether these are real names, so this is not a win for either rule set. All 548 dotted matches have octets from 0 to 255, so an octet check alone rejects none. The cue words remove at most 99 (18.1%). The other 449 were not examined, and the test cannot say what they are.

Limits stated by the tester: CUAD is mostly US SEC filings, and the rules were built for UK and EU text and were not tuned on it. Party annotations are partial and can include defined terms, states of incorporation or addresses. A company is identified only by a legal-suffix token. The full-cover measure is strict, so it is a floor, and the character-level share is the fairer figure. One run on one machine, so timings are indicative.

### A ceiling and a floor: the invented corpus and the real contracts

The two numbers must not be read as one range. **A1 is an upper bound.** The corpus was built around the known failures, the replacement rules were written from the same notes, and templates are regular. The 98.6% span recall tells how well the replacement fixes those shapes. It does not estimate real contracts.

**B1 is a floor.** The test did not feed typed party details, which is the mechanism the plan relies on for the parties the user names. The measure is strict: a party answer counts only if every character is covered, and many answers carry a defined-term tail, a state of incorporation or an address that no COMPANY span covers. The contracts are mostly US SEC filings, and the rules were built for UK and EU text and not tuned on them. The tester did not split the causes of the misses (all-capitals names, a missing suffix, trailing text), so no cause is known.

**What follows for Q1.** Cue rules alone will not find most parties: the replacement fully covers 16.1% of annotated party answers and 18.7% of their characters. That is not a surprise and not yet a product risk. ADR 0008 puts the promise on a deterministic layer in front (typed party details and their variants, checksum patterns, company-suffix rules and address rules), with NER as the net behind it. So the typed party details and the stage 7 detector carry the rest, and the cue rules are one part of the front layer. The unsure display matters more: code cannot reach a party that nobody typed and the detector did not flag. **I do not call the 16% a product risk until the typed-party follow-up (see 'Open owner questions') has run.** Until then no CUAD figure goes into the spec or an ADR.

### Later work: plan simulations and checks (22 Nov 2026)

This work tested the plan, not the finder rules. The numbers come from the plan's change log (rows of 21 and 22 Nov) and from the reports of the agents that ran each step. I did not re-run any of them. The scratch copies are outside the repo.

| Step | What ran | Result |
|---|---|---|
| M1 and M2 simulation | A cheap implementer built the tasks from the plan text alone, in a copy | 190 tests passing; 1 plan defect (the S4-M2-T9 example); about a dozen ambiguities closed (S4-M1-T3, S4-M1-T6, S4-M2-T1, S4-M2-T4, S4-M2-T7, S4-M2-T9, S4-M2-T10, S4-M2-T11) |
| M3 simulation, T1 to T6 and T11 | The same method on the changed M3 tasks | 135 tests passing; lint defects in the plan's code blocks found and fixed (line length, `zip` strictness, `Final` annotations); four ambiguities closed (S4-M3-T1, S4-M3-T2, S4-M3-T11) |
| Plan checker | A script over task ids, dependencies, define-and-use order, test counts and links | 43 tasks, 442 tests, no findings |
| Real repo | `scripts/check.sh` after the docs edits | Exits 0 |
| Property timing | Hypothesis at 1,000 examples | About 10 s for each property; the privacy suite took about 2 min 18 s in the copy, before M4 and before S4-M2-T12 |
| S4-M2-T12 | A mini-simulation of the 35 new tests | 61 passed; ruff, mypy and lint-imports clean; 10 of 11 mutants caught |
| S4-M2-T12 | A differential run of the new finders against the reference code | 0 differences on 307 real inputs (counts only, no text kept) |

What these numbers do not show:

- **Not simulated:** M3 tasks T7 to T10, all of M4 and all of M5 (the owner's choice), and S4-M2-T12 beyond the mini-simulation above.
- **Old checks not repeated for T12.** The earlier 11 properties and the defect tests were not re-run after S4-M2-T12, because their scratch files were lost. The 61 passed tests are the new tests and their neighbours, not the whole suite.
- **One mutant survived.** 10 of 11 mutants were caught. I was not told which one survived.
- **The end-to-end run on the sample** ran once, on 21 Nov, before the M3 changes and before S4-M2-T12 (7 entities, 10 spans, an exact restore). It was not repeated.
- **A simulation by a cheap implementer shows that the text is complete enough to build from.** It does not show that the rules find personal data in real contracts. That is the job of the tests above and of the CUAD follow-up.

### Per-question summary

| Q | What was measured | The number | Supports the verdict? |
|---|---|---|---|
| 1 | Hard-name spans (A1); party answers on real contracts (B1) | 26 of 97 against 97 of 97; 16.1% of 2,546 answers (plan 10.8%) | Yes for the change. B1 shows cue rules alone are not enough, which is a floor |
| 2 | Company spans and look-alikes (A1); reproduction (A2) | 48 of 56 against 56 of 56; look-alike hits 13 of 13 against 0 of 13; A2 3 of 3 | Yes |
| 3 | Address spans and look-alikes (A1); reproduction (A2) | 18 of 46 against 46 of 46; look-alikes 5 of 8 against 0 of 8; A2 4 of 4 | Yes, with one cost: 3 of 6 adversarial chains start too early |
| 4 | Not measured: no typed-party path was run | None | Neither way |
| 5 | Recall and over-masked characters, value-only against keyword in span (A1) | Same recall (415 of 421); over-masked 511 against 225 | Yes. The kind-order trap is untested |
| 6 | Mutilated and dangerous replies (B2) | 0 of 152 with the instruction, 28 of 201 without; 0 of 544 calls dangerous, 353 non-empty | Yes |
| 7 | Offset cases (A2); validator properties (A3) | 3 of 6 confirmed; P10 passes, P10b fails | Yes. The plan text is looser than needed |
| 8 | Split properties (A3) | P9a and P9b pass 5000 each | Yes |
| 9 | Overlap properties and the union (A3) | P1 to P9 pass, P11 fails; union differs in 5 and 8 of 5000 | Yes for keep and for the cut at the place. The union gain is small |
| 10 | Token cost (B2, A4); copy rate and spoof (B2) | +3.65 per placeholder, about 14% on dense text; mutilation 11 of 51; spoof 0 of 9 against 5 of 27 | Mixed. Keep is the owner's call; the data favour `[PERSON_n]` on cost and copy rate |
| 11 | Reproduction (A2) | Bare `Mercury` leaks; `Agency` stays readable | Yes |
| 12 | Not measured | None | Neither way |
| 13 | Not measured | None | Neither way |
| 14 | Flags and over-capture (A1); real contracts (B1); reproduction (A2); P11 (A3) | 10 against 5 of 27 flags; 6 of 12 leak against 0; places kept 22 against 134 | Yes. The cost of the owner's own list does not show in A1 |
| 15 | Phones (A1); proxies (B1) | Bracketed 0 of 6 against 6 of 6; a cue gate leaks 44 on 4 of 4; the shape check leaves 6 of 6 references; no-cue short phones 20.9% against 6.6% | Partly. Phone fixes yes; no cue gate. The verdict text changed |
| 16 | Listed first tokens (B1) | 4 against 12 | Neutral |
| 17 | Stop-list groups (A1); first tokens (B1) | 0 month leaks; 25 letters on `Contact Will`; layer 3: 6 of 6 hits to 2 of 6 | Yes for the list, the vetoes and layer 3 |

## Where each change belongs

This section was a plan of work in the second revision. It is now a record of what is done. The plans README ("When the plan is wrong") lets a planner split, reorder or add a task alone, and requires the owner for anything that touches the spec, the system design, the testing strategy or a decision record. Group A stayed inside the stage 4 plan. Group B touched accepted documents. Group C needed no change.

### Group A: plan-only changes in the stage 4 tasks

All of group A is done in the plan: 43 tasks, 442 tests, and the plan checker reports no findings. Each change moved expected test values; the planner took them from the reference code and marked them "owner to confirm" (Constitution T11).

| Change | Questions | Task | Status |
|---|---|---|---|
| Name fragments, cues, trims; name variants | Q1, Q4 | S4-M2-T7, S4-M2-T1 | Done for the three cue rules, the name token and the trims. Not done: label lines, contact and individual-party cues, a date veto, and the extra forms of Q4 (initial, surname first, suffix, hyphen, nickname) |
| Company and address rules | Q2, Q3 | S4-M2-T5, S4-M2-T6 | Done. An over-long address chain keeps a truncated chain (plan 23, decided 22 Nov 2026), not the postcode alone |
| Closed place list (the owner's five categories) | Q14 | S4-M3-T3 | Done in the plan. The list file S4-M2-T11 is an owner task and is not written |
| Cut instead of drop at the place; hybrid for `PERSON` and `COMPANY` | Q9, Q14 | S4-M3-T3 (`cut_in_places`), S4-M3-T11 (P11, P12) | Done |
| Offset checks with `ValueError` and the `privacy:` prefix; no swallowed detector error | Q7 | S4-M3-T1, S4-M3-T6 | Done |
| `split_at` returns through `unique_sorted` | Q8 | S4-M3-T5 | No plan edit was needed: the task already says so |
| Mercury subset rule | Q11 | S4-M3-T2 | Done |
| Phone forms with no cue gate | Q15 | S4-M2-T2 | Done (four forms, including 11 unseparated digits) |
| Four more patterns: NINO, Luhn card, bare GB VAT, company prefixes | Q15 | S4-M2-T12 | Done (35 tests) |
| Legal-word veto; layer 3 with layer 4 off | Q17 | S4-M2-T1, S4-M2-T4, S4-M2-T7 | Done. Not done: the one `ambiguous_name_policy` constant. Not taken: moving `will`, `mark`, `grant` and `bill` to layer 3 |
| Union for `NER` spans only | Q9 | S4-M3-T4 (`union_ner`) | Done |
| Value-only ID spans, with a local rank so ID and BANK beat PHONE | Q5 | S4-M2-T2, S4-M3-T4 (`TIE_RANK`) | Done |
| One entity per form, by the set of entities that generate the form | Q12 | S4-M3-T7 | Not done as written. T7 groups by word sets and gives a short form of two heads its own entity |

### Group B: changes to accepted documents

| Change | Document | Status |
|---|---|---|
| Stage 7 adapter contract (whole text, code-point offsets, no silent truncation, fail closed, spans only) | System design 15.7; plan section 9 | Done as text. The change to the `PiiDetector` docstring ("Raises: None") is a stage 7 `core` task and is not done |
| The doubt shape | Stage 1 plan, S1-M6-T8 (own branch `feat/core-doubt-shape`) | The task is written in the stage 1 plan. Not done: the `core` code, and the Doubt rows of system design 3.4, which come with S1-M6-T8 |
| The "write placeholders exactly" prompt rule | System design 15.8 (stage 8) | Done |
| The stage 8 free-text replacer and the import wall | System design 15.8; plan section 9 | Done as text. The replacer is built in stage 8 |
| Spec 4.2: closed place list and hybrid clause | Spec 4.2 (Kept line); Spec 13 line | Done: two clauses in the Kept line and one Spec 13 line |
| ADR 0008 amendment of 22 Nov 2026 | ADR 0008 | Done |
| Spec 4.2 sentence for an ambiguous short form | Spec 4.2 | Not done. The report's draft was not added to the spec |
| The `privacy` row | Testing strategy section 4 | Done: true and false rows, value-only spans, the closed list, the hybrid, properties of the resolve step, `ValueError` on a bad offset |
| The prototype ID row | `prototype/privacy-check.html` | Done: "company number" stays outside the span |
| The promise table | WRITING_DOCS | Done: one row for the kept place |
| Reordering `PlaceholderKind` | `core/enums.py` | Not needed: `TIE_RANK` in `privacy` does the job |
| New placeholder kinds (URL, date of birth) | `core/enums.py`, Spec 4.2, prototype | Not done, as recommended. A card number uses `BANK` |
| Plan listed in the plans README; task plan line in system design 15.4 | `docs/plans/README.md`; system design 15.4 | Done |

The ux-copy "Kept" note names England and Wales. It is unchanged and still true, because that place is in the closed list.

### Group C: no change

- **The token form `⟦ ⟧`.** Decided by the owner, with no ADR. The format stays one constant in `core/enums.py`.
- **Spec 8.4 exact restore.** B2 shows exact match plus one retry works. No tolerant restore was added.
- **CUAD numbers in the spec or an ADR.** None. The result is a floor until the typed-party follow-up has run.

### Not done

- The `core` code of S1-M6-T8 (`DoubtCode` and `Doubt`), and the Doubt rows of system design 3.4.
- The `PiiDetector` docstring change, a stage 7 `core` task.
- The seven owner tasks: the finders table (S4-M2-T8), the party details table (S4-M2-T9), the place list (S4-M2-T11), the pipeline table (S4-M3-T8), the entities table (S4-M3-T9), the sample table (S4-M5-T5) and the reading of the golden files (S4-M5-T7).

## Ideas from nearby fields

Four notes looked outside the privacy field: localisation and machine translation, court pseudonymisation, secret scanners and legal extractors, and name matching and signature blocks. The table lists each idea as an exact rule. All rules are pure code, with no model call. The owner writes any word list and expected value (Constitution T11). The last column labels how strong the source is.

| Idea | Exact rule | Question | Licence note | Source strength |
|---|---|---|---|---|
| Tag-parity check and closed id set | Compare the tokens found in a reply with the tokens sent, as multisets. An extra token breaks the reply and nothing is restored. A missing token is recorded as dropped. Restore only exact members of the set sent; never pick the nearest id | Q6 | None; write it fresh | Practitioner blogs and vendor pages, plus [Hanneman and Dinu 2020](https://aclanthology.org/2020.wmt-1.138.pdf) (peer-reviewed) for the failure classes. The rule is the researchers' own |
| Explicit copy instruction | Every prompt that carries placeholders says: copy each token exactly, never write a new one | Q6, Q10 | None | Strong: B2 (0 of 152 mutilated with it, 28 replies without), [Jon and Bojar 2026](https://aclanthology.org/2026.lrec-1.34.pdf) (25.4 to 87.8 BLEU on a small model), and Veil-then-Reveal (31 to 52 of 137 repeats on a small model) |
| One retry | If a reply fails the parity or closed-set check, send one retry that lists the exact missing and extra tokens and nothing new. If it fails, show the reply unrestored | Q6 | None | Weak: one blog and vendor pages, no measured success rate for the retry. Never more than one: a second invites invented copies |
| One opener per real token | Before sending, count the opener glyph in the outgoing text. It must equal the number of real tokens, or the run fails before sending | Q10 | None | Inference from the ICU and XLIFF rule of escaping at the boundary. The count assertion is the researchers' own |
| True and false sample lists per pattern, as a build gate | Each pattern exports true samples and false samples. One test asserts each true sample gives exactly one span and each false sample gives none. A reported false hit becomes a false sample before the rule changes | Q15, Q16 | [gitleaks](https://github.com/gitleaks/gitleaks) is MIT; copy the idea, not the code | Practice read in source. Its use here is a proposal |
| Dotted-number veto | Veto a dotted number that follows clause, section, schedule, paragraph, article or the section sign within 12 characters, or is followed by a closing bracket or a full stop and a digit. Accept an IP address only with valid octets, no leading zeros, and a cue word such as ip, host or server within 40 characters. Needed only if an IP finder is added | Q15 | Octet check is in the Python standard library | B1: 548 matches, all valid octets, 99 after a cue, so an octet check alone rejects none. The veto is a proposal |
| Card and phone vetoes with checksums | Card: strip hyphens and spaces; 13 to 19 digits; first digit 3, 4, 5 or 6; Luhn valid; a card word within 40 characters before, otherwise only a 4-4-4-4 grouping that starts with 4 or 5. Phone: veto slash dates, timestamps, page ranges and ISO dates; at most 3 bracket pairs and 4 punctuation characters in a row. Veto repeated or sequential digits | Q15 | Presidio is MIT, python-phonenumbers is Apache-2.0, python-stdnum is LGPL: restate the algorithm, do not copy the file | Source read. No published precision on contract text. Luhn alone passes about 1 in 10 random strings |
| Three stop sets, with a reason per word | Keep three frozen sets: seed stop (vetoes a cue-found name), form stop (vetoes one-word variants only), trim stop (trims leading or trailing tokens). A word may sit in one set only. Each word has a comment naming the false hit it stops and one test row. A test fails if a word has no row | Q16, Q17 | gitleaks is MIT; detect-secrets is Apache-2.0 | Practice read in source. gitleaks' own authors call their stop list crude |
| Doubt list codes | Five codes, computed after resolution, never changing masking. SHORT_NAME: an accepted PERSON seed or form whose last token has 1 or 2 letters. NEAR_DUPLICATE: two different PERSON or COMPANY forms of the same length, plus or minus 1, at edit distance 1. TWO_KINDS: one case-folded string covered as two kinds. SKIPPED_COMMON: a stop-listed or common-word one-word form skipped at a capitalised position. NO_CUE_RUN: an orphan capitalised run (last row) | Q17, Q1 | [Cour de cassation](https://github.com/Cour-de-cassation/moteurNER) repos are MIT; no code copied | The French doubt messages and check flag are published practice. The five codes are the researchers' own proposals. They need a core shape (owner decision 3) |
| Repeat-evidence promotion | Count n(T): exact capitalised occurrences of token T (3 or more letters, not in the hard stop list) inside accepted PERSON spans. If n(T) is at least 1, every capitalised occurrence of T that is not at a sentence start and not in a heading becomes a one-word PERSON form. A common-word name needs n(T) of at least 2. Sentence-start uses raise SKIPPED_COMMON | Q1, Q17 | None | The French "more than twice, annotate all" rule is in a README; its threshold and effect are unpublished. [Mikheev 2002](https://aclanthology.org/J02-3002.pdf) is newswire |
| Signature-block rule | A block is a run of at most 8 non-blank lines with at least two labels from By, Name, Print name, Title, Its, Date, Signature, Witness, Signed. Text after Name or Printed name is a seed if it fits `NAME_RUN`. A By value that fits `NAME_RUN`, or follows `/s/`, is a seed. A By line with a company suffix, "its", or a corporation phrase is an entity line and gives no person. A bare name line within 2 lines of Title or Date is the weakest part and is optional | Q1 | None | [Carvalho and Cohen 2004](https://www.cs.cmu.edu/~wcohen/postscript/email-2004.pdf) (peer-reviewed, email, not contracts) and one lawyer's blog on US practice. No recall figure on contracts |
| By and Name agreement | If a block has a By value and a Name value that fold to the same text, mark the seed confirmed (an internal label only). If they differ and both fit `NAME_RUN`, accept both and do not merge them | Q1, Q12 | None | Weak: inference from one blog's example |
| Generation-suffix guard | Entities whose full names differ only in Jr, Sr, II, III, IV or a trailing roman numeral are separate entities. Every form that omits the suffix is ambiguous between them | Q4, Q12 | None | The [VIAF](https://dlib.org/dlib/july14/hickey/07hickey.html) clustering rule is published. The application is a proposal |
| Initial-compatibility check | A form of an initial plus a surname joins entity E only if the surname equals E's last token and the initial equals the first letter of one of E's given tokens. Never form one from a middle initial alone. If two entities fit, the form is ambiguous | Q4 | nameparser is LGPL and is not a dependency; idea only | nameparser documentation and VIAF. A proposal |
| Nickname from text only | When the contract shows Given (Nick) Surname, or the nickname in quotes, and Given Surname matches a seed or a typed party, add Nick as a one-word form and Nick Surname as a two-word form for that entity, with the 3-letter minimum and the stop list. No nickname table. An optional list of at most about 30 owner-written pairs would add Short Surname only, never Short alone | Q4 | The Apache-2.0 nickname list carltonnorthern/nicknames states a coverage bias; bundling it needs an owner decision | Record-office indexing practice (a professional standard). A proposal |
| Closed jurisdiction list | Keep a place only after a governing-law cue and only if its case-folded text is an exact member of the list. Anything else stays masked or flagged. Never keep a city, street or postcode. Court-seat cities only from an owner list that defaults to empty | Q14 | None; the owner writes the list | [Swiss federal court rules](https://www.bger.ch/home/juridiction/jurisdiction-recht/anonymisierungsregeln.html) and the Canadian Judicial Council protocol (official). The owner decided a narrower list |
| Kept words never restored inside a longer masked span | The allow-list and the kept place apply only to characters not covered by a PERSON, COMPANY or ADDRESS span. Order: build spans, resolve overlaps, then subtract kept words | Q11, Q14 | None | A Swiss example ("Zurich" inside a company name) from a peer-reviewed paper. It touches the order of S4-M3-T2 and S4-M3-T3 |
| Date veto | A month or day token is not a name when the previous token is a digit, or the next token is a digit, a four-digit year, `of`, or a comma and a digit, even with an honorific. Masking a date of birth is a new kind and an owner decision | Q17 | None | Court practice varies: the Netherlands and France keep the birth year. The veto sentence is low risk and a proposal |
| Near-miss flag at Jaro-Winkler 0.92 | After masking, compare every remaining capitalised token of 5 or more letters with every masked surname or given name of 5 or more letters. If the first letters match and the score is 0.92 or more, add an unsure note. Flag only; never mask | Q4, Q12, Q17 | None (about 25 lines of code) | [Christen 2006](https://users.cecs.anu.edu.au/~christen/publications/mcd2006.pdf) and the Splink threshold are documented. The flag use is a proposal |
| Orphan capitalised run (owner option) | After the cue rules, mask every run of 2 or 3 capitalised name tokens not covered by a kept span, unless a token is a legal, lead, month, day or defined-term word. Raise NO_CUE_RUN if the run occurs once. Default on only in the first 1,500 characters | Q1 | None | Court and Swiss figures suggest a recall gain at a precision cost. No figure exists for this rule |

**Which are published practice and which are the researchers' own.** The tools and rule sets named in the last column are published and were read. The rules in the second column are the researchers' own proposals, built from them. No source publishes any of these rules as stated, and none gives a false-positive rate on contract text. The first and third rows rest on translation tooling and practitioner blogs, not on contract work.

**What real courts hide and keep.** Every public body read hides the names of natural persons, addresses and ID numbers, and keeps judges, lawyers and public bodies. They split on companies: Dutch, French and CJEU practice keeps them by default, Germany and Switzerland hide private ones, and the TAB benchmark masks an organisation that could identify someone. They split on places: Germany hides them, the Swiss federal court hides a party's residence and seat but keeps places needed to understand the decision, and the Zurich canton keeps most. Names become role labels where the role matters, and none of these bodies treats the result as truly anonymous. This app hides companies, which is the stricter side. **No court publishes a rule for common-word names** such as Will, May or Price, or for sentence-initial capitals. The Cour de cassation replaced its rule-based engine (error rate near 5%, a single unsourced figure in a README) with a trained model plus post-processing. What courts do publish is document-level consistency and a doubt message for a human reviewer.

## Open owner questions

Everything the owner answered on 21 and 22 Nov 2026 is removed from this list (see "Owner decisions"). Five items are still open. Each has a recommended answer. None is decided here.

1. **The seven owner tasks.** The owner writes the finders table (S4-M2-T8), the party details table (S4-M2-T9), the place list (S4-M2-T11), the pipeline table (S4-M3-T8), the entities table (S4-M3-T9) and the sample table (S4-M5-T5), and reads the golden files (S4-M5-T7, at the end of the stage). The agent does not write them (Constitution T11). One point for the place list: the planner's draft in S4-M2-T11 also holds Canadian and Australian territories, and the owner's decision names provinces and states only. Recommended: write the file to the five categories, and add a name only if a real contract needs it.
2. **The CUAD follow-up with typed parties (free).** Feed each contract's annotated main parties in as typed `Party` values and count what the front layer covers. Split the misses by cause in the same pass (all-capitals names, a missing suffix, trailing text, a state of incorporation, an address). Recommended: yes, outside the repo and with no text in the output, before any CUAD figure is called a risk or written into a document.
3. **More paid runs.** About $1.19 of the $2.00 key was left, and the key is deleted. A new run needs a new key and a written spend cap, and in-flight calls count against the cap, because B2 went 1.2 cents over its cap. Recommended: not now. If one run is wanted, repeat the copy-rate test with a larger token limit and reasoning off, and add the Sonnet spoof run with the copy instruction.
4. **Known limits of S4-M2-T12.** The new patterns do not find a lower-case NINO, the `XI`, `GD` and `HA` VAT forms, the `BR` and `OE` company prefixes, or a card number spaced 4-6-5. Recommended: leave them until a real contract shows the need, and add them as a new task, not as a change to S4-M2-T12.
5. **Acceptance of the plan, in words.** The plan stays Draft until the owner accepts it. Only the owner accepts.

Some recommendations of the entries above are in no plan task and no document. They are not questions for the owner now, and each belongs to a later stage:

- how a skipped ambiguous hit is shown (stage 12, with the doubt shape of S1-M6-T8);
- inside-marker folding in `restore_reply`, which would need a Spec 8.4 wording change (Q6);
- the Spec 4.2 sentence for a short form that fits two people (Q12);
- the multiset parity check and the single retry for AI replies (Q6; stage 6 and later);
- the free-text case rule (Q13; the stage 8 plan states which rule wins).

## Evidence quality and gaps

**Closed since the first revision:** the real token cost of the placeholder forms on a Claude model (B2), free tokenisation (A4, OpenAI and GPT-2 vocabularies), reproduction of the defects (A1, A2, A3) and a first measurement on real contracts (B1, party names only). Closed since the second revision: the owner's answers to all 26 plan questions, and a build-from-text check of M1, M2 and part of M3 by a cheap implementer.

**Confirmed absences** (searched again in the evidence check, across SciSpace, alphaXiv, Exa and Firecrawl; B1 and B2 narrow two of them):

- No study of a rule-only person-name finder on contracts, and no contract corpus with person-name annotations. CUAD annotates parties, partly. B1 gives the first measurement, for party names only, and as a floor. The nearest published numbers are newswire (Mikheev 1999: cue-only rules recall 40, precision 99), SEC filings (E-NER dictionary baseline F1 0.491, all entity types) and clinical text (Philter and PhysioNet deid); Philter's name recall fell to 87% on independent Australian data ([El-Hayek et al.](https://pubmed.ncbi.nlm.nih.gov/36870249/)).
- No study of name redaction effects on LLM contract review. "Better Call GPT" ([arXiv 2401.16212](https://arxiv.org/html/2401.16212v1)) pseudonymised before testing and has no unredacted comparison. General studies show task-dependent drops; a legal drop is plausible and unmeasured.
- No figures for placeholder copy or alteration on OpenAI or Google models, and none on a Claude model for contract review. B2 covers two Claude models on invented text.
- No vendor guidance on placeholder format from OpenAI, Anthropic or Google. Microsoft has a sample with a retain-exactly instruction.
- No false-positive rate per common-word name, no comparison of overlap rules for de-identification output, no benchmark of merge against split errors in contract review, no measure of placeholder consistency against reply length.
- No court publishes a rule for common-word names or sentence-initial capitals.

**New limits from the tests:**

- **A1 is an upper bound and B1 is a floor** (see "A ceiling and a floor"). Neither track fed typed party details, the defined-term allow-list, a real detector or the sample contract. The typed-party path, the name forms of S4-M2-T1 and the grouping of S4-M3-T7 are unmeasured.
- **A1 is one generator seed with regular templates and small groups.** The tester relabelled spans and added groups after seeing results (denominator 429 to 421). The place list and the layer 3 word list overlap the test words. The kind-order trap was never exercised.
- **A2's fixes are the tester's own code** and its place list is short. Defect 4 reproduced only with an injected span, and defect 6 only partly.
- **A3 discarded some generated inputs and the cause was not investigated.** P7, P8 and P11 were revised after a first run found mistakes in the properties themselves.
- **B1 has no ground truth for false positives.** Densities and list counts are proxies. The causes of the misses were not split. The dotted-number test cannot say what the 449 matches without a cue are.
- **B2 is small and partly empty.** Two Claude models (haiku and sonnet), invented text, a short writing or summary request and not a contract check. 188 of 480 haiku calls returned nothing because reasoning used the token limit. Sonnet got 112 of 216 planned copy-rate calls. Sample sizes are 12 to 15 replies per cell for sonnet and 3 to 6 per spoof cell. A result of 0 failures in n trials bounds the rate only at about 3 in n. The instruction effect is partly confounded by which haiku replies finished. The spoof styles for the ASCII forms were the tester's own choice. The run went 1.2 cents over its cap.
- **The plan simulations are partial** (see 'Later work'). M3 T7 to T10, M4, M5 and S4-M2-T12 beyond its mini-simulation were not simulated; the old properties were not re-run after T12; one of 11 mutants survived. The counts of 43 tasks and 442 tests are the plan checker's, and I did not re-derive them. The plan is a Draft that nobody has built.
- **No tokeniser count for Claude exists apart from B2's prompt-token counts,** and nothing for OpenAI or Google models beyond A4's vocabularies.

**Now verified against primary sources** (page or section as the notes give it): the 2610.34012 claims (App. C p20, App. D pp21-22, Sec. 4.3 p10, p9, Sec. 5 p10); the 2610.22800 refusals (App. B.1 p12) and shared surrogate (p14); the 2609.11335 MuSR figures (0.73, 0.70, 0.58, 0.52; Sec. 4.2 p9, Fig. 4 p11); DeidSharp's chunk sizes, whole-word location, span union and fail-closed run (pp3 to 5, abstract p1); CAMP (Sec. III.E, IV.B to IV.F); Staab et al. (Table 2 p7, Sec. 6); TAB Table 7 and Mikheev's figures; Presidio, scrubadub and LLM Guard behaviour read in source (see Q7, Q9, Q11, Q6); Wikidata CC0; the Census figure of 162,253 names.

**Still weak:**

- Single-author preprints: arXiv 2610.34012 (run by the engine's author), 2611.12709 (built with an AI coding assistant, protocol timing resting on its own git log) and 2604.16521. Authors at one vendor: 2611.07633.
- Synthetic data: 2610.34012, 2609.29682 (six documents, one Marathi model, no baseline table seen), 2604.16521 (four scenarios), 2611.07633 (100 resumes).
- Small local models: 2610.34012 (9B to 12B) and 2610.22800 (2B to 3B). The 2609.11335 result is one model, one run, three benchmarks.
- Other single sources: E-NER has one annotator; the clinical systems are not legal text; Staab et al. use Reddit; practitioner and vendor blogs (Medium, WSO2, MLflow, PEyeEye) and secondary write-ups (Belgavi.AI Lab, address-patent and Lucid Privacy summaries) carry no data of their own. The localisation numbers on tag survival are translation tasks, and the vendor benchmarks among them are unchecked. Three secret-scanner benchmarks were produced by the authors of competing tools. Presidio files were the `main` branch at fetch time, with no commit SHA recorded.
- Unverified: Philter precedence (model extraction of the file); Presidio issue 2433; Presidio's handling of touching spans; Welsh `Cyf`; OpenCorporates normalisation; libpostal; Google DLP span rules; the EDPB paragraph beyond the excerpt; `COMMON_WORD_NAMES` and `LEGAL_STOP` (general knowledge, not cited); the UK postcode letter exclusions; the Talon, GATE and Splink licences.

**What was not read:**

- Read only as abstracts or summaries: Garat and Wonsever, Thomas et al., Sivapiran et al., Lothritz et al., Raheja and Chernodub, Dozier et al.; Mikheev 2002 (introduction only in the first pass; the nearby-field note read its figures in text, not from the table cells); the PMC13727743 legal-consultation paper (search excerpt). Not read: Leitner et al., MAPA, LeNER-Br, Philter per-type numbers.
- Not opened: ContractScrub (2608.20204), RedactionBench (2606.18782), RAT-Bench (2602.12806), RedacBench (2603.20208). Open them first if the redaction-effect gap matters.
- arXiv 2407.11770 was not re-checked and stays in the weak-source group.
- Private AI documentation and the Google DLP pages were unreachable or second-hand. Not fetched or opened: Presidio issue 2433, the PR 1805 diff, the SSA and Census zips, the `wikidata-names` and Philter LICENSE files, the juritools function bodies.

**What was run.** The testers ran A1 to A3 in scratch folders outside the repo with reference copies of the plan code. B1 ran on 510 real contracts outside the repo, and only counts left that folder. B2 ran on Claude haiku and sonnet through OpenRouter with invented text; its key and raw replies stay outside the repo. I did not re-run any track. The numbers in this report are copied from the result files and checked against them. The `research_notes/` folder is git-ignored, so the numbers live in this report. The plan's first verification (21 Nov) ran the Spec 14.5 sample end to end with the reference code (7 entities, 10 spans, an exact restore). That run was not repeated after the later M3 changes and S4-M2-T12, so the plan's statement that the person rules find exactly three names must be re-confirmed after any edit, with expected values written by the owner (T11).

**Legal.** No lawyer was consulted. The GDPR, EDPB and ICO material is cited for the pseudonymised-not-anonymous wording only, under the ADR 0016 working position. Nothing here states how the EU AI Act applies.

## Next steps

In this order:

1. The owner fills the owner tables and the place list (S4-M2-T8, S4-M2-T9, S4-M2-T11, S4-M3-T8, S4-M3-T9, S4-M5-T5). S4-M5-T7, the reading of the golden files, comes at the end of the stage, after the golden files exist.
2. The owner accepts the plan in words. The plan stays Draft until then.
3. The agent sets the status to Accepted and fills "Accepted on", in a commit of its own.
4. Implementation starts with milestone 1, on `feat/privacy-m1-foundations`. Each milestone has its own branch (see the plan header).
5. Stage 1 task S1-M6-T8 (the doubt shape) goes on its own branch, `feat/core-doubt-shape`. It is separate, and stage 4 does not need it.
6. Outside the plan, the free CUAD follow-up runs before any CUAD figure is called a risk. A paid run starts only with a new key and an approved spend cap.
7. Before the stage closes, the owner confirms the values marked "owner to confirm" and reads the golden files (S4-M5-T7).
