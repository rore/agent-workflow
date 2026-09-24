<!-- agent-workflow:start -->
**Outcome:** Pull-request CI detects a Work Record requirement baseline rewritten after its first committed version.

**Target:** agent-workflow.

**Scope:** Normative baseline rule, existing checker and CI history integration, focused and end-to-end tests, relevant public and agent guidance, generated package, and this Work Record.

**Constraints:** Preserve current Work Record format, legitimate legacy baseline establishment, and the advisory commit-order rule. Do not claim Git history proves initial requirement accuracy, semantic classification, or resistance to rewritten branch history. Avoid a new artifact, configuration field, or CI job.

**Completion criteria:** On PRs, a later baseline rewrite fails the existing Agent Workflow check for new and existing Work Records; unchanged baselines pass despite JSON formatting changes; legacy owner establishment remains possible; unavailable required history fails visibly; end-to-end tests cover real Git history and packaged CI-style execution; documentation explains the protection and limits.

**Requirement baseline:** {"source":"user-request:0f7c016d-cad2-48ad-9f5f-330325cf69f2","outcome":"Pull-request CI detects a Work Record requirement baseline rewritten after its first committed version.","scope":"Normative baseline rule, existing checker and CI history integration, focused and end-to-end tests, relevant public and agent guidance, generated package, and this Work Record.","constraints":"Preserve current Work Record format, legitimate legacy baseline establishment, and the advisory commit-order rule. Do not claim Git history proves initial requirement accuracy, semantic classification, or resistance to rewritten branch history. Avoid a new artifact, configuration field, or CI job.","completion_criteria":"On PRs, a later baseline rewrite fails the existing Agent Workflow check for new and existing Work Records; unchanged baselines pass despite JSON formatting changes; legacy owner establishment remains possible; unavailable required history fails visibly; end-to-end tests cover real Git history and packaged CI-style execution; documentation explains the protection and limits."}

**Risk:** High

**Complexity:** Moderate

**Reason:** Redline classifies the normative SPEC as red and requires architecture-review. The new non-waivable PR gate affects every consuming repository; a false pass or false failure changes governance behavior.

**Discovery:** Pending.

**Material assumptions:** Pending.

**Plan:** Pending discovery and clean-context review.

**Verification plan:** Pending discovery.

**Plan review:** Pending.

**Approvals:** Pending user plan approval.

**Exceptions:** —

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- Established initial Task Context before implementation. Scope is not documentation-only. Redline pre-edit classification is RED/architecture-review, with no boundary rule or API/schema/security path in the intended change.

## Evidence

- Source request: user-request:0f7c016d-cad2-48ad-9f5f-330325cf69f2.
