#!/usr/bin/env bash
# tests/run-all.sh
#
# Full local test suite. CI runs the same script.
#
# Layers (each also runnable directly):
#   tests/budget/check-budget.sh    — file-size ceilings on agent-loaded files
#   tests/schema/check-schema.sh    — validate templates against JSON Schemas
#   tests/checker/run-checker.sh    — golden inputs/outputs for the CI checker
#   tests/links/check-links.sh      — markdown link integrity
#   tests/package/check-package.sh  — committed dist/agent-workflow/ matches source
#
# Usage:
#   bash tests/run-all.sh
#   bash tests/run-all.sh --verbose
#   bash tests/run-all.sh --only budget       # one layer
#   bash tests/run-all.sh --skip checker      # skip a layer

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAYERS=(budget schema work-record checker redline tuner hooks links package)
ONLY=""
SKIP=""
VERBOSE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --only) ONLY="$2"; shift 2 ;;
    --skip) SKIP="$2"; shift 2 ;;
    --verbose) VERBOSE=1; shift ;;
    -h|--help)
      sed -n '2,/^$/p' "$0" | sed 's/^# \?//'
      exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

run_layer() {
  local name="$1"
  local script="$REPO_ROOT/tests/$name/run.sh"
  if [[ ! -f "$script" ]]; then
    echo "  $name — skipped (no run.sh yet)"
    return 0
  fi
  echo "[ $name ]"
  if [[ "$VERBOSE" == "1" ]]; then
    bash "$script"
  else
    bash "$script" >/dev/null
  fi
  echo "  $name — ok"
}

for layer in "${LAYERS[@]}"; do
  [[ -n "$ONLY" && "$layer" != "$ONLY" ]] && continue
  [[ -n "$SKIP" && "$layer" == "$SKIP" ]] && continue
  run_layer "$layer"
done

echo
echo "all layers ok"
