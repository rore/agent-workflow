# Current focus

Agent Workflow's existing workflow and CI checker remain the shipped foundation.
The next improvements are a local preflight command that reuses those checks and
an explicit repository policy for when the workflow can be skipped, including
permission for qualifying roadmap-only edits directly on main.

Both items are planned work, not implemented capabilities. They should reuse the
existing checker and configuration patterns rather than introduce another policy
engine. The applicability policy can ship independently; doctor should consume
its shared decision when available.
