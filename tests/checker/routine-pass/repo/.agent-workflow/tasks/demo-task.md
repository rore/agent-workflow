<!-- agent-workflow:start -->
**Outcome:** Concurrent retries against the wallet creation endpoint produce a single wallet.

**Target:** wallet-service.

**Scope:** Wallet creation retry path; its regression tests.

**Constraints:** Public API unchanged. Tenant isolation unchanged.

**Completion criteria:** Regression test asserts single-wallet behaviour under simulated concurrent retries; wallet-service CI stays green.

**Risk:** Routine

**Complexity:** Simple

**Reason:** Localised, reversible

**Approach:** Reuse the existing retry utility plus an idempotency check keyed on the request identifier.

**Verification:** New regression test plus the required wallet-service CI job.

**State:** Ready for review.
<!-- agent-workflow:end -->
