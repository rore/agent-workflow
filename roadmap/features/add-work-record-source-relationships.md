---
id: add-work-record-source-relationships
title: 'Store source-item and PR relationships in Work Records'
status: queued
priority: medium
commitment: committed
---

# Store source-item and PR relationships in Work Records

## Summary

Make the Work Record the authoritative place for exact source-item and pull-request relationships. Expose a bounded, versioned, machine-readable read contract so another tool can show related work without maintaining backlinks. A reader must distinguish an explicit declaration of no source item from an old record whose source is unknown.

## Why

The current guidance asks agents to carry source identity, but records may keep it only in prose. The existing optional `Requirement baseline.source` is an immutable requirement provenance string, not a mutable, validated relationship list. The [canonical Work Record resolver](../../docs/SPEC.md#131-canonical-work-record) identifies one record and its state; it does not expose source items or PRs. A consumer cannot safely recover exact links by scanning prose or titles.

This feature is the Agent Workflow part of the [collection plan](https://github.com/rore/rore-collection/blob/main/plans/feature-related-work.md). [Minimap's related-work feature](https://github.com/rore/minimap/blob/main/roadmap/features/show-feature-related-work.md) owns discovery, reverse lookup, and display. The two implementers must agree on the smallest interoperable read contract before coding; Agent Workflow owns and documents its normative format.

## Existing seams to inspect

- [Work Record parser and renderer](../../core/work_record/parser.py), [routine](../../core/templates/work-record-routine.md) and [expanded](../../core/templates/work-record-expanded.md) templates: marker-bounded fields, optional JSON fields, legacy parsing, and round trips.
- [Configured local backend](../../core/work_record/local_backend.py), [configuration](../../core/config/loader.py), and [schema](../../core/schema/agent-workflow.schema.json): `workRecord.local.taskPath`, containment, and multiple repository layouts.
- [Read-only resolver](../../core/checker/checker.py) and [SPEC §13.1](../../docs/SPEC.md#131-canonical-work-record): supplied `agent-workflow:<slug>` identity, repository-relative path, bounded JSON output, trusted executable, and branch fallback. Extend or compose with this owner; do not define an independent Markdown parser or another record-selection rule.
- [Context](../../docs/agent-workflow/establish-context.md), transition guidance, [checker](../../core/checker/predicates.py), and packaging: capture, update, validation, and consumer behavior must agree in source and installed copies.

## In Scope

### Authoritative relationship data

Define one versioned structured relationship format inside each Work Record, readable by humans and parsed by Agent Workflow. Reuse the existing marker-block parser and optional-field pattern where it fits. Specify the exact field names, value types, normalization, size limits, and version handling in the normative SPEC before changing templates or code. The relationship data is separate from the immutable Requirement baseline; changes to links must not rewrite baseline history.

For each source item, retain provider, repository or namespace, and provider-owned item identity as separate exact values. Store a usable location only where needed for navigation; URLs, titles, display labels, and text matches are not identity. Support more than one source item when the task genuinely spans sources. Express deliberate `no source item` distinctly from `unknown/not recorded` on legacy records. Do not require any tracker, Minimap, Pallium, or a particular provider for ordinary tasks. Define exact PR identity by its hosting provider, repository, and PR number or provider-owned ID, using the smallest canonical representation that can be validated and navigated; allow multiple PRs for a task. Reject duplicate exact identities and malformed or unsupported versions rather than guessing their meaning.

Keep the existing canonical `agent-workflow:<slug>` Work Record identity stable across branch changes and worktrees. A record's repository-relative location comes from the selected checkout's configured `taskPath`, not a hardcoded directory or another worktree's common Git directory. Preserve source and PR references when the file moves within that configuration. The read result must distinguish selected checkout/revision or otherwise let a consumer keep conflicting versions of the same record identity separate; it must not silently merge them.

### Capture and lifecycle

When an authoritative source reference is supplied at creation or pickup, record its exact identity without inferring missing fields from its title. Preserve and update references through resume, handoff, PR creation or linking, and completion. Adding, changing, and removing a relationship is an explicit Work Record edit; PR closure or merge may be observed by the PR owner but does not itself rewrite source relationships. A missing source in an old record remains unknown until verified; the agent must not invent `no source` merely to satisfy the format.

Provide a check that catches malformed relationship data and a supplied source or PR reference lost between an authoritative input and the Work Record. Compare against trustworthy input already available in the creation or transition flow; do not require a new evidence artifact merely for the comparison. Where that input is unavailable, report that the relationship is unverified instead of claiming it matched. Keep legacy records parseable and eligible for ordinary existing workflow checks. Legacy prose may remain useful for humans, but a consumer must not treat it as an authoritative relationship or search it by substring.

### Interoperable read contract

Publish a bounded, read-only structured result from the existing parser/resolver owner, with documented schema version, exact identities, Work Record reference, configured repository-relative record path, selected checkout or revision provenance, and found/absent/invalid/legacy outcomes. Define the consumer handshake and error behavior. The result must be usable by a non-Python consumer without adding Python or other dependencies solely to render a roadmap board and without executing scripts from the inspected repository. Agree the surface with Minimap before implementation; use a trusted packaged command, portable data export, or another small existing mechanism that meets these constraints. A tool may cache a disposable reverse index, but Work Records remain the only maintained links.

Update the SPEC, relevant Work Record/transition guidance, templates, checker/parser documentation, and packaged distribution together. Preserve existing consumers of the version-1 resolver result or provide a documented versioned transition; do not change its meaning silently.

## Acceptance coverage

Test through public source and packaged consumer surfaces, with at least two configured `taskPath` layouts and no imports from the development checkout. Include:

1. Create a record from an exact supplied source, then add, change, and remove source and PR references. Resume and handoff preserve identity; a PR link appears without a second backlink edit.
2. One source, multiple distinct sources and PRs, explicit no-source, and legacy unknown. Exact provider/repository/item matching survives Unicode, spaces, same-named items in different repositories, and similarly numbered PRs. No substring or title match creates a relationship.
3. Missing or malformed fields, duplicate identities, unsupported versions, invalid URLs or unsafe paths, and a supplied reference that was dropped or altered. Invalid data has an explicit error outcome; legacy prose remains readable without becoming authoritative.
4. The same Work Record identity viewed from two worktrees at different revisions, including conflicting links or paths. The consumer can tell the versions apart, while the canonical local resolver never selects a different checkout or scans for the newest file.
5. A changed or removed relationship disappears from the read result. A consumer can rebuild its reverse lookup entirely from current Work Record outputs; no synchronized backlink list is created.
6. A non-Python consumer reads the published contract without installing Python just for display or executing code supplied by an inspected repository. Existing resolver clients and ordinary records still work; source and packaged tests exercise the same contract.

## Out of Scope

Minimap discovery, cache, refresh, and UI; Pallium changes; a mandatory issue tracker; live PR status polling; assignment or approval inboxes; a new task state; automatic feature completion; repository-wide backlink files; and changing current installations or integrations as part of this roadmap item.

## Done When

Agent Workflow owns one documented relationship format and compatible read surface. Its source and packaged E2E checks pass for the lifecycle and edge cases above. Minimap can consume exact links without a second maintained link list, while feature progress remains a reviewed judgment.
