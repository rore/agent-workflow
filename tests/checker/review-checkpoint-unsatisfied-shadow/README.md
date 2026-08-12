# Scenario: review-checkpoint-unsatisfied-shadow

Same diff as `review-checkpoint-unsatisfied` (red-zone persistence
change with an unsatisfied `persistence-review` checkpoint), but the
redline verdict carries `modes.default: shadow` and `perCheck.report`
not pinned to binding. Demonstrates that `review.checkpoints_satisfied`
surfaces the finding as **advisory** (`blocking: false`) instead of
blocking, matching the reporter's own `exitCode: 1` /
`recommendedAction: review-shadow-warnings` disposition during the
calibration window. Boundary-violation predicate remains blocking
because its own hardcoded default keeps it binding regardless of
`modes.default`. Risk-mismatch (`risk.declared_not_below_detected`)
stays blocking in this fixture as well — F4 scope is the result-review
checkpoint signal, not the agent's own classification declaration.

