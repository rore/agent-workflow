# Reuse completed reviews and assess test adequacy

Source: Relay relay-msg-064c8acafcfd4ca4bb99983e4c91810f. Direct user authorization verified in manager thread 01a0d7cd-696b-76a0-8f2f-48a80a201905, user message 01a0f628-d701-7b43-8ff2-1ba28eaba0b0: "Okay, so let's do it." Assigned scope is exactly the two instruction clarifications below.

<!-- agent-workflow:start -->
**Outcome:** Agents reuse valid completed technical reviews for unchanged applications and assess whether tests detect the relevant failure using faithful interfaces.
**Target:** agent-workflow
**Scope:** Existing technical-review reuse and test-adequacy instructions in the normative SPEC and relevant skill/checkpoint source, decision rationale, generated package/local mirrors, and this Work Record.
**Constraints:** Preserve applicability, Work Record, destination risk, independent/human review and trust duties; no broad install/hook exemptions, risk downgrades, model changes, new review stages, checker mechanisms, infrastructure or consumer edits. Preserve root checkout and local hook preview.
**Completion criteria:** Unchanged reviewed application guidance checks change identity/revision and destination compatibility and reuses valid review evidence; changed behavior, assumptions or risk get review of the uncovered decision. Existing technical review asks whether tests would catch the relevant failure and fakes match the real interface, resolving uncertainty with the smallest targeted check. Instructions remain consistent, within existing budgets, packaged and independently reviewed.
**Requirement baseline:** {"source":"relay-msg-064c8acafcfd4ca4bb99983e4c91810f","outcome":"Agents reuse valid completed technical reviews for unchanged applications and assess whether tests detect the relevant failure using faithful interfaces.","scope":"Existing technical-review reuse and test-adequacy instructions in the normative SPEC and relevant skill/checkpoint source, decision rationale, generated package/local mirrors, and this Work Record.","constraints":"Preserve applicability, Work Record, destination risk, independent/human review and trust duties; no broad install/hook exemptions, risk downgrades, model changes, new review stages, checker mechanisms, infrastructure or consumer edits. Preserve root checkout and local hook preview.","completion_criteria":"Unchanged reviewed application guidance checks change identity/revision and destination compatibility and reuses valid review evidence; changed behavior, assumptions or risk get review of the uncovered decision. Existing technical review asks whether tests would catch the relevant failure and fakes match the real interface, resolving uncertainty with the smallest targeted check. Instructions remain consistent, within existing budgets, packaged and independently reviewed."}
**Risk:** High
**Complexity:** Simple
**Reason:** Intended SPEC clarification touches the normative red contract and architecture-review checkpoint. Skill/checkpoint/package paths are gray/watch, record blue. One bounded prose change; no executable behavior change.
**Discovery:** SPEC 9.4 already requires valid-review reuse, but application identity and destination compatibility are implicit. Operating mode and plan checkpoint repeat the short rule; result checkpoint assesses adequacy without concrete failure-path/interface questions. Budgets are tight (operating 1896/1900, plan 886/900, result 623/700); replace redundant text and cross-reference one shared reuse instruction, without raising ceilings.
**Material assumptions:** These clarify existing review/evidence responsibilities; materially new exemptions or destination/human/trust waivers would exceed authorization and return to planning.
**Plan:** Edit SPEC 9.4 and 9.7 first: reuse completed technical review after confirming unchanged reviewed identity/revision and destination compatibility; retain destination verification, applicability, records, human and trust duties. Put shared guidance in operating-mode.md Clean-context delegation, cross-reference from plan-and-review.md and review-result.md; add failure-path and fake-interface questions to existing result review, with the smallest targeted check for uncertainty. Append DECISIONS rationale and regenerate/install dist and local mirrors. No runtime/checker change. Stop for any new exemption, risk waiver or budget increase.
**Verification plan:** Reuse unchanged local application, reject unverified identity/revision or incompatible destination, review only materially uncovered behavior/assumptions/risk, and preserve independent/human/trust/record duties -> independent plan/result scenario review. Adequacy detects an unexercised failure path or fake repeating an invalid interface and calls for a targeted check, not a new stage -> independent result scenario review. Source/dist coherence and unchanged token ceilings -> existing budget/link/package checks. Mandatory pre-push gate -> one tests/run-all.sh after edits; repeat only for a new material reason.
**Plan review:** Agent technical review: /root/review_reuse_technical at b3887e11413b383c041743707f9189213401f6d9; approved with shared-rule placement correction recorded in Plan. See Plan review below.
**Approvals:** Approved by user 2026-10-01: "Okay, so let's do it." Authorizes the manager's two bounded instruction changes, verified direct source above; separate final human result review remains with manager.
**Exceptions:** —
**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

Applicability: normative SPEC and agent instructions are never documentation-exempt. Clean completed managed checkout reused on feat/review-reuse-adequacy from live main f778377b2d093966f0f82d59a9364f1e3b29f629; root checkout remains untouched. Baseline recorded before discovery, planning or source edits. Blocked on discovery and required technical plan review, not a duplicate permission request.

Discovery complete. The change clarifies existing gates; no executable mechanism or extra review stage is needed. No applicable tracked roadmap item has been assigned; this is a bounded corrective instruction task.

Implementation: SPEC amended first, then one shared reuse rule in operating-mode with plan/result references; the existing result adequacy checklist now probes triggering paths and fake-interface fidelity. DECISIONS rationale appended. Redundant delegation/recovery wording trimmed without removing directives. Budget check passes unchanged ceilings: operating 1857/1900 (was 1896), plan 876/900 (was 886), result 658/700 (was 623); combined loaded instruction cost decreases by 14 tokens. Packaging/local reinstall completed; root checkout and runtime trust untouched.

Verification exposed two public checkpoint copies in docs/agent-workflow/ that packaging does not regenerate. They were synchronized exactly using existing declared public-link rewrites in ee61077. This is instruction propagation only, not changed behavior or authorization scope. Existing technical review reused for unchanged source; reviewer inspected only this uncovered mirror delta.

PR https://github.com/rore/agent-workflow/pull/47 opened at 907936f; full CI suite and both governance checks passed. CodeRabbit completed with two valid minor wording findings and the known pending architecture checkpoint. In 70d676b, result-checklist guidance now explicitly covers every Risk level, matching unchanged SPEC 9.7 without changing Routine reviewer identity; the new DECISIONS entry moved unchanged to the required newest-first position. Source/native/dist/public copies synchronized and reinstalled. Budget remains within unchanged ceilings (result 655/700); final combined affected instruction cost decreases by 17 tokens. Independent reviewer revalidated only this delta and preserved the earlier broad review.

## Plan review

Agent technical review: /root/review_reuse_technical, clean-context non-implementer Sol/high, inspected b3887e11413b383c041743707f9189213401f6d9: baseline/plan, SPEC 9.4/9.7/13.3/13.4, source modes/checkpoints, governance, authoring, packaging and checks. Approved High/Simple plan; no blockers. Shared reuse belongs in operating-mode with checkpoint references. Preserve all destination, independent/human, applicability/record and trust duties; scenario review covers missing identity, changed destination and insufficient failure-path/fake evidence. Plan only; final agent/human result and architecture checkpoint remain required. Placement correction accepted before implementation.

## Evidence

- Instruction semantics and preserved duties -> independent scenario review /root/review_reuse_technical at b9df47b76ab5766711f7b90ee3bfcb416eac962f; approved, six scenarios covered below. Public-mirror-only delta revalidated at ee61077899a07f287b29212a524f255a5f2b5404; approved.
- Regression gate -> bash tests/run-all.sh at b9df47b: budget, schema, work-record, checker, redline, tuner and hooks passed; links failed only on the two unsynchronized public copies, so package was not reached. After mirror-only fix at ee61077, bash tests/run-all.sh --only links and --only package both passed (exit 0). All nine layers now have passing evidence; earlier seven not repeated because neither their inputs nor product semantics changed. Final CI will run the complete suite on the PR head.
- Package/references/budgets -> install-skill-locally.sh completed, source/dist/native copies consistent; unchanged budget ceilings pass and combined affected instruction cost decreases by 14 tokens. Link check verifies public parity and references; package check verifies generated artifact drift. git diff --check passes.
- Root preservation -> root .codex/hooks.json SHA256 remains 6B9A5ED80441142646E3E634B4F768E0C2D930F71AEBDB4B055B066165C5CC1E; original branch/local hook preview untouched.
- Review-correction propagation -> budget check and bash tests/run-all.sh --only links / --only package passed at 70d676b (exit 0). Prior broad review and unaffected verification remain valid; current-head CI runs automatically after push. CI full suite at 907936f: https://github.com/rore/agent-workflow/actions/runs/36827184965; governance: https://github.com/rore/agent-workflow/actions/runs/36827184980.

## Result review

Agent technical review: /root/review_reuse_technical, clean-context non-implementer Sol/high.
Reviewed revision: b9df47b76ab5766711f7b90ee3bfcb416eac962f; public-mirror delta revalidated at ee61077899a07f287b29212a524f255a5f2b5404; all-Risk wording/order delta revalidated at 70d676bedcd987485e78f2a0cf5199bc7b335dc9.
Verification adequacy: approved semantics and instruction propagation. Inspected full edited instructions, SPEC 9.4/9.7 against 13.3/13.4, baseline/plan, DECISIONS, package/native diffs and public link rewrites. Scenarios: compatible unchanged local application reuses original independent plan/result evidence; unknown/mismatched revision cannot reuse; incompatible destination exposes uncovered decisions; materially changed decisions get scoped review; unexercised failure-triggering path and fake encoding an invalid real interface require the smallest targeted check. Trimming preserves scope/update/read-only/exact-checkout/recovery directives. No findings. This verifies guidance, not deterministic future agent behavior. Reviewer did not rerun the suite. Final CI, separate human result review and architecture checkpoint remain required before acceptance.

Bounded revalidation at 70d676b: all-Risk checklist matches unchanged SPEC; Routine still permits normal PR review with no new independent-agent/human-review duty. Public/native/dist propagation and DECISIONS ordering verified. No findings; prior review remains valid for unchanged material.

## Checkpoint: architecture-review

What is changing: SPEC clarifies existing review reuse and adequacy obligations, propagated to installed and public guidance.
Why: avoid duplicate unchanged technical judgment and expose tests that miss failure paths or repeat invalid interface assumptions.
Affected contract: SPEC 9.4 and 9.7; no schema/checker/runtime change.
Compatibility risk: low implementation complexity, High governance consequence; no exemption or waived approval/trust duties.
Verification: independent plan/result scenario review, unchanged budget ceilings, nine repository layers with passing evidence after public mirror correction; final CI and human architecture/result review pending.

## Recovery / next action

Canonical task: agent-workflow:review-reuse-adequacy, branch feat/review-reuse-adequacy, PR #47. Focused checks and delta review passed at 70d676b; push record/corrections, reply and resolve the two corrected bot findings, then verify current-head CI. The third finding (architecture/human result) remains open until manager coordinates the separate final human approval; do not label or merge before it. Root checkout/local hook preview remains preserved. No new plan permission or broad review is needed for record-only bookkeeping or unchanged copies.
