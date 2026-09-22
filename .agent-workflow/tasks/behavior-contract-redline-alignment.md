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

**Plan:** Complete caller/schema/bootstrap discovery, then amend this plan before implementation. Prefer one Redline behaviorContracts block using existing paths/checkpoint concepts plus the minimum verification metadata; make matching paths red and emit affected-path detail; make Agent Workflow consume that trusted detail while retaining Work Record semantic classifications and exact approval records; remove duplicated Agent Workflow path/authority configuration; update bootstrap, docs, tests, and generated artifacts.

**Verification plan:** Canonical Redline configuration, red classification, exact affected paths, path-scoped CODEOWNER satisfaction, fail-closed changed-path evidence, semantic classification/approval, and verification linkage → focused schema/reporter/checker tests. Bootstrap and shipped copies → packaged bootstrap/install tests. Normative/public consistency and links → documentation parity/link checks. No regressions → complete repository suite and final local checker with fresh Redline evidence.

**Plan review:** Pending human review after discovery completes and the plan is finalized.

**Approvals:** Approved by user 2026-09-22: "so we should rewrite and fix this feature to align it properly"

**Exceptions:** —

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- Established the corrective task from the design review; applicability requires the normal workflow because governance schemas, reporter/checker code, and normative specification are in scope.
- Pre-edit Redline classification is High: policy/schema/spec are red contract surfaces with architecture review; no boundary rule applies.

## Evidence

- Checkout started clean at `8b0f7161bf131856836b18f10caa9df0bda0c808` on `origin/main`.
- Initial task-local checker with complete tracked/untracked NUL path evidence and a fresh Redline verdict: clean while State is Blocked.

## Plan review

Pending completion of discovery and human review of the finalized plan.

## Result review

Pending.
