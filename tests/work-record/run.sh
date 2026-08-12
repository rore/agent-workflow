#!/usr/bin/env bash
# tests/work-record/run.sh
#
# Pytest layer for the Work Record parser. Run as part of the full
# suite (tests/run-all.sh) or directly for fast iteration.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Use python3 if python isn't on PATH (matches agent-redline's shim).
if command -v python >/dev/null 2>&1; then
  PY=python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "error: no python interpreter found on PATH" >&2
  exit 1
fi

# -q: quiet (one dot per test); the run-all orchestrator suppresses
# everything anyway when --verbose isn't passed.
exec "$PY" -m pytest tests/work-record -q
