import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs/promises";
import { fileURLToPath } from "node:url";
import os from "node:os";
import path from "node:path";
import plugin from "../../core/skill/opencode/agent-workflow.mjs";

const root = path.resolve(fileURLToPath(new URL("../..", import.meta.url)));
const source = await fs.readFile(path.join(root, "core/skill/opencode/agent-workflow.mjs"), "utf8");
assert.match(source, /timeout:\s*30000/);
assert.match(source, /windowsHide:\s*true/);
assert.match(source, /if \(result\.error\) return \{ deny:/);

function git(cwd, ...args) {
  const result = spawnSync("git", args, { cwd, encoding: "utf8", windowsHide: true });
  assert.equal(result.status, 0, result.stderr);
}

const temp = await fs.mkdtemp(path.join(os.tmpdir(), "agent-workflow-opencode-"));
const repo = path.join(temp, "repo");
const origin = path.join(temp, "origin.git");
await fs.mkdir(path.join(repo, "scripts"), { recursive: true });
await fs.copyFile(
  path.join(root, "scripts/agent-workflow-runtime.py"),
  path.join(repo, "scripts/agent-workflow-runtime.py"),
);
await fs.writeFile(path.join(repo, "README.md"), "fixture\n");
git(repo, "init", "-q", "-b", "main");
git(repo, "config", "user.email", "test@example.com");
git(repo, "config", "user.name", "Runtime Test");
git(repo, "add", ".");
git(repo, "commit", "-qm", "baseline");
git(temp, "init", "--bare", "-q", origin);
git(repo, "remote", "add", "origin", origin);
git(repo, "push", "-q", "origin", "main");
git(origin, "symbolic-ref", "HEAD", "refs/heads/main");
git(repo, "fetch", "-q", "origin");
git(repo, "switch", "-qc", "feat/no-record");

const savedPython = process.env.PYTHON;
const savedPath = process.env.PATH;
const python = process.platform === "win32"
  ? path.join(root, ".venv/Scripts/python.exe")
  : "python3";
try {
  process.env.PYTHON = python;
  const denial = await plugin({ directory: repo });
  await assert.rejects(
    denial["tool.execute.before"](
      { tool: "write" },
      { args: { file_path: path.join(repo, "src/example.py") } },
    ),
    /DENY.*agent-workflow\.yaml/,
  );

  process.env.PYTHON = process.execPath;
  const failed = await plugin({ directory: repo });
  await assert.rejects(
    failed["tool.execute.before"](
      { tool: "write" },
      { args: { file_path: path.join(repo, "src/example.py") } },
    ),
  );

  delete process.env.PYTHON;
  process.env.PATH = "";
  const logs = [];
  const degraded = await plugin({
    directory: path.join(temp, "missing-runtime"),
    client: { app: { log: async (entry) => logs.push(entry) } },
  });
  await assert.doesNotReject(
    degraded["tool.execute.before"](
      { tool: "write" },
      { args: { file_path: "src/example.py" } },
    ),
  );
  assert.ok(logs.some(({ body }) => body?.message === "Runtime guard degraded"));
} finally {
  if (savedPython === undefined) delete process.env.PYTHON;
  else process.env.PYTHON = savedPython;
  process.env.PATH = savedPath;
  await fs.rm(temp, { recursive: true, force: true });
}

console.log("ok: OpenCode denial, fail-closed errors, and degraded unavailability");