"""Tests for the local Work Record backend.

Each completion criterion from the original Step 3 Work Record is
exercised plus the slice-A contract change: backends read and write
:class:`ParsedRecord` (carrying shape + record), not raw
``WorkRecord``. Both shapes round-trip through the same backend
methods; the parser's dispatcher picks the shape.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from core.work_record import (
    ExpandedWorkRecord,
    LocalBackend,
    ParsedRecord,
    WorkRecord,
    WorkRecordBackend,
    WorkRecordParseError,
    parse_record,
)

ROUTINE_TEMPLATE = ".agent-workflow/tasks/{slug}.md"


def _sample_routine() -> ParsedRecord:
    return ParsedRecord(
        shape="routine",
        record=WorkRecord(
            outcome="Concurrent retries produce a single wallet.",
            target="wallet-service.",
            scope="Retry path; existing regression test suite.",
            constraints="Public API unchanged.",
            completion_criteria="A regression test asserts single-wallet behaviour.",
            risk="Routine",
            complexity="Simple",
            reason="Localised, reversible.",
            approach="Reuse the existing retry utility plus an idempotency check.",
            verification="New regression test plus wallet-service CI.",
            state="Ready to implement",
        ),
    )


def _sample_expanded() -> ParsedRecord:
    return ParsedRecord(
        shape="expanded",
        record=ExpandedWorkRecord(
            outcome="Tenant-scoped wallet idempotency across restarts.",
            target="wallet-service.",
            scope="Wallet creation flow + idempotency table.",
            constraints="Tenant isolation MUST remain intact.",
            completion_criteria="Concurrent retries produce a single wallet per tenant.",
            risk="Elevated",
            complexity="Moderate",
            reason="Persistence + multi-tenancy are Elevated triggers per DEFAULT_PROFILE §3.",
            discovery="No tenant-scoped key today; retry utility is in-memory only.",
            material_assumptions=(
                "Request identifier is stable across retries — disproved by ingress "
                "log inspection; action if disproved: return to planning."
            ),
            plan="Add wallet_requests table keyed on (tenant_id, request_identifier).",
            verification_plan="Concurrent retries → WalletConcurrentRetryTest; restart → WalletRestartIdempotencyTest.",
            plan_review="Clean-context agent review (Elevated path).",
            approvals="Not required at Elevated risk level.",
            state="Ready to implement",
        ),
    )


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


def test_local_backend_satisfies_protocol(tmp_path: Path) -> None:
    backend = LocalBackend(tmp_path, ROUTINE_TEMPLATE)
    assert isinstance(backend, WorkRecordBackend)


# ---------------------------------------------------------------------------
# Construction validation
# ---------------------------------------------------------------------------


def test_template_must_contain_slug_placeholder(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=r"\{slug\}"):
        LocalBackend(tmp_path, ".agent-workflow/tasks/static.md")


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------


def test_read_missing_file_returns_none(tmp_path: Path) -> None:
    backend = LocalBackend(tmp_path, ROUTINE_TEMPLATE)
    assert backend.read("anything") is None


def test_read_returns_routine_parsed_record(tmp_path: Path) -> None:
    backend = LocalBackend(tmp_path, ROUTINE_TEMPLATE)
    backend.write("task-1", _sample_routine())

    parsed = backend.read("task-1")
    assert parsed is not None
    assert parsed.shape == "routine"
    assert parsed == _sample_routine()


def test_read_returns_expanded_parsed_record(tmp_path: Path) -> None:
    backend = LocalBackend(tmp_path, ROUTINE_TEMPLATE)
    backend.write("task-2", _sample_expanded())

    parsed = backend.read("task-2")
    assert parsed is not None
    assert parsed.shape == "expanded"
    assert parsed == _sample_expanded()


def test_read_propagates_parse_errors(tmp_path: Path) -> None:
    """Malformed Work Records are surfaced, not silently treated as missing."""
    backend = LocalBackend(tmp_path, ROUTINE_TEMPLATE)
    path = tmp_path / ".agent-workflow" / "tasks" / "broken.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "<!-- agent-workflow:start -->\n**Outcome:** only field\n<!-- agent-workflow:end -->\n",
        encoding="utf-8",
    )
    with pytest.raises(WorkRecordParseError):
        backend.read("broken")


# ---------------------------------------------------------------------------
# Write — first time
# ---------------------------------------------------------------------------


def test_write_creates_file_and_parent_dirs(tmp_path: Path) -> None:
    backend = LocalBackend(tmp_path, ROUTINE_TEMPLATE)
    backend.write("task-1", _sample_routine())

    path = tmp_path / ".agent-workflow" / "tasks" / "task-1.md"
    assert path.exists()
    assert "<!-- agent-workflow:start -->" in path.read_text(encoding="utf-8")


def test_write_round_trips_through_parser_routine(tmp_path: Path) -> None:
    """parse_record(read()) returns what was written for routine shape."""
    backend = LocalBackend(tmp_path, ROUTINE_TEMPLATE)
    backend.write("task-1", _sample_routine())

    raw = (tmp_path / ".agent-workflow" / "tasks" / "task-1.md").read_text(encoding="utf-8")
    assert parse_record(raw) == _sample_routine()


def test_write_round_trips_through_parser_expanded(tmp_path: Path) -> None:
    """parse_record(read()) returns what was written for expanded shape."""
    backend = LocalBackend(tmp_path, ROUTINE_TEMPLATE)
    backend.write("task-2", _sample_expanded())

    raw = (tmp_path / ".agent-workflow" / "tasks" / "task-2.md").read_text(encoding="utf-8")
    assert parse_record(raw) == _sample_expanded()


# ---------------------------------------------------------------------------
# Write — update preserves surrounding prose
# ---------------------------------------------------------------------------


def test_write_preserves_prefix_and_suffix_prose(tmp_path: Path) -> None:
    """Updating an existing file replaces only the marker block.

    Notes above and below the block are part of the human task page
    (see .agent-workflow/tasks/README.md). They must not be clobbered
    on every backend write.
    """
    backend = LocalBackend(tmp_path, ROUTINE_TEMPLATE)
    path = tmp_path / ".agent-workflow" / "tasks" / "task-1.md"
    path.parent.mkdir(parents=True)

    initial = (
        "# Task page\n\n"
        "Some human-written notes above the marker block.\n\n"
        "<!-- agent-workflow:start -->\n"
        "**Outcome:** initial outcome\n"
        "**Target:** t\n"
        "**Scope:** s\n"
        "**Constraints:** c\n"
        "**Completion criteria:** cc\n"
        "**Risk:** Routine\n"
        "**Complexity:** Simple\n"
        "**Reason:** —\n"
        "**Approach:** a\n"
        "**Verification:** v\n"
        "**State:** Ready to implement\n"
        "<!-- agent-workflow:end -->\n\n"
        "Trailing notes below the block.\n"
    )
    path.write_text(initial, encoding="utf-8")

    updated = _sample_routine()
    backend.write("task-1", updated)

    final = path.read_text(encoding="utf-8")
    assert final.startswith("# Task page")
    assert "Some human-written notes above the marker block." in final
    assert "Trailing notes below the block." in final
    # The updated marker block reflects the new record.
    assert parse_record(final) == updated
    # No duplicated marker blocks.
    assert final.count("<!-- agent-workflow:start -->") == 1
    assert final.count("<!-- agent-workflow:end -->") == 1


def test_write_refuses_to_append_when_existing_file_has_no_markers(tmp_path: Path) -> None:
    """A file at the slug path without a marker block is malformed, not append-able.

    Without this guard, the backend would silently turn a stray
    note-file into a half-task-half-notes hybrid.
    """
    backend = LocalBackend(tmp_path, ROUTINE_TEMPLATE)
    path = tmp_path / ".agent-workflow" / "tasks" / "task-1.md"
    path.parent.mkdir(parents=True)
    path.write_text("Just human notes, no Work Record block.\n", encoding="utf-8")

    with pytest.raises(WorkRecordParseError, match="no Work Record marker"):
        backend.write("task-1", _sample_routine())


# ---------------------------------------------------------------------------
# Multiple tasks coexist
# ---------------------------------------------------------------------------


def test_multiple_tasks_coexist_at_different_slugs(tmp_path: Path) -> None:
    backend = LocalBackend(tmp_path, ROUTINE_TEMPLATE)

    a = _sample_routine()
    b = _sample_expanded()

    backend.write("task-a", a)
    backend.write("task-b", b)

    assert backend.read("task-a") == a
    assert backend.read("task-b") == b
    # Files exist independently.
    assert (tmp_path / ".agent-workflow" / "tasks" / "task-a.md").exists()
    assert (tmp_path / ".agent-workflow" / "tasks" / "task-b.md").exists()


# ---------------------------------------------------------------------------
# Slug substitution
# ---------------------------------------------------------------------------


def test_resolve_location_reports_repo_relative_path(tmp_path: Path) -> None:
    backend = LocalBackend(tmp_path, ROUTINE_TEMPLATE)
    rel = backend.resolve_location("walking-skeleton-step-3")
    # Path separators differ by platform; check the structure either way.
    assert rel.replace("\\", "/") == ".agent-workflow/tasks/walking-skeleton-step-3.md"


def test_resolve_location_uses_custom_template(tmp_path: Path) -> None:
    backend = LocalBackend(tmp_path, "docs/tasks/{slug}.md")
    rel = backend.resolve_location("foo")
    assert rel.replace("\\", "/") == "docs/tasks/foo.md"
