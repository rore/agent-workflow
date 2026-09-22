"""Cross-platform checks for the consumer runtime check entrypoint."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "dist/agent-workflow/scripts/agent-workflow-check.py"
SHELL = ROOT / "scripts/agent-workflow-runtime.sh"
POWERSHELL = ROOT / "scripts/agent-workflow-runtime.ps1"
TEMP_ROOT = None if os.name == "nt" else "/tmp"


def run(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=cwd, env=env, text=True, capture_output=True, timeout=20
    )


def python_launcher(root: Path) -> Path:
    directory = root / "interpreter path with spaces"
    venv.EnvBuilder(with_pip=False).create(directory)
    return directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def fixture_repo(root: Path) -> Path:
    repo = root / "consumer repo"
    scripts = repo / "scripts"
    scripts.mkdir(parents=True)
    subprocess.run(
        [shutil.which("git") or "git", "init", "-q"], cwd=repo, check=True
    )
    shutil.copy2(SHELL, scripts / SHELL.name)
    shutil.copy2(POWERSHELL, scripts / POWERSHELL.name)
    for wrapper in (scripts / SHELL.name, scripts / POWERSHELL.name):
        wrapper.write_bytes(wrapper.read_bytes().replace(b"\r\n", b"\n"))
    (scripts / "agent-workflow-check.py").write_text(
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "Path(os.environ['AW_ARGS_OUT']).write_text(json.dumps(sys.argv[1:]))\n"
        "sys.exit(int(os.environ.get('AW_EXIT', '0')))\n",
        encoding="utf-8",
    )
    return repo


def restricted_env(root: Path) -> dict[str, str]:
    git = shutil.which("git")
    assert git
    env = os.environ.copy()
    if os.name == "nt":
        env["PATH"] = str(Path(git).parent)
    else:
        restricted_bin = root / "restricted-bin"
        restricted_bin.mkdir()
        os.symlink(git, restricted_bin / "git")
        env["PATH"] = str(restricted_bin)
    env["PYTHON"] = str(python_launcher(root))
    env["AW_ARGS_OUT"] = str(root / "args.json")
    return env


def assert_adapter(command: list[str], repo: Path, env: dict[str, str]) -> None:
    expected = ["--repo-root", str(repo), "--slug", "slug with spaces"]
    result = run(command + expected, repo, env)
    assert result.returncode == 0, result.stderr
    assert json.loads(Path(env["AW_ARGS_OUT"]).read_text()) == expected
    env["AW_EXIT"] = "1"
    assert run(command + expected, repo, env).returncode == 1
    git = Path(shutil.which("git") or "git")
    non_python_success = (
        git.parent.parent / "usr/bin/true.exe"
        if os.name == "nt"
        else Path(shutil.which("true") or "")
    )
    for invalid in (
        Path(repo / "missing python"),
        Path(shutil.which("where.exe") or "")
        if os.name == "nt"
        else Path(shutil.which("false") or ""),
        non_python_success,
    ):
        assert invalid and (not invalid.exists() or invalid.is_file())
        env["PYTHON"] = str(invalid)
        result = run(command + expected, repo, env)
        assert result.returncode == 2
        assert "Python 3.11+" in result.stderr and "set PYTHON" in result.stderr
        assert "DEGRADED:" not in result.stderr


def test_adapters() -> None:
    with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as raw:
        root = Path(raw)
        repo = fixture_repo(root)
        env = restricted_env(root)
        commands: list[list[str]] = []

        bash = shutil.which("bash")
        if bash and not (os.name == "nt" and "system32" in bash.lower()):
            commands.append(
                [bash, str(repo / "scripts" / SHELL.name), "codex", "check"]
            )
        else:
            print("skip: no same-filesystem Bash")

        powershells = [shutil.which("pwsh")]
        if os.name == "nt":
            powershells.append(shutil.which("powershell.exe"))
        for powershell in dict.fromkeys(p for p in powershells if p):
            commands.append(
                [
                    powershell,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(repo / "scripts" / POWERSHELL.name),
                    "codex",
                    "check",
                ]
            )
        if not any(powershells):
            print("skip: native PowerShell unavailable")

        assert commands
        for index, command in enumerate(commands):
            adapter_env = env.copy()
            adapter_env["PYTHON"] = str(python_launcher(root / f"adapter-{index}"))
            assert_adapter(command, repo, adapter_env)

        no_python = env.copy()
        no_python.pop("PYTHON", None)
        result = run(commands[0], repo, no_python)
        assert result.returncode == 2
        assert "Python 3.11+" in result.stderr and "set PYTHON" in result.stderr


def test_missing_dependencies() -> None:
    for present_stub, missing in (("yaml", "jsonschema"), ("jsonschema", "PyYAML")):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as raw:
            stub = Path(raw)
            (stub / f"{present_stub}.py").write_text("", encoding="utf-8")
            env = os.environ.copy()
            env["PYTHONPATH"] = str(stub)
            result = run([sys.executable, "-S", str(CHECKER), "--help"], ROOT, env)
            assert result.returncode == 2
            assert not result.stdout and "Traceback" not in result.stderr
            assert missing in result.stderr and sys.executable in result.stderr
            assert "Create a repository .venv if absent" in result.stderr
            assert '".venv/bin/python" -m pip install pyyaml jsonschema' in result.stderr
            assert '& ".venv/Scripts/python.exe" -m pip install pyyaml jsonschema' in result.stderr


if __name__ == "__main__":
    test_adapters()
    test_missing_dependencies()
    print("ok: runtime check entrypoints")