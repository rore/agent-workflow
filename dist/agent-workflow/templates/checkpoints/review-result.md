# review-result

Closes the workflow. Reviewer evaluates the change against Task Context, plan, Risk/Complexity decision, Verification Record, final diff, and evidence prose. SPEC §9.7 lists the obligations.

## What the harness enforces

**`review.checkpoints_satisfied`** (mode-dependent, non-waivable). Reads agent-redline's checkpoint satisfaction state from its verdict JSON. Each red-zone or contract-class change triggers one or more named checkpoints (`api-review`, `persistence-review`, `security-review`, `architecture-review`, …) from `agent-redline-policy.yaml`. Each checkpoint's `satisfiedBy` rules — typically:

- `codeownerApproval` — a CODEOWNER must approve the PR
- `{ label: <name> }` — a maintainer must apply a named PR label

Redline evaluates each triggered checkpoint against the PR's labels + CODEOWNER approvals (OR-semantics across `satisfiedBy` entries) and emits `satisfied: true | false`. The checker surfaces unsatisfied checkpoints; they block in binding mode and remain advisory in shadow mode.

The harness does not re-implement redline's matching. Redline owns the rules; we surface the result.

Non-waivable per SPEC §13.4: checkpoint satisfaction MUST remain structurally distinct from human approval.

## What stays reviewer judgment (SPEC §9.7)

The reviewer of Elevated and High work MUST also assess:

- whether completion criteria are satisfied
- whether the recorded Verification Record is **adequate** (the harness validates presence and structural well-formedness, not adequacy)
- whether evidence is sufficient
- whether scope expanded unintentionally
- whether assumptions remain unresolved
- whether the final diff changes the risk classification

Review identity: Routine may use normal PR review; Elevated requires a non-implementer; High requires a human. Model choice is optional; clean context and evidence matter. Agent review never replaces mandated human approval.

If evidence is insufficient, run or request the smallest behavioral check that resolves it; prefer the relevant end-to-end transition to rerunning a passing suite. Record the result through authoritative PR/evidence references; if unavailable, leave the gate unsatisfied.

## Satisfy-by paths in practice

**CODEOWNER approval.** Repo's `CODEOWNERS` maps paths to teams. With "Require Code Owner review" in branch protection, GitHub enforces approvals come from the owning team. The CI template intersects the PR's APPROVED reviewers against this and passes the resulting login list to redline.

When no `CODEOWNERS` exists, CI emits a workflow-log warning and passes an empty approver list. Checkpoints whose only `satisfiedBy` is `codeownerApproval` surface as unsatisfied — that's correct.

**Label satisfaction.** Some checkpoints accept a named label (`label: api-reviewed`). A maintainer applying the label asserts the review happened. Lower friction; suitable when review-by-anyone is acceptable. Redline's policy decides which path a checkpoint accepts.

## Relationship to plan-time approvals

Plan-time approvals (Approvals field, clean-context Plan review reference) are recorded in the Work Record BEFORE implementation. Result-review checkpoint satisfaction happens on the PR AFTER implementation. Structurally distinct:

- **Plan-time** (slice D): agent-attested plan approval in the Work Record. Cheating window acknowledged.
- **PR-time** (slice G): GitHub + CODEOWNERS evaluate; redline surfaces; checker blocks.

A High-risk task in default profile mode passes through both: human-approved plan in Approvals + CODEOWNER-approved PR or maintainer-applied review label.

## Skill feedback check

Before marking `Ready for review`, load [`../skill-feedback.md`](../skill-feedback.md) if this task exposed any of these: repeated workaround, human correction, failed instruction/documented behavior, contradiction, broken reference, unmapped error/gate, or consequential guess from missing guidance. That guide owns the detailed triggers, filters, and safe submission steps. Otherwise, done.
