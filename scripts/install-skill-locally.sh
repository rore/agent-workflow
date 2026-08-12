#!/usr/bin/env bash
# scripts/install-skill-locally.sh
#
# Install agent-workflow's skill into .claude/skills/ at the repo root
# so Claude Code activates it for this project. Run after checkout, and
# after edits to core/skill/* or core/templates/checkpoints/*.
#
# .claude/skills/ is gitignored — every developer regenerates locally.
# The target name matches the SKILL.md frontmatter `name:` field, which
# is what Claude Code uses for slash-command and discovery.
#
# Why this exists: we dogfood agent-workflow on agent-workflow itself.
# The local install lets the Claude Code session pick up the skill the
# same way a consuming repo would, including when we are editing the
# skill source.
#
# Two-step pipeline: this script delegates the file-copy logic to
# scripts/package-skill.sh, which also produces the committed
# dist/agent-workflow/ tree. One file list, one source of truth.
#
# Usage:
#   scripts/install-skill-locally.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$REPO_ROOT/.claude/skills/agent-workflow"

bash "$REPO_ROOT/scripts/package-skill.sh" --dest "$TARGET"

echo "installed agent-workflow skill at $TARGET"
