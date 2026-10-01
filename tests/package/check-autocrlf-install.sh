#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIST="$REPO_ROOT/dist/agent-workflow"
PY="${PYTHON:-python}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
CONSUMER="$TMP/consumer"
CHECKOUT="$TMP/autocrlf"
CLAUDE="$CONSUMER/.claude/skills/agent-workflow"
CODEX="$CONSUMER/.agents/skills/agent-workflow"

[[ -d "$DIST" ]] || { echo "error: run scripts/package-skill.sh first" >&2; exit 1; }
mkdir -p "$CLAUDE" "$CODEX" "$CONSUMER/.claude/hooks" "$CONSUMER/scripts" \
  "$CONSUMER/.github/workflows"
cp -r "$DIST/." "$CLAUDE/"
cp -r "$DIST/." "$CODEX/"
cp "$CLAUDE/hooks/"*.sh "$CONSUMER/.claude/hooks/"
cp "$CLAUDE/scripts/agent-workflow-check.py" "$CLAUDE/scripts/agent-workflow-runtime.py" \
  "$CLAUDE/scripts/agent-workflow-runtime.sh" "$CODEX/agent-redline/scripts/agent-redline-report.py" \
  "$CONSUMER/scripts/"
cp "$CLAUDE/agent-redline/assets/templates/pre-push-check.sh" \
  "$CONSUMER/scripts/agent-redline-check.sh"
cp "$CLAUDE/templates/.github/workflows/agent-workflow.yml.template" \
  "$CONSUMER/.github/workflows/agent-workflow.yml"
mkdir -p "$CONSUMER/docs"
printf 'keep\n' > "$CONSUMER/docs/keep.txt"
printf '#!/bin/sh\necho vendor\n' > "$CONSUMER/.claude/hooks/vendor.sh"
printf '#!/usr/bin/env python3\nprint("vendor")\n' > "$CONSUMER/scripts/agent-workflow-tune.py"
printf '#!/bin/sh\necho vendor\n' > "$CONSUMER/scripts/agent-redline-vendor.sh"

# Preserve an unrelated rule while adding only the install's scoped rules.
printf 'docs/** text eol=crlf\n' > "$CONSUMER/.gitattributes"
printf '.claude/hooks/vendor.sh text eol=crlf\n' >> "$CONSUMER/.gitattributes"
printf 'scripts/agent-workflow-tune.py text eol=crlf\n' >> "$CONSUMER/.gitattributes"
printf 'scripts/agent-redline-vendor.sh text eol=crlf\n' >> "$CONSUMER/.gitattributes"
while IFS= read -r rule; do
  grep -Fxq "$rule" "$CONSUMER/.gitattributes" || printf '%s\n' "$rule" >> "$CONSUMER/.gitattributes"
done < "$CLAUDE/templates/agent-workflow-consumer.gitattributes"

cd "$CONSUMER"
git init -q
git config user.name "Install probe"
git config user.email "install-probe@example.invalid"
git add -A
for path in \
  .claude/hooks/seed-workflow.sh .claude/hooks/check-plan.sh .claude/hooks/reinforce-workflow.sh \
  scripts/agent-workflow-runtime.sh scripts/agent-redline-check.sh \
  scripts/agent-workflow-check.py scripts/agent-workflow-runtime.py scripts/agent-redline-report.py; do
  git update-index --chmod=+x -- "$path"
done
git commit -qm "install workflow fixture"
git -c core.autocrlf=true -c core.filemode=true clone -q --local "$CONSUMER" "$CHECKOUT"

"$PY" - "$CHECKOUT" <<'PYEOF'
import sys
from pathlib import Path

root = Path(sys.argv[1])
manifests = []
skill_roots = (root / ".claude/skills/agent-workflow", root / ".agents/skills/agent-workflow")
for skill in (root / ".claude/skills/agent-workflow", root / ".agents/skills/agent-workflow"):
    raw = (skill / "manifest.txt").read_bytes()
    manifests.append(raw)
    for line in raw.splitlines():
        rel, size = line.decode("utf-8").split("\t")
        path = skill / rel
        assert path.is_file() and path.stat().st_size == int(size), rel
assert manifests[0] == manifests[1]
entries = [line.decode("utf-8").split("\t", 1)[0] for line in manifests[0].splitlines()]
for rel in entries:
    assert (skill_roots[0] / rel).read_bytes() == (skill_roots[1] / rel).read_bytes(), rel
assert b"docs/** text eol=crlf" in (root / ".gitattributes").read_bytes()
assert b".claude/hooks/vendor.sh text eol=crlf" in (root / ".gitattributes").read_bytes()
assert b"scripts/agent-workflow-tune.py text eol=crlf" in (root / ".gitattributes").read_bytes()
assert b"scripts/agent-redline-vendor.sh text eol=crlf" in (root / ".gitattributes").read_bytes()
assert b"\r\n" in (root / "docs/keep.txt").read_bytes()
assert b"\r\n" in (root / ".claude/hooks/vendor.sh").read_bytes()
assert b"\r\n" in (root / "scripts/agent-workflow-tune.py").read_bytes()
assert b"\r\n" in (root / "scripts/agent-redline-vendor.sh").read_bytes()
assert b"\r\n" not in (root / "scripts/agent-workflow-runtime.sh").read_bytes()
PYEOF

for path in \
  .claude/hooks/seed-workflow.sh .claude/hooks/check-plan.sh .claude/hooks/reinforce-workflow.sh \
  scripts/agent-workflow-runtime.sh scripts/agent-redline-check.sh \
  scripts/agent-workflow-check.py scripts/agent-workflow-runtime.py scripts/agent-redline-report.py; do
  mode="$(git -C "$CHECKOUT" ls-files --stage -- "$path" | cut -d' ' -f1)"
  [[ "$mode" == 100755 ]] || { echo "FAIL: $path mode is $mode, expected 100755" >&2; exit 2; }
done
for path in docs/keep.txt .claude/hooks/vendor.sh scripts/agent-workflow-tune.py scripts/agent-redline-vendor.sh; do
  mode="$(git -C "$CHECKOUT" ls-files --stage -- "$path" | cut -d' ' -f1)"
  [[ "$mode" == 100644 ]] || { echo "FAIL: unrelated $path mode is $mode, expected 100644" >&2; exit 2; }
done
bash -n "$CHECKOUT/scripts/agent-workflow-runtime.sh"
PYTHON="$PY" bash "$CHECKOUT/scripts/agent-workflow-runtime.sh" codex seed >/dev/null
echo "ok: autocrlf fresh clone preserves both manifests, LF, shell startup and executable modes."
