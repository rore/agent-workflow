"""Unit tests for extensions/python/scripts/run-import-linter.py.

These cover the adapter's exit-code semantics with duck-typed fake Report
objects, so they run WITHOUT import-linter installed (the end-to-end
tests/extensions/python/check-extension.sh needs the real package; main()
imports import-linter internals before it ever builds a report, so the
exit-code logic is split into handle_report() to keep it testable here).

Regression guard for the config-error defect: invalid contract options are
a CONFIG error, not a broken contract. The adapter used to emit them as
error-severity `violations` entries and return 1 — which made the
downstream redline reporter headline a false BOUNDARY_VIOLATION. It must
now return 2 (script error) and write an EMPTY violations report.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest  # type: ignore

# core/agent-redline (the redline root): tests/extensions/python/<file>.
REDLINE_ROOT = Path(__file__).resolve().parents[3]

_spec = importlib.util.spec_from_file_location(
    "run_import_linter",
    REDLINE_ROOT / "extensions" / "python" / "scripts" / "run-import-linter.py",
)
adapter = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(adapter)

# WARNING: do NOT call adapter.main() from this file. main() runs
# _import_internals() first, which calls sys.exit(2) when import-linter is
# not installed — that would crash the whole test session at import time.
# Exercise handle_report() / _config_error_messages() directly instead;
# those were split out of main() precisely so the exit-code logic is
# testable without the import-linter dependency.


class _FakeExc:
    def __init__(self, errors: dict):
        self.errors = errors


class _FakeCheck:
    def __init__(self, kept: bool, metadata: dict):
        self.kept = kept
        self.metadata = metadata


class _FakeContract:
    def __init__(self, name: str):
        self.name = name


class _FakeReport:
    def __init__(self, *, could_not_run=False, invalid_contract_options=None,
                 contracts_and_checks=None):
        self.could_not_run = could_not_run
        self.invalid_contract_options = invalid_contract_options or {}
        self._cc = contracts_and_checks or []

    def get_contracts_and_checks(self):
        return self._cc


def _load(out: Path) -> dict:
    return json.loads(out.read_text(encoding="utf-8"))


def test_config_error_returns_exit_2_and_empty_report(tmp_path):
    report = _FakeReport(
        could_not_run=True,
        invalid_contract_options={
            "my-layers-contract": _FakeExc({"containers": "must be a list"}),
        },
    )
    out = tmp_path / "report.json"
    rc = adapter.handle_report(report, out)
    # Documented exit code 2 = script error (config errors belong here),
    # NOT 1 (a broken contract).
    assert rc == 2
    # Empty violations → the reporter cannot headline a false
    # BOUNDARY_VIOLATION from a config error.
    assert _load(out)["violations"] == []


def test_config_error_messages_format():
    report = _FakeReport(
        could_not_run=True,
        invalid_contract_options={
            "my-contract": _FakeExc({"containers": "must be a list"}),
        },
    )
    messages = adapter._config_error_messages(report)
    assert messages == [
        "my-contract: invalid contract option containers: must be a list",
    ]


def test_broken_contract_returns_exit_1(tmp_path):
    report = _FakeReport(contracts_and_checks=[
        (
            _FakeContract("no-domain-to-infra"),
            _FakeCheck(False, {"invalid_dependencies": [
                {"importer": "domain", "imported": "infra", "routes": []},
            ]}),
        ),
    ])
    out = tmp_path / "report.json"
    rc = adapter.handle_report(report, out)
    assert rc == 1
    violations = _load(out)["violations"]
    assert len(violations) == 1
    assert violations[0]["rule"] == "no-domain-to-infra"
    assert violations[0]["severity"] == "error"


def test_clean_report_returns_exit_0(tmp_path):
    report = _FakeReport(contracts_and_checks=[
        (_FakeContract("kept-contract"), _FakeCheck(True, {})),
    ])
    out = tmp_path / "report.json"
    rc = adapter.handle_report(report, out)
    assert rc == 0
    assert _load(out)["violations"] == []
