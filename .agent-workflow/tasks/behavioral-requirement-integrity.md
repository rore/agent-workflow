<!-- agent-workflow:start -->
**Outcome:** Agent Workflow preserves the behavior a task entered with and protects configured repository behavior contracts, so agents cannot silently make incomplete work pass by weakening requirements or tests.

**Target:** agent-workflow.

**Scope:** Normative workflow semantics; Work Record schema, parser, templates, checker predicates and verdicts; agent guidance and bootstrap/reconfiguration UX; packaged artifacts and focused regression/acceptance coverage, including the Pallium PR #167 replay.

**Constraints:** No new checkpoint, semantic-diff engine, service, universal requirement-ID format, or routine ceremony when behavior is unchanged. Reuse trusted changed-path matching. Keep task-local and repository-wide approval authority distinct; mutation integrity must not be presented as CI regression enforcement.

**Completion criteria:** Initial Task Context is durably baselined before discovery; approved changes retain the baseline and exact decision trail; unapproved task or protected-contract requirement changes block; equivalent and coverage-only changes remain usable; configured contracts require existing CI linkage and cannot use documentation-only exemption; PR #167 erosion paths are rejected; source and packaged tests pass across at least two repository layouts.

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Redline classifies docs/SPEC.md and core/schema/agent-workflow.schema.json as red contract surfaces requiring architecture-review. The feature spans workflow semantics, schema, checker, skill UX, packaging, and tests but remains one repository and one coherent delivery.

**Discovery:** Pending focused inspection of the normative spec, Work Record/parser/checker flow, path matching, bootstrap UX, tests, and packaging.

**Material assumptions:** The existing marker-block parser can support optional baseline/change fields without a new record format; disprove by parser/schema inspection, then choose the smallest compatible structured representation. Existing changed-path and path-pattern code can enforce protected contract mutations; disprove by checker inspection, then extend the shared path layer only. Required-CI linkage can be validated structurally from repository configuration without querying hosting APIs; disprove during schema/checker discovery, then block and return to planning rather than inventing enforcement.

**Plan:** Blocked pending discovery and clean-context plan review.

**Verification plan:** Blocked pending discovery mapping of every completion criterion to focused tests and the full packaged suite.

**Plan review:** Pending required clean-context Elevated-risk review.

**Approvals:** Not required at this risk level; architecture-review remains required by repository governance.

**Exceptions:** —

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- Established Task Context from the committed roadmap feature and completed clean-context pre-edit Redline classification. No product files changed.

## Evidence

- Pre-edit Redline review: `SCHEMA_CHANGE/RED`; architecture-review required; no boundary risk.

## Plan review

Pending after discovery.

## Result review

Pending implementation and verification.
