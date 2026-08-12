"""Unit tests for ``core/checker/redline_verdict.py``.

Loads the goldens redline ships under
``core/agent-redline/tests/reporter/*/expected-verdict.json`` and
asserts the parser's classification matches what
``core/templates/checkpoints/assess-risk.md`` documents. Keeping the
real reporter goldens as the input means the test would catch a
verdict-shape change upstream without needing to re-author hand-rolled
fixtures.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from core.checker.redline_verdict import (
    RedlineVerdict,
    RedlineVerdictError,
    load_redline_verdict,
    risk_at_least,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REDLINE_GOLDENS = REPO_ROOT / "core" / "agent-redline" / "tests" / "reporter"


# Goldens → expected detected_risk(). The expected values mirror the
# translation table in ``assess-risk.md``:
# - blue-only / zones empty → Routine
# - any gray zone → Elevated
# - any red zone + a *_changed disambiguator OR a High checkpoint → High
# - any red zone otherwise → Elevated
_RISK_EXPECTATIONS: dict[str, str] = {
    "blue-only": "Routine",
    "gray-only": "Elevated",
    # red-zone changes with only architecture-review checkpoints stay
    # Elevated (architecture-review is not in the High checkpoint list).
    "red-changed-with-checkpoint": "Elevated",
    "red-changed-no-checkpoint": "Elevated",
    "mixed": "Elevated",
    # schema-changed triggers schemaChanges.detected → High.
    "schema-changed": "High",
    # api-changed triggers apiChanges.detected → High.
    "api-changed": "High",
    "api-changed-controllers": "High",
    # runtime-config-changed triggers runtimeConfigChanges.detected
    # plus an ops-review checkpoint — operational surface, Elevated.
    "runtime-config-changed": "Elevated",
    # Boundary violations don't affect detected_risk() (that's the
    # boundary predicate's job). The underlying zones determine risk —
    # this fixture is gray-only.
    "boundary-violation": "Elevated",
}


def _golden_dirs() -> list[Path]:
    """Every reporter-golden subdir with an expected-verdict.json file."""
    if not REDLINE_GOLDENS.exists():
        return []
    return sorted(
        p for p in REDLINE_GOLDENS.iterdir()
        if p.is_dir() and (p / "expected-verdict.json").exists()
    )


@pytest.mark.parametrize(
    "golden_dir",
    [p for p in _golden_dirs() if p.name in _RISK_EXPECTATIONS],
    ids=lambda p: p.name,
)
def test_detected_risk_matches_translation_table(golden_dir: Path) -> None:
    """Loading a real redline golden produces the expected detected_risk()."""
    verdict = load_redline_verdict(golden_dir / "expected-verdict.json")
    assert verdict is not None, f"{golden_dir.name}: load returned None"
    expected = _RISK_EXPECTATIONS[golden_dir.name]
    assert verdict.detected_risk() == expected, (
        f"{golden_dir.name}: expected detected_risk()={expected!r}, "
        f"got {verdict.detected_risk()!r}"
    )


def test_load_missing_file_returns_none(tmp_path: Path) -> None:
    """A missing verdict file yields ``None`` rather than raising.

    The checker uses this to distinguish "no verdict" from "broken
    verdict" — the former is a config decision (required vs optional),
    the latter is always a hard error.
    """
    assert load_redline_verdict(tmp_path / "no-such-file.json") is None


def test_load_invalid_json_raises(tmp_path: Path) -> None:
    """A verdict file with malformed JSON surfaces as a typed error."""
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(RedlineVerdictError):
        load_redline_verdict(bad)


def test_load_non_object_root_raises(tmp_path: Path) -> None:
    """A JSON file whose root is not an object is rejected explicitly."""
    arr = tmp_path / "array.json"
    arr.write_text("[]", encoding="utf-8")
    with pytest.raises(RedlineVerdictError):
        load_redline_verdict(arr)


def test_boundary_violation_property() -> None:
    """``has_boundary_violation`` reflects the parsed list non-emptiness."""
    empty = RedlineVerdict(
        boundary_violations=[],
        zones={"blue": [], "gray": [], "red": [], "watch": []},
        checkpoints=[],
        api_changed=False,
        schema_changed=False,
        security_changed=False,
        runtime_config_changed=False,
    )
    assert empty.has_boundary_violation is False

    nonempty = RedlineVerdict(
        boundary_violations=[{"rule": "r1", "detail": "d", "severity": "error"}],
        zones={"blue": [], "gray": [], "red": [], "watch": []},
        checkpoints=[],
        api_changed=False,
        schema_changed=False,
        security_changed=False,
        runtime_config_changed=False,
    )
    assert nonempty.has_boundary_violation is True


def test_high_checkpoint_lifts_red_to_high() -> None:
    """A red-zone change with a ``persistence-review`` checkpoint → High.

    Defensive cover for the case where redline raises a checkpoint id
    in the High set without setting any of the ``*_changed`` booleans
    (e.g. a custom policy that emits its own checkpoint ids).
    """
    v = RedlineVerdict(
        boundary_violations=[],
        zones={
            "blue": [],
            "gray": [],
            "red": ["src/main/java/com/example/orders/repository/OrderRepo.java"],
            "watch": [],
        },
        checkpoints=[
            {"id": "persistence-review", "reason": "x", "satisfied": False}
        ],
        api_changed=False,
        schema_changed=False,
        security_changed=False,
        runtime_config_changed=False,
    )
    assert v.detected_risk() == "High"


def test_red_without_disambiguator_stays_elevated() -> None:
    """Red-zone change without any High signal stays Elevated."""
    v = RedlineVerdict(
        boundary_violations=[],
        zones={
            "blue": [],
            "gray": [],
            "red": ["src/main/java/com/example/orders/domain/Order.java"],
            "watch": [],
        },
        checkpoints=[{"id": "architecture-review", "reason": "x", "satisfied": True}],
        api_changed=False,
        schema_changed=False,
        security_changed=False,
        runtime_config_changed=False,
    )
    assert v.detected_risk() == "Elevated"


@pytest.mark.parametrize(
    "declared,detected,expected",
    [
        ("Routine", "Routine", True),
        ("Elevated", "Routine", True),
        ("High", "Routine", True),
        ("Elevated", "Elevated", True),
        ("High", "Elevated", True),
        ("High", "High", True),
        ("Routine", "Elevated", False),
        ("Routine", "High", False),
        ("Elevated", "High", False),
        # Unknown values are False defensively.
        ("Bogus", "High", False),
        ("Elevated", "Bogus", False),
    ],
)
def test_risk_at_least(declared: str, detected: str, expected: bool) -> None:
    assert risk_at_least(declared, detected) is expected


def test_defensive_defaults_for_missing_keys(tmp_path: Path) -> None:
    """An almost-empty verdict object parses with safe defaults.

    The checker shouldn't crash if redline upstream slims down its
    output. Missing keys default to empty / False; downstream
    predicates see a clean Routine verdict.
    """
    minimal = tmp_path / "minimal.json"
    minimal.write_text("{}", encoding="utf-8")
    v = load_redline_verdict(minimal)
    assert v is not None
    assert v.boundary_violations == []
    assert v.zones == {"blue": [], "gray": [], "red": [], "watch": []}
    assert v.checkpoints == []
    assert v.api_changed is False
    assert v.schema_changed is False
    assert v.security_changed is False
    assert v.runtime_config_changed is False
    assert v.detected_risk() == "Routine"
