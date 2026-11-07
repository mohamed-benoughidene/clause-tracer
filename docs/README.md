# Docs

This folder holds the project's written documents: specs, design and copy guides, brand material, research and decision records. Code and prototypes live elsewhere. The tables below list what is here now. Add a row when you add a file.

## Where to start

| If you want to… | Read |
| --- | --- |
| Understand what the app does and how it works | [`spec.md`](spec.md) |
| Build or change a screen | [`design-system.md`](design-system.md), then the page in [`../prototype/`](../prototype/) |
| Write or check the words on a screen | [`ux-copy.md`](ux-copy.md) |
| Know why it looks the way it does | [`design-direction.md`](design-direction.md) and the [ADRs](adr/) |
| Use the logo or make brand material | [`clause-tracer-logo-guide.pdf`](clause-tracer-logo-guide.pdf) and [`../assets/`](../assets/) |

## Files

| File | What it is |
| --- | --- |
| [`spec.md`](spec.md) | **The source of truth.** What version 1 is: the glossary, user flow, features, labelling rules, AI pipeline, privacy, acceptance tests and open decisions. Section 14 is the handoff to the prototype: the screens, states, visual rules and sample data. |
| [`design-system.md`](design-system.md) | The visual system the prototype uses: tokens, icons, components, patterns and accessibility. Section 8 is an audit of where the prototype differs from the system, with fixed and open items. |
| [`ux-copy.md`](ux-copy.md) | The copy deck: the voice, the word list, and the words for every screen. Section 6 records the clashes found between the spec, the prototype and the copy, and how each one was settled. |
| [`design-direction.md`](design-direction.md) | The agreed actions that stop the app from looking generic: paper and ink, pencilled versus inked labels, two radii, and one shadow. |
| [`clause-tracer-brand-philosophy.md`](clause-tracer-brand-philosophy.md) | Why the app has this name, why a red thread and why a butterfly, and the rules for imagery. |
| [`clause-tracer-logo-guide.pdf`](clause-tracer-logo-guide.pdf) | The logo guide: the parts of the mark, colours, construction, minimum sizes and what not to do. |
| [`adr/`](adr/) | Architecture decision records. Each one is a single decision, with its reasons. |

## Decisions (ADRs)

| ADR | Decision |
| --- | --- |
| [0001](adr/0001-show-contracts-as-original-pdf-pages.md) | Show a contract as its original PDF pages, drawn as pictures, so nothing in the file can run. |
| [0002](adr/0002-label-look-split-stamp.md) | Labels are split stamps: a colour block with an icon, then the word. Only pencilled (AI judgment) stamps are dashed. |
| [0003](adr/0003-walk-away-takes-the-brand-red.md) | The brand red `#A91207` is used only for walk-away. |
| [0004](adr/0004-code-layout.md) | The code is one package with a pure core, six pipeline modules, adapters and a CLI. The import rules are checked automatically. |

To record a new decision, copy an existing ADR and give it the next number. Keep the front matter (`status`, `date`), and describe the decision in the first paragraph. If a later choice changes an ADR, add a dated **Amendment** section to it rather than rewriting it. ADR 0002 shows how.

## Keeping the docs in step

The spec, the design system, the copy deck and the prototype describe the same app, so they have to agree. The full guide, with what to update for each kind of change, is [WRITING_DOCS.md](../WRITING_DOCS.md) in the repo root.

- **When you change one, check the others.** If two disagree, fix all of them, and record the fix in `ux-copy.md` section 6.
- **Where each thing is decided:**
  - What the app does: `spec.md`.
  - How it looks: `prototype/styles.css`, as described in `design-system.md`.
  - What it says: `ux-copy.md`.
- **The writing style:** British English, plain words and short sentences. The app never says "I". Say "source available", never "open source" (see [the licence](../LICENSE)).
