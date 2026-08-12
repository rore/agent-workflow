#!/usr/bin/env bash
# tests/schema/run.sh
#
# Pytest layer for the agent-workflow.yaml schema + loader.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

if command -v python >/dev/null 2>&1; then
  PY=python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "error: no python interpreter found on PATH" >&2
  exit 1
fi

exec "$PY" -m pytest tests/schema -q
