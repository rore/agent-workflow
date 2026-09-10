<!-- agent-workflow:start -->
**Outcome:** Codex support claims and installed controls match behavior that Codex actually enforces for native file changes; Claude Code, Codex, and OpenCode retain the strongest truthful common workflow contract, with CI authoritative where a runtime cannot block before mutation.

**Target:** agent-workflow.

**Scope:** Normative runtime-integration contract; Codex hook installation and activation reporting if supported by native evidence; focused runtime/package tests; integration/bootstrap docs; regenerated dogfood and dist artifacts.

**Constraints:** Do not claim native pre-edit parity without an observed Codex denial; preserve third-party hooks and exact trust semantics; do not parse arbitrary shell commands; keep Claude Code and OpenCode behavior unchanged; use the existing shared evaluator; CI remains authoritative; no new dependency or speculative adapter.

**Completion criteria:** The documented Codex guarantee matches observed supported-runtime behavior; a native Codex file-change path is blocked before mutation if Codex exposes a suitable hook, otherwise Codex is explicitly reported as degraded for that path; automated coverage prevents an unverified activation from being reported as equivalent; source, dogfood, and packaged artifacts agree; the full suite passes and the reviewed PR is merged.

**Risk:** High

**Complexity:** Moderate

**Reason:** Correcting the normative SPEC and shipped cross-runtime activation contract affects every consumer install. The implementation should remain small, but a false allow/block claim would silently weaken governance.

**Discovery:** Trusted project `UserPromptSubmit` and `PreToolUse` hooks are listed by Codex. The shared evaluator directly denies the probe payload, but native Codex `apply_patch` writes succeeded under both CLI 0.149.1 and the desktop-bundled 0.153.4, including a user-approved `danger-full-access` probe. This demonstrates native enforcement failure on those tested paths; missing dispatch is the leading hypothesis, but matcher selection, native payload shape, and hook-result handling remain possible until distinguished. OpenCode stable 1.x native denial remains verified. Claude Code seed activation is verified, while mutation activation remains unverified on this host because the API credential is not exposed to the CLI process.

**Material assumptions:** A supported Codex hook or event may synchronously cover native file changes; disprove with official hook capabilities, installed protocol/binary evidence, and at most one bounded distinguishing native probe that captures hook entry, received payload, exit result, and target-file state, then downgrade the tested Codex pre-edit guarantee instead of adding a workaround. Existing CI covers final repository state independently of runtime dispatch; disprove with the package/CI tests, then stop because no runtime wording change may weaken merge enforcement.

**Plan:** First define the smallest truthful capability-based contract in `docs/SPEC.md`: native pre-mutation parity exists only for a specific runtime version, execution surface, and mutation tool with observed denial; unavailable or unproven enforcement is a named degraded state with CI authoritative. Inspect Codex's supported events and actual app-server behavior once. If a native synchronous file-change event exists and denial is demonstrated with unchanged target contents, wire the existing shared evaluator through the current installer. If no suitable event exists, or a documented event still cannot demonstrate native denial, keep only useful hook coverage, qualify the unsupported equivalence claim, and make the existing installer/bootstrap activation output distinguish installation/trust/direct-evaluator success from verified native mutation coverage, including repeat/no-change installation. Apply the same evidence standard to Claude's currently unverified mutation activation without changing its adapter behavior. Append a correcting decision that supersedes the prior Codex implication while preserving history. Propagate only the necessary wording/configuration through `docs/INTEGRATION.md`, `docs/DECISIONS.md`, `core/skill/bootstrap-mode.md`, affected templates/tests, dogfood files, and `dist/agent-workflow/`. Stop and re-plan if the fix requires shell-command parsing, a second evaluator, undocumented Codex internals, or a general capability registry/probe framework.

**Verification plan:**
- When Codex performs a tested native file change, the installed integration shall either deny before mutation with unchanged target contents or report that version/surface/tool as degraded, never verified without denial evidence → official capability inspection plus a bounded native probe or explicit degraded-state fixture.
- When activation evidence is generated, installed/trusted hooks and a successful direct evaluator check shall remain distinct from verified native mutation coverage, including repeat/no-change installs → focused installer/bootstrap/package regression.
- When Claude mutation activation has not been observed, activation evidence shall use the same unverified/degraded standard without changing the existing integration → focused activation-output regression.
- When Claude Code or OpenCode integrations are packaged, their current behavior shall remain unchanged → existing hook and OpenCode native-denial tests.
- When the package is regenerated, source, dogfood, and dist runtime artifacts shall agree → package drift checks and `bash scripts/package-skill.sh`.
- When the correction is ready to merge, all workflow and Redline gates shall pass → checker, `bash tests/run-all.sh`, smart result review, and PR CI.

**Plan review:** Fresh smart clean-context architecture review completed; verdict approve-with-required-corrections. All three required corrections are incorporated below. Human approval received.

**Approvals:** Approved by user 2026-09-10: "ok"

**Exceptions:** —

**State:** Ready to implement
<!-- agent-workflow:end -->

## Plan review

The reviewer approved the capability-based decision fork and minimal scope, while requiring three corrections: narrow the root-cause conclusion to observed native enforcement failure; make unproven enforcement degraded even when a documented event exists; and distinguish installed/trusted hooks plus direct evaluator success from native interception evidence. The revised plan records version/surface/tool-scoped evidence, unchanged target contents for a verified denial, the same standard for Claude, repeat-install regression coverage, and no new capability registry or probe framework.

## Evidence

- Official Codex hooks documentation: https://learn.chatgpt.com/docs/hooks
- Native Codex 0.149.1 and 0.153.4 probes allowed `apply_patch` despite trusted project hooks; direct invocation of the same installed evaluator denied the same payload with exit 2.
