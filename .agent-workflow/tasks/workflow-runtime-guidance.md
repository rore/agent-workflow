<!-- agent-workflow:start -->
**Outcome:** Cross-checkout delegation names the exact write target, and local checker guidance remains usable when bare `python` is unavailable.

**Target:** agent-workflow

**Scope:** Existing delegation guidance, generated consumer local-check guidance, focused contract assertions, and regenerated package/local mirrors.

**Constraints:** Add only slim existing-location guidance. No new wrapper, interpreter discovery contract, checklist, runtime-behavior claim, Bash Redline-wrapper change, public defect report, or private downstream detail.

**Completion criteria:** Delegation guidance requires the exact checkout plus explicit workdir or absolute write targets and identifies relative `apply_patch` as session-cwd-relative; generated local-check guidance names the repository/runtime-provided Python fallback and requires recording the exact invocation; maintained mirrors remain consistent and within budget.

**Risk:** Elevated

**Complexity:** Simple

**Reason:** Redline classifies the installed skill and consumer instruction sources as gray/watch surfaces. The change is two bounded guidance rules with mechanical mirrors and focused assertions.

**Discovery:** `core/skill/operating-mode.md` carries the canonical four-item delegation prompt but omits checkout targeting. `core/templates/agents-section.md.template` documents a bare `python` local check. Existing runtime adapters already select available interpreters, so no new launcher is needed. No matching guidance covers either incident. Baseline budgets are nearly full: 1,898/1,900 and 396/400 tokens respectively.

**Material assumptions:** Two imperative rules are sufficient because both failures are instruction-selection problems and can replace/compress nearby wording within existing ceilings without dropping rules; if that is impossible, or implementation requires a runtime contract, executable discovery, wrapper, or cross-tool semantics beyond observed behavior, return to planning. The Bash Redline-wrapper report remains separate pending its own evidence.

**Plan:** (1) Invoke agent-workflow and record the GRAY/Elevated classification before edits. (2) Replace/compress nearby wording to add one checkout-target rule to the existing delegation section and one interpreter-fallback rule beside the existing local-check command without raising either budget or dropping a rule. (3) Extend existing lightweight source/package assertions only where they prevent wording drift. (4) Regenerate dist and dogfood installs, then run budget, package consistency, links, and the aggregate suite. Stop if the rules cannot fit, if claims cannot be stated portably, or on scope expansion.

**Verification plan:** When delegation targets another checkout, guidance shall require exact checkout plus explicit workdir/absolute writes and warn that relative `apply_patch` uses session cwd; when bare `python` is absent, generated guidance shall select an available repository/runtime interpreter and record the invocation → focused source/package assertions, budget/reference checks, package regeneration consistency, and `tests/run-all.sh`.

**Plan review:** Approved by clean-context reviewer `/root/runtime_guidance_plan_review` after the budget correction.

**Approvals:** Not required at this risk level.

**Exceptions:** —

**State:** Ready to implement
<!-- agent-workflow:end -->

## Implementation

- Established context and pre-edit Redline classification on `feat/workflow-runtime-guidance`; the Work Record preceded every guidance edit. Clean-context plan review approved the budget-corrected two-rule approach.

## Plan review

Clean-context reviewer `/root/runtime_guidance_plan_review` approved ownership, portability boundaries, and verification, but required the plan to handle the existing 1,898/1,900 and 396/400 token pressure. The revised plan requires replacing/compressing nearby wording within both ceilings, preserving every rule, and stopping rather than raising budgets. Follow-up review approved the correction with no remaining blocker.

