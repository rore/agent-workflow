<!-- agent-workflow:start -->
**Outcome:**
Agent Workflow stays inactive for standalone read-only review, explanation, diagnosis, comparison, and inspection requests, while still starting before implementation planning or repository mutation and when an existing workflow task is advanced.

**Target:**
agent-workflow

**Scope:**
Clarify the normative workflow boundary; align the installed skill, workflow seed, shared runtime copy, OpenCode copy, and this repository's dogfood instruction; add focused regression coverage; record the decision and rationale; regenerate packaged artifacts.

**Constraints:**
Do not add a configuration flag or treat read-only work as a changed-path applicability exemption. Do not weaken the fail-closed behavior after implementation planning or mutation is requested. Do not change checker or mutation-guard enforcement unless review proves the prompt-level boundary cannot work. Preserve seed parity and generated/source parity. Keep recurring instruction cost small.

**Completion criteria:**
1. A standalone request to review, explain, diagnose, compare, or inspect without requesting an implementation plan or mutation does not create or update a Work Record or run change-workflow checkpoints.
2. Requests to plan implementation, edit/fix/build, review and fix, explicitly use Agent Workflow, or resume/advance an existing workflow task still enter the workflow before planning or editing.
3. If a read-only request later expands into implementation planning or mutation, Agent Workflow starts before that expanded work.
4. Source and generated instruction surfaces remain aligned, with focused regression checks for both the exclusion and retained positive triggers.

**Risk:**
Elevated

**Complexity:**
Moderate

**Reason:**
The change touches the normative workflow contract and installed agent instructions. A false negative could bypass governance; a false positive recreates the reported cost problem.

**Discovery:**
`docs/SPEC.md` scopes Agent Workflow to delivery of software changes, but `AGENTS.md` says every task uses it and the injected seed says every engineering task is recorded. The operating mode enters applicability without first deciding whether a change task exists. Changed-path applicability cannot correctly classify a request that authorizes no change. The plan hook is already narrower: it guards implementation plans that mention configured code paths.

**Material assumptions:**
- Assumption: the defect is caused by ambiguous entry instructions, so a shared early scope rule is sufficient. Disproof: an integration independently invokes the skill for read-only requests regardless of those instructions. Action if disproved: stop and trace that integration before changing enforcement.
- Assumption: checker and mutation-guard behavior should remain unchanged because they govern work after a change is intended. Disproof: a guard is invoked by read-only operations or requires a Work Record before any mutation has been requested. Action if disproved: reassess scope and record the additional enforcement change before editing it.

**Plan:**
1. Define the change-task boundary in the normative spec: standalone read-only analysis is outside scope; transition to planning or mutation enters before that work.
2. Express the same boundary once in the skill entry/operating instructions and concise seed copies; remove the contradictory dogfood wording. Use this request matrix: standalone review/explain/diagnose/compare/inspect = outside; implementation plan, edit/fix/build, review-and-fix, explicit Agent Workflow use, and resume/advance of an existing workflow task = inside; a later expansion enters before implementation planning or mutation.
3. Add the smallest deterministic checks that fail if the textual entry contract or seed parity drifts. Do not add a natural-language classifier that production does not use; replay the request matrix manually to assess agent interpretation.
4. Record the design decision, regenerate/install packaged artifacts, and run focused plus full verification.

**Verification plan:**
- Criteria 1-3 → inspect the final spec and instruction diff and manually replay every positive and negative request in the recorded matrix.
- Criterion 4 → run hook/seed parity tests and focused assertions for the new boundary language.
- Workflow/package integrity → run the local checker with the Redline verdict, package regeneration checks, and `bash tests/run-all.sh`.
- Red-zone regression risk → obtain a separate clean-context result review of the final diff.

**Plan review:**
See `## Plan review` below; clean-context review approved the revised plan.

**Approvals:**
Not required at this risk level.

**Exceptions:**
—

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

Defined request scope before changed-path applicability in the normative spec. Updated the skill selector, compressed operating-mode entry, three seed sources, and this repository's dogfood wording. Added focused source/package parity checks and preserved the existing plan and mutation guards unchanged. Regenerated the distribution and local installed copies. Pre-edit Redline classification was red-zone `architecture-review` because `docs/SPEC.md` is normative; no boundary violation or specialized API/schema/security/config review was identified.

## Evidence

- Criteria 1-3: manual matrix replay confirms standalone read-only review/explain/diagnose/compare/inspect exits before config or Work Record creation; implementation-plan, edit/fix/build, review-and-fix, explicit-workflow, and existing-task actions enter; later expansion enters before planning or mutation.
- Criterion 4: `bash tests/hooks/run.sh` passed, including source/runtime/dogfood/package seed parity and both engagement-scope directions.
- Context budget: `bash tests/budget/check-budget.sh --verbose` passed without raising ceilings; `agent-workflow.md` is 494/500 and `operating-mode.md` is 1892/1900 estimated tokens.
- Full verification: `bash tests/run-all.sh` passed all layers using the checkout's existing virtualenv for pytest and the native Linux interpreter for hook subprocesses.

## Plan review

Clean-context reviewer `/root/scope_plan_review` returned **REVISE**. It confirmed the pre-applicability scope gate, unchanged checker/runtime enforcement, parity surfaces, package flow, and full-suite verification. It requested an explicit positive/negative request matrix and deterministic protection of the textual entry contract. The revised plan adds both, plus manual scenario replay because no production natural-language classifier exists to exercise in a unit test. Follow-up review **approved the revised plan for implementation**, with one accepted residual risk: agent interpretation cannot be mechanically proved. The reviewer required explicit coverage of the existing-task resume/advance override and all seed/generated copies.

## Result review

Clean-context reviewer `/root/scope_result_review` returned **APPROVE** with no findings. It confirmed the pre-applicability scope gate, both sides of the request matrix, unchanged checker/mutation enforcement, generated-copy parity, focused coverage, and unchanged budget ceilings. Accepted residual risk: request scope remains prompt-interpreted because the product has no natural-language classifier; adding an unused classifier would not enforce runtime behavior.
