<!-- agent-workflow:start -->
**Outcome:** Migrate the tenant-isolation column to the new schema.

**Target:** demo-service.

**Scope:** Flyway migration plus repository tests.

**Constraints:** Zero downtime.

**Completion criteria:** All tenants migrated.

**Risk:** High

**Complexity:** Moderate

**Reason:** Destructive migration.

**Discovery:** Reviewed current migration approach.

**Material assumptions:** None material.

**Plan:** Apply the schema change.

**Verification plan:** Per-tenant migration replay.

**Plan review:** Approved by user 2026-06-24T15:30Z: "approved"

**Approvals:** approved by user 2026-06-24T15:30Z:  "approved"

**State:** Ready for review.
<!-- agent-workflow:end -->
