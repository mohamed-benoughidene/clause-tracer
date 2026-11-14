<!--
Template note (delete this note in your copy).
Copy this file to `stage-NN-name.md`. Keep every part, and write "None" where a part is empty.
Read the README in this folder first: it says how a plan is read, written and implemented.
Prompts in italics tell you what belongs in each part. Replace them with your own text.
-->

# Stage N plan: `module`

| | |
| --- | --- |
| Stage | *N, and the module name. For example: 1, `core`* |
| Status | Draft *(one of: Draft, Accepted, In progress, Done. See [the README](README.md). Only the owner accepts a plan. The agent records it)* |
| Branch | *The branch pattern, one branch for each milestone. For example: `feat/core-mN-short-name`. See [the README](README.md), "Branches and pull requests"* |
| Accepted on | Not yet |
| Stage outline | [System design section 15.N](../system-design.md) *(replace N, and link to the heading)* |

## 1. Goal

*One or two sentences: what exists when the stage is done.*

## 2. Scope

*What this stage builds, and what it leaves to later stages. Cover everything the stage outline and the testing strategy ask for, and nothing more.*

### Builds

- *One bullet for each thing the stage builds.*

### Leaves to later stages

- *One bullet for each thing that is close by but not in this stage, with the stage that takes it.*

## 3. Read first

*The sections of the spec, the system design, the testing strategy and the decision records that govern this stage. Link to them. Do not repeat them.*

- [Spec section N](../spec.md)
- [System design section N](../system-design.md)
- [Testing strategy section N](../testing-strategy.md)
- ADR NNNN, linked as `../adr/NNNN-title.md`

## 4. Checks before starting

*Anything to confirm before the first task, such as an unverified assumption. If a check fails, stop and bring it to the owner. Write "None" if there are none.*

- [ ] *The check, and how to run it.*

## 5. Milestones and tasks

*Two to six milestones. Each one is a set of tasks that together give one result you can see or test. Keep each task to one commit, at most about half a day. Give every task a test or a check. Order by dependency: shapes before the code that uses them, fakes before the code tested with them. Task ids are `SN-M1-T1`: stage, milestone, task.*

### M1: *name*

*What you can see or test when this milestone is done.*

*The task below is an example of the right size. Replace it with your own first task.*

- [ ] **S1-M1-T1: Add the `Span` shape (EXAMPLE, replace)**
  - **Build:** Add a frozen dataclass `Span` with `start` and `end` offsets into the canonical text. The range is half-open: `start` is included and `end` is not. A span with `end < start` or a negative `start` raises `ValueError`.
  - **Files:** `src/clause_tracer/core/span.py`, `src/clause_tracer/core/tests/test_span.py`, `src/clause_tracer/core/README.md` (add `Span` to the shapes).
  - **Tests first:** `test_span_length_is_end_minus_start`; `test_empty_span_is_allowed`; `test_negative_start_raises`; `test_end_before_start_raises`; `test_span_is_frozen`. Each fails before the code exists.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_span.py` passes, and `scripts/check.sh` passes.
  - **Rules:** Constitution S3 (shape written down in the module README), T1 (pure, no side effects), D4 (bad input is rejected at the door).
  - **Depends on:** None

### M2: *name*

*What you can see or test when this milestone is done.*

- [ ] **SN-M2-T1: *short name***
  - **Build:** *What to build, in one to three sentences.*
  - **Files:** *The files it creates or changes.*
  - **Tests first:** *The tests written before the code, and what each must prove.*
  - **Done when:** *The observable check.*
  - **Rules:** *Constitution rule ids and decision records that shaped it.*
  - **Depends on:** *SN-M1-T1*

- [ ] **SN-M2-T2: *short name of an owner-only task* (Owner)**
  - **Build:** *Owner only. For example, the expected-answer table of an acceptance test. The AI agent does not write or change it (Constitution T11). The agent ticks it after the owner says so.*
  - **Files:** *The files the owner changes.*
  - **Tests first:** *None. The owner's values are the expected answers.*
  - **Done when:** *The owner has written the values and said so.*
  - **Rules:** *Constitution T11.*
  - **Depends on:** *None*

## 6. Open questions

*Points the docs do not settle. Each goes to the owner before the task that needs it. Do not answer them here: the last column holds a link to where the owner's decision was recorded (its home: the spec, the system design or a decision record), not the decision itself. Write "None" in the first row if there are none.*

| # | Question | Needed by task | Recommendation (if any) | Owner's answer |
| --- | --- | --- | --- | --- |
| 1 | *The question.* | *SN-M1-T1* | *Your suggestion, or "None".* | *Left empty until the owner answers, then a link.* |

## 7. Done when

*The checks that close the stage. Tick each one only when it is true.*

- [ ] Every task above is ticked.
- [ ] `scripts/check.sh` passes with no errors.
- [ ] Each touched module's README records its shapes (Constitution S3).
- [ ] Every promise the stage touches has its test (Constitution T13).
- [ ] The lines that state the project's status are updated (see the README, "When the stage is done").
- [ ] The owner has been told what was built, and what the next stage should know.
- [ ] *Stage-specific check, from the stage outline's "Done when". Add one line for each.*

## 8. Change log

*Dated notes of every change made to the plan after the owner accepted it: what changed, and why. Which changes need the owner first: see the README, "When the plan is wrong".*

| Date | Change | Why |
| --- | --- | --- |
| *D Mon YYYY* | *What changed.* | *Why it changed.* |

## 9. Notes for the next stage

*Filled in when the stage is done. What was built. What differs from the outline. What the next stage should know. Write "None" under a heading if there is nothing to say.*
