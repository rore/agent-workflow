<!-- agent-workflow:start -->
**Outcome:**
Elevated and High Agent Workflow plans and results receive independent, risk-competent technical review, while human approval remains a separate authorization/attention gate.

**Target:**
agent-workflow.

**Scope:**
Normative Agent Workflow SPEC, relevant skill/checkpoint guidance, and only the minimal checker/schema/tests/package changes needed to represent and validate independent review evidence in this repository.

**Constraints:**
Preserve Routine proportionality, user-selected model settings, and independent repository/organization human-specialist requirements. Approval text or labels cannot count as technical review evidence. No blanket multiple expensive reviewers, new service/telemetry framework, or consumer-repository edits. Coordinator alone requests human approval.

**Completion criteria:**
When an Elevated or High plan/result advances, guidance requires a clean-context non-implementer agent technical review appropriate to its risk, including verification adequacy and specialist escalation where needed; human approval remains distinct. Checker distinguishes structurally recorded agent result evidence from approval without claiming to prove review quality. Focused tests and full suite cover the new gates and Routine fast path.

**Requirement baseline:**
{"source":"pallium-relay:relay-msg-c61152b1af0e46ff961e17fb6d8f79e3","outcome":"Elevated and High Agent Workflow plans and results receive independent, risk-competent technical review, while human approval remains a separate authorization/attention gate.","scope":"Normative Agent Workflow SPEC, relevant skill/checkpoint guidance, and only the minimal checker/schema/tests/package changes needed to represent and validate independent review evidence in this repository.","constraints":"Preserve Routine proportionality, user-selected model settings, and independent repository/organization human-specialist requirements. Approval text or labels cannot count as technical review evidence. No blanket multiple expensive reviewers, new service/telemetry framework, or consumer-repository edits. Coordinator alone requests human approval.","completion_criteria":"When an Elevated or High plan/result advances, guidance requires a clean-context non-implementer agent technical review appropriate to its risk, including verification adequacy and specialist escalation where needed; human approval remains distinct. Checker distinguishes structurally recorded agent result evidence from approval without claiming to prove review quality. Focused tests and full suite cover the new gates and Routine fast path."}

**Risk:**
High

**Complexity:**
Moderate

**Reason:**
docs/SPEC.md is Redline red with architecture-review; this changes the governance contract for all consumers. Moderate complexity: one repository and one related review-evidence path.

**Discovery:**
Pending source inspection after the baseline commit.

**Material assumptions:**
Existing Work Record prose/fields may carry result-review evidence without schema change; if not, plan only the smallest necessary structural field. No source edits before reviewed plan approval.

**Plan:**
Pending discovery and clean-context plan review. No substantive source edits before coordinator-obtained human approval.

**Verification plan:**
Pending discovery; cover Elevated/High plan and result, Routine fast path, separate human approval, specialist/verification adequacy, and truthful checker limits.

**Plan review:**
Pending clean-context agent review.

**Approvals:**
Pending human plan approval; coordinator is sole requester.

**Exceptions:**
—

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- 2026-09-25: Accepted Pallium Relay assignment from relay-msg-c61152b1af0e46ff961e17fb6d8f79e3. Started isolated branch feat/independent-technical-review at fbe6c768. Requirement baseline captured before discovery; next: inspect current review contract and checker, then plan review. No substantive source edits.

