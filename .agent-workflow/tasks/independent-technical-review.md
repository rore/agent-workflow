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
SPEC §9.4 says Elevated clean-context plan review SHOULD and High human plan review MUST; the current default profile and plan checkpoint already require clean-context plan review for both. SPEC §9.7 permits human OR agent Elevated result review and requires human High result review, but neither requires a separate agent technical result review. The reviewer already must judge verification adequacy. Checker currently gates Elevated plan-reference presence, High plan-approval-shaped text, their separation, and Redline PR checkpoints; it has no independent agent result-review predicate. The Work Record parser leaves Result review in prose outside the marker block, which checker already reads as raw text. SPEC §5 and the existing traceability-not-identity decision limit checker to structural evidence; it cannot authenticate a reviewer or judge competence/adequacy. Relevant sources: docs/SPEC.md §§3, 5, 8, 9.4, 9.6, 9.7, 13.4; docs/DEFAULT_PROFILE.md §3; docs/ENFORCEMENT.md; core/checker/predicates.py; core/work_record/parser.py; core/templates/checkpoints/{plan-and-review,review-result}.md. No applicable canonical roadmap item found for this change. Material conflict: the old default High human technical plan/result-review obligation assumes humans supply technical assurance; the user's requirement assigns technical assurance to independent agents while retaining distinct human authorization/attention. This task must revise the old default, not preserve it.

**Material assumptions:**
The existing Plan review field and ## Result review prose can carry distinct agent-review references without a schema change; validate with parser/checker tests before committing to that shape. Structural markers are attestations, not authenticated proof; if a reliable machine check would require identity, competence, or review-quality inference, leave that to reviewer judgment instead of claiming enforcement. Existing records and fixtures may use older prose; keep them parseable but require new evidence before a legacy task advances under the new gate. Update focused fixtures, not unrelated historical records. Existing PR-time Redline/CODEOWNER/label checkpoints are path-triggered and may run in shadow mode, so they cannot alone supply a generic High final human-authorization gate. Use a distinct High result-authorization reference in existing Work Record prose, after agent result review and tied to the reviewed revision; let checker validate structural presence and separation without claiming human identity. PR and external human-review requirements remain additive. No source edits before reviewed plan approval.

**Plan:**
1. Amend SPEC first, including §3's obsolete claim that clean-context agent review is not independent assurance: require a clean-context, non-implementer agent technical plan review and result review for Elevated and High; reviewers assess verification adequacy and match expertise to risk, escalating to a specialist when needed. Keep separate High human plan authorization and final result authorization/attention gates; do not require default human technical review or treat authorization as a technical assessment. Preserve human technical/specialist review only where separately mandated by explicit repository, organization, security, or compliance policy. Clarify that human approval, CODEOWNER approval, or a label is authorization/checkpoint evidence, never a substitute for the agent technical review. Keep Routine self/normal-PR path.
2. Align the default profile and the smallest relevant skill/checkpoint/template text with the SPEC. Record resolvable agent review references, reviewer/implementer separation, revision, findings/disposition, and source evidence inspected in Plan review and ## Result review; require the result reviewer to assess verification adequacy and expertise limits. Use the least costly capable reviewer and reuse valid unchanged reviews. Trim/rephrase existing prose to respect skill token budgets; do not add a service or duplicate platform-specific guidance.
3. Add the smallest truthful checker gates: agent-specific Elevated and High clean-context plan-review evidence (tighten the existing Elevated gate) and Elevated/High agent result-review evidence at Ready for review. Require a distinct agent-review-shaped reference, not approval/label text alone; retain the separate High human plan-authorization gate and add a minimal High final result-authorization reference/gate in existing Work Record prose. Keep PR-time Redline/CODEOWNER/label checkpoints additive, not substitutes for either agent technical evidence or High final authorization. Authorization/labels cannot satisfy a missing agent technical-review gate. Reuse raw Work Record prose; avoid schema changes unless focused tests disprove this path. Document that presence/separation, not identity, expertise, or adequacy, is machine-checked. Preserve the existing exception model rather than silently making new gates non-waivable.
4. Add focused checker cases for both risk levels, absent/malformed/approval-only agent evidence, verification-adequacy reference, High human-gate separation, legacy-record advancement, and Routine fast path. Update only affected fixtures/docs; append the substantive decision. Regenerate/install the skill and package, run focused checks, budget/link/package checks, and the full test suite before any push.
Stop and return to planning if a schema migration, new identity authority, broader consumer-repo edits, or weakened verification becomes necessary.

**Verification plan:**
- When an Elevated or High plan advances, the agent shall have a distinct clean-context technical plan review → SPEC/checkpoint audit plus focused checker cases for both risks, including approval-only rejection.
- When an Elevated or High result is Ready for review, the record shall carry a non-implementer agent technical review reference and verification-adequacy assessment → focused positive/negative checker tests against ## Result review.
- When High work advances, human plan authorization and post-review final result authorization shall remain separate from agent technical assurance; only explicit external policy adds human technical/specialist review → normative/default-profile review and focused tests for distinct plan/result authorization refs, missing final authorization, and approval/label-only evidence that cannot satisfy agent technical review.
- When work is Routine, the normal proportional path shall remain available → focused Routine checker fixture and no new review requirement.
- When delivered across supported tools, the same skill/checker contract shall ship without budget or package regression → skill budget, link/package checks, full tests/run-all.sh; local checker after each State change. Independent agent reviewers judge technical adequacy and their expertise limits; explicit external policy may also mandate human technical review. Humans authorize/attend. Checker cannot authenticate reviewer identity or judge review quality.

**Plan review:**
Agent technical review: /root/technical_assurance_delta_review (gpt-6-astra, clean context, 2026-09-25) approved the corrected delta with no blocking findings. Prior /root/independent_review_plan approval of fbf34ee was superseded after the coordinator found its default human-technical-review contradiction.

**Approvals:**
Pending human plan approval; coordinator is sole requester.

**Exceptions:**
—

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- 2026-09-25: Accepted Pallium Relay assignment from relay-msg-c61152b1af0e46ff961e17fb6d8f79e3. Started isolated branch feat/independent-technical-review at fbe6c768. Requirement baseline captured before discovery. Inspected current review contract and checker; clean-context Astra plan review approved with two clarifications incorporated. No substantive source edits; coordinator rejected fbf34ee for preserving default High human technical review. Focused clean-context Astra delta review approved the corrected plan with no blocking findings. Awaiting coordinator-obtained human plan approval.
