<!-- agent-workflow:start -->
**Outcome:**
Agents keep an applicable canonical roadmap item accurate as a task moves through pickup, pause, resume, handoff, and completion, without treating partial task delivery as whole-feature delivery.

**Target:**
Agent Workflow's portable task-transition guidance.

**Scope:**
Update the normative SPEC, the existing operating and result-review guidance where needed, one small native roadmap item and board entry, decision rationale, this Work Record, and generated skill copies.

**Constraints:**
No required roadmap dependency, new Work Record field, workflow stage, hook, tracker, or constant context block. Use each repository roadmap's rules; leave Minimap commands and Pallium attachment to their owning skills. Carry exact item identity, respect roadmap manager/shared-checkout ownership, preserve read-only exemption, and never mark a broader feature complete from one partial task.

**Completion criteria:**
At each named task transition, an agent with an applicable canonical roadmap item reconciles or reports this task's progress under that roadmap's rules; no item triggers no action. Partial delivery retains remaining feature scope. Shared roadmap ownership is respected. Source and packaged guidance agree, budgets and required repository checks pass.

**Requirement baseline:**
{"source":"relay-msg-86f79352b87e408aaabaa6ba6f87f4c9","outcome":"Agents keep an applicable canonical roadmap item accurate as a task moves through pickup, pause, resume, handoff, and completion, without treating partial task delivery as whole-feature delivery.","scope":"Update the normative SPEC, the existing operating and result-review guidance where needed, one small native roadmap item and board entry, decision rationale, this Work Record, and generated skill copies.","constraints":"No required roadmap dependency, new Work Record field, workflow stage, hook, tracker, or constant context block. Use each repository roadmap's rules; leave Minimap commands and Pallium attachment to their owning skills. Carry exact item identity, respect roadmap manager/shared-checkout ownership, preserve read-only exemption, and never mark a broader feature complete from one partial task.","completion_criteria":"At each named task transition, an agent with an applicable canonical roadmap item reconciles or reports this task's progress under that roadmap's rules; no item triggers no action. Partial delivery retains remaining feature scope. Shared roadmap ownership is respected. Source and packaged guidance agree, budgets and required repository checks pass."}

**Risk:** High

**Complexity:** Moderate

**Reason:**
Redline classifies the normative `docs/SPEC.md` contract as red and requires architecture review; the change also affects agent-loaded transition guidance. Moderate because pickup, handoff, completion, and external roadmap ownership must stay coherent.

**Discovery:**
The shipped result-review rule already conditionally reconciles a tracked roadmap item at completion (`docs/SPEC.md` §9.7 and `review-result.md`). Pickup and stop/handoff guidance carries Work Record identity but no roadmap transition reminder. This repo has a native markdown board and features directory; no canonical item for this extension exists. `agent-workflow.yaml` exempts roadmap-only changes, but this mixed SPEC/skill change requires the workflow and a branch.

**Material assumptions:**
The existing operating-mode transition instructions can carry one conditional reminder without a new artifact or repeated checkpoint prose. Disproof: independent review finds a missed transition or ambiguity; then revise the smallest existing instruction surface. An applicable item may be managed outside the current checkout. Disproof: owner guidance authorizes direct edits; follow that guidance after verifying ownership, otherwise report progress to the manager.

**Plan:**
1. Create `roadmap/features/roadmap-transition-reconciliation.md` and place it on the native board as the canonical item. 2. Add a short normative rule beside SPEC §6's existing handoff contract; keep §9.7's completion detail authoritative. 3. Add one conditional operating-mode reminder naming pickup, pause, resume, handoff, and completion; carry the exact item identity in existing recovery prose, report to a designated roadmap owner without touching their checkout, and adjust result-review wording only if needed for partial feature delivery. 4. Append the design decision, regenerate packaged skill copies, verify budgets/links/package and the full test suite. Stop for review if wording forces a new field, hook, tracker, or Minimap-specific mechanics.

**Verification plan:**
- Applicable item at pickup, pause, resume, handoff, completion; absent item; non-Minimap native roadmap; partial task versus whole feature; managed dirty checkout; standalone read-only work → scenario review against the normative and agent-loaded wording, including independent result review.
- No new mechanism or recurring prose load → diff and token-budget review.
- Source/packaged parity and repository integrity → package, links, and `bash tests/run-all.sh`; PR CI and Redline verdict.

**Plan review:**
Approved by clean-context `/root/roadmap_transition_plan_review`; details below.

**Approvals:**
Approved by user 2026-09-24 07:42:59 UTC: "Approve this plan"

**Exceptions:**
—

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

Planning in isolated branch `feat/roadmap-transition-reconciliation`, based on `9daead3`. Clean-context plan review approved; user approved the exact plan.

Implemented `docs/SPEC.md` §6, the one-sentence `core/skill/operating-mode.md` reminder, `docs/DECISIONS.md`, and the native roadmap item/board; regenerated `dist/` and both local skill installs. The existing §9.7/result-review rule already covers status, shipped scope, and remaining scope, so it stays unchanged. Minimap owns its item states, shared checkout procedure, and Pallium attachment.

## Plan review

The independent reviewer approved the approach. It required naming all five transitions because State alone can remain unchanged; preserving the exact roadmap item in existing recovery prose; reporting progress to the designated owner without modifying, committing, or cleaning their checkout; and retaining remaining feature scope after a partial task completes. The no-item and standalone read-only cases are no-ops. The normative placement is SPEC §6, with §9.7 retaining completion detail. Operating-mode has 67 tokens of budget headroom and review-result has one, so replace redundant text if either must change.

## Evidence

- Verified the working diff atop planning commit `4fe920d`: budget (operating-mode 1882/1900), schema, Work Record, checker, Redline, tuner, hooks, and links passed under native Git Bash with the repository test venv. The OpenCode fixture required a temporary worktree `.venv` junction; it was removed after the pass and its target preserved.
- WSL package layer passed: dist/source parity, committed skill parity, references, install probe, and bootstrap E2E in two layouts. `git diff --check` passed. PR CI remains the authoritative post-commit check.
- Scenario review: no applicable item is a no-op; native roadmap rules own progress; partial task completion retains broader scope; a designated owner receives a progress report without another checkout mutation; standalone read-only work remains outside the workflow.

## Result review

Clean-context Astra review of `origin/main..a22c55e` found no actionable issues. It checked all five transitions, exact identity, no-item/read-only behavior, native ownership, partial task scope, SPEC placement, and source/package parity. PR: https://github.com/rore/agent-workflow/pull/38. A separate human result review and post-commit CI remain required before merge.
