# Scenario: review-checkpoint-unsatisfied

Redline reports a triggered `persistence-review` checkpoint with
`satisfied: false` — no CODEOWNER approval on the PR yet. The
`review.checkpoints_satisfied` predicate blocks. Closes SPEC §9.7
result-review enforcement at the harness level: red-zone changes
cannot merge without their required PR-side review.
