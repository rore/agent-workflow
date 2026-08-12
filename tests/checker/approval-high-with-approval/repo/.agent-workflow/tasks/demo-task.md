<!-- agent-workflow:start -->
**Outcome:** Migrate the tenant-isolation column to the new schema.

**Target:** demo-service.

**Scope:** Flyway migration plus repository tests.

**Constraints:** Zero downtime; rollback path documented.

**Completion criteria:** All tenants migrated; tests cover both old- and new-schema reads during cutover.

**Risk:** High

**Complexity:** Moderate

**Reason:** Destructive migration on a tenant-isolation column — High per DEFAULT_PROFILE §3.

**Discovery:** Reviewed current migration approach and tenant-isolation invariants.

**Material assumptions:** No tenant currently relies on the old column's exact type.

**Plan:** Apply the schema change in two steps with a fallback flag.

**Verification plan:** Per-tenant migration replay plus the existing isolation test.

**Plan review:** clean-context session 2026-06-24/cc-7 confirmed the rollout plan.

**Approvals:** Approved by user 2026-06-24T15:30Z: "approved, proceed with the two-step plan"

**State:** Ready for review.
<!-- agent-workflow:end -->
