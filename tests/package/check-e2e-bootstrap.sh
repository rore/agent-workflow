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
#   - Bootstrap Phase 6 probe: write a _probe Work Record using the
#     compact-shape template, run the vendored checker, expect exit
#     code 0 or 1 (clean / advisory) — exit 2 means the probe broke.
#
# What this does NOT cover:
#   - Conversational bootstrap behaviour (the Phase 1–3 inspection /
#     proposal / adapt steps need an LLM; layer-3 stays mechanical).
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

cd "$CONSUMER"

# --- Step 2: Phase 4 writes — perform mechanical equivalents of what
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

echo "ok: e2e bootstrap simulation passed (install → Phase 4 writes → Phase 6 probe; checker exit $PROBE_EXIT)."
