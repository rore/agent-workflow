"""End-to-end checks for evidence-calibrated bootstrap zone proposals."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from core.reporter.reporter import Diff, classify, render_markdown  # noqa: E402


def _check(policy: dict, files: list[str], expected: dict[str, list[str]]) -> None:
    verdict = classify(policy, Diff(files, len(files), 1))
    assert {zone: verdict.zones[zone] for zone in expected} == expected
    comment = render_markdown(verdict)
    for path in files:
        assert f"`{path}`" in comment


def test_src_layout_keeps_protected_mixed_and_uncertain_paths_conservative():
    files = [
        "src/acme/formatting/normalize.py",
        "tests/unit/formatting/nested/test_normalize.py",
        "src/acme/domain/order.py",
        "agent-redline-policy.yaml",
        "docs/contracts/order-lifecycle.md",
        "experimental/legacy.py",
    ]
    policy = {
        "version": 1,
        "project": {"name": "src-service", "extension": "python"},
        "zones": {
            "red": [
                {"path": "src/acme/domain/**", "reason": "domain model", "checkpoint": "architecture-review"},
                {"path": "agent-redline-policy.yaml", "reason": "governance", "checkpoint": "architecture-review"},
            ],
            "blue": [
                {"path": "src/acme/formatting/**", "reason": "replaceable formatting code"},
                {"path": "tests/unit/formatting/**", "reason": "focused formatter tests"},
            ],
        },
        "behaviorContracts": {"paths": ["docs/contracts/**"], "verification": "contract-check", "checkpoint": "behavior-review"},
        "checkpoints": {"architecture-review": {"satisfiedBy": ["codeownerApproval"]}, "behavior-review": {"satisfiedBy": ["codeownerApproval"]}},
    }
    _check(policy, files, {
        "red": ["src/acme/domain/order.py", "agent-redline-policy.yaml", "docs/contracts/order-lifecycle.md"],
        "blue": ["src/acme/formatting/normalize.py", "tests/unit/formatting/nested/test_normalize.py"],
        "gray": ["experimental/legacy.py"],
    })


def test_nested_jvm_layout_classifies_narrow_tests_and_contract_docs():
    files = [
        "modules/catalog/src/main/kotlin/org/acme/catalog/format/Slug.kt",
        "modules/catalog/src/test/kotlin/org/acme/catalog/format/nested/SlugTest.kt",
        "modules/catalog/src/main/kotlin/org/acme/catalog/domain/Item.kt",
        "modules/catalog/src/test/kotlin/org/acme/catalog/architecture/LayerRulesTest.kt",
        "contracts/catalog.yaml",
        "modules/catalog/src/main/kotlin/org/acme/catalog/legacy/Bridge.kt",
    ]
    policy = {
        "version": 1,
        "project": {"name": "multi-module", "extension": "jvm-archunit"},
        "zones": {
            "red": [
                {"path": "modules/catalog/src/main/kotlin/**/domain/**", "reason": "domain model", "checkpoint": "architecture-review"},
                {"path": "modules/catalog/src/test/kotlin/**/architecture/**", "reason": "architecture rules", "checkpoint": "architecture-review"},
            ],
            "blue": [
                {"path": "modules/catalog/src/main/kotlin/**/format/**", "reason": "isolated formatting"},
                {"path": "modules/catalog/src/test/kotlin/**/format/**", "reason": "focused formatter tests"},
            ],
        },
        "behaviorContracts": {"paths": ["contracts/**"], "verification": "contract-check", "checkpoint": "behavior-review"},
        "checkpoints": {"architecture-review": {"satisfiedBy": ["codeownerApproval"]}, "behavior-review": {"satisfiedBy": ["codeownerApproval"]}},
    }
    _check(policy, files, {
        "red": [
            "modules/catalog/src/main/kotlin/org/acme/catalog/domain/Item.kt",
            "modules/catalog/src/test/kotlin/org/acme/catalog/architecture/LayerRulesTest.kt",
            "contracts/catalog.yaml",
        ],
        "blue": [
            "modules/catalog/src/main/kotlin/org/acme/catalog/format/Slug.kt",
            "modules/catalog/src/test/kotlin/org/acme/catalog/format/nested/SlugTest.kt",
        ],
        "gray": ["modules/catalog/src/main/kotlin/org/acme/catalog/legacy/Bridge.kt"],
    })