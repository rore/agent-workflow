# Field feedback contract

<!-- agent-workflow:start -->
<!-- A `**Label:**` at the start of a line inside this block is parsed as a field
     header; an unexpected one (unknown or duplicate) fails the record. Keep bold
     sub-headings out of a field's prose value (put such structure below the block,
     or use plain text). -->
**Outcome:**
Agent-workflow reports repeatable, actionable upstream product or skill defects through a shared, context-conscious field-feedback contract.

**Target:**
The agent-workflow skill source, packaged distribution, and dogfood guidance.

**Scope:**
Refine the existing Skill feedback trigger and template; add focused package/link/budget coverage if needed; record the design decision; regenerate dist.

**Constraints:**
Keep normally loaded guidance tiny. Load detailed triggers, filters, privacy rules, deduplication, report schema, and submission steps only after suspected feedback. Preserve one report per task and the unsent fallback. Require user approval before public submission unless automatic reporting was explicitly enabled. Add no service, telemetry, or dependency.

**Completion criteria:**
1. A compact always-visible instruction routes suspected product/skill defects to on-demand guidance.
2. The on-demand guidance filters for repeatability, actionability, upstream ownership, sanitized evidence, and duplicates.
3. Public issue creation requires user approval unless automatic reporting was explicitly enabled; unavailable or declined submission leaves a usable draft.
4. Source and packaged links resolve, budgets remain justified, and the repository test suite passes.

**Risk:**
Elevated

**Complexity:**
Moderate

**Reason:**
Agent instruction and template surfaces are Redline watch paths. The behavior changes issue-submission safety across consuming installs and needs clean-context review, but no runtime or schema changes are expected.

**Discovery:**
The existing flow has seven useful triggers, repeatability/actionability filtering, one-report-per-task, a 200-word redacted issue body, and an unsent fallback. It is skill-specific, hard-codes immediate `gh issue create`, lacks upstream-ownership and duplicate checks, and puts the full trigger table in the Review-result checkpoint. `core/skill/agent-workflow.md`, `core/templates/checkpoints/review-result.md`, and `core/templates/skill-feedback.md` are the operative surfaces; packaging already carries them.

**Material assumptions:**
- The source repository remains `rore/agent-workflow`. Disproof: package metadata or remote points elsewhere. Action: derive or update the target before implementation.
- A compact suspected-defect pointer can replace the Review-result trigger table without reducing detection. Disproof: clean-context review cannot identify when to load the detailed guide. Action: retain the smallest necessary trigger examples at the checkpoint.
- The existing issue body and Work Record fallback can be evolved in place. Disproof: package/link compatibility requires a new artifact. Action: add the smallest compatible reference file.

**Plan:**
1. Keep one compact trigger pointer in the normal skill/review path and move detailed classification into `core/templates/skill-feedback.md`.
2. Extend that on-demand template with upstream ownership, sanitized evidence, open/closed issue deduplication, a bounded cross-product schema, and approval-gated submission while preserving one-report-per-task and Work Record fallback.
3. Update the decision log, package the skill, and add only focused checks not already covered by package/link/budget tests.
4. Run budget/link/package checks, then the full suite. Stop and return to planning if the shared wording requires runtime-specific infrastructure or materially expands beyond guidance.

**Verification plan:**
1. When an agent suspects a product/skill defect, the normally loaded surface shall point to the on-demand guide without carrying detailed policy -> inspect source/dist and budget output.
2. When detailed guidance loads, it shall contain every trigger, filter, privacy, dedupe, schema, and submission rule -> focused content assertions or manual contract review.
3. When submission is not approved or GitHub is unavailable, the agent shall preserve a sanitized draft without publishing -> focused content assertion.
4. When packaged, all links shall resolve and the full repository suite shall pass -> package/link checks plus `bash tests/run-all.sh`.

**Plan review:**
Pending clean-context review.

**Approvals:**
Not required at this risk level

**Exceptions:**
—

<!-- Ready to implement | Blocked | Ready for review -->
**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- Discovery complete. Existing behavior is reusable; this task tightens and generalizes the contract rather than adding a new reporting system.
- Risk assessed as Elevated / Moderate because packaged agent instructions change and the contract includes an external write boundary.

## Evidence

Pending.

## Plan review

Pending clean-context review.

## Result review

Pending.
