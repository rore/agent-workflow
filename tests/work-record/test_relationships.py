"""Shared Python conformance for optional Work Record Relationships."""

from __future__ import annotations

import json
from tempfile import TemporaryDirectory
from pathlib import Path, PurePosixPath

import pytest
import yaml

from core.checker.predicates import (
    CheckerContext,
    workrecord_relationships_valid,
)
from core.work_record import (
    decode_relationships,
    parse_record,
    render_record,
)
from core.work_record.local_backend import LocalBackend
from core.work_record.local_backend import InvalidTaskPathError, validate_task_path_template

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads(
    (ROOT / "tests/work-record/fixtures/relationships.json").read_text(encoding="utf-8")
)


def _fixture_record(raw: str | None) -> str:
    field = "" if raw is None else "**Relationships:**\n" + raw
    return FIXTURE["record_template"].replace("__RELATIONSHIPS__", field)


def _expanded_record(raw: str) -> str:
    text = (ROOT / "tests/fixtures/work-record/expanded-pass/work-record.md").read_text(
        encoding="utf-8"
    )
    return text.replace("**State:**", "**Relationships:**\n" + raw + "\n\n**State:**")


def test_shared_relationship_cases_match_status_and_reason() -> None:
    for case in FIXTURE["cases"]:
        result = decode_relationships(case["raw"])
        assert result["status"] == case["status"], case["name"]
        assert result.get("reason") == case.get("reason"), case["name"]


def test_relationships_round_trip_on_both_record_shapes() -> None:
    raw = FIXTURE["cases"][3]["raw"]
    for text in (_fixture_record(raw), _expanded_record(raw)):
        parsed = parse_record(text)
        assert parsed.record["relationships"] == raw
        rendered = render_record(parsed)
        assert parse_record(rendered).record["relationships"] == raw


def test_surrounding_hints_are_ignored_but_comment_like_json_bytes_survive() -> None:
    case = next(case for case in FIXTURE["cases"] if case["name"] == "unicode-and-comment-like-refs")
    parsed = parse_record(_fixture_record(case["raw"]))
    assert "<!-- untouched -->" in parsed.record["relationships"]

    hinted = next(case for case in FIXTURE["cases"] if case["name"] == "surrounding-template-hints")
    record = parse_record(_fixture_record(hinted["raw"]))
    assert record.record["relationships"].startswith("{")
    assert decode_relationships(record.record["relationships"])["status"] == "declared"

    combined = "<!-- outer -->\n" + case["raw"] + "\n<!-- outer -->"
    combined_record = parse_record(_fixture_record(combined))
    assert "<!-- untouched -->" in combined_record.record["relationships"]
    assert decode_relationships(combined_record.record["relationships"])["status"] == "declared"


def test_relationship_json_bounds_and_deep_parser_errors_are_explicit() -> None:
    oversized = '{"schema_version":1,"sources":[{"provider":"p","scope_ref":"' + "x" * 65536 + '","local_ref":"l"}],"pull_requests":[]}'
    assert decode_relationships(oversized) == {
        "status": "invalid",
        "reason": "relationships_too_large",
    }
    deeply_nested = "[" * 5000 + "0" + "]" * 5000
    assert decode_relationships(deeply_nested) == {
        "status": "invalid",
        "reason": "invalid_json",
    }
    assert decode_relationships("\ud800")["status"] == "invalid"
    assert decode_relationships(
        '{"schema_version":1,"sources":[{"provider":"p","scope_ref":"\\ud800","local_ref":"l"}],"pull_requests":[]}'
    ) == {"status": "invalid", "reason": "invalid_relationships"}


def test_integral_json_number_version_matches_javascript_number_semantics() -> None:
    result = decode_relationships('{"schema_version":1.0,"sources":[],"pull_requests":[]}')
    assert result["status"] == "declared"


def test_pr_number_identity_does_not_require_integer_conversion() -> None:
    url = "https://github.com/rore/agent-workflow/pull/" + "9" * 5000
    raw = json.dumps({"schema_version": 1, "sources": [], "pull_requests": [url]})
    assert decode_relationships(raw)["relationships"]["pull_requests"] == [url]


def test_relationship_byte_limit_accepts_exact_boundary() -> None:
    def value(ref: str) -> str:
        return json.dumps({"schema_version": 1, "sources": [{"provider": "p", "scope_ref": "s", "local_ref": ref}], "pull_requests": []})

    length = 65536 - len(value("").encode("utf-8"))
    assert decode_relationships(value("x" * length))["status"] == "declared"
    assert decode_relationships(value("x" * (length + 1))) == {
        "status": "invalid", "reason": "relationships_too_large",
    }


def test_config_layout_profiles_use_current_pyyaml_and_path_validator() -> None:
    for case in FIXTURE["config_cases"]:
        if case["status"] != "ok" and case["name"] != "yaml11-bool-not-path":
            continue
        config = yaml.safe_load(case["text"])
        work_record = config.get("workRecord") if isinstance(config, dict) else None
        if case["status"] == "ok":
            assert config.get("version") == 1
            assert isinstance(work_record, dict) and work_record.get("backend") == "local"
            local = work_record.get("local")
            assert isinstance(local, dict) and isinstance(local.get("taskPath"), str)
            assert PurePosixPath(validate_task_path_template(local["taskPath"])).as_posix() == case["task_path"]
            if "record_path" in case:
                backend = LocalBackend(ROOT, local["taskPath"])
                assert backend.resolve_location("fixture") == case["record_path"]
        elif case["name"] == "yaml11-bool-not-path":
            assert isinstance(work_record["local"]["taskPath"], bool)
            with pytest.raises(InvalidTaskPathError):
                validate_task_path_template(work_record["local"]["taskPath"])


def test_local_backend_round_trips_raw_relationships_across_configured_layouts() -> None:
    samples = [
        next(case["raw"] for case in FIXTURE["cases"] if case["name"] == "known-none"),
        next(case["raw"] for case in FIXTURE["cases"] if case["name"] == "future-version"),
        None,
    ]
    layouts = [
        case["task_path"]
        for case in FIXTURE["config_cases"]
        if case["status"] == "ok"
    ]
    with TemporaryDirectory(prefix="relationships-test-", dir=ROOT) as temp_root:
        for index, layout in enumerate(layouts):
            backend = LocalBackend(Path(temp_root) / str(index), layout)
            for sample_index, raw in enumerate(samples):
                parsed = parse_record(_fixture_record(raw))
                slug = f"case-{sample_index}"
                backend.write(slug, parsed)
                returned = backend.read(slug)
                assert returned is not None
                assert returned.record["outcome"] == parsed.record["outcome"]
                assert returned.record.get("relationships") == parsed.record.get("relationships")


def test_invalid_utf8_fixture_vectors_are_rejected_before_record_parsing() -> None:
    for value in FIXTURE["invalid_utf8_hex"]:
        with pytest.raises(UnicodeDecodeError):
            bytes.fromhex(value).decode("utf-8", errors="strict")


def test_relationship_predicate_blocks_invalid_and_advises_unsupported() -> None:
    for case, blocking in (("malformed-json", True), ("future-version", False)):
        raw = next(item["raw"] for item in FIXTURE["cases"] if item["name"] == case)
        parsed = parse_record(_fixture_record(raw))
        ctx = CheckerContext(
            backend=LocalBackend(ROOT, ".agent-workflow/tasks/{slug}.md"),
            slug="fixture",
            record=parsed.record,
            shape=parsed.shape,
            parse_error=None,
            raw_text=None,
            redline_verdict=None,
            redline_required=False,
            redline_verdict_parse_error=None,
        )
        result = workrecord_relationships_valid(ctx)
        assert result.passed is (not blocking)
        assert result.blocking is blocking


def test_existing_integrity_json_comment_stripping_is_unchanged() -> None:
    text = _fixture_record(None).replace(
        "**State:** Ready to implement",
        '**Requirement baseline:** {"source":"scope<!-- hint -->","outcome":"o","scope":"s","constraints":"c","completion_criteria":"cc"}\n**State:** Ready to implement',
    )
    parsed = parse_record(text)
    assert parsed.record["requirement_baseline"].source == "scope"
