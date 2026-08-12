<!-- agent-workflow:start -->
**Outcome:** Idempotency check.

**Target:** wallet-service.

**Scope:** Wallet retry path.

**Constraints:** Public API unchanged.

**Completion criteria:** Concurrent retries produce a single wallet.

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Persistence semantics.

**Material assumptions:** Request identifier is stable across retries.

**Plan:** Add tenant-scoped idempotency table.

**Verification plan:** WalletConcurrentRetryTest plus a restart-tolerance test.

**Plan review:** Clean-context agent review.

**Approvals:** —

**State:** Ready to implement
<!-- agent-workflow:end -->
