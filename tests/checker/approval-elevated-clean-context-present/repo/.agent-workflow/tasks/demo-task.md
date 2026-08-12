<!-- agent-workflow:start -->
**Outcome:** Add a new HTTP endpoint to the wallet API.

**Target:** demo-service.

**Scope:** WalletController plus its tests.

**Constraints:** Backwards-compatible.

**Completion criteria:** New GET endpoint returns the wallet by id.

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Touches the public API surface.

**Discovery:** Reviewed existing handlers and controller patterns.

**Material assumptions:** None material.

**Plan:** Add the controller method; wire to existing handler.

**Verification plan:** Existing API conformance suite plus a new controller test.

**Plan review:** clean-context session 2026-06-24/abc-123 — review confirmed the change is non-breaking and well-scoped.

**Approvals:** —

**State:** Ready for review.
<!-- agent-workflow:end -->
