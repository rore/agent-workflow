#!/usr/bin/env bash
# tests/redline/run.sh
#
# Runs the curated set of agent-redline's own tests as part of our
# suite. Redline is bundled inside agent-workflow at core/agent-redline/;
# its tests run here so regressions in the risk detector surface in
# bash tests/run-all.sh, not later.
#
# Layer selection rationale lives in core/agent-redline/BASELINE.md.
# In short: we run the layers that exercise the verdict-producing
# logic and the skill content we consume; we skip layers that test
# redline's own development surface (scaffolding, packaging,
# demo-sync, language extensions that need Gradle/import-linter).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REDLINE_ROOT="$REPO_ROOT/core/agent-redline"

if [[ ! -f "$REDLINE_ROOT/tests/run-all.sh" ]]; then
  echo "error: $REDLINE_ROOT/tests/run-all.sh not found" >&2
  exit 1
fi

# Layers we run. Each one of redline's invocations is name-keyed; we
# pass --only with the layer name we want. Redline's runner exits
# non-zero on the first failing layer, so we invoke once per layer to
# keep failure attribution clear.
#
# Scope rationale:
# - schema, skill-yaml — validate the policy schema and the skill
#   frontmatter agent-workflow consumes via the assess-risk pointer.
# - reporter-goldens — the verdict-computation regression suite. This
#   is what guarantees the risk detector we depend on still behaves.
#
# Not included: skill-refs (needs the built dist/), reporter-unit
# (references scripts/ tooling we skipped), links (references docs/
# and top-level README we skipped), and the scaffolding/packaging/
# extension layers that test redline's own development surface. Those
# are not what we depend on; running them would just be noise.
LAYERS=(
  schema
  skill-yaml
  reporter-goldens
)

cd "$REDLINE_ROOT"

for layer in "${LAYERS[@]}"; do
  echo "  redline.$layer ..."
  bash tests/run-all.sh --only "$layer"
done

echo "  redline.reporter-evidence-unit ..."
if [[ -n "${PYTHON:-}" ]]; then
  REDLINE_PY="$PYTHON"
elif command -v python >/dev/null 2>&1; then
  REDLINE_PY=python
else
  REDLINE_PY=python3
fi
"$REDLINE_PY" -m pytest tests/reporter/test_reporter_unit.py -q

echo "  redline.node-profile ..."
"$REDLINE_PY" "$REPO_ROOT/tests/redline/check-node-profile.py"

echo "  redline.ci-evidence ..."
"$REDLINE_PY" "$REPO_ROOT/tests/redline/check-ci-evidence.py"
