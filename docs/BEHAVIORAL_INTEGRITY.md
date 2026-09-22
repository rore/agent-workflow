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

Those paths are configured once in `agent-redline-policy.yaml`:

```yaml
behaviorContracts:
  paths:
    - "tests/contracts/**"
  verification: behavior-contracts
  checkpoint: behavior-review
```

- `paths` identifies the authoritative contract files. Agent Redline always classifies a changed matching path as red, even if a broader rule calls the surrounding test directory blue.
- `verification` names the existing required CI check that exercises the behavior. Agent Workflow requires an affected Work Record to reference it.
- `checkpoint` routes the change for review. It must use CODEOWNER approval; the last matching base-branch CODEOWNERS rule determines who has repository authority.

There is no separate approver list in Agent Workflow. CODEOWNERS remains the repository source of truth, and GitHub's required Code Owner review authenticates the approval.

Every changed protected path needs one `equivalent`, `coverage-only`, or `requirement-change` entry in a changed Work Record. A repository-level requirement change also needs exact approval from one of the CODEOWNERS tokens reported for that path.

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

Bootstrap does not guess which tests are authoritative. It proposes a behavior-contract path only when it can verify:

- an existing required CI check;
- matching CODEOWNERS on the base branch; and
- required Code Owner review in repository governance.

A human explicitly selects or rejects each candidate. Missing or conflicting evidence leaves the path unconfigured.

## What this does not prove

The checker validates structure and consistency. It cannot decide whether `equivalent` is semantically honest, prove that a test fully captures the requirement, authenticate a reviewer, or replace GitHub's required-check and Code Owner enforcement.

That separation is intentional:

- Agent Workflow preserves task intent and records semantic changes.
- Agent Redline protects configured repository paths and routes review.
- Required CI runs the regression checks.
- GitHub governance authenticates repository approval.
- Human reviewers judge whether the claimed meaning is true.

## Related documentation

- [Operational behavioral-integrity checkpoint](agent-workflow/behavioral-integrity.md)
- [Bootstrap and repository integration](INTEGRATION.md#optional-behavior-contracts)
- [Agent Redline policy reference](REDLINE.md)
- [CI enforcement predicates](ENFORCEMENT.md#behavioral-integrity--do-requirements-remain-traceable)
