# ADR-0005: Keep a hand-written step runner, frozen core shapes and Protocol ports

**Status:** Accepted (12 Nov 2026)
**Date:** 2026-11-11
**Deciders:** Project owner

## Context
[Spec 6.1](../spec.md) fixes the pipeline: code runs a set sequence, and the AI only fills forms. Spec 6.2 sets the retry rules: one retry for a broken reply, three for a network error. Spec 6.3 says Resume continues from the first unfinished step, and finished steps aren't paid for again. [ADR 0004](0004-code-layout.md) puts the shapes in `core` and the wiring in `cli`.

The [pipeline architecture report](../../reports/Clause%20Tracer%20pipeline%20architecture.md) proposed a runner, core shapes and five ports. [The v1 design decisions report](../../reports/Clause%20Tracer%20v1%20design%20decisions.md) re-checked them against package metadata and documentation on 11 Nov 2026. For the choices in this record, it kept all but one and corrected the HTTP library. One developer reviews only Python, and AI agents write most of the code. So every part of the engine should be plain Python that this developer can read in one sitting.

## Decision
The project owner accepted the following on 12 Nov 2026.

- **Runner.** A hand-written runner of about 200 lines `[Assumption]` in `cli`. Each step is a `StepSpec(name, version, run)`. The cache key is a SHA-256 of the step name, version, prompt hash, model id, privacy mode and input hashes. State lives in the app's own encrypted store ([ADR 0006](0006-encrypted-storage-and-secrets.md)). Each AI step splits into a **call** (raw reply cached by request hash) and a **parse** (a pure, versioned function of the reply).
- **Shapes.** Frozen, slotted standard-library dataclasses in `core`, with tuples and no third-party imports. Pydantic `TypeAdapter` validates at the edges, for storage and config. AI reply schemas stay in the owning module.
- **Ports.** `typing.Protocol` ports in `core`: `AiClient`, `PiiDetector`, `ReviewStore`, `SecretStore` and `Clock`. One hand-written composition root, `cli/_wiring.py`, builds the adapters.
- **AI calls.** `httpx2` (BSD-3) with a retry loop of about 20 lines `[Assumption]`: a cap of 3 tries, with jitter. The step owns a hand-written one-retry reask loop and saves the raw reply bytes of every attempt. OpenRouter's Response Healing stays off.
- **Request shape.** `AiRequest` carries both the structured task inputs and the rendered messages. [ADR 0015](0015-provider-ready-seam.md) sets out why.

## Options Considered

### Option A: Hand-written runner, stdlib shapes, Protocol ports, httpx2 (chosen)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low: a few hundred lines of plain Python in total |
| Cost | No new runtime packages beyond `httpx2` and Pydantic, which Presidio brings anyway |
| Scalability | Single user, not a scale question. Resume is a cache lookup |
| Team familiarity | High: standard library and one small HTTP package |

**Pros:** cache keys are content-based, so a parser fix re-runs with no AI calls (D2, derived data can be rebuilt; D8, save the AI's exact reply). `core` stays pure (T1, keep the core pure; B3, depend on things that change rarely). Every retry rule matches Spec 6.2 exactly.
**Cons:** the project owns the runner's bugs. There is no ready-made dashboard or retry policy.

### Option B: DBOS as the runner
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med: a framework with its own storage and serialisation |
| Cost | A new runtime dependency; bundle size not researched |
| Scalability | Built for servers; recommends Postgres for production |
| Team familiarity | Low |

**Pros:** the strongest challenger. It gives durable workflows out of the box.
**Cons:** it pickles step outputs into its own SQLite file by default ([DBOS serialisation](https://docs.dbos.dev/python/reference/contexts#custom-serialization)). It keys checkpoints by workflow and step order, not by content ([DBOS config](https://docs.dbos.dev/python/reference/configuration)). Its state would sit outside the encrypted store.

### Option C: Hamilton
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med |
| Cost | A new runtime dependency |
| Scalability | Single user, not a scale question |
| Team familiarity | Low |

**Pros:** content-keyed caching, which is the idea Option A borrows.
**Cons:** its docs warn that cache keys "could be unstable across Python and Apache Hamilton versions" ([Hamilton caching](https://hamilton.apache.org/concepts/caching/)). Its results store sits outside the encrypted store.

### Option D: Pydantic models everywhere, with a DI container
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med |
| Cost | `core` depends on a fast-moving library |
| Scalability | Single user, not a scale question |
| Team familiarity | Med |

**Pros:** one validation library across the code.
**Cons:** it breaks the rule that `core` imports nothing outside the standard library. A DI container is not justified for five ports. msgspec is faster, but a second validation library is not worth it for v1.

### Option E: OpenAI SDK or Instructor for AI calls
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low to use, Med to bend to the retry rules |
| Cost | A larger dependency |
| Scalability | Single user, not a scale question |
| Team familiarity | Med |

**Pros:** proven with OpenRouter.
**Cons:** the OpenAI SDK retries twice by default and wraps raw responses in a "legacy" class ([openai-python](https://github.com/openai/openai-python)). Instructor and pydantic-ai own the retry loop, which conflicts with Spec 6.2's one retry and with saving raw bytes per attempt.

## Trade-off Analysis
The facts about DBOS and Hamilton are verified. The choice of Option A over them is judgement. The shapes and ports choices are judgement, with package facts verified. Abstract base classes are a fair alternative to Protocols if runtime enforcement is wanted. The report notes that plain `httpx` last released 0.28.1 on 6 Dec 2024 and that the OpenAI SDK has moved to `httpx2`. That fact is verified, but `httpx2`'s maintainer and changelog were not fetched. Gaps carried over: whether DBOS can open its SQLite through SQLCipher is unknown; Burr and pydantic-graph pages were not re-fetched; no 2025 or 2026 shapes benchmark was fetched; the `TypeAdapter` page text could not be extracted; OpenRouter docs were not re-fetched. Response Healing stays off because it changes the reply before the app sees it, which breaks D8.

## Consequences
- Easier: a parser fix replays saved replies at no cost, and every step runs alone with a fake (S1, every module runs by itself; T7, test around the model with a fake).
- Easier: an agent can read the whole engine in one place, and `lint-imports` guards the boundaries.
- Harder: the project writes and tests its own runner, retry loop and reask loop.
- Revisit if the runner grows well past its size estimate, or if `httpx2` shows no active maintainer.

## Action Items
1. [ ] Check `httpx2`'s maintainer, changelog and licence file before adding it with `uv add`.
2. [ ] Confirm that Pydantic `TypeAdapter` validates straight into frozen, slotted dataclasses on the pinned version.
3. [ ] Write the runner's cache-key rule and the call/parse split into `src/clause_tracer/cli/README.md`.
4. [ ] Record the `core` shapes and ports in `src/clause_tracer/core/README.md` when `core` is built (S3, write down input and output shapes).

## Amendment (12 Nov 2026): `httpx2` checked, and how to fake it in tests

- **`httpx2` is confirmed as the HTTP client.** It is maintained by the Pydantic organisation ([pydantic/httpx2](https://github.com/pydantic/httpx2)), which took over because `httpx` had gone quiet. Licence BSD-3-Clause, version 2.16.0 of 21 Oct 2026, and the OpenAI Python SDK depends on it. This closes action item 1.
- **Do not use `respx` with it.** `respx` 0.23.1 patches `httpx`, not `httpx2`. In a local test on 12 Nov 2026 the mock did not intercept, and the request went to the real network. Use `httpx2.MockTransport` instead: it is built in, it was tested the same day, and a handler of a few lines can refuse an unrecorded request and report unused recordings.
- **This is why tests block sockets.** A mocking tool that silently stops matching sends real requests. The suite-wide socket block in [`testing-strategy.md`](../testing-strategy.md) section 8 turns that into a failing test.

## Amendment (13 Nov 2026): three shape points settled for build stage 1

A review of the docs found three points about `core` shapes that no record settled. The project owner decided them on 13 Nov 2026.

- **Each step has its own input shape.** `AiRequest.inputs` holds the step's own frozen dataclass, never a free-form dictionary. `json_schema` is a read-only mapping built from the step's reply schema. Reason: stricter and easier to test.
- **Playbook text carries no written-by value.** It is always the user's own words or a starter's fixed text. The written-by value of [ADR 0016](0016-legal-positions-without-a-lawyer.md) stays on review output, messages, rewrites and notes.
- **`checking` is handed a cancel check.** `core` defines a small `CancelCheck` callable. The runner passes it in, and `checking` asks it between per-clause calls. Reason: the other way moves the per-clause calls into the runner and splits the checking logic across two places.

[The system design](../system-design.md) section 3.4 lists the shapes.

## Amendment (14 Nov 2026): stage 1 shape points answered

Writing the stage 1 task plan found points about `core` shapes and ports that no record settled. The project owner answered them on 14 Nov 2026.

- **Pydantic is installed now**, as a runtime dependency, through `.venv/bin/uv add pydantic`, with `uv.lock` committed. Action item 2 (the `TypeAdapter` check) runs on that locked version. `core` still never imports Pydantic.
- **The fakes live in `clause_tracer.core.fakes`.** They use only the standard library, are exported from `core`, and serve tests and every module's run-alone command.
- **`AiRecord` carries its own `schema_version`.** `AiRequest.inputs` is typed as an empty base class, `StepInputs`, which every step's own input shape subclasses. Stage 1 has only a test-only subclass.
- **`ReviewStore` in stage 1** saves and loads raw AI records, lists reviews, deletes a review, and purges expired reviews given "now". Stage 6 adds the rest as new methods.
- **"Unlimited"** is one field on `CheckedValue`, `unlimited: bool = False`. The stage 8 number parser turns "none" into 0.
- **The planner defines the extra shapes**, not the implementer: scan findings, the last check's result, the cost range, the input bundle of the label rules and the extra reason codes. They are exact in [the system design](../system-design.md) section 3.4, and the owner approves them with the plan.
- **The playbook checks of Spec 4.1** are pure functions in `core`, built in stage 1 and shared by stage 6 (reading playbook files) and stage 12 (the editor).
- **A rate limit is its own error.** `RateLimitedError`, code `rate_limited`, is a model-service error beside `NoCreditError` and `InvalidApiKeyError`. It carries an optional wait in seconds, `retry_after_seconds`, taken from the service's `Retry-After`. The OpenRouter adapter raises it after 3 retries of an HTTP 429. Stage 6 maps it to Interrupted with its own message (Spec 6.2 and 6.3).
- **A new reason code**, `UNLIMITED_UNCLEAR`, joins the label reasons: "unlimited" on a position where higher is better is unsure (see the amendment of 14 Nov 2026 in ADR 0012).

[The system design](../system-design.md) section 3.4 lists every shape, port and fake exactly.
