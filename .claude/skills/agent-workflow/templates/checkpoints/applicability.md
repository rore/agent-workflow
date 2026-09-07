# Workflow applicability

Load only when `agent-workflow.yaml` contains `applicability.documentationOnly` or during bootstrap discovery.

## Decision order

1. Require the workflow if any changed path is unapproved, protected, risky, duplicated, malformed, or missing from the evidence.
2. Otherwise use a branch/PR without a Work Record.
3. Direct default-branch work is the lowest priority and needs every condition below.

Never exempt config, policy, schema, CI, agent instructions, hooks, installed/vendored harness files, Work Records, or normative specs even when an approved directory contains them. A rename supplies both old and new paths. Any doubt selects step 1.

## Bootstrap

Discover actual tracked documentation, roadmap/planning, and root README paths from the repository; names such as `roadmap/` are not canonical. Show exact candidates in the inert config draft and require explicit human approval. Mirror approved ordinary documentation paths into Redline blue zones; keep governance exclusions red/watch. Omit the block when approval is absent.

Resolve the repository's actual default branch. Check both classic branch protection and applicable rulesets live. Set `directDefaultBranchAllowed: true` only when both conclusively show the branch is unprotected and the human separately approves direct work; protected, authenticated-but-incomplete, unsupported, or unavailable checks mean `false`.

## Runtime

Use one complete NUL-delimited path set. CI uses `git diff --name-only -z --no-renames <base> <head>`; local work concatenates `git diff --name-only -z --no-renames HEAD` (staged + unstaged tracked) and `git ls-files --others --exclude-standard -z` (untracked). Feed the same file to Redline and `agent-workflow-check --changed-files-z`. Only a passing `workflow.applicability` result removes the Work Record requirement. Redline must classify every path blue with no watch entries, checkpoint, boundary violation, or change flag.

Before suggesting direct default-branch work, rerun the checker with `--check-default-branch-protection`; it resolves the actual default branch and checks GitHub protection plus applicable rulesets. If protection is present or cannot be proven absent, use a branch/PR without a Work Record. A normal workflow decision always wins. This gate never authorizes commit or push and never bypasses protection.

PR CI enforces the no-Work-Record exemption and still runs Redline and repository tests. It cannot police direct pushes; the runtime gate and repository protection are that control.