# Writing and updating the docs

This guide is for anyone changing Clause Tracer: people and AI agents. Follow it whenever you add a feature, a screen, a file or a folder, or change something the docs promise.

**The rule:** a change isn't finished until the docs say what the app now does. Out-of-date docs are worse than none, because people trust them.

## 1. Where each thing is decided

Every fact has one home. Other files may repeat it, but the home wins. If they disagree, decide which is right, fix the home first, then the copies. Record the disagreement and the fix in `docs/ux-copy.md` section 6.

| Kind of fact | Its home | Also appears in |
| --- | --- | --- |
| What the app does, and its rules | `docs/spec.md` | `README.md`, `prototype/` |
| Research findings | `reports/` | ADRs, Spec |
| Why we chose something | `docs/adr/` | Spec, design-direction |
| How it looks | `prototype/styles.css`, described in `docs/design-system.md` | Spec 14.4 |
| What it says on screen | `docs/ux-copy.md` | Every `prototype/*.html` page |
| The brand and logo | `docs/clause-tracer-logo-guide.pdf`, `docs/clause-tracer-brand-philosophy.md` | `assets/README.md`, design-system section 2 |
| Privacy and security promises | `docs/spec.md` section 8 | `README.md`, `SECURITY.md`, Help and Settings pages, ux-copy |
| The licence | `LICENSE` | `README.md`, `COMMERCIAL_LICENSE.md`, `CLA.md`, Help and Settings pages |
| How the code is built | `Constitution.md` | ADR 0004, `src/clause_tracer/README.md`, `AGENTS.md` |
| How the code is laid out | `docs/adr/0004-code-layout.md` | `src/clause_tracer/README.md`, the import rules in `pyproject.toml`, `AGENTS.md` |
| Terms for contributors and paying users | `CLA.md`, `COMMERCIAL_LICENSE.md` | `README.md` |
| How to keep the docs up to date | This file | `AGENTS.md`, `docs/README.md` |
| How commits and branches are named | `GIT_CONVENTIONS.md` | `AGENTS.md`, `README.md` |
| What a folder holds | That folder's `README.md` | `docs/README.md` |

## 2. What to update when…

Find your change in the left column. Update every file in the right column in the same commit or pull request. If a file doesn't need changing, say why in the commit or pull request message.

| When you… | Update |
| --- | --- |
| **Add or change a feature** | Spec: section 4 (the feature), 3 (user flow, if it changes), 11 (an acceptance test), 12 (remove it from "Not in version 1"). Then ux-copy for its words, and README if it's a headline feature. |
| **Add a screen or a state** | Spec 14.1 or 14.2, the prototype page, `prototype/states.html`, `prototype/README.md` (the Pages table) and ux-copy section 4. |
| **Add or rename a term** (a label, a status, a button name) | Spec section 2 (glossary), then the ux-copy word list (section 2). Search for the old word everywhere (see section 4 of this guide). |
| **Change a setting, or add one** | Spec 14.3, the Settings page, ux-copy (Settings in section 4), and README if users would look for it there. |
| **Change the AI steps or models** | Spec section 6. If what is sent to the AI changes, treat it as a privacy change too (the row below). |
| **Make a decision someone may later ask "why?" about** | Write an ADR (section 6). |
| **Change a token or a component** | `styles.css` first, then the matching part of `design-system.md`. If the change fixes an audit item, mark it ✅ in design-system section 8. |
| **Change what data the app stores, sends or keeps** | Spec section 8, the SECURITY.md scope, the README privacy lines and badges, and the Help and Settings copy. See section 3. |
| **Add a module, or change a module's input or output** | The module's `README.md` (its shapes, Constitution S3), the map in `src/clause_tracer/README.md`, and the import rules in `pyproject.toml` if it needs a new one. If module boundaries change, amend ADR 0004. |
| **Add a file** | The README of its folder. If it's in `docs/`, add a row to `docs/README.md`. |
| **Add a folder** | Give it a `README.md` (section 7), and link it from the root `README.md` if people outside the project need it. |
| **Delete or move a file** | Search for its name and fix every link. |
| **Change the logo or brand colours** | The files in `assets/` and their copies in `prototype/`, `assets/README.md`, design-system section 2, and the logo guide. |
| **Change the licence** | `LICENSE` (the official text only), `README.md`, `COMMERCIAL_LICENSE.md`, `CLA.md`, the Help and Settings pages, ux-copy, and Spec sections 10 and 13. |
| **Release a version** | Release notes, the README status note and badge, and "Supported versions" in `SECURITY.md`. |
| **Start a new version** (v2) | See section 8. |

## 3. Promises that live in many places

Some sentences are promises to users. They're repeated across the README, the spec, the security policy and the app itself. If one stops being true, every copy has to change in the same change.

This table was checked on 7 Nov 2026. When you add a promise or find a new copy, add it here. The search in section 4 is the real test: the table only tells you where to start.

| Promise today | Where it appears |
| --- | --- |
| No accounts, no sign-in, no server run by the project | README, Spec 1 and 12 |
| No telemetry | README (text and badge), Spec 8.1, Help, ux-copy |
| Runs on Linux and Windows. Mac comes later | README (text and badge), Spec 1 and 9 |
| English contracts only | README, Spec 1, 9 and 12, New review, ux-copy |
| Uses your own OpenRouter key | README, Spec, SECURITY.md, most prototype pages, ux-copy |
| Personal data is replaced on your computer, with Presidio | README, Spec 4.2 and 6, SECURITY.md |
| Everything saved is encrypted. Auto-delete after 7, 30 or 90 days | README, Spec 8.3 and 9, SECURITY.md (scope), Settings, Home, Output, ux-copy |
| Not legal advice | README, Spec 10, First launch, Output, Settings, Help, ux-copy |
| Source available, never "open source" | README, Spec 1, Help, ux-copy, `docs/README.md` |
| The app is in design, and nothing is released yet | README (status note and badge), `SECURITY.md` (supported versions) |

**Example: adding accounts.** Suppose a later version adds sign-in and cloud sync. Then, in the same change:

1. Write an ADR that explains why, and what data the server holds.
2. Rewrite Spec section 8: what leaves the computer, what's stored where, and how it's protected. Remove "Accounts, sign-in…" from section 12, and change "Nothing goes to a server run by the project" in section 1.
3. Add the server and sign-in to the SECURITY.md scope, under "What counts". Account takeover, broken access between users and server data leaks all become in scope.
4. Change the README: the opening paragraph ("There's no account…"), the "Not in version 1" row, and the keywords if needed. Remove the promise from the table above.
5. Update the Help and First launch copy in ux-copy, then in the prototype.
6. Search for every phrase from the table above (section 4) and fix what's left.

## 4. Find every copy before you change something

Search the whole repo, not just `docs/`:

```bash
grep -rniI --exclude-dir=.git "telemetry" .
```

Put in the old word or the promise, then check every hit. Search for the plural and other forms too ("account", "accounts", "sign in", "sign-in").

To check that no link points to a missing file, from the repo root:

```bash
find . -name '*.md' -not -path './.git/*' -not -path './.venv/*' -not -path './.cache/*' -not -name WRITING_DOCS.md | while read -r f; do d=$(dirname "$f"); grep -o '](\([^)#]*\))' "$f" | sed 's/](\(.*\))/\1/' | grep -v '^http' | while read -r l; do [ -e "$d/$l" ] || echo "$f: $l"; done; done
```

No output means every link works.

## 5. How to write

These rules apply to every doc. The app's own words follow `ux-copy.md` too.

- **British English.** "Colour", "licence" (the noun), "organise", "labelling". The licence's own name keeps its US spelling: the Functional Source **License**. So do file names that tools look for, such as `LICENSE`. Older text still has some US spellings (Spec section 5 is "Labeling rules"). Fix them when you're editing nearby.
- **Lead with the point.** The first sentence says what the file or section is for, or what the reader must do.
- **Short sentences.** Aim for 15 to 20 words. One idea per sentence.
- **Plain words.** "Use", not "utilise". "Start", not "commence". Explain a technical term the first time you use it.
- **Active voice, and talk to the reader.** "Run this command", not "This command should be run".
- **Tables and lists for anything you compare or follow in order.** Use prose for reasons.
- **Absolute dates.** "7 Nov 2026", never "last week" or "recently".
- **Names:** the product is **Clause Tracer**. The repository is `clause-tracer`. Say "source available", never "open source".
- **Be honest about status.** Say what's built, what's only designed, and what's planned. Never describe a planned feature as if it exists.
- **Link, don't copy.** If a fact has a home (section 1), link to it instead of writing it out again. Copy it only when the reader needs it right there, like the promises in section 3.
- **Mark guesses.** Write `[Assumption]` before a number or claim that hasn't been tested yet.

## 6. Decision records (ADRs)

Write an ADR for a decision that is hard to undo, or that someone will later ask "why did we do this?" about.

- **Name:** `docs/adr/NNNN-short-title.md`, with the next number.
- **Front matter:** `status` (proposed, accepted or superseded) and `date`.
- **First paragraph:** the decision, in plain words.
- **Then:** `## Considered options` and `## Consequences`, as in the existing ADRs.

```markdown
---
status: proposed
date: YYYY-MM-DD
---

# The decision, as a short statement

One or two paragraphs: what we decided, and why.

## Considered options

- The option we chose, and why.
- Each option we didn't choose, and why not.

## Consequences

What changes because of this, good and bad.
```

**Never rewrite an accepted ADR.** If a later decision changes it, add a section to the end called `## Amendment (YYYY-MM-DD): what changed`, as ADRs 0002 and 0003 do. If a new ADR replaces it completely, set the old one's status to `superseded by NNNN`. Then add or update its row in `docs/README.md`.

## 7. A README for every folder

Each folder people work in (`assets/`, `docs/`, `prototype/`, `tests/` and every module in `src/clause_tracer/`) has a `README.md` that says:

1. **What the folder is for**, in one or two sentences. Describe the purpose, not today's contents, so it stays true as the folder grows.
2. **How to use it**, if there's anything to run or choose (for example, "Which file do I need?").
3. **What's in it**: a table with one row per file or group of files.
4. **Rules**, if there are any, for adding to it.

When you add a file, add its row in the same commit.

## 8. New versions

The spec describes the version being built now.

- **While version 1 is being built**, change `docs/spec.md` directly. Git keeps the history.
- **When version 1 ships**, tag the release (for example `v1.0.0`). That tag is the record of what version 1 was.
- **When work on version 2 starts:**
  - Update `spec.md` to describe version 2, and change its title and section 1.
  - Rename section 12 to "Not in version 2". As each feature in it is planned, move it into the body.
  - If people still need the version 1 spec while version 2 is being designed, copy it to `docs/archive/Spec-v1.md`, mark it **frozen** at the top, and don't edit it again.
  - Record big changes of direction as ADRs, not only in the spec.
- **Research** goes in `reports/`, one report per topic, with a date and a short summary at the top. A spec or ADR that relies on a report links to it.

## 9. Before you commit or open a pull request

- [ ] Every file in the "What to update" row for this change is updated (section 2).
- [ ] If a promise changed, every copy of it is updated (section 3).
- [ ] The search for old words finds nothing that's left over (section 4).
- [ ] Every link works (section 4).
- [ ] New files are listed in their folder's README.
- [ ] The text follows the writing rules in section 5.
- [ ] A decision worth explaining has an ADR.
