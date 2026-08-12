# Scenario: multi-record-two-pass

Two valid routine Work Records changed in one PR. Both pass the predicate
set; overall verdict is clean. Exercises the slice 0 multi-record path.

The test harness invokes `run_checker_multi(repo, ["task-alpha", "task-bravo"])`
and expects a verdict whose `records` carries both, in input order, each
clean.

Redline is `optional` in this fixture so the redline predicates produce
one advisory per record (missing verdict file). The overall verdict
remains advisory, not blocking.
