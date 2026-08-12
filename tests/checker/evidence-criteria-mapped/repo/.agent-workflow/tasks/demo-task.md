<!-- agent-workflow:start -->
**Outcome:** Concurrent retries against the wallet creation endpoint produce a single wallet.

**Target:** demo-service.

**Scope:** Wallet creation retry path and its tests.

**Constraints:** Public API unchanged.

**Completion criteria:** Concurrent retries observably create one wallet; no regression in single-call wallet creation.

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Concurrency-sensitive path.

**Discovery:** No persisted idempotency key exists; concurrent retry coverage missing.

**Material assumptions:** Request identifier stable across retries.

**Plan:** Persist a tenant-scoped idempotency key; enforce uniqueness by tenant and request id.

**Verification plan:**
- Concurrent retries create one wallet → WalletConcurrentRetryTest
- Tenant isolation remains intact → CrossTenantAuthTest
- Single-call regression → existing WalletCreationTest

**Plan review:** clean-context session 2026-06-24/concurrency-review

**Approvals:** —

**State:** Ready for review.
<!-- agent-workflow:end -->
