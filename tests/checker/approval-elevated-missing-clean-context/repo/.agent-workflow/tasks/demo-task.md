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

**Plan review:** self

**Approvals:** —

**State:** Ready for review.
<!-- agent-workflow:end -->
