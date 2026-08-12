<!-- agent-workflow:start -->
**Outcome:** Safe blue-zone refactor.

**Target:** demo-service.

**Scope:** Internal utility class plus its tests.

**Constraints:** —

**Completion criteria:** Existing tests stay green.

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Pinned Elevated despite blue-zone redline finding — agent judges the refactor wider than redline detects. (This fixture exercises the exception-against-boundary path; the elevated declaration is incidental.)

**Discovery:** Reviewed callers; no surprises.

**Material assumptions:** None.

**Plan:** Extract helper; update call sites.

**Verification plan:** Existing unit suite.

**Plan review:** clean-context review.

**Approvals:** —

**Exceptions:**
- rule: risk.boundary_violation_absent
  reason: trying to waive a boundary-violation predicate — should be rejected
  scope: this PR only
  approver: I123456
  expiry: 2099-12-31
  compensating_validation: none — this exception is intentionally invalid

**State:** Ready for review.
<!-- agent-workflow:end -->
