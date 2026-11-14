# Plans

This folder holds the **task plans**: one file per build stage, written just before that stage is built. A task plan turns a stage into small tasks that a person or an AI agent can build and check one at a time.

A plan decides nothing about the product. Decisions live in the spec and the decision records. A plan only orders the work.

## Where plans sit

The project is planned at three levels. Each level has one home.

| Level | What it holds | Home |
| --- | --- | --- |
| 1. Roadmap | The twelve build stages and their order | [System design](../system-design.md) section 15 |
| 2. Stage outline | For each stage: what is built, which decision records govern it, when it is done | System design sections 15.1 to 15.12, and the [testing strategy](../testing-strategy.md) |
| 3. Task plan | For one stage: milestones and tasks, in order | This folder |

Levels 1 and 2 cover the whole product. Level 3 exists only for the stage being built, and sometimes the next one. A task plan written many stages ahead goes stale, because each stage changes what the next one needs.

## What is in this folder

| File | What it is |
| --- | --- |
| [TEMPLATE.md](TEMPLATE.md) | The form every plan follows. Copy it to start a plan |
| `stage-NN-name.md` | The plan for build stage NN. One file for each stage. `name` is the stage's short name from the table in system design section 15, in kebab case |
| [stage-01-core.md](stage-01-core.md) | The plan for build stage 1, `core` |

List every new plan in the table above when it is added. The status of a plan lives in the plan's own header, not in this table.

## How to read a plan

Every plan starts with a header table. It has five rows: Stage, Status, Branch, Accepted on, and Stage outline (a link to the stage's section in the system design). After the header come nine numbered parts, in the same order every time.

1. **Goal.** One or two sentences: what exists when the stage is done.
2. **Scope.** What this stage builds, and what it leaves to later stages.
3. **Read first.** The sections of the spec, the system design, the testing strategy and the decision records that govern this stage. The plan links to them and does not repeat them.
4. **Checks before starting.** Anything that must be confirmed before the first task, such as an unverified assumption.
5. **Milestones and tasks.** Two to six milestones. Each milestone is a set of tasks that together give one result you can see or test.
6. **Open questions.** Points the docs do not settle. Each one goes to the owner before the task that needs it.
7. **Done when.** The checks that close the stage.
8. **Change log.** Dated notes of every change made to the plan after it was accepted.
9. **Notes for the next stage.** Filled in when the stage is done: what was built, what differs from the outline, what the next stage should know.

**Task ids.** Each task has an id of the form `S1-M2-T3`: stage 1, milestone 2, task 3. Use the id in commit messages and questions.

**A task says:** what to build, which files it touches, which tests are written first, when it is done, which rules shaped it (Constitution rule ids, decision records), and which tasks it depends on ("Depends on").

**Owner tasks.** A task marked "(Owner)" is done by the owner alone. The agent ticks it only after the owner says it is done.

**Status.** A plan is in one of four states.

| Status | Meaning |
| --- | --- |
| Draft | Written, not yet accepted. Do not build from it |
| Accepted | The owner has accepted it. Work may start |
| In progress | At least one task is done |
| Done | Every task is ticked and the "Done when" checks pass |

Only the owner accepts a plan. When the owner says so in words, the agent sets the status to Accepted and fills in "Accepted on", in a commit of its own. The implementer sets In progress with the first ticked task.

## What the owner does

The owner decides. The agent plans and builds. In each stage the owner:

- accepts the Draft plan, in words (the agent records it);
- answers the open questions;
- does the "(Owner)" tasks, such as the expected-answer tables;
- says "go" before each paid run;
- reads golden-file diffs when the agent asks;
- confirms that the stage is Done.

## How to write a plan

### Read before planning

Read these before you write a single task. The plan is built from them, and it must not disagree with any of them.

| Read | What it gives the plan |
| --- | --- |
| [System design](../system-design.md) section 15, the table of stages | The twelve stages and their order, so you know what came before this stage and what comes after |
| System design section 15.N, for the stage you are planning | What the stage builds, which decision records govern it, and when it is done |
| System design sections 15.N+1 onwards, skimmed | What later stages expect this stage to leave ready |
| The other system design sections that section 15.N points to | The shapes, the data flow and the rules the stage must follow. For stage 1 this is section 3.4, the core shapes |
| [Testing strategy](../testing-strategy.md) sections 3 (layers), 4 (this module's row), 10 (expected answers) and 13 (gaps by stage), plus the sections named in the outline's "Tests" line. For stages 9 and 10, also section 7.5 | Which tests the stage needs, and which rules cover expected answers and saved replies |
| The decision records in [`../adr/`](../adr/) that section 15.N names, with every dated amendment | The decisions the stage rests on. An amendment can change the body above it. Check each status line. If one is only proposed, ask the owner before planning on it |
| [The architecture report](../../reports/Clause%20Tracer%20pipeline%20architecture.md) | The research behind the stage. Its stage table and shapes sketch are historical: section 15 wins |
| [Spec](../spec.md): the sections the stage implements, and section 13 | What the app does, says and promises, and what is still open |
| [Constitution](../../Constitution.md) | The binding rules for code. Tasks cite its rule ids |
| [AGENTS.md](../../AGENTS.md) and [GIT_CONVENTIONS.md](../../GIT_CONVENTIONS.md) | The commands, the import rules, and how branches and commits are named |
| The code as it stands: the module's folder and README, `pyproject.toml`, `scripts/check.sh` | The real starting point. A plan starts from what exists, not from what the docs expect |
| The plan of the stage before, and its "Notes for the next stage" | What was learned that changes this stage |

List the ones that govern the stage under "Read first" in the plan, so the person who implements it reads the same things.

### Steps

1. **Plan one stage.** Write the plan for the next stage only when the stage before it is done, or on its last milestone.
2. **Copy [TEMPLATE.md](TEMPLATE.md)** to `stage-NN-name.md` and fill in every part. Keep every part; write "None" where a part is empty.
3. **Start from the stage outline** (system design section 15.N) and the testing strategy sections read above. The plan must cover everything they ask for, and nothing more.
4. **Keep tasks small.** One task is one commit, and at most about half a day of work. If a task needs the word "and" twice, split it.
5. **Give every task a test or a check.** A task with no way to fail is not a task.
6. **Give every promise a test.** If the stage touches a promise made to users, a task must add the test that fails when the promise breaks (Constitution T13).
7. **Order by dependency.** Shapes before the code that uses them. Fakes before the code that is tested with them.
8. **Plan paid runs as owner gates.** Each paid run is a task of its own. It names the step of the spending plan (testing strategy section 7.5) and its planned spend, and depends on the spend-ledger task and on an owner task "Owner says go".
9. **Link, do not repeat.** A decision is stated once, in its home. The plan points to it.
10. **List what the docs do not settle** under "Open questions". Copy every "Not yet decided" point from section 15.N and every open item in Spec section 13 that the stage touches. Do not answer them. When the owner answers, record the decision in its home (the spec, the system design or an amendment to a decision record) in the same change, and put a link to it in the "Owner's answer" column.
11. **Set the status to Draft** and bring the plan to the owner. Add it to the table in this README.

Write in British English, in short plain sentences, as [WRITING_DOCS.md](../../WRITING_DOCS.md) asks.

### Before you hand it over

Check each line. Fix the plan until all are true.

- [ ] Every "Builds" item and every "Done when" item of section 15.N maps to a task or a check.
- [ ] Every testing strategy section named in the outline's "Tests" line maps to a task.
- [ ] Every "Not yet decided" point is an open question.
- [ ] Every expected-answer table is an owner task.
- [ ] Task ids are unique.
- [ ] Every link resolves.

If two docs disagree, do not choose. List it as an open question.

## How to implement a plan

### Steps

1. **Check the status.** Build only from a plan that is Accepted or In progress.
2. **Read first.** Read the plan's "Read first" list, [AGENTS.md](../../AGENTS.md) and the [Constitution](../../Constitution.md).
3. **Do the checks before starting.** If one fails, stop and bring it to the owner.
4. **Take one task at a time, in the listed order.** Do not work on two at once. If a task waits on the owner, go on to the next task that does not depend on it.
5. **Write the tests first.** Use fakes and saved replies. Unit tests need no network, no key and no cost. See each new test fail for the right reason before you write the code.
6. **Run `scripts/check.sh`.** A task is not done until it passes. Never skip, disable or loosen a check or a test to make it pass. If it fails for a reason outside your task, stop and tell the owner; fix it in a commit of its own.
7. **Tick the task in the same commit as its code.** Put the task id in the commit message. Follow [GIT_CONVENTIONS.md](../../GIT_CONVENTIONS.md).
8. **Update the module's README** when a shape changes, in the same change (Constitution S3).
9. **Leave expected answers to the owner.** Never write or edit the expected values of an acceptance table (testing strategy section 10). Write the loader and the test, then stop at the owner task. Regenerate golden files only with `--update-goldens`, in a commit of their own, and ask the owner to read the diff (Constitution T11).
10. **Stop at an open question.** Ask the owner. Do not pick an answer.
11. **Never start a paid AI run without asking**, and never without the spend cap in place (testing strategy section 7.5).
12. **Keep tasks small.** If a task proves bigger than half a day, split it in the plan and note it in the change log.

### When the plan is wrong

Do not work around it quietly. Stop and change the plan. You may do these alone: split a task, reorder tasks, correct a file path, add a task. Ask the owner first for anything else: a change to Scope or "Done when", removing a task or a test, an owner task, a paid run, or anything that touches the spec, the system design, the testing strategy or a decision record. Either way, add a dated line to the change log saying what changed and why.

### When the stage is done

Run the "Done when" checks. Write "Notes for the next stage" in the plan: what was built, what differs from the outline, what the next stage should know. Update every line that states the project's status: [AGENTS.md](../../AGENTS.md) "Where the project stands", the status line in [README.md](../../README.md), and [testing strategy](../testing-strategy.md) section 13. Set the status to Done, then tell the owner.
