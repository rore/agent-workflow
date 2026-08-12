#!/usr/bin/env bash
# tests/package/check-package.sh
#
# Drift check: rebuilds the skill package into a temp directory, then
# compares against the committed dist/agent-workflow/. If they differ,
# someone changed source-of-truth files (core/skill/*,
# core/templates/checkpoints/*, the bundled redline subtree, or one of
# the scripts the install carries) without re-running
# scripts/package-skill.sh.
#
# Exit codes:
#   0 — package is up to date with sources
#   1 — script error (dist missing, build failed)
#   2 — drift detected (run scripts/package-skill.sh and commit the result)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIST="$REPO_ROOT/dist/agent-workflow"

[[ -d "$DIST" ]] || { echo "error: $DIST missing — run scripts/package-skill.sh first" >&2; exit 1; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

bash "$REPO_ROOT/scripts/package-skill.sh" --dest "$TMP/agent-workflow" >/dev/null

# Compare every file. --strip-trailing-cr tolerates CRLF/LF differences
# in case Git's autocrlf setting bites on Windows checkouts.
DIFF_OUTPUT=$(diff -r --strip-trailing-cr "$DIST" "$TMP/agent-workflow" 2>&1 || true)

if [[ -n "$DIFF_OUTPUT" ]]; then
  echo "FAIL: dist/agent-workflow/ is out of sync with sources." >&2
  echo "Run: bash scripts/package-skill.sh && git add dist/agent-workflow/" >&2
  echo >&2
  echo "Diff (truncated to 100 lines):" >&2
  echo "$DIFF_OUTPUT" | head -100 >&2
  exit 2
fi

echo "ok: dist/agent-workflow/ matches sources."
