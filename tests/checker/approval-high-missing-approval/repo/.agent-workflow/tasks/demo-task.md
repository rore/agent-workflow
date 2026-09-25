<!-- agent-workflow:start -->
**Outcome:** Migrate the tenant-isolation column to the new schema.

**Target:** demo-service.

**Scope:** Flyway migration plus repository tests.

**Constraints:** Zero downtime.

**Completion criteria:** All tenants migrated.

**Requirement baseline:** {"source":"test-fixture-initial","outcome":"Migrate the tenant-isolation column to the new schema.","scope":"Flyway migration plus repository tests.","constraints":"Zero downtime.","completion_criteria":"All tenants migrated."}

**Risk:** High

**Complexity:** Moderate

**Reason:** Destructive migration.

**Discovery:** Reviewed current migration approach.

**Material assumptions:** None material.

**Plan:** Apply the schema change.

**Verification plan:** Per-tenant migration replay.

**Plan review:** Agent technical review: fixture/session-plan

**Approvals:** —

**State:** Ready for review.
<!-- agent-workflow:end -->

## Result review
Agent technical review: fixture/session-result
Reviewed revision: abc1234
Verification adequacy: fixture checks cover the completion criteria.
