# Work Record task ownership

<!-- agent-workflow:start -->
**Outcome:** Each Work Record identifies one accountable task and implementation line, with distinct records for independent parallel deliveries and preserved identity for assistance and handoffs.

**Target:** agent-workflow

**Scope:** Clarify existing task ownership and assignment identity guidance in SPEC and operating-mode; update the decision log and generated repository-local skill mirrors.

**Constraints:** Reuse existing canonical identity and decomposition rules. No mandatory parent record, one-worktree rule, helper branch requirement, schema, checker, registry, new gate, retrospective record split or live installation change. Preserve supplied identity for the same task and legitimate manager-owned shared work. Keep private approval provenance local.

**Completion criteria:** Independent parallel delivery tasks use distinct linked Work Records; bounded assistance, manager-owned shared tasks and replacement checkouts retain one task identity; required reviews, instruction budgets, package parity and repository checks pass.

**Requirement baseline:**
{"source":"direct-user-approved-task-ownership-clarification","outcome":"Each Work Record identifies one accountable task and implementation line, with distinct records for independent parallel deliveries and preserved identity for assistance and handoffs.","scope":"Clarify existing task ownership and assignment identity guidance in SPEC and operating-mode; update the decision log and generated repository-local skill mirrors.","constraints":"Reuse existing canonical identity and decomposition rules. No mandatory parent record, one-worktree rule, helper branch requirement, schema, checker, registry, new gate, retrospective record split or live installation change. Preserve supplied identity for the same task and legitimate manager-owned shared work. Keep private approval provenance local.","completion_criteria":"Independent parallel delivery tasks use distinct linked Work Records; bounded assistance, manager-owned shared tasks and replacement checkouts retain one task identity; required reviews, instruction budgets, package parity and repository checks pass."}

**Relationships:**
{"schema_version":1,"sources":null,"pull_requests":[]}

**Risk:** High

**Complexity:** Simple

**Reason:** SPEC is the normative contract in the architecture-review red zone; operating guidance affects every supported agent. One bounded prose clarification uses existing workflow concepts.

**Discovery:** SPEC sections 6, 8.2 and 10 already define canonical identity, decomposition and optional parent records. Operating-mode Step 2 unconditionally reuses supplied identity, while Delegating to subagents unconditionally inherits the record; neither distinguishes independent delivery from assistance. Clarify those decision points only. CONTRIBUTING requires deletion-test discipline and existing 1900-token operating-mode ceiling; baseline budget check passes all 23 files with operating-mode exactly at ceiling. Existing whole-suite, links and package tests cover instruction packaging; scenario review supplies semantic verification. No exact external feature reference was provided.

**Material assumptions:** Assignment concerns future task identity, not retrospective repair of other active work. If a new ownership or enforcement mechanism is needed, return to planning before expanding scope.

**Plan:** First clarify SPEC section 6: one accountable owner and authoritative implementation line per task at a time; independently implemented/reviewed parallel delivery tasks get distinct records linked to the same existing feature or parent, with no mandatory parent. Preserve one task identity for bounded assistance, manager-owned shared tasks, handoffs, replacement checkouts and ordinary Git copies. Reconcile conflicting supplied identity with the assigner before starting an independent delivery; do not invent a competing record. Then update operating-mode Step 2 and delegation wording to apply that distinction, compacting only the same identity/delegation instructions to stay under the unchanged ceiling. Reuse sections 8.2 and 10 rather than duplicating decomposition. Append one rationale decision, regenerate dist and isolated repository skill mirrors. Stop on changed responsibility/enforcement scope or unresolved assignment conflict. Required independent technical plan/result reviews and separate final human result review remain in force.

**Verification plan:** Independent scenario review: two independently delivered parallel tasks; bounded research/review/implementation helpers; manager-owned shared task; same-task supplied identity on another branch or replacement checkout; handoff; ordinary Git copies; conflicting supplied identity for a new delivery; absent feature/parent; authoritative existing feature link. Check no schema/checker/gate/runtime/config changes and no privacy disclosures. Run existing instruction budgets, links/package parity and the required full tests/run-all.sh once before pushing; run local checker after each State change with actual Redline verdict. Do not add tests that merely match prose or increase ceilings.

**Plan review:** Pending independent technical review.

**Approvals:** Approved by user 2026-10-31: "ok, so make sure we update what is needed" for the presented bounded task-ownership rule. Exact approval provenance is retained privately. Separate final-result review remains pending.

**Exceptions:** None.

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- Established context and immutable baseline before implementation planning. Focused discovery and bounded plan are complete; blocked only on independent technical plan review. Supplied human approval covers the presented rule; no new implementation approval requested.

## Evidence

- Initial base: 00cf3a4cee15f1a276933c159552ac2e123f56c9, freshly fetched main.
- No exact external feature/source tuple was supplied; Relationships remains unverified without guessed identifiers.

## Recovery

- Branch: feat/work-record-task-ownership. Work Record: agent-workflow:work-record-task-ownership at .agent-workflow/tasks/work-record-task-ownership.md.
- Next: obtain independent technical plan review, then implement within the existing human approval.
- Prior completed privacy work and necessary private evidence remain in their retained checkout.
