#!/usr/bin/env bash
# tests/tuner/run.sh
#
# Diff the tuner's output against each fixture's expected.md.
# Fixtures live in tests/tuner/fixtures/<name>/; each carries:
#   meta.json — {"repo": "<org>/<name>"}
#   merged-prs.json — output of `gh pr list ...`
#   pr-N-approvers.json — output per PR
#   org-teams.json — output of `gh api orgs/<org>/teams`
#   team-<slug>-members.json — output per team
#   expected.md — the rendered markdown the tuner must produce
#
# Fixture mode (--mock-gh-fixture) keeps these tests offline.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Prefer `python` (Windows / Git Bash); fall back to `python3` (Linux / WSL).
# Same shim the other test runners use. Overridable with PYTHON=path.
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

# These fixtures exercise the CODEOWNERS-proposal layer. The calibration
# layer is held constant by pointing --policy at a path that does not
# exist — that yields the "_No red rules..._" placeholder block the
# expected.md files all carry. Without this, the tuner picks up
# whatever policy happens to live at its default path (e.g. the dev
# repo's own agent-redline-policy.yaml once installed), and the
# fixtures' expected.md drifts. A fixture that wants to test
# calibration too should carry its own policy.yaml and pass it through.
NULL_POLICY="$REPO_ROOT/tests/tuner/.no-such-policy.yaml"
[[ -f "$NULL_POLICY" ]] && rm "$NULL_POLICY"  # belt-and-suspenders

failed=0
for fixture in tests/tuner/fixtures/*/; do
  name=$(basename "$fixture")
  expected="${fixture}expected.md"
  if [[ ! -f "$expected" ]]; then
    echo "  $name — no expected.md, skipping"
    continue
  fi
  # A fixture that carries its own policy.yaml exercises the calibration
  # layer; otherwise hold calibration constant with the NULL policy so the
  # CODEOWNERS-only fixtures render their "_No red rules_" placeholder.
  policy="${fixture}policy.yaml"
  [[ -f "$policy" ]] || policy="$NULL_POLICY"
  actual=$("$PY" scripts/agent-workflow-tune.py --mock-gh-fixture "$fixture" --policy "$policy" 2>&1)
  expected_content=$(cat "$expected")
  if [[ "$actual" == "$expected_content" ]]; then
    echo "  $name — ok"
  else
    echo "  $name — FAIL"
    diff -u "$expected" <(printf "%s\n" "$actual") || true
    failed=$((failed + 1))
  fi
done

# Unit layer: parse-path + glob-matching regressions that fixture mode can't
# reach (the live gh path) or under-specifies (glob edge cases). Run after the
# fixture diffs; fail the layer if either the diffs or the units fail. Not
# `exec pytest` — that would skip the loop above.
echo "[ pytest tests/tuner ]"
if ! "$PY" -m pytest tests/tuner -q; then
  failed=$((failed + 1))
fi

if [[ $failed -gt 0 ]]; then
  echo
  echo "$failed check(s) failed"
  exit 1
fi
