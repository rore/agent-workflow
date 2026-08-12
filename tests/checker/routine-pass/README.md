# routine-pass — checker fixture

Self-contained repository fixture: an `agent-workflow.yaml` plus a
populated routine Work Record under `.agent-workflow/tasks/`. The
checker is pointed at this directory's `repo/` subdir; every
predicate should pass and the verdict should be `clean` with exit 0.
