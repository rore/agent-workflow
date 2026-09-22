<!-- agent-workflow:start -->
**Outcome:** Repository behavior contracts are declared once in Redline, classified as red contract surfaces, and enforced through Redline review plus Agent Workflow semantic-change records without duplicated path or authority configuration.

**Target:** agent-workflow.

**Scope:** Normative behavioral-integrity design; Redline policy schema, reporter, checkpoint ownership, bootstrap guidance, and documentation; Agent Workflow configuration, checker integration, Work Record guidance, tests, and generated/install artifacts affected by moving repository contract ownership into Redline.

**Constraints:** Reuse Redline paths, checkpoints, CODEOWNERS, and modes. Keep task-local requirement baselines unchanged. Do not retain two canonical path lists, add a separate approval-authority subsystem, scan test semantics, or introduce a new top-level verdict when existing RED/MIXED plus structured detail suffices. Preserve fail-closed mutation integrity and external required-CI enforcement.

**Completion criteria:** A configured behavior-contract path is canonically defined by Redline, reported as a red contract surface with path-specific review evidence, and consumed by Agent Workflow for complete equivalent/coverage-only/requirement-change records and verification linkage; bootstrap, public docs, package artifacts, focused tests, and the full suite agree on that model.

**Requirement baseline:** {"source":"user-request:406220eb-37cf-4fa6-9e00-125f66142caa","outcome":"Repository behavior contracts are declared once in Redline, classified as red contract surfaces, and enforced through Redline review plus Agent Workflow semantic-change records without duplicated path or authority configuration.","scope":"Normative behavioral-integrity design; Redline policy schema, reporter, checkpoint ownership, bootstrap guidance, and documentation; Agent Workflow configuration, checker integration, Work Record guidance, tests, and generated/install artifacts affected by moving repository contract ownership into Redline.","constraints":"Reuse Redline paths, checkpoints, CODEOWNERS, and modes. Keep task-local requirement baselines unchanged. Do not retain two canonical path lists, add a separate approval-authority subsystem, scan test semantics, or introduce a new top-level verdict when existing RED/MIXED plus structured detail suffices. Preserve fail-closed mutation integrity and external required-CI enforcement.","completion_criteria":"A configured behavior-contract path is canonically defined by Redline, reported as a red contract surface with path-specific review evidence, and consumed by Agent Workflow for complete equivalent/coverage-only/requirement-change records and verification linkage; bootstrap, public docs, package artifacts, focused tests, and the full suite agree on that model."}

**Risk:** High

**Complexity:** Moderate

**Reason:** The correction changes normative governance, both schemas, Redline classification/checkpoint evidence, and Agent Workflow's non-waivable contract gate. It is one coherent repository change but spans several coupled components.

**Discovery:** Initial design review found that behavior-contract paths currently live only in agent-workflow.yaml, so Redline can classify an authoritative contract test as blue while Agent Workflow independently protects it. Existing Redline red zones, custom checkpoints, CODEOWNER satisfaction, vertical-signal details, and modes provide most required primitives; current checkpoint owner calculation is whole-diff rather than trigger-path-specific.

**Material assumptions:** CODEOWNERS can represent repository authority for protected contract paths; evidence that repositories require a distinct non-CODEOWNER authority returns the design to planning. One compatible path/check set remains sufficient for v1; evidence of active multi-owner/check consumers returns schema shape to planning. Existing RED/MIXED verdicts plus structured behavior-contract detail are sufficient; evidence that consumers require a distinct top-level verdict returns reporter design to planning.

**Plan:** 1. Amend the normative spec and supersede the 2026-09-20 repository-contract decision: keep task baselines unchanged, but make Redline the sole owner of repository contract paths, CODEOWNERS authority, and review routing. 2. Add one optional Redline behaviorContracts block with unique safe paths, verification, and checkpoint. Matched paths override excludes and broader blue rules, classify red, and trigger the configured checkpoint from the exact matched paths. Policy loading rejects a missing checkpoint or one whose satisfaction is not CODEOWNER-only. Redline resolves each affected path with GitHub's last-matching CODEOWNERS rule and emits versioned deterministic behaviorContractChanges facts: detected, exact path plus canonical owner tokens, verification, and checkpoint. Work Records retain semantic classification and exact approval evidence; existing top-level verdicts remain unchanged. 3. Scope local checkpoint evaluation to the matched paths and bootstrap only one set with compatible non-empty CODEOWNERS owners. User-owner intersection remains Redline's local best effort; team membership and actual approval remain enforced by required Code Owner review in the hosting platform. Checkpoint satisfaction remains distinct and follows Redline modes/platform governance. 4. Remove Agent Workflow's duplicate paths/approvalAuthority model, explicitly reject the legacy block despite permissive top-level schema handling, and replace every cfg.behavior_contracts/applicability call site with strict consumption of Redline detail. The checker rejects unsupported payload versions and malformed, duplicate, unsafe, non-red, out-of-diff, ownerless, or incompatible-owner entries; requires exactly one Work Record classification per reported path; and for requirement-change requires repository authority.name and approval.by to match one canonical owner token for that path plus exact approval-shaped evidence. It separately requires the reported checkpoint to be present in Redline and the reported verification identifier in an affected Work Record. A legacy reporter cannot accept the new Redline block because its closed policy schema rejects it, so configured contracts fail before producing a verdict; stale detail is rejected against the trusted current path set, while old verdicts remain accepted for policies without this feature. 5. Align bootstrap: candidates require an existing required-CI identifier, live required-status evidence, path-covering compatible CODEOWNERS evidence, and live required Code Owner review; require explicit selection; write the block and CODEOWNER-only checkpoint into the Redline draft; include CODEOWNERS/self-protection actions in the proposal; and omit unresolved candidates. 6. Update focused schema/reporter/checker tests, packaged consumer E2E in two layouts, public docs, installed/generated copies, and run the full suite. Stop and return to planning if selected paths need incompatible verification/checkpoint/owner groups, CODEOWNERS cannot express the authority, or existing verdicts plus structured detail cannot support the fail-closed gate.

**Verification plan:** When a selected path is also covered by a blue rule, Redline shall classify it red, emit the exact path/check/verification detail, and require the path-scoped checkpoint → Redline schema, unit, and reporter golden tests. When Agent Workflow receives a changed behavior-contract detail, it shall fail closed on incomplete path evidence, missing/duplicate classification, wrong checkpoint authority, missing exact approval, or missing verification linkage → focused checker tests. When bootstrap finds supported candidates, it shall require explicit selection and generate Redline policy/checkpoint plus CODEOWNERS guidance; when evidence is missing it shall omit them → packaged bootstrap consumer E2E across both fixture layouts. When the feature ships, source/public/dist guidance shall agree and legacy Agent Workflow configuration shall fail loudly → schema, link, package, and documentation checks. When all changes are complete, the repository shall pass tests/run-all.sh and the final task-local checker with fresh Redline evidence.

**Plan review:** Clean-context review by /root/alignment_plan_review approved the twice-revised plan; approved by user 2026-09-22: "i approve".

**Approvals:** Approved by user 2026-09-22: "approve"

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

- Moved repository behavior-contract configuration to Redline as one optional `behaviorContracts` block: paths, required-CI verification identifier, and a dedicated CODEOWNER-only checkpoint. Removed and explicitly rejected the legacy Agent Workflow block.
- Made matching contract paths override exclusions and broader blue zones, classify red, use base-revision GitHub CODEOWNERS last-match semantics, and emit deterministic versioned per-path owner facts without creating another verdict class or authority system.
- Made Agent Workflow correlate those facts with the current Redline policy and changed paths, then fail closed on missing or stale evidence, malformed owners, incomplete semantic classifications, wrong repository authority, absent exact approval, or missing verification linkage.
- Kept hosting-platform governance authoritative for team membership and required Code Owner review. Added CI refresh on submitted or dismissed PR reviews so binding checkpoint state cannot remain stale.
- Aligned bootstrap to propose only explicitly selected candidates backed by live required-CI, base CODEOWNERS, and required Code Owner review evidence. Added packaged E2E coverage for two repository layouts and two contract roots.
- Updated the normative specification first, decision history, enforcement/integration/Redline/default-profile guidance, public behavioral-integrity docs, roadmap detail, schemas, generated distribution, and local installs.

## Evidence

- Checkout started clean at `8b0f7161bf131856836b18f10caa9df0bda0c808` on `origin/main`.
- Focused local reporter/checker regression suite: 215 passed. Independent result-review rerun: 235 focused tests passed.
- Full supported local Windows Python suite: 495 passed. Redline schema fixtures, skill-YAML fragments, and all 26 reporter goldens passed.
- Local WSL checks: hooks passed; all 194 Markdown files had valid links; package parity/install and packaged two-layout bootstrap E2E passed; all 20 skill-budget files remained within limits.
- Independent result review reran package parity and the complete `tests/run-all.sh`; all layers passed.
- `git diff --check` passed with only line-ending normalization warnings. Source was packaged and reinstalled locally after the final implementation changes.
- Final task-local checker passed every blocking predicate after human result approval; the repository's shadow-mode `architecture-review` checkpoint remains advisory until PR governance supplies its label or CODEOWNER approval.
- Implementation revision: `8fc0cd8506809fbb4d43e23af9c318eaf580bbeb`.

## Plan review
Initial clean-context review rejected the draft pending exact payload validation, CODEOWNERS semantics, exclude precedence, explicit legacy migration, old-reporter behavior, and full bootstrap evidence. The revised plan makes contract paths override excludes/blue rules; constrains the checkpoint to CODEOWNER-only satisfaction and compatible owner sets; emits versioned per-path canonical CODEOWNERS owners using last-match semantics while keeping semantic classifications in Work Records; validates repository authority separately from checkpoint routing; rejects the legacy Agent Workflow block; relies on the old Redline schema's closed top level to fail a new policy loudly; and requires live required-status, required Code Owner review, and path-covering CODEOWNERS evidence in bootstrap. The final clean-context re-review approved this separation with no blocking findings. User approved the finalized plan on 2026-09-22: "i approve".

## Result review

Clean-context review by `/root/behavior_contract_result_review` approved the result with no blocking code, governance, security, compatibility, test, documentation, packaging, scope, or bookkeeping findings. The reviewer independently passed 235 focused tests, package parity, and every layer of `tests/run-all.sh`. Separate human result approval remains required for this High-risk task.

## Skill feedback

Trigger 3 dropped: the current task's packaged bootstrap fixture initially omitted the relocated Work Record from its fixture-specific blue zone. The E2E caught it before review, the fixture was corrected, and no released defect remained.