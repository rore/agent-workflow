# expanded-pass — checker fixture

Self-contained repository fixture: an `agent-workflow.yaml` plus a
populated expanded Work Record at `(Elevated, Moderate)`. Every
predicate should pass — including the new shape-aware predicates from
slice A — and the verdict should be `clean` with exit 0. The
`workrecord.expanded_fields_present` predicate fires (not
`workrecord.routine_fields_present`).
