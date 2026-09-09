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

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

Branch: `feat/budget-locale-determinism`.

Revision: `a2af7d0` replaces the named-locale `wc -w` call with `awk` field counting and updates the manifest comment.

Evidence:

- `LC_ALL=C` and `LC_ALL=C.UTF-8` budget runs produced identical counts; all 19 files passed.
- Independent review confirmed every budgeted file matches UTF-8 `wc -w`; `C` and `C.UTF-8` runs are identical.
- All nine repository test layers passed: 257 Python tests, budget, redline, tuner fixtures, hooks, links, and package/bootstrap E2E.
- `git diff --check` passed.
- High-reasoning independent review approved with no actionable findings.
