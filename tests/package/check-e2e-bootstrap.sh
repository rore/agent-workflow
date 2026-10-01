#!/usr/bin/env bash
# tests/package/check-e2e-bootstrap.sh
#
# Layer-3 end-to-end. Simulates a consumer adopting the skill from the
# committed dist, mechanically performs the file-write steps bootstrap
# Phase 4 would execute, then runs bootstrap Phase 6's self-probe
# (write the bootstrap Work Record, produce required Redline evidence,
# run the installed adapter, and report gates separately). This proves what we ship
# installs and runs.
#
# What this covers:
#   - Copying dist/agent-workflow/ into a fresh consumer's .claude/skills/
#     (the install step) succeeds and leaves a valid skill directory.
#   - Bootstrap Phase 4 file writes succeed using the templates the
#     skill ships:
#       * agent-workflow.yaml from templates/agent-workflow.yaml.template
#       * agent-redline-policy.yaml from the redline subtree's
#         assets/templates/agent-policy.yaml.template
#       * scripts/agent-workflow-check.py vendored from scripts/
#       * scripts/agent-redline-report.py vendored from agent-redline/scripts/
#       * .github/workflows/agent-workflow.yml from templates/.github/workflows/
#       * .agent-workflow/tasks/ skeleton
#   - Bootstrap Phase 6 required-verdict probe plus applicability approval
#     seam and packaged reporter/checker journeys in two consumer layouts.
#
# What this does NOT cover:
#   - LLM judgment used to identify documentation or behavior-contract candidates,
#     evaluate required-CI/authority evidence, and apply human selection. The test
#     covers shipped guidance and deterministic config/checker paths, not those judgments.
#   - Actual CI runs in a consumer repo's GitHub Actions.
#
# Exit codes:
#   0 — full bootstrap simulation passed
#   1 — script error (dist missing, prerequisite tool absent)
#   2 — bootstrap simulation failed (named in stderr)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIST="$REPO_ROOT/dist/agent-workflow"

# Prefer `python` (Windows / Git Bash); fall back to `python3` (Linux / WSL).
# Same shim other test runners use. Overridable with PYTHON=path.
if [[ -n "${PYTHON:-}" ]]; then
  PY="$PYTHON"
elif command -v python >/dev/null 2>&1; then
  PY=python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "error: no python interpreter found on PATH" >&2
  exit 1
fi

[[ -d "$DIST" ]] || { echo "error: $DIST missing — run scripts/package-skill.sh first" >&2; exit 1; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

CONSUMER="$TMP/consumer-repo"
SKILL="$CONSUMER/.claude/skills/agent-workflow"
mkdir -p "$CONSUMER" "$(dirname "$SKILL")"

cd "$CONSUMER"
git init -q
printf 'consumer baseline\n' > README.md
git add README.md
git -c user.name=Bootstrap -c user.email=bootstrap@example.invalid commit -qm baseline
BASE_SHA="$(git rev-parse HEAD)"

# --- Step 1: install the skill (the documented "clone this repo and copy
# dist/agent-workflow/ into your .claude/skills/" path).
cp -r "$DIST" "$SKILL"
CODEX_SKILL="$CONSUMER/.agents/skills/agent-workflow"
mkdir -p "$(dirname "$CODEX_SKILL")"
cp -r "$DIST" "$CODEX_SKILL"
"$PY" - "$SKILL" "$CODEX_SKILL" <<'PYEOF'
import hashlib, sys
from pathlib import Path
left, right = map(Path, sys.argv[1:])
def files(root): return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
assert files(left) == files(right)
manifest = dict(line.split("\t", 1) for line in (left/"manifest.txt").read_text().splitlines())
for rel in files(left):
    assert (left/rel).read_bytes() == (right/rel).read_bytes(), rel
    if rel != "manifest.txt": assert int(manifest[rel]) == (left/rel).stat().st_size, rel
bootstrap = (left/"bootstrap-mode.md").read_text(encoding="utf-8")
for fragment in (
    "Behavior-contract candidates",
    "Propose only; missing evidence is unresolved.",
    "named verification and combined harness PR-execution evidence",
    "branch-required status, base-branch CODEOWNERS, and required review",
    "PR verification + harness evidence",
    "Missing PR execution defers both",
    "select/reject, choose `repository` or `workflow`",
    "Selection is not requirement-change approval.",
    "`repository` (default)",
    "`workflow`",
    "Never downgrade.",
    "Proposal-only defers.",
    "Do not put behavior-contract paths or authority in `agent-workflow.yaml`.",
    "complete diff exactly matches a verified commit",
    "derive NUL paths, NUL numstat, and `-U0` patch",
    "git diff --cached <saved baseline>",
    "--head-ref",
    "--changed-files-z changed-files.z --redline-verdict redline-verdict.json",
    "feedback disposition",
    "Fresh installs use `docs/agent/`",
):
    assert fragment in bootstrap, fragment
PYEOF

# --- Step 2: Phase 4 writes — perform mechanical equivalents of what
# Concrete runtime install operations documented by bootstrap.
mkdir -p .opencode/plugins .claude/hooks .claude .codex
cp "$SKILL/opencode/agent-workflow.mjs" .opencode/plugins/agent-workflow.mjs
cat > agent-workflow.yaml <<'EOF'
version: 1
project: {name: consumer-repo}
workRecord:
  backend: local
  local:
    taskPath: ".agent-workflow/tasks/{slug}.md"
redline: optional
hooks:
  guardedPaths: [src/, lib/]
EOF
printf '{"hooks":{"UserPromptSubmit":[{"hooks":[{"type":"command","command":"third-party-claude"}]}]}}\n' > .claude/settings.json
printf '{"hooks":{"PreToolUse":[{"matcher":"third-party","hooks":[{"type":"command","command":"third-party-codex"}]}]}}\n' > .codex/hooks.json
cp "$SKILL/hooks/install-settings.py" install-settings.py
"$PY" install-settings.py --runtime claude --settings .claude/settings.json >/dev/null
cp .claude/settings.json .claude/before
"$PY" install-settings.py --runtime claude --settings .claude/settings.json >/dev/null
cmp -s .claude/settings.json .claude/before || exit 2
"$PY" install-settings.py --runtime codex --settings .codex/hooks.json >/dev/null
cp .codex/hooks.json .codex/before
"$PY" install-settings.py --runtime codex --settings .codex/hooks.json >/dev/null
cmp -s .codex/hooks.json .codex/before || exit 2
"$PY" - <<'PYEOF'
import json
from pathlib import Path
c=json.loads(Path(".claude/settings.json").read_text()); x=json.loads(Path(".codex/hooks.json").read_text())
assert any(h["command"]=="third-party-claude" for g in c["hooks"]["UserPromptSubmit"] for h in g["hooks"])
assert any(h["command"]=="third-party-codex" for g in x["hooks"]["PreToolUse"] for h in g["hooks"])
runtime=[h for gs in x["hooks"].values() for g in gs for h in g["hooks"] if "agent-workflow-runtime" in h.get("command","")]
assert len(runtime)==2 and all(h.get("commandWindows","").startswith("powershell.exe ") and " -EncodedCommand " in h["commandWindows"] for h in runtime)
assert json.loads(Path(".claude/hooks/guarded-paths.json").read_text())["guardedPaths"]==["src/","lib/"]
PYEOF
cat > AGENTS.md <<'EOF'
# Consumer guidance

Root prose before.
<!-- agent-workflow:agents-section:start -->
STALE BODY
<!-- agent-workflow:agents-section:end -->
Root prose after.
EOF
printf 'Claude-specific instructions\n' > CLAUDE.md
printf 'Codex-specific instructions\n' > CODEX.md
cp CLAUDE.md CLAUDE.before; cp CODEX.md CODEX.before
mkdir -p docs/agent
cp "$SKILL/agent-redline/references/per-checkpoint/blue-zone-work.md" docs/agent/
"$PY" "$SKILL/hooks/merge-agents-section.py" --file AGENTS.md --template "$SKILL/templates/agents-section.md.template" >/dev/null
grep -Fq '`docs/agent/`' AGENTS.md
if grep -Fq '`docs/agent-redline/skills/`' AGENTS.md; then exit 2; fi
[[ -f docs/agent/blue-zone-work.md ]]
cp AGENTS.md AGENTS.before
"$PY" "$SKILL/hooks/merge-agents-section.py" --file AGENTS.md --template "$SKILL/templates/agents-section.md.template" >/dev/null
cmp -s AGENTS.md AGENTS.before || exit 2
mkdir -p legacy/docs/agent-redline/skills
cp "$SKILL/agent-redline/references/per-checkpoint/blue-zone-work.md" legacy/docs/agent-redline/skills/
cp legacy/docs/agent-redline/skills/blue-zone-work.md legacy/blue-zone-work.before
cat > legacy/AGENTS.md <<'EOF'
Legacy prose before.
<!-- agent-workflow:agents-section:start -->
STALE BODY
<!-- agent-workflow:agents-section:end -->
Legacy prose after.
EOF
"$PY" "$SKILL/hooks/merge-agents-section.py" --file legacy/AGENTS.md \
  --template "$SKILL/templates/agents-section.md.template" \
  --redline-docs-path docs/agent-redline/skills/ >/dev/null
grep -Fq '`docs/agent-redline/skills/`' legacy/AGENTS.md
if grep -Fq '`docs/agent/`' legacy/AGENTS.md; then exit 2; fi
[[ -f legacy/docs/agent-redline/skills/blue-zone-work.md && ! -e legacy/docs/agent ]]
cmp -s legacy/docs/agent-redline/skills/blue-zone-work.md legacy/blue-zone-work.before
cp legacy/AGENTS.md legacy/AGENTS.before
"$PY" "$SKILL/hooks/merge-agents-section.py" --file legacy/AGENTS.md \
  --template "$SKILL/templates/agents-section.md.template" \
  --redline-docs-path docs/agent-redline/skills/ >/dev/null
cmp -s legacy/AGENTS.md legacy/AGENTS.before || exit 2
cmp -s CLAUDE.md CLAUDE.before && cmp -s CODEX.md CODEX.before || exit 2
grep -Fq 'Outcome-affecting subagents inherit this Work Record.' "$SKILL/operating-mode.md" || exit 2
grep -Fq 'Exact target checkout; use explicit shell workdir or absolute write targets.' "$SKILL/operating-mode.md" || exit 2
grep -Fq 'Relative `apply_patch` targets the session cwd' "$SKILL/operating-mode.md" || exit 2
grep -Fq 'forward a received approval immediately' "$SKILL/operating-mode.md" || exit 2
grep -Fq 'Human consent to the presented plan is approval; no magic word.' "$SKILL/templates/checkpoints/plan-and-review.md" || exit 2
"$PY" - <<'PYEOF'
from pathlib import Path
t=Path("AGENTS.md").read_text()
legacy=Path("legacy/AGENTS.md").read_text()
assert "Root prose before." in t and "Root prose after." in t and "STALE BODY" not in t
assert "Legacy prose before." in legacy and "Legacy prose after." in legacy and "STALE BODY" not in legacy
assert "verified requires a denied operation with unchanged target" in t
assert "Record every other combination as degraded." in t
assert "Evaluator failure returns deny; native prevention requires that evidence." in t
assert "bash scripts/agent-workflow-runtime.sh codex check" in t
assert "scripts/agent-workflow-runtime.ps1 codex check" in t
PYEOF

# bootstrap-mode would do conversationally. Each write uses a file the
# packaged skill actually ships; failure here proves a missing template.

# 2a. agent-workflow.yaml. The template carries placeholders like
# <repo-name> that the bootstrap conversation fills in — we substitute
# trivially so the checker can read the resulting YAML.
sed 's|<repo-name>|consumer-repo|g' \
    "$SKILL/templates/agent-workflow.yaml.template" \
  > agent-workflow.yaml \
  || { echo "FAIL: could not write agent-workflow.yaml from template" >&2; exit 2; }

# The template ships in declarative form; the schema-checker requires
# a specific shape. Replace the workRecord block with a minimal valid
# local-backend config. (Real bootstrap does this through the conversation;
# the simulation skips the dialogue.)
"$PY" - <<'PYEOF' || { echo "FAIL: could not write minimal agent-workflow.yaml" >&2; exit 2; }
from pathlib import Path
Path("agent-workflow.yaml").write_text(
    "version: 1\n"
    "project:\n"
    "  name: consumer-repo\n"
    "workRecord:\n"
    "  backend: local\n"
    "  local:\n"
    "    taskPath: \".agent-workflow/tasks/{slug}.md\"\n"
    "redline: required\nredlineVerdictPath: redline-verdict.json\n",
    encoding="utf-8",
)
PYEOF

# 2b. .agent-workflow/tasks/ skeleton.
mkdir -p .agent-workflow/tasks

# 2c. Redline policy and its vendored schema. The reporter resolves the
# consumer schema from .agent-redline/ and validates every generated policy.
mkdir -p .agent-redline
cp "$SKILL/agent-redline/assets/templates/agent-policy.yaml.template" \
   agent-redline-policy.yaml \
  || { echo "FAIL: could not copy agent-policy.yaml.template" >&2; exit 2; }
cp "$SKILL/agent-redline/assets/schema/agent-policy.schema.json" \
   .agent-redline/agent-policy.schema.json \
  || { echo "FAIL: could not copy agent-policy.schema.json" >&2; exit 2; }

# 2d. Vendored checker + reporter. These are the same scripts the
# install probe already exercised; here we make sure they live at the
# consumer-repo locations bootstrap-mode names.
mkdir -p scripts
cp "$SKILL/scripts/agent-workflow-check.py" scripts/agent-workflow-check.py
cp "$SKILL/agent-redline/scripts/agent-redline-report.py" scripts/agent-redline-report.py
cp "$SKILL/scripts/agent-workflow-runtime.py" scripts/agent-workflow-runtime.py
cp "$SKILL/scripts/agent-workflow-runtime.sh" scripts/agent-workflow-runtime.sh
cp "$SKILL/scripts/agent-workflow-runtime.ps1" scripts/agent-workflow-runtime.ps1

# Bootstrap guidance exposes both protection choices and never persists a
# workflow-only claim when the PR harness remains proposal-only.
grep -Fq '`repository` (default)' "$SKILL/bootstrap-mode.md"
grep -Fq '`workflow`' "$SKILL/bootstrap-mode.md"
grep -Fq 'Proposal-only defers.' "$SKILL/bootstrap-mode.md"
# 2e. CI workflow. Just confirm we can lay it down — the template
# contains the workflow YAML.
mkdir -p .github/workflows
cp "$SKILL/templates/.github/workflows/agent-workflow.yml.template" \
   .github/workflows/agent-workflow.yml
grep -Fq 'pull_request_review:' .github/workflows/agent-workflow.yml
grep -Fq 'types: [submitted, dismissed]' .github/workflows/agent-workflow.yml
grep -Fq 'checked in PR CI, but GitHub does not require it for merge' .github/workflows/agent-workflow.yml

# --- Step 3: commit Phase 4, then probe mixed committed-install and
# uncommitted-Phase-6 changes using one saved-baseline comparison.
git add -A
git -c user.name=Bootstrap -c user.email=bootstrap@example.invalid commit -qm "bootstrap Phase 4 install"
PHASE4_HEAD="$(git rev-parse HEAD)"
USER_INDEX_TREE="$(git write-tree)"

cat > .agent-workflow/tasks/bootstrap-consumer.md <<'EOF'
<!-- agent-workflow:start -->
**Outcome:** Install the workflow skill and its required governance checks.

**Target:** consumer-repo

**Scope:** Skill package, checker, reporter, configuration, task guidance, and CI workflow.

**Constraints:** Preserve required Redline and report gate outcomes accurately.

**Completion criteria:** Installed adapter receives genuine reporter evidence and emits a structured result.

**Requirement baseline:** {"source":"bootstrap-phase-6","outcome":"Install the workflow skill and its required governance checks.","scope":"Skill package, checker, reporter, configuration, task guidance, and CI workflow.","constraints":"Preserve required Redline and report gate outcomes accurately.","completion_criteria":"Installed adapter receives genuine reporter evidence and emits a structured result."}

**Risk:** High

**Complexity:** Moderate

**Reason:** Bootstrap changes governance configuration and CI evidence paths.

**Discovery:** Fresh install creates the configured package, policy, scripts, and workflow.

**Material assumptions:** The installed backend can execute its checker; missing reporter evidence must block.

**Plan:** Run the installed adapter against the exact bootstrap slug and complete installation diff.

**Verification plan:** Generate a reporter verdict from the committed diff; assert evidence availability separately from task-gate status.

**Plan review:** Fixture for the mechanical bootstrap test.

**Approvals:** Omitted; the fixture does not synthesize human approval.

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->
EOF

printf 'scripts/agent-workflow-check.py\n' > .gitignore
TEMP_INDEX="$TMP/bootstrap.index"
GIT_INDEX_FILE="$TEMP_INDEX" git read-tree "$PHASE4_HEAD"
GIT_INDEX_FILE="$TEMP_INDEX" git add -A
BOOTSTRAP_CHANGED_FILES="$TMP/bootstrap-changed-files.z"
BOOTSTRAP_LINES_PER_FILE="$TMP/bootstrap-lines-per-file.z"
BOOTSTRAP_DIFF="$TMP/bootstrap-diff.patch"
GIT_INDEX_FILE="$TEMP_INDEX" git diff --cached --name-only -z --no-renames "$BASE_SHA" > "$BOOTSTRAP_CHANGED_FILES"
GIT_INDEX_FILE="$TEMP_INDEX" git diff --cached --numstat -z --no-renames "$BASE_SHA" > "$BOOTSTRAP_LINES_PER_FILE"
GIT_INDEX_FILE="$TEMP_INDEX" git diff --cached --no-ext-diff --no-textconv --no-color --no-renames -U0 "$BASE_SHA" > "$BOOTSTRAP_DIFF"
[[ "$(git write-tree)" == "$USER_INDEX_TREE" ]]
"$PY" - "$BOOTSTRAP_CHANGED_FILES" "$BOOTSTRAP_LINES_PER_FILE" "$BOOTSTRAP_DIFF" <<'PYEOF'
import sys
from pathlib import Path
changed, numstat, patch = map(lambda p: Path(p).read_bytes(), sys.argv[1:])
paths = set(changed.split(b"\0")[:-1])
assert b"agent-workflow.yaml" in paths
assert b"scripts/agent-workflow-check.py" in paths
assert b".agent-workflow/tasks/bootstrap-consumer.md" in paths
assert b".gitignore" in paths
assert b"agent-workflow.yaml" in numstat and b"bootstrap-consumer.md" in numstat
assert b"agent-workflow-check.py" in patch and b"bootstrap-consumer.md" in patch
PYEOF

git ls-files --error-unmatch scripts/agent-workflow-check.py >/dev/null
git check-ignore --no-index -q scripts/agent-workflow-check.py
[[ "$(git write-tree)" == "$USER_INDEX_TREE" ]]
MIXED_VERDICT="$TMP/mixed-redline-verdict.json"
set +e
"$PY" scripts/agent-redline-report.py --policy agent-redline-policy.yaml \
  --changed-files-z "$BOOTSTRAP_CHANGED_FILES" \
  --lines-per-file-z "$BOOTSTRAP_LINES_PER_FILE" \
  --diff-unified "$BOOTSTRAP_DIFF" --json-out "$MIXED_VERDICT" \
  > "$TMP/mixed-redline-output.txt" 2>&1
MIXED_REPORTER_EXIT=$?
set -e
[[ "$MIXED_REPORTER_EXIT" -le 2 && -s "$MIXED_VERDICT" ]]
set +e
PYTHON="$PY" bash scripts/agent-workflow-runtime.sh codex check \
  --repo-root . --slug bootstrap-consumer \
  --changed-files-z "$BOOTSTRAP_CHANGED_FILES" \
  --redline-verdict "$MIXED_VERDICT" \
  > "$TMP/mixed-probe-output.json" 2> "$TMP/mixed-probe-error.txt"
MIXED_PROBE_EXIT=$?
set -e
[[ "$MIXED_PROBE_EXIT" -le 2 ]]
"$PY" - "$MIXED_VERDICT" "$TMP/mixed-probe-output.json" <<'PYEOF'
import json, sys
from pathlib import Path
verdict = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert "error" not in verdict, verdict
payload = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
record = next(r for r in payload["records"] if r["slug"] == "bootstrap-consumer")
predicate = next(p for p in record["predicates"] if p["name"] == "risk.redline_findings_available")
assert predicate["passed"], predicate
PYEOF

# Commit only Phase 6 source files; generated evidence stays outside the repo.
git add -- .agent-workflow/tasks/bootstrap-consumer.md .gitignore
git -c user.name=Bootstrap -c user.email=bootstrap@example.invalid commit -qm "bootstrap Phase 6 record"
PHASE6_HEAD="$(git rev-parse HEAD)"
git diff --name-only -z --no-renames "$BASE_SHA" "$PHASE6_HEAD" > changed-files.z
git diff --numstat -z --no-renames "$BASE_SHA" "$PHASE6_HEAD" > lines-per-file.z
git diff --no-ext-diff --no-textconv --no-color --no-renames -U0 "$BASE_SHA" "$PHASE6_HEAD" > diff-unified.patch

set +e
"$PY" scripts/agent-redline-report.py --policy agent-redline-policy.yaml \
  --changed-files-z changed-files.z --lines-per-file-z lines-per-file.z \
  --diff-unified diff-unified.patch --head-ref "$PHASE6_HEAD" \
  --json-out redline-verdict.json > redline-output.txt 2>&1
REPORTER_EXIT=$?
set -e
[[ "$REPORTER_EXIT" -le 2 && -s redline-verdict.json ]]
"$PY" - <<'PYEOF'
import json
from pathlib import Path
verdict = json.loads(Path("redline-verdict.json").read_text(encoding="utf-8"))
assert "error" not in verdict, verdict
PYEOF

# Required mode blocks without the artifact, then receives the real verdict.
mv redline-verdict.json redline-verdict.saved.json
set +e
PYTHON="$PY" bash scripts/agent-workflow-runtime.sh codex check \
  --repo-root . --slug bootstrap-consumer --changed-files-z changed-files.z \
  > missing-verdict-output.json 2> missing-verdict-error.txt
MISSING_EXIT=$?
set -e
mv redline-verdict.saved.json redline-verdict.json
[[ "$MISSING_EXIT" -eq 2 ]]
"$PY" - <<'PYEOF'
import json
from pathlib import Path
payload = json.loads(Path("missing-verdict-output.json").read_text(encoding="utf-8"))
record = next(r for r in payload["records"] if r["slug"] == "bootstrap-consumer")
predicate = next(p for p in record["predicates"] if p["name"] == "risk.redline_findings_available")
assert not predicate["passed"]
PYEOF

set +e
PYTHON="$PY" bash scripts/agent-workflow-runtime.sh codex check \
  --repo-root . --slug bootstrap-consumer --changed-files-z changed-files.z \
  --redline-verdict redline-verdict.json > probe-output.json 2> probe-error.txt
PROBE_EXIT=$?
set -e

[[ "$PROBE_EXIT" -le 2 ]]
"$PY" - <<'PYEOF'
import json
from pathlib import Path
payload = json.loads(Path("probe-output.json").read_text(encoding="utf-8"))
record = next(r for r in payload["records"] if r["slug"] == "bootstrap-consumer")
predicate = next(p for p in record["predicates"] if p["name"] == "risk.redline_findings_available")
assert predicate["passed"], predicate
assert Path("redline-verdict.json").is_file()
PYEOF

# Invalid slugs remain structured in the packaged normal checker path.
set +e
"$PY" scripts/agent-workflow-check.py --repo-root . --slug "my task" \
  > invalid-slug.json 2> invalid-slug-error.txt
INVALID_SLUG_EXIT=$?
set -e
[[ "$INVALID_SLUG_EXIT" -eq 2 ]]
[[ ! -s invalid-slug-error.txt ]]
"$PY" - <<'PYEOF'
import json
from pathlib import Path
verdict = json.loads(Path("invalid-slug.json").read_text(encoding="utf-8"))
assert verdict["status"] == "blocking"
assert verdict["records"][0]["slug"] == "my task"
assert verdict["records"][0]["predicates"][0]["name"] == "workrecord.exists"
PYEOF
# --- Step 4: packaged applicability approval and first layout. Drive the
# documented CLI, prove partial/rejected/injected approval, then run both
# shipped callers on the resulting config.
"$PY" - <<'PYEOF'
from pathlib import Path
Path("proposal.z").write_bytes(b"docs/\0roadmap/\0README.md\0")
Path("approved.z").write_bytes(b"docs/\0README.md\0")
Path("rejected.z").write_bytes(b"")
Path("injected.z").write_bytes(b"handbook/\0")
PYEOF
"$PY" scripts/agent-workflow-check.py --repo-root . \
  --bootstrap-applicability-proposal-z proposal.z \
  --bootstrap-applicability-approved-z approved.z \
  --bootstrap-direct-default-branch-approved \
  --bootstrap-protection-status protected > applicability-rule.json
"$PY" scripts/agent-workflow-check.py --repo-root . \
  --bootstrap-applicability-proposal-z proposal.z \
  --bootstrap-applicability-approved-z rejected.z \
  --bootstrap-protection-status unavailable > rejected-rule.json
set +e
"$PY" scripts/agent-workflow-check.py --repo-root . \
  --bootstrap-applicability-proposal-z proposal.z \
  --bootstrap-applicability-approved-z injected.z \
  --bootstrap-protection-status unprotected >/dev/null 2>&1
INJECTED_EXIT=$?
set -e
if (( INJECTED_EXIT != 2 )); then
  echo "FAIL: packaged approval CLI accepted an unproposed path" >&2
  exit 2
fi
"$PY" - <<'PYEOF'
import json
from pathlib import Path
rule = json.loads(Path("applicability-rule.json").read_text(encoding="utf-8"))
assert rule == {
    "paths": ["docs/", "README.md"],
    "workflowRequired": False,
    "directDefaultBranchAllowed": False,
}
assert json.loads(Path("rejected-rule.json").read_text(encoding="utf-8")) is None
Path("agent-workflow.yaml").write_text(
    "version: 1\nproject: {name: consumer-repo}\n"
    "workRecord:\n  backend: local\n  local:\n"
    "    taskPath: \".agent-workflow/tasks/{slug}.md\"\n"
    "redline: required\nredlineVerdictPath: redline-verdict.json\n"
    "applicability:\n  documentationOnly:\n"
    f"    paths: [{', '.join(rule['paths'])}]\n"
    "    workflowRequired: false\n"
    f"    directDefaultBranchAllowed: {str(rule['directDefaultBranchAllowed']).lower()}\n",
    encoding="utf-8",
)
Path("agent-redline-policy.yaml").write_text(
    "version: 1\nproject: {name: consumer-repo}\n"
    "zones:\n  red:\n    - path: agent-redline-policy.yaml\n"
    "      reason: governance\n      checkpoint: architecture-review\n"
    "  blue:\n    - path: docs/**\n      reason: documentation\n"
    "    - path: README.md\n      reason: repository overview\n"
    "boundaryAdapter: {outputFormat: none}\napi: {type: none}\n"
    "checkpoints:\n  behavior-review:\n    description: behavior review\n"
    "    satisfiedBy: [codeownerApproval]\n"
    "  architecture-review:\n    description: review\n"
    "    satisfiedBy: [{label: architecture-reviewed}]\n"
    "modes: {default: binding}\n",
    encoding="utf-8",
)
paths = ["docs/guide.md", "README.md"]
Path("changed.z").write_bytes(b"\0".join(p.encode() for p in paths) + b"\0")
PYEOF
"$PY" scripts/agent-redline-report.py --policy agent-redline-policy.yaml \
  --changed-files-z changed.z --json-out redline-verdict.json >/dev/null
set +e
"$PY" scripts/agent-workflow-check.py --repo-root . \
  --changed-files-z changed.z --redline-verdict redline-verdict.json \
  > applicability-output.json 2>&1
APPLICABILITY_EXIT=$?
set -e
if (( APPLICABILITY_EXIT != 0 )); then
  echo "FAIL: packaged applicability checker exit $APPLICABILITY_EXIT" >&2
  cat applicability-output.json >&2
  exit 2
fi
"$PY" - <<'PYEOF' || { echo "FAIL: packaged applicability verdict was not explicit" >&2; exit 2; }
import json
payload = json.load(open("applicability-output.json", encoding="utf-8"))
predicates = [p for r in payload["records"] for p in r["predicates"]]
assert any(p["name"] == "workflow.applicability" and p["passed"] for p in predicates)
PYEOF

# A nested agent instruction remains protected even though Redline labels it blue.
printf 'docs/AGENTS.md\0' > changed.z
"$PY" scripts/agent-redline-report.py --policy agent-redline-policy.yaml \
  --changed-files-z changed.z --json-out redline-verdict.json >/dev/null
set +e
"$PY" scripts/agent-workflow-check.py --repo-root . \
  --changed-files-z changed.z --redline-verdict redline-verdict.json >/dev/null 2>&1
NESTED_EXIT=$?
set -e
if (( NESTED_EXIT != 2 )); then
  echo "FAIL: packaged nested instruction was not denied (exit $NESTED_EXIT)" >&2
  exit 2
fi

# A selected behavior contract is written only to Redline. It overrides the
# broad tests/** blue zone, resolves authority from CODEOWNERS, and drives the
# packaged Agent Workflow semantic gate.
mkdir -p tests/contracts .github
printf 'tests/contracts/** @contract-owner\n' > .github/CODEOWNERS
cp .github/CODEOWNERS base-CODEOWNERS
"$PY" - <<'PYEOF'
from pathlib import Path
policy = Path("agent-redline-policy.yaml").read_text(encoding="utf-8")
policy = policy.replace(
    "    - path: README.md\n      reason: repository overview\n",
    "    - path: README.md\n      reason: repository overview\n"
    "    - path: tests/**\n      reason: ordinary tests\n",
)
policy = policy.replace(
    "boundaryAdapter: {outputFormat: none}\n",
    "behaviorContracts:\n"
    "  paths: [tests/contracts/**]\n"
    "  verification: behavior-contracts\n"
    "  checkpoint: behavior-review\n"
    "excludes: [tests/contracts/**]\n"
    "boundaryAdapter: {outputFormat: none}\n",
)
policy = policy.replace(
    "checkpoints:\n",
    "checkpoints:\n"
    "  behavior-review:\n"
    "    description: behavior review\n"
    "    satisfiedBy: [codeownerApproval]\n",
)
Path("agent-redline-policy.yaml").write_text(policy, encoding="utf-8")
PYEOF
cat > .agent-workflow/tasks/contract.md <<'EOF'
<!-- agent-workflow:start -->
**Outcome:** Preserve repository behavior while reorganizing its contract test.

**Target:** consumer-repo

**Scope:** Contract test mechanics only.

**Constraints:** Required behavior remains unchanged.

**Completion criteria:** The behavior-contracts check covers the same behavior.

**Requirement baseline:** {"source":"bootstrap-e2e","outcome":"Preserve repository behavior while reorganizing its contract test.","scope":"Contract test mechanics only.","constraints":"Required behavior remains unchanged.","completion_criteria":"The behavior-contracts check covers the same behavior."}

**Risk:** High

**Complexity:** Moderate

**Reason:** A protected repository contract changes.

**Discovery:** Redline reported tests/contracts/wake.md with @contract-owner authority.

**Material assumptions:** Existing required CI and Code Owner review were verified during bootstrap.

**Plan:** Reorganize the contract without changing required behavior.

**Verification plan:** When the contract changes, the behavior-contracts check shall cover the same behavior → behavior-contracts.

**Plan review:** Agent technical review: bootstrap-e2e-review of fixture plan and verification.

**Approvals:** Approved by user 2026-09-22: "Approve bootstrap E2E fixture."

**Behavior changes:** [{"target":"repository-contract","path":"tests/contracts/wake.md","classification":"coverage-only","before":"Original contract mechanics.","after":"Reorganized contract mechanics.","reason":"Preserve behavior while reorganizing verification."}]

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Result review
Agent technical review: bootstrap-e2e-result-review
Reviewed revision: fixture-contract-revision
Verification adequacy: behavior-contracts covers the same behavior; fixture evidence inspected.
EOF
printf '.agent-workflow/tasks/contract.md\0tests/contracts/wake.md\0' > changed.z
"$PY" scripts/agent-redline-report.py --policy agent-redline-policy.yaml \
  --changed-files-z changed.z --codeowners-file base-CODEOWNERS \
  --codeowner-approvals contract-owner \
  --json-out redline-verdict.json >/dev/null
"$PY" scripts/agent-workflow-check.py --repo-root . --slug contract \
  --changed-files-z changed.z --redline-verdict redline-verdict.json \
  > behavior-contract-output.json
"$PY" - <<'PYEOF' || { echo "FAIL: packaged behavior-contract flow disagreed" >&2; exit 2; }
import json
from pathlib import Path
redline = json.loads(Path("redline-verdict.json").read_text(encoding="utf-8"))
assert redline["zones"]["red"] == ["tests/contracts/wake.md"]
assert redline["behaviorContractChanges"] == {
    "version": 1,
    "detected": True,
    "paths": [{
        "path": "tests/contracts/wake.md",
        "owners": ["@contract-owner"],
    }],
    "verification": "behavior-contracts",
    "checkpoint": "behavior-review",
}
payload = json.loads(Path("behavior-contract-output.json").read_text(encoding="utf-8"))
contract = next(r for r in payload["records"] if r["slug"] == "<behavior-contracts>")
assert contract["status"] == "clean"
assert all(p["passed"] for p in contract["predicates"])
PYEOF

# --- Step 5: second consumer layout. The same production approval CLI and
# both packaged callers use noncanonical paths and a relocated Work Record.
printf 'handbook/\0plans/\0' > proposal.z
printf 'handbook/\0' > approved.z
"$PY" scripts/agent-workflow-check.py --repo-root . \
  --bootstrap-applicability-proposal-z proposal.z \
  --bootstrap-applicability-approved-z approved.z \
  --bootstrap-direct-default-branch-approved \
  --bootstrap-protection-status unprotected > applicability-rule.json
"$PY" - <<'PYEOF'
import json
from pathlib import Path
rule = json.loads(Path("applicability-rule.json").read_text(encoding="utf-8"))
assert rule["paths"] == ["handbook/"]
assert rule["directDefaultBranchAllowed"] is True
Path("agent-workflow.yaml").write_text(
    "version: 1\nproject: {name: second-layout}\n"
    "workRecord:\n  backend: local\n  local:\n"
    "    taskPath: \".work/items/{slug}.record.md\"\n"
    "redline: required\nredlineVerdictPath: redline-verdict.json\n"
    "applicability:\n  documentationOnly:\n"
    "    paths: [handbook/]\n    workflowRequired: false\n"
    "    directDefaultBranchAllowed: true\n",
    encoding="utf-8",
)
Path("agent-redline-policy.yaml").write_text(
    "version: 1\nproject: {name: second-layout}\n"
    "zones:\n  red:\n    - path: agent-redline-policy.yaml\n"
    "      reason: governance\n      checkpoint: architecture-review\n"
    "  blue:\n    - path: handbook/**\n      reason: documentation\n"
    "    - path: .work/**\n      reason: task records\n"
    "    - path: quality/**\n      reason: ordinary quality assets\n"
    "behaviorContracts:\n  protection: workflow\n"
    "  paths: [quality/scenarios/**]\n"
    "  verification: scenario-contracts\n"
    "boundaryAdapter: {outputFormat: none}\napi: {type: none}\n"
    "checkpoints:\n  architecture-review:\n    description: review\n"
    "    satisfiedBy: [{label: architecture-reviewed}]\n"
    "modes: {default: binding}\n",
    encoding="utf-8",
)
Path("changed.z").write_bytes(b"handbook/guide.md\0")
PYEOF
"$PY" scripts/agent-redline-report.py --policy agent-redline-policy.yaml \
  --changed-files-z changed.z --json-out redline-verdict.json >/dev/null
"$PY" scripts/agent-workflow-check.py --repo-root . \
  --changed-files-z changed.z --redline-verdict redline-verdict.json >/dev/null

rm -f .github/CODEOWNERS base-CODEOWNERS

# The relocated Work Record and a different contract root exercise the same
# generated Redline → checker flow in the second repository layout.
mkdir -p quality/scenarios .work/items
"$PY" - <<'PYEOF'
import json
from pathlib import Path
record = Path(".agent-workflow/tasks/contract.md").read_text(encoding="utf-8")
record = record.replace("tests/contracts/wake.md", "quality/scenarios/flow.md")
record = record.replace("behavior-contracts", "scenario-contracts")
record = record.replace(
    "Existing required CI and Code Owner review were verified during bootstrap.",
    "PR execution of the named verification and combined harness was verified; merge enforcement is intentionally absent.",
)
lines = record.splitlines()
index = next(i for i, line in enumerate(lines) if line.startswith("**Behavior changes:** "))
lines[index] = "**Behavior changes:** " + json.dumps([{
    "target": "repository-contract",
    "path": "quality/scenarios/flow.md",
    "classification": "requirement-change",
    "before": "Deliver while unloaded.",
    "after": "Deliver on next resume.",
    "reason": "Exercise exact workflow-protection approval.",
    "impact": "Repository behavior changes.",
    "alternatives": "Keep the unloaded-delivery contract.",
    "authority": {"scope": "task", "name": "task-owner"},
    "approval": {
        "by": "user",
        "reference": "bootstrap-e2e-approval",
        "verbatim": "Approve delivery on next resume for this exact contract change.",
    },
}], separators=(",", ":"))
record = "\n".join(lines) + "\n"
Path(".work/items/layout-contract.record.md").write_text(record, encoding="utf-8")
Path("changed.z").write_bytes(
    b".work/items/layout-contract.record.md\0quality/scenarios/flow.md\0"
)
PYEOF
"$PY" scripts/agent-redline-report.py --policy agent-redline-policy.yaml \
  --changed-files-z changed.z --json-out redline-verdict.json >/dev/null
"$PY" scripts/agent-workflow-check.py --repo-root . \
  --changed-files-z changed.z --redline-verdict redline-verdict.json \
  > second-contract-output.json
"$PY" - <<'PYEOF'
import json
from pathlib import Path
redline = json.loads(Path("redline-verdict.json").read_text(encoding="utf-8"))
assert redline["zones"]["red"] == ["quality/scenarios/flow.md"]
assert redline["behaviorContractChanges"] == {
    "version": 2,
    "protection": "workflow",
    "detected": True,
    "paths": ["quality/scenarios/flow.md"],
    "verification": "scenario-contracts",
}
payload = json.loads(Path("second-contract-output.json").read_text(encoding="utf-8"))
contract = next(r for r in payload["records"] if r["slug"] == "<behavior-contracts>")
assert contract["status"] == "clean"
assert all(p["passed"] for p in contract["predicates"])
assert "merge is not enforced" in next(
    p["detail"] for p in contract["predicates"]
    if p["name"] == "behavior_contracts.requirement_changes_authorized"
)
PYEOF

# The packaged resolver uses the configured non-default path, preserves a supplied
# identity, and does not mutate the consumer record.
mkdir -p .work/items
cp .agent-workflow/tasks/bootstrap-consumer.md .work/items/persisted.record.md
cp .work/items/persisted.record.md resolver-before.md
"$PY" scripts/agent-workflow-check.py --repo-root . --resolve-work-record \
  --work-record-ref agent-workflow:persisted > resolver-output.json 2> resolver-error.txt
"$PY" scripts/agent-workflow-check.py --repo-root . --resolve-work-record \
  --work-record-ref agent-workflow:missing > resolver-absent.json 2>> resolver-error.txt
printf 'not a Work Record\n' > .work/items/malformed.record.md
set +e
"$PY" scripts/agent-workflow-check.py --repo-root . --resolve-work-record \
  --work-record-ref agent-workflow:malformed > resolver-malformed.json 2>> resolver-error.txt
RESOLVER_MALFORMED_EXIT=$?
set -e
"$PY" - <<'PYEOF'
from pathlib import Path
Path("agent-workflow.yaml").write_text(
    "version: 1\nproject: {name: bad-path}\nworkRecord:\n  backend: local\n  local:\n"
    '    taskPath: "tasks/\\0{slug}.md"\n',
    encoding="utf-8",
)
PYEOF
set +e
"$PY" scripts/agent-workflow-check.py --repo-root . --resolve-work-record \
  --work-record-ref agent-workflow:probe > resolver-nul.json 2>> resolver-error.txt
RESOLVER_NUL_EXIT=$?
set -e
cmp -s .work/items/persisted.record.md resolver-before.md
[[ ! -s resolver-error.txt ]]
[[ "$RESOLVER_MALFORMED_EXIT" -eq 2 ]]
[[ "$RESOLVER_NUL_EXIT" -eq 2 ]]
"$PY" - <<'PYEOF'
import json
from pathlib import Path
found = json.loads(Path("resolver-output.json").read_text(encoding="utf-8"))
assert found == {
    "schema_version": 1,
    "status": "found",
    "reason": "record_found",
    "work_record_ref": "agent-workflow:persisted",
    "slug": "persisted",
    "record_path": ".work/items/persisted.record.md",
    "record_state": "Ready for review",
    "message": None,
}
absent = json.loads(Path("resolver-absent.json").read_text(encoding="utf-8"))
assert (absent["status"], absent["reason"], absent["record_path"]) == (
    "absent", "record_not_found", ".work/items/missing.record.md"
)
malformed = json.loads(Path("resolver-malformed.json").read_text(encoding="utf-8"))
assert (malformed["status"], malformed["reason"]) == ("error", "malformed_record")
nul_path = json.loads(Path("resolver-nul.json").read_text(encoding="utf-8"))
assert (nul_path["status"], nul_path["reason"]) == ("error", "invalid_config")
assert "control characters" in nul_path["message"]
for name in (
    "resolver-output.json",
    "resolver-absent.json",
    "resolver-malformed.json",
    "resolver-nul.json",
):
    assert len(Path(name).read_bytes()) <= 8192
PYEOF

# Exercise the vendored entrypoint's Python-3.12 symlink-loop shape without
# depending on host symlink privileges.
"$PY" - <<'PYEOF'
import importlib.util
import io
import json
import sys
from pathlib import Path

Path("agent-workflow.yaml").write_text(
    "version: 1\nproject: {name: loop-path}\nworkRecord:\n  backend: local\n  local:\n"
    '    taskPath: ".work/items/{slug}.record.md"\n',
    encoding="utf-8",
)
spec = importlib.util.spec_from_file_location(
    "packaged_workflow_checker", "scripts/agent-workflow-check.py"
)
checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checker
assert spec.loader is not None
spec.loader.exec_module(checker)
original_resolve = checker.Path.resolve

def resolve(path, *args, **kwargs):
    if path.name == "loop.record.md":
        raise RuntimeError("Symlink loop from synthetic filesystem")
    return original_resolve(path, *args, **kwargs)

stdout_bytes, stderr_bytes = io.BytesIO(), io.BytesIO()
stdout = io.TextIOWrapper(stdout_bytes, encoding="utf-8")
stderr = io.TextIOWrapper(stderr_bytes, encoding="utf-8")
old_stdout, old_stderr = sys.stdout, sys.stderr
checker.Path.resolve = resolve
try:
    sys.stdout, sys.stderr = stdout, stderr
    code = checker.main([
        "--repo-root", ".", "--resolve-work-record",
        "--work-record-ref", "agent-workflow:loop",
    ])
    stdout.flush()
    stderr.flush()
finally:
    checker.Path.resolve = original_resolve
    sys.stdout, sys.stderr = old_stdout, old_stderr
payload = stdout_bytes.getvalue()
assert code == 2
assert stderr_bytes.getvalue() == b""
assert payload.count(b"\n") == 1 and len(payload) <= 8192
result = json.loads(payload)
assert (result["status"], result["reason"]) == ("error", "unsafe_record_path")
PYEOF

echo "ok: e2e bootstrap simulation passed (install → mixed/full required-verdict probes → approved applicability in two layouts → packaged read-only resolver; mixed reporter/checker $MIXED_REPORTER_EXIT/$MIXED_PROBE_EXIT, committed reporter/checker/missing $REPORTER_EXIT/$PROBE_EXIT/$MISSING_EXIT)."
