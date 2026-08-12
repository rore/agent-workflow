<!-- agent-workflow:start -->
**Outcome:** Schema migration adds a new column to the wallets table.

**Target:** demo-service.

**Scope:** Persistence layer; Flyway migration.

**Constraints:** Backward-compatible column add.

**Completion criteria:** Migration applies cleanly on existing data; existing tests pass.

**Risk:** Elevated

**Complexity:** Simple

**Reason:** Persistence schema change.

**Discovery:** Reviewed migration history; no conflicts.

**Material assumptions:** Column add is backward-compatible.

**Plan:** Add Flyway V42__add_segment.sql; update WalletEntity.

**Verification plan:**
- Migration applies cleanly → MigrationApplyIT
- Backward compat → existing wallet-service CI

**Plan review:** clean-context session 2026-06-24/schema-migration

**Approvals:** —

**State:** Ready for review.
<!-- agent-workflow:end -->
