# Current focus

Agent Workflow's workflow applicability policy and deterministic Work Record
resolver are shipped.

The next improvement is behavioral requirement integrity. It should preserve
the Task Context established before discovery, require authorized human approval
for material requirement changes, and protect repository-designated behavioral
contracts without pretending that path protection proves regression safety.

The local preflight command remains next after this work and should compose the
existing Redline and workflow checks rather than introduce another policy engine.
