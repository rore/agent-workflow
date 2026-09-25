<!-- agent-workflow:start -->
**Outcome:** Review-evidence gates reject placeholder values that do not identify a review, revision, or adequacy assessment.

**Target:** agent-workflow repository.

**Scope:** Shared review-evidence parser, focused checker regression tests, and regenerated distribution.

**Constraints:** Preserve acceptance of valid review references and the distinction between attested evidence and verified reviewer identity. Do not change policy or workflow requirements.

**Completion criteria:** Elevated/High plan and result gates reject `unknown` and `not provided`, accept real references, and the packaged checker passes the repository suite.

**Requirement baseline:**
{"source":"Pallium PR #250 CodeRabbit inline review 4106872028 and user bug-fix instruction","outcome":"Review-evidence gates reject placeholder values that do not identify a review, revision, or adequacy assessment.","scope":"Shared review-evidence parser, focused checker regression tests, and regenerated distribution.","constraints":"Preserve acceptance of valid review references and the distinction between attested evidence and verified reviewer identity. Do not change policy or workflow requirements.","completion_criteria":"Elevated/High plan and result gates reject `unknown` and `not provided`, accept real references, and the packaged checker passes the repository suite."}

**Risk:** Elevated

**Complexity:** Simple

**Reason:** Tracked .claude/skills/agent-workflow install files are watch-only and otherwise unclassified, so the final diff is GRAY; one shared parser guard remains a Simple change.

**Discovery:** Pallium PR #250 CodeRabbit comment 4106872028 identified that unknown and not provided pass the shared review-evidence parser. The focused regression reproduced four failures before the fix. Source parser, both plan gates, the result gate, existing tests, and packaging were inspected. Redline after packaging found gray tracked .claude skill copies, correcting the initial Routine classification.

**Material assumptions:** Existing positive review references remain accepted; focused and package checks detect drift. If either fails, stop before resyncing Pallium.

**Plan:** Reject unknown and not provided in core/checker/predicates.py's shared placeholder regex; add one parameterized regression in tests/checker/test_agent_review_evidence.py; rebuild dist and tracked .claude install; run relevant layers, independent technical review, then publish the upstream fix before re-syncing Pallium. No policy, SPEC, or workflow-rule changes. The initial Routine classification was incorrect and was corrected after implementation, before any push.

**Verification plan:** When Elevated/High plan or result fields contain unknown/not provided, gates reject them while valid references still pass -> focused checker regression and complete Python suite. Packaged checker remains synchronized -> package drift/install checks. No unrelated behavior changes -> final diff, Redline, workflow check, and CI.

**Plan review:** Agent technical review: delegated Codex /root/upstream_review_plan, 2026-09-25, working-diff hash 2737762621d140976d64108a27d5e457904e0fc7; scoped technical plan approved with no blocking code findings. This review was after implementation because initial Redline risk was misclassified; it is not claimed as a pre-edit review.

**Approvals:** Not required at this risk level.

**Exceptions:**
- rule: approval.elevated_clean_context_review_present
  reason: Initial Routine misclassification meant the independent Elevated plan review happened after implementation; no pre-edit review is claimed.
  scope: Pre-implementation review timing for this task and PR #44 only.
  approver: Rotem Hermon, 2026-09-25, "Yes, I approve."
  compensating_validation: Independent plan and result reviews; 27 focused tests, 414 Python tests, package checks, and green PR CI.

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

Isolated branch `feat/reject-review-placeholders` from upstream `origin/main` at 7d6d46d. Pallium PR #250 remains unmerged while this source defect is corrected.

## Verification

Regression was red before the parser change (4 failures for unknown / not provided at Elevated/High), then 27/27 focused review-evidence tests passed. Complete Python layers: 414 passed. Budget, schema, Work Record, checker, Redline, tuner, and hooks layers passed under Git Bash after providing the checkout's expected .venv; link and all package checks, including end-to-end bootstrap, passed under WSL. A single run-all.sh invocation could not pass in one shell: WSL lacks pytest/Node and Git Bash's package rebuild silently exits, so equivalent layers were run with the available runtimes. PR CI is still required.

## Plan review

Agent technical review: delegated Codex /root/upstream_review_plan, 2026-09-25. Reviewer inspected the shared parser, plan/result callers, regression, packaged checker and manifest, and corrected GRAY classification. No blocking code finding; verification adequate before CI. Process caveat: the review happened after implementation and cannot retroactively satisfy the pre-edit gate. Result review remains pending.

## Result review

Agent technical review: delegated Codex /root/upstream_result_review, 2026-09-25; no blocking code findings. The shared parser rejects both placeholders through plan and result gates, positive references remain accepted, and packaged copies match. The late plan-review caveat remains disclosed above.
Reviewed revision: 7a847cec52c8a1e99a237a10ab156a072a70106b
Verification adequacy: 27/27 focused tests, 414 Python tests, package drift/install/E2E bootstrap, Redline and local workflow checks adequately cover this narrow source fix before CI. One-shell full suite remains unverified because local Git Bash and WSL prerequisites are split; upstream PR CI is required.

## Process gate, 2026-09-25

CodeRabbit review on upstream PR #44 correctly flagged that the independent Elevated plan review occurred after implementation due to the initially incorrect Routine classification. Green checker/CI does not repair the timing requirement. Rotem Hermon explicitly approved a one-task exception on 2026-09-25: "Yes, I approve." The exception applies only to PR #44's missed pre-edit timing; it does not relax future review requirements or assert that this review happened before implementation.

Skill-feedback trigger 2 dropped: the late review was caused by this task's own initial risk misclassification, not an upstream skill defect.
