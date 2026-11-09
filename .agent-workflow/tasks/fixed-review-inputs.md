# Fixed review inputs

<!-- agent-workflow:start -->
**Outcome:** Reviewers use fixed inputs when implementation continues during review.

**Target:** agent-workflow.

**Scope:** One sentence in core/templates/checkpoints/review-result.md and regenerated package/install mirrors.

**Constraints:** Keep guidance short without duplicating existing instructions; no gates, schema, configuration, or runtime changes.

**Completion criteria:** The review-result guide instructs reviewers to review a fixed snapshot of the assigned revision or verified immutable build artifacts when the owner continues editing; mirrors match and required checks pass.

**Requirement baseline:**
{"source":"work-record-initial","outcome":"Reviewers use fixed inputs when implementation continues during review.","scope":"One sentence in core/templates/checkpoints/review-result.md and regenerated package/install mirrors.","constraints":"Keep guidance short without duplicating existing instructions; no gates, schema, configuration, or runtime changes.","completion_criteria":"The review-result guide instructs reviewers to review a fixed snapshot of the assigned revision or verified immutable build artifacts when the owner continues editing; mirrors match and required checks pass."}

**Relationships:**
{"schema_version":1,"sources":null,"pull_requests":[]}

**Risk:** Elevated

**Complexity:** Simple

**Reason:** The template and generated skill package/install mirrors are otherwise unclassified paths, giving a GRAY floor. One instructional sentence changes no enforcement.

**Discovery:** Upstream review-result records the reviewed revision but does not require fixed inputs during concurrent editing. No equivalent rule was found in the skill or checkpoint guides. Packaging copies the guide and regenerates its manifest entry.

**Material assumptions:** The existing reviewed-revision contract needs only operational clarification. Stop if implementation requires enforcement, configuration, or normative contract changes.

**Plan:** Add exactly: "When the owner continues editing during review, review a fixed snapshot of the assigned revision or verified immutable build artifacts." Place it beside review identity. Regenerate package/install mirrors using existing scripts; run the required full suite, privacy/diff and workflow/Redline checks; obtain independent result review and resolve PR feedback before authorized merge and compatible local refresh.

**Verification plan:** Exact wording and synchronized mirrors -> inspect the single source sentence and generated copies for exact wording and no duplication. Existing budget/link/package checks prove packaging integrity; bash tests/run-all.sh supplies required regression coverage. Redline and the workflow checker verify the final record and classification. Verify merged revision and refreshed bytes before completion.

**Plan review:** Agent technical review: independent plan review of commit 3d4d372. Accepted before implementation; inspected the record, review-result, operating-mode, CONTRIBUTING and SPEC sections 9.4/9.7. No blocking findings; verification adequate.

**Approvals:** Not required at this risk level.

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

Branch `feat/fixed-review-inputs` starts from upstream c0d69150ca05cdfab7951f741c16f7a477c7630a. Planning record committed before source changes. Source implementation and independent review complete; next action: publish the PR and require full CI success before merge. Source identity is unverified because no provider tuple was supplied.

## Plan review

Agent technical review: independent plan review of commit 3d4d372; accepted with no blocking findings. Elevated/Simple classification and the existing verification plan are adequate.

## Implementation plan clarification

The guide already uses 699/700 estimated tokens. Preserve the existing ceiling by shortening the roadmap paragraph while retaining its status, shipped/remaining scope, obsolete next steps, placement, prerequisite, record-result, skip and source-lifecycle obligations; then add the exact sentence beside review identity. This meaning-preserving compression adds no behavior or enforcement. Intended files: core/templates/checkpoints/review-result.md; docs/agent-workflow/review-result.md public mirror; generated dist and tracked .claude review-result.md and manifest.txt; this Work Record.

## Implementation progress

The requested sentence is present once beside review identity; roadmap wording retains all obligations while reducing the guide from 699 to 696 estimated tokens under the unchanged 700 cap. Regenerated dist and both isolated native installations match. The existing public guide is synchronized with its declared link rewrites. The first implementation commit omitted that mirror; parity inspection caught it before publishing.

## Evidence

`bash tests/run-all.sh` was attempted against daee9ac and exited 1: budget, schema, Work Record, checker, Redline and tuner passed; hooks failed because the isolated checkout lacks the test-assumed Python environment and the existing python3 launcher cannot load its runtime library. No runtime or test code changed, and these failures are not claimed as passes. Full successful PR CI is required before merge.

The previously unrun package layer passed: source/dist parity, one-build native install parity, committed install parity, internal references, install probe, fresh autocrlf checkout and end-to-end bootstrap simulation. Canonical `bash tests/links/run.sh` passed all 205 Markdown files after relocating the isolated task checkout outside the scanner's excluded parent directory; its initial no-files exit remains a local qualification limitation. No passing broad layers were repeated. Exact sentence, native mirror bytes, budget (696/700), diff whitespace and changed-content privacy checks passed.

## Result review

Agent technical review: independent result review of daee9aca22505599fd43a7c093ed6ef6edeae99c, supplemented by focused public-mirror review of 49caee0c9adabb80902ea84da8684d5dbacbb6ff. No findings. The exact sentence, unchanged roadmap obligations/crosslinks, source/package rewrites and existing ceiling were inspected. No scope or risk escalation. Acceptance requires full successful PR CI plus final workflow/Redline checks; no local verification failure is waived.
Reviewed revision: 49caee0c9adabb80902ea84da8684d5dbacbb6ff
Verification adequacy: local package, link, budget, mirror and policy evidence covers the prose/package change; the complete successful required CI suite remains mandatory before merge because the local full suite failed on environment prerequisites.
