# Safe completion worktree guidance

Source: workflow manager chat `01a0d7cd-696b-76a0-8f2f-48a80a201905`, forwarding user approval item `01a153cf-2bcc-7432-bafb-d93cbf8bd0bc`: "ok, coordinate this with the workflow manager and add the small coordination instruction if needed. keep it short, don’t duplicate instructions, and sync the installed skills when done."

<!-- agent-workflow:start -->
**Outcome:** Agents distinguish handoff from completed delivery and safely dispose of task-created worktrees or report why retained.
**Target:** agent-workflow
**Scope:** Existing completion guidance in core/skill/operating-mode.md and its generated package/native copies; this Work Record.
**Constraints:** Instructions only: remove no existing worktrees. No new artifact, gate, helper, tracker, budget increase or collection-skill duplication. Preserve canonical checkout and all unrelated work. Consumer sync requires current owner/hold coordination.
**Completion criteria:** Completion guidance covers authorized verified delivery, task ownership and dependencies, preservation, host/native cleanup, no-force/shared-checkout protection and retained reasons; package parity, budgets, required suite and independent reviews pass; merge is verified and exact artifacts handed to sync owner.
**Requirement baseline:**
{"source":"work-record-initial","outcome":"Agents distinguish handoff from completed delivery and safely dispose of task-created worktrees or report why retained.","scope":"Existing completion guidance in core/skill/operating-mode.md and its generated package/native copies; this Work Record.","constraints":"Instructions only: remove no existing worktrees. No new artifact, gate, helper, tracker, budget increase or collection-skill duplication. Preserve canonical checkout and all unrelated work. Consumer sync requires current owner/hold coordination.","completion_criteria":"Completion guidance covers authorized verified delivery, task ownership and dependencies, preservation, host/native cleanup, no-force/shared-checkout protection and retained reasons; package parity, budgets, required suite and independent reviews pass; merge is verified and exact artifacts handed to sync owner."}
**Relationships:**
{"schema_version":1,"sources":null,"pull_requests":[]}
**Risk:** Elevated
**Complexity:** Simple
**Reason:** Watch-zone agent instructions and generated installs; operational completion hygiene, no new workflow state, gate, schema or normative concept. Independent review must confirm scope and safeguards.
**Discovery:** Step 8 currently covers stop/handoff but not completed-task worktrees. Operating-mode is 1880/1900 estimated tokens; result-review is 700/700. Installed collection-coordination already requests a worker cleanup/retention report and delegates the procedure to repo/host. SPEC section 6 already separates readiness/handoff from verified delivery and protects owner-managed checkouts.
**Material assumptions:** Existing Step 8 can carry the procedure within budget while preserving recovery obligations; if not, return to planning rather than add a file or raise budget. No SPEC concept change is needed; if independent review disagrees, reassess before editing. Installed consumer ownership is not inferred from prior holds.
**Plan:** Compact only Step 8's existing recovery wording and append the conditional completion procedure. Preserve State, branch, clean revision, unfinished work/next action, exact identities, committed recovery and prompt approval forwarding. Rebuild package plus isolated native copies. Obtain independent plan/result reviews and required suite/CI, resolve PR findings, merge under existing authority, hand exact changed artifacts/revision to the coordinated sync owner. Never perform worktree cleanup in this task.
**Verification plan:**
- Safeguards and recovery remain complete -> independent plan/result scenario review of completed delivery, handoff, shared checkout, dirty/unpushed/ignored work, active agents/processes, installed references, follow-up and unavailable authority.
- Budget and package/native parity remain valid -> budget and package/link checks in required bash tests/run-all.sh plus exact artifact hashes.
- Required checks and delivery are real -> full local suite, current-head CI/review threads and owning PR merge evidence.
- Environment stays untouched -> isolated paths only; canonical status/hash comparison and owner-coordinated artifact handoff, no consumer writes or worktree deletion.
**Plan review:** Agent technical review: /root/relationships_corrected_result_review at 9a8a1e28a7627d3f90e32c123a5237e2ac07fd6f, recorded under Plan review below. No blocking findings; Elevated/Simple and existing Step 8 seam confirmed.
**Approvals:** Not required at this risk level. Manager-directed instructions-only implementation and normal PR delivery authorized; no environment or cleanup authority inferred.
**Exceptions:** —
**State:** Ready to implement
<!-- agent-workflow:end -->

## Implementation

2026-10-19: Applicability denied: skill instructions and generated harness files are never documentation-only exempt. Isolated managed checkout created from verified origin/main 2e1233634263695dc7c4a41eaf5122825158b2e6; task branch feat/completion-worktree-guidance. Canonical checkout remains on its original branch and revision with only .codex/hooks.json dirty. Full intended path set is this record, core/skill/operating-mode.md, dist/agent-workflow/{operating-mode.md,manifest.txt} and .claude/skills/agent-workflow/{operating-mode.md,manifest.txt}; ignored isolated .agents mirror also regenerated. No source provider identity was supplied for the chat-only task, so relationships remain unresolved rather than guessed. No applicable canonical roadmap item was supplied; no roadmap item invented.

## Evidence

Pre-edit budget check: all 22 files within existing ceilings. No implementation or cleanup performed. Plan review and required checks pending.

## Plan review

Independent non-implementer /root/relationships_corrected_result_review inspected the record at 9a8a1e28a7627d3f90e32c123a5237e2ac07fd6f, source Step 8, SPEC section 6 and authoring rules. Plan adequate, no blocking findings; operational completion hygiene requires no new SPEC concept/state/gate. Safeguards cover active dependencies, preservation, ownership and authority. Host archiving must preserve needed material first; otherwise retain/report. Actual wording, budget and mirror parity remain result-review checks. No cleanup or consumer writes were reviewed or authorized.

## Result review

Pending implementation and independent review.
