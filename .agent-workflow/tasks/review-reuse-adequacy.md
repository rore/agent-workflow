# Reuse completed reviews and assess test adequacy

Source: Relay relay-msg-064c8acafcfd4ca4bb99983e4c91810f. Direct user authorization verified in manager thread 01a0d7cd-696b-76a0-8f2f-48a80a201905, user message 01a0f628-d701-7b43-8ff2-1ba28eaba0b0: "Okay, so let's do it." Assigned scope is exactly the two instruction clarifications below.

<!-- agent-workflow:start -->
**Outcome:** Agents reuse valid completed technical reviews for unchanged applications and assess whether tests detect the relevant failure using faithful interfaces.
**Target:** agent-workflow
**Scope:** Existing technical-review reuse and test-adequacy instructions in the normative SPEC and relevant skill/checkpoint source, decision rationale, generated package/local mirrors, and this Work Record.
**Constraints:** Preserve applicability, Work Record, destination risk, independent/human review and trust duties; no broad install/hook exemptions, risk downgrades, model changes, new review stages, checker mechanisms, infrastructure or consumer edits. Preserve root checkout and local hook preview.
**Completion criteria:** Unchanged reviewed application guidance checks change identity/revision and destination compatibility and reuses valid review evidence; changed behavior, assumptions or risk get review of the uncovered decision. Existing technical review asks whether tests would catch the relevant failure and fakes match the real interface, resolving uncertainty with the smallest targeted check. Instructions remain consistent, within existing budgets, packaged and independently reviewed.
**Requirement baseline:** {"source":"relay-msg-064c8acafcfd4ca4bb99983e4c91810f","outcome":"Agents reuse valid completed technical reviews for unchanged applications and assess whether tests detect the relevant failure using faithful interfaces.","scope":"Existing technical-review reuse and test-adequacy instructions in the normative SPEC and relevant skill/checkpoint source, decision rationale, generated package/local mirrors, and this Work Record.","constraints":"Preserve applicability, Work Record, destination risk, independent/human review and trust duties; no broad install/hook exemptions, risk downgrades, model changes, new review stages, checker mechanisms, infrastructure or consumer edits. Preserve root checkout and local hook preview.","completion_criteria":"Unchanged reviewed application guidance checks change identity/revision and destination compatibility and reuses valid review evidence; changed behavior, assumptions or risk get review of the uncovered decision. Existing technical review asks whether tests would catch the relevant failure and fakes match the real interface, resolving uncertainty with the smallest targeted check. Instructions remain consistent, within existing budgets, packaged and independently reviewed."}
**Risk:** High
**Complexity:** Simple
**Reason:** Intended SPEC clarification touches the normative red contract and architecture-review checkpoint. Skill/checkpoint/package paths are gray/watch, record blue. One bounded prose change; no executable behavior change.
**Discovery:** Pending bounded inspection of existing reuse and adequacy rules after this baseline commit.
**Material assumptions:** These clarify existing review/evidence responsibilities; materially new exemptions or destination/human/trust waivers would exceed authorization and return to planning.
**Plan:** Pending discovery and independent technical plan review; edit SPEC first if its normative meaning needs clarification, then propagate only load-bearing instructions.
**Verification plan:** Two authorized behaviors and preserved duties -> independent plan/result scenario review. Source/dist coherence and token ceilings -> existing budget/link/package checks. Mandatory pre-push repository gate -> one tests/run-all.sh run after edits; no repeated suite without a new reason.
**Plan review:** Pending independent agent technical review.
**Approvals:** Approved by user 2026-10-01: "Okay, so let's do it." Authorizes the manager's two bounded instruction changes, verified direct source above; separate final human result review remains with manager.
**Exceptions:** —
**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

Applicability: normative SPEC and agent instructions are never documentation-exempt. Clean completed managed checkout reused on feat/review-reuse-adequacy from live main f778377b2d093966f0f82d59a9364f1e3b29f629; root checkout remains untouched. Baseline recorded before discovery, planning or source edits. Blocked on discovery and required technical plan review, not a duplicate permission request.
