#!/usr/bin/env bash
# tests/links/run.sh
#
# Validate every relative link in the repo's markdown resolves to a real path.
# Implementation in tests/links/check-links.py. Same checker pattern + skip-set
# the agent-redline subtree uses upstream.
#
# Exit codes mirror check-links.py: 0 clean, 2 at least one broken link.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Use the standard PY shim so this works on Windows / Git Bash where
# `python3` may be bare while `python` has the deps. F8 fix made the
# rest of the test runners consistent on this.
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

exec "$PY" tests/links/check-links.py "$@"
