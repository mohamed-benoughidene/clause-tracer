# Docs

This folder holds the project's written documents: specs, design and copy guides, brand material, research and decision records. Code and prototypes live elsewhere. The tables below list what is here now. Add a row when you add a file.

## Where to start

| If you want to… | Read |
| --- | --- |
| Understand what the app does and how it works | [`spec.md`](spec.md) |
| See how the parts fit together before building one | [`system-design.md`](system-design.md) |
| Know which tests to write, and what must pass before a release | [`testing-strategy.md`](testing-strategy.md) |
| Build a stage of the app | The stage's plan in [`plans/`](plans/), after [`system-design.md`](system-design.md) and [`testing-strategy.md`](testing-strategy.md) |
| Build or change a screen | [`design-system.md`](design-system.md), then the page in [`../prototype/`](../prototype/) |
| Write or check the words on a screen | [`ux-copy.md`](ux-copy.md) |
| Know why it looks the way it does | [`design-direction.md`](design-direction.md) and the [ADRs](adr/) |
| Use the logo or make brand material | [`clause-tracer-logo-guide.pdf`](clause-tracer-logo-guide.pdf) and [`../assets/`](../assets/) |

## Files

| File | What it is |
| --- | --- |
| [`spec.md`](spec.md) | **The source of truth.** What version 1 is: the glossary, user flow, features, labelling rules, AI pipeline, privacy, acceptance tests and open decisions. Section 14 is the handoff to the prototype: the screens, states, visual rules and sample data. |
| [`system-design.md`](system-design.md) | The design of the whole of version 1: processes, modules, data and storage, the engine protocol, failure handling, security, packaging, and every decision with its record. Accepted on 12 Nov 2026. |
| [`testing-strategy.md`](testing-strategy.md) | The test plan: the five test layers, what each module must prove, the paid test set and its budget, privacy and security tests, release gates and coverage targets. Accepted on 12 Nov 2026. |
| [`design-system.md`](design-system.md) | The visual system the prototype uses: tokens, icons, components, patterns and accessibility. Section 8 is an audit of where the prototype differs from the system, with fixed and open items. |
| [`ux-copy.md`](ux-copy.md) | The copy deck: the voice, the word list, and the words for every screen. Section 6 records the clashes found between the spec, the prototype and the copy, and how each one was settled. |
| [`design-direction.md`](design-direction.md) | The agreed actions that stop the app from looking generic: paper and ink, pencilled versus inked labels, two radii, and one shadow. |
| [`clause-tracer-brand-philosophy.md`](clause-tracer-brand-philosophy.md) | Why the app has this name, why a red thread and why a butterfly, and the rules for imagery. |
| [`clause-tracer-logo-guide.pdf`](clause-tracer-logo-guide.pdf) | The logo guide: the parts of the mark, colours, construction, minimum sizes and what not to do. |
| [`plans/`](plans/) | Task plans, one per build stage. Start with its README. |
| [`adr/`](adr/) | Architecture decision records. Each one is a single decision, with its reasons. |

## Decisions (ADRs)

| ADR | Decision |
| --- | --- |
| [0001](adr/0001-show-contracts-as-original-pdf-pages.md) | Show a contract as its original PDF pages, drawn as pictures, so nothing in the file can run. |
| [0002](adr/0002-label-look-split-stamp.md) | Labels are split stamps: a colour block with an icon, then the word. Only pencilled (AI judgment) stamps are dashed. |
| [0003](adr/0003-walk-away-takes-the-brand-red.md) | The brand red `#A91207` is used only for walk-away. |
| [0004](adr/0004-code-layout.md) | The code is one package with a pure core, six pipeline modules, adapters and a CLI. The import rules are checked automatically. |

ADRs 0005 to 0015 were all **accepted** by the project owner on 12 Nov 2026, and ADR 0016 on 13 Nov 2026.

| ADR | Decision or recommendation |
| --- | --- |
| [0005](adr/0005-engine-runner-shapes-and-ports.md) | Keep a hand-written step runner, frozen dataclasses in `core`, `Protocol` ports and a small HTTP retry loop. No framework. |
| [0006](adr/0006-encrypted-storage-and-secrets.md) | Store data in one encrypted SQLite file plus a key per review, so deleting a review destroys its key. |
| [0007](adr/0007-document-reading-stack.md) | Read PDFs with one engine (`pypdfium2`), Word files with a hardened XML parser, and parse untrusted files in a limited child process. |
| [0008](adr/0008-personal-data-detection-bundle.md) | Ship Presidio with a pinned config and the medium spaCy model, behind code-first finders. |
| [0009](adr/0009-desktop-shell-protocol-and-packaging.md) | Use pywebview as the shell, run the engine as a child process over stdio, and package with PyInstaller and Inno Setup. |
| [0010](adr/0010-starting-models.md) | Start with Claude Sonnet 5.5 and two comparison models. Keep Jev as an experiment. |
| [0011](adr/0011-who-writes-the-words.md) | Build the message and a label's panel words from code templates, pick not-covered clause types from a closed list, and use one fixed line for AI wording. |
| [0012](adr/0012-missing-unsure-and-evidence-failures.md) | Show a checkable "searched, nothing found" list, turn disagreeing searches into unsure, and keep the label when a quote can't be placed on the page. |
| [0013](adr/0013-test-layers-and-release-gates.md) | Test in five layers, four of them free, with the project's own release gates and a paid-run budget. |
| [0014](adr/0014-protection-and-release-integrity.md) | Use no obfuscation. Protect the project with signed and attested releases and honest wording. A trade mark is deferred. |
| [0015](adr/0015-provider-ready-seam.md) | Keep version 1 as specified, but keep the seams open for a later hosted option with accounts. |
| [0016](adr/0016-legal-positions-without-a-lawyer.md) | Cautious working positions on the pikepdf licence, enforcing the project's licence and the EU AI Act, because no lawyer is available. |

To record a new decision, copy [ADR 0005](adr/0005-engine-runner-shapes-and-ports.md) and give it the next number ([WRITING_DOCS.md](../WRITING_DOCS.md) section 6 has the format). ADRs 0001 to 0004 use an older, shorter format with front matter (`status`, `date`). If a later choice changes an ADR, add a dated **Amendment** section to it rather than rewriting it. ADR 0002 shows how.

## Keeping the docs in step

The spec, the design system, the copy deck and the prototype describe the same app, so they have to agree. The full guide, with what to update for each kind of change, is [WRITING_DOCS.md](../WRITING_DOCS.md) in the repo root.

- **When you change one, check the others.** If two disagree, fix all of them, and record the fix in `ux-copy.md` section 6.
- **Where each thing is decided:**
  - What the app does: `spec.md`.
  - How it looks: `prototype/styles.css`, as described in `design-system.md`.
  - What it says: `ux-copy.md`. `scripts/copy_lint.py` checks the prototype against it, and `scripts/check.sh` runs it.
- **The writing style:** British English, plain words and short sentences. The app never says "I". Say "source available", never "open source" (see [the licence](../LICENSE)).
