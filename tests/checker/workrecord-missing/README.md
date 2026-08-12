# workrecord-missing — checker fixture

Repo has `agent-workflow.yaml` but no `.agent-workflow/tasks/demo-task.md`.
The `workrecord.exists` predicate fails. The other predicates downstream
short-circuit (they cannot meaningfully evaluate without a Work Record)
and report `passed: false` with a "skipped" detail so the verdict
explains the cascade rather than reporting four independent failures.
