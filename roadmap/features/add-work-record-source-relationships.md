---
id: add-work-record-source-relationships
title: 'Store source-item and PR relationships in Work Records'
status: done
priority: medium
commitment: committed
---

# Store source-item and PR relationships in Work Records

## Summary

Work Records now store exact source-item and pull-request relationships. The shipped versioned metadata decoder lets Minimap show related work without maintained backlinks, while distinguishing declared no-source from legacy unknown. Implementation is complete; installation coverage and pending natural-use adoption are recorded separately under Notes.

## Why

Before this change, agents could keep source identity only in prose. The optional `Requirement baseline.source` remains immutable requirement provenance, not a mutable relationship list. The [canonical Work Record resolver](../../docs/SPEC.md#131-canonical-work-record) still identifies one record and its state without exposing source items or PRs; the separate metadata decoder supplies those links without scanning prose or titles.

This is the Agent Workflow part of the [collection plan](https://github.com/rore/rore-collection/blob/main/plans/feature-related-work.md). [Minimap's related-work feature](https://github.com/rore/minimap/blob/main/roadmap/features/show-feature-related-work.md) owns discovery, reverse lookup, and display. Both implementations use the agreed Workflow-owned contract in [SPEC §13.1](../../docs/SPEC.md#optional-source-relationships).

## Delivered integration surfaces

- [Work Record parser and renderer](../../core/work_record/parser.py), [routine](../../core/templates/work-record-routine.md) and [expanded](../../core/templates/work-record-expanded.md) templates: marker-bounded fields, optional JSON fields, legacy parsing, and round trips.
- [Configured local backend](../../core/work_record/local_backend.py), [configuration](../../core/config/loader.py), and [schema](../../core/schema/agent-workflow.schema.json): `workRecord.local.taskPath`, containment, and multiple repository layouts.
- [Read-only resolver](../../core/checker/checker.py) and [SPEC §13.1](../../docs/SPEC.md#131-canonical-work-record): supplied `agent-workflow:<slug>` identity, repository-relative path, bounded JSON output, trusted executable, and branch fallback. Resolver v1 remains unchanged; the Workflow-owned metadata decoder is a separate read surface, not another record-selection rule.
- [Context](../../docs/agent-workflow/establish-context.md), transition guidance, [checker](../../core/checker/predicates.py), and packaging: capture, update, validation, and consumer behavior must agree in source and installed copies.

## In Scope

### Authoritative relationship data

The optional `Relationships` JSON field uses `schema_version: 1`, exact source tuples and recorded PR URLs. Both Work Record shapes use the existing marker parser; the normative SPEC owns types, bounds and supported/unsupported outcomes. Relationship edits never rewrite the immutable Requirement baseline.

Each source retains exact `provider`, `scope_ref` and `local_ref`; an optional URL is navigation, not identity. Multiple sources and PRs are supported. `sources: []` means known no-source, `sources: null` means unverified, and an absent field is legacy unknown. No tracker or provider is mandatory. Initial supported PR references are canonical GitHub HTTPS URLs. Duplicate identities and malformed/unsafe data are invalid; safe unsupported profiles and versions have explicit diagnostics rather than guessed meaning.

Keep the existing canonical `agent-workflow:<slug>` Work Record identity stable across branch changes and worktrees. A record's repository-relative location comes from the selected checkout's configured `taskPath`, not a hardcoded directory or another worktree's common Git directory. Preserve source and PR references when the file moves within that configuration. The read result must distinguish selected checkout/revision or otherwise let a consumer keep conflicting versions of the same record identity separate; it must not silently merge them.

### Capture and lifecycle

When an authoritative source reference is supplied at creation or pickup, record its exact identity without inferring missing fields from its title. Preserve and update references through resume, handoff, PR creation or linking, and completion. Adding, changing, and removing a relationship is an explicit Work Record edit; PR closure or merge may be observed by the PR owner but does not itself rewrite source relationships. A missing source in an old record remains unknown until verified; the agent must not invent `no source` merely to satisfy the format.

The checker rejects malformed relationship data. Agents capture supplied references and owning-tool PR URLs in the same normal creation/transition edit, then compare read-back with authoritative input already available. A named source without a tuple is resolved through its owning tool; unavailable or ambiguous identity stays unverified. This approved first slice is not automatic input capture or a guarantee that omitted/unreceived input is detected. Legacy records remain parseable; prose is never an authoritative inferred relationship.

### Interoperable read contract

The trusted packaged Node ESM artifact exposes `decodeConfig(bytes)` and `decodeRecord(bytes, {task_path, record_path})`, with shared Python/Node conformance fixtures and explicit declared/legacy/invalid/unsupported outcomes. Its bundled data-only YAML runtime requires no consumer Python installation or execution of viewed-repository code. Minimap owns filesystem discovery/containment, selected-checkout/revision provenance and its disposable reverse index; Work Records remain the only maintained links. Resolver v1 keeps its existing eight-key/8192-byte contract.

SPEC, capture/transition guidance, templates, parser/checker documentation and the packaged distribution shipped together. Consumers refresh the whole skill package and vendored checker as one matched revision; installation does not itself establish natural-use adoption.

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

## Notes

### Shipped and installed — 2026-10-17

- Producer [PR #53](https://github.com/rore/agent-workflow/pull/53) merged at `751ec7bb7399dab6036babae0c15e3d11552e5fc`; independent technical/human result review, all nine local test layers and required CI passed. All review findings were resolved.
- Consumer [Minimap PR #49](https://github.com/rore/minimap/pull/49) merged at `f851e3b6169049a5b1513d2c52c0cddccacd5f17`. Its owner verified the installed shared UI on 4312 using genuine Workflow output, including the feature relationship, recorded state, readable record open/return and actual PR #53 link. Owner-reported screenshots are `artifacts/related-work-rollout-backup-20261017/installed-related-work.png` and `installed-work-record.png` in the Minimap checkout, not the earlier isolated-preview images. This is delivery qualification, not natural adoption evidence.
- Workflow's manager verified matched installations in the source repository, Dictation and Minimap. Pallium's canonical and stable installations remain on a separate owner-managed hold during wake-delivery diagnosis; enterprise installations are excluded under separate ownership. These rollout states do not reopen the shipped producer implementation.
- Capture remains the agent's same normal edit plus exact read-back, not automatic capture or detection of never-received input. Unsupported metadata is disclosed, not silently repaired or treated as confirmed empty.

### Adoption pending

Natural-use evidence starts at **0 observations**. Parent Astra owns the existing daily `check-feature-relationship-adoption` monitor for **2026-10-17 to 2026-10-31 (Asia/Jerusalem)**, with a final assessment on October 31 followed by pause; no duplicate monitor or pre-merge gate is added here.

Target five naturally occurring eligible new/resumed feature assignments across at least two repositories and multiple agents. Link successes and misses here: exact source tuple, actual PR when created, and visibility in the intended Minimap checkout. Cover direct-human and manager-mediated assignments, explicit no-source and unavailable-source cases when they naturally occur. Do not manufacture cases or count historical backfills, lifecycle fixtures, implementation tests or genuine-output/UI qualification as adoption. If traffic is insufficient, record **inconclusive**, not success or a reopened implementation task.
