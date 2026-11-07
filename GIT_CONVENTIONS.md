# Git conventions

This file says how to write commit messages and name branches in Clause Tracer. People and AI agents follow it alike. Agents write most of the code, so the rules are strict and short.

## 1. Commit messages

Use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/). It is a format that makes each message readable by people and by tools. A commit message has this shape:

```text
type(scope): subject

Body: what changed and why.

Footer: Refs: #12
```

### Types

| Type | Use it when you… | Example |
| --- | --- | --- |
| `feat` | add behaviour the user can see | `feat(checking): add the quote check` |
| `fix` | correct a bug | `fix(ingest): keep numbering in .docx lists` |
| `docs` | change only documentation | `docs(repo): add the git conventions guide` |
| `test` | add or change tests only | `test(privacy): cover overlapping placeholders` |
| `refactor` | restructure code without changing behaviour | `refactor(links): split the term finder` |
| `perf` | make something faster or lighter | `perf(ingest): read large PDFs in pages` |
| `build` | change packaging or dependencies | `build(deps): add python-docx` |
| `ci` | change the CI workflow or `scripts/check.sh` | `ci(repo): run lint-imports on every push` |
| `chore` | do upkeep that fits nowhere else | `chore(repo): ignore the uv cache folder` |
| `style` | change formatting only, with no logic change | `style(cli): apply the formatter` |
| `revert` | undo an earlier commit | `revert: feat(writing): add clause rewrite` |

### Scopes

A scope names the part of the repo you changed. Put it in brackets after the type. Use one of these.

| Kind | Scopes |
| --- | --- |
| Code modules ([ADR 0004](docs/adr/0004-code-layout.md)) | `core`, `ingest`, `privacy`, `links`, `checking`, `writing`, `outputs`, `adapters`, `cli` |
| Everything else | `prototype`, `docs`, `assets`, `deps`, `license`, `security`, `repo` |

Leave the scope out only when a change spans many parts, and then say so in the body. Never invent a new scope without asking the user.

### The subject

The subject is the first line.

- **Imperative mood.** Write it as a command: "add", not "added" or "adds". It should finish the sentence "If applied, this commit will…".
- **Lowercase** after the colon, except for names such as `Presidio` or `OpenRouter`.
- **No full stop** at the end.
- **About 50 characters.** The hard limit is 72.

### The body

Add a body when the subject does not explain the change. Leave one blank line after the subject.

- Wrap lines at 72 characters.
- Explain what changed and why. Do not explain how: the diff shows that.
- Cite a [Constitution](Constitution.md) rule ID with its plain name when one shaped the change. Example: "D8 (save the AI's exact reply)".

### Footers

A footer is a `Token: value` line after the body, with one blank line before it.

| Footer | Use it for |
| --- | --- |
| `BREAKING CHANGE: <what breaks>` | A change that breaks a module's input or output shape, or a public command. Add `!` after the scope as well: `feat(core)!:`. Say what callers must change. Saved data never breaks: a change to its shape ships a migration, as D5 (add fields rather than rename) and D6 (migrations and a schema version) require. |
| `Refs: #12` | The issue or pull request the commit relates to. |
| `Co-Authored-By: Name <email>` | Credit for a co-author. Agents add their own attribution line. |

### One change per commit

- **One logical change per commit.** If the subject needs "and", split it.
- **Update the docs in the same commit** when the change affects what the app does, says or promises. [WRITING_DOCS.md](WRITING_DOCS.md) section 2 says which files.
- **Commit `uv.lock` with any dependency change.**
- **Run `scripts/check.sh` first.** It must pass with no errors.
- **Never commit real contracts, real personal data or real keys.** Use the sample contract and invented placeholders ([AGENTS.md](AGENTS.md)).

## 2. Branch names

Use `type/short-kebab-description`. "Kebab" means lowercase words joined by hyphens.

- Use the same types as commits.
- Add a scope as the first word of the description when it helps: `feat/checking-quote-check`.
- Add an issue number after the slash if there is one: `fix/42-docx-numbering`.
- Use lowercase, ASCII letters, digits and hyphens only. No spaces, underscores or accents.
- Keep it under about 50 characters.

`main` is the default branch. Once others contribute, never commit to it directly: open a pull request.

Agents name branches by the same rule. Claude Code worktree branches may carry a tool prefix, such as `claude/`. Keep the `type/description` part after the prefix, and do not rename the tool's prefix.

## 3. Pull requests

A pull request (PR) asks the owner to merge your branch into `main`.

- **Title:** follow the subject rules in section 1, with the type and scope.
- **Squash-merge.** This joins all commits of a PR into one. `main` then reads as one Conventional Commit per PR. The PR title becomes that commit's subject.
- **Description:** say what changed and why. Link the issue.
- **Outside contributors:** add this line, from [CLA.md](CLA.md) section 6: "I have read the CLA in CLA.md and I agree to it."

## 4. Good and bad

| Bad | Good | Why |
| --- | --- | --- |
| `Fixed stuff` | `fix(ingest): keep numbering in .docx lists` | Says what and where. |
| `feat: Added the quote check.` | `feat(checking): add the quote check` | Imperative, lowercase, no full stop. |
| `update(checking): quote check` | `feat(checking): add the quote check` | `update` is not a type. |
| `feat(checking): add the quote check and fix docx numbering` | Two commits: one `feat`, one `fix` | One change per commit. |
| `feat(Checking): add the quote check` | `feat(checking): add the quote check` | Scopes are lowercase. |
| Branch `Feature/Quote Check` | Branch `feat/checking-quote-check` | Lowercase, hyphens, a known type. |
| Branch `fix_docx_numbering` | Branch `fix/42-docx-numbering` | Uses `type/`, hyphens, an issue number. |

A full commit with a body and footers:

```text
feat(checking)!: return quotes as sentence ids plus a short quote

The AI now points at numbered sentences and quotes only the exact
words, so code can check each quote inside those sentences. This
removes the open search for the quote in the offset chain. Raw replies
are still saved, as D8 (save the AI's exact reply) requires.

BREAKING CHANGE: checking.extract() now takes the sentence map from
ingest. The cli passes it in; other callers must do the same.
Refs: #12
Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
```

## 5. Checklist

- [ ] `scripts/check.sh` passes.
- [ ] The commit makes one logical change.
- [ ] The type and scope come from the lists above.
- [ ] The subject is imperative, lowercase and without a full stop, and it is 72 characters or fewer.
- [ ] The body wraps at 72 and says what and why.
- [ ] Any Constitution rule that shaped the change is cited with its ID and name.
- [ ] The docs and `uv.lock` are updated where needed.
- [ ] No real contracts, personal data or keys are included.
- [ ] The branch is named `type/short-kebab-description`.
- [ ] The PR title follows the subject rules, and outside contributors add the CLA line.
