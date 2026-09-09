<!-- agent-workflow:start -->
**Outcome:** Budget checks produce the same word/token count locally and in CI without requiring a named locale.

**Target:** `tests/budget/check-budget.sh` and its manifest documentation.

**Scope:** Replace locale-sensitive word counting with locale-independent standard-tool counting; update the explanatory comment. No ceiling changes.

**Constraints:** Preserve the existing `ceil(words * 1.33)` estimator, manifest format, CLI, and exit codes.

**Completion criteria:** The checker no longer depends on `en_US.UTF-8`; counts match UTF-8 `wc -w` for current budgeted files; the budget layer and full suite pass locally and in CI.

**Risk:** Routine

**Complexity:** Simple

**Reason:** Focused test-tool portability fix with no shipped workflow or runtime behavior change.

**Approach:** Count whitespace-delimited fields with `awk`, which matches the intended UTF-8 counts for repository Markdown and avoids locale selection entirely.

**Verification:** Compare `awk` with `LC_ALL=C.UTF-8 wc -w`, run budget tests under multiple `LC_ALL` values, then run `bash tests/run-all.sh` and PR CI.

**State:** Ready to implement
<!-- agent-workflow:end -->

## Implementation

Branch: `feat/budget-locale-determinism`. Planned files: `tests/budget/check-budget.sh`, `tests/budget/budget.yaml`, and this Work Record.
