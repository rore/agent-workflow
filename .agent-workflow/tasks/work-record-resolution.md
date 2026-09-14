<!-- agent-workflow:start -->
**Outcome:** Agent Workflow provides one authoritative, optional way to resolve the current Work Record, and its guidance preserves supplied source and Work Record identity across pickup, handoff, and completion.

**Target:** agent-workflow

**Scope:** Normative workflow contract, existing checker/runtime entry point, agent-workflow skill guidance, focused tests, and regenerated distribution artifacts.

**Constraints:** Reuse existing config and Work Record parsing; no orchestration layer, mandatory Pallium/Minimap dependency, duplicate identity algorithm, new reference family, migration of persisted identities, or artificial Work Record for exempt tasks.

**Completion criteria:** A consumer can resolve the authoritative current Work Record for custom taskPath, resumed/renamed/detached/worktree contexts with explicit found/absent/error results; pickup and handoff guidance preserves valid supplied identity and actual merge/release semantics; existing independent use remains unchanged.

**Risk:** High

**Complexity:** Moderate

**Reason:** The intended normative spec and resolver contract are red-zone cross-install surfaces requiring architecture review. Moderate complexity spans contract, runtime, guidance, tests, and generated distribution without crossing repository boundaries.

**Discovery:** `core.config.load` validates `workRecord.local.taskPath`; `LocalBackend.resolve_location/read` already own path and record resolution; the checker reuses both, but branch-to-slug selection exists only in `core/skill/operating-mode.md`. The vendored checker is rebuilt from this source. Existing Pallium identity is `agent-workflow:<slug>`; cross-repo confirmation is pending.

**Material assumptions:** The existing `agent-workflow:<slug>` identity remains authoritative and needs no migration; Pallium contract feedback disproving its format or conflict semantics returns the task to planning. Resolver invocation is event-scoped, not per-turn; a consumer requirement for hot-path calls requires performance evidence and re-planning.

**Plan:** Proposed: specify one additive read-only resolver mode; implement it in the existing checker using the config loader, LocalBackend, and one shared branch-to-slug helper; cover found/absent/error and supplied-identity conflicts; tighten pickup/handoff/completion guidance without new fields; append the design decision; regenerate dist/local installs. Stop on cross-repo contract disagreement, incompatible persisted identity, or required new parser/dependency. Implementation is blocked pending cross-repo and clean-context plan review plus human approval.

**Verification plan:** Custom taskPath, current/resumed record, absent/exempt record, renamed/detached branch, worktrees, malformed/missing config, invalid/conflicting supplied identity, malformed record, and optional-tool absence semantics → focused checker CLI tests. Pickup/handoff/completion rules → skill-reference/budget tests plus clean-context review. Generated install parity → package checks and local reinstall. Whole change → local checker with fresh Redline verdict and `bash tests/run-all.sh`.

**Plan review:** Pending clean-context review.

**Approvals:** Pending human approval.

**Exceptions:** —

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- Established isolated branch `feat/work-record-resolution`; applicability did not exempt contract and skill changes.
- Pre-edit classification: RED contract surface, High risk, Moderate complexity; no boundary rule applies.
- Discovery identified existing config/backend authority and no executable branch-to-slug resolver; sent contract proposal through Relay as `relay-msg-ae157aa307d348b4bc5fcb42242f5209` and to both coordinating tasks.

## Evidence

- Pending.

## Result review

- Pending.
