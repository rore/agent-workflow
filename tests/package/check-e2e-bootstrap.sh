#!/usr/bin/env bash
# tests/package/check-e2e-bootstrap.sh
#
# Layer-3 end-to-end. Simulates a consumer adopting the skill from the
# committed dist, mechanically performs the file-write steps bootstrap
# Phase 4 would execute, then runs bootstrap Phase 6's self-probe
# (write _probe.md Work Record, run the vendored checker, expect clean
# exit). This is the cheapest test that proves what we ship actually
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
#   - Bootstrap Phase 6 probe plus the deterministic applicability approval
#     seam and packaged reporter/checker journeys in two consumer layouts.
#
# What this does NOT cover:
#   - LLM judgment used to identify candidate documentation paths; the test
#     covers validation, partial/rejected approval, and persistence mechanically.
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
PYEOF

cd "$CONSUMER"

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
"$PY" "$SKILL/hooks/merge-agents-section.py" --file AGENTS.md --template "$SKILL/templates/agents-section.md.template" >/dev/null
cp AGENTS.md AGENTS.before
"$PY" "$SKILL/hooks/merge-agents-section.py" --file AGENTS.md --template "$SKILL/templates/agents-section.md.template" >/dev/null
cmp -s AGENTS.md AGENTS.before || exit 2
cmp -s CLAUDE.md CLAUDE.before && cmp -s CODEX.md CODEX.before || exit 2
"$PY" - <<'PYEOF'
from pathlib import Path
t=Path("AGENTS.md").read_text()
assert "Root prose before." in t and "Root prose after." in t and "STALE BODY" not in t
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
    "redline: optional\n",
    encoding="utf-8",
)
PYEOF

# 2b. .agent-workflow/tasks/ skeleton.
mkdir -p .agent-workflow/tasks

# 2c. agent-redline-policy.yaml from the redline template. We
# do not exercise the policy here — the workflow checker only needs
# it absent or syntactically present, and the file is part of the
# install surface.
cp "$SKILL/agent-redline/assets/templates/agent-policy.yaml.template" \
   agent-redline-policy.yaml \
  || { echo "FAIL: could not copy agent-policy.yaml.template" >&2; exit 2; }

# 2d. Vendored checker + reporter. These are the same scripts the
# install probe already exercised; here we make sure they live at the
# consumer-repo locations bootstrap-mode names.
mkdir -p scripts
cp "$SKILL/scripts/agent-workflow-check.py" scripts/agent-workflow-check.py
cp "$SKILL/agent-redline/scripts/agent-redline-report.py" scripts/agent-redline-report.py

# 2e. CI workflow. Just confirm we can lay it down — the template
# contains the workflow YAML.
mkdir -p .github/workflows
cp "$SKILL/templates/.github/workflows/agent-workflow.yml.template" \
   .github/workflows/agent-workflow.yml

# --- Step 3: Phase 6 self-probe. Write a minimal compact-shape Work
# Record at _probe slug and run the vendored checker against it.
# Pattern from core/skill/bootstrap-mode.md §6.2.
cat > .agent-workflow/tasks/_probe.md <<'EOF'
<!-- agent-workflow:start -->
**Outcome:** Probe Work Record for the bootstrap self-check.

**Target:** consumer-repo

**Scope:** None — probe record only.

**Constraints:** —

**Completion criteria:** Checker exits cleanly against this record.

**Risk:** Routine

**Complexity:** Simple

**Reason:** —

**Approach:** —

**Verification:** This file is verified by `scripts/agent-workflow-check.py --slug _probe`.

**State:** Ready for review
<!-- agent-workflow:end -->
EOF

set +e
"$PY" scripts/agent-workflow-check.py --repo-root . --slug _probe > probe-output.txt 2>&1
PROBE_EXIT=$?
set -e

# Exit code 0 = clean; 1 = advisory only (e.g. redline verdict not
# present — that's fine for a probe on a synthetic repo). Anything
# else fails the simulation.
if (( PROBE_EXIT > 1 )); then
  echo "FAIL: probe checker exit code $PROBE_EXIT (expected 0 or 1)" >&2
  echo "--- checker output ---" >&2
  cat probe-output.txt >&2
  exit 2
fi

# Confirm the checker actually produced a verdict (non-empty output).
if [[ ! -s probe-output.txt ]]; then
  echo "FAIL: probe checker produced no output" >&2
  exit 2
fi

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
    "checkpoints:\n  architecture-review:\n    description: review\n"
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

echo "ok: e2e bootstrap simulation passed (install → probe → approved packaged applicability in two layouts; checker exit $PROBE_EXIT)."