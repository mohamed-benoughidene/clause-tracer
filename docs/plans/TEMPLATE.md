<!--
Template note (delete this note in your copy).
Copy this file to `stage-NN-name.md`. Keep every part, and write "None" where a part is empty.
Read the README in this folder first: it says how a plan is read, written and implemented.
Prompts in italics tell you what belongs in each part. Replace them with your own text.
A strong model writes the plan and a cheaper model implements it: leave the implementer no design choice. Every name, field, type, signature, error and test case is written in the task.
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

*Write each task so the implementer makes no design choice. **Build:** the exact file, class and function names, every field with its type, every signature with its return type, and the error raised and when. **Tests first:** each test by name, with its input and expected result, or the owner table that holds the expected result (its path, its columns and how the test reads it). For a property test, the property and the generator. **Done when:** a command and its expected outcome. Never write "as needed", "suitable", "such as", "or similar", "consider" or "decide".*

### M1: *name*

*What you can see or test when this milestone is done.*

*The task below is an example of the right size. Replace it with your own first task.*

- [ ] **S1-M1-T1: Add the `Span` shape (EXAMPLE, replace)**
  - **Build:** In `src/clause_tracer/core/wording.py`, add `@dataclass(frozen=True, slots=True, kw_only=True) class Span` with exactly two fields, `start: int` and `end: int`, and no more. The range is half-open: `start` is included and `end` is not. Add `def __post_init__(self) -> None` that raises `ValueError("span start must be 0 or more")` when `start < 0`, and `ValueError("span end must not be before start")` when `end < start`. Add `Span` to `__all__` in `src/clause_tracer/core/__init__.py`.
  - **Files:** `src/clause_tracer/core/wording.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_span.py`, `src/clause_tracer/core/README.md` (add `Span` to the shapes).
  - **Tests first:** in `test_span.py`: `test_span_length_is_end_minus_start` (`Span(start=2, end=5)`: `end - start == 3`); `test_empty_span_is_allowed` (`Span(start=4, end=4)` builds); `test_negative_start_raises` (`Span(start=-1, end=2)` raises `ValueError`); `test_end_before_start_raises` (`Span(start=5, end=4)` raises `ValueError`); `test_span_is_frozen` (assigning `start` raises `dataclasses.FrozenInstanceError`). See each fail before the code exists.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_span.py` reports 5 passed, and `scripts/check.sh` exits 0.
  - **Rules:** Constitution S3 (shape written down in the module README), T1 (pure, no side effects), D4 (bad input is rejected at the door).
  - **Depends on:** None

### M2: *name*

*What you can see or test when this milestone is done.*

- [ ] **SN-M2-T1: *short name***
  - **Build:** *The exact file, names, fields with types, signatures with return types, and errors. No choice left to the implementer.*
  - **Files:** *The files it creates or changes.*
  - **Tests first:** *Each test by name, with its input and expected result, or the owner table that holds it.*
  - **Done when:** *A command and its expected outcome.*
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
- [ ] Every deviation is recorded in section 10, and "Notes for the next stage" sums them up.
- [ ] *Stage-specific check, from the stage outline's "Done when". Add one line for each.*

## 8. Change log

*Dated notes of every change made to the plan after the owner accepted it: what changed, and why. Which changes need the owner first: see the README, "When the plan is wrong".*

| Date | Change | Why |
| --- | --- | --- |
| *D Mon YYYY* | *What changed.* | *Why it changed.* |

## 9. Notes for the next stage

*Filled in when the stage is done. What was built. What differs from the outline. A short summary of the deviations in section 10. What the next stage should know. Write "None" under a heading if there is nothing to say.*

## 10. Deviations from the plan

*Filled in by the implementer while building. A deviation is a place where the built code differs from plan text that stays as it is: a private helper the plan does not name, an extra check, a different build order, a line split to satisfy `ruff`. Follow the plan exactly; a deviation is the exception, never the way to work.*

*A deviation never changes a name, a field, a type, a signature, an error or its message, an expected value, a test, or what the code does. Any of those is a stop: ask the owner, and change the plan (see [the README](README.md), "When the plan is wrong"). A change to the plan text goes in the change log (section 8), not here.*

*Add the row in the same commit as the task. Write "None" in the first row while there are none.*

| Date | Task | What the build does differently | Why | Behaviour changed |
| --- | --- | --- | --- | --- |
| *D Mon YYYY* | *SN-M1-T1* | *What differs from the plan text, with the file and the name.* | *Why the plan text could not be followed as written.* | *No. (Yes is never allowed here: it is a stop.)* |
