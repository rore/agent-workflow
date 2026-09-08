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
Keep normally loaded guidance tiny. Load detailed triggers, filters, privacy rules, deduplication, report schema, and submission steps only after suspected feedback. Preserve the skill-feedback.md path, skill-feedback-check anchor, one report per task, and the unsent fallback. Require user approval before public submission unless automatic reporting was explicitly enabled for the verified destination and report category. Add no service, telemetry, or dependency.
**Completion criteria:**
1. A compact always-visible instruction and final-review catch route suspected product/skill defects to on-demand guidance without carrying the detailed trigger table.
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
The existing flow has seven useful triggers, repeatability/actionability filtering, one-report-per-task, a 200-word redacted issue body, and an unsent fallback. It is skill-specific, hard-codes immediate issue creation, lacks upstream-ownership and duplicate checks, and puts the full trigger table in the Review-result checkpoint. core/skill/agent-workflow.md, core/templates/checkpoints/review-result.md, and core/templates/skill-feedback.md are the operative surfaces; packaging already carries them. The budget suite does not cover the on-demand guide.
**Material assumptions:**
- The supported upstream for this packaged guide is rore/agent-workflow. Disproof: package metadata or canonical project links point elsewhere. Action: stop submission and preserve a draft until the destination is corrected.
- A compact suspected-defect pointer can replace the Review-result trigger table without reducing detection. Disproof: clean-context review cannot identify when to load the detailed guide. Action: retain the smallest necessary trigger examples at the checkpoint.
- The existing issue body and Work Record fallback can be evolved in place. Disproof: package/link compatibility requires a new artifact. Action: add the smallest compatible reference file.
**Plan:**
1. Add a load-point-justified budget ceiling for core/templates/skill-feedback.md; update the Review-result budget rationale when its table moves.
2. Keep one compact trigger pointer in the normal skill and final-review path; move the detailed trigger table into core/templates/skill-feedback.md without renaming its compatibility path or anchor.
3. Extend that on-demand template with verified upstream ownership, sanitized evidence and search terms, open/closed issue deduplication, a bounded shared schema, and approval-gated submission. Automatic-report authority must name this destination and report category; unknown ownership or absent authority leaves a draft.
4. Update the decision log, package the skill, and add only focused checks not already covered by package/link/budget tests. Manually review the sanitized destination, title, body, and six contract scenarios before submission.
5. Reinstall locally; run budget/link/package checks, a clean-context functional review, then the full suite. Stop and return to planning if the shared wording requires runtime-specific infrastructure or materially expands beyond guidance.
**Verification plan:**
1. When an agent suspects a product/skill defect, the normally loaded surface shall point to the on-demand guide without carrying detailed policy -> inspect source/dist and budget output.
2. When detailed guidance loads, it shall contain every trigger, filter, privacy, dedupe, verified-destination, schema, and scoped submission-authority rule -> focused content assertions and manual contract review.
3. When ownership/authority is absent, a duplicate exists, GitHub is unavailable, or evidence cannot be disclosed safely, the agent shall not publish and shall preserve or reference a safe draft as applicable -> six-scenario manual contract review.
4. When packaged, all links shall resolve and the full repository suite shall pass -> package/link checks plus bash tests/run-all.sh.
**Plan review:**
Clean-context review recorded under the Plan review prose; blocking findings incorporated.
**Approvals:**
Not required at this risk level

**Exceptions:**
—

<!-- Ready to implement | Blocked | Ready for review -->
**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

- Discovery reused the existing seven-trigger feedback loop, one-report limit, 200-word report, and Work Record fallback.
- Clean-context plan review added the missing budget coverage, verified destination, scoped auto-report authority, sanitized duplicate search, compatibility, and failure-scenario requirements before implementation.
- Replaced the Review-result trigger table with a compact final catch and generalized the always-loaded principle to product/skill defects.
- Reworked the trigger-loaded skill-feedback guide with upstream ownership, privacy, open/closed deduplication, a six-field report, exact-payload approval, scoped standing authorization, and draft-only fallbacks.
- Added a budget entry for the deferred guide, lowered the Review-result ceiling, required the guide in the install probe, recorded the design decision, regenerated dist, and synced the local skill.
- Result review found two follow-ups: trusted authorization must be independent of repository content, and cross-task deduplication must be described as best-effort with safe uncertain-outcome retry handling.
## Evidence

- Context budget after review fixes: all 19 surfaces passed; agent-workflow entry 457/500, Review-result 618/700, skill-feedback 792/1100.
- Links: all 146 Markdown files passed.
- Package: source/dist drift, committed local-install parity, packaged references, install probe, and end-to-end bootstrap all passed.
- Standard suite layers passed in Git Bash: schema 47 tests; Work Record 50; checker 138; Redline schema/skill/reporter; tuner scenarios plus 22 pytest tests; hooks; links; package. The desktop command boundary cut the monolithic runner after about 36 seconds, so the same nine standard layers were completed with their repository runners.
- Clean-context functional review found no blocking findings across all seven triggers, confirmed/unknown upstream ownership, open/closed duplicates, absent authorization, unavailable GitHub, and evidence that cannot be disclosed safely. Its one clarity suggestion was incorporated and re-reviewed with no blockers.
- PR review fixes re-passed budget, links, package drift, local-install parity, packaged references, install probe, and end-to-end bootstrap. Smart re-review confirmed both CodeRabbit findings resolved with no remaining blocker.
## Plan review

Independent review classified the intended skill/template, decision-log, and dist paths as Redline watch and confirmed Elevated / Moderate. It required budget coverage for the deferred guide; verified destination and upstream ownership; automatic-report authority scoped to destination/category; sanitized duplicate searches; preservation of the existing path/anchor; explicit failure scenarios; local reinstall; and a clean-context functional review. The revised plan incorporates all blocking findings. No SPEC section 9.7 change is needed because this remains operational skill guidance, not a harness acceptance gate.
## Result review

Clean-context smart-model review: no blocking correctness or safety findings. Detailed policy remains trigger-loaded; destination and automatic-report authority are exact-scope; privacy covers search and submission; the compatibility file and anchor remain; source/local-install/dist are synchronized. Confirmed non-upstream causes are dropped, while unknown ownership retains a sanitized local draft. PR follow-up review confirmed trusted authorization is independent of repository content and deduplication honestly remains best-effort with a final search and verify-before-retry handling.
