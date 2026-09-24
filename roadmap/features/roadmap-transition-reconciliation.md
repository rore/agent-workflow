---
id: roadmap-transition-reconciliation
title: 'Reconcile roadmap progress at task transitions'
status: active
priority: medium
commitment: committed
---

# Reconcile roadmap progress at task transitions

## Summary

When a workflow task has an applicable canonical roadmap item, remind the agent to carry its exact reference and reconcile or report task progress at pickup, pause, resume, handoff, and completion. Use that roadmap's own rules. The existing result-review check remains the detailed completion check.

## Acceptance scenarios

- No roadmap or no applicable item: no roadmap action.
- Native roadmap item: use its own status and ownership convention, without requiring Minimap.
- Partial task completion: report shipped task scope while retaining unfinished feature scope.
- Pause or handoff with a designated roadmap owner: report progress and exact item reference; do not modify, commit, or clean the owner's checkout.
- Standalone read-only request: stays outside Agent Workflow.

## Scope

Update the SPEC and existing agent-loaded transition guidance; record the decision and ship synchronized skill copies. Do not add a field, hook, tracker, required dependency, or Minimap-specific commands and state vocabulary.

## Done when

The guidance and packaged copies agree, scenario review passes, and required CI passes.
