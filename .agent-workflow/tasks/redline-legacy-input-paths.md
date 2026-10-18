# Preserve Redline legacy changed-file inputs when unified diffs are supplied

<!-- agent-workflow:start -->
**Outcome:**
Keep the reporter's legacy newline-delimited `--changed-files` interface usable together with `--diff-unified` for Git C-quoted paths, by comparing and classifying canonical decoded paths while retaining exact path-set validation in both modes.

**Target:**
The Agent Workflow source reporter and its packaged distribution.

**Scope:**
`core/agent-redline/core/reporter/reporter.py`, a focused regression in `core/agent-redline/tests/reporter/test_reporter_unit.py`, and regenerated `dist/agent-workflow/**` only as required by package rules.

**Constraints:**
Preserve existing NUL-delimited strict validation, suppression detection, command-line compatibility, repository-local dirty checkouts, and installed tools. Do not edit local installations or unrelated product behavior.

**Completion criteria:**
1. Legacy newline-delimited changed-file input plus a Git unified diff for a filename containing a newline is accepted and retains the added-line evidence.
2. NUL-delimited path-set validation continues to reject mismatches.
3. The source and packaged reporter agree; required suite passes when its execution slot is available.

**Requirement baseline:**
{"source":"work-record-initial","outcome":"Preserve existing Redline reporter input compatibility when unified-diff evidence is enabled.","scope":"Reporter loader, focused regression test, and package-generated dist reporter.","constraints":"Keep NUL-delimited strict validation and avoid installed changes or unrelated scope.","completion_criteria":"Legacy quoted unusual path loads with unified diff; NUL mismatch still fails; source/package parity and required tests pass."}

**Behavior changes:**
[{"target":"task-context.outcome","classification":"equivalent","before":"Preserve existing Redline reporter input compatibility when unified-diff evidence is enabled.","after":"Keep the reporter's legacy newline-delimited `--changed-files` interface usable together with `--diff-unified` for Git C-quoted paths, by comparing and classifying canonical decoded paths while retaining exact path-set validation in both modes.","reason":"The current wording spells out the same reporter-input compatibility outcome and path canonicalization; it does not add a new behavior obligation."},{"target":"task-context.scope","classification":"equivalent","before":"Reporter loader, focused regression test, and package-generated dist reporter.","after":"`core/agent-redline/core/reporter/reporter.py`, a focused regression in `core/agent-redline/tests/reporter/test_reporter_unit.py`, and regenerated `dist/agent-workflow/**` only as required by package rules.","reason":"The current file paths make the same reporter, regression, and package-output scope precise without adding a new surface."},{"target":"task-context.constraints","classification":"equivalent","before":"Keep NUL-delimited strict validation and avoid installed changes or unrelated scope.","after":"Preserve existing NUL-delimited strict validation, suppression detection, command-line compatibility, repository-local dirty checkouts, and installed tools. Do not edit local installations or unrelated product behavior.","reason":"The current wording makes the existing-input and no-install boundaries explicit; it does not change the accepted behavior or permit broader edits."},{"target":"task-context.completion_criteria","classification":"equivalent","before":"Legacy quoted unusual path loads with unified diff; NUL mismatch still fails; source/package parity and required tests pass.","after":"1. Legacy newline-delimited changed-file input plus a Git unified diff for a filename containing a newline is accepted and retains the added-line evidence.\n2. NUL-delimited path-set validation continues to reject mismatches.\n3. The source and packaged reporter agree; required suite passes when its execution slot is available.","reason":"The current criteria unpack the same compatibility, strict mismatch, parity, and test outcomes into observable checks without broadening the task."}]

**Relationships:**
{"schema_version":1,"sources":null,"pull_requests":[]}

**Risk:**
Elevated

**Complexity:**
Simple

**Reason:**
The reporter implementation path is gray/watch under the current Redline policy; tests are blue. The change is one loader condition with one focused regression.

**Discovery:**
At the pinned origin/main revision, `load_diff_from_files` parses legacy changed-file input as newline-delimited text but parses Git unified headers into decoded paths. `_decode_git_path_header` already handles Git C-quoted headers, but legacy rows are not decoded before the exact path-set comparison at `reporter.py:2177` or before classification. This Windows host rejects newline-bearing filesystem and index paths, so the disposable local Git probe could not generate that case; the regression must assert Git output on a supporting host and exercise a synthetic C-quoted fixture where the OS/Git rejects such paths. The existing loader coverage uses NUL input only.

**Material assumptions:**
- Git's legacy `diff --name-only` C-quotes unusual paths, while `--name-only -z` returns the raw path; the regression must assert actual command output bytes on a host that permits newline names. If Git rejects the path here, keep the synthetic C-quoted test and don't claim live Windows evidence.
- Decoding only Git C-quoted legacy rows with the existing `_decode_git_path_header` makes the changed-file list, unified-diff path set, classification, and suppression evidence refer to the same canonical path. Retain exact path-set validation in both input modes; do not bypass it or change unrelated parsing.

**Plan:**
1. Add a focused test in `TestUnifiedDiffEvidence` that creates a temporary Git repo and asserts `git diff --name-only` emits Git's quoted newline path while `--name-only -z` emits the literal path; use the resulting real unified diff and input file to exercise the loader. Skip only the live Git-path portion on platforms where Git rejects that path, and retain a synthetic C-quoted loader case there.
2. Decode each legacy changed-file line with `_decode_git_path_header` before path-set validation and classification; leave NUL-framed input unchanged.
3. Retain strict path-set rejection in both modes. Assert the legacy fixture has canonical `changed_files`, exact `added_by_file` mapping and marker detection; keep the existing NUL mismatch test.
4. Regenerate package output through the repository's package script; do not run the local skill installer.
5. Run the focused regression and `bash tests/run-all.sh` when the shared execution slot is released.

**Verification plan:**
- Actual legacy and NUL Git output for a newline path → the focused regression documents framing semantics and the legacy loader preserves canonical classification and added-line marker evidence.
- Existing NUL mismatch fixture → still raises the path-set mismatch error.
- Package source/output → generated reporter matches source.
- Repository checks → `bash tests/run-all.sh` after slot release; package check included.

**Plan review:**
Agent technical review: `/root/simplicity_reviewer` (independent clean-context result delivered to root). Reviewed revision: `2e1233634263695dc7c4a41eaf5122825158b2e6`. The reviewer confirmed the C-quoted legacy decoder approach, exact path-set validation in both modes, the actual Git-output regression on supported hosts, and the synthetic quoted-path case on Windows. Findings incorporated; GO before implementation.

**Approvals:**
Not required at this risk level.

**Exceptions:**
—

<!-- Blocked | Ready to implement | Ready for review -->
**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

Implemented legacy C-quoted path decoding with the existing decoder, retained strict path-set checks for both input framings, and added real Git output assertions on supporting hosts plus a synthetic Windows fixture and marker-evidence checks. Regenerated `dist/agent-workflow` from source, then regenerated the committed `.claude/skills/agent-workflow/` mirror with `bash scripts/package-skill.sh --dest .claude/skills/agent-workflow`; only the mirrored reporter and its manifest byte count changed. No local installer was run.

Focused validation passed: `python.exe -m pytest tests/reporter/test_reporter_unit.py -q` from `core/agent-redline` → 172 passed, exit 0, including the legacy numstat regression. The regression asserts Git's actual quoted `--numstat` output on supporting hosts, canonical `lines_by_file`, and the observable PR-size included line count. Legacy numstat keys now use the same existing C-quoted path decoder as changed-file rows. Runtime was the existing private CPython 3.13.14 with pytest 8.4.2, PyYAML 6.0.3, and jsonschema 4.26.0. No installed tools or shared environment changed.

The corrected canonical `bash tests/run-all.sh --verbose` run reached all layers and exited 2. Budget, schema, work-record, checker, redline, tuner, and hooks passed. Links failed because the temporary checkout `.venv` junction exposed five broken Markdown links inside the private venv's third-party documentation; the junction was removed without changing its target. A links-only run with the junction absent passed all 164 Markdown files. Package-only first exposed the stale committed `.claude` mirror; after the mirror regeneration above, package-only passed source/dist parity, install sync, committed-skill parity, package references, install probe, autocrlf clone, and end-to-end bootstrap checks (exit 0). These separately recorded results do not constitute one green full-suite run. The later numstat correction was regenerated into both tracked package outputs; source, `dist`, and `.claude` reporter blobs now share SHA256 `BC78AD53E55DCB4616B5BE994C687602BE7EEBD1B849AE7AEC4DA66555AC972E`, and each manifest has 76 entries. The first regeneration attempt exited 127 after the generator wiped `dist`; the retained recovery invocation used the checkout-scoped private Python shim and completed with exit 0, rebuilding 76 files. No local `.agents` install was created. Logs and source manifests are retained under `C:\Dev\rore\Pallium\build\consumer-upstream-validation-20261018\agent-workflow-*`, including `agent-workflow-numstat-dist.{stdout,stderr,exit}`, `agent-workflow-numstat-dist-recovery.{stdout,stderr,exit}`, `agent-workflow-numstat-claude.{stdout,stderr,exit}`, and `agent-workflow-numstat-focused.{stdout,stderr,exit}`. The earlier full-run attempts and their exit markers remain preserved there as well. The initial Git Bash invocation exited 127 because the nested shell could not resolve `bash`; the earlier corrected runner attempt exited 1 on hook prerequisites before the private Git Bash runner and checkout-local venv shim were prepared. No hook, runtime adapter, or hook-test source was changed. Branch `feat/redline-legacy-input-paths`, based on pinned upstream `origin/main` `2e1233634263695dc7c4a41eaf5122825158b2e6`.

## Result review

Agent technical review: `/root/encoded_setup_review`.

Reviewed revision: `51f65a6c22fd067458f0d9341a0036e653620f4f`.

Verification adequacy: The reporter unit file passed all 172 tests, including actual Git `--name-only` and `--numstat` quoted-path output on supported hosts, canonical per-file counts and PR-size totals, plus the Windows synthetic fixture. Source, dist, and committed Claude reporter outputs match byte-for-byte and both package manifests contain 76 entries. The earlier canonical full suite exited 2 because links followed a temporary private-venv junction into five broken third-party documentation links; links-only and package-only passed separately, not as one green full run. On the initial PR head, hosted unit and Redline checks passed; the Agent Workflow checker blocked because this Work Record lacked a traceable Task Context chain and a result-review section. The current Work Record now records equivalent clarification entries from its immutable initial baseline and this technical result review; hosted Agent Workflow requalification is pending.
