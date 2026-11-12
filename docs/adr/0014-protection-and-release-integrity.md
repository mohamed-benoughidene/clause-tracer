# ADR-0014: Protect the project with signed releases and honest wording, not obfuscation

**Status:** Accepted (12 Nov 2026)
**Date:** 2026-11-11
**Deciders:** Project owner

## Context
The project is source available under FSL-1.1-ALv2. Anyone can read the code, and each version becomes Apache 2.0 two years after release ([Spec 10](../spec.md)). Spec 8.3 encrypts stored data with a key in the system's password store. Spec 8.4 says each release publishes checksums. Spec 9 ships an unsigned Windows installer first. Runtime dependencies must be MIT, BSD or Apache.

The owner asked how to protect the code, the builds, local data and any hidden parts. [The v1 design decisions report](../../reports/Clause%20Tracer%20v1%20design%20decisions.md) found that nothing technical stops a copy, because the source is public. Obfuscating a binary protects nothing against a copycat, who takes the repository. It only adds antivirus flags and contradicts the "read the source" promise. Nothing in this ADR is legal advice.

## Decision
The project owner accepted the following on 12 Nov 2026, with the trade mark deferred.

- **No obfuscation** of any kind.
- **Copycats.** Keep FSL-1.1-ALv2. Enforce by polite email, then a DMCA notice for copied code, then a lawyer. **No trade mark for now:** the owner ruled it out on 12 Nov 2026 because of its cost. In its place, at no cost: use the name and logo the same way everywhere, and keep dated public proof of first use (signed Git tags, release dates, the repository history). This is weaker than a registered mark. How far an unregistered name is protected differs by country and needs a lawyer to say. Revisit registration before wide promotion, or if a copy appears under the same name.
- **Tampered builds.** A GPG-signed `SHA256SUMS`, GitHub artifact attestations, and reproducible Linux builds with fixed `PYTHONHASHSEED` and `SOURCE_DATE_EPOCH`. Windows OV signing when affordable ([ADR 0009](0009-desktop-shell-protocol-and-packaging.md)). A notify-only, opt-in update check against GitHub Releases.
- **Local data.** The planned design ([ADR 0006](0006-encrypted-storage-and-secrets.md)), a data directory with mode 0700, and an opt-in Argon2id passphrase. Publish the honest claim. Never promise memory wiping.
- **Hidden parts.** Ship nothing that must stay secret. Prompts stay public. The golden test set stays in a private repository used only in CI.

The honest wording for local data: contracts and the API key are encrypted at rest. They are protected from other people who use the computer and from someone who takes the disk. They are not protected from malware running under the user's own account.

## Options Considered

### Option A: Signed and attested releases, honest wording, trade mark deferred (recommended)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low to Med: release-workflow steps and paperwork |
| Cost | Nothing now. Later, if the trade mark is taken up: EUIPO 850 euros for one class ([EUIPO](https://www.euipo.europa.eu/en/trade-marks/before-applying/fees-payable-direct-to-the-euipo)) or USPTO $350 per class ([USPTO](https://www.uspto.gov/trademarks/trademark-fee-information)); OV certificate about $99 a year |
| Scalability | The name outlasts each version's two-year conversion to Apache 2.0 |
| Team familiarity | High for the workflow; legal steps need an attorney |

**Pros:** the name is the durable asset. Users can verify a download. The wording matches what tests can prove.
**Cons:** costs money and legal time. Does not stop a copy that uses another name.

### Option B: Binary obfuscation (PyArmor or Nuitka Commercial)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med to High |
| Cost | Adds antivirus flags; measured rates not researched |
| Scalability | Single user, not a scale question |
| Team familiarity | Low |

**Pros:** none against a copycat, who has the source.
**Cons:** public static unpackers exist for PyArmor up to 9.3 on Python 3.7 to 3.13 ([Pyarmor-Static-Unpack-1shot](https://github.com/Lil-House/Pyarmor-Static-Unpack-1shot)). Python bytecode decompiles at a 75% perfect rate. Both tools put proprietary runtime code into the app, against the licence rule.

### Option C: Runtime self-integrity checks
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med |
| Cost | Effort only |
| Scalability | Single user, not a scale question |
| Team familiarity | Med |

**Pros:** catches casual tampering.
**Cons:** a patched binary can patch out the check.

### Option D: Chrome-style app-bound encryption
| Dimension | Assessment |
|-----------|------------|
| Complexity | High: a privileged Windows service |
| Cost | High effort |
| Scalability | Single user, not a scale question |
| Team familiarity | Low |

**Pros:** raises the bar against same-user malware.
**Cons:** infostealers bypassed even Chrome's within months ([Elastic](https://www.elastic.co/security-labs/threat-command/katz-and-mouse-game)).

## Trade-off Analysis
The licence text, fees, attestation and reproducibility facts are verified. The enforcement ladder and the release chain are judgement. No FSL-specific enforcement story was found. The most public dispute, HashiCorp and OpenTofu in April 2024, ended in letters, not a ruling. Windows reproducibility is not guaranteed, so the claim is "Linux reproducible; Windows attested". The SLSA level was not confirmed, so do not quote one.

Prompts can never be secret: they leave the machine in plaintext on every call. OWASP says a system prompt "should not be considered a secret" ([OWASP LLM07](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/)). With no server, any licence check runs in the app and can be patched out, so any paid add-on is protected by licence, not obfuscation. gnome-keyring says it cannot keep secrets from other programs in the same session. A Python process cannot reliably wipe memory, because strings are immutable and libraries copy them.

Gaps carried over: UK and Madrid fees and app-store takedown routes were not verified. Smart App Control, Nuitka, Inno Setup and AppImage signing were not researched. No Microsoft primary document on DPAPI or Credential Manager was fetched. KWallet, Windows 11 Administrator protection and AppArmor were not researched. Cython difficulty and antivirus rates per tool were not researched.

## Consequences
- Easier: every release can be checked by anyone, and the promises match what tests prove.
- Easier: no secret parts means no secret-keeping work.
- Harder: legal steps and fees fall on the owner, and the golden set needs a private repository and CI access.
- Revisit when a copy appears, when the budget allows OV signing, or when a later version plans a hosted service ([ADR 0015](0015-provider-ready-seam.md)).

## Action Items
1. [ ] When money allows, take legal advice on: whether to register a trade mark, and its classes and market; FSL with any proprietary part, and its effect on the Apache 2.0 conversion; EU AI Act Article 50 (applies since 2 Aug 2026; do not state in the docs that it does not apply).
2. [ ] Add signed `SHA256SUMS`, `actions/attest` and a CycloneDX SBOM to the release workflow.
3. [ ] Make the Linux build reproducible and test it by building twice.
4. [ ] Create the private golden-set repository and give CI read access only.
5. [ ] If accepted, update Spec 8.3 and 8.4 with the honest wording and the release chain, and `docs/ux-copy.md` with matching lines.
