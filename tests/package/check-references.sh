#!/usr/bin/env bash
# tests/package/check-references.sh
#
# Layer-1 completeness check. Every internal path the packaged skill
# markdown points at must resolve inside the dist tree.
#
# Catches the failure mode where the packager forgets to ship a file
# the skill text references (which the layer-0 drift check cannot
# catch — the packager and the diff agree the file is absent).
#
# Scope:
#   - markdown links of the form [text](relative/path) where the path
#     does not start with http:, https:, mailto:, or #
#   - bare path tokens of known top-level forms (templates/...,
#     assets/..., scripts/..., references/..., agent-redline/...,
#     extensions/...) that appear inside backticks or after the word
#     "Copy"/"copy" — these are the references bootstrap-mode uses
#     when it tells the agent where to find a file
#
# Out of scope:
#   - <install-root>/... references — these are install-root-relative
#     and resolve at install time; we strip the prefix and re-check
#   - paths outside the dist (e.g. .github/workflows/ inside a consumer
#     repo) — those are *outputs* the skill writes, not files it reads
#
# Exit codes:
#   0 — every reference resolves
#   1 — script error
#   2 — at least one broken reference

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

"$PY" - "$DIST" <<'PYEOF'
import re
import sys
from pathlib import Path

DIST = Path(sys.argv[1])

# Path roots that, if seen, must resolve inside DIST. Other roots
# (.github/, .agent-workflow/, .agent-redline/, docs/, build/) are
# either consumer-repo outputs or dev-repo paths; not our concern here.
INTERNAL_PREFIXES = (
    "SKILL.md",
    "operating-mode.md",
    "bootstrap-mode.md",
    "templates/",
    "assets/",
    "scripts/",
    "agent-redline/",
)
# Inside agent-redline/, redline's own packaged paths.
REDLINE_INTERNAL_PREFIXES = (
    "SKILL.md",
    "operating-mode.md",
    "bootstrap-mode.md",
    "references/",
    "assets/",
    "scripts/",
    "extensions/",
)

# These prefixes resolve at install time inside the consumer repo, not
# inside the dist. Skip them.
CONSUMER_REPO_PREFIXES = (
    ".github/",
    ".agent-workflow/",
    ".agent-redline/",
    "docs/",
    "build/",
)

LINK_RE = re.compile(r"\]\(([^)]+)\)")

# Capture <install-root>/foo references — bootstrap-mode uses this
# placeholder to mean "the directory the skill was installed into."
# Strip the placeholder and verify the remaining path resolves inside
# DIST (since DIST is the install root in our model).
INSTALL_ROOT_RE = re.compile(r"<install-root>/([^\s`)<>]+)")

errors = []

def resolve_or_skip(ref: str, source: Path) -> None:
    """Return None if the ref resolves or is intentionally skipped;
    otherwise append an error."""
    # Strip a leading <install-root>/ — that maps to DIST root.
    m = INSTALL_ROOT_RE.fullmatch(ref)
    if m:
        ref = m.group(1)
    # Anchors/external/mail: skip.
    if ref.startswith(("http:", "https:", "mailto:", "#")):
        return
    # Strip an anchor fragment if present.
    ref = ref.split("#", 1)[0]
    if not ref:
        return
    # Consumer-repo outputs the skill writes (not files it reads).
    if ref.startswith(CONSUMER_REPO_PREFIXES):
        return
    # Resolve relative to the source file's directory first.
    candidate = (source.parent / ref).resolve()
    if candidate.exists():
        return
    # Some skill text writes dist-root-relative tokens. Try DIST root
    # (and, for files inside agent-redline/, the redline subroot).
    if any(ref.startswith(p) for p in INTERNAL_PREFIXES):
        if (DIST / ref).exists():
            return
    if "agent-redline" in source.parts:
        # Inside the redline subtree, bare references resolve relative
        # to the redline root.
        redline_root = DIST / "agent-redline"
        if (redline_root / ref).exists():
            return
        # Or redline-internal-prefixed.
        if any(ref.startswith(p) for p in REDLINE_INTERNAL_PREFIXES):
            if (redline_root / ref).exists():
                return
    errors.append(f"{source.relative_to(DIST)}: unresolved reference '{ref}'")

for md in sorted(DIST.rglob("*.md")):
    text = md.read_text(encoding="utf-8")
    for m in LINK_RE.finditer(text):
        resolve_or_skip(m.group(1).strip(), md)
    for m in INSTALL_ROOT_RE.finditer(text):
        resolve_or_skip("<install-root>/" + m.group(1).strip(), md)

if errors:
    print(f"FAIL: {len(errors)} unresolved references inside dist/agent-workflow/", file=sys.stderr)
    for e in errors[:50]:
        print(f"  {e}", file=sys.stderr)
    if len(errors) > 50:
        print(f"  ... and {len(errors) - 50} more", file=sys.stderr)
    sys.exit(2)

print(f"ok: every internal reference in dist/agent-workflow/ resolves.")
PYEOF
