# Scenario: review-checkpoint-satisfied

Redline reports a triggered `persistence-review` checkpoint that is
already `satisfied: true` (the PR carries a CODEOWNER approval).
`review.checkpoints_satisfied` predicate passes. Overall verdict clean
(redline's High classification matches the declared Risk).
