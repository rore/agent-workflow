# Implementation handoff decisions

<!-- agent-workflow:start -->
**Outcome:** Implementation handoffs carry settled caller-visible behavior decisions in the same Work Record or precise authoritative links, kept current under existing change rules.

**Target:** agent-workflow

**Scope:** Clarify the existing Hand-off readiness text in core/templates/checkpoints/plan-and-review.md and regenerate isolated repository skill mirrors and manifests.

**Constraints:** Preserve the immutable original baseline and existing behavior-change authority. No SPEC or policy changes, new schema, gate, matrix, decision artifact, runtime or duplicated Coordination adoption checks. No consumer or live-installation changes; no private incident details. Keep existing token ceilings and required controls.

**Completion criteria:** Before implementation assignment, settled caller-visible decisions are recorded or precisely linked in the same Work Record; later decisions use existing current-context/change rules without baseline rewrites; concrete handoff and later-change review, instruction budgets, packaging and required repository checks pass.

**Requirement baseline:**
{"source":"work-record-initial","outcome":"Implementation handoffs carry settled caller-visible behavior decisions in the same Work Record or precise authoritative links, kept current under existing change rules.","scope":"Clarify the existing Hand-off readiness text in core/templates/checkpoints/plan-and-review.md and regenerate isolated repository skill mirrors and manifests.","constraints":"Preserve the immutable original baseline and existing behavior-change authority. No SPEC or policy changes, new schema, gate, matrix, decision artifact, runtime or duplicated Coordination adoption checks. No consumer or live-installation changes; no private incident details. Keep existing token ceilings and required controls.","completion_criteria":"Before implementation assignment, settled caller-visible decisions are recorded or precisely linked in the same Work Record; later decisions use existing current-context/change rules without baseline rewrites; concrete handoff and later-change review, instruction budgets, packaging and required repository checks pass."}

**Relationships:**
{"schema_version":1,"sources":null,"pull_requests":[]}

**Risk:** Elevated

**Complexity:** Simple

**Reason:** Agent-loaded checkpoint and generated instruction surfaces are gray/watch, setting an Elevated floor. This applies an existing normative requirement at one handoff point without changing the contract or controls.

**Discovery:** Current main is 29c508a350942d2127c337655907fb02cc8cfdb0. SPEC sections 6 and 9.1 already require material decisions, authoritative links, current-context changes and baseline preservation. Hand-off readiness only lists populated fields, and delegation only supplies record path/scope/authority. No equivalent explicit pre-assignment instruction was found.

**Material assumptions:** The normative behavior already exists. Stop and report exact citations if current main supersedes the gap or if the proposed wording needs a new authority or gate.

**Plan:** Add one sentence under Hand-off readiness requiring settled caller-visible behavior decisions or precise authoritative links in the same Work Record before assigning implementation, maintained through the existing behavioral-integrity guide without rewriting the original baseline. Keep the existing field-presence requirements; compress only the adjacent shape headers, readiness list and opening review sentence to fit the unchanged 900-token ceiling. Do not edit SPEC or operating-mode because the normative obligations and existing delegation pointer already suffice. Regenerate dist and isolated repository mirrors; no extra decision document or mechanical prose test. Stop if this changes authority, introduces a new gate or cannot preserve existing controls within budget.

**Verification plan:**
- manual: Review a concrete caller-visible decision handoff with a precise source link, a later behavior change under existing authority and unchanged baseline, and a routine implementation detail that needs no new approval.
- Existing instruction and package checks -> Run unchanged budgets, mirror parity, links and required repository tests before publication; verify final-head CI and review findings before merge.

**Plan review:** Agent technical review: independent non-implementer review accepted c740e5aec632ee664bca536b49b8f8aab7388507 against main 29c508a350942d2127c337655907fb02cc8cfdb0. No blocking finding; existing normative behavior and authority suffice. See Plan review below.

**Approvals:** Not required at this risk level. The bounded conditional user authorization and manager assignment are retained privately; no approval quote is invented.

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

- Verified the conditional gap against freshly fetched main and recorded context/classification before implementation planning. Independent technical plan review accepted the bounded existing-checkpoint clarification; ready for implementation with no source edit yet.
- Added the pre-assignment sentence at Hand-off readiness and compacted only adjacent field headers, readiness text and the introductory review sentence. All field-presence, review, approval, exception and authority controls remain. Regenerated dist and both isolated repository skill mirrors; all 23 budgets pass, with plan-and-review at 898/900 tokens and no ceiling increase.
- Independent technical result review accepted 8a1a828a7b21216407c9f5492a23cb661437d53b without blocking findings. The full repository suite is running once; State remains Ready to implement until verification completes. Reconciled the recovery next action to the current verification/delivery stage.
- The single full-suite run at 8a1a828a7b21216407c9f5492a23cb661437d53b exited 2 after seven passing layers: links detected the existing public guide mirror was not synchronized. Package checks had not run. Blocked only on synchronizing docs/agent-workflow/plan-and-review.md and running links plus the remaining package layer. No earlier passed check is claimed to cover the missing mirror.
- Synchronized the existing public guide with the reviewed source and its declared link rewrite. Independent review accepted the repair at 268b302a62e7146d8be66479b24f0b99bdd1e0a4 with no outstanding findings. Links and the complete remaining package layer each passed with exit 0; the earlier seven passing layers are reused. The original full-run exit remains 2 and is not represented as a passing final-revision full invocation. Final-head CI remains required before merge.

## Plan review

Independent review accepted the plan and Elevated/Simple classification at c740e5aec632ee664bca536b49b8f8aab7388507. Existing SPEC sections 6 and 9.1 already govern decisions and later changes; the handoff point needs only the direct reminder and existing behavioral-integrity link. A vague issue/document link is insufficient. A later material change stays proposed until the applicable authority accepts it; then current context/ordered change entries and decision references update while the original baseline remains intact. Routine mechanics require no additional approval. Planned scenario, budget, existing-control, link, package and repository checks are adequate.

## Handoff example for review

Illustrative task: the settled caller-visible requirement is that a missing item returns 404. Before assigning its implementation, the owner records that decision in the same Work Record or links the exact authoritative contract revision and missing-item section; a generic document or issue link does not identify the decision sufficiently.

If 200/null is proposed later, 404 remains current until the applicable authority approves that exact departure under the existing rules. After approval, update current Task Context, the ordered change entry and decision/source reference while retaining the original 404 baseline. Refactoring lookup mechanics while preserving 404 requires no additional approval. This example creates no new product requirement or approval gate.

## Result review

Agent technical review: independent non-implementer review accepted the final source, generated scope and illustrative handoff/later-change case without blocking findings.

Reviewed revision: 268b302a62e7146d8be66479b24f0b99bdd1e0a4

Verification adequacy: the sentence applies to both record shapes, precise sources expose the settled decision, later changes retain applicable authority and baseline integrity, and compaction preserves existing fields and risk-specific reviews/approvals. Independent review accepted the public mirror parity repair and reuse of seven passing layers with passing links and package checks. Budgets and whitespace also pass. Exact-final-head full-suite CI remains required before merge; no observed live adoption is claimed.

## Recovery

- Branch: feat/implementation-handoff-decisions. Work Record: agent-workflow:implementation-handoff-decisions at .agent-workflow/tasks/implementation-handoff-decisions.md.
- Initial clean base: 29c508a350942d2127c337655907fb02cc8cfdb0. Last reviewed source and public guide: 268b302a62e7146d8be66479b24f0b99bdd1e0a4. Local verification is complete with the original failure and passing link/package repair accurately recorded. Next publish, verify exact-head CI and all review threads, then merge within the authorized scope. Work Record-only evidence/link updates preserve the reviewed source.
- Prior completed task checkouts and necessary private evidence remain untouched. No exact external source tuple was supplied; do not invent one.
