# ADR-0016: Take cautious working positions on three legal questions, because no lawyer is available

**Status:** Accepted (13 Nov 2026)
**Date:** 2026-11-12
**Deciders:** Project owner

## Context
Three legal questions were left "for a lawyer" by ADRs [0007](0007-document-reading-stack.md), [0011](0011-who-writes-the-words.md) and [0014](0014-protection-and-release-integrity.md):

1. What the MPL-2.0 licence asks when the app bundles `pikepdf`.
2. How the project's own licence (FSL-1.1-ALv2) could be enforced.
3. Whether the EU AI Act's Article 50 applies to the app, and what it would ask.

On 12 Nov 2026 the project owner said a lawyer is not an option. So the questions can't stay parked on one. This record takes a working position on each, from the official texts only.

**Nothing here is legal advice, and nobody qualified has checked it.** A working position is how the project behaves while the answer is unknown. The rule used for all three: where the answer is unclear, act as if the stricter reading is true whenever doing so is cheap, and write down the risk that is left.

What was read, all on 11 and 12 Nov 2026:

- The [MPL-2.0 text](https://www.mozilla.org/en-US/MPL/2.0/) and [Mozilla's FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/). Section 3.2 was re-read word for word on 12 Nov.
- The [FSL template](https://github.com/getsentry/fsl.software), [GitHub's DMCA policy](https://docs.github.com/en/site-policy/content-removal-policies/dmca-takedown-policy) and [17 U.S.C. 512](https://www.law.cornell.edu/uscode/text/17/512).
- [Article 50](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50) on the Commission's own AI Act site (the consolidated text of 27 Jul 2026), the [Commission's guidelines on Article 50](https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems), its [questions and answers](https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act) and the [Code of Practice on AI-generated content](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content).

One earlier doubt is closed. Two dates had been found for the guidelines. The Commission's page shows one document: published on 20 Jul 2026, with the page last updated on 5 Nov 2026, when the other language versions were added. There is one set of guidelines, not two.

## Decision
The project owner accepted this on 13 Nov 2026.

### 1. `pikepdf` and the MPL-2.0: do exactly what the licence text asks
The text is clear enough to follow without help. Section 3.2 asks for two things when the library is shipped in built form: the source must be available and people must be told how to get it, and the app's own licence must not limit their rights to that source. Section 3.3 lets the rest of the app use any licence.

- Ship `pikepdf` unchanged. A test compares the installed files with the hashes in the wheel's own `RECORD` file, so a changed file fails the build.
- The third-party licences page names `pikepdf`, its exact version, the full MPL-2.0 text, and a link to the source of that exact version. It also carries the licence files of the libraries inside the wheel (qpdf and others).
- Attach the source archive of that exact `pikepdf` version to each release, so the source stays available even if the upstream link breaks.
- The page says: "Clause Tracer's licence does not limit your rights to pikepdf's source code under the MPL-2.0."
- If a `pikepdf` file ever has to change, send the change upstream, or publish the changed file under the MPL-2.0.

The same care applies to PyGObject (LGPL) on Linux: ship it unchanged as separate files that a user could replace, with its licence text and a link to its source.

**Risk left:** low. This follows the licence's own words and Mozilla's FAQ.

### 2. The project's licence: treat it as a deterrent, and plan as if it can't be enforced
No court has ruled on the FSL, and no published case of FSL enforcement was found. A court case is out of reach for one person. So:

- Keep the cheap evidence: the exact `LICENSE` text, a copyright line with the owner's name and the year, a signed and dated tag for every release (each version's two-year clock starts on its date), and the contributor agreement in `CLA.md` for any outside code.
- The steps, in order: a polite message; then a GitHub DMCA notice. After that, stop.
- **Send a DMCA notice only for a plain copy:** the project's code republished without the licence or the copyright line. Never send one to argue that someone's product is a "competing use". The notice is sworn, it is published, and a wrong one can make the sender liable for the other side's costs (17 U.S.C. 512(f)). If the other side objects, the copy comes back unless a court case is filed within about two weeks.
- Don't build any plan on the licence stopping a determined copier. What protects the project is being the trusted source: signed releases, the name, and steady work ([ADR 0014](0014-protection-and-release-integrity.md)).

**Risk left:** real, and accepted. A competitor in another country could ignore the licence, and the project could do little about it.

### 3. EU AI Act, Article 50: act as if the project is a "provider", and do the cheap things now
The guidance does not say who the provider is when a user brings their own key. It does say that an app offered under its own name is a provider, free or paid, wherever its maker lives. So the cautious reading is that the project is one. Article 50 also has no exemption for open or source-available software.

What each part asks, and what the app does:

| Part | What it asks | Working position |
| --- | --- | --- |
| 50(1) and 50(5) | Tell people, clearly and at first contact, that they are dealing with an AI system | Already met in the design: the fixed AI line sits beside AI-written text, and setup says contract text goes to an AI model. Keep the line on every screen and report page that shows AI wording, readable by screen readers. A notice only in Help or the licence would not be enough |
| 50(2) | AI-written text carries a machine-readable mark, as far as this is technically feasible. Very short text is outside it, and so is light editing. "Rewriting text" and summaries are inside it | Three measures, below |
| 50(4) | Whoever *publishes* AI text on matters of public interest says so | Falls on the user, not the app. A message to the other side or a clause in a contract is private correspondence under the guidelines' own examples. No change |

The three measures for 50(2):

1. **Record who wrote every piece of text.** Each stored text has a field: written by code, by AI, or by the user. The design already tracks this for pencilled labels; this makes it a rule for every text.
2. **Mark exports that can carry a mark.** When a PDF report includes AI-written text, the app writes that into the file's metadata, using the standard IPTC "digital source type" terms. This costs a few lines of code.
3. **Keep AI text short and optional.** Reasons stay one or two sentences. The message is built by code by default, and "Rewrite with AI" stays an explicit choice ([ADR 0011](0011-who-writes-the-words.md)).

**Risk left:** plain text that the user copies out can't carry a hidden mark, and the app can't add one: the Code of Practice puts that kind of mark at the model, and allows relying on the model provider's mark without removing the app maker's own responsibility. A long AI rewrite copied out as plain text is therefore the one place where the app may fall short of 50(2) if the project is a provider. The owner accepts this for now. The only way to remove it is to drop the AI rewrites.

**The grace period does not help.** The delay to 2 Dec 2026 covers only systems on the market before 2 Aug 2026. Article 50 applies to this app from its first release.

**A free way to get an official answer.** The Commission runs the [AI Act Service Desk](https://ai-act-service-desk.ec.europa.eu/en), where anyone with a stake can [send a question](https://ai-act-service-desk.ec.europa.eu/en/form/helpdesk) and get an answer from experts who work with the EU's AI Office. Send it the provider question before the first public release. The page mentions no charge. An answer from it is not a ruling, but it is the closest thing to advice within reach.

**The rule in `AGENTS.md` stays:** nothing in the app or the docs may say that Article 50 doesn't apply.

### When to look again
- Before the first public release: re-read the guidelines page and the questions and answers, and check the Service Desk's reply.
- If the Commission publishes anything about apps that call a model with the user's own key.
- If the project ever takes money, runs a server ([ADR 0015](0015-provider-ready-seam.md)) or gains an EU business customer. Money for a lawyer should come first from there.

## Options Considered

### Option A: Cautious working positions (recommended)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low: one metadata field, one stored field, one licences page, one test |
| Cost | No money. A day or two of build work, spread across stages |
| Scalability | The positions hold until the project earns money or runs a server |
| Team familiarity | High: all of it is ordinary code and files |

**Pros:** every question has an answer the project can act on today. The stricter reading is followed wherever that is cheap. The risks left are written down.
**Cons:** not checked by anyone qualified. One known gap stays under 50(2).

### Option B: Leave the questions parked
| Dimension | Assessment |
|-----------|------------|
| Complexity | None |
| Cost | None now |
| Scalability | Poor: the questions return at release, with less time |
| Team familiarity | High |

**Pros:** no work.
**Cons:** "ask a lawyer" will never happen, so parked means never answered. The cheap measures would be missed.

### Option C: Remove what raises the questions
| Dimension | Assessment |
|-----------|------------|
| Complexity | Medium: drop `pikepdf` and both AI rewrites |
| Cost | Loses the hidden-layer check and two features users were promised |
| Scalability | Good: fewer duties |
| Team familiarity | High |

**Pros:** the smallest legal surface.
**Cons:** the app gets worse at its main job. The pencilled reasons are still AI-written, so Article 50 would not go away.

## Trade-off Analysis
Option A costs little and removes most of the doubt. The MPL position is close to certain, because the licence text is plain. The FSL position is a matter of accepting a limit, not of reading law. Article 50 is the only one with real doubt, and there the choice is between a small known gap (A) and losing features that the owner chose to keep on 12 Nov 2026 (C).

What this record cannot do: it cannot tell whether a regulator would agree. Fines under Article 50 can reach 15 million euros in law, with proportionality for small operators. For a free tool from one person, the realistic first step from a regulator is a request to fix something, but that is a judgement, not a fact.

## Consequences
- Easier: agents and the owner have one place that says how to behave on each question.
- Easier: the Linux and Windows builds know what the licences page must contain.
- Harder: every stored text needs a "written by" value, and the PDF export gains a metadata step with a test.
- Still true: none of this has been checked by a lawyer, and the docs must keep saying so.

## Action Items
1. [x] Owner: accept or change this record. Accepted, 13 Nov 2026.
2. [x] On acceptance: rewrite the "parked" entry in Spec section 10 as a working position, replace "check the wording with a lawyer" there, and update Spec 13, `system-design.md` and ADRs 0007, 0011 and 0014 with dated amendments. Done, 13 Nov 2026.
3. [x] Add to the spec: the "written by" field, and the metadata mark on PDF reports that contain AI wording (Spec 4.7 and 6.2). Done, 13 Nov 2026: the spec wording and the planned test rows ([testing strategy](../testing-strategy.md) section 1). **Still to do at build time:** write the two tests (Constitution T13).
4. [x] Add the build test that `pikepdf` is unchanged, and the third-party licences page with the sentences above. Done, 13 Nov 2026: the docs describe both (Spec 8.4, Spec 14.1 row 21, [ux-copy](../ux-copy.md) section 4.18, and the build test in [testing strategy](../testing-strategy.md) section 8). **Still to do at build time:** write the test, build the page, and attach the `pikepdf` source archive to each release.
5. [x] Owner: send the provider question to the AI Act Service Desk before the first public release. Sent on 13 Nov 2026; no reply yet, so the working position stands until one arrives. A draft is in section 9 of [the edit record](../../reports/Edits%20to%20source%20documents%202026-11-11.md).
