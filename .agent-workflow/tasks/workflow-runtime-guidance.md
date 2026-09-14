<!-- agent-workflow:start -->
**Outcome:** Cross-checkout delegation names the exact write target, and local checker guidance remains usable when bare `python` is unavailable.

**Target:** agent-workflow

**Scope:** Existing delegation guidance, generated consumer local-check guidance, focused contract assertions, and regenerated package/local mirrors.

**Constraints:** Add only slim existing-location guidance. No new wrapper, interpreter discovery contract, checklist, runtime-behavior claim, Bash Redline-wrapper change, public defect report, or private downstream detail.

**Completion criteria:** Delegation guidance requires the exact checkout plus explicit workdir or absolute write targets and identifies relative `apply_patch` as session-cwd-relative; generated local-check guidance names the repository/runtime-provided Python fallback and requires recording the exact invocation; maintained mirrors remain consistent and within budget.

**Risk:** Elevated

**Complexity:** Simple

**Reason:** Redline classifies the installed skill and consumer instruction sources as gray/watch surfaces. The change is two bounded guidance rules with mechanical mirrors and focused assertions.

**Discovery:** `core/skill/operating-mode.md` carries the canonical four-item delegation prompt but omits checkout targeting. `core/templates/agents-section.md.template` documents a bare `python` local check. Existing runtime adapters already select available interpreters, so no new launcher is needed. No matching guidance already covers either incident.

**Material assumptions:** Two imperative sentences are sufficient because both failures are instruction-selection problems; if implementation requires a runtime contract, executable discovery, wrapper, or cross-tool semantics beyond observed behavior, return to planning. The Bash Redline-wrapper report remains separate pending its own evidence.

**Plan:** (1) Invoke agent-workflow and record the GRAY/Elevated classification before edits. (2) Add one checkout-target rule to the existing delegation section and one interpreter-fallback rule beside the existing local-check command. (3) Extend existing lightweight package/contract assertions only where they prevent wording drift. (4) Regenerate dist and dogfood installs, then run budget, package consistency, links, and the aggregate suite. Stop on budget pressure, tool-specific claims that cannot be stated portably, or scope expansion.

**Verification plan:** When delegation targets another checkout, guidance shall require exact checkout plus explicit workdir/absolute writes and warn that relative `apply_patch` uses session cwd; when bare `python` is absent, generated guidance shall select an available repository/runtime interpreter and record the invocation → focused source/package assertions, budget/reference checks, package regeneration consistency, and `tests/run-all.sh`.

**Plan review:** Pending clean-context review.

**Approvals:** Not required at this risk level.

**Exceptions:** —

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- Established context and pre-edit Redline classification on `feat/workflow-runtime-guidance`; implementation is blocked pending the required Elevated clean-context plan review.

