<!-- agent-workflow:start -->
**Outcome:** Refactor of the public API contract response shape.

**Target:** demo-service public API v1.

**Scope:** PublicApiV1 controller plus its tests.

**Constraints:** Backwards-compatible field addition only.

**Completion criteria:** Existing OpenAPI conformance tests stay green; new field appears in the response.

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Touches the public API contract surface — redline flags red-zone. Agent declared Elevated; redline detects minimum High. Mismatch waived for this PR per the recorded exception below.

**Discovery:** PublicApiV1 controller, OpenAPI spec, contract tests.

**Material assumptions:** Field addition is consumed by clients defensively. Disproving evidence: a client breaks. Action if disproved: roll back; re-classify as High and reopen plan.

**Plan:** Add the optional field; update OpenAPI; add a regression test.

**Verification plan:** OpenAPI conformance test + contract round-trip test.

**Plan review:** clean-context review on the contract change.

**Approvals:** —

**Exceptions:**
- rule: risk.declared_not_below_detected
  reason: backwards-compatible field addition only; clients ignore unknown fields
  scope: this PR only
  approver: I123456
  expiry: 2099-12-31
  compensating_validation: clean-context contract review + OpenAPI conformance test

**State:** Ready for review.
<!-- agent-workflow:end -->
