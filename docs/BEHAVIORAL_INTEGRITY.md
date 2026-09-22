# Behavioral integrity

Behavioral integrity means an implementation cannot quietly change the behavior it was asked to preserve.

This matters because a change can look successful while delivering less. An agent may discover that a requirement is difficult, narrow the scope, weaken a completion criterion, or edit a regression test so the incomplete implementation passes. The code is green, but the promise changed.

agent-workflow protects that promise at two levels.

## 1. Task requirements

Before implementation, the Work Record copies its Outcome, Scope, Constraints, and Completion criteria into a Requirement baseline. The baseline records the behavior implementation started with and is never rewritten.

Later behavioral edits are recorded with exact before and after values:

| Classification | Meaning | Approval |
|---|---|---|
| `equivalent` | Wording or mechanics changed; required behavior did not. | No requirement-change approval. |
| `coverage-only` | Verification improved without adding or changing a product obligation. | No requirement-change approval. |
| `requirement-change` | Required behavior was weakened, removed, narrowed, deferred, made manual or best-effort, otherwise redefined, or materially broadened. | Explicit approval from the task owner, bound to that exact change. |

Until a requirement change is approved, the Work Record stays `Blocked`. Plan approval, agent review, and risk classification do not substitute for the task owner's decision.

## 2. Repository behavior contracts

Task requirements protect what the current task promised. Repositories may also have long-lived behavior that every future task must preserve, such as acceptance tests, protocol fixtures, or end-to-end scenarios.

Those paths are configured once in `agent-redline-policy.yaml`. Every mode has the same core behavior:

- `paths` identifies authoritative contract files. Redline classifies every changed match as red, even under a broader blue rule or exclude.
- `verification` names an existing check that exercises the behavior on pull requests. An affected Work Record must reference it.
- Every changed protected path needs exactly one `equivalent`, `coverage-only`, or `requirement-change` entry.
- A requirement change needs exact approval bound to its before and after values.

`protection` chooses who enforces that approval boundary:

| Protection | Use it when | Additional controls | Important limit |
|---|---|---|---|
| `repository` | The repository has shared governance and GitHub should prevent an unapproved merge. | Branch-required verification, compatible base-branch CODEOWNERS, required Code Owner review, and a dedicated CODEOWNER-only checkpoint. | Repository setup and permissions are required. |
| `workflow` | A solo developer or lightweight repository wants the semantic safeguards without CODEOWNERS or branch protection. | The named verification and the combined Redline/Agent Workflow harness still run on pull requests. Requirement changes use exact task-owner/user approval evidence. | The checker does not authenticate repository authority, and GitHub may still allow a manual merge. |

Repository protection is the compatible default when `protection` is omitted:

```yaml
behaviorContracts:
  protection: repository
  paths:
    - "tests/contracts/**"
  verification: behavior-contracts
  checkpoint: behavior-review

checkpoints:
  behavior-review:
    description: Review authoritative behavior-contract changes
    satisfiedBy:
      - codeownerApproval
```

Workflow protection is explicit and has no behavior checkpoint:

```yaml
behaviorContracts:
  protection: workflow
  paths:
    - "tests/contracts/**"
  verification: behavior-contracts
```

Under repository protection, a `requirement-change` names one CODEOWNERS token reported for the path and records approval by the same token. Under workflow protection it records `authority.scope: task`, `authority.name: task-owner`, and `approval.by: user`. That second shape is deliberate approval evidence for the workflow; it is not authenticated repository authority.

## How the two protections work together

Suppose a task requires automatic delivery while a recipient is offline. During implementation, the agent finds that the current architecture can only queue the message and deliver it after the recipient restarts.

Without behavioral integrity, the agent could make the work appear complete by changing “deliver while offline” to “deliver on next restart,” narrowing Scope to exclude offline recipients, or weakening the contract test.

With behavioral integrity:

1. The original offline-delivery promise remains in the task baseline.
2. Rewording the completion criteria or narrowing Scope is a `requirement-change`.
3. Weakening a configured contract test is also a protected repository-contract change.
4. The task stays blocked while the agent explains the impact and alternatives and requests the correct approval.
5. If approval is refused, the result is `Blocked`, not a green implementation that silently does less.

The requirement may still change. The feature makes that change visible, attributable, and reviewable.

## What bootstrap configures

Bootstrap does not guess which tests are authoritative. It first identifies candidates and proves that the named verification runs on pull requests. It then explains both protection choices and asks the developer to select or reject each candidate and choose a mode.

Repository protection is offered only with live evidence for branch-required status, compatible base-branch CODEOWNERS, and required Code Owner review. Workflow protection needs no CODEOWNERS or branch protection, but it still requires the named verification and combined harness to run on pull requests. Bootstrap never silently downgrades repository protection. If the harness remains proposal-only or required evidence is missing, it leaves the block unconfigured and reports the decision as unresolved.

## What this does not prove

The checker validates structure and consistency. It cannot decide whether `equivalent` is semantically honest, prove that a test fully captures the requirement, authenticate a reviewer, prove the named check ran or passed, or prevent a hosting-platform merge. Repository protection delegates authentication and merge enforcement to GitHub; workflow protection states plainly that those controls are absent.

That separation is intentional:

- Agent Workflow preserves task intent and records semantic changes.
- Agent Redline protects configured repository paths and routes repository-mode review.
- The named PR check runs regression verification; repository protection also makes it branch-required.
- GitHub governance authenticates repository approval only under repository protection.
- Human reviewers judge whether the claimed meaning is true.

## Related documentation

- [Operational behavioral-integrity checkpoint](agent-workflow/behavioral-integrity.md)
- [Bootstrap and repository integration](INTEGRATION.md#optional-behavior-contracts)
- [Agent Redline policy reference](REDLINE.md)
- [CI enforcement predicates](ENFORCEMENT.md#behavioral-integrity--do-requirements-remain-traceable)
