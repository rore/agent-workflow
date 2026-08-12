# Expanded fixture — elevated/moderate wallet idempotency

> Test fixture for the parser. Populated expanded-shape Work Record used
> by `tests/work-record/test_parser.py` to verify the expanded-path
> round-trip.

This fixture continues the wallet idempotency theme established in the
routine-pass fixture. The work is
elevated/moderate because it requires a tenant-scoped persisted
idempotency table — a sensitive surface per `docs/DEFAULT_PROFILE.md` §3
(persistence + multi-tenancy) — and stretches across more than one
component.

<!-- agent-workflow:start -->
**Outcome:** Concurrent wallet-creation requests across multiple service instances produce at most one wallet for a given tenant-scoped request identifier, with the de-duplication state surviving service restarts.

**Target:** wallet-service.

**Scope:** Wallet creation flow, the new tenant-scoped idempotency table, the persistence-mapper layer, and the regression tests covering concurrency and restart.

**Constraints:** Public API unchanged. Tenant isolation MUST remain intact — the idempotency key is scoped per tenant. No breaking schema migration; the new table is purely additive. No change to the response shape on hit/miss.

**Completion criteria:** Concurrent retries against the wallet creation endpoint produce a single wallet, observable via a regression test. The new table's row count matches the count of distinct tenant-scoped request identifiers. A service restart between two retries still produces a single wallet.

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Persistence semantics + multi-tenancy isolation are both Elevated triggers per DEFAULT_PROFILE §3. The change touches multiple components (HTTP handler, idempotency layer, persistence mapper, regression suite) which makes it Moderate complexity.

**Discovery:** No tenant-scoped idempotency key currently exists. The existing retry utility is in-memory only and does not survive restarts. Concurrent retry coverage is missing from the wallet-service test suite. The request identifier passed by callers appears stable across retries (assumption captured below).

**Material assumptions:** The request identifier passed by callers is stable across retries — disproved if retry requests are observed with different identifiers in the wallet-service ingress logs; action if disproved: stop and return to planning, the design depends on a stable identifier and would need a different idempotency key strategy.

**Plan:** Add a `wallet_requests` table keyed on `(tenant_id, request_identifier)`. The wallet creation handler queries this table first; on hit it returns the existing wallet; on miss it inserts both the wallet and the dedup row in one transaction. Add concurrent-retry regression tests against a Testcontainers-backed Postgres. No deviation from the standard persistence-mapper pattern.

**Verification plan:** Completion criterion "concurrent retries produce a single wallet" verified by a new concurrency regression test (`WalletConcurrentRetryTest`). Completion criterion "row count matches distinct identifiers" verified by an assertion inside that test. Completion criterion "restart between retries" verified by a restart-tolerant test (`WalletRestartIdempotencyTest`). Tenant isolation regression covered by the existing `WalletTenantIsolationTest` re-run.

**Plan review:** Clean-context agent review (Elevated path).

**Approvals:** Not required at Elevated risk level.

**State:** Ready to implement
<!-- agent-workflow:end -->

## Implementation

(Out of scope for the fixture — this is a parser fixture, not a real PR.)

## Evidence

(Out of scope for the fixture.)
