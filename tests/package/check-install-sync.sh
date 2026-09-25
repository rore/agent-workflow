#!/usr/bin/env bash
# Run the installer on a scratch source tree; all native installs must match dist.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -n "${PYTHON:-}" ]]; then PY="$PYTHON"; elif command -v python >/dev/null 2>&1; then PY=python; else PY=python3; fi
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cp -r "$REPO_ROOT/core" "$REPO_ROOT/scripts" "$TMP/"
bash "$TMP/scripts/install-skill-locally.sh" >/dev/null
for target in "$TMP/.claude/skills/agent-workflow" "$TMP/.agents/skills/agent-workflow"; do
  diff -r --strip-trailing-cr "$TMP/dist/agent-workflow" "$target"
done
"$PY" - "$TMP/dist/agent-workflow" <<'PYEOF'
import sys
from pathlib import Path
root = Path(sys.argv[1])
agents = (root / "templates/agents-section.md.template").read_text()
summary = (root / "templates/bootstrap-summary.md.template").read_text()
bootstrap = (root / "bootstrap-mode.md").read_text()
assert "<skill>/templates/checkpoints/" in agents
assert ".claude/skills/agent-workflow/templates/checkpoints/" in summary
assert ".agents/skills/agent-workflow/templates/checkpoints/" in summary
assert "Leave any existing `docs/agent-workflow/` mirror and links intact" in bootstrap
assert "do not create or refresh it" in bootstrap
PYEOF
echo "ok: one-build install parity and bootstrap mirror guidance passed"