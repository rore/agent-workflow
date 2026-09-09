<!-- agent-workflow:start -->
**Outcome:**
When a repository already uses a roadmap and completed work affects a tracked item's progress or scope, result review keeps that item accurate; unrelated work and repositories without an applicable roadmap item incur no roadmap ceremony.

**Target:**
The normative result-review contract and its existing agent-loaded checkpoint.

**Scope:**
Add one conditional roadmap-reconciliation obligation to `docs/SPEC.md` §9.7 and `core/templates/checkpoints/review-result.md`; record the decision; regenerate only required packaged/install copies and this Work Record.

**Constraints:**
No new workflow stage, operating-mode step, Work Record field, schema/checker logic, repository scan, automatic feature split, Minimap-specific path/status, mandatory roadmap diff, or installation requirement. Preserve reviewer independence, human-approval, and Redline obligations. Standalone bugs may have no roadmap item.

**Completion criteria:**
Result review triggers reconciliation only when an existing repository roadmap applies and work affects a tracked item's progress or scope; it distinguishes item status from shipped scope and covers remaining scope, obsolete next steps, placement, and directly affected prerequisites; it explicitly permits no edit when already accurate and skips when no roadmap/item applies; source/package copies agree, the checkpoint remains within 700 tokens, and all tests/CI pass.

**Risk:** Elevated

**Complexity:** Simple

**Reason:**
Redline classifies `docs/SPEC.md` as a red normative-spec surface requiring `architecture-review`; no boundary violation exists. The change is one coherent documentation/skill rule with generated-copy synchronization.

**Discovery:**
SPEC §9.7 and `review-result.md` already own completion review but do not mention roadmap reconciliation. `review-result.md` is exactly at its 700-token ceiling, so new operational wording must replace non-load-bearing narration/restatement rather than raise the ceiling. Operating mode, schemas, and checker need no change. The independent design review approved the two-location approach with narrower trigger and status/scope wording.

**Material assumptions:**
Existing surrounding Work Record/PR prose can hold the brief reconciliation result without a new field. Disproof: independent result review finds the location ambiguous. Action: clarify the checkpoint sentence without adding schema. Generated copies should change only through existing install/package scripts. Disproof: package check identifies another required source. Action: synchronize only that required copy.

**Plan:**
1. Add the conditional invariant to SPEC §9.7. 2. Append the decision rationale. 3. Add the operational rule to `review-result.md`, deleting its narrative opening and compressing only redundant Redline ownership prose so all existing obligations remain explicit within 700 tokens. 4. Reinstall/package through repository scripts. 5. Verify focused wording, budgets, links/package parity, full suite, and CI. Stop if fitting the rule would require dropping an existing obligation or raising the ceiling.

**Verification plan:**
- Conditional trigger, explicit skips, and status-versus-shipped-scope distinction → exact diff review against approved wording plus clean-context result review.
- Existing review/approval/Redline obligations remain intact → semantic comparison of pre/post checkpoint and SPEC §9.7.
- Thin/package-correct skill → `bash tests/budget/run.sh --verbose`, link/package checks, and source/dist/install comparison.
- Repository remains green → `bash tests/run-all.sh` locally and PR CI.

**Plan review:**
Approved with exact corrections by clean-context Codex task `01a07bef-18c8-71b2-89ab-c0cbe91e73ad`; details below.

**Approvals:**
Not required at this risk level.

**Exceptions:**
—

<!-- Ready to implement | Blocked | Ready for review -->
**State:** Ready for review
<!-- agent-workflow:end -->

## Plan review

The independent reviewer approved the existing SPEC §9.7 plus `review-result.md` locations. Required corrections incorporated here: trigger when an existing roadmap applies and work affects a tracked item's progress or scope; say item status and shipped scope; preserve explicit skip/no-edit cases and all existing reviewer, human-approval, and Redline obligations. No operating-mode, schema, or checker change.

## Implementation

Branch: `feat/roadmap-reconciliation`.

Revision `981c99d` adds the conditional SPEC §9.7 obligation and operational result-review rule, records the design decision, and synchronizes the dist/dogfood copies. No operating-mode, schema, checker, or roadmap-tool-specific behavior changed.

## Evidence

- Budget: `review-result.md` is 679/700 estimated tokens; all 19 budget checks pass with no ceiling change.
- Full local suite: 257 Python tests plus Redline, tuner fixtures, hooks, links, and package/bootstrap E2E passed.
- Packaging: source, dist, and `.claude` checkpoint bytes match; generated manifests match.
- Integrity: `git diff --check` passed.
- PR CI: pending.

## Result review

High-reasoning independent review task `/root/roadmap_result_review` approved `981c99d` against `main` with no source findings. It checked all conditional/no-op scenarios and confirmed existing reviewer independence, human approval, Redline, unavailable-evidence, and merge-thread obligations remain intact.