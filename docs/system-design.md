# System design: Clause Tracer version 1

11 Nov 2026 · status: **accepted** on 12 Nov 2026

This is the design of the whole of version 1: the Python engine, the desktop shell around it, storage, packaging and release. It says how the parts fit, what each one promises, and which choices are still open. Nothing here is built yet. The code is an empty skeleton.

**How to read it.** [`spec.md`](spec.md) says what the app does, and wins if this file disagrees with it. Each choice below that is hard to undo has a decision record (ADR) with its runner-up. The project owner accepted them all on 12 Nov 2026 (section 13). The evidence is in [the v1 design decisions report](../reports/Clause%20Tracer%20v1%20design%20decisions.md). How to test all of it is in [`testing-strategy.md`](testing-strategy.md). The rules the code must follow are in the [Constitution](../Constitution.md), cited here by ID.

## 1. Requirements

### 1.1 What it does

Clause Tracer checks one contract against the user's own playbook and shows the evidence for every label. The full behaviour is Spec sections 3 to 7. The design rests on four promises from the Spec:

1. **Code decides wherever it can.** Code picks number and yes/no labels, checks every quote and number, and chooses what runs next (Spec 5, 6.1, 8.4).
2. **Only placeholder text leaves the computer**, and only to the AI provider the user chose (Spec 8.1).
3. **Everything saved is encrypted**, and reviews delete themselves on a schedule (Spec 8.3, 9).
4. **No telemetry, no accounts, no server run by the project** in version 1 (Spec 1, 8.1, 12).

### 1.2 Qualities it must have

| Quality | Target for version 1 | Source |
| --- | --- | --- |
| Privacy | No confirmed personal item, note or name in any outgoing request or log. Proven by test on every change | Spec 11 |
| Correct labels | Every planted walk-away found. At least 90% of numbers and labels correct on the test set | Spec 11 |
| Evidence | No quote reaches the screen unless code found it word for word in the contract | Spec 11 |
| Cost per review | `[Assumption]` about $0.28 for a 10,000-word contract and $0.82 for 50,000 words on a Sonnet-class model; a few cents on a cheap model | [ADR 0010](adr/0010-starting-models.md) |
| Input size | `[Assumption]` files up to 20 MB and 50,000 words (about 65,000 tokens, about 2,500 sentences) | Spec 9 |
| Offline | Saved reviews open offline. A draft can be prepared offline. Only AI steps need the internet | Spec 9 |
| Systems | Linux and Windows 10/11. Mac later | Spec 9 |
| Download | As small as the personal-data model allows. `[Assumption]` roughly 150 to 250 MB installed with the medium model; not yet measured | [ADR 0008](adr/0008-personal-data-detection-bundle.md) |
| Resume | An interrupted review continues from the first unfinished step. Finished AI calls are never paid for twice | Spec 6.3 |
| Upkeep | One person can review every line that ships. That means Python, plus the HTML, CSS and JavaScript of the existing prototype | Constraint below |

There is no load or scaling target. The app serves one user on one computer, and runs one review at a time.

### 1.3 Constraints

- **One developer, who reviews Python.** AI agents write most code. Any Rust or TypeScript would ship unreviewed, so the design avoids both.
- **No Windows machine.** The developer works on Debian. Windows builds must be built and tested by CI.
- **Licence rule.** The project is source available under FSL-1.1-ALv2. Runtime dependencies must be MIT, BSD or Apache. No GPL or AGPL. One named exception: `pikepdf` (MPL-2.0), allowed on 12 Nov 2026 for reading hidden PDF layers ([ADR 0007](adr/0007-document-reading-stack.md)).
- **Tie-break.** When two good options conflict, the better experience for non-technical freelancers wins: a small download, a quick start and a smooth install.
- **Later, not now.** A future version may let the project itself become the AI provider, with optional accounts. Version 1 must not block that (section 11).

## 2. The system in one picture

```text
 ┌──────────────────────────── the user's computer ────────────────────────────┐
 │                                                                              │
 │  ┌─────────────── shell process (Python, pywebview) ───────────────┐         │
 │  │  system webview  ◄── js_api facade ──►  engine client           │         │
 │  │  (prototype HTML,     (narrow, typed)    (spawns and talks      │         │
 │  │   CSS, JS)                                to the engine)        │         │
 │  └─────────────────────────────────────────────┬──────────────────┘         │
 │                        newline-delimited JSON over stdin/stdout             │
 │  ┌──────────────────────────────────────────────▼─────────────────┐         │
 │  │ engine process: the same executable, `clause-tracer serve --stdio`       │
 │  │                                                                 │         │
 │  │   cli ── runner ──► ingest ► privacy ► links ► checking ► writing ► outputs
 │  │    │                    (pipeline modules import only core)     │         │
 │  │    └─ wires adapters:  storage · keyring · presidio · openrouter│         │
 │  └───────┬──────────────┬────────────────────────────┬─────────────┘         │
 │          ▼              ▼                            │                       │
 │   encrypted store   OS password store                │                       │
 │   (data folder)     (master key, API key)            │                       │
 └──────────────────────────────────────────────────────┼───────────────────────┘
                                                        ▼  HTTPS, placeholder text only
                                        OpenRouter ──► AI provider (zero retention asked)

   GitHub Releases: opened only when the user presses "Check for updates".
```

Two processes, one executable. The shell draws the interface. The engine does all the work and is the same program the command-line tool runs. Both are Python.

## 3. Components

### 3.1 The engine

The engine keeps the layout in [ADR 0004](adr/0004-code-layout.md): a pure `core`, six pipeline modules, adapters at the edge, and `cli` as the only place that wires them together. `lint-imports` enforces the import rules.

| Part | Job | Hides this decision (B4) |
| --- | --- | --- |
| `core` | Shapes, ports, labelling rules, output scans, error types. No files, network, clock or third-party imports (T1) | What a label is and how it is picked |
| `ingest` | Read the file, build the canonical text, find hidden text, split clauses and sentences | Which PDF and Word libraries read a file |
| `privacy` | Suggest personal data, number placeholders, keep the exact map between the two texts | How names become placeholders and back |
| `links` | Cross-references, defined terms, overrides, references to other documents | The patterns that find a link |
| `checking` | Match, extract, quote check, judge, explain, summarise | Prompts, reply forms and their checks |
| `writing` | Rewrite a clause as small edits that code applies | The rewrite form and its rules |
| `outputs` | The message and the report | Templates and the PDF library |
| `adapters` | OpenRouter, Presidio, storage, the password store | Each outside tool |
| `cli` | Commands, the step runner, wiring, the stdio server | The order of steps and how resume works |

**Ports.** `core` defines five small `typing.Protocol` ports, and `cli` passes the real adapters in (P4, T2). [ADR 0005](adr/0005-engine-runner-shapes-and-ports.md) records why each is a port.

| Port | Real adapter | Fake used in tests |
| --- | --- | --- |
| `AiClient` | `adapters/openrouter` | Replay fake keyed by request hash |
| `PiiDetector` | `adapters/presidio` | Fake that returns planted suggestions |
| `ReviewStore` | `adapters/storage` | In-memory store |
| `SecretStore` | `adapters/keyring` | In-memory store |
| `Clock` | Standard library, in `cli` | Fixed clock |

PDF and Word parsers, the report renderer and JSON handling are **not** ports. Each is an internal choice of one module (the P4 trap: a port for something that will not change).

### 3.2 The shell

The recommended shell is **pywebview** ([ADR 0009](adr/0009-desktop-shell-protocol-and-packaging.md)). It shows the pages of [`../prototype/`](../prototype/) in the system webview (WebView2 on Windows, WebKitGTK on Linux), and every line of shell code is Python. It will live in its own top-level folder, as ADR 0004 says.

- **The interface never talks to the engine directly.** JavaScript calls a narrow Python facade through `window.pywebview.api`. The facade checks its inputs and forwards typed requests to the engine.
- **Untrusted content stays inert.** PDF pages are pictures. Contract, playbook and AI text is set with `textContent`, never as HTML. A strict content security policy forbids remote content. Links open in the system browser after the Spec 4.3 warning. Developer tools and the remote debugging port are off in release builds.
- **Open point.** The prototype is several pages and remembers theme and text size in browser storage, which `file://` pages may forget. Serving the pages from pywebview's built-in server on `127.0.0.1` fixes that but opens a loopback port. This needs a decision and a test before the shell stage.

### 3.3 Why two processes

The engine runs as a child process of the shell, started from the same frozen executable.

- **One engine for both forms.** The command-line tool and the desktop app run the same code through the same protocol (Spec 9).
- **A heavy or stuck step cannot freeze the window.** Personal-data detection and PDF reading are slow and run outside the interface process.
- **No port is opened** between shell and engine. They talk over stdin and stdout.
- **Hostile files are contained.** File parsing runs in its own short-lived child process with time and memory limits (section 8.4).

## 4. Data flow

### 4.1 The fixed pipeline

The order is fixed and code runs it (P3). The AI never chooses a step and has no tools (Spec 6.1).

| Stage | Spec steps | Module | AI? | Leaves the computer |
| --- | --- | --- | --- | --- |
| Read and split | 1–2 | `ingest` | No | Nothing |
| Map links | 5 | `links` | No | Nothing |
| Find personal data | 3 | `privacy` + Presidio | No | Nothing |
| Privacy check | 4 | The user | No | Nothing |
| Match, extract | 6a, 6b | `checking` | Yes | Placeholder text, position topics and types |
| Quote check | 7 | `checking` (code) | No | Nothing (one retry call on a failed quote) |
| Pick labels | 8 | `core` | No | Nothing |
| Judge, explain, summarise | 9–11 | `checking` | Yes | Placeholder text, level text, fixed labels |
| Rewrite (on request) | 12 | `writing`, then `checking` | Yes | One clause as placeholder text |
| Message | 13 | `outputs` | No, unless the user asks for a rewrite | Nothing by default ([ADR 0011](adr/0011-who-writes-the-words.md)) |
| Report | 14 | `outputs` | No | Nothing |

`links` runs before `privacy` so the privacy allow-list can reuse the defined terms ("the Contractor"). The Spec's step numbers do not change. `cli` passes `LinkMap.terms`, a `core` shape, into `privacy`.

### 4.2 The offset chain

Every position in the app points into **one canonical text**, built from the page's own characters. Nothing is found by searching a second copy.

```text
 glyphs on the page ──► canonical text ──► match key        (folded copy + index map)
        ▲                     │
        │                     ├──► sentences  4.2.s1, 4.2.s2 …  (stable ids)
   page boxes                 │
        ▲                     └──► placeholder text  (segments: copy · entity · escape)
        │                                   │
        └── exact maps back ◄── quote ◄── AI reply: sentence ids + short quote
```

The AI answers with pointers: clause and sentence ids from a closed list, then a short quote. Code confirms the quote appears exactly once inside the cited sentences, maps it back through the segments to the real text, and from there to page boxes. The same rule runs again, by a different code path, right before a highlight is drawn. If that last check fails, nothing is drawn and the app says "Check [clause] yourself." The full reasoning is in [the seams report](../reports/Clause%20Tracer%20pipeline%20seams.md).

## 5. Data model and storage

### 5.1 Three kinds of data

| Kind | Examples | Rule |
| --- | --- | --- |
| **Raw** | Original file bytes, pasted text, typed party details, the confirmed placeholder map, the playbook snapshot, Presidio's findings, every AI request with its exact reply (failed ones too) | Append-only, never edited (D1, D8) |
| **Derived** | Canonical text, clauses, links, values, labels, explanations, the report | Rebuildable from raw; stored with `derived_by = step@version` and its cache key (D2) |
| **User state** | Checks, notes, ticks, tone, suggestions | Kept apart, keyed by stable position ids, so Re-run keeps it (Spec 6.3) |

Every stored record carries a schema version. Numbered migrations move derived data forward, after the encrypted file is copied to a numbered backup (D5, D6, D7). Ids are opaque strings made at the edge. Clause and sentence ids are derived from the clause number and span, so they stay the same when the same file is read again.

### 5.2 Where it is stored

The recommended design is a **hybrid** ([ADR 0006](adr/0006-encrypted-storage-and-secrets.md)).

```text
 OS password store ──► master key (32 random bytes) ──┬─► opens the encrypted SQLite file
   (or passphrase,                                    │     index, statuses, playbooks,
    Argon2id)                                         │     customers, user state, small records
                                                      │
                                                      └─► wraps one key per review
                                                              │
                                                              └─► AES-GCM blobs: contract bytes,
                                                                  placeholder map, AI replies
```

- **Deleting a review destroys its key.** The blobs cannot then be read, whatever the disk keeps. This matters because an app cannot overwrite a block on an SSD.
- **Blobs are bound to their place.** `review_id | record_id | schema_version` is passed as associated data, so a blob cannot be swapped for another.
- **Nothing readable is left in side files.** Temporary storage stays in memory, secure delete is on, and the write-ahead log is truncated after a delete and on close.
- **The honest claim.** "Encrypted at rest. Once its key is destroyed, a review is unreadable by this app." Not "securely erased". A backup made earlier still holds the old key, and the app says so.

### 5.3 What the password store does and does not protect

The master key and the API key sit in Windows Credential Manager or the Linux Secret Service. If Linux has no password store, the app asks for a passphrase and derives the key from it. It never writes a plain-text key.

This protects saved data from other people who use the computer and from someone who takes the disk. **It does not protect from malware running under the user's own account.** The OS stores are not built to do that, and no app-side trick closes the gap ([ADR 0014](adr/0014-protection-and-release-integrity.md)). The Help page should say this plainly.

## 6. Interfaces

### 6.1 The engine protocol

The shell and the engine exchange one JSON object per line. Every message carries `protocol_version`, so a shell and an engine that do not match fail at start-up with a clear error, not half-way through a review (I13).

| Request | Purpose |
| --- | --- |
| `hello` | Exchange protocol and app versions |
| `list_reviews`, `get_review` | Read saved reviews |
| `create_draft`, `update_draft` | Load a contract, pick a playbook and party, fix clause splits, confirm the privacy check |
| `estimate_cost` | The pre-run estimate, as a range |
| `start_review`, `resume_review`, `rerun_review` | Run the pipeline |
| `cancel` | Stop the running review; the engine answers with the cost so far |
| `set_label`, `set_note`, `mark_read` | User state |
| `rewrite_clause`, `build_message`, `build_report` | Writing and outputs |
| `delete_review`, `delete_all` | Deletion (idempotent, I8) |
| Playbook, customer and settings requests | The remaining screens |

The engine sends **events** on the same channel: `StepStarted`, `CallFinished(cost, tokens)`, `StepFinished`, `ReviewInterrupted`, `ReviewFailed(code)`. The command-line tool prints the same events to standard error.

Requests that change data are safe to repeat (I14's idempotency rule, applied to a local protocol). Errors come back as a code plus ids, never as contract text, because the user can copy error details (Spec 8.3).

### 6.2 The command line

```text
clause-tracer review --input contract.pdf --playbook freelancer.json --output report.md
clause-tracer resume --review <id>
clause-tracer serve --stdio
python -m clause_tracer.<module> --input samples/…        # any module alone (S1)
```

Exit codes are fixed in one place in `cli`: 0 success, 1 internal bug, 2 usage, 3 input file, 4 model service, 5 local storage or secrets, 6 interrupted and resumable (I12). Results go to standard output and errors to standard error.

### 6.3 The AI request

Every AI step uses one request shape and one frame for the prompt. The shape is deliberately **provider-neutral** (section 11).

```python
AiRequest(step, prompt_id, prompt_version,
          inputs,            # typed, structured inputs of the task
          messages,          # the prompt, rendered by the owning module
          schema_id, json_schema, model, privacy_mode, max_tokens)
AiReply(raw_body: bytes, text, model_used, provider_used, usage, generation_id)
```

The OpenRouter adapter sends `messages` with a strict JSON schema, `require_parameters`, and zero-retention routing when private mode is on. It never logs a body or a header. The module that owns the step validates the reply against its own Pydantic reply schema (D4, I16), and the exact reply bytes are saved before anything parses them (D8).

### 6.4 Errors

One base `ClauseTracerError(code, context)` in `core`, with a small tree of expected failures: input errors, model-service errors, local errors and cancellation (I5, I6). The runner maps model-service errors and cancellation to **Interrupted**, other project errors to **Failed** with their code, and anything else to Failed with code `internal` plus a local log entry. Only the edge turns a code into words, using [`ux-copy.md`](ux-copy.md) (I7).

## 7. Caching, resume and cost

**The runner** is about 200 lines of plain Python in `cli`, with no orchestration framework ([ADR 0005](adr/0005-engine-runner-shapes-and-ports.md)). Each step is a `StepSpec(name, version, run)`. The runner computes a key from the step name and version, prompt hash, model, privacy mode and the hashes of the step's inputs. If the store holds a finished output for that key, it loads it. Otherwise the step runs and its output is saved under the key.

**Each AI step is split in two.** The *call* is cached as a raw reply, keyed by a hash of the exact request. The *parse* is a pure, separately versioned function of that raw reply. Three things follow from this one mechanism:

- **Resume is a cache lookup.** An interrupted step continues at the next unsent call.
- **A parser fix costs nothing.** Fixed code re-reads the saved replies with no new AI calls (D2).
- **Test fixtures come free.** Saved replies from a paid run become replay fixtures.

**Prompt caching.** Prompts put the byte-stable system text first, the contract block next, and the per-position task last, so the provider can reuse the prefix. The app reads the cached-token count on every call and warns when caching misses, because a miss raises the cost of a 50,000-word review from about $0.82 to about $3.77 on the recommended default model `[Assumption]`.

**Estimate.** `[Assumption]` A review of 11 positions over about 50 clauses makes roughly 35 to 40 AI calls: one forward match per position, a few reverse-match batches, a handful of pair checks, one extraction per position, and the judge, explain and summarise calls. The pre-run estimate is shown as a range and is calibrated from the `usage.cost` of real runs.

## 8. Reliability and failure handling

### 8.1 Statuses

Review statuses and their moves are fixed by Spec 6.3. The runner writes the status row after each step, so a crash leaves the review Interrupted, never half-finished.

### 8.2 Calls to the AI service

| Failure | Handling |
| --- | --- |
| Network error or timeout | Retried 3 times with a pause and jitter, honouring `Retry-After`, then the review becomes Interrupted (I15) |
| Broken, empty or unknown reply | Retried once with a message saying what failed, then that value becomes unsure (Spec 6.2) |
| Quote not found, or number not in its quote | One retry, then unsure: "Couldn't confirm the wording" (Rule 3) |
| AI text fails a scan | One retry, then the slot falls back to its code template. The failed text is never shown |
| No private-mode endpoint, wrong key, no credit | Named error, review Interrupted with a plain fix |

A broken or timed-out reply is **never** treated as "nothing found". The two have separate result types (I4).

### 8.3 Cancel, close and orphans

- **Cancel** is a message. The runner checks a cancel token between steps and between per-clause calls, then reports the cost so far.
- **Closing the app pauses the review.** The engine exits when its stdin reaches end-of-file, so it cannot outlive the shell. On Windows a Job Object with kill-on-close backs this up.
- **Retry records are written before the pause**, so Resume knows which calls were already paid for.

### 8.4 Hostile files

A contract is untrusted input (D4, Spec 8.4). Before parsing, code checks the member count, declared and real expanded size, compression ratio and page count. XML is read with one hardened `lxml` parser: no entities, no network, no DTD. Relationships marked external are never followed. Each parse runs in a child process with a memory limit and a wall-clock limit, so a file built to exhaust the machine ends as `UnreadableFileError`, not a frozen app ([ADR 0007](adr/0007-document-reading-stack.md)).

## 9. Security and privacy

### 9.1 Trust boundaries

| Boundary | What crosses it | Guard |
| --- | --- | --- |
| File → engine | A contract or an imported playbook | Limits before parsing, child process, hidden-text checks, strict playbook format |
| Engine → AI provider | Placeholder text, position text | Privacy check, placeholder map, request builder tests, zero-retention routing |
| AI provider → engine | Filled-in forms | Closed schemas, Pydantic checks, quote check, output scans, code-picked labels |
| Engine → interface | Labels, quotes, AI wording | Plain text only, page pictures, no remote content |
| Engine → disk | Everything saved | Encrypted file, per-review keys, key in the OS store |
| Engine → logs | Events | Ids, codes, counts and costs only; never contract text |

### 9.2 What planted contract text can and cannot do

With code-picked labels, pointer answers, templates and output scans in place, text planted in a contract **cannot** change a number or yes/no label, show an invented number, name or phone number, tell the user to sign, or state law. It **can** still bias the reason given for a pencilled words label and an opt-in rewrite. Both sit under the real quote and carry the AI mark. This is a judgement, so the test set measures it with planted injections ([`testing-strategy.md`](testing-strategy.md) section 7).

### 9.3 Promises the app can prove, and ones it cannot

| Promise | Can a test prove it? | Wording to use |
| --- | --- | --- |
| No personal item in any request or log | Yes | Keep as written |
| No telemetry | Yes, for the engine. Not yet for the packaged shell | Keep; add a release-level network check |
| Private mode asks for zero retention | Yes: the request carries the fields | "asks for", as Spec 8.2 already says |
| Providers do not keep the contract | **No.** Nothing in the reply proves it | Keep Spec 8.2's careful wording; record the provider used per call and compare it with OpenRouter's zero-retention list |
| Saved data is unreadable without the key | Yes | Keep |
| A deleted review is gone | Partly | "unreadable once its key is destroyed", not "securely erased" |
| Safe from other software on the computer | **No** | Say what it protects from, and what it does not (section 5.3) |

Checking the provider against OpenRouter's zero-retention list is a new kind of request to OpenRouter. If the owner accepts it, Spec 8.1 must list it.

### 9.4 Copying, tampering and reverse engineering

The source is public, so nothing technical stops a copy, and hiding the shipped code would add antivirus warnings while protecting nothing. The design uses **no obfuscator** ([ADR 0014](adr/0014-protection-and-release-integrity.md)). Protection comes from elsewhere:

- **Copycats:** the licence. A registered trade mark on the name would be the stronger defence, but the owner ruled it out for now on cost (12 Nov 2026). Until then, keep dated public proof of first use of the name: signed Git tags and release dates.
- **Tampered builds:** make the real build easy to verify (section 10).
- **Secrets:** ship none. Prompts are public. The test set stays in a private repository used only by CI.

## 10. Packaging and release

| Step | Recommendation | Record |
| --- | --- | --- |
| Freeze the Python engine and shell | PyInstaller, one-folder build (one-file builds unpack on every start) | [ADR 0009](adr/0009-desktop-shell-protocol-and-packaging.md) |
| Windows installer | Inno Setup, scripted on GitHub's Windows runner, with the WebView2 bootstrapper | ADR 0009 |
| Linux package | **Open.** AppImage, `.deb` and Flatpak were not compared | Section 13 |
| Personal-data model | Bundled in the installer, never downloaded on first run | [ADR 0008](adr/0008-personal-data-detection-bundle.md) |
| Signing | Unsigned at first, with published checksums. An individual certificate later | ADR 0009 |
| Integrity | Signed `SHA256SUMS`, GitHub build attestations, a reproducible Linux build | [ADR 0014](adr/0014-protection-and-release-integrity.md) |
| Updates | "Check for updates" opens the GitHub release page, only when pressed (Spec 8.1) | Spec |
| Windows testing | CI installs the build silently and drives the real window with Playwright for Python. A 90-day evaluation VM covers the manual look | ADR 0009 |

CI runs `scripts/check.sh` on Linux on every pull request. A Windows job joins when the first code that touches files, paths or wheels lands, because the developer has no Windows machine to catch those problems by hand.

## 11. Room for a hosted option later

The owner may later let Clause Tracer itself be the AI provider, with optional accounts. **Version 1 does not change:** own key, no accounts, no server. The design only keeps the door open ([ADR 0015](adr/0015-provider-ready-seam.md)). `[Assumption]` Even then, contracts are handled on the user's computer by default.

| Seam | What version 1 does now |
| --- | --- |
| The AI call | One `AiClient` port. `AiRequest` carries structured inputs as well as the rendered prompt, so a hosted adapter could build prompts on a server |
| Core shapes | Nothing OpenRouter-specific in `core`. Routing flags and cost fields live in the adapter |
| Evidence guarantees | Quote checks, number checks and code-picked labels stay on the user's computer, whoever runs the model |
| Credentials | Stored under a provider id, so an account token could later use the same slot |
| Engine protocol | Transport-neutral requests and events; no screen logic in the engine |
| Paid features | No licence or feature gating in the app. It could be patched out, and would be a pattern to undo |
| Release channel | Signed and attested from the first release |

If a hosted option is ever added, these promises change and every copy must be updated in the same change ([WRITING_DOCS.md](../WRITING_DOCS.md) section 3): "no accounts, no sign-in, no server run by the project" and "uses your own OpenRouter key". A hosted service would also make the project a processor of users' contract text, which needs legal advice first.

## 12. Trade-offs, and what to revisit

| Choice | What it costs | Revisit when |
| --- | --- | --- |
| Hand-written runner, no framework | The project owns about 200 lines of resume and cache code | Steps stop being a fixed list |
| pywebview, not Tauri or Electron | No built-in updater, bundler or permission system; the Linux webview varies between distributions | A second developer who reviews Rust or TypeScript joins, or WebKitGTK problems pile up |
| One PDF engine through its low-level API | Harder C-style calls inside `ingest` | The bundled PDFium lacks a needed function, or reading order fails on two-column contracts |
| Hybrid storage | Two mechanisms to test instead of one | Never, unless per-review deletion is dropped |
| Medium personal-data model | Lower recall than larger models on some names | The planted-entity set shows a larger model's gain is real |
| Templates instead of AI wording | Stiffer tone in the message and explanations | Users ask for warmer text; the opt-in rewrite covers the first step |
| Four match searches instead of one | About two cents more per review `[Assumption]` | The test set shows a search adds nothing |
| No obfuscation | Shipped code is readable | Never for public code; a server is the place for anything secret |
| Unsigned Windows installer at first | A SmartScreen warning on install | Before wide promotion |

## 13. Decisions

The owner accepted ADRs 0005 to 0015 on 12 Nov 2026.

| Decision | Recommendation | Record |
| --- | --- | --- |
| Step runner, core shapes, ports, HTTP client | Hand-written runner; frozen dataclasses; `Protocol` ports; `httpx2` with a small retry loop | [ADR 0005](adr/0005-engine-runner-shapes-and-ports.md) |
| Storage and secrets | Hybrid encrypted store with a key per review; OS password store with a passphrase fallback | [ADR 0006](adr/0006-encrypted-storage-and-secrets.md) |
| Reading PDF and Word files; report PDF | `pypdfium2` alone at run time; hardened `lxml` for Word; NUPunkt; ReportLab | [ADR 0007](adr/0007-document-reading-stack.md) |
| Personal-data detection (Spec 13) | Presidio with a pinned config and the medium spaCy model, behind code-first finders | [ADR 0008](adr/0008-personal-data-detection-bundle.md) |
| Desktop shell, protocol, packaging (Spec 13) | pywebview; engine child process over stdio; PyInstaller one-folder; Inno Setup | [ADR 0009](adr/0009-desktop-shell-protocol-and-packaging.md) |
| Starting models and Jev (Spec 13) | Claude Sonnet 5.5 by default, two comparison models; Jev as an experiment only | [ADR 0010](adr/0010-starting-models.md) |
| Who writes the message, summaries and AI mark | Code templates by default; clause types from a closed list; one fixed line saying what was checked | [ADR 0011](adr/0011-who-writes-the-words.md) |
| Missing, unsure and failed evidence | A checkable "searched, nothing found" list; disagreeing searches become unsure; unplaceable quotes keep their label | [ADR 0012](adr/0012-missing-unsure-and-evidence-failures.md) |
| Test layers and release gates | Five layers, a paid run on a budget, the project's own gates | [ADR 0013](adr/0013-test-layers-and-release-gates.md) |
| Protection and release integrity | No obfuscation; signed and attested releases; honest wording; trade mark deferred | [ADR 0014](adr/0014-protection-and-release-integrity.md) |
| Room for a hosted option | Keep the seams in section 11 open; change nothing users see | [ADR 0015](adr/0015-provider-ready-seam.md) |

**Still open after this work.** These were not researched well enough to recommend, or need a measurement or a lawyer:

- The Linux package format (AppImage, `.deb` or Flatpak).
- Whether the pages are served from `file://` or a loopback server (section 3.2).
- Final input limits and the real cost per review, from the first paid run (Spec 13).
- Whether EU AI Act Article 50 puts a marking duty on this app. Take legal advice; the docs must not say it does not apply.
- Whether to register a trade mark later, and how FSL would be enforced. Both need a lawyer.
- Presidio's speed on a real 60,000-character contract on an ordinary laptop.

## 14. Changes this work made to earlier documents

The research found facts in the earlier architecture report that are out of date or wrong, and rules worth adding to the Constitution. Each edit, with its reason and source, is listed in [the edit record](../reports/Edits%20to%20source%20documents%202026-11-11.md).
