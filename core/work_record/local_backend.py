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

from pathlib import Path, PurePosixPath, PureWindowsPath
import unicodedata

from .parser import (
    ParsedRecord,
    WorkRecordParseError,
    find_block_span,
    parse_record,
    render_record,
)

_PLACEHOLDER = "{slug}"
_MAX_SLUG_BYTES = 255
_MAX_PATH_BYTES = 4096
_WINDOWS_INVALID = frozenset('<>:"|?*')
_WINDOWS_DEVICES = frozenset(
    {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    | {f"COM{number}" for number in range(1, 10)}
    | {f"LPT{number}" for number in range(1, 10)}
)


class InvalidSlugError(ValueError):
    """The supplied Work Record slug is unsafe or outside the contract."""


class InvalidTaskPathError(ValueError):
    """The configured local taskPath is invalid."""


class UnsafeWorkRecordPathError(ValueError):
    """A resolved Work Record path escapes the selected checkout."""


def validate_slug(slug: str) -> str:
    """Return *slug* when it is safe as one filename component."""
    try:
        encoded = slug.encode("utf-8")
    except (AttributeError, UnicodeEncodeError) as exc:
        raise InvalidSlugError("slug must be valid UTF-8 text") from exc
    if not encoded or len(encoded) > _MAX_SLUG_BYTES:
        raise InvalidSlugError("slug must contain 1 to 255 UTF-8 bytes")
    if any(ch.isspace() or unicodedata.category(ch) == "Cc" for ch in slug):
        raise InvalidSlugError("slug must not contain whitespace or control characters")
    if any(ch in _WINDOWS_INVALID or ch in "/\\" for ch in slug):
        raise InvalidSlugError("slug contains a path separator or invalid filename character")
    if slug.startswith(".") or slug.endswith((".", " ")) or slug in {".", ".."}:
        raise InvalidSlugError("slug has an unsafe leading or trailing character")
    if slug.split(".", 1)[0].upper() in _WINDOWS_DEVICES:
        raise InvalidSlugError("slug uses a reserved Windows device basename")
    return slug


def validate_task_path_template(template: str) -> str:
    """Validate and slash-normalize a repository-relative taskPath."""
    try:
        encoded = template.encode("utf-8")
    except (AttributeError, UnicodeEncodeError) as exc:
        raise InvalidTaskPathError("taskPath must be valid UTF-8 text") from exc
    if not encoded or len(encoded) > _MAX_PATH_BYTES:
        raise InvalidTaskPathError("taskPath must contain 1 to 4096 UTF-8 bytes")
    if any(unicodedata.category(ch) == "Cc" for ch in template):
        raise InvalidTaskPathError("taskPath must not contain control characters")
    if template.count(_PLACEHOLDER) != 1:
        raise InvalidTaskPathError("taskPath must contain exactly one '{slug}' placeholder")

    normalized = template.replace("\\", "/")
    windows_path = PureWindowsPath(template)
    if (
        PurePosixPath(normalized).is_absolute()
        or windows_path.is_absolute()
        or windows_path.drive
    ):
        raise InvalidTaskPathError("taskPath must be repository-relative")
    if any(part in {".", ".."} for part in normalized.split("/")):
        raise InvalidTaskPathError("taskPath must not contain '.' or '..' components")
    return normalized


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
        self._repo_root = Path(repo_root).resolve()
        self._template = validate_task_path_template(task_path_template)

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
        return self._resolve_path(slug).relative_to(self._repo_root).as_posix()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _resolve_path(self, slug: str) -> Path:
        relative = self._template.replace(_PLACEHOLDER, validate_slug(slug))
        if len(relative.encode("utf-8")) > _MAX_PATH_BYTES:
            raise UnsafeWorkRecordPathError("resolved taskPath exceeds 4096 UTF-8 bytes")
        try:
            path = (self._repo_root / relative).resolve()
        except (OSError, ValueError) as exc:
            raise UnsafeWorkRecordPathError(
                "could not safely resolve Work Record path"
            ) from exc
        try:
            repo_relative = path.relative_to(self._repo_root)
        except ValueError as exc:
            raise UnsafeWorkRecordPathError(
                "resolved Work Record path escapes the selected checkout"
            ) from exc
        if len(repo_relative.as_posix().encode("utf-8")) > _MAX_PATH_BYTES:
            raise UnsafeWorkRecordPathError("resolved record path exceeds 4096 UTF-8 bytes")
        return path
