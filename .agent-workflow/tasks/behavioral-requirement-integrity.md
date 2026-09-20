<!-- agent-workflow:start -->
**Outcome:** Agent Workflow preserves the behavior a task entered with and protects configured repository behavior contracts, so agents cannot silently make incomplete work pass by weakening requirements or tests.

**Target:** agent-workflow.

**Scope:** Normative workflow semantics; Work Record schema, parser, templates, checker predicates and verdicts; agent guidance and bootstrap/reconfiguration UX; packaged artifacts and focused regression/acceptance coverage, including the Pallium PR #167 replay.

**Constraints:** No new checkpoint, semantic-diff engine, service, universal requirement-ID format, or routine ceremony when behavior is unchanged. Reuse trusted changed-path matching. Keep task-local and repository-wide approval authority distinct; mutation integrity must not be presented as CI regression enforcement.

**Completion criteria:** Initial Task Context is durably baselined before discovery; approved changes retain the baseline and exact decision trail; unapproved task or protected-contract requirement changes block; equivalent and coverage-only changes remain usable; configured contracts require existing CI linkage and cannot use documentation-only exemption; PR #167 erosion paths are rejected; source and packaged tests pass across at least two repository layouts.


**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Redline classifies docs/SPEC.md and core/schema/agent-workflow.schema.json as red contract surfaces requiring architecture-review. The feature spans workflow semantics, schema, checker, skill UX, packaging, and tests but remains one repository and one coherent delivery.

**Discovery:** Existing parser optional-extra fields and checker predicate plumbing can carry the feature without a new record format. Trusted NUL changed paths already cover malformed, renamed/deleted, Unicode, spaced, containment, and untracked cases. Config has no behavior-contract model; applicability can protect exact paths and trailing /** directory prefixes. Bootstrap already inspects authoritative sources, CI, and CODEOWNERS. Relevant evidence: docs/SPEC.md §§4-9, 13-14; core/work_record/parser.py; core/config/{loader,applicability}.py; core/checker/{checker,predicates}.py; core/skill/{operating-mode,bootstrap-mode}.md; existing work-record, schema, checker, applicability, package, and budget tests.

**Material assumptions:** Exact slash-normalized repository paths plus a boundary-safe trailing /** descendant form cover v1 contract adoption; a demonstrated need for arbitrary glob semantics stops implementation and returns to planning. Canonical JSON safely carries multiline/Unicode Task Context and change evidence. Baseline immutability and semantic classification remain reviewer judgments because the current record cannot authenticate its own history; the checker must not claim otherwise. Bootstrap/review validates required-CI status and human authority; any need for hosting-API authentication returns to planning.

**Plan:** 1. Update docs/SPEC.md first and append rationale to docs/DECISIONS.md, distinguishing guidance, structural enforcement, and reviewer judgment. 2. Add optional parser fields on both Work Record shapes: Requirement baseline is canonical JSON containing source plus exact Outcome/Scope/Constraints/Completion criteria; Behavior changes is a canonical JSON array. New templates capture the baseline during Establish Context without user interaction. Legacy records remain parseable but a non-waivable predicate blocks advancement until an owner establishes the baseline from an authoritative source. 3. Each task-context change entry targets one protected field and carries exact before/after strings, classification, rationale, and conditional impact/alternatives/typed approval. Enforce ordered before→after continuity and final equality with current Task Context; missing, reordered, duplicate/no-op, malformed, or unapproved requirement changes block. The checker cannot prove that the first baseline was never rewritten or that a semantic classification is honest; result review owns those judgments. 4. Add behaviorContracts config with safe exact or boundary-safe dir/** paths, verification, and approvalAuthority. The CLI runs one global contract gate from the same complete trusted NUL path set even when Work Records resolve: every affected old/new/deleted/untracked path needs exactly one entry; requirement-change authority must exactly match repository config; task-local, clean-context, plan, or Redline approval cannot substitute; the named verification must appear in a Work Record. Missing/incomplete/legacy path evidence fails the contract gate. Configured contract paths always deny documentation-only exemption. 5. Put operational rules in one on-demand integrity guide with minimal checkpoint references; bootstrap proposes only discovered contract candidates already exercised by required CI and asks for repository authority. Mutation integrity is enforced structurally; regression execution and authority/authorship remain external evidence. 6. Test compact/expanded and legacy migration; multiline/Unicode/tampered chains; PR #167 Scope narrowing, deferred/manual fallback, best-effort weakening, and broader platform/state/input guarantees; equivalent/coverage-only handling; authority substitutions; exact and dir/** layouts; rename/delete/untracked/spaces/containment; exemption denial; and positive/negative verification linkage. 7. Regenerate/install/package dist, reconcile roadmap status, and run focused plus full suites. Stop rather than add semantic diffing, general globbing, stable IDs, new stages, or hosting APIs.

**Verification plan:** Baseline structure, multiline values, legacy migration, exact ordered chains, and compact/expanded behavior → parser and predicate unit tests. Unapproved task changes block while equivalent/coverage-only and exact approved changes work → checker tests covering PR #167 Scope, deferred/manual, best-effort, and broader-obligation cases with semantic classification reviewed, not inferred. Global contract mutation integrity and authority separation → trusted NUL changed-path E2E for exact and dir/** layouts, rename/delete/untracked/Unicode/spaces/containment, duplicates, task-owner/agent/plan/Redline substitutions, and repository authority. CI linkage boundary and exemption denial → schema/loader/bootstrap/applicability tests showing structural reference only and blocked missing evidence. Skill UX and package parity → clean-context functional review, budget, links, package E2E, local checker, and bash tests/run-all.sh.

**Plan review:** Clean-context review by /root/plan_review; blocking findings resolved in the amended plan and summarized below.

**Approvals:** Not required at this risk level; architecture-review remains required by repository governance.

**Exceptions:** —

**State:** Ready to implement
<!-- agent-workflow:end -->

## Requirement baseline (pre-feature bootstrap)

The accepted source is roadmap/features/behavioral-requirement-integrity.md@b6ddd9d. Before discovery, commit 47816ee recorded the exact Outcome, Scope, Constraints, and Completion criteria now present in Task Context. This baseline temporarily remains outside the marker block because the pre-feature parser rejects the new field; implementation will migrate it verbatim into canonical JSON once parser support lands.

## Implementation

- Established Task Context from the committed roadmap feature and completed clean-context pre-edit Redline classification. No product files changed.
- Discovery found reusable optional-field parsing, predicate plumbing, trusted changed-path evidence, applicability safety, and bootstrap seams; arbitrary semantic comparison, external authority authentication, and a new checkpoint remain unnecessary.

## Evidence

- Pre-edit Redline review: `SCHEMA_CHANGE/RED`; architecture-review required; no boundary risk.

## Plan review

Clean-context review /root/plan_review identified six blockers; the amended plan now:

- uses canonical JSON for multiline-safe baseline and change evidence, ordered exact Task Context chains, and non-waivable predicates;
- keeps legacy records parseable but blocked until an owner establishes a baseline, while unchanged new routine tasks need no Behavior changes entry;
- defines one global contract gate over complete trusted NUL paths with exact or boundary-safe dir/** matching;
- models task versus repository authority inside the exact change entry and rejects approval substitutions;
- treats configured verification as a structural reference while bootstrap/review owns required-CI evidence; and
- extends PR #167 coverage to deferred/manual, best-effort, and broader-obligation changes.

The reviewer also confirmed that semantic classification and historical baseline immutability cannot be authenticated by the current-file checker and must remain explicit result-review judgments.

## Result review

Pending implementation and verification.
