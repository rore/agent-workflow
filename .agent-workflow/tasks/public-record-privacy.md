# Redact private provenance from a public Work Record

Source: the maintainer's standing public-documentation privacy directive. The affected artifact was published with [PR 58](https://github.com/rore/agent-workflow/pull/58). Original operational evidence remains private and local; no private instruction or session pointer is reproduced here.

<!-- agent-workflow:start -->
**Outcome:** The known public Work Record no longer discloses private provenance or operational details.
**Target:** agent-workflow
**Scope:** Current-content redaction of .agent-workflow/tasks/core-behavior-preservation.md, necessary publication surfaces, and this correction record; preserve original evidence in ignored local storage.
**Constraints:** Preserve product behavior, requirement meaning, review authority and existing enforcement. No broad audit, shared-history rewrite, force-push, record deletion, live installation or configuration change. Public evidence uses repository-relative references, public URLs and generic placeholders.
**Completion criteria:** Remove known private references from current public content through a supported workflow route; preserve behavioral/audit meaning privately; pass targeted checker and publication-privacy validation, independent review and required repository checks; report the correction revision and historical exposure that remains.
**Requirement baseline:**
{"source":"maintainer-privacy-directive","outcome":"The known public Work Record no longer discloses private provenance or operational details.","scope":"Current-content redaction of .agent-workflow/tasks/core-behavior-preservation.md, necessary publication surfaces, and this correction record; preserve original evidence in ignored local storage.","constraints":"Preserve product behavior, requirement meaning, review authority and existing enforcement. No broad audit, shared-history rewrite, force-push, record deletion, live installation or configuration change. Public evidence uses repository-relative references, public URLs and generic placeholders.","completion_criteria":"Remove known private references from current public content through a supported workflow route; preserve behavioral/audit meaning privately; pass targeted checker and publication-privacy validation, independent review and required repository checks; report the correction revision and historical exposure that remains."}
**Relationships:**
{"schema_version":1,"sources":null,"pull_requests":[]}
**Risk:** Elevated
**Complexity:** Simple
**Reason:** Intended Work Record paths are blue, with no boundary or runtime changes. Raised for publication privacy and immutable provenance/audit-integrity risk; no enforcement relaxation is assumed.
**Discovery:** SPEC 9.1/13.3 and `core/checker/predicates.py` compare the entire committed baseline, including source. `requirements.baseline_unchanged` is explicitly non-waivable, so the source-only mechanism merged in [PR 59](https://github.com/rore/agent-workflow/pull/59) at `a2a01cf682fc967f6cd9e91717a89a03fe15cb87` does not automatically authorize migrating this record. Any migration needs this exact record path and anchor, plus approval before the migration. Protected functional baseline/current-context wording also contains private operational details, so the source-only mechanism cannot complete full remediation. The already-reviewed ten-line unprotected prose redactions are ready for independent Result review, required checks and a normal PR.
**Material assumptions:** Keep the protected source and all five Task Context fields, the requirement baseline, risk, complexity and approval authority unchanged. The merged source-only mechanism does not itself authorize this record's migration; its exact path and anchor must be covered and approval obtained first. Do not remove records, weaken enforcement or claim full privacy remediation. The previously reviewed unprotected redactions remain separately eligible for Result review and publication.
**Plan:** Preserve the independently reviewed unprotected redactions, using generic role attestations and public PR/commit references. Keep both marker blocks, all five Task Context fields, the requirement baseline, approval authority and functional meaning intact. The accepted plan review covers these unprotected redactions; no duplicate plan approval is needed while that plan is unchanged. Record the source-only mechanism's merged status and its limits. A proposal for the broader protected-text migration and its exact gate remains pending; make no protected edit or normative/checker/schema change until the exact record path and anchor are covered and approval is obtained. Full privacy remediation remains incomplete.
**Verification plan:**
- Current-content privacy -> inspect the one affected artifact and necessary publication surfaces, scan replacement text and added diff content without printing private values.
- Requirement/audit integrity -> compare exact original privately, exercise baseline/history validation and verify no product/checker/policy/schema change.
- Safe delivery -> independent plan/result review, required repository checks and normal PR; report retained historical exposure without rewriting it.
**Plan review:** Agent technical review: independent non-implementer plan review accepted unprotected redactions only; full remediation remains blocked. Private review evidence is retained locally; see Plan review below.
**Approvals:** Not required at this risk level. The standing maintainer directive authorizes current-content privacy removal, not history rewriting or enforcement weakening.
**Exceptions:** —
**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

Applicability requires the workflow: Work Records are never ordinary-documentation exemptions. Initialized a separate isolated task from public main df8639da94916bc8f8a879f71f8eba59fc2b43e2 and classified before implementation. The completed feature is not reopened. Only the known artifact and necessary publication surfaces are in scope.

## Partial implementation and evidence

Unprotected prose now uses generic authority attestations and public artifact references. Removed ignored-evidence locations, unrelated coordination context and proposal fingerprints. The entire original subject marker block is byte-identical, including Task Context, baseline, approvals and State. Exact original evidence remains private; no private before-values or their hashes were added to public evidence.

Fresh publication history starts at public main a2a01cf682fc967f6cd9e91717a89a03fe15cb87. This task's valid immutable baseline was committed before the prose correction. The final two-file tree equals the independently accepted content, and scans cover both the current added diff and every new commit's added content. Earlier unpublished review drafts are excluded from this branch's ancestry. No shared history was rewritten.

Actual two-path Redline exits 0. The actual base/head checker has no blocking failures; exit 1 is solely the commit-order advisory for the pre-existing completed subject record. That record predates this branch, and this correction's own planning record precedes the prose edit. No waiver or enforcement change is used.

All nine local layers report success across the hooks and remaining-eight invocations against unchanged source/package code. The remaining-eight run captured exit 0. The hooks log reports successful assertions and layer completion, but its wrapper did not retain a separate raw exit code; it is not claimed as captured. Temporary test setup was removed. Final PR CI must independently pass the complete suite before merge.

## Result review

Agent technical review: independent non-implementer accepted the partial result and unchanged-plan reuse at 42f6d2a49a259746b8c3eaf9edea806e38ea1803 after correcting its privacy and stale-route findings. No new actionable findings. Authority boundaries, verification distinctions and protected content are preserved.

Reviewed revision: 42f6d2a49a259746b8c3eaf9edea806e38ea1803.

Verification adequacy: sufficient for partial publication, conditional on final PR CI. Exact protected-byte comparison, fresh added-history privacy scan and actual classifier/history-aware checker support the unchanged-application review. Full remediation remains Blocked: protected source and functional wording require a specifically approved supported route. Historical public exposure remains; this change does not erase it.

## Recovery

Independent plan review is already complete for the unchanged unprotected-redaction plan. The ten-line redactions are ready for independent Result review, required checks and a normal PR. The source-only mechanism merged in [PR 59](https://github.com/rore/agent-workflow/pull/59) at `a2a01cf682fc967f6cd9e91717a89a03fe15cb87`, but does not automatically authorize migrating this record; the exact path and anchor must be covered and approval obtained first. Protected functional baseline/current-context wording also contains private operational details, so full remediation remains blocked and the original outcome/completion criteria remain unsatisfied. Make no product, enforcement or live-environment change. Keep private original evidence ignored/local; do not repeat removed values in public content, PR descriptions or review replies. Canonical provider tuples were not supplied, so Relationships sources stays unresolved rather than guessed.

## Discovery evidence

The record's earlier plan-review concern is stale: independent review accepted the unprotected-redaction plan. The source metadata conflict remains governed by SPEC 13.3, the baseline predicate and the explicit non-waivable set; an ordinary exception is not a supported workaround. Source-only engine PR 59 is merged, but it does not automatically authorize this record's migration. Protected functional wording also contains private operational details. The broader protected-text proposal and exact gate remain pending; the existing partial redactions are ready for Result review, required checks and a normal PR.

Extending the source-only mechanism to protected functional text would change a normative/checker contract and requires separately reviewed explicit scope and approval. Existing source-only adoption uses PR 59's exact record/anchor/replacement authorization gate. This task authorizes neither extension, a blanket exception, forged approval, shared-history rewriting nor live changes.

## Plan review

Agent technical review: independent non-implementer review accepted the unprotected-redaction plan. Preserve exact baseline/current functional fields, approval authority, historical validation distinctions and truthful partial status; validate with actual base/head history and independent result review. PR 59 now supplies a source-only route, but this record lacks its specific authorization and protected functional text remains unsupported. Protected functional wording also contains private operational ownership details, so a source-only migration cannot finish this record's cleanup. No human approval of a new governance contract is claimed.

The maintainer-requested proposal for broader protected-text migration, including exact path/anchor and approval gate, remains pending. The accepted independent plan review already covers the unchanged unprotected-redaction plan; no duplicate plan approval is needed. The partial ten-line unprotected redactions are ready for independent Result review, required checks and a normal PR. This record remains Blocked and its original full outcome and completion criteria remain unsatisfied. No functional mechanism, history rewrite, generic exception framework or second source-only mechanism is authorized.
