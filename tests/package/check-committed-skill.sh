#!/usr/bin/env bash
# tests/package/check-committed-skill.sh
#
# Drift check: the committed .claude/skills/agent-workflow/ (what Claude
# Code activates when this repo is opened as a project) must match the
# committed dist/agent-workflow/ (the install artifact). Both are produced
# by scripts/package-skill.sh from the same source, so they are identical
# trees.
#
# Unlike a typical consumer, this repo commits the skill itself — not just
# dist/ — so a fresh clone is governed by /agent-workflow with no manual
# install step, and the committed .claude/hooks/ don't point at a missing
# skill. This check keeps that committed copy from drifting out of sync
# when someone edits skill source without re-installing.
#
# Exit codes:
#   0 — committed skill matches dist/
#   1 — script error (a tree is missing)
#   2 — drift detected (run scripts/install-skill-locally.sh and commit)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL="$REPO_ROOT/.claude/skills/agent-workflow"
DIST="$REPO_ROOT/dist/agent-workflow"

[[ -d "$DIST" ]] || { echo "error: $DIST missing — run scripts/package-skill.sh first" >&2; exit 1; }
[[ -d "$SKILL" ]] || { echo "error: $SKILL missing — the committed skill is required; run scripts/install-skill-locally.sh" >&2; exit 1; }

# --strip-trailing-cr tolerates CRLF/LF differences on Windows checkouts,
# matching check-package.sh.
DIFF_OUTPUT=$(diff -r --strip-trailing-cr "$SKILL" "$DIST" 2>&1 || true)

if [[ -n "$DIFF_OUTPUT" ]]; then
  echo "FAIL: .claude/skills/agent-workflow/ is out of sync with dist/agent-workflow/." >&2
  echo "Run: bash scripts/install-skill-locally.sh && git add .claude/skills/agent-workflow/" >&2
  echo >&2
  echo "Diff (truncated to 100 lines):" >&2
  echo "$DIFF_OUTPUT" | head -100 >&2
  exit 2
fi

echo "ok: .claude/skills/agent-workflow/ matches dist/agent-workflow/."
