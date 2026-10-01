#!/usr/bin/env python3
"""Exercise representative Node policy adaptations through the real schema and reporter."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
REDLINE = ROOT / "core" / "agent-redline"
sys.path.insert(0, str(REDLINE))
from core.reporter.reporter import Diff, classify, classify_files, resolve_suppressions_config

SCHEMA = json.loads((REDLINE / "core/schema/agent-policy.schema.json").read_text(encoding="utf-8"))
ADAPTER = yaml.safe_load((REDLINE / "extensions/node/adapter.yaml").read_text(encoding="utf-8"))
SUPPRESSIONS = yaml.safe_load((REDLINE / "extensions/node/suppressions.yaml").read_text(encoding="utf-8"))

FIXTURES = {
"Minimap-like package and checked-in mirrors": {
        "red": [
            {"path": "package/minimap/src/source-write-guard.js", "reason": "guarded source writes and rollback", "checkpoint": "architecture-review"},
            {"path": "package/minimap/src/sessions.js", "reason": "server lifecycle and shared session contract", "checkpoint": "architecture-review"},
            {"path": "package/minimap/src/checkout-identity.js", "reason": "checkout identity boundary", "checkpoint": "architecture-review"},
            {"path": "package/minimap/server.js", "reason": "server lifecycle entry point", "checkpoint": "architecture-review"},
            {"path": "package/minimap/CONTRACT.md", "reason": "public behavior contract", "checkpoint": "architecture-review"},
            {"path": "test/contracts/**", "reason": "protected contract tests", "checkpoint": "architecture-review"},
            {"path": "agent-redline-policy.yaml", "reason": "governance source of truth", "checkpoint": "architecture-review"},
        ],
        "blue": [
            {"path": "test/unit/**", "reason": "unit tests"},
            {"path": "test/playwright/**", "reason": "browser tests"},
            {"path": "docs/**", "reason": "documentation"},
        ],
        "watch": [
            {"path": "package/minimap/package.json", "reason": "package scripts and exports"},
            {"path": "package-lock.json", "reason": "resolved dependencies"},
            {"path": "skills/minimap-roadmap/runtime/**", "reason": "checked-in runtime mirror"},
            {"path": "skills/minimap-spec-review/runtime/**", "reason": "checked-in runtime mirror"},
        ],
        "files": [
            "package/minimap/src/source-write-guard.js", "package/minimap/src/sessions.js",
            "package/minimap/src/checkout-identity.js", "package/minimap/server.js",
            "package/minimap/CONTRACT.md", "test/contracts/checkout.test.js", "test/unit/options.test.js",
            "test/playwright/smoke.spec.js", "package/minimap/package.json", "package-lock.json",
            "skills/minimap-roadmap/runtime/source-write-guard.js",
            "skills/minimap-spec-review/runtime/server.js", "package/minimap/ui/panel.js", "docs/setup.md",
            "agent-redline-policy.yaml",
        ],
        "red_paths": [
            "package/minimap/src/source-write-guard.js", "package/minimap/src/sessions.js",
            "package/minimap/src/checkout-identity.js", "package/minimap/server.js",
            "package/minimap/CONTRACT.md", "test/contracts/checkout.test.js", "agent-redline-policy.yaml",
        ],
        "blue_paths": ["test/unit/options.test.js", "test/playwright/smoke.spec.js", "docs/setup.md"],
        "mirrors": ["skills/minimap-roadmap/runtime/source-write-guard.js", "skills/minimap-spec-review/runtime/server.js"],
        "watched": ["package/minimap/package.json", "package-lock.json", "skills/minimap-roadmap/runtime/source-write-guard.js", "skills/minimap-spec-review/runtime/server.js"],
        "gray": ["package/minimap/ui/panel.js"],
        "markers": {
            "package/minimap/src/source-write-guard.js": "// eslint-disable-next-line",
            "test/contracts/checkout.test.js": "// @ts-ignore",
        },
    },
    "Representative TypeScript workspace": {
        "red": [
            {"path": "packages/engine/lib/security/**", "reason": "security-sensitive code", "checkpoint": "security-review"},
            {"path": "packages/engine/lib/index.ts", "reason": "published API entry point", "checkpoint": "api-review"},
            {"path": "packages/engine/test/contracts/**", "reason": "protected contract tests", "checkpoint": "architecture-review"},
            {"path": "agent-redline-policy.yaml", "reason": "governance source of truth", "checkpoint": "architecture-review"},
        ],
        "blue": [
            {"path": "packages/engine/test/unit/**", "reason": "unit tests"},
            {"path": "docs/**", "reason": "documentation"},
        ],
        "watch": [
            {"path": "package.json", "reason": "workspace scripts"},
            {"path": "packages/engine/package.json", "reason": "workspace package exports"},
            {"path": "yarn.lock", "reason": "resolved dependencies"},
            {"path": "packages/engine/lib/generated/**", "reason": "generated declarations and mirrors"},
        ],
        "files": [
            "packages/engine/lib/security/token.ts", "packages/engine/lib/index.ts",
            "packages/engine/test/contracts/public-api.test.ts", "packages/engine/test/unit/math.test.ts",
            "package.json", "packages/engine/package.json", "yarn.lock",
            "packages/engine/lib/generated/api.d.ts", "packages/ui/src/Button.tsx", "docs/architecture.md",
            "agent-redline-policy.yaml",
        ],
        "red_paths": [
            "packages/engine/lib/security/token.ts", "packages/engine/lib/index.ts",
            "packages/engine/test/contracts/public-api.test.ts",
            "agent-redline-policy.yaml",
        ],
        "blue_paths": ["packages/engine/test/unit/math.test.ts", "docs/architecture.md"],
        "mirrors": ["packages/engine/lib/generated/api.d.ts"],
        "watched": ["package.json", "packages/engine/package.json", "yarn.lock", "packages/engine/lib/generated/api.d.ts"],
        "gray": ["packages/ui/src/Button.tsx"],
        "markers": {
            "packages/engine/lib/security/token.ts": "// nosemgrep",
            "packages/engine/test/contracts/public-api.test.ts": "/* eslint-disable */",
        },
    },
}


def run() -> tuple[int, int, list[str]]:
    failures: list[str] = []
    if ADAPTER != {"boundaryAdapter": {"outputFormat": "none"}}:
        failures.append("adapter must declare only outputFormat: none")
    if not SUPPRESSIONS.get("suppressions", {}).get("inlineComments"):
        failures.append("Node suppression defaults are missing")

    for name, fixture in FIXTURES.items():
        policy = {
            "version": 1,
            "project": {"name": "fixture", "extension": "node"},
            "zones": {key: fixture[key] for key in ("red", "blue", "watch")},
            "boundaryAdapter": ADAPTER["boundaryAdapter"],
            "suppressions": {"useExtensionDefaults": True, "exemptPaths": []},
            "prRules": {"maxChangedFiles": {"warn": 30, "fail": 80}, "maxLinesChanged": {"warn": 800, "fail": 1500}},
            "checkpoints": {
                "architecture-review": {"description": "Architecture review", "satisfiedBy": ["codeownerApproval", {"label": "architecture-reviewed"}]},
                "api-review": {"description": "API review", "satisfiedBy": ["codeownerApproval", {"label": "api-reviewed"}]},
                "security-review": {"description": "Security review", "satisfiedBy": ["codeownerApproval", {"label": "security-reviewed"}]},
            },
            "modes": {"default": "shadow", "perCheck": {"boundary_violation": "binding"}},
        }
        try:
            jsonschema.validate(policy, SCHEMA)
            zones = classify_files(fixture["files"], policy)
            if not set(fixture["red_paths"]) <= set(zones["red"]):
                raise AssertionError(f"sensitive source or protected contract escaped red: {fixture['red_paths']}")
            if not set(fixture["blue_paths"]) <= set(zones["blue"]):
                raise AssertionError(f"narrow unit tests or ordinary docs escaped blue: {fixture['blue_paths']}")
            if not set(fixture["gray"]) <= set(zones["gray"]):
                raise AssertionError(f"unknown implementation should remain gray: {zones['gray']}")
            if not set(fixture["watched"]) <= set(zones["watch"]):
                raise AssertionError(f"manifest, lock, generated, or mirror paths not watched: {fixture['watched']}")
            if zones["excluded"]:
                raise AssertionError(f"unexpected exclusions: {zones['excluded']}")
            mirror_zones = [zone for zone in ("red", "blue", "gray") if set(fixture["mirrors"]) <= set(zones[zone])]
            if len(mirror_zones) != 1:
                raise AssertionError("mirrors must remain visible in the same ordinary zone")

            with tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                marker_lines = {path: [(1, marker)] for path, marker in fixture["markers"].items()}
                (repo / ".agent-redline").mkdir()
                (repo / ".agent-redline/suppressions.yaml").write_text(yaml.safe_dump(SUPPRESSIONS), encoding="utf-8")
                effective = resolve_suppressions_config(policy, repo)
                verdict = classify(policy, Diff(list(fixture["markers"]), len(fixture["markers"]), 2, added_by_file=marker_lines), suppressions_config=effective)
                found = {match.file for match in verdict.suppressions}
                if found != set(fixture["markers"]):
                    raise AssertionError(f"suppression scan missed source/contract test: {found}")
                if "architecture-review" not in {checkpoint.id for checkpoint in verdict.checkpoints}:
                    raise AssertionError("red policy and protected contract paths must request architecture review")

                unit_glob = next(entry["path"] for entry in fixture["blue"] if "unit" in entry["path"])
                exempt_policy = {**policy, "suppressions": {"useExtensionDefaults": True, "exemptPaths": [unit_glob]}}
                exempt_path = next(path for path in fixture["blue_paths"] if "unit" in path)
                protected_path = next(path for path in fixture["red_paths"] if "/test/" in path or path.startswith("test/"))
                exempt_diff = Diff(
                    [exempt_path, protected_path], 2, 2,
                    added_by_file={exempt_path: [(1, "// @ts-ignore")], protected_path: [(1, "// @ts-ignore")]},
                )
                exempt_config = resolve_suppressions_config(exempt_policy, repo)
                exempt_verdict = classify(exempt_policy, exempt_diff, suppressions_config=exempt_config)
                if {match.file for match in exempt_verdict.suppressions} != {protected_path}:
                    raise AssertionError("narrow ordinary-unit exemption must preserve protected contract suppression")
        except Exception as exc:
            failures.append(f"{name}: {exc}")
    return len(FIXTURES), len(failures), failures


if __name__ == "__main__":
    total, failed, failures = run()
    print(f"STATUS: {'PASS' if failed == 0 else 'FAIL'}")
    print(f"SUMMARY: {total - failed}/{total} representative Node policy adaptations validated")
    print(f"FAILURES: {failed}")
    for failure in failures:
        print(f"  - {failure}", file=sys.stderr)
    raise SystemExit(bool(failed))
