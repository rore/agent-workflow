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

**Material assumptions:** Assignment concerns future task identity, not retrospective repair of other active work. One authoritative implementation line means accountable integration and acceptance, not a ban on parallel contributor branches or substantial implementation contributions. If a new ownership or enforcement mechanism is needed, return to planning before expanding scope.

**Plan:** First clarify SPEC section 6: one accountable owner controls authoritative workflow state, integration and final acceptance per task at a time; independently progressing implementation/review delivery tasks get distinct records linked to the same existing feature or parent, with no mandatory parent. Preserve one task identity for contributions under that owner's workflow, including substantial parallel implementation, manager-owned shared tasks, handoffs, replacement checkouts and ordinary Git copies. Shared-task contributors add attributable revision/evidence; the owner consolidates the record without replacing authoritative requirements, approvals or global State with contributor bookkeeping. Reconcile conflicting supplied identity with the assigner before starting an independent delivery; do not invent a competing record. Then update operating-mode Step 2 and delegation wording to apply that distinction, compacting only the same identity/delegation instructions to stay under the unchanged ceiling. Reuse sections 8.2 and 10 rather than duplicating decomposition. Append one rationale decision, regenerate dist and isolated repository skill mirrors. Stop on changed responsibility/enforcement scope or unresolved assignment conflict. Required independent technical plan/result reviews and separate final human result review remain in force.

**Verification plan:**
- manual: Independent scenario review covers two independently delivered parallel tasks; bounded research/review/implementation helpers; manager-owned shared task; same-task supplied identity on another branch or replacement checkout; handoff; ordinary Git copies; conflicting supplied identity for a new delivery; absent feature/parent; authoritative existing feature link.
- manual: Inspect the complete diff for no schema/checker/gate/runtime/config changes and no privacy disclosures.
- Required repository gates -> Run existing instruction budgets, links/package parity and the full tests/run-all.sh once before pushing; run local checker after each State change with actual Redline verdict. Do not add tests that merely match prose or increase ceilings.

**Plan review:** Agent technical review: independent architecture and plan review recorded under Plan review below, covering c6983b5021d475915c59dfc8146d94875ca453f7 and subsequent Verification plan/Exceptions syntax corrections. Approved with no blocking findings; keep manager-owned independent deliveries distinct and do not equate implementation line with physical checkout.

**Approvals:** Approved by user 2026-10-31: "ok, so make sure we update what is needed" for the presented bounded task-ownership rule. Exact approval provenance is retained privately. Separate final-result review remains pending.

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

- Established context and immutable baseline before implementation planning. Focused discovery and bounded plan are complete. Independent plan review approved; supplied human approval covers the presented rule. Ready for bounded implementation.
- Assignment clarified within the same scope: substantial parallel contributions may share one task when one owner controls requirements, approvals, workflow state, integration and final acceptance. No violation or retrospective migration follows from multiple writers, branches or checkouts. Implementation and independent reviewer received this precision before delivery.
- Independent technical plan approval carries forward for that precision. Implemented SPEC section 6 first, then operating-mode identity/delegation instructions and the rationale decision. Kept supplied-reference resolver and slug-prefix behavior, exact target checkout and read-only/material authority. No enforcement or schema change.
- Regenerated dist and both isolated repository skill mirrors. Actual operating-mode budget is 1897/1900 tokens with the existing ceiling unchanged. Full verification and independent result review are next.
- Independent result review found one compression regression: delegation lost explicit excluded scope. Restored allowed/excluded scope at f8bc4af56015b9b059708c53e7ff88502ba924b6 and regenerated mirrors. Independent technical and architecture review accepted the correction; all 23 final instruction budgets pass, operating-mode 1898/1900.
- The full suite passed its first eight layers and the package parity, install-sync, references, install-probe and line-ending checks, then stopped at three existing bootstrap assertions matching superseded delegation sentences. Updated only those assertions to the reviewed equivalent wording; no new test or coverage removal. Focused bootstrap rerun is in progress. This is required test maintenance within the existing instruction change, not a new behavior or gate.
- Complete focused bootstrap rerun passed with exit 0 on the corrected content at 154e59309230eb59d512b9580be9c9986d77c865. Independent review accepted the three assertion updates and reuse of the preceding passing layers. Advanced to Ready for review; no final-revision full-suite pass is claimed until CI provides it.
- Removed the temporary task-only interpreter junction nonrecursively; the existing interpreter remains intact. Only this task checkout and isolated test repositories were changed.
- Trigger 2 dropped: the assignment clarification and corrected compression are covered by this change; no additional distinct upstream defect requires a separate report.

## Plan review

- Independent non-implementer technical review approved the plan at c6983b5021d475915c59dfc8146d94875ca453f7 plus syntax-only Verification plan/Exceptions corrections. Inspected this Work Record, AGENTS.md, SPEC sections 6, 8.2, 9.4 and 10, operating-mode identity/delegation guidance, CONTRIBUTING and Redline policy.
- Architecture judgment: clarify SPEC section 6 and existing identity/delegation decision points; existing decomposition and identity rules suffice. No schema, registry, checker or new gate is justified.
- Scenario coverage accepted. Result review must confirm manager ownership cannot exempt independent deliveries and implementation line does not require one physical checkout or prohibit helpers. Final wording, checks and separate human result review remain outstanding.

## Evidence

- Initial base: 00cf3a4cee15f1a276933c159552ac2e123f56c9, freshly fetched main.
- No exact external feature/source tuple was supplied; Relationships remains unverified without guessed identifiers.
- Actual committed-diff checker has no blocking failures; architecture-review remains an advisory pending separate human result review. The immutable task baseline is unchanged.
- Full tests/run-all.sh started at 09df756d7609419eb1ac170e4a880334d02d5986 and exited 2 at the final bootstrap test's stale literal assertions. All eight preceding layers and the earlier package checks passed. The source correction during that run was only allowed/excluded delegation wording and generated manifests at f8bc4af56015b9b059708c53e7ff88502ba924b6; final budgets were rechecked. Subsequent changes update only the three obsolete test literals. The complete focused bootstrap rerun passed with exit 0; its corrected test/source content matches 154e59309230eb59d512b9580be9c9986d77c865. Original failure evidence is retained locally. Exact published-head full-suite CI remains required before merge.

## Result review

- Agent technical review: independent non-implementer result and architecture review accepted f8bc4af56015b9b059708c53e7ff88502ba924b6 after the explicit excluded-scope correction. Inspected the full diff, connected identity/delegation guidance, SPEC, decision rationale and all operating mirrors. No blocking finding remains.
- Reviewed revision: 154e59309230eb59d512b9580be9c9986d77c865, carrying forward the source/architecture review of f8bc4af56015b9b059708c53e7ff88502ba924b6 and reviewing the three existing assertion updates.
- Verification adequacy: independent review accepts reuse of the eight passing layers and earlier package checks with the entire corrected bootstrap rerun passing. No test coverage was removed, and repeating unrelated history tests locally would add no useful assurance. Final-head CI and separate human result/architecture review remain required; no runtime adoption is claimed.
- Shared-task disposition: where one owner genuinely retains requirements, baseline, approvals, authoritative State, integration and combined final acceptance, multiple contributors/checkouts require no migration. Independently progressing workflow/review tasks remain separate. No consumer task was changed or retrospectively split.
- Everyday installations are unchanged. A later owner-authorized sync could update only operating-mode.md and manifest.txt in each existing repository-local skill mirror, with backups, compatibility verification and rollback; it requires its own exact destination/owner window. No global or runtime configuration change is proposed.

## Recovery

- Branch: feat/work-record-task-ownership. Work Record: agent-workflow:work-record-task-ownership at .agent-workflow/tasks/work-record-task-ownership.md.
- Last reviewed source/test revision: 154e59309230eb59d512b9580be9c9986d77c865. Local verification is complete with the original failure and passing focused repair accurately recorded. Next publish the reviewed PR, verify exact-head CI and review threads, then obtain separate human result/architecture review before merge. No live-sync window is authorized; keep everyday installations unchanged.
- Prior completed privacy work and necessary private evidence remain in their retained checkout.
