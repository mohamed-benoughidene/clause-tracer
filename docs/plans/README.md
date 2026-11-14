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
| `stage-NN-name.md` | The plan for build stage NN. One file for each stage |
| [stage-01-core.md](stage-01-core.md) | The plan for build stage 1, `core` (Draft) |

List every new plan in the table above when it is added.

## How to read a plan

Every plan has the same parts, in the same order.

1. **Header.** The stage, the status, the branch, and the date the owner accepted it.
2. **Goal.** One or two sentences: what exists when the stage is done.
3. **Scope.** What this stage builds, and what it leaves to later stages.
4. **Read first.** The sections of the spec, the system design, the testing strategy and the decision records that govern this stage. The plan links to them and does not repeat them.
5. **Checks before starting.** Anything that must be confirmed before the first task, such as an unverified assumption.
6. **Milestones and tasks.** Three to six milestones. Each milestone is a set of tasks that together give one result you can see or test.
7. **Open questions.** Points the docs do not settle. Each one goes to the owner before the task that needs it.
8. **Done when.** The checks that close the stage.
9. **Change log.** Dated notes of every change made to the plan after it was accepted.

**Task ids.** Each task has an id of the form `S1-M2-T3`: stage 1, milestone 2, task 3. Use the id in commit messages and questions.

**A task says:** what to build, which files it touches, which tests are written first, when it is done, and which rules shaped it (Constitution rule ids, decision records).

**Status.** A plan is in one of four states.

| Status | Meaning |
| --- | --- |
| Draft | Written, not yet accepted. Do not build from it |
| Accepted | The owner has accepted it. Work may start |
| In progress | At least one task is done |
| Done | Every task is ticked and the "Done when" checks pass |

Only the owner moves a plan from Draft to Accepted.

## How to implement a plan

1. **Check the status.** Build only from a plan that is Accepted or In progress.
2. **Read first.** Read the plan's "Read first" list, [AGENTS.md](../../AGENTS.md) and the [Constitution](../../Constitution.md).
3. **Do the checks before starting.** If one fails, stop and bring it to the owner.
4. **Take one task at a time, in order.** Do not start a task before the tasks it depends on are ticked.
5. **Write the tests first.** Use fakes and saved replies. Unit tests need no network, no key and no cost.
6. **Run `scripts/check.sh`.** A task is not done until it passes.
7. **Tick the task in the same commit as its code.** Put the task id in the commit message. Follow [GIT_CONVENTIONS.md](../../GIT_CONVENTIONS.md).
8. **Update the module's README** when a shape changes, in the same change (Constitution S3).
9. **Leave expected answers to the owner.** Do not change code and the expected values of its acceptance tests in one step (Constitution T11).
10. **Stop at an open question.** Ask the owner. Do not pick an answer.
11. **Never start a paid AI run without asking**, and never without the spend cap in place (testing strategy section 7.5).

**When the plan is wrong.** Do not work around it quietly. Stop, change the plan, and add a dated line to its change log saying what changed and why. If the change touches a decision record or the spec, ask the owner first.

**When the stage is done.** Run the "Done when" checks, set the status to Done, and tell the owner what was built and what was learned that the next stage should know.

## How to write a plan

1. **Plan one stage.** Write the plan for the next stage only when the stage before it is done, or nearly done.
2. **Copy [TEMPLATE.md](TEMPLATE.md)** to `stage-NN-name.md` and fill in every part. Keep every part; write "None" where a part is empty.
3. **Start from the stage outline** in the system design section 15, and the stage's rows in the testing strategy. The plan must cover everything they ask for, and nothing more.
4. **Keep tasks small.** One task is one commit, and at most about half a day of work. If a task needs the word "and" twice, split it.
5. **Give every task a test or a check.** A task with no way to fail is not a task.
6. **Give every promise a test.** If the stage touches a promise made to users, a task must add the test that fails when the promise breaks (Constitution T13).
7. **Order by dependency.** Shapes before the code that uses them. Fakes before the code that is tested with them.
8. **Link, do not repeat.** A decision is stated once, in its home. The plan points to it.
9. **List what the docs do not settle** under "Open questions". Do not answer them in the plan.
10. **Set the status to Draft** and bring the plan to the owner. Add it to the table in this README.

Write in British English, in short plain sentences, as [WRITING_DOCS.md](../../WRITING_DOCS.md) asks.
