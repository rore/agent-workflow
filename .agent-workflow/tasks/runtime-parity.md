<!-- agent-workflow:start -->
**Outcome:** Claude Code, Codex, and OpenCode installations provide equivalent workflow discovery, applicability-first engagement, checker-backed pre-implementation decisions where native activation is verified, and CI behavior.

**Target:** agent-workflow.

**Scope:** Normative integration contract; bootstrap/install/package flows; runtime hooks and OpenCode plugin; cross-runtime AGENTS/skill discovery; focused tests; regenerated dogfood and dist artifacts.

**Constraints:** Preserve existing repository instructions and third-party hooks; require explicit platform trust/approval; remain repo-structure-agnostic and fail open on integration faults; never weaken CI; avoid runtime-specific duplication where a shared evaluator suffices.

**Completion criteria:** Bootstrap installs a natively discoverable skill and supported engagement controls for all three runtimes; each runtime applies the same applicability-first rule and blocks guarded implementation lacking workflow evidence where its API permits; trust and fallback behavior are documented; automated tests cover equivalent allow/deny/fail-open cases and two repository layouts; the full suite passes and the reviewed PR is merged.

**Risk:** High

**Complexity:** Moderate

**Reason:** The normative SPEC and shipped pre-edit controls change across every consumer install. High because incorrect activation can silently bypass the workflow; Moderate because this is one repository with several runtime adapters.

**Discovery:** Claude ships seed, ExitPlanMode gate, and reinforcement hooks. Codex now exposes corresponding UserPromptSubmit, PreToolUse, and PostToolUse hooks plus exit-2 denial, but bootstrap installs neither its native skill path nor hooks. OpenCode currently receives only a system-prompt seed; its tool-before lifecycle is the candidate enforcement point. Existing CI is runtime-independent, while Codex/OpenCode runtime tests are missing.

**Material assumptions:** Codex project hooks and native skill discovery work in supported local Codex surfaces; disprove with the packaged runtime smoke test, then document/exclude unsupported surfaces rather than claim parity. OpenCode stable 1.x can synchronously reject `tool.execute.before`; disprove with a real plugin test, then stop and revise the parity claim because prompt-only behavior is not equivalent. OpenCode 2 remains beta and is outside the stable support claim unless its compatibility test passes without weakening 1.x.

**Plan:** Define observable parity in SPEC first for supported local Claude Code, Codex, and stable OpenCode 1.x: native skill discovery, repository instructions, the same applicability-first seed, and the same decision before supported structured file mutations. Implement one shared checker-backed mutation evaluator: union prospective paths with committed, dirty, and untracked paths; allow Work Record creation/repair; otherwise require a structurally implementation-ready configured Work Record or a complete low-risk documentation-only exemption. On the actual default branch, only the complete documentation-only exemption is eligible, and it separately requires recorded direct-default approval plus a fresh unprotected result; a ready Work Record never authorizes code changes there. Missing/invalid/stale evidence denies readiness; adapter execution failure remains a reported fail-open degradation and CI stays authoritative. Register thin adapters for Claude (`PreToolUse`), Codex (`.codex/hooks.json`, including Windows commands and explicit trust), and OpenCode (`tool.execute.before`); scope all three to the same structured edit/write/patch operations and document shell mutation as an equal unsupported runtime path: it bypasses runtime guarding, while PR CI validates final workflow artifacts and applicability without guaranteeing pre-edit ordering or preventing direct pushes. Keep plan hooks as supplemental guidance and correct their path-neutral wording. Install the same package into `.claude/skills` and `.agents/skills`, always maintain the owned `AGENTS.md` marker while preserving other instruction files/hooks, update bootstrap and refresh flows, regenerate dogfood/dist artifacts, and test the behavior matrix in two layouts. Treat OpenCode 2 beta support as optional unless a dual-compatible adapter passes both real loader tests.

**Verification plan:**
- Native installation and preservation → package/bootstrap E2E in two layouts plus manifest, custom-path, idempotency, and existing-hook assertions.
- Equivalent runtime decisions → shared matrix for missing/not-ready/ready Work Records, recovery-only versus recovery-plus-code operations, documentation-only, mixed/governance, malformed/incomplete/stale evidence, nested-cwd, delegated, and default-branch cases including ready-record code denial.
- Runtime wiring → no-model loader/denial smoke tests against installed Claude Code, Codex, and stable OpenCode 1.x; unavailable evidence remains unverified.
- Cross-platform behavior → Codex Windows command-shape and interpreter-degradation tests.
- Regression safety → budget/reference/package checks and `bash tests/run-all.sh`.
- Review quality → smart clean-context result review plus resolved PR threads before merge.

**Plan review:** Human approval received. Clean-context architecture review required the shared mutation boundary, complete applicability evidence, default-branch separation, explicit degraded state, install/update parity, and real runtime tests; incorporated above. See `## Plan review`.

**Approvals:** Approved by user 2026-09-10: "approve"

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

- Establish Context: bounded the task to equivalent guarantees across the three declared runtimes without changing CI semantics.
- Discover: confirmed asymmetric skill installation and hook coverage; delegated clean-context Redline, Codex, and OpenCode audits.
- Assess Risk: recorded High risk and received the required verbatim human approval.
- Plan: incorporated two blocking Astra findings; the independent re-review approved the corrected plan.
- Added 17 focused runtime-guard tests covering shared decisions, recovery, applicability, custom paths, patch moves, degradation, and complete git scope.
- Extended focused runtime-guard coverage with default-branch protection and ready-record denial cases.
- Added Astra regression coverage for unknown defaults, incomplete merge-base scope, nested patch paths, and invalid integration inputs.
- Updated runtime fixtures with an authoritative local origin and explicit unknown-default opt-out.
- Updated bootstrap, templates, integration, and packaging docs for dual skill installs, owned AGENTS.md reconciliation, runtime adapters/settings, stable OpenCode 1.x limits, manifest/runtime verification, and update preservation.
- Extended package E2E coverage for manifest-verified dual installs, runtime hook/plugin installation, idempotency, hook preservation, and AGENTS/instruction-file reconciliation.
- Added an OpenCode plugin smoke test covering real shared-evaluator denial, bounded spawn options, and missing-interpreter fail-open logging.
- Hardened default-branch discovery, merge-base completeness, nested-cwd path resolution, malformed-evidence denial, OpenCode degraded diagnostics, and hidden Windows child processes after Astra review.
- Corrected Codex `commandWindows` stdin forwarding with an explicit `-HookInput` boundary and installer assertion.
- Native probes confirmed OpenCode loading/denial and Claude seed activation; Claude PreToolUse did not activate on this Windows runtime, so the shipped contract reports activation failure as degraded and leaves CI authoritative rather than claiming readiness.
- Resolved all Astra result-review blockers: trusted remote default scope, unpublished default commits, current-branch Work Record isolation, structured schema-invalid denial, Windows exit/UTF-8/hidden-child handling, exact dogfood drift checks, and honest activation claims.

## Plan review

The smart clean-context review rejected literal hook copying because Claude's current plan-text gate is weaker than an OpenCode mutation gate. It required one shared pre-mutation decision across all three runtimes, using the existing applicability and Work Record rules; explicit supported-tool and stable-version boundaries; fail-open transport distinguished from readiness; native install/trust/update coverage; and behavioral E2E evidence. The revised plan incorporates every blocking point. A second Astra review caught and corrected default-branch admission and shell-fallback overclaims before implementation, then approved the corrected plan with no remaining blockers. OpenCode 2 beta and shell-command mutation parsing remain explicit non-claims rather than speculative compatibility code.

## Evidence

- Official Codex hooks documentation: https://learn.chatgpt.com/docs/hooks
- Shared runtime matrix: `python -m pytest tests/hooks/test_runtime_guard.py` → 30 passed before the final config fix; the expanded missing/malformed/schema-invalid group then passed 3/3.
- OpenCode adapter: `node tests/hooks/test_opencode_plugin.mjs` → real evaluator denial, bounded spawn, and degraded fail-open passed.
- Focused hooks: `bash tests/hooks/run.sh` → all hook, installer, wrapper, dogfood, and plugin checks passed.
- Full regression: `bash tests/run-all.sh` → budget, schema, Work Record, checker, Redline, tuner, hooks, links, and package all passed (WSL reused the checkout's pure-Python pytest packages through temporary `/tmp` links).
- Packaging: `bash scripts/package-skill.sh` → 65-file manifests regenerated identically for dist, Claude, and Agents installs.
- Native evidence: OpenCode stable 1.x loaded and denied; Claude seed activated but Claude PreToolUse did not activate on this Windows host; Codex exposed project hooks, and its Windows input-forwarding defect was fixed and covered statically without repeating the popup-producing native probe.

## Result review

- Astra final result review: APPROVE, no actionable blockers. Residual risk is limited to the explicitly documented native activation gaps: Claude Windows mutation guarding was unavailable on this host, and Codex Windows native activation remains unverified; native probes were not repeated after the popup issue.
