# Scenario: review-checkpoint-shadow-advisory-overall

Demonstrates F4's end-to-end behavior at the top level: when the
redline policy is in **shadow mode** and the *only* failing predicate
is `review.checkpoints_satisfied`, the overall verdict flips to
**advisory** (`exit_code: 1`, `status: advisory`) instead of blocking.

Diff: a gray-zone application change to `WalletService.java`. The
agent declared Risk=Elevated honestly, so `risk.declared_not_below_detected`
passes. Redline triggered the `architecture-review` checkpoint with
`satisfied: false` — no CODEOWNER approval / label yet. Because the
verdict carries `modes.default: shadow`, the `review.checkpoints_satisfied`
predicate surfaces the finding with `blocking: false` and the detail
appends `[shadow — advisory]`. With no other blocking failure, the
overall verdict aggregates to advisory.

Companion to `review-checkpoint-unsatisfied-shadow`, which exercises
the predicate's disposition in isolation (alongside an unrelated
blocking failure). This fixture pins the calibration-window
end-to-end behavior the docs (README.md / INTEGRATION.md /
REDLINE.md) promise: during shadow mode, CI does not block on
unmet checkpoints.
