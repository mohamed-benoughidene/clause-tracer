# Clause Tracer — Brand Philosophy

**Purpose:** This document explains the thinking behind Clause Tracer's name and visual identity. It records what "Tracer" means in the context of contract review, why the red thread represents the review process, and why the mark is a butterfly. Use it as a reference when creating, evaluating, or evolving Clause Tracer's visual identity and brand communication.

## 1. The Name: Clause Tracer

**Clause** identifies what is being examined: a provision within a legal agreement. **Tracer** represents the act of following a path through the text and returning to it deliberately during review.

Together, Clause Tracer describes a methodical approach to contract review: follow the language, examine it step by step, and retrace the path as needed to understand what it says and where the review leads.

## 2. The Visual Identity: The Red Thread

Following the thread means tracing one continuous path through a complicated subject until you understand where it leads.

For Clause Tracer, the red thread represents the reviewer's path through a contract: a visible line to follow while examining the text carefully and returning to important points as the review develops.

The thread embodies the act of review itself: the deliberate process of tracing a path through contract language rather than reading it only once and moving on.

## 3. The Mark: A Butterfly That Makes You Look Twice

Many butterflies carry eyespots on their wings. The spots have a job: they make a predator look twice, and they draw an attack away from the parts that matter.

That is Clause Tracer's job. It makes you look twice at a contract, and it points your attention to the clause that matters, with the exact words to back it up.

The butterfly carries the rest of the story too:
- **Two wings, two sides.** A contract joins two parties, the way a butterfly's wings meet at its body. A butterfly flies only when both wings carry their share. So does a fair deal.
- **Four eyespots, the clauses.** Each spot is a place to look closely.
- **One red eyespot, the one that matters.** Red is reserved for "a line you won't cross" (ADR 0003), so only one spot is red.
- **One unbroken line.** The whole butterfly is drawn without lifting the pen. This is the red thread: the reader's path through the contract. It goes around each clause, never through it, and comes back. Nothing is skipped.

**A secondary idea, for copy only:** the butterfly effect. A small clause can change everything that follows ("Small words, big effects"). Use it in marketing or Help, not as the core meaning: it's well worn.

**What the butterfly does not mean:** metamorphosis, freedom or fragility. They're clichés, and they don't describe what the app does. Don't build copy on them.

## 4. The Logo: The Butterfly Beside the Name

The logo is one drawn butterfly followed by the name "Clause Tracer". The butterfly leads, like the mark a careful reader makes in the margin beside the line that matters.

Each part carries the philosophy:

- **The name.** It's set in IBM Plex Serif SemiBold, the same face as the app's headings. A serif from the world of printed agreements: formal, serious and easy to read.
- **The mark in the margin.** The butterfly sits before the name, taller than the capitals, the way a reader's mark sits in the margin of a contract, beside the clause it points to.
- **Two wings, one line.** Two wings for the two sides of an agreement, drawn as one unbroken line that never touches the eyespots. This is the red thread.
- **Four eyespots.** The clauses. The line goes around each one and never through it.
- **The red eyespot.** The clause that matters, and the only red spot.
- **The broad nib.** The mark is drawn, not built from shapes. A flat nib held at 30° makes the line thick and thin as it turns, lighter where the pen lands and lifts. It's a careful person reading, not a machine stamping.

**Colours:**
- Oxblood (#A91207) is used for the line and the eyespot that matters, on both light and dark backgrounds.
- Ink (#1F2328) is used for the name and the other eyespots.
- On dark (#1E1D1A), the name and the eyespots turn light (#ECE8E1), and the butterfly's line stays oxblood.

**Construction:**
- The butterfly is 1.6 × the height of the name's capitals, centred halfway up them.
- The gap between the butterfly and the C is 0.45 × the cap height, measured from the ink.
- Clear space is one cap height on every side.
- Minimum sizes: the logo at 120 px (30 mm) wide; the butterfly alone at 16 px (5 mm).

The butterfly alone is the app icon and favicon.

### Where the line comes from

The mark is drawn on one rule: a single unbroken line that goes around every point and never touches it. That rule is shared by two living traditions:
- **sona,** the sand drawings of the Chokwe people of eastern Angola (UNESCO Intangible Cultural Heritage), drawn while a story is told;
- **sikku kolam,** the interlaced threshold drawings of Tamil Nadu.

We credit both for the rule wherever the logo's construction is described. The butterfly itself is our own figure, not a copy of any recorded sona or kolam.

## 5. Imagery: One Among Many

The First launch picture is a page from an imagined natural-history book: many butterflies etched in black and white, and one in colour, red, with four eyespots. Many clauses, and the one that matters.

The rules for imagery follow from the mark:
- **Only one thing is red.** Everything else stays in ink, paper and quiet colour, so the red one stands out the way a walk-away clause should.
- **Hand-made, not generated-looking.** Etching, watercolour, gouache, paper grain, small imperfections. No glow, no gloss, no lens effects.
- **No text in pictures.** Words belong in the interface, where they can be read and translated.
- **The mark itself appears once,** where it means something. Other butterflies in a picture are ordinary ones; the logo is never repeated as a pattern.

## 6. Files

The master files are in `assets/` (the build scripts stay in `Prototyping/logo/final/`). They were drawn in vectorcraft and simplified there, with corners kept. The name is IBM Plex Serif converted to outlines. The HTML prototype uses the same artwork through `prototype/logo.svg` (and `logo-dark.svg`), and the First launch picture is `prototype/hero-butterflies.webp`.
- `clause-tracer-logo.svg` (light backgrounds), `-reversed.svg` (dark backgrounds, transparent), `-on-dark.svg` and `-mono.svg`.
- `clause-tracer-symbol.svg`: the butterfly alone, plus the same three variants.
- `clause-tracer-logo-guide.pdf`: the logo, what each part means, colours, construction and use, and why a butterfly. It's built by `build_guide.py` in the same folder.
