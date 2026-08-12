<!-- agent-workflow:start -->
**Outcome:** Small refactor.

**Target:** demo-service.

**Scope:** Wallet retry helper.

**Constraints:** No API change.

**Completion criteria:** Retry test passes.

**Risk:** Routine

**Complexity:** Simple

**Reason:** Localised.

**Approach:** Inline a private helper.

**Verification:** WalletRetryTest.

**State:** Ready for review.
<!-- agent-workflow:end -->

## Evidence

First run: WalletRetryTest ❌ FAILED with an unrelated flaky assertion.
After investigation: WalletRetryTest ✅ passed on the second attempt.
