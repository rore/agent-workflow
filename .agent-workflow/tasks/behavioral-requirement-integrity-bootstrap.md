<!-- agent-workflow:start -->
**Outcome:** Bootstrap reliably discovers and presents repository behavior-contract candidates for explicit developer selection, and the public documentation accurately describes the shipped behavioral-integrity feature.

**Target:** agent-workflow.

**Scope:** Bootstrap guidance; the existing packaged bootstrap E2E; generated distribution and local skill copies; public README, integration/default-profile/index docs, public workflow-guide copies, and roadmap summaries.

**Constraints:** Do not add an automated semantic scanner or new bootstrap harness. Never protect candidates automatically. Emit behaviorContracts only for explicitly selected exact or dir/** paths with an existing required-CI check and repository approval authority. Keep bootstrap token cost and public-doc duplication minimal.

**Completion criteria:** Phase 1 always reports behavior-contract candidates or explicit none with path, required-CI, and authority evidence; Phase 3 explicitly confirms selection; unresolved or unselected candidates cannot enter behaviorContracts; the packaged bootstrap E2E verifies the shipped contract; public docs and roadmap state match the shipped feature; package parity and the full suite pass.

**Requirement baseline:** {"source":"user-request:89beaf00-b5ee-4977-b3fa-089598690fac","outcome":"Bootstrap reliably discovers and presents repository behavior-contract candidates for explicit developer selection, and the public documentation accurately describes the shipped behavioral-integrity feature.","scope":"Bootstrap guidance; the existing packaged bootstrap E2E; generated distribution and local skill copies; public README, integration/default-profile/index docs, public workflow-guide copies, and roadmap summaries.","constraints":"Do not add an automated semantic scanner or new bootstrap harness. Never protect candidates automatically. Emit behaviorContracts only for explicitly selected exact or dir/** paths with an existing required-CI check and repository approval authority. Keep bootstrap token cost and public-doc duplication minimal.","completion_criteria":"Phase 1 always reports behavior-contract candidates or explicit none with path, required-CI, and authority evidence; Phase 3 explicitly confirms selection; unresolved or unselected candidates cannot enter behaviorContracts; the packaged bootstrap E2E verifies the shipped contract; public docs and roadmap state match the shipped feature; package parity and the full suite pass."}

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Clean-context Redline classified bootstrap skill source and generated package copies as gray/watch surfaces with no boundary risk; tests and public docs are blue. The work spans bootstrap UX, shipped-package verification, generated parity, and public documentation in one repository.

**Discovery:** Bootstrap already tells the agent to inspect candidate acceptance/E2E/contract/regression paths and to omit behaviorContracts without required-CI and authority evidence, but the mandatory Phase 1 finding has no candidate field and Phase 3 has no selection question. The existing package E2E is the smallest shipped-skill seam and already asserts conversational bootstrap rules that cannot be mechanically executed. Normative SPEC and enforcement docs already define the feature; public README, integration guide, default-profile examples, public checkpoint copies, and roadmap summaries are stale.

**Material assumptions:** Agent-led repository inspection is sufficient for candidate discovery; evidence for a need to parse test semantics or CI graphs programmatically returns this task to planning. Stable shipped-text assertions are sufficient E2E evidence for conversational rules; evidence that the package test can execute LLM judgment deterministically returns testing to planning. Public workflow-guide content stays synchronized with source; public-only cross-reference rewrites are allowed and must be link-checked. Any other divergence returns the task to planning.

**Plan:** 1. In core/skill/bootstrap-mode.md, make the Phase 1 finding report each candidate (or explicit none) as an exact repo-relative path or boundary-safe dir/** pattern, required-CI identifier plus current required-status evidence, and repository-authority evidence covering that path; incomplete evidence is unresolved. Phase 3 requires explicit select/reject per candidate, states selection is not authority approval, and emits only one compatible path set sharing one verification identifier and authority; otherwise split/defer or omit. 2. Extend tests/package/check-e2e-bootstrap.sh with stable positive and fail-closed assertions against the installed bootstrap-mode.md; do not add a scanner or claim deterministic proof of LLM judgment. 3. Run the focused bootstrap/package test before documentation work. 4. Update README.md, docs/INTEGRATION.md, docs/DEFAULT_PROFILE.md examples, docs/README.md only if its index wording changes, roadmap/scope.md, and roadmap/board.md; synchronize docs/agent-workflow/ content from core/templates/checkpoints/, including applicability.md and behavioral-integrity.md; rewrite only public-layout cross-references and make the link checker cover the public tree. 5. Regenerate dist and local installs, verify source/package/public-copy parity, run budget/link/package checks and tests/run-all.sh. Stop if bootstrap growth exceeds its existing budget, evidence needs hosting-API automation, or public copies require divergent content.

**Verification plan:** Phase 1 reports candidate/none evidence, Phase 3 requires select/reject and compatible check/authority sets, and incomplete evidence is omitted → positive and fail-closed assertions in tests/package/check-e2e-bootstrap.sh against the installed bootstrap-mode.md. Packaged consumer receives the guidance and existing bootstrap journeys still run → bash tests/package/check-e2e-bootstrap.sh. Public docs and workflow guides match source feature semantics and all public-layout links resolve → content comparison plus link checks that include docs/agent-workflow/. Skill growth remains bounded and generated artifacts match source → budget and package checks. Entire repository remains green → bash tests/run-all.sh.

**Plan review:** Clean-context review by `/root/bootstrap_plan_review`; initial findings resolved. Focused public-link amendment accepted by `/root/bootstrap_result_review`.

**Approvals:** Not required at this risk level.

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

- Resumed the shipped behavioral-integrity feature as a clean follow-up branch because the original branch was squash-merged.
- Read-only audit confirmed bootstrap guidance was partially present but not guaranteed in the structured finding or developer-confirmation flow.
- Clean-context Redline review classified the intended scope Elevated with no boundary risk.
- Clean-context plan review identified evidence-binding and single-check/authority compatibility gaps; the plan now fails closed on both.
- Updated, packaged, and locally installed the bootstrap contract; the focused packaged consumer E2E passes before public-doc changes.
- Mechanically synchronized every public workflow guide from core/templates/checkpoints, including applicability.md and behavioral-integrity.md.
- Updated the public README, bootstrap integration flow, default-profile examples, documentation index, and roadmap summaries without changing normative behavior.
- Result review rejected the byte-identical public-copy assumption because copied package-relative links are broken in the repository public layout; returned to planning for link adaptation and coverage.
- Rewrote only the four reviewed public-layout links, removed the link-check exclusion, and added parity enforcement that permits only those declared substitutions.
- CodeRabbit found two documentation-contract mismatches: the public Implement guide obscured its required target-file/class-list exception, and the README implied every affected Work Record must carry the verification identifier. Corrected the authoritative template, public/generated copies, and README to match the established contract.

## Evidence

- Pre-edit Redline review by `/root/bootstrap_redline`: gray/watch for bootstrap source and generated package; blue for tests/docs/roadmap; no boundary risk.
- Read-only test design by `/root/bootstrap_test_design`: extend the existing packaged bootstrap simulation; no new harness.
- `bash tests/budget/run.sh --verbose`: all skill surfaces within existing ceilings; bootstrap-mode 4455/4600 tokens.
- `bash tests/package/check-e2e-bootstrap.sh`: passed against installed dist, including the new candidate/selection/fail-closed assertions.
- Verified all checkpoint basenames were present and byte-identical; this exposed the invalid assumption because source-relative links do not resolve in the public layout.
- Updated `bash tests/links/run.sh`: all 194 Markdown files, including `docs/agent-workflow/`, have valid links; public/source parity passes after only the four declared link substitutions.
- Final `bash tests/run-all.sh` after the public-link fix: exit 0 across every layer.
- Final task-local checker with regenerated complete changed-path evidence and Redline verdict: clean; detected Elevated, with no boundary violation or required review checkpoint.
- Initial `bash tests/links/run.sh` passed 185 files but excluded `docs/agent-workflow/`; result review correctly rejected it as evidence for the public guides.
- `bash tests/package/run.sh`: source/dist/local parity, references, install probe, and bootstrap E2E passed.
- `bash tests/run-all.sh` with the existing project virtual environment selected for WSL: exit 0 across budget, schema, Work Record, checker, Redline, tuner, hooks, links, and package layers; evaluated the working tree based on `f6a68c6`.
- Post-CodeRabbit correction: `bash tests/links/run.sh` and `bash tests/package/run.sh` passed; budget, schema, Work Record, checker, Redline, tuner, and links passed with the project pytest environment; the package and hook layers passed separately under native WSL Python because Windows Python cannot address their WSL temporary paths.

## Plan review

Clean-context review by `/root/bootstrap_plan_review` required the Phase 1 finding to bind every candidate to current required-status evidence and path-covering repository authority, not merely name a workflow or CODEOWNERS file. It also identified that the single configured verification and authority cannot represent mixed candidate sets. The amended plan requires per-candidate select/reject, distinguishes selection from authority approval, permits only compatible sets, and adds packaged positive and fail-closed assertions without claiming to execute LLM judgment.

Focused re-review by `/root/bootstrap_result_review` accepted four declared public-link substitutions plus removal of the public-guide link-check exclusion as the smallest complete fix. Verification must compare public/source content after only those substitutions.
## Result review

Clean-context reviewer `/root/bootstrap_result_review` first rejected the public-copy link assumption and later two Work Record evidence defects. After the four link rewrites, public-tree link/parity coverage, corrected record, final full suite, and clean task-local checker, the reviewer accepted the result with no remaining blocker.

## Skill feedback (unsent)

**Affected surface:** `docs/agent-workflow/` publication and `tests/links/check-links.py` at the behavioral-integrity bootstrap follow-up.

**Expected:** Published checkpoint guides keep source content synchronized while every public relative link is validated.

**Actual:** Byte-identical copies retained package/source-relative links that do not resolve in the public layout, while the link checker excluded the directory.

**Minimal reproduction:** Copy `core/templates/checkpoints/*.md` directly into `docs/agent-workflow/`, then inspect links in `assess-risk.md`, `plan-and-review.md`, and `review-result.md`.

**Evidence:** Independent result review found four broken layout-dependent references that the passing link suite did not inspect.

**Suggested owner:** Public-guide synchronization rules in `docs/README.md` and coverage in `tests/links/check-links.py`.
