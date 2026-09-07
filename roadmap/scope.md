# Current focus

Agent Workflow's workflow applicability policy is shipped: bootstrap discovers
repository-specific documentation paths, CI evaluates the complete diff, and
direct-default work remains separately gated by live branch protection.

The next improvement is a local preflight command that composes the existing
Redline and workflow checks. It should consume the shipped applicability
decision rather than introduce another policy engine.