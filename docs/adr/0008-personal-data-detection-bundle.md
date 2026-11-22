# ADR-0008: Bundle Presidio with spaCy en_core_web_md behind a code-first layer

**Status:** Accepted (12 Nov 2026)
**Date:** 2026-11-11
**Deciders:** Project owner

## Context
[Spec 4.2](../spec.md) replaces names of people and companies, addresses, emails, phone numbers, ID numbers and bank numbers before anything goes to the AI. Spec 6.1 step 3 runs on the user's computer with code plus Presidio. Spec 11 requires that Presidio plus typed details catch every planted name, company and address. Spec 13 leaves open how Presidio and its model are bundled, and the download size.

The [pipeline architecture report](../../reports/Clause%20Tracer%20pipeline%20architecture.md) put deterministic finders before NER. It also said Presidio's default now uses a slim spaCy engine plus GLiNER. [The v1 design decisions report](../../reports/Clause%20Tracer%20v1%20design%20decisions.md) found that claim is not supported by the code on `main`. Runtime dependencies must be MIT, BSD or Apache. Spec 8.1 lists every outbound call, so a model download would add one.

## Decision
The project owner accepted the following on 12 Nov 2026.

- **Presidio** with the adapter's own pinned config file, never the packaged default.
- **spaCy `en_core_web_md`** (31.9 MB), with the ORGANIZATION label switched back on.
- **A deterministic layer in front**, which carries the promise: typed party details and their variants, checksum patterns such as bank numbers, company-suffix rules and address rules. NER is a net behind them.
- **Bundle the model in the installer.** No download on first run.
- **Switch rule.** Move to `en_core_web_lg` (382 MB), or add Knowledgator's small GLiNER model, only if the project's own planted-entity set shows a gain whose confidence interval excludes zero.
- **A test** asserts the loaded engine name, model name and recogniser list.

## Options Considered

### Option A: Presidio, en_core_web_md, ORGANIZATION on, deterministic layer (chosen)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med: a pinned config and several rule finders |
| Cost | 31.9 MB model in the installer |
| Scalability | Single user. Latency on a 60,000-character contract is not measured |
| Team familiarity | High: Python and spaCy |

**Pros:** small download and fully offline. No PyTorch. Rules that code can test carry the promise.
**Cons:** NER recall on organisations and addresses is weak, so the rules must be good.

### Option B: Presidio with en_core_web_lg
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low: the same stack |
| Cost | 382 MB model |
| Scalability | Single user, not a scale question |
| Team familiarity | High |

**Pros:** the model the packaged default config names; fully offline.
**Cons:** about twelve times the download, for a gain nobody has measured on contracts.

### Option C: GLiNER through Presidio
| Dimension | Assessment |
|-----------|------------|
| Complexity | High: PyTorch or ONNX in the bundle |
| Cost | Torch and onnxruntime sizes not researched |
| Scalability | 20 to 50 times slower on CPU |
| Team familiarity | Low |

**Pros:** organisation recall of 93% against 23% in a vendor benchmark.
**Cons:** needs PyTorch. Its ONNX path was measured 8 to 11 times slower than torch on x86. The benchmark comes from a vendor who sells a competing tool ([getshadow.dev](https://getshadow.dev/benchmarks/)).

### Option D: Download the model on first run
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med: pinning, checks, offline handling |
| Cost | Smaller installer |
| Scalability | Single user, not a scale question |
| Team familiarity | Med |

**Pros:** a smaller first download.
**Cons:** adds a second outbound host, fails offline, and contradicts Spec 8.1. If ever used, pin a SHA-256 and use safetensors or ONNX, not pickle.

**Rejected models.** `openai/privacy-filter` has no organisation label and is at least 809 MB. Piiranha is CC-BY-NC-ND, so not for commercial use ([Piiranha](https://huggingface.co/iiiorg/piiranha-v1-detect-personal-information)). Flair has had no release since Feb 2025. `nvidia/gliner-PII` only if its licence text is cleared.

## Trade-off Analysis
Sizes, licences and defaults are verified ([Presidio releases](https://github.com/data-privacy-stack/presidio/releases)). The packaged [default.yaml](https://raw.githubusercontent.com/data-privacy-stack/presidio/main/presidio-analyzer/presidio_analyzer/conf/default.yaml) still names `en_core_web_lg` and ignores ORGANIZATION with the comment "Has many false positives". So the vendor's 23% figure probably reflects that setting, not spaCy's ceiling. That is judgement. A newer slim engine and GLiNER config were merged on 12 Apr 2026 ([PR #1916](https://github.com/data-privacy-stack/presidio/pull/1916)), but they are opt-in and signposted for Presidio v3. The default is expected to change, which is why the config is pinned and tested. A pinned `preshed<3.0.14` was needed in Oct 2026 to keep spaCy model loading working. That is a live reason to pin the whole stack.

The recall figures are a vendor's, with code "available on request". No public benchmark of person, organisation and address recall on English commercial contracts exists. So the bundle choice rests on judgement until the project measures its own planted-entity set. Gaps carried over: latency on a 60,000-character contract was not measured by anyone; the installed sizes and PyInstaller behaviour of torch and onnxruntime were not researched; the NVIDIA licence text was not read in full; no English contract corpus with gold PII labels was found.

## Consequences
- Easier: a small, offline installer, and a promise carried by rules that tests can check.
- Easier: the planted-entity set gives a clear, measured trigger for any model change.
- Harder: the deterministic layer is real work: variants, checksums, suffixes and addresses.
- Revisit when the planted-entity set shows a gain for `lg` or GLiNER whose confidence interval excludes zero, or when Presidio v3 changes the defaults.

## Action Items
1. [ ] Measure Presidio latency on a real 60,000-character contract on the developer's machine.
2. [ ] Build the planted-entity generator with Faker and real dictionaries, and score "any token survives in the placeholder text" per type.
3. [ ] Write the pinned config and the test that asserts engine, model and recogniser list.
4. [ ] Check spaCy model loading under PyInstaller one-dir ([ADR 0009](0009-desktop-shell-protocol-and-packaging.md)).
5. [x] Tick the Presidio bundling item in Spec 13 (done 12 Nov 2026).
6. [ ] State the download size in Spec 9, once measured.
7. [ ] Check the Text Anonymization Benchmark, which the research did not look at, before building the planted-entity set.

## Amendment (13 Nov 2026): known names are replaced in position text and rewrite instructions too

Before this, only "why this matters" notes had known names replaced before they were sent. Position topics, types and level text, and the rewrite instruction (Spec 6.1 step 12), were sent as typed. A name typed into a position or an instruction could leave the computer.

The project owner decided on 13 Nov 2026:

- **Known names** are the confirmed personal items of this review and the typed party details.
- Code replaces them with their placeholders in **position text** (topics, types and level text) and in **rewrite instructions**, as well as in the contract text and notes, before anything is sent. Code puts them back in what comes back.
- The **privacy canary test** covers both fields: a known name typed into a position and one typed into a rewrite instruction must not appear in any request body ([testing strategy](../testing-strategy.md) section 8).
- This does not change the bundle chosen above. It widens the text that the deterministic layer's replacement list is applied to.

Spec sections 4.2, 4.6, 6.1, 6.2 and 13 say the same, and so does [the system design](../system-design.md) section 4.1.

## Amendment (22 Nov 2026): rules that the stage 4 plan settled

The project owner decided on 21 and 22 Nov 2026, in answer to the open questions of the [stage 4 plan](../plans/stage-04-privacy.md) and the [research report](../../reports/Privacy%20finder%20design%20choices.md):

- **The kept place.** The place named in the governing-law clause is kept only when it is a country, a nation of the United Kingdom ("England and Wales" counts as one), a US state, a Canadian province or an Australian state. Any other place in that clause, such as a city, is replaced if a finder marks it. [Spec 4.2](../spec.md#42-privacy-check) says the same.
- **A name next to the place.** When a person's or company's name that a finder marks touches the kept place, the whole marked name is replaced and the place words that touch it go with it. Every other kind of span is cut at the place. The reason: cutting a name could leave one word of it readable.
- **ID and bank spans hold the value only.** "Company number" stays readable and only `09876543` becomes `ID 1`.
- **Four more deterministic patterns** are built in stage 4 and not left to stage 7: UK National Insurance numbers, Luhn-checked card numbers, bare GB VAT numbers with their checksum, and UK company-number prefixes. A bare number that a checksum does not support is not replaced by these patterns.
- **The placeholder marker stays `⟦ ⟧`.** A paid check on real Claude models found no difference in survival between the marker forms. The prompts carry the rule "write each placeholder exactly as it appears" ([system design 15.8](../system-design.md#158-stage-8-checking-and-the-message-templates)).
- **Doubts come later.** The shape exists in `core` (task S1-M6-T8 of the stage 1 plan). The code that fills it is built where the user first sees suggestions.

None of this changes the bundle chosen above. It narrows what the deterministic layer keeps and widens what it finds.
