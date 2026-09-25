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
SPEC §9.4 says Elevated clean-context plan review SHOULD and High human plan review MUST; the current default profile and plan checkpoint already require clean-context plan review for both. SPEC §9.7 permits human OR agent Elevated result review and requires human High result review, but neither requires a separate agent technical result review. The reviewer already must judge verification adequacy. Checker currently gates Elevated plan-reference presence, High plan-approval-shaped text, their separation, and Redline PR checkpoints; it has no independent agent result-review predicate. The Work Record parser leaves Result review in prose outside the marker block, which checker already reads as raw text. SPEC §5 and the existing traceability-not-identity decision limit checker to structural evidence; it cannot authenticate a reviewer or judge competence/adequacy. Relevant sources: docs/SPEC.md §§3, 5, 8, 9.4, 9.6, 9.7, 13.4; docs/DEFAULT_PROFILE.md §3; docs/ENFORCEMENT.md; core/checker/predicates.py; core/work_record/parser.py; core/templates/checkpoints/{plan-and-review,review-result}.md. No applicable canonical roadmap item found for this change. User clarification: existing High human technical plan/result reviews remain required and ADDITIVE. An agent technical review must itself assess adequacy; a human review cannot replace it, and approval alone is not evidence that either technical review occurred.

**Material assumptions:**
The existing Plan review field and ## Result review prose can carry distinct agent-review references without a schema change; validate with parser/checker tests before committing to that shape. Structural markers are attestations, not authenticated proof; if a reliable machine check would require identity, competence, or review-quality inference, leave that to reviewer judgment instead of claiming enforcement. Existing records and fixtures may use older prose; keep them parseable but require new evidence before a legacy task advances under the new gate. Update focused fixtures, not unrelated historical records. Existing High human plan/result review obligations stay in the SPEC and profile. PR-time Redline/CODEOWNER/label checkpoints remain separate attention mechanisms; they do not prove either agent or human technical review. Do not add a new generic final-authorization artifact or checker gate for this clarification. No source edits before reviewed plan approval.

**Plan:**
1. Amend SPEC first: require clean-context, non-implementer agent technical plan and result reviews for Elevated and High; each agent review must stand on its own, assess verification adequacy and match expertise to risk. Retain existing High human plan review/approval and separate human result review, with specialist expertise where necessary; these are additive and cannot replace agent review. Preserve any further repository/organization/security/compliance human mandates. Preserve §3's caveat that clean context reduces anchoring but does not itself guarantee independent assurance or remove shared-model blind spots; require source-backed agent judgment without claiming checker-authenticated identity or quality. Approval, CODEOWNER approval, or labels do not prove either technical review occurred. Keep Routine self/normal-PR path.
2. Align the default profile and the smallest relevant skill/checkpoint/template text with the SPEC. Record resolvable agent review references, reviewer/implementer separation, revision, findings/disposition, and source evidence inspected in Plan review and ## Result review; require the result reviewer to assess verification adequacy and expertise limits. Use the least costly capable reviewer and reuse valid unchanged reviews. Trim/rephrase existing prose to respect skill token budgets; do not add a service or duplicate platform-specific guidance.
3. Add the smallest truthful checker gates: agent-specific Elevated and High clean-context plan-review evidence (tighten the existing Elevated gate) and Elevated/High agent result-review evidence at Ready for review. Require a distinct agent-review-shaped reference, not approval/label or human-review text alone. Retain existing High human plan approval, High human result-review obligation, and PR-time Redline/CODEOWNER/label checkpoints as additive gates; none can satisfy a missing agent technical-review gate. Reuse raw Work Record prose; avoid schema changes unless focused tests disprove this path. Document that presence/separation, not identity, expertise, or adequacy, is machine-checked. Preserve the existing exception model rather than silently making new gates non-waivable.
4. Add focused checker cases for both risk levels, absent/malformed/approval-only agent evidence, verification-adequacy reference, High human-gate separation, legacy-record advancement, and Routine fast path. Update only affected fixtures/docs; append the substantive decision. Regenerate/install the skill and package, run focused checks, budget/link/package checks, and the full test suite before any push.
Stop and return to planning if a schema migration, new identity authority, broader consumer-repo edits, or weakened verification becomes necessary.

**Verification plan:**
- When an Elevated or High plan advances, the agent shall have a distinct clean-context technical plan review → SPEC/checkpoint audit plus focused checker cases for both risks, including approval-only rejection.
- When an Elevated or High result is Ready for review, the record shall carry a non-implementer agent technical review reference and verification-adequacy assessment → focused positive/negative checker tests against ## Result review.
- When High work advances, existing human plan review/approval and separate human result review shall add to, never replace, independently adequate agent plan/result reviews → normative/default-profile audit and focused tests showing human approval, review text, or labels alone cannot satisfy agent technical gates.
- When work is Routine, the normal proportional path shall remain available → focused Routine checker fixture and no new review requirement.
- When delivered across supported tools, the same skill/checker contract shall ship without budget or package regression → skill budget, link/package checks, full tests/run-all.sh; local checker after each State change. Independent agent reviewers judge technical and verification adequacy and their expertise limits; existing High human reviewers add their review. Approval is not evidence of either review. Checker cannot authenticate reviewer identity or judge review quality.

**Plan review:**
Agent technical review: /root/technical_assurance_delta_review (gpt-6-astra, independent focused re-review, 2026-09-25) approved the additive human-plus-agent correction with no blocking findings. Prior fbf34ee and 40ec855 plan reviews are superseded.

**Approvals:**
Approved by user 2026-09-25 (relayed by coordinator from thread 01a0d7cd-696b-76a0-8f2f-48a80a201905): "why didn't you tell the agent to continue?" This authorizes implementation of reviewed plan cbe8a8b380d5bb701de332402820ad45430a3411 in context; it is not human code inspection or result review.

**Exceptions:**
—

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

- 2026-09-25: Accepted Pallium Relay assignment from relay-msg-c61152b1af0e46ff961e17fb6d8f79e3. Started isolated branch feat/independent-technical-review at fbe6c768. Requirement baseline captured before discovery. Inspected current review contract and checker; clean-context Astra plan review approved with two clarifications incorporated. No substantive source edits. After 40ec855, the user clarified that existing High human technical reviews remain additive, never substitutes for agent review. Focused independent Astra delta re-review approved the additive correction with no blocking findings. Coordinator relayed the user's direction to continue on reviewed plan cbe8a8b; recorded the exact words above as implementation authorization, not technical review. Intended targets before first source edit: docs/SPEC.md, docs/DEFAULT_PROFILE.md, docs/ENFORCEMENT.md, docs/DECISIONS.md, core/skill/operating-mode.md, core/templates/checkpoints/{plan-and-review,review-result}.md, core/templates/work-record-expanded.md, core/checker/predicates.py, focused tests/checker tests/fixtures, and generated dist/agent-workflow. No schema or CI workflow edit planned.

- 2026-09-25: SPEC §3/§8/§9/§13 updated first; shipped guidance now requires source-backed agent plan/result review while retaining additive High human reviews. Checker draft adds High plan and Elevated/High result structural gates using existing Work Record prose, so no schema migration was needed. Budget check passes. Local checker validates this task's High plan evidence; only the expected ad hoc Redline verdict is missing. Next: focused tests and golden-fixture migration.

- 2026-09-25: Added structural High plan and Elevated/High result review gates, kept High human approval distinct, and migrated checker goldens and the packaged consumer bootstrap fixture. Focused review-evidence tests passed (19); curated checker goldens passed (80); `bash tests/run-all.sh` passed all nine layers after package/native-install regeneration. Native Git Bash used the existing virtualenv via local ignored shims because the managed worktree lacks its own interpreter and the machine's `python3` alias is broken; no product runtime was changed for this setup.

- 2026-09-25: Independent Astra result review found three gaps: dotted `Ready for review.` skipped the result gate, valid Markdown source links were rejected, and new predicate provenance was `unknown`. Fixed all three and added positive/negative link, dotted-state, provenance, and exception-path regressions. Full suite passed again after the fixes. Final independent delta review and separate human High result review remain pending.
- 2026-09-25: Independent delta review of a6e9283 found a remaining Markdown-link punctuation edge. The parser now recognizes complete links followed by ordinary sentence punctuation without treating bracket placeholders as links. Added Markdown/autolink punctuation regressions; focused tests passed (23), then the full nine-layer suite passed again after package/native-install regeneration. Awaiting final independent disposition on this revision and separate human High result review.
- 2026-09-25: Independent Astra final disposition approved b23a7bf653f69c6272d7ebaa2025d0d6132cba12. No remaining actionable findings. Skill-feedback filter: Trigger 1 dropped: the repeated Python workaround is machine-local, not upstream-owned. Trigger 2 dropped: reviewer findings were implementation defects resolved before delivery, not a separate product/skill field defect. Separate High human result review and PR-time architecture review remain pending.

- 2026-09-25: Coordinator relayed the user's correction that contextual plan authorization must not be treated as missing for want of a magic word. Existing SPEC §9.4 already preserves approval through nonmaterial wording and revision bookkeeping. This is a nonmaterial clarification to the same plan/approval checkpoint and handoff instructions, with no new gate, schema, or human approval request. Before edit: touch only core/templates/checkpoints/plan-and-review.md and core/skill/operating-mode.md plus their generated/mirrored copies; then recheck budgets, links, package, full suite, and independent result review. Prior result review remains valid for unchanged code but must be reconciled against this guidance delta.

- 2026-09-25: Clarified existing contextual plan approval and continuity in the plan checkpoint, and immediate forwarding of received approval in handoff guidance. Kept material-change gates and unrelated blockers intact. Independent Astra review found one overbroad Blocked sentence; corrected it and received final approval with no remaining findings. Mirrored public guidance, regenerated source/dist/native installs, and added packaged consumer assertions. `bash tests/run-all.sh` passed all nine layers on the final guidance diff. No schema, checker, CI, or normative SPEC change.
## Evidence

- Completion criterion, independent agent plan/result review: SPEC and installed checkpoint guidance now require both for Elevated/High, with High human plan/result reviews additive. Focused checker review-evidence tests passed: 23 on b23a7bf; curated golden checker scenarios passed: 80. The checker validates structural attestations, not reviewer identity or review quality.
- Completion criterion, no Routine regression and package parity: `bash tests/run-all.sh` passed all nine layers on b23a7bf (budget, schema, work-record, checker, Redline, tuner, hooks, links, package); package layer includes a fresh consumer bootstrap. Native Git Bash used local ignored Python shims to the existing virtualenv. No required check failed or was skipped in the final run.
- Redline local verdict: RED because `docs/SPEC.md` changed; `architecture-review` remains unsatisfied in shadow/advisory mode until PR review. No boundary violation was reported. PR CI passed on the prior head and must be rechecked after this update.

- Approval continuity: existing SPEC §9.4 rule retained; packaged consumer bootstrap asserts both clarification lines. Budget passed 20/20 and `bash tests/run-all.sh` passed all nine layers on eb9d8f5503aa0505747595c0d401589809817cdc. Independent Astra review approved the corrected guidance; no checker, schema, CI, or normative SPEC change.

## Result review

Agent technical review: /root/approval_continuity_review (independent Astra final disposition on eb9d8f5503aa0505747595c0d401589809817cdc)
Reviewed revision: eb9d8f5503aa0505747595c0d401589809817cdc
Verification adequacy: The reviewer verified the clarification against SPEC §9.4, source/package/mirror parity, budget, and packaged assertions; the implementer ran the full nine-layer suite. The prior independent technical review remains valid for unchanged code.
Inspected evidence: normative SPEC/default profile, checker/source/package/native install diff, focused regression run (23 passed), guidance source/public mirror and packaged assertions, recorded full nine-layer suite result, Work Record plan and approved scope. Prior structural review: /root/technical_review_result on b23a7bf653f69c6272d7ebaa2025d0d6132cba12.
Findings: structural-review issues were fixed in b23a7bf; the guidance reviewer found an overbroad handoff Blocked sentence, narrowed before final approval. No actionable findings remain.
Limits: reviewer did not repeat the full suite. Structural markers do not authenticate technical reviewer identity, competence, or quality. Separate High human result review and architecture-review checkpoint remain pending; Ready for review is not acceptance or merge.
