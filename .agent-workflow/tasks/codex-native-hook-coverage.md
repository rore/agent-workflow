<!-- agent-workflow:start -->
**Outcome:** Codex support claims and installed controls match behavior that Codex actually enforces for native file changes; Claude Code, Codex, and OpenCode retain the strongest truthful common workflow contract, with CI authoritative where a runtime cannot block before mutation.

**Target:** agent-workflow.

**Scope:** Normative runtime-integration contract; Codex hook installation and activation reporting if supported by native evidence; focused runtime/package tests; integration/bootstrap docs; regenerated dogfood and dist artifacts.

**Constraints:** Do not claim native pre-edit parity without an observed Codex denial; preserve third-party hooks and exact trust semantics; do not parse arbitrary shell commands; keep Claude Code and OpenCode behavior unchanged; use the existing shared evaluator; CI remains authoritative; no new dependency or speculative adapter.

**Completion criteria:** The documented Codex guarantee matches observed supported-runtime behavior; a native Codex file-change path is blocked before mutation if Codex exposes a suitable hook, otherwise Codex is explicitly reported as degraded for that path; automated coverage prevents an unverified activation from being reported as equivalent; source, dogfood, and packaged artifacts agree; the full suite passes and the reviewed PR is merged.

**Risk:** High

**Complexity:** Moderate

**Reason:** Correcting the normative SPEC and shipped cross-runtime activation contract affects every consumer install. The implementation should remain small, but a false allow/block claim would silently weaken governance.

**Discovery:** Trusted project `UserPromptSubmit` and `PreToolUse` hooks are listed by Codex. A live Codex 0.153.4 desktop `apply_patch` with a blocked Work Record created its target without entering the instrumented trusted wrapper. Codex CLI `bypassPermissions` did enter the wrapper with canonical `tool_name: "apply_patch"` and `tool_input.command`; the shared evaluator returned exit 2, but Codex still created the target. The matcher, payload parser, wrapper, and evaluator therefore need no repo-side fix; those version/surface/mode paths are degraded. OpenCode 1.x plugin callback denial remains verified, but native coverage lacks version/tool/unchanged-target evidence and is degraded under the corrected standard. Claude Code seed activation is verified, while mutation activation remains unverified on this host because the API credential is not exposed to the CLI process.

**Material assumptions:** Disproved: the tested Codex desktop path does not dispatch the trusted wrapper, while CLI `bypassPermissions` ignores its exit-2 denial; the tested paths are downgraded rather than given a workaround. Confirmed locally: CI/package checks cover final repository state independently of runtime dispatch; any future native coverage claim still requires version/surface/tool-scoped denial with an unchanged target.

**Plan:** First define the smallest truthful capability-based contract in `docs/SPEC.md`: native pre-mutation parity exists only for a specific runtime version, execution surface, and mutation tool with observed denial; unavailable or unproven enforcement is a named degraded state with CI authoritative. Inspect Codex's supported events and actual app-server behavior once. If a native synchronous file-change event exists and denial is demonstrated with unchanged target contents, wire the existing shared evaluator through the current installer. If no suitable event exists, or a documented event still cannot demonstrate native denial, keep only useful hook coverage, qualify the unsupported equivalence claim, and make the existing installer/bootstrap activation output distinguish installation/trust/direct-evaluator success from verified native mutation coverage, including repeat/no-change installation. Apply the same evidence standard to Claude's currently unverified mutation activation without changing its adapter behavior. Append a correcting decision that supersedes the prior Codex implication while preserving history. Propagate only the necessary wording/configuration through `docs/INTEGRATION.md`, `docs/DECISIONS.md`, `core/skill/bootstrap-mode.md`, affected templates/tests, dogfood files, and `dist/agent-workflow/`. Stop and re-plan if the fix requires shell-command parsing, a second evaluator, undocumented Codex internals, or a general capability registry/probe framework.

**Verification plan:**
- When Codex performs a tested native file change, the installed integration shall either deny before mutation with unchanged target contents or report that version/surface/tool as degraded, never verified without denial evidence → official capability inspection plus a bounded native probe or explicit degraded-state fixture.
- When activation evidence is generated, installed/trusted hooks and a successful direct evaluator check shall remain distinct from verified native mutation coverage, including repeat/no-change installs → focused installer/bootstrap/package regression.
- When Claude mutation activation has not been observed, activation evidence shall use the same unverified/degraded standard without changing the existing integration → focused activation-output regression.
- When Claude Code or OpenCode integrations are packaged, their current behavior shall remain unchanged → existing hook and OpenCode callback-denial tests.
- When the package is regenerated, source, dogfood, and dist runtime artifacts shall agree → package drift checks and `bash scripts/package-skill.sh`.
- When the correction is ready to merge, all workflow and Redline gates shall pass → checker, `bash tests/run-all.sh`, smart result review, and PR CI.

**Plan review:** Fresh smart clean-context architecture review completed; verdict approve-with-required-corrections. All three required corrections are incorporated below. Human approval received.

**Approvals:** Approved by user 2026-09-10: "ok"

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Plan review

The reviewer approved the capability-based decision fork and minimal scope, while requiring three corrections: narrow the root-cause conclusion to observed native enforcement failure; make unproven enforcement degraded even when a documented event exists; and distinguish installed/trusted hooks plus direct evaluator success from native interception evidence. The revised plan records version/surface/tool-scoped evidence, unchanged target contents for a verified denial, the same standard for Claude, repeat-install regression coverage, and no new capability registry or probe framework.

## Implementation

- Made runtime parity evidence-scoped in SPEC and appended a superseding decision without removing history.
- Kept the shared evaluator and Codex hook installer unchanged: native evidence showed no repository-side matcher, payload, or exit propagation defect to fix.
- Changed bootstrap guidance and self-summary output to record installation/trust separately from native mutation coverage.
- Updated README, integration, packaging, consumer AGENTS template, dist, and local dogfood installs.
- Added focused source and packaged-E2E regressions preventing installed/trusted hooks or direct evaluator success from being presented as verified native coverage.

## Evidence

- Verification revision: `5cd8cef18ee9d27403d3dd0ada0136eed2270c45`.
- Official Codex hook contract: https://learn.chatgpt.com/docs/hooks — `apply_patch` is documented for `PreToolUse`, exit 2 is documented to deny, and specialized tool paths may opt out.
- Live Codex desktop 0.153.4: trusted wrapper instrumented; blocked Work Record; native `apply_patch` created the target; wrapper-entry log absent. Target and all instrumentation were removed; wrapper and Work Record restored byte-for-byte.
- Codex CLI 0.153.4 `bypassPermissions`: wrapper received canonical `apply_patch` input and its child returned 2; target was nevertheless created, then removed; wrapper and Work Record restored byte-for-byte.
- Native-probe transcript: Codex task `01a07c7d-0619-73c2-b2be-0b8f2db45f28`; ephemeral CLI sessions `01a08ba2-d751-7c10-8624-808b804bde29` and `01a08ba4-f131-7361-a3b5-0f6e59a2a287` (results retained here because those probe sessions were disposable).
- Direct installed evaluator: the same blocked payload returns exit 2.
- `bash tests/hooks/run.sh` passed, including activation-evidence and package wiring regressions.
- `bash tests/package/check-e2e-bootstrap.sh` passed in two consumer layouts.
- On revision `5cd8cef18ee9d27403d3dd0ada0136eed2270c45`, `bash tests/run-all.sh --verbose` passed all layers using temporary ignored interpreter shims: budget; schema (47); Work Record (50); checker (138); Redline; tuner (22); hooks; 180-link validation; package and bootstrap E2E. The shims were removed after the run.

## Result review

Smart clean-context result review approved `0e02de1637d85306d96c74d26e22d80a1483f04f` with no remaining findings. Earlier reviews requested three evidence/claim corrections and one evaluator-denial wording correction; `dbeb28f`, `e952676`, and `5cd8cef` resolved them. The reviewer confirmed generated artifacts, assertions, evidence scope, completion criteria, and High risk classification.
