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

**Plan review:** clean-context session 2026-06-24/missing-approval-fixture

**Approvals:** —

**State:** Ready for review.
<!-- agent-workflow:end -->
