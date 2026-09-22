<!-- agent-workflow:start -->
**Outcome:** Supported consumer installations can run Agent Workflow checks through the existing runtime adapters even when `python` is absent from PATH; missing checker dependencies produce an actionable blocking error instead of a traceback or false success.

**Target:** `rore/agent-workflow` consumer installation and local-check runtime path on `feat/python-runtime-prerequisites`.

**Scope:** Checker dependency startup handling; existing shell and PowerShell runtime-adapter interpreter selection/check invocation; bootstrap and generated consumer instructions; focused installation/runtime tests; regenerated packaged skill.

**Constraints:** Work only in the isolated worktree. Do not modify the concurrent `feat/behavior-contract-redline-alignment` task. Do not hardcode Codex runtime paths, silently install packages, mutate shared interpreters, add another launcher/dependency manager, weaken validation, or change the established `0/1/2` checker exit contract. Preserve hook-specific degraded behavior unless evaluation has begun.

**Completion criteria:** A supported install runs a meaningful checker command through the existing adapter; an explicit supported interpreter works without `python` on PATH, including a path with spaces; missing Python or `PyYAML`/`jsonschema` returns concise repair guidance and a blocking result with no traceback; bootstrap verifies dependencies with the same interpreter used by its probe; generated instructions name that command; present dependencies preserve required validation; focused and full repository tests pass; existing consumers receive a clear update path.

**Requirement baseline:**
{"source":"user request plus attached defect report","outcome":"Supported consumer installations can run Agent Workflow checks through the existing runtime adapters even when `python` is absent from PATH; missing checker dependencies produce an actionable blocking error instead of a traceback or false success.","scope":"Checker dependency startup handling; existing shell and PowerShell runtime-adapter interpreter selection/check invocation; bootstrap and generated consumer instructions; focused installation/runtime tests; regenerated packaged skill.","constraints":"Work only in the isolated worktree. Do not modify the concurrent `feat/behavior-contract-redline-alignment` task. Do not hardcode Codex runtime paths, silently install packages, mutate shared interpreters, add another launcher/dependency manager, weaken validation, or change the established `0/1/2` checker exit contract. Preserve hook-specific degraded behavior unless evaluation has begun.","completion_criteria":"A supported install runs a meaningful checker command through the existing adapter; an explicit supported interpreter works without `python` on PATH, including a path with spaces; missing Python or `PyYAML`/`jsonschema` returns concise repair guidance and a blocking result with no traceback; bootstrap verifies dependencies with the same interpreter used by its probe; generated instructions name that command; present dependencies preserve required validation; focused and full repository tests pass; existing consumers receive a clear update path."}

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Clean-context Redline review classified checker/skill/template/dist paths as gray with watch tags; scripts and tests are blue. Moderate because one behavior must stay consistent across bootstrap, both platform adapters, generated guidance, packaging, and isolated failure tests.

**Discovery:** Current upstream `main` at `8b0f716` reproduces a raw `ModuleNotFoundError: jsonschema` from the vendored checker. Consumer dependencies are named in the generated checker, test requirements, and CI, but bootstrap neither selects one durable interpreter nor preflights its imports. Generated guidance hardcodes `python`; shell/OpenCode honor `PYTHON`, while PowerShell does not. Runtime adapters are hook guards, but their existing interpreter resolution is the correct mechanism to extend rather than adding another launcher. CI installs both dependencies and remains authoritative.

**Material assumptions:** The existing runtime adapters can expose a local-check action without changing hook behavior; disprove by an incompatible CLI/PowerShell binding, then return to planning. Missing prerequisites can use exit `2` without changing successful/advisory semantics; disprove by an existing contract requiring a different startup exit. CI needs no workflow change because both jobs already install `pyyaml` and `jsonschema`; disprove if focused tests show a CI bypass. Consumer installation remains user-authorized and must not install into arbitrary shared interpreters.

**Plan:** 1. Extend the existing shell and PowerShell adapters with a separate `check` action: resolve the repo/checker without reading hook stdin, honor `PYTHON` as one executable path plus existing project-venv and platform fallbacks, preserve checker arguments and exits `0/1/2`, and make missing repo/checker/interpreter block with `2`; leave `guard`/`seed` behavior unchanged. 2. Make the generated checker catch missing `PyYAML`/`jsonschema` before normal startup and emit one concise exit-2 diagnostic naming `sys.executable` and an authorized repository-venv repair command. Valid `--resolve-work-record` output remains unchanged—single-line JSON, empty stderr—while missing dependencies are a failed invocation, not a resolver result. 3. Update bootstrap to verify imports and run its probe through the same adapter-selected interpreter; update generated AGENTS/bootstrap-summary and integration guidance to name POSIX and PowerShell commands, and record the design choice without adding a launcher. 4. Update the packaged bootstrap fixture to install adapters and initialize Git before the probe. Add isolated tests for missing interpreter, invalid explicit interpreter, missing `yaml`, missing `jsonschema`, no traceback/no false success, explicit interpreter with restricted PATH, path/argument spacing, advisory exit preservation, invalid config with dependencies, and native PowerShell execution. 5. Regenerate `dist/`, reinstall the dogfood skill, run focused checks then `tests/run-all.sh`, and review the final diff. Stop and re-plan if the adapter must install dependencies, evaluate `PYTHON` as a command string, or alter successful resolver/checker semantics.

**Verification plan:** When `yaml` or `jsonschema` is missing, the checker shall separately exit `2` with concise actionable stderr and no traceback -> two isolated startup tests. When no interpreter or an invalid explicit interpreter is selected, adapter `check` shall return `2`; when `PYTHON` names a working executable and PATH has no Python, it shall run -> shell and native PowerShell adapter tests. When interpreter paths contain spaces, named checker options and arguments shall remain intact -> platform adapter path/argument tests. When the checker returns advisory `1`, `check` shall preserve it while `guard` behavior remains unchanged -> stub-checker adapter test plus existing guard suite. When bootstrap verifies an install, dependency preflight and probe shall use the same adapter selection after adapters and Git exist -> packaged bootstrap E2E assertions. When dependencies are present, invalid config remains blocking and required validation plus valid resolver JSON/empty-stderr and `0/1/2` semantics remain -> existing checker/package suites plus focused regressions and `bash tests/run-all.sh`. When package source changes, shipped `dist/` shall match -> package check and local skill reinstall.

**Plan review:** Clean-context review by `/root/runtime_prereq_plan_review`; blocking contract and portability findings incorporated below.

**Approvals:** Not required at this risk level.

**Exceptions:** —

**State:** Ready to implement
<!-- agent-workflow:end -->

## Implementation

- Discovery, clean-context Redline classification, and clean-context plan review completed before implementation; no code edits started.

## Evidence

- Reproduced current packaged-checker startup under `.venv\Scripts\python.exe -S`: exit 1 with raw `ModuleNotFoundError: jsonschema`.
- Verified upstream `main` is `8b0f7161bf131856836b18f10caa9df0bda0c808`.

## Plan review

The reviewer approved extending the existing adapters as the smallest design after requiring a separate no-stdin `check` path, exact `0/1/2` preservation, executable-only `PYTHON`, explicit resolver-output treatment, native PowerShell coverage, separate missing-dependency cases, deterministic PATH tests, and a corrected bootstrap fixture. The revised Plan and Verification plan incorporate every finding. No architectural objection remains.

## Result review

The reviewer approved extending the existing adapters as the smallest design after requiring a separate no-stdin `check` path, exact `0/1/2` preservation, executable-only `PYTHON`, explicit resolver-output treatment, native PowerShell coverage, separate missing-dependency cases, deterministic PATH tests, and a corrected bootstrap fixture. The revised Plan and Verification plan incorporate every finding. No architectural objection remains.
