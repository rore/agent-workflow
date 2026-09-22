<!-- agent-workflow:start -->
**Outcome:** Repositories without branch protection or CODEOWNERS can opt into workflow-only behavior-contract protection that keeps red classification, semantic change records, explicit user approval, and PR CI verification without claiming merge enforcement.

**Target:** agent-workflow.

**Scope:** Normative behavior-contract model; Redline policy schema, reporter payload/reporting, Agent Workflow checker consumption, bootstrap choice and explanation, tests, public documentation, and generated/install artifacts.

**Constraints:** Existing behaviorContracts configurations remain repository-protected by default and unchanged. Workflow-only protection remains explicit, requires a PR CI job that runs the named verification, omits CODEOWNERS/required-status/branch-protection claims, and does not create a second path classifier, checkpoint system, or approval registry.

**Completion criteria:** A repository can explicitly choose workflow-only protection; protected paths remain red and require per-path classification, requirement changes require exact user approval, the named PR CI verification is linked and visibly fails when broken, reports disclose that GitHub does not block merge, strict existing configurations behave unchanged, and bootstrap explains and tests both choices.

**Requirement baseline:** {"source":"user-request:0365fa2e-e664-4a7c-89ed-d51839cce546","outcome":"Repositories without branch protection or CODEOWNERS can opt into workflow-only behavior-contract protection that keeps red classification, semantic change records, explicit user approval, and PR CI verification without claiming merge enforcement.","scope":"Normative behavior-contract model; Redline policy schema, reporter payload/reporting, Agent Workflow checker consumption, bootstrap choice and explanation, tests, public documentation, and generated/install artifacts.","constraints":"Existing behaviorContracts configurations remain repository-protected by default and unchanged. Workflow-only protection remains explicit, requires a PR CI job that runs the named verification, omits CODEOWNERS/required-status/branch-protection claims, and does not create a second path classifier, checkpoint system, or approval registry.","completion_criteria":"A repository can explicitly choose workflow-only protection; protected paths remain red and require per-path classification, requirement changes require exact user approval, the named PR CI verification is linked and visibly fails when broken, reports disclose that GitHub does not block merge, strict existing configurations behave unchanged, and bootstrap explains and tests both choices."}

**Risk:** High

**Complexity:** Moderate

**Reason:** Redline classifies the normative spec and policy schema as red architecture contracts. This opt-in relaxation changes protection and approval semantics across schema, reporter, checker, bootstrap, and packaged consumers; a wrong default could silently weaken existing repositories.

**Discovery:** Pending focused discovery. Clean-context pre-edit Redline review classified the intended change RED/SCHEMA_CHANGE with architecture-review, no boundary violation, and a High risk floor.

**Material assumptions:** Existing strict behaviorContracts configuration can remain the default without migration. A PR-triggered CI job can be distinguished from a branch-required status check using bootstrap evidence and explicit user choice. Evidence to the contrary returns the design to planning.

**Plan:** Pending focused discovery and High-risk plan approval. No implementation is authorized yet.

**Verification plan:** Pending discovery; must cover strict backward compatibility, workflow-only path classification and approvals, visible non-enforcement reporting, bootstrap choice/evidence, PR CI linkage, package parity, and the full suite.

**Plan review:** Pending clean-context review.

**Approvals:** Pending explicit human plan approval.

**Exceptions:** —

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- Established Task Context and pre-edit classification before implementation. The change is not documentation-only because schema, reporter, checker, bootstrap, and normative specification are in scope.

## Evidence

- Clean checkout on `feat/workflow-only-behavior-contracts` from `ff081714806504284c61051594103145ca7bfd88`.
- Clean-context pre-edit Redline review: RED/SCHEMA_CHANGE, architecture-review, no boundary violation, High risk floor.

## Plan review

Pending.

## Result review

Pending.
