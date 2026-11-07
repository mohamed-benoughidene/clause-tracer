---
status: accepted
date: 2026-11-06
---

# Walk-away takes the brand red

The walk-away label uses the brand's red (#A91207, with a light tint for washes and pins). Red now has a single meaning across the app: a line you won't cross.

This reverses the earlier rule that the red thread and the walk-away label must never share a colour. That rule led to plum for walk-away, which carried no meaning: nobody reads purple as "stop", so it had to be learned. Giving walk-away the brand red makes the logo say what the app does: it finds your red lines.

## Considered options

- **Plum (the earlier choice):** clearly separate from the brand, but meaningless, as above.
- **Vermilion:** an orange-red that reads as "stop", but it sits between the brand red and Unsure's amber, so the three blur, especially for colour-blind readers.
- **Ink strike:** black, like a proofreader's delete mark. It's strong and doesn't clash, but black is already used for primary buttons and text.

## Consequences

- No other UI may use red as decoration. The active nav marker, progress bars and the focus ring move off red (to ink or another accent), so red is never diluted.
- Walk-away is told apart from Unsure (amber) by its ✕ icon and its word, not by colour alone. Greyscale checks must still pass.
- The design tokens `walk/fg`, `walk/bg` and `walk/solid` change, and the prototype needs rebuilding to show this.
- The comparison is on the "Clause Tracer label sets" design canvas, Decisions page, Q5.

## Amendment (2026-11-06): no thread lines on the review screen

The prototype drew the red thread as lines on the review screen: one down the page margin between walk-away clauses, and one from the open clause to its note. On review, the lines read as unexplained connectors and confused the reader, so both are removed. Walk-aways are still marked by their red pins, stamps and highlights, and red still means only "a line you won't cross". The thread stays in the logo and the brand story, and as the labelled evidence trail inside a clause's note.
