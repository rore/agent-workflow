<!-- agent-workflow:start -->
**Outcome:** OrderService receives a small refactor.

**Target:** demo-service.

**Scope:** `src/main/java/com/example/orders/application/OrderService.java`.

**Constraints:** Public API unchanged.

**Completion criteria:** Existing tests stay green; refactor passes review.

**Risk:** Elevated

**Complexity:** Simple

**Reason:** Touches an application-tier file that gray-zone classifies.

**Discovery:** No new dependencies expected.

**Material assumptions:** Refactor does not cross architectural boundaries — would be disproved by an ArchUnit failure; action if disproved: stop and re-plan.

**Plan:** Extract the order-validation logic to a private helper. Keep imports inside the application tier.

**Verification plan:** Unit tests for OrderService; ArchUnit boundary tests.

**Plan review:** Self-review.

**Approvals:** Not required at Elevated risk level.

**State:** Ready for review
<!-- agent-workflow:end -->
