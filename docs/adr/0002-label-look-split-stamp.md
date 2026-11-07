---
status: accepted
date: 2026-11-05
---

# Labels look like a split stamp

Each label chip is a reviewer's stamp. It has square corners (3px radius) and a 1.5px border in the label's colour. On the left is a solid colour block holding a white line icon: ✓ preferred, ≈ acceptable, ✕ walk-away, ? unsure. Next to it is the label word in small capitals. Not covered uses a dashed grey border and a dashed ring icon. Margin pins are square too: a light tint, a 1.5px border in the label colour, and a dark number. Clauses on the page keep the light wash in the label's colour and also get a thin underline in that colour. The colours stay as they were, with plum for walk-away.

We chose this because the labels must look unlike the AI judgment tag and the review status pills, which are both rounded. Square corners and small capitals set the labels apart at a glance. They also read as more formal and firm, which suits contract review. The research behind that effect is modest; telling labels apart from tags is the main reason.

## Considered options

- **Keep the current set:** a tinted box with a solid border and a different filled shape per label (circle, square, octagon, diamond, dashed ring). Rejected because the five shapes look busy. Also, the white numbers on the green and amber pins fall below AA contrast (about 4.2:1 and 3.7:1).
- **Soft pill:** a rounded tint with no border and line icons in the label's ink. This was the calmest option. Rejected because rounded labels look too much like the rounded tags and status pills.

## Consequences

- The pin numbers are now dark text on a tint, which passes AA. The white icon on each solid block is a non-text graphic, so it needs only 3:1, and it meets that on every colour.
- The prototype (the design-system chips, pins, washes and every screen that uses them) still shows the old look and needs rebuilding. The comparison is on the "Clause Tracer label sets" design canvas.

## Amendment (2026-11-07): only pencilled stamps are dashed

Not covered no longer has a dashed border. A dashed border now means only one thing: a pencilled label (the app judged it from the wording, Spec glossary "AI judgment"). Before, both looked dashed, so Not covered read as an AI judgment.

- **Not covered:** a solid grey border, and a dashed-ring icon (`i-ring-dashed`) in the block.
- **Acceptable:** the ≈ icon (`i-approx`). The prototype had used a minus for both Acceptable and Not covered, so without colour the two looked the same.
- **Pencilled:** a dashed graphite border (`--pencil`), a hatched block in the label colour, and a dashed graphite underline on the clause (`.clause.pencilled`).
