# Walking-skeleton routine fixture

> This is a hand-authored Work Record used as a test fixture for the
> Step 1 parser. The marker-bounded block below is what the parser
> consumes. Prose above and below the markers is human notes and must
> not affect parsing.

This fixture exercises the routine fast-path: all nine routine fields
populated with realistic content, single block, no expanded-path fields.

<!-- agent-workflow:start -->
**Outcome:** Concurrent retries against the wallet creation endpoint produce a single wallet, not multiple.

**Target:** wallet-service.

**Scope:** Wallet creation retry path; its existing regression test suite.

**Constraints:** Public API unchanged. Tenant isolation unchanged. No schema migrations.

**Completion criteria:** A new regression test asserts single-wallet behaviour under simulated concurrent retries; the existing wallet-service CI job stays green.

**Risk:** Routine

**Complexity:** Simple

**Reason:** Localised change inside one service; no sensitive path; reversible

**Approach:** Reuse the existing retry utility and add an idempotency check keyed on the request identifier. Add the regression test alongside.

**Verification:** New regression test plus the required `wallet-service` CI job. CI is authoritative.

**State:** Ready for review.
<!-- agent-workflow:end -->

Trailing prose. The parser must ignore everything outside the marker pair.
