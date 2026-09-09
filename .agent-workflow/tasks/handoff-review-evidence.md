<!-- agent-workflow:start -->
**Outcome:** Receiving sessions validate that canonical recovery state is actionable, and result reviewers obtain targeted behavioral evidence when supplied evidence is insufficient.

**Target:** Packaged agent-workflow operating and result-review guidance.

**Scope:** `core/skill/operating-mode.md`, `core/templates/checkpoints/review-result.md`, the result-review predicate docstring, decision log, regenerated package, and focused tests. No checker behavior or schema changes.

**Constraints:** Add no workflow stage, artifact, field, mandatory handoff agent, model requirement, broad test rerun, or mechanical claim that prose/evidence adequacy is proven. Preserve mandated human review.

**Completion criteria:**
- On takeover/resume, guidance requires the receiver to identify the next action, constraints, and verification from canonical state or repair/clarify that state before proceeding.
- When result-review evidence is insufficient, guidance selects the smallest useful behavioral check instead of routinely rerunning the full suite.
- Elevated/High reviewer identity rules are explicit, and checker documentation describes only the checkpoint subset it enforces.
- Packaged skill output is synchronized and all repository tests pass.

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Small prose changes alter recovery and review behavior across every consuming installation and must stay aligned with normative judgment boundaries.

**Discovery:** SPEC §§4, 6, 9.7, 13.3, 13.5, and 15 already define resumability and evidence-adequacy outcomes. Current skill guidance tells the outgoing session how to preserve recovery state but does not tell the receiver to validate it. Result-review guidance requires adequacy judgment but gives no bounded action when evidence is weak and omits explicit reviewer-identity rules. `review_checkpoints_satisfied` enforces only Redline checkpoints although its docstring says it closes §9.7 result-review enforcement.

**Material assumptions:** The existing Work Record plus repository and authoritative linked artifacts remain the canonical recovery surface; disproof would require a SPEC/backend redesign and stops this change. Behavioral evidence can be added to existing PR/result-review prose; if not, a new artifact decision is required and this change stops.

**Plan:** Add one receiver-side rule when loading an existing record; add a compact risk/identity rule and conditional targeted-check instruction to result review; narrow the predicate docstring; record the no-new-stage/artifact decision; regenerate/install the package; run budget, link/package, focused checker, and full tests. Stop if token ceilings require a material increase or existing tests reveal a contract conflict.

**Verification plan:**
- Receiver readiness and review guidance are present, correctly triggered, and package-synchronized → source/dist inspection plus install/package checks.
- Skill additions remain within recurring token ceilings → `bash tests/budget/run.sh --verbose`.
- Checker wording change does not alter behavior → focused checker tests and full `bash tests/run-all.sh`.
- Relative links and packaged references remain valid → link/package test layers.

**Plan review:** Clean-context review `/root/handoff_review_plan` approved; preserve mode-dependent checkpoint enforcement and fail closed when targeted evidence is unavailable.

**Approvals:** Not required at this risk level.

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

Branch: `feat/handoff-review-evidence`. Clean-context plan review approved the narrow guidance-only approach. It required mode-qualified checkpoint wording and explicit unavailable-evidence handling; both were incorporated. Implementation revision: `c6d8de6`.

Added receiver readiness to the existing record-load step, conditional targeted behavioral checks and exact reviewer identity rules to result review, and narrowed the checker docstring to its Redline-checkpoint subset. Regenerated `dist/` and the dogfood install without adding a stage, artifact, field, model requirement, or predicate.

## Evidence

- Packaged fresh-session scenarios `/root/handoff_review_scenarios`: complete recovery state proceeds; ambiguous state stops for repair; sufficient direct evidence avoids redundant checks; unavailable multi-step evidence leaves the gate unsatisfied.
- Budget: all 19 files remain within existing ceilings. Strict `C.UTF-8` counts are `operating-mode.md` 1888/1900 and `review-result.md` 700/700.
- Package/install/reference/bootstrap checks passed; all 146 Markdown links passed.
- Checker: 138 tests passed using the repository `.venv`.
- Full nine-layer suite passed across the repository's standard runners. The combined WSL run's hooks layer was rerun natively after the temporary Windows-Python shim introduced CRLF/exit-code artifacts; native hooks passed every case.
- Full-suite implementation revision: `c6d8de6`. Final reviewed revision: `881f361`; post-fix budget, package/install, link, and whitespace checks passed.
- Initial PR CI exposed that the local machine lacks the budget script's pinned `en_US.UTF-8` locale and under-counted words. The operating guidance was compressed rather than raising its ceiling; the independent reviewer reapproved the strict-budget version.

## Result review

Clean-context reviewer `/root/handoff_review_result` initially blocked on ambiguous record creation and reviewer identity weaker than SPEC §9.7; `bd6aba5` fixed both. After CI exposed the locale-dependent budget under-count, `92b7a4d` compressed the pickup rule without weakening it. CodeRabbit then found one remaining unconditional PR-time blocking claim; `881f361` made it binding-mode-only. After rebase onto `a694472`, the reviewer checked the full diff, source/dist/install synchronization, and strict budgets, then approved `881f361` with no remaining findings.
