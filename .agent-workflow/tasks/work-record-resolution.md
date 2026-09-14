<!-- agent-workflow:start -->
**Outcome:** Agent Workflow provides one authoritative, optional way to resolve the current Work Record, and its guidance preserves supplied source and Work Record identity across pickup, handoff, and completion.

**Target:** agent-workflow

**Scope:** Normative workflow contract, existing checker/runtime entry point, agent-workflow skill guidance, focused tests, and regenerated distribution artifacts.

**Constraints:** Reuse existing config and Work Record parsing; no orchestration layer, mandatory Pallium/Minimap dependency, duplicate identity algorithm, new reference family, migration of persisted identities, or artificial Work Record for exempt tasks.

**Completion criteria:** A consumer can resolve the authoritative current Work Record for custom taskPath, resumed/renamed/detached/worktree contexts with explicit found/absent/error results; pickup and handoff guidance preserves valid supplied identity and actual merge/release semantics; existing independent use remains unchanged.

**Risk:** High

**Complexity:** Moderate

**Reason:** The intended normative spec and resolver contract are red-zone cross-install surfaces requiring architecture review. Moderate complexity spans contract, runtime, guidance, tests, and generated distribution without crossing repository boundaries.

**Discovery:** Config loading and `LocalBackend` own taskPath/path/record parsing, but the backend accepts outside-root locations and only checks that `{slug}` exists. Slug derivation is duplicated: operating guidance and runtime strip one of seven prefixes, while current and templated CI also strip `refactor/` and may strip successive prefixes. Pallium confirmed the existing `agent-workflow:<slug>` identity, requires repo-relative path plus parsed record state, and keeps scope consumer-owned. No trusted provider-owned resolver path is exposed to automatic hooks today.

**Material assumptions:** The existing `agent-workflow:<slug>` identity remains authoritative and needs no migration; a supplied valid identity wins without branch comparison and is scoped by the caller’s explicit checkout. The skill invokes resolution during pickup/resume/handoff guidance; current hooks expose no such automatic event. Automatic Pallium consumption is out of scope until trusted setup supplies and verifies an absolute provider-owned executable path; any repo-local execution or cache framework returns to planning.

**Plan:** Revised proposal: (1) SPEC-first define resolver lookup semantics and source/identity handoff rules. (2) Tighten the shared LocalBackend boundary to require exactly one `{slug}` and keep resolved files inside the selected checkout. (3) Add a separate read-only checker mode that validates a supplied existing reference or, only when absent, derives the documented seven-prefix/first-match slug; do not claim it unifies the pre-existing runtime/CI algorithms. (4) Update operating/checkpoint guidance once, with cross-references and no new Work Record field. (5) Add focused source and packaged CLI tests with read-only assertions, then record the decision and regenerate dist/local installs. Stop on persisted-reference incompatibility, required repo-code execution, or any expansion into automatic consumer integration. Runtime implementation is blocked pending resolution of review findings and human approval.

**Verification plan:** Supplied ref on a differently named branch returns that exact ref/path/state and never inspects/falls back to the branch; custom taskPath/current branch returns found; missing record/config and detached HEAD return the specified absent reasons; malformed config/record/state, invalid ref, Git failure, unsupported backend, Windows/UNC/traversal/symlink escape return specified errors; `feat/fix/example` resolves `fix-example` and `refactor/example` resolves `refactor-example` → focused source CLI tests asserting JSON, exit code, empty stderr, and no filesystem mutation. Packaged checker runs the custom-path/supplied-ref/absent/malformed matrix without checkout-source imports. Guidance semantics → budget/reference checks plus clean-context review. Package/install parity → package checks and local reinstall. Whole change → fresh Redline, local checker, and `bash tests/run-all.sh`.

**Plan review:** Clean-context reviews `/root/work_record_contract_review` and `/root/resolver_plan_review`; findings and responses recorded under `## Plan review`; revised producer plan approved for High-risk human approval.

**Approvals:** Approved by user 2026-09-14T13:56:27+03:00: "allways approve"

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

- Established isolated branch `feat/work-record-resolution`; applicability did not exempt contract and skill changes.
- Pre-edit classification: RED contract surface, High risk, Moderate complexity; no boundary rule applies.
- Discovery identified existing config/backend authority plus duplicated runtime/CI slug derivation; sent contract proposal through Relay as `relay-msg-ae157aa307d348b4bc5fcb42242f5209` and to both coordinating tasks.
- Human approved the concrete reviewed plan at 2026-09-14T13:56:27+03:00 with the verbatim response "allways approve"; implementation gate opened.
- Defined the resolver and identity/handoff contract in SPEC first; implemented the lookup-only checker mode and centralized taskPath validation through the existing config/backend path.
- Closed the shared LocalBackend escape: one validated `{slug}`, bounded safe slugs/paths, link-aware containment before every read/write, and repository-relative locations only.
- Updated operating/context/result-review guidance without adding a field or raising token ceilings; recorded the decision and active roadmap item; regenerated dist plus Claude/Codex dogfood installs.

## Contract proposal

`python <trusted-install>/scripts/agent-workflow-check.py --repo-root <checkout> --resolve-work-record [--work-record-ref agent-workflow:<slug>]`

Valid resolver invocations emit exactly one single-line UTF-8 JSON object, at most 8192 bytes including the final newline, and leave stderr empty:

```json
{"schema_version":1,"status":"found|absent|error","reason":"<stable code>","work_record_ref":"agent-workflow:<slug>|null","slug":"<slug>|null","record_path":"<slash-normalized repo-relative path>|null","record_state":"Ready to implement|Blocked|Blocked or returned to planning|Ready for review|null","message":"<diagnostic>|null"}
```

| Status / reason | `work_record_ref`, `slug`, `record_path` | `record_state` | `message` | Exit |
|---|---|---|---|---|
| `found` / `record_found` | required | required | null | 0 |
| `absent` / `record_not_found` | required | null | null | 0 |
| `absent` / `workflow_not_configured`, `current_record_unavailable` | null | null | null | 0 |
| `error` / any error reason | null | null | required, ≤512 Unicode scalar values | 2 |

Error reasons are exhaustive: `invalid_config`, `unsupported_backend`, `invalid_work_record_ref`, `git_unavailable`, `unsafe_record_path`, `unreadable_record`, `malformed_record`, `invalid_record_state`. Invalid CLI flag combinations remain argparse errors outside the resolver result contract.

A valid supplied reference uses the literal `agent-workflow:` prefix plus a nonempty Unicode slug of at most 255 UTF-8 bytes. Preserve spelling. Reject control or whitespace characters, `/`, `\`, Windows-invalid `< > : " | ? *`, leading dot, trailing dot/space, `.`/`..`, and case-insensitive Windows device basenames. A supplied valid reference is authoritative: resolve only it; missing/malformed never falls back to the branch. Without one, strip the first matching `slice/`, `feat/`, `feature/`, `fix/`, `bug/`, `chore/`, or `demo/` prefix from the current branch and replace remaining `/` with `-`.

Validated local `taskPath` must contain exactly one `{slug}`, be at most 4096 UTF-8 bytes, and be repo-relative with no drive, UNC, absolute form, or `.`/`..` segment. The backend resolves the substituted path before every read and write, follows symlinks/reparse points, and rejects anything outside the explicit checkout. `record_path` is the resolved repo-relative path and is at most 4096 UTF-8 bytes.

The resolver only selects and parses a record. It never evaluates readiness/Redline/applicability, creates or scans records, emits consumer scope, returns an absolute path, claims merge/release state, or changes stored identity. Missing config and detached HEAD are absence, not proof of exemption. Current automatic hooks have no pickup/resume/handoff trigger or trusted provider locator; automatic consumer execution is excluded.

## Cross-repo contract review

Pallium review accepted the additive installed-checker mode with four corrections now incorporated: supplied identity wins without branch comparison; detached HEAD is absent rather than error; `record_path` is guaranteed repo-relative; `record_state` is parsed and returned. Pallium retains ownership of legacy `roadmap:v1:<repo>#roadmap` scope and will not derive scope from the Work Record path. Automatic hook consumption remains blocked because current integrations expose only repository-owned scripts; current cross-tool scope is guidance plus explicit attach APIs. A future automatic integration would require a separately approved Pallium-owned absolute provider path with a startup `schema_version: 1` handshake and fail-degraded/no-fallback behavior.

## Plan review

Clean-context reviewer `/root/work_record_contract_review` confirmed High/Moderate plus architecture-review and raised six findings: correct slug-discovery drift; define supplied-reference precedence; enforce path safety; separate lookup from readiness/Redline and applicability; and assert packaged/read-only behavior. The revised plan incorporates all six. Independent producer reviewer `/root/resolver_plan_review` then approved the plan for human approval with automatic Pallium consumption excluded, requiring the exact grammar, field matrix, bounded JSON, and pre-read containment now specified above. Missing config and detached HEAD deliberately remain `absent` because no implicit current record exists; neither result asserts applicability.

Remaining risks: the existing mutation runtime and CI can still derive a different slug after branch rename; this resolver does not claim to unify them. The general LocalBackend containment defect is fixed here because one shared read/write boundary is safer and smaller than a resolver-only guard; record the compatibility tightening in the decision log and roadmap. No automatic consumer may invoke the resolver until a trusted provider-owned executable path is configured outside repository control. Concurrent checkout/config changes require a fresh agent-invoked resolution.

## Evidence

- Focused affected suites: schema/config 50 passing, Work Record/backend 68 passing, checker/resolver 156 passing.
- Packaged consumer E2E: custom `.work/items/{slug}.record.md` found/absent/malformed/NUL/symlink-loop matrix; exact exits, empty stderr, ≤8192-byte JSON, and unchanged record all passed without source-checkout imports.
- Skill budget: all 19 files within existing ceilings; internal link check: all 180 Markdown files valid.
- Required aggregate `tests/run-all.sh`: exit 0, all nine layers passed (`budget`, `schema`, `work-record`, `checker`, `redline`, `tuner`, `hooks`, `links`, `package`). Windows hook probes emitted their existing temporary-cwd warning only.
- Post-review rerun after the NUL-path fix: aggregate `tests/run-all.sh` again exited 0 with all nine layers; packaged NUL config returned one `invalid_config` JSON object, empty stderr, and exit 2.
- Fresh Redline over all 29 tracked/untracked paths: no boundary rule; `architecture-review` triggered by the red-zone schema/SPEC/governance surfaces and awaits PR-time satisfaction.

## Result review

- Smart clean-context review `/root/astra_reviewer` requested one change: a YAML-decoded NUL in `taskPath` could make `Path.resolve()` escape the structured resolver result with traceback/exit 1.
- Resolved in the shared boundary: taskPath rejects control characters during config loading, and residual filesystem resolution failures become `UnsafeWorkRecordPathError`. Source and packaged regressions assert the complete JSON/stderr/exit contract.
- First follow-up independently confirmed the NUL fix, then found Python 3.12 symlink-loop `RuntimeError` could escape `Path.resolve()`.
- Resolved by translating `RuntimeError` at the same backend boundary. Source and dynamically loaded vendored-entrypoint regressions assert `unsafe_record_path`, one bounded JSON line, empty stderr, and exit 2 without requiring host symlink privileges.
- Post-fix aggregate `tests/run-all.sh` exited 0 with all nine layers. Final reviewer confirmation pending.
