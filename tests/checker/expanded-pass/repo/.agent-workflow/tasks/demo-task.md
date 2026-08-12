<!-- agent-workflow:start -->
**Outcome:** Concurrent wallet-creation requests across multiple service instances produce at most one wallet per tenant-scoped request identifier, with state surviving restarts.

**Target:** wallet-service.

**Scope:** Wallet creation flow + new tenant-scoped idempotency table + the regression tests covering concurrency and restart.

**Constraints:** Public API unchanged. Tenant isolation MUST remain intact. No breaking schema migration; the new table is additive.

**Completion criteria:** Concurrent retries produce a single wallet, asserted by a regression test. The new table's row count matches the count of distinct tenant-scoped request identifiers. A service restart between two retries still produces a single wallet.

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Persistence semantics + multi-tenancy isolation are both Elevated triggers per DEFAULT_PROFILE §3. Touches HTTP handler + idempotency layer + persistence mapper + regression suite (Moderate complexity).

**Discovery:** No tenant-scoped idempotency key currently exists. The existing retry utility is in-memory only and does not survive restarts. Concurrent retry coverage is missing from the wallet-service test suite.

**Material assumptions:** The request identifier passed by callers is stable across retries — disproved if retry requests are observed with different identifiers in the wallet-service ingress logs; action if disproved: stop and return to planning.

**Plan:** Add a `wallet_requests` table keyed on `(tenant_id, request_identifier)`. Handler queries the table; on hit returns existing wallet, on miss inserts wallet + dedup row in one transaction.

**Verification plan:** Concurrent-retry behaviour → `WalletConcurrentRetryTest`. Row-count assertion → inside that test. Restart between retries → `WalletRestartIdempotencyTest`. Tenant isolation → existing `WalletTenantIsolationTest` re-run.

**Plan review:** Clean-context agent review (Elevated path).

**Approvals:** Not required at Elevated risk level.

**State:** Ready for review
<!-- agent-workflow:end -->
