# Clause Tracer design direction

This file records how Clause Tracer should look, and why, so the app doesn't look generic or AI-made. The research behind it is in `Prototyping/clause-tracer/research/07-anti-generic-design.md`.

## Agreed actions (2026-11-06)

1. ~~Make the red thread a functional trace that links a clause to its explanation and links walk-aways down the margin (ADR 0003).~~ Dropped 2026-11-06: the lines read as unexplained connectors. Walk-aways keep the red; the thread stays in the logo (ADR 0003, amendment).
2. Replace the sparkle icon on "AI judgment" with a document mark and a plain word. **Decided: D · Pencil, not ink.** Labels from a clear rule match are inked (solid stamp, solid underline). Labels the app judged from the wording are pencilled (a dashed graphite stamp with a hatched colour block, and a grey dashed underline on the clause). The note says so in words ("Pencilled in: judged from the wording, not a number.").
3. Build around pages, margins and ruled lines, with at most two corner radii.
4. Give the stamps fixed meanings and print-ink tones, and make them the main signal.
5. Give the primary button its own ink colour, and keep red for one serious action.
6. Pick the paper tone for a reason, and use a cooler tone for the app chrome.
7. Use a distinct serif for headings, alongside a plain sans at chosen weights (settled: IBM Plex, principle 4).
8. Use one way of showing depth, and don't border every group.
9. Use real contract text everywhere, including empty states.
10. Run an audit before release: greyscale, logo swap, a checklist of tells, and contrast.

## Principles to work through together

| # | Principle | Decision |
| --- | --- | --- |
| 1 | Point of view first; the logo-swap test | **A · The careful friend** (2026-11-06): "Like a friend who reads contracts for a living, marking yours up in the margin." The contract fills the screen. The app speaks through margin notes, in plain words. (Changed 2026-11-07: the app no longer says "I". Its notes are neutral, such as "This one is a walk-away." See Spec 14.4.) Calm and personal, not a dashboard. |
| 2 | Every element needs a reason | A habit, not a look: applied as a removal pass when the prototype is rebuilt. |
| 3 | One signature move, one repeated layout pattern | The margin beside the page: the friend's notes and the reading log live there. |
| 4 | Type: two voices, big jumps | **C · IBM Plex Sans + IBM Plex Serif**: Plex Sans for the UI, Plex Serif for headings, the friend's notes (italic) and quotes from the contract. Typeset contract pages use Liberation Serif, so they read as the document, not the app. Drops Inter. |
| 5 | Colour: one dominant colour, a sparing accent, greyscale test, a physical reference | **A · Paper and oxblood**: cool grey chrome (#ECEEF0), warm paper (#FBF8F2) only on the contract sheet, ink text and primary button (#1F2328, radius 4). Red (#A91207) only for walk-away (and the logo's thread). |
| 6 | Shape: two radii, one way of showing depth | **B · The lifted page**: only the contract sheet casts a soft shadow; no borders on groups; radii 4 and 8. |
| 7 | Group by space, then tone, then border | **B · Tone shift**: groups sit on a slightly darker tone (#F3EFE8), with no border. |
| 8 | Real content, and designed empty, error and loading states | **B · The reading log** (2026-11-06), from the labor-illusion research: the friend keeps a log in the margin of what it is really doing, with real numbers and timestamps ("0:18 Late fees: your limit is 30 days. 5.4 says 60. Walk-away."). Lines are pencilled while running and inked when done; finished lines can be hidden. An unreadable file or page stops or skips at the line where it failed ("Page 7 is a scanned image, so it's skipped for now."), with the fix offered there (Word version or paste the text). No fake delay, no spinner. |
| 9 | Own icons, no tiles; density suits a professional tool | **C · Drawn ink icons, airy**: custom 1.6px stroke icons (1.6 settled 7 Nov 2026: crisper at 16px) with rounded ends, no tiles, 40px list rows. |
