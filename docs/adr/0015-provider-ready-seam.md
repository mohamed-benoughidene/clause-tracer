# ADR-0015: Ship version 1 with the user's own key, but keep one seam open for a hosted provider

**Status:** Proposed
**Date:** 2026-11-11
**Deciders:** Project owner

## Context
[Spec 1](../spec.md) says the app runs on the user's computer with the user's own OpenRouter key, and nothing goes to a server run by the project. Spec 12 rules out accounts, sign-in and any project server in version 1. A later version may let the project itself become the AI provider, with optional user accounts. Version 1 must not block that.

[The v1 design decisions report](../../reports/Clause%20Tracer%20v1%20design%20decisions.md) gives seven steps for this. Its authors say this section is **entirely judgement**: the research budget was spent before it, and it cites only OWASP and MASVS-based material ([MASVS-RESILIENCE](https://mas.owasp.org/MASVS/11-MASVS-RESILIENCE/)). The whole of this ADR is therefore judgement. A server is the only place a secret, a paid feature or a real licence check can be protected. It also makes the owner a processor of users' contracts.

**Assumption:** contract handling stays on the user's computer by default, even if a hosted option is added. Reading, privacy replacement, quote checks and label picking never move to a server.

## Decision
We recommend keeping version 1 exactly as specified, and holding these seams open. This awaits the owner's decision.

1. **One provider port.** The AI call sits behind one port, `AiClient` ([ADR 0005](0005-engine-runner-shapes-and-ports.md)).
2. **`AiRequest` carries both forms of the task.** The structured inputs: step, prompt id and version, typed inputs, schema id, model and privacy mode. And the rendered messages, built by the pipeline module that owns the step. The OpenRouter adapter sends the rendered messages. A future hosted adapter could send only the structured inputs and build prompts on its server.
3. **Neutral core shapes.** Nothing OpenRouter-specific appears in core shapes beyond neutral fields: no zero-retention flags, no cost-field names, no model-name lists. The adapter maps privacy mode to OpenRouter's settings.
4. **Checks stay local.** Code-picked labels and the quote and number checks run in the app, whatever runs the model.
5. **Credentials under a provider id**, so an account token could later sit in the same OS-store slot as the user's own key ([ADR 0006](0006-encrypted-storage-and-secrets.md)).
6. **No licence or feature gating** built into the app in version 1. It would be crackable and set a pattern to undo.
7. **Open wording.** Prefer "this version has no server; your contracts go only to the AI provider you choose" over "will never connect to any server".
8. **Signed and attested releases from v1** ([ADR 0014](0014-protection-and-release-integrity.md)), and a notify-only, opt-in update check, so a future service cannot quietly become a telemetry channel.

## Options Considered

### Option A: v1 as specified, seams held open (recommended)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low: a few extra fields and one naming rule |
| Cost | Little extra effort now |
| Scalability | A hosted adapter can be added without touching pipeline modules |
| Team familiarity | High: plain dataclasses and one port |

**Pros:** no promise changes now. A later hosted option needs a new adapter, not a rewrite.
**Cons:** `AiRequest` carries some fields the v1 adapter does not send.

### Option B: v1 with the rendered prompt string only
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low |
| Cost | None now |
| Scalability | A hosted provider would need pipeline changes |
| Team familiarity | High |

**Pros:** the simplest request shape.
**Cons:** prompts could only be built in the app, so a server-side prompt path would mean reworking every step.

### Option C: Build accounts or a licence check into v1
| Dimension | Assessment |
|-----------|------------|
| Complexity | High |
| Cost | A server to run, and legal duties |
| Scalability | Real scale and uptime questions |
| Team familiarity | Low |

**Pros:** ready for a paid service.
**Cons:** breaks Spec 1 and Spec 12. A check in the app can be patched out.

## Trade-off Analysis
All of this is judgement, as the report says. The core trade is a few unused fields now against a rewrite later. Keeping checks local means a hosted path would keep the same evidence guarantees. Keeping OpenRouter names out of `core` honours B3 (depend on things that change rarely) and P4 (ports and adapters).

These existing user promises would have to change if a hosted option is ever added. **None changes now.**

| Promise | Where |
|---------|-------|
| "Accounts, sign-in, or any server run by the project" are not in v1 | Spec 12 |
| "Nothing goes to a server run by the project" | Spec 1 |
| "uses your own OpenRouter key" | Spec 1, `docs/ux-copy.md` intro |
| "There's no account, no server run by the project and no telemetry" | `README.md` |
| The outbound list (OpenRouter and GitHub only) | Spec 8.1 |

Gaps, stated plainly in the report: GDPR duties for a solo developer running an LLM proxy that handles contracts, upstream zero-retention terms, and the cost of a minimal proxy were not researched. A lawyer is needed before that version is planned.

## Consequences
- Easier: a hosted provider later is a new adapter plus a server, with no pipeline changes.
- Easier: the evidence guarantees stay identical whoever runs the model.
- Harder: reviewers must keep provider-specific names out of `core`.
- Revisit only when the owner plans a hosted version. Trigger a legal review first.

## Action Items
1. [ ] Define `AiRequest` in `core` with both the structured inputs and the rendered messages.
2. [ ] Add an architecture test that `core` shapes contain no OpenRouter-specific field names.
3. [ ] Store the API key under a provider id in the `SecretStore` adapter.
4. [ ] Review the docs for wording that rules out a future opt-in service, and prefer the open wording above.
5. [ ] If accepted, no Spec change is needed now. List this ADR in Spec 12 as the reason the seam exists.
