#!/usr/bin/env bash
# scripts/package-skill.sh
#
# Build the dist/agent-workflow/ tree — the install source for the
# agent-workflow skill. Two callers:
#   1. The committed dist/agent-workflow/ in this repo (checked in;
#      a visitor can install by copying the directory).
#   2. The local dogfood install via scripts/install-skill-locally.sh
#      (gitignored target under .claude/skills/agent-workflow/).
#
# The packaged tree is self-contained: every reference inside skill
# markdown resolves inside the package. Source markdown uses repo-root
# paths (core/templates/..., core/agent-redline/core/...); this script
# applies path substitutions at build time so the dist markdown points
# at the packaged locations (templates/..., agent-redline/...).
#
# Layout:
#   dist/agent-workflow/
#   ├── SKILL.md, operating-mode.md, bootstrap-mode.md
#   ├── templates/
#   │   ├── checkpoints/*.md
#   │   ├── agents-section.md.template
#   │   ├── work-record-routine.md, work-record-expanded.md
#   │   ├── agent-workflow.yaml.template
#   │   └── .github/workflows/agent-workflow.yml.template
#   ├── assets/schema/agent-workflow.schema.json
#   ├── scripts/
#   │   ├── agent-workflow-check.py        (rebuilt from core/checker/ at package time)
#   │   ├── format-verdict-comment.py
#   │   └── agent-workflow-tune.py
#   └── agent-redline/                     (self-contained, mirrors redline's own dist)
#       ├── SKILL.md, operating-mode.md, bootstrap-mode.md
#       ├── references/per-checkpoint/*.md
#       ├── assets/schema/*.json, assets/templates/*
#       ├── scripts/agent-redline-report.py
#       └── extensions/{jvm-archunit,python}/...
#
# Usage:
#   scripts/package-skill.sh                  # writes dist/agent-workflow/
#   scripts/package-skill.sh --dest <path>    # writes the given directory

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$REPO_ROOT/dist/agent-workflow"
EXPLICIT_DEST=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest) TARGET="$2"; EXPLICIT_DEST=1; shift 2 ;;
    -h|--help)
      sed -n '2,/^$/p' "$0" | sed 's/^# \?//'
      exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

# ---------------------------------------------------------------------
# Sanity checks on sources.
# ---------------------------------------------------------------------

required_paths=(
  "core/skill/agent-workflow.md"
  "core/skill/operating-mode.md"
  "core/skill/bootstrap-mode.md"
  "core/skill/hooks/seed-workflow.sh"
  "core/skill/hooks/reinforce-workflow.sh"
  "core/skill/hooks/check-plan.sh"
  "core/skill/hooks/check-plan.py"
  "core/skill/hooks/install-settings.py"
  "core/skill/hooks/merge-agents-section.py"
  "core/templates/checkpoints"
  "core/templates/agents-section.md.template"
  "core/templates/work-record-routine.md"
  "core/templates/work-record-expanded.md"
  "core/templates/bootstrap-summary.md.template"
  "core/templates/skill-feedback.md"
  "core/templates/agent-workflow.yaml.template"
  "core/templates/.github/workflows/agent-workflow.yml.template"
  "core/schema/agent-workflow.schema.json"
  "core/agent-redline/core/skill/agent-redline.md"
  "core/agent-redline/core/skill/bootstrap-mode.md"
  "core/agent-redline/core/skill/operating-mode.md"
  "core/agent-redline/core/templates/skills"
  "core/agent-redline/core/templates/agent-policy.yaml.template"
  "core/agent-redline/core/templates/AGENTS.md.template"
  "core/agent-redline/core/templates/pr-template.md"
  "core/agent-redline/core/templates/pre-push-check.sh"
  "core/agent-redline/core/templates/suppressions.yaml"
  "core/agent-redline/core/schema/agent-policy.schema.json"
  "core/agent-redline/core/schema/boundary-violations.schema.json"
  "core/agent-redline/core/schema/suppressions.schema.json"
  "core/agent-redline/core/reporter/reporter.py"
  "core/agent-redline/extensions/jvm-archunit"
  "core/agent-redline/extensions/python"
  "scripts/format-verdict-comment.py"
  "scripts/agent-workflow-tune.py"
  "scripts/build-vendored-checker.sh"
)
for p in "${required_paths[@]}"; do
  [[ -e "$REPO_ROOT/$p" ]] || { echo "error: missing source $p" >&2; exit 1; }
done

# ---------------------------------------------------------------------
# Wipe destination and rebuild.
# ---------------------------------------------------------------------

rm -rf "$TARGET"
mkdir -p "$TARGET/templates/checkpoints" \
         "$TARGET/templates/.github/workflows" \
         "$TARGET/assets/schema" \
         "$TARGET/scripts" \
         "$TARGET/hooks" \
         "$TARGET/agent-redline/references/per-checkpoint" \
         "$TARGET/agent-redline/assets/schema" \
         "$TARGET/agent-redline/assets/templates" \
         "$TARGET/agent-redline/scripts" \
         "$TARGET/agent-redline/extensions"

# ---------------------------------------------------------------------
# Path-substitution helpers.
#
# Skill markdown in core/skill/ and core/agent-redline/core/skill/
# references repo-root paths that don't exist in the packaged layout.
# Rewrite them at build time so a consumer's installed skill can
# resolve every reference inside its own directory.
#
# Workflow side (paths inside the package are package-root-relative):
#   core/templates/.github/      → templates/.github/
#   core/templates/checkpoints/  → templates/checkpoints/
#   core/templates/              → templates/
#   core/schema/                 → assets/schema/
#   core/agent-redline/core/reporter/reporter.py → agent-redline/scripts/agent-redline-report.py
#   core/agent-redline/core/     → agent-redline/
#   <install-root>/scripts/agent-workflow-check.py.bundled → scripts/agent-workflow-check.py
#   <install-root>/              → ./
#
# Redline side (substituted within agent-redline/* only, matching
# redline's own package-skill.sh rewrites):
#   core/templates/skills/       → references/per-checkpoint/
#   core/templates/              → assets/templates/
#   core/schema/                 → assets/schema/
#   core/reporter/reporter.py    → scripts/agent-redline-report.py
#   core/reporter/               → scripts/
# ---------------------------------------------------------------------

substitute_workflow_paths() {
  local src="$1" dst="$2"
  python3 - "$src" "$dst" <<'PYEOF'
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
text = src.read_text(encoding="utf-8")

# Order matters — most specific first. The source skill markdown uses
# repo-root paths from the dev tree (core/templates/..., core/agent-redline/...)
# AND already-install-root-relative paths (agent-redline/core/skill/...)
# that resolve in the dev install but not in the packaged dist. Both
# get rewritten here so the dist is self-resolving.
substitutions = [
    # Dev-tree repo-root paths.
    ("core/agent-redline/core/reporter/reporter.py", "agent-redline/scripts/agent-redline-report.py"),
    ("core/agent-redline/core/skill/agent-redline.md", "agent-redline/SKILL.md"),
    ("core/agent-redline/core/skill/", "agent-redline/"),
    ("core/agent-redline/core/templates/skills/", "agent-redline/references/per-checkpoint/"),
    ("core/agent-redline/core/templates/", "agent-redline/assets/templates/"),
    ("core/agent-redline/core/schema/", "agent-redline/assets/schema/"),
    ("core/agent-redline/extensions/", "agent-redline/extensions/"),
    ("core/agent-redline/", "agent-redline/"),
    ("core/templates/.github/", "templates/.github/"),
    ("core/templates/checkpoints/", "templates/checkpoints/"),
    ("core/templates/", "templates/"),
    # Skill-source references from checkpoint files use ../../skill/...
    # in source (where checkpoint files live at core/templates/checkpoints/
    # and skill files at core/skill/). In dist the layout flattens —
    # checkpoint files at <pkg-root>/templates/checkpoints/ and skill
    # files at <pkg-root>/ — so the up-up-skill segment becomes up-up.
    ("../../skill/", "../../"),
    ("core/schema/", "assets/schema/"),
    # Install-root-relative paths that mirror the dev tree's agent-redline
    # subdirectory structure (e.g. <install-root>/agent-redline/core/reporter/...).
    # These appear in the source when bootstrap-mode tells the agent to
    # copy a file out of the installed skill; the install-root in our
    # dist points at the package root, not the dev-tree shape.
    ("agent-redline/core/reporter/reporter.py", "agent-redline/scripts/agent-redline-report.py"),
    ("agent-redline/core/skill/agent-redline.md", "agent-redline/SKILL.md"),
    ("agent-redline/core/skill/", "agent-redline/"),
    ("agent-redline/core/templates/skills/", "agent-redline/references/per-checkpoint/"),
    ("agent-redline/core/templates/", "agent-redline/assets/templates/"),
    ("agent-redline/core/schema/", "agent-redline/assets/schema/"),
    # The .bundled fallback exists for cases where build-vendored-checker.sh
    # can't run; the packager always pre-builds, so just point at the
    # final filename.
    ("<install-root>/scripts/agent-workflow-check.py.bundled",
     "<install-root>/scripts/agent-workflow-check.py"),
]
for old, new in substitutions:
    text = text.replace(old, new)
dst.write_text(text, encoding="utf-8", newline="\n")
PYEOF
}

substitute_redline_paths() {
  local src="$1" dst="$2"
  python3 - "$src" "$dst" <<'PYEOF'
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
text = src.read_text(encoding="utf-8")

# Same substitutions redline's own package-skill.sh applies.
substitutions = [
    ("core/templates/skills/", "references/per-checkpoint/"),
    ("core/templates/", "assets/templates/"),
    ("core/schema/", "assets/schema/"),
    ("core/reporter/reporter.py", "scripts/agent-redline-report.py"),
    ("core/reporter/", "scripts/"),
]
for old, new in substitutions:
    text = text.replace(old, new)
dst.write_text(text, encoding="utf-8", newline="\n")
PYEOF
}

substitute_extension_paths() {
  # Redline extension markdown uses ../../docs/X.md to point at the
  # upstream redline project docs. Inside our dist those docs do not
  # exist (we don't ship them). Rewrite to absolute upstream-repo URLs
  # so the consumer's installed skill has working links — same pattern
  # redline's own packager applies.
  local src="$1" dst="$2"
  python3 - "$src" "$dst" <<'PYEOF'
import re
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
text = src.read_text(encoding="utf-8")

base = "https://github.com/rore/agent-redline/blob/main/"

# [text](../../docs/FILE.md) → [text](<base>docs/FILE.md)
# [text](../../README.md)    → [text](<base>README.md)
text = re.sub(
    r"\]\(\.\./\.\./([^)]+)\)",
    lambda m: f"]({base}{m.group(1)})",
    text,
)

dst.write_text(text, encoding="utf-8", newline="\n")
PYEOF
}

# ---------------------------------------------------------------------
# 1. Workflow-side skill entry + modes + checkpoint references.
# ---------------------------------------------------------------------

substitute_workflow_paths "$REPO_ROOT/core/skill/agent-workflow.md"   "$TARGET/SKILL.md"
substitute_workflow_paths "$REPO_ROOT/core/skill/operating-mode.md"   "$TARGET/operating-mode.md"
substitute_workflow_paths "$REPO_ROOT/core/skill/bootstrap-mode.md"   "$TARGET/bootstrap-mode.md"

for f in "$REPO_ROOT"/core/templates/checkpoints/*.md; do
  substitute_workflow_paths "$f" "$TARGET/templates/checkpoints/$(basename "$f")"
done

# ---------------------------------------------------------------------
# 2. Workflow-side templates the skill copies/reads during bootstrap.
# ---------------------------------------------------------------------

cp "$REPO_ROOT/core/templates/agents-section.md.template"    "$TARGET/templates/"
cp "$REPO_ROOT/core/templates/work-record-routine.md"        "$TARGET/templates/"
cp "$REPO_ROOT/core/templates/work-record-expanded.md"       "$TARGET/templates/"
cp "$REPO_ROOT/core/templates/bootstrap-summary.md.template" "$TARGET/templates/"
cp "$REPO_ROOT/core/templates/skill-feedback.md"             "$TARGET/templates/"
cp "$REPO_ROOT/core/templates/agent-workflow.yaml.template"  "$TARGET/templates/"
cp "$REPO_ROOT/core/templates/.github/workflows/agent-workflow.yml.template" \
   "$TARGET/templates/.github/workflows/"

# ---------------------------------------------------------------------
# 3. Workflow-side schema.
# ---------------------------------------------------------------------

cp "$REPO_ROOT/core/schema/agent-workflow.schema.json" "$TARGET/assets/schema/"

# ---------------------------------------------------------------------
# 4. Workflow-side scripts. The CI checker is rebuilt from source via
#    build-vendored-checker.sh so consumers can install without running
#    any build step in their own repo.
# ---------------------------------------------------------------------

cp "$REPO_ROOT/scripts/format-verdict-comment.py" "$TARGET/scripts/"
cp "$REPO_ROOT/scripts/agent-workflow-tune.py"    "$TARGET/scripts/"

# Claude Code hooks (verbatim — shell + python, no path substitution).
cp "$REPO_ROOT/core/skill/hooks/"* "$TARGET/hooks/"
chmod +x "$TARGET/hooks/"*.sh 2>/dev/null || true

bash "$REPO_ROOT/scripts/build-vendored-checker.sh" "$TARGET/scripts/agent-workflow-check.py"
chmod +x "$TARGET/scripts/agent-workflow-check.py" 2>/dev/null || true

# ---------------------------------------------------------------------
# 5. agent-redline subtree — self-contained, mirrors redline's promoted
#    dist layout. Skill markdown uses redline's `core/...` substitutions
#    so consumers see the same package shape they would from upstream
#    redline.
# ---------------------------------------------------------------------

# 5a. Redline skill entry + modes.
substitute_redline_paths "$REPO_ROOT/core/agent-redline/core/skill/agent-redline.md" \
                         "$TARGET/agent-redline/SKILL.md"
substitute_redline_paths "$REPO_ROOT/core/agent-redline/core/skill/operating-mode.md" \
                         "$TARGET/agent-redline/operating-mode.md"
substitute_redline_paths "$REPO_ROOT/core/agent-redline/core/skill/bootstrap-mode.md" \
                         "$TARGET/agent-redline/bootstrap-mode.md"

# 5b. Per-checkpoint reference docs.
for f in "$REPO_ROOT"/core/agent-redline/core/templates/skills/*.md; do
  substitute_redline_paths "$f" "$TARGET/agent-redline/references/per-checkpoint/$(basename "$f")"
done

# 5c. Stack-neutral templates.
cp "$REPO_ROOT/core/agent-redline/core/templates/agent-policy.yaml.template" "$TARGET/agent-redline/assets/templates/"
cp "$REPO_ROOT/core/agent-redline/core/templates/AGENTS.md.template"        "$TARGET/agent-redline/assets/templates/"
cp "$REPO_ROOT/core/agent-redline/core/templates/pr-template.md"            "$TARGET/agent-redline/assets/templates/"
cp "$REPO_ROOT/core/agent-redline/core/templates/pre-push-check.sh"         "$TARGET/agent-redline/assets/templates/"
cp "$REPO_ROOT/core/agent-redline/core/templates/suppressions.yaml"         "$TARGET/agent-redline/assets/templates/"
chmod +x "$TARGET/agent-redline/assets/templates/pre-push-check.sh" 2>/dev/null || true

# 5d. Schemas.
cp "$REPO_ROOT/core/agent-redline/core/schema/agent-policy.schema.json"        "$TARGET/agent-redline/assets/schema/"
cp "$REPO_ROOT/core/agent-redline/core/schema/boundary-violations.schema.json" "$TARGET/agent-redline/assets/schema/"
cp "$REPO_ROOT/core/agent-redline/core/schema/suppressions.schema.json"        "$TARGET/agent-redline/assets/schema/"

# 5e. Reporter — vendored as user-facing scripts/agent-redline-report.py.
cp "$REPO_ROOT/core/agent-redline/core/reporter/reporter.py" \
   "$TARGET/agent-redline/scripts/agent-redline-report.py"
chmod +x "$TARGET/agent-redline/scripts/agent-redline-report.py" 2>/dev/null || true

# 5f. Extensions — self-contained folders with markdown, adapter.yaml,
#     suppressions.yaml, optional scripts/. Excludes test fixtures.
#     Markdown files get extension-path substitution (../../docs/X.md
#     → absolute upstream URL) so they resolve inside the package.
for ext_dir in "$REPO_ROOT"/core/agent-redline/extensions/*/; do
  ext_name=$(basename "$ext_dir")
  mkdir -p "$TARGET/agent-redline/extensions/$ext_name"
  for src_file in "$ext_dir"/*; do
    base=$(basename "$src_file")
    if [[ "$base" == _* ]]; then
      continue
    fi
    if [[ -d "$src_file" ]]; then
      cp -r "$src_file" "$TARGET/agent-redline/extensions/$ext_name/$base"
      # Strip nested test fixtures.
      find "$TARGET/agent-redline/extensions/$ext_name/$base" -type d -name '_test_fixture*' -prune -exec rm -rf {} + 2>/dev/null || true
      find "$TARGET/agent-redline/extensions/$ext_name/$base" -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
    elif [[ "$src_file" == *.md ]]; then
      substitute_extension_paths "$src_file" "$TARGET/agent-redline/extensions/$ext_name/$base"
    else
      cp "$src_file" "$TARGET/agent-redline/extensions/$ext_name/$base"
    fi
  done
done

echo "packaged agent-workflow skill at $TARGET"
echo "files: $(find "$TARGET" -type f | wc -l | tr -d ' ')"

# ---------------------------------------------------------------------
# 6. Manifest — a deterministic file list a consumer can verify the
#    install against (completeness). Written LAST, after every copy, and
#    EXCLUDES itself so recording its own size can't prevent convergence
#    through the `package` drift check. Format: <relpath>\t<bytes>,
#    LC_ALL=C sorted, LF newlines, no mtimes.
# ---------------------------------------------------------------------
(
  cd "$TARGET"
  find . -type f ! -path "./manifest.txt" \
    | sed 's|^\./||' \
    | LC_ALL=C sort \
    | while IFS= read -r f; do
        printf '%s\t%s\n' "$f" "$(wc -c < "$f" | tr -d ' ')"
      done
) > "$TARGET/manifest.txt"
echo "manifest: $(wc -l < "$TARGET/manifest.txt" | tr -d ' ') entries"

# When building the default dist (not a --dest invocation), also sync the
# local dogfood install so it stays in step with the committed dist.
# Claude Code reads from .claude/skills/agent-workflow/ — always synced.
# Codex reads from .agents/skills/agent-workflow/ — synced only when the
# .agents/skills/ parent already exists, so we don't create a Codex tree
# on machines that never installed Codex.
if [[ "$EXPLICIT_DEST" -eq 0 ]]; then
  LOCAL="$REPO_ROOT/.claude/skills/agent-workflow"
  bash "$0" --dest "$LOCAL"
  echo "synced local install at $LOCAL"

  CODEX_PARENT="$REPO_ROOT/.agents/skills"
  if [[ -d "$CODEX_PARENT" ]]; then
    CODEX_LOCAL="$CODEX_PARENT/agent-workflow"
    bash "$0" --dest "$CODEX_LOCAL"
    echo "synced codex install at $CODEX_LOCAL"
  fi
fi
