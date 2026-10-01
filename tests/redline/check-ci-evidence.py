#!/usr/bin/env python3
"""Run shipped CI evidence/report/gate blocks against genuine Git objects."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[2]
REPORTER = ROOT / "core/agent-redline/core/reporter/reporter.py"
BASH = r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt" else shutil.which("bash")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
CATALOGS = [f"{root}/skills/agent-workflow/agent-redline/extensions/node/suppressions.yaml" for root in (".claude", ".agents")]
ODD_PATHS = ["src/space name.ts", "src/trailing.ts ", "src/tab\tname.ts", "src/שלום.ts", "src/line\nname.ts"]
WORKFLOWS = ("core/templates/.github/workflows/agent-workflow.yml.template", ".github/workflows/agent-workflow.yml")


def command(args, cwd, *, data=None, env=None, check=True):
    result = subprocess.run(args, cwd=cwd, input=data, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env, creationflags=NO_WINDOW)
    if check and result.returncode:
        raise AssertionError(f"{args[0]} exited {result.returncode}: {result.stderr.decode('utf-8', 'replace')}")
    return result


def git(repo, *args, data=None):
    return command(["git", *args], repo, data=data).stdout


def commit(repo, files, parent=None):
    # Index/object fixtures can represent tabs/newlines without creating NTFS names.
    git(repo, "read-tree", "--empty")
    rows = b""
    for name, content in files.items():
        blob = git(repo, "hash-object", "-w", "--stdin", data=content).strip()
        rows += b"100644 " + blob + b"\t" + name.encode("utf-8") + b"\0"
    git(repo, "update-index", "-z", "--index-info", data=rows)
    tree = git(repo, "write-tree").decode().strip()
    args = ["commit-tree", tree] + (["-p", parent] if parent else [])
    return git(repo, *args, data=b"CI evidence fixture\n").decode().strip()


def shell(repo, script, env, expressions=None):
    expressions = expressions or {}
    script = re.sub(r"\$\{\{\s*(.*?)\s*\}\}", lambda m: expressions[m[1]], script)
    assert "${{" not in script
    if os.name == "nt":
        script = 'export PATH="$(cygpath -u "$CI_TEST_BIN"):$PATH"\n' + script
    return command([BASH, "--noprofile", "--norc", "-eo", "pipefail", "-c", script],
                   repo, env=env, check=False)


def fixture(repo, active):
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "fixture@example.invalid")
    git(repo, "config", "user.name", "CI fixture")
    # Permit Git-only object/index names; these paths are never checked out.
    git(repo, "config", "core.protectNTFS", "false")
    catalog = (ROOT / "core/agent-redline/extensions/node/suppressions.yaml").read_bytes()
    common_files = {"src/guard.ts": b"const before = 1;\n"}
    common = commit(repo, common_files)
    base = commit(repo, {**common_files, "base-only.ts": b"base branch only\n"}, common)
    head_files = {**common_files, **dict.fromkeys(CATALOGS, catalog),
                  "binary.dat": b"\0binary\0", ".agent-workflow/ignored.md": b"ignored\n" * 20}
    head_files["src/guard.ts"] = b"// @ts-ignore\nconst after = 2;\n" if active else b"const after = 2;\n"
    for path in ODD_PATHS:
        head_files[path] = b"// @ts-ignore\nconst unusual = 3;\n" if active else b"const unusual = 3;\n"
    head = commit(repo, head_files, common)
    git(repo, "update-ref", "HEAD", head)
    git(repo, "update-ref", "refs/remotes/origin/main", base)
    for path in ("scripts/agent-redline-report.py", "core/agent-redline/core/reporter/reporter.py"):
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPORTER, target)
    for name in ("agent-policy", "suppressions"):
        target = repo / f".agent-redline/{name}.schema.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / f"core/agent-redline/core/schema/{name}.schema.json", target)
    (repo / ".agent-redline/suppressions.yaml").write_bytes(catalog)
    # Exact-head masking must not depend on this dirty working-tree catalog.
    for path in CATALOGS:
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(catalog + b"\n# // @ts-ignore\n")
    policy = yaml.safe_load((ROOT / "agent-redline-policy.yaml").read_text(encoding="utf-8"))
    policy["project"]["extension"] = "node"
    policy["suppressions"] = {"useExtensionDefaults": True, "exemptPaths": []}
    policy["prRules"] = {"maxChangedFiles": {"warn": 1000, "fail": 2000},
                         "maxLinesChanged": {"warn": 10000, "fail": 20000}}
    policy["modes"] = {"default": "shadow", "perCheck": {"boundary_violation": "binding"}}
    bins = repo / "test-bin"
    bins.mkdir()
    driver = bins / "python"
    driver.write_text("#!/bin/sh\nexec " + shlex.quote(Path(sys.executable).as_posix()) + ' "$@"\n', encoding="utf-8")
    driver.chmod(0o755)
    env = {**os.environ, "BASE_SHA": base, "HEAD_SHA": head, "CI_TEST_BIN": str(bins),
           "GITHUB_OUTPUT": str(repo / "github-output"), "GITHUB_STEP_SUMMARY": str(repo / "job-summary")}
    if os.name != "nt":
        env["PATH"] = str(bins) + os.pathsep + env["PATH"]
    return common, head, head_files, policy, env


def verdict_step(repo, step, env, expressions):
    (repo / "github-output").write_text("", encoding="utf-8")
    result = shell(repo, step["run"], env, expressions)
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    outputs = dict(line.split("=", 1) for line in (repo / "github-output").read_text().splitlines() if "=" in line)
    assert (repo / "redline-verdict.json").exists(), (result.stderr + result.stdout)[-3000:].decode("utf-8", "replace")
    return int(outputs["exit_code"]), json.loads((repo / "redline-verdict.json").read_text(encoding="utf-8"))


def scaffold_blocks(repo, env, expected):
    expressions = {"github.event.pull_request.base.sha": env["BASE_SHA"],
                   "github.event.pull_request.head.sha": env["HEAD_SHA"],
                   "github.event.before": env["BASE_SHA"], "github.sha": env["HEAD_SHA"]}
    event = repo / "event.json"
    event.write_text('{"pull_request":{"labels":[]}}', encoding="utf-8")
    env = {**env, "GITHUB_EVENT_PATH": str(event)}
    assert shell(repo, "command -v jq", env).returncode == 0, "PR scaffold requires real jq on PATH"
    exercised = 0
    for extension in ("python", "jvm-archunit"):
        text = (ROOT / f"core/agent-redline/extensions/{extension}/scaffold.md").read_text(encoding="utf-8")
        for block in re.findall(r"^```yaml\s*\n(.*?)\n```", text, re.S | re.M):
            if "python scripts/agent-redline-report.py" not in block:
                continue
            document = yaml.safe_load(block)
            for job in document.get("jobs", document).values():
                if not isinstance(job, dict):
                    continue
                steps = job.get("steps", [])
                reports = [step for step in steps if "python scripts/agent-redline-report.py" in step.get("run", "")]
                if not reports:
                    continue
                (repo / "github-output").write_text("", encoding="utf-8")
                result = shell(repo, reports[0]["run"], env, expressions)
                assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
                verdict = json.loads((repo / "build/verdict.json").read_text(encoding="utf-8"))
                assert verdict["suppressions"] == expected["suppressions"] and verdict["prSize"] == expected["prSize"]
                assert "exit_code=2" in (repo / "github-output").read_text()
                gate = next(step for step in steps if step.get("name") == "Enforce reporter exit code")
                assert shell(repo, gate["run"], env, {**expressions, "steps.report.outputs.exit_code": "2"}).returncode != 0
                exercised += 1
    assert exercised == 3, f"Expected actual Python PR/push and JVM reporter blocks, found {exercised}"


def exercise(path, active, size):
    workflow = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    steps = workflow["jobs"]["redline"]["steps"]
    changed = next(step for step in steps if step.get("id") == "changed")
    review_inputs = next(step for step in steps if step.get("id") == "review_inputs")
    report = next(step for step in steps if step.get("id") == "report")
    enforce = next(step for step in steps if step.get("name") == "Enforce reporter exit code")
    artifact = next(step for step in steps if step.get("uses", "").startswith("actions/upload-artifact@"))
    assert artifact["if"] == "always()" and artifact["with"]["path"] == "redline-verdict.json"
    with tempfile.TemporaryDirectory(prefix="ci-evidence-") as tmp:
        repo = Path(tmp)
        common, head, files, policy, env = fixture(repo, active)
        env["LABELS_JSON"] = "[]"
        expressions = {"github.repository": "fixture/repository", "github.event.pull_request.number": "1"}
        assert shell(repo, changed["run"], env).returncode == 0
        changed_paths = (repo / "changed-files.z").read_bytes().split(b"\0")
        expected_paths = {p.encode() for p in files}
        assert changed_paths[-1] == b"" and set(changed_paths[:-1]) == expected_paths, (
            f"Missing paths {expected_paths - set(changed_paths[:-1])!r}; extra paths {set(changed_paths[:-1]) - expected_paths!r}")
        assert b"base-only.ts" not in changed_paths
        assert f"merge_base={common}" in (repo / "github-output").read_text()
        assert shell(repo, review_inputs["run"], env, expressions).returncode == 0
        review_output = dict(line.split("=", 1) for line in (repo / "github-output").read_text().splitlines() if "=" in line)
        expressions.update({"steps.review_inputs.outputs.labels": review_output["labels"],
                            "steps.review_inputs.outputs.codeowner_approvals": review_output["codeowner_approvals"]})
        numstat = git(repo, "diff", "--numstat", "-z", "--no-renames", common, head)
        rows = [row.split(b"\t", 2) for row in numstat.split(b"\0") if row]
        counted = [row for row in rows if not row[2].startswith(b".agent-workflow/")]
        lines = sum(int(a) + int(d) for a, d, _ in counted if a != b"-")
        if size != "ok":
            policy["prRules"]["maxLinesChanged"] = {"warn": lines - 2, "fail": lines + 1 if size == "warn" else lines - 1}
            policy["modes"]["perCheck"]["pr_size"] = "binding"
        (repo / "agent-redline-policy.yaml").write_text(yaml.safe_dump(policy), encoding="utf-8")
        code, verdict = verdict_step(repo, report, env, expressions)
        assert "prSize" in verdict, verdict
        assert verdict["prSize"] == {"files": len(counted), "lines": lines, "verdict": size,
                                     "excludedFiles": 1, "excludedLines": 20}, verdict["prSize"]
        matches = {item["file"] for item in verdict["suppressions"]}
        assert matches == ({"src/guard.ts", *ODD_PATHS} if active else set()), matches
        visible = set().union(*(set(paths) for paths in verdict["zones"].values()))
        assert set(CATALOGS) <= visible and set(ODD_PATHS) <= visible
        assert code == 2 if active or size == "fail" else code in (0, 1)
        expressions["steps.report.outputs.exit_code"] = str(code)
        gated = shell(repo, enforce["run"], env, expressions)
        assert (gated.returncode != 0) == (code == 2)
        local = shell(repo, (ROOT / "core/agent-redline/core/templates/pre-push-check.sh").read_text(encoding="utf-8"), env)
        assert local.returncode == code, local.stderr.decode("utf-8", "replace")
        local_verdict = json.loads(local.stdout)
        assert local_verdict["prSize"] == verdict["prSize"] and local_verdict["suppressions"] == verdict["suppressions"]
        if path == WORKFLOWS[0] and active:
            scaffold_blocks(repo, env, verdict)
        # Run the actual checker-side changed block too, preserving both job callers.
        checker_changed = next(step for step in workflow["jobs"]["agent-workflow"]["steps"] if step.get("id") == "changed")
        assert shell(repo, checker_changed["run"], env).returncode == 0
        assert (repo / "changed-files.z").read_bytes().split(b"\0") == changed_paths
        if not active and size == "ok":
            artifact_path = repo / "redline-verdict.json"
            artifact_path.write_text("not JSON", encoding="utf-8")
            assert shell(repo, enforce["run"], env, expressions).returncode != 0
            artifact_path.unlink()
            assert shell(repo, enforce["run"], env, expressions).returncode != 0
            cli = [sys.executable, str(repo / "scripts/agent-redline-report.py"), "--policy", "agent-redline-policy.yaml",
                   "--changed-files-z", "changed-files.z", "--lines-per-file-z", "lines-per-file.z",
                   "--diff-unified", "diff-unified.patch", "--json-out", "direct-verdict.json"]
            missing_head = command(cli, repo, check=False)
            assert missing_head.returncode == 2
            assert set(CATALOGS) <= {item["file"] for item in json.loads((repo / "direct-verdict.json").read_text())["suppressions"]}
            invalid = command(cli + ["--head-ref", "not-a-commit"], repo, check=False)
            assert invalid.returncode == 2 and b"Traceback" not in invalid.stderr
            assert json.loads((repo / "direct-verdict.json").read_text())["exitCode"] == 2
            evidence = repo / "lines-per-file.z"
            original = evidence.read_bytes()
            for malformed in (original[:-1], original + b"1\t0\toutside.ts\0"):
                evidence.write_bytes(malformed)
                result = command(cli + ["--head-ref", head], repo, check=False)
                assert result.returncode == 2 and b"Traceback" not in result.stderr
                assert json.loads((repo / "direct-verdict.json").read_text())["exitCode"] == 2
            evidence.write_bytes(original)


def main():
    total = 0
    for path in WORKFLOWS:
        for active, size in ((False, "ok"), (True, "ok"), (False, "warn"), (False, "fail")):
            try:
                exercise(path, active, size)
            except Exception as exc:
                raise AssertionError(f"{path}, active={active}, size={size}: {exc}") from exc
            total += 1
    print("STATUS: PASS")
    print(f"SUMMARY: {total} actual CI block scenarios; merge-base, lossless paths, suppression definitions/source, line limits and gates")
    print("LIMITS: NTFS-invalid names covered via Git objects/index; GitHub artifact service, generation/ArchUnit/import-linter/API validation not exercised")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("STATUS: FAIL")
        print(f"FAILURES: {exc}", file=sys.stderr)
        raise SystemExit(1)
