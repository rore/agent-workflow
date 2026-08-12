"""Local Markdown Work Record backend.

Reads and writes Work Records as marker-bounded blocks inside Markdown
files at a per-slug path. Path resolution uses simple ``{slug}``
substitution into the template configured at
``workRecord.local.taskPath`` in ``agent-workflow.yaml``.

On write, the backend preserves anything outside the marker block —
header notes, trailing prose, etc. — and replaces only the marker
region. If the file does not exist yet, it is created with the marker
block as its sole content.

Both record shapes (routine and expanded) flow through the same
:class:`ParsedRecord` carrier; the parser's dispatcher decides which
schema applies on read, and :func:`render_record` picks the right
renderer on write.
"""

from __future__ import annotations

from pathlib import Path

from .parser import (
    ParsedRecord,
    WorkRecordParseError,
    find_block_span,
    parse_record,
    render_record,
)

_PLACEHOLDER = "{slug}"


class LocalBackend:
    """File-backed Work Record backend.

    Parameters
    ----------
    repo_root:
        Absolute path to the repository root. All resolved paths are
        relative to this.
    task_path_template:
        Template from ``agent-workflow.yaml``'s
        ``workRecord.local.taskPath``. MUST contain ``{slug}``;
        otherwise every task would write to the same file.
    """

    def __init__(self, repo_root: Path, task_path_template: str) -> None:
        if _PLACEHOLDER not in task_path_template:
            raise ValueError(
                f"taskPath template {task_path_template!r} is missing the "
                f"{_PLACEHOLDER!r} placeholder — every task would collide "
                "on the same file"
            )
        self._repo_root = Path(repo_root).resolve()
        self._template = task_path_template

    # ------------------------------------------------------------------
    # WorkRecordBackend protocol
    # ------------------------------------------------------------------

    def read(self, slug: str) -> ParsedRecord | None:
        path = self._resolve_path(slug)
        if not path.exists():
            return None
        return parse_record(path.read_text(encoding="utf-8"))

    def write(self, slug: str, parsed: ParsedRecord) -> None:
        path = self._resolve_path(slug)
        new_block = render_record(parsed)

        if not path.exists():
            # First write — create parent dirs and dump the block.
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(new_block, encoding="utf-8")
            return

        existing = path.read_text(encoding="utf-8")
        span = find_block_span(existing)
        if span is None:
            # File exists but has no marker block. Treat that as a
            # malformed-but-present case rather than silently appending —
            # callers should clean up the file or pick a different slug.
            raise WorkRecordParseError(
                f"file {path} exists but contains no Work Record marker "
                "block; refusing to append a new one"
            )
        start, end = span

        # Splice: preserve the prefix up to the start marker and the
        # suffix from after the end marker; replace the marker region
        # with the freshly rendered block. find_block_span returns end
        # past the end marker, so we need to also strip its trailing
        # newline (if any) to avoid creating a double newline when we
        # join — render_record() already adds one.
        suffix = existing[end:]
        if suffix.startswith("\n"):
            suffix = suffix[1:]
        path.write_text(existing[:start] + new_block + suffix, encoding="utf-8")

    def resolve_location(self, slug: str) -> str:
        try:
            return str(self._resolve_path(slug).relative_to(self._repo_root))
        except ValueError:
            # Path is outside the repo root (only possible with absolute
            # taskPath templates). Fall back to the raw path.
            return str(self._resolve_path(slug))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _resolve_path(self, slug: str) -> Path:
        relative = self._template.replace(_PLACEHOLDER, slug)
        # Treat the template as repo-relative even when it starts with
        # '/' on Windows-style configs — bootstrap will normalise this,
        # but we accept either.
        relative = relative.lstrip("/\\")
        return (self._repo_root / relative).resolve()
