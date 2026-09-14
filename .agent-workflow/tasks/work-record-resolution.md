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

**Material assumptions:** The existing `agent-workflow:<slug>` identity remains authoritative and needs no migration; a supplied valid identity wins without branch comparison and is scoped by the caller’s explicit checkout. Resolver use is event-scoped. Automatic Pallium hook consumption is out of scope until trusted setup supplies and verifies an absolute provider-owned executable path; any requirement to execute repo-local code or add a hot-path lookup returns to planning.

**Plan:** Revised proposal: (1) SPEC-first define resolver lookup semantics and source/identity handoff rules. (2) Tighten the shared LocalBackend boundary to require exactly one `{slug}` and keep resolved files inside the selected checkout. (3) Add a separate read-only checker mode that validates a supplied existing reference or, only when absent, derives the documented seven-prefix/first-match slug; do not claim it unifies the pre-existing runtime/CI algorithms. (4) Update operating/checkpoint guidance once, with cross-references and no new Work Record field. (5) Add focused source and packaged CLI tests with read-only assertions, then record the decision and regenerate dist/local installs. Stop on persisted-reference incompatibility, required repo-code execution, or any expansion into automatic consumer integration. Runtime implementation is blocked pending resolution of review findings and human approval.

**Verification plan:** Supplied ref on a differently named branch returns that exact ref/path/state and never inspects/falls back to the branch; custom taskPath/current branch returns found; missing record/config and detached HEAD return the specified absent reasons; malformed config/record/state, invalid ref, Git failure, unsupported backend, Windows/UNC/traversal/symlink escape return specified errors; `feat/fix/example` resolves `fix-example` and `refactor/example` resolves `refactor-example` → focused source CLI tests asserting JSON, exit code, empty stderr, and no filesystem mutation. Packaged checker runs the custom-path/supplied-ref/absent/malformed matrix without checkout-source imports. Guidance semantics → budget/reference checks plus clean-context review. Package/install parity → package checks and local reinstall. Whole change → fresh Redline, local checker, and `bash tests/run-all.sh`.

**Plan review:** Clean-context review `/root/work_record_contract_review`; blocking findings and responses recorded under `## Plan review`.

**Approvals:** Pending human approval.

**Exceptions:** —

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- Established isolated branch `feat/work-record-resolution`; applicability did not exempt contract and skill changes.
- Pre-edit classification: RED contract surface, High risk, Moderate complexity; no boundary rule applies.
- Discovery identified existing config/backend authority and no executable branch-to-slug resolver; sent contract proposal through Relay as `relay-msg-ae157aa307d348b4bc5fcb42242f5209` and to both coordinating tasks.

## Contract proposal

`python <install-root>/scripts/agent-workflow-check.py --repo-root <repo> --resolve-work-record [--work-record-ref agent-workflow:<slug>]`

```json
{
  "schema_version": 1,
  "status": "found|absent|error",
  "reason": "<stable code>",
  "work_record_ref": "agent-workflow:<slug>|null",
  "slug": "<slug>|null",
  "record_path": "<UTF-8 slash-normalized repo-relative path>|null",
  "record_state": "Ready to implement|Blocked|Blocked or returned to planning|Ready for review|null",
  "message": "<diagnostic>|null"
}
```

Exit `0` for `found` and `absent`; exit `2` for `error`; valid resolver outcomes write only JSON to stdout and leave stderr empty. A supplied valid reference is authoritative and bypasses branch inspection. Without one, derive the slug by stripping the first matching `slice/`, `feat/`, `feature/`, `fix/`, `bug/`, `chore/`, or `demo/` prefix and replacing remaining `/` with `-`. Stable reasons are `record_found`; `workflow_not_configured`, `record_not_found`, `current_record_unavailable`; and `invalid_config`, `unsupported_backend`, `invalid_work_record_ref`, `git_unavailable`, `unsafe_record_path`, `unreadable_record`, `malformed_record`, `invalid_record_state`. The resolver never decides applicability, creates a record, emits consumer scope, returns an absolute path, scans other Work Records, falls back from a supplied identity, or changes stored identity. Incompatible resolver/checker flags are CLI errors.

## Cross-repo contract review

Pallium review accepted the additive installed-checker mode with four corrections now incorporated: supplied identity wins without branch comparison; detached HEAD is absent rather than error; `record_path` is guaranteed repo-relative; `record_state` is parsed and returned. Pallium retains ownership of legacy `roadmap:v1:<repo>#roadmap` scope and will not derive scope from the Work Record path. Automatic hook consumption remains blocked because current integrations expose only repository-owned scripts; current cross-tool scope is guidance plus explicit attach APIs. A future automatic integration would require a separately approved Pallium-owned absolute provider path with a startup `schema_version: 1` handshake and fail-degraded/no-fallback behavior.

## Plan review

Clean-context reviewer `/root/work_record_contract_review` confirmed High/Moderate plus architecture-review and raised six findings: correct the executable slug-discovery claim and algorithm drift; define supplied-reference precedence; enforce slug/template/path containment at the shared backend boundary; make lookup semantics independent of readiness/Redline; keep applicability separate; and assert packaged/read-only behavior. The revised plan incorporates all six. One deliberate consumer-reviewed deviation remains: missing config and detached HEAD are `absent`, not `error`, because the resolver is optional and no implicit current record exists; neither result asserts applicability.

Remaining risks: the existing mutation runtime and CI can still derive a different slug after branch rename; this resolver does not claim to unify them. No automatic consumer may invoke it until a trusted provider-owned executable path is configured outside repository control. Concurrent checkout/config changes require re-resolution at the next pickup/resume/handoff event.

## Evidence

- Pending.

## Result review

- Pending.
