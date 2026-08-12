#!/usr/bin/env bash
# tests/budget/run.sh
#
# Enforce file-size ceilings on agent-loaded files. Budgets are declared in
# tests/budget/budget.yaml. Implementation lives in check-budget.sh — same
# pattern + parser the agent-redline subtree uses.
#
# Exit codes mirror check-budget.sh: 0 clean, 1 script error, 2 budget breach.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$REPO_ROOT/tests/budget/check-budget.sh" "$@"
