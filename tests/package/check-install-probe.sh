#!/usr/bin/env bash
# tests/package/check-install-probe.sh
#
# Layer-2 install probe. Copies the packaged dist into a temp directory
# (simulating a consumer's .claude/skills/agent-workflow/) and verifies
# the install is minimally functional:
#
#   - A required-file manifest is present and non-empty.
#   - SKILL.md frontmatter parses with non-empty name + description.
#   - The vendored checker is invokable (`--help` exits 0).
#   - The vendored redline reporter is invokable (`--help` exits 0).
#
# Catches: a file rename that the packager missed, a script that won't
# even start, missing frontmatter.
#
# Does not test: bootstrap behaviour end-to-end (that's check-e2e-bootstrap.sh).
#
# Exit codes:
#   0 — probe passed
#   1 — script error
#   2 — probe failed (named in stderr)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIST="$REPO_ROOT/dist/agent-workflow"

# Prefer `python` (Windows / Git Bash); fall back to `python3` (Linux / WSL).
# Overridable with PYTHON=path.
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

[[ -d "$DIST" ]] || { echo "error: $DIST missing — run scripts/package-skill.sh first" >&2; exit 1; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
PROBE="$TMP/agent-workflow"
cp -r "$DIST" "$PROBE"

errors=()

require() {
  local path="$1"
  if [[ ! -e "$PROBE/$path" ]]; then
    errors+=("missing: $path")
  elif [[ -f "$PROBE/$path" && ! -s "$PROBE/$path" ]]; then
    errors+=("empty: $path")
  fi
}

# Required manifest — files a consumer install must have. Update this
# list deliberately when the skill surface changes; the layer-1
# reference check covers in-markdown links, and this list backs up the
# files those references depend on.
require "SKILL.md"
require "operating-mode.md"
require "bootstrap-mode.md"
require "templates/checkpoints/establish-context.md"
require "templates/checkpoints/assess-risk.md"
require "templates/checkpoints/verify.md"
require "templates/agents-section.md.template"
require "templates/agent-workflow.yaml.template"
require "templates/work-record-routine.md"
require "templates/work-record-expanded.md"
require "templates/.github/workflows/agent-workflow.yml.template"
require "assets/schema/agent-workflow.schema.json"
require "scripts/agent-workflow-check.py"
require "scripts/format-verdict-comment.py"
require "scripts/agent-workflow-tune.py"
require "hooks/seed-workflow.sh"
require "hooks/reinforce-workflow.sh"
require "hooks/check-plan.sh"
require "hooks/check-plan.py"
require "hooks/install-settings.py"
require "hooks/merge-agents-section.py"
require "manifest.txt"
require "agent-redline/SKILL.md"
require "agent-redline/operating-mode.md"
require "agent-redline/bootstrap-mode.md"
require "agent-redline/assets/schema/agent-policy.schema.json"
require "agent-redline/assets/templates/agent-policy.yaml.template"
require "agent-redline/assets/templates/AGENTS.md.template"
require "agent-redline/assets/templates/pre-push-check.sh"
require "agent-redline/scripts/agent-redline-report.py"
require "agent-redline/extensions/jvm-archunit/profile.md"
require "agent-redline/extensions/python/profile.md"

# SKILL.md frontmatter sanity.
"$PY" - "$PROBE/SKILL.md" <<'PYEOF' || errors+=("SKILL.md frontmatter invalid")
import re, sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding="utf-8")
m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
if not m:
    sys.exit("no frontmatter block")
fm = m.group(1)
if not re.search(r"^name:\s*\S+", fm, re.MULTILINE):
    sys.exit("missing/empty name")
if not re.search(r"^description:\s*\S+", fm, re.MULTILINE):
    sys.exit("missing/empty description")
PYEOF

# Invokability.
"$PY" "$PROBE/scripts/agent-workflow-check.py" --help >/dev/null 2>&1 \
  || errors+=("agent-workflow-check.py --help failed")
"$PY" "$PROBE/agent-redline/scripts/agent-redline-report.py" --help >/dev/null 2>&1 \
  || errors+=("agent-redline-report.py --help failed")

# Manifest completeness — the forward check a consumer runs to confirm the
# install is whole: every path listed in manifest.txt exists with the recorded
# byte size. Authoritative for missing/corrupt files. (The reverse direction —
# "no unlisted file" — is intentionally NOT enforced: a real consumer generates
# __pycache__/.pyc under the skill tree, which would false-fail.)
verify_manifest() {
  "$PY" - "$1" <<'PYEOF'
import os, sys
root = sys.argv[1]
bad = []
with open(os.path.join(root, "manifest.txt"), encoding="utf-8") as fh:
    for line in fh:
        line = line.rstrip("\n")
        if not line:
            continue
        rel, _, size = line.partition("\t")
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            bad.append("missing: " + rel)
        elif str(os.path.getsize(p)) != size:
            bad.append("size %s != %s: %s" % (os.path.getsize(p), size, rel))
sys.exit(2 if bad else 0)
PYEOF
}
verify_manifest "$PROBE" || errors+=("manifest verify failed on a clean install")

# Negative test — corrupting a listed file MUST be detected (proves the check
# has teeth). $PROBE is a throwaway temp copy.
printf 'x' >> "$PROBE/SKILL.md"
if verify_manifest "$PROBE"; then
  errors+=("manifest verify did NOT detect a corrupted file (negative test)")
fi

if (( ${#errors[@]} > 0 )); then
  echo "FAIL: install probe ${#errors[@]} issue(s):" >&2
  for e in "${errors[@]}"; do
    echo "  - $e" >&2
  done
  exit 2
fi

echo "ok: install probe passed (manifest + frontmatter + invokability)."
