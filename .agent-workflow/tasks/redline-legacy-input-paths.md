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
**State:** Ready to implement
<!-- agent-workflow:end -->

## Implementation

No source or test edits yet. The clean-context plan review approved the narrow decoder change. Branch `feat/redline-legacy-input-paths`, based on pinned upstream `origin/main` `2e1233634263695dc7c4a41eaf5122825158b2e6`.
