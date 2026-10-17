# Work Record source relationships — contract proposal

Source feature: https://github.com/rore/agent-workflow/blob/main/roadmap/features/add-work-record-source-relationships.md

Combined authority: https://github.com/rore/rore-collection/blob/main/plans/feature-related-work.md

Assignment: `relay-msg-02b8bdaef9044184b7955123fe0dc2b4` from workflow manager. Direct human authorization verified in `astra reviewer`, thread `01a07bef-18c8-71b2-89ab-c0cbe91e73ad`, user item `01a1493a-c390-78f3-bd9b-212e89384d36`; later user items `01a1493c-30df-7883-947a-cfecfcf43d3e` and `01a1493d-12e5-70c2-b190-66cc342c809e` require a simple useful human flow and many Work Records/PRs per feature. This is the first proposal phase, not product implementation or completion of the feature. Workflow manager owns roadmap progress and cross-manager/Minimap/Astra agreement. Provider work references have not been supplied or resolved; none is invented.

<!-- agent-workflow:start -->
**Outcome:** Provide the workflow manager one concrete minimal portable source-relationship contract proposal so Workflow and Minimap can agree how a human finds a feature's related Work Records and PR evidence before implementation.

**Target:** agent-workflow.

**Scope:** First-phase canonical Work Record, bounded read-only inspection of existing parser/creation tooling and authoritative requirements, and a concrete contract sample plus consumer read/compatibility proposal recorded in this same Work Record. No product implementation.

**Constraints:** Agree one shared format through the workflow manager, Minimap and Astra before product implementation; no competing format, new registry, speculative framework, duplicate backlinks, export maintenance, mandatory Python/new dependency for Minimap display, or execution of viewed repository code. Reuse exact provider references; never invent identity or equate recorded state with verified delivery. Preserve existing records, owner-managed roadmap/checkouts, unrelated work, live environment, global/consumer installs, configuration and hooks. Capture supplied references naturally where supported rather than adding a remembered manual task. Do not implement or merge product/schema/runtime changes in this phase.

**Completion criteria:** The manager receives a concrete proposed representation and existing-code evidence covering exact provider source identity, Work Record identity and version provenance, zero/many PR links, explicit no-source versus legacy unknown, automatic capture points, and a portable passive read path. The proposal addresses one feature with many Work Records/PRs, unique PR versus relationship counts, bounded stable/version-aware reads without silently claiming completeness, and useful human feature-to-record/PR navigation. Compatibility, trust boundaries, affected surfaces, open decisions and proposed checks are explicit; implementation remains pending cross-manager/Minimap/Astra agreement and subsequent applicable reviews.

**Requirement baseline:**
{"source":"codex-user:01a1493a-c390-78f3-bd9b-212e89384d36","outcome":"Provide the workflow manager one concrete minimal portable source-relationship contract proposal so Workflow and Minimap can agree how a human finds a feature's related Work Records and PR evidence before implementation.","scope":"First-phase canonical Work Record, bounded read-only inspection of existing parser/creation tooling and authoritative requirements, and a concrete contract sample plus consumer read/compatibility proposal recorded in this same Work Record. No product implementation.","constraints":"Agree one shared format through the workflow manager, Minimap and Astra before product implementation; no competing format, new registry, speculative framework, duplicate backlinks, export maintenance, mandatory Python/new dependency for Minimap display, or execution of viewed repository code. Reuse exact provider references; never invent identity or equate recorded state with verified delivery. Preserve existing records, owner-managed roadmap/checkouts, unrelated work, live environment, global/consumer installs, configuration and hooks. Capture supplied references naturally where supported rather than adding a remembered manual task. Do not implement or merge product/schema/runtime changes in this phase.","completion_criteria":"The manager receives a concrete proposed representation and existing-code evidence covering exact provider source identity, Work Record identity and version provenance, zero/many PR links, explicit no-source versus legacy unknown, automatic capture points, and a portable passive read path. The proposal addresses one feature with many Work Records/PRs, unique PR versus relationship counts, bounded stable/version-aware reads without silently claiming completeness, and useful human feature-to-record/PR navigation. Compatibility, trust boundaries, affected surfaces, open decisions and proposed checks are explicit; implementation remains pending cross-manager/Minimap/Astra agreement and subsequent applicable reviews."}

**Behavior changes:**
[]

**Risk:** High

**Complexity:** Moderate

**Reason:** The next implementation touches normative docs/SPEC.md and a trusted cross-consumer metadata/runtime contract: High risk, Moderate complexity, architecture-review checkpoint. Only this Work Record planning/approval packet may change until independent smart review and the exact human plan/capture-adjustment approval are recorded. Current Task Context remains the proposal baseline; no product implementation is authorized by agent contract acceptance alone.

**Discovery:** Parser already supports optional strict JSON fields on both shapes and exact duplicate-key rejection; baseline.source is immutable free text, not relationships. LocalBackend owns configured path containment and prose-preserving writes. Resolver v1 returns identity/path/state only, has an exact eight-key 8192-byte contract, and must remain unchanged. There is no structured source/PR creation input today: agents copy templates and edit records. Minimap is an existing dependency-free Node ESM runtime with JSON roadmap config and a purpose-specific frontmatter parser, not an evidenced general Workflow YAML reader. Portable config decoding is therefore a real agreement decision, not solved by saying JSON.parse. Existing parser, resolver, package and configurable-layout tests provide seams; see proposal/evidence below.

**Material assumptions:** Accepted contract 60111d4 is fixed; the implementation packet below proposes js-yaml's published self-contained Node ESM with bounded library parsing and a small cycle check. Static package evidence is not runtime safety/parity proof: failed focused fixtures or an unexpectedly broad closure stop implementation and return to planning. Agent-edit capture is an explicit first-slice limitation requiring task-owner approval, not equivalent automatic capture. Minimap owns filesystem containment, provenance, reverse index, paging and UI; its unverified checks are never claimed here.

**Plan:** Prepare and independently review the Current implementation approval packet below, including exact proposed Task Context replacements, the integrity correction, concrete SPEC-first targets, safe bundled Node dependency, focused shared fixtures and earliest decoder handoff. Workflow manager is the single human approval requester. The conditional implementation sequence may begin only after the exact missing human approval; preserve resolver v1 and all live installations. No additional format proposal round is required.

**Verification plan:**
- Proposed source identity, Work Record provenance, PR multiplicity and compatibility -> concrete samples compared against existing parser/creation evidence and authoritative requirements.
- Portable passive consumption, natural capture and many-related-work semantics -> trace minimal producer/consumer paths and list bounded scenario checks and unresolved decisions for cross-manager agreement.
- Canonical baseline, classification and isolation before discovery -> first record commit plus genuine reporter/checker result and unchanged shared-root branch/head/hooks evidence.
- Shared agreement before implementation -> manager handoff with exact feature/Work Record/revision; independent contract review follows agreement, not a self-approved format.

**Plan review:** Pending independent clean-context smart technical/architecture review of the Current implementation approval packet below. Astra accepted contract 60111d4; that is not this plan's review or human approval.

**Approvals:** Pending exact human approval of the reviewed High-risk implementation plan and task-context/capture requirement changes. Workflow manager confirmed no such specific verified approval exists and will be the sole requester. Existing user authorization covers coordination, format-first work and this approval preparation; Astra agent acceptance is not human approval. Separate High-risk result review and architecture-review checkpoint remain required before merge.

**Exceptions:** —

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

2026-10-17 accepted the distinct proposal-only assignment. Applicability is normal workflow: the intended canonical Work Record is explicitly non-exempt, and the request includes implementation planning. Prior PR51 is complete. This baseline precedes product discovery or design. Isolated branch `feat/work-record-source-contract` starts at main `98353e8b51f2cc51a7d21c73cdfb3b2a2adcaaf2`; identity `agent-workflow:work-record-source-contract`, path `.agent-workflow/tasks/work-record-source-contract.md`. Blocked names the unestablished proposal/agreement gate, not missing task authorization. Next: inspect existing source/creation/read surfaces and return the first proposal to the manager only.

The shared root remains on `feat/requirement-baseline-history` at `98353e8b51f2cc51a7d21c73cdfb3b2a2adcaaf2`, only original `.codex/hooks.json` dirty, SHA256 `6B9A5ED80441142646E3E634B4F768E0C2D930F71AEBDB4B055B066165C5CC1E`. The existing roadmap-only temp checkout/branch is not reused or changed. No everyday or consumer installation/configuration changes are authorized or made.

## Evidence

Pending initial genuine state check. No product files inspected or changed before this baseline. Manager acceptance send `relay-msg-dab79a57abba466197e969f2b1af807d` was saved/pending; this is not confirmed recipient receipt. No manual receive/ACK or resend of the queued assignment.

Initial genuine state check at `12fc749b561b494f57efbc7688b2558b91bbcac3`: reporter 0/BLUE, checker 2; only blocking predicate is the missing Elevated independent technical plan review (chunk 39c26b). Baseline and marker structure passed. That is the expected unestablished review gate, not a passing readiness claim or product failure. State remains Blocked for agreement/review, with proposal work permitted and product implementation prohibited.

Read-only inventory `/root/source_contract_facts` inspected parser/backend/resolver/creation seams; no edits, tests or consumer code execution. Its Git status invocation could not recognize the worktree; parent independently confirmed exact checkout/clean identity at `12fc749` (403bd0), so no cleanliness claim rests on that failed child invocation. Parent inspected the actual source excerpts and authoritative collection plan. No Minimap skill/CLI exists at the three conventional installed skill locations checked (9b1ea0); no provider scope/local pair was supplied or fabricated, so optional association is unavailable and skipped. Workflow manager retains the authoritative roadmap-update obligation; pickup/proposal progress is reported to that owner, not edited in a shared checkout.

## Revised contract proposal — pending joint review

Same proposal, revised after Astra's direction review of `4ad1a889` and Minimap's consumer acceptance. One optional `Relationships` strict-JSON field inside the existing marker block; immutable Requirement baseline is unchanged. The sample is illustrative metasyntax, not a real source reference or PR created by this task:

```text
**Relationships:**
{"schema_version":1,"sources":[{"provider":"minimap","scope_ref":"<exact provider scope_ref>","local_ref":"<exact provider local_ref>"}],"pull_requests":["https://github.com/rore/agent-workflow/pull/53"]}
```

| Case | Proposed semantics |
|---|---|
| Supplied source | Exact `(provider, scope_ref, local_ref)` tuple; for Minimap copy CLI values verbatim. No case-folding, Unicode normalization, title/substring matching or reconstructing missing parts. `url` is optional safe navigation only, never identity. Other source providers use their authoritative namespace/item pair, not Minimap-specific parsing. |
| Deliberate no source | `sources: []`, only when known. |
| Unverified source | `sources: null`; absence of a supplied item alone must not silently manufacture a declaration. |
| Legacy | Missing Relationships remains parseable; read as legacy/unknown, never authoritative empty sources or PRs inferred from prose. |
| PR references | Zero/many validated canonical GitHub PR URLs, initially `https://github.com/<owner>/<repo>/pull/<positive-number>`. Workflow's one published rule lowercases GitHub host/owner/repository for identity/deduplication and uses canonical positive decimal PR numbers; it does not normalize source tuples. Reject credentials, ports, query/fragment, encoded/unsafe paths, unsupported hosts and non-PR URLs. No redundant stored host/repository/number fields or live API polling. `pull_requests: []` means no recorded links, not proof that no PR exists. Other hosts need explicit supported-host agreement. |
| Duplicates/invalid/future | Reject duplicate exact identities and JSON keys, malformed types, unsupported schema versions, unsafe navigation URLs and unsafe paths. Preserve existing bytes; do not repair or truncate silently. Unknown metadata stays unknown. |
| Relationship edits | Add/change/remove explicitly in this field; never rewrite baseline, retain duplicate backlinks, poll PR status, or infer feature completion. |

Keep canonical `agent-workflow:<slug>` unchanged. Minimap binds the decoded configured `taskPath` to its explicitly selected checkout, applies its existing containment/reparse-point checks and supplies source/version context. It must not use the common Git directory, branch fallback for an already known identity, or newest-record search. Do not store second path/state/checkout copies in Relationships. Minimap's existing read context carries checkout/source key, Git revision where available and config/record content hashes; dirty or conflicting versions remain distinct even at the same HEAD. These are observed versions, not proof of delivery or activity.

### One trusted decoder, not another CLI

Preserve resolver-v1 command/result/limits. No second relationship-read command, export, service, registry or locator. One Workflow-owned Node ESM decoder, shipped with the existing trusted Minimap distribution, accepts data bytes rather than repository paths or executable callbacks. Minimal API for agreement:

```text
decodeConfig(configBytes) -> {status: ok, task_path} | {status: invalid|unsupported, reason}
decodeRecord(recordBytes, {task_path, record_path})
  -> {status: declared|legacy, work_record_ref, title, recorded_state, relationships}
   | {status: invalid|unsupported, reason}
```

`decodeConfig` validates the supported config version and local-backend/taskPath contract once per config revision; unsupported backends do not fall back to local. `decodeRecord` receives the already decoded template and candidate's configured repository-relative lexical path as DATA, validates their slug/ref mapping using Workflow's existing rules, and uses the same owned marker/field/JSON grammar as the Python parser. This avoids a second Minimap record-identity rule while leaving actual filesystem containment to Minimap. It returns the metadata/read profile, not a duplicate workflow checker or readiness verdict. Missing files/configuration are Minimap filesystem outcomes, not invented empty byte strings. Invalid/unsupported/oversized metadata is explicit, never an empty related-work list. Minimap owns filesystem I/O and containment, selected source/path binding, discovery, provenance, reverse lookup, cache generations and paging. Workflow owns the stored grammar, both language adapters' semantic conformance and fixture expectations. Neither decoder opens paths, executes viewed-repository code or imports a module chosen by repository data.

Locator/decoder choice: use the configured taskPath returned by the owned decoder and Minimap's existing contained-file/snapshot facilities. Bundle pinned `yaml` 2.9.1 with the Workflow-owned trusted decoder; do not write a YAML parser or ask users to run npm/install Python. Minimap manager owns the completed package comparison, relayed by workflow manager: `yaml` 2.9.1 is ISC, no dependencies, Node >=14.6, 686,297 bytes for the WHOLE unpacked published package. Alternative `js-yaml` 5.5.0 is MIT, 1,626,579 unpacked bytes plus `argparse ^3.0.3`. These are owner-reported official npm figures, not a locally measured runtime bundle or a claim of complete behavior parity. Sources: https://registry.npmjs.org/yaml/2.9.1 and https://eemeli.org/yaml/ . Reuse that evidence rather than repeating package research. Preserve pinned version and license/redistribution notices in the trusted distribution; use existing packaging and measure actual shipped size there, without inventing trimming machinery. Zero new consumer installation step and zero inspected-repository code execution remain hard constraints.

Supported configuration profile for joint review: a single data-only mapping document with the current relevant `workRecord.backend`/`workRecord.local.taskPath` types and existing slug/template constraints; block/flow mappings, quoted/plain strings and bounded anchors/merge under explicit YAML 1.1-compatible scalar rules. Boolean/null/numeric values are not valid taskPath strings. Explicit mapping keys override merged keys as in the supported PyYAML cases. Reject duplicate explicit keys, cycles, parser errors and alias expansion beyond a finite budget (propose 100); allow only agreed safe standard data tags and reject unsupported/custom tags. YAML 1.1 mode alone does not establish parity. Shared fixtures must check these cases against current PyYAML and document deliberate narrower outcomes, especially duplicate keys/tags/alias limits. Outside this profile return invalid/unsupported with a reason, never a guessed default location, empty relationship set or fallback execution; ordinary board/Workflow operation remains usable. This defines a bounded metadata-reader profile, not a change to the ordinary Python config loader.

Correctness gate before implementation: Minimap/Workflow must accept the exact supported subset and shared expected outcomes, not just the library/version. A disagreement affecting configured record selection, scalar types or merge precedence is a blocker for the reviewed contract. No broad PyYAML parity or already-tested compatibility is claimed by this proposal; aliases/tag/duplicate-key cases are mandatory implementation conformance checks.

Strict-byte fixture refinements accepted by Minimap: both decoder inputs are raw bytes and must reject malformed UTF-8, never replace invalid bytes before identity comparison. Duplicate JSON keys are compared after JSON escape decoding: for example `{"a":1,"\u0061":2}` is invalid, not two independent keys or last-key-wins. Preserve both cases in shared source/trusted-package fixtures. These refine the existing exact-byte/strict-JSON contract; no new API or review phase.

The provisional 64 KiB UTF-8 limit applies to Relationships JSON only, NOT the whole Work Record; overflow is explicit, never truncation. Many records/PRs per feature remain a core case with no arbitrary feature-wide cap. Minimap alone defines bounded snapshot paging, stable ordering, invalidation and incomplete/loading/stale/error presentation. Distinguish canonical records from checkout versions and unique PR counts from relationship counts; no per-PR remote query. Human-facing title/recorded state and record-to-PR grouping come first; identity/provenance are details.

### Capture is the normal agent edit

| Existing action | Exact smallest relationship edit |
|---|---|
| Create Work Record from template | In the SAME initial file edit as Task Context/baseline, add Relationships and copy supplied exact source tuples. Use `[]` only for known no-source, otherwise `null`; copy known supported PR URLs or start the recorded PR-link list empty. |
| Pickup/resume/handoff | In the normal record update, preserve existing tuples/URLs; add or correct only authoritative supplied references. Missing legacy field remains unknown unless verified input now establishes it. Never reset a broad source to none or rewrite baseline. |
| PR creation/linking | In the SAME normal record/transition edit, append the validated canonical URL returned by the owning PR tool; preserve unrelated sources/PRs and avoid duplicates. No source-item backlink list or separate capture command. |

This is an agent-performed edit and read-back comparison with the references supplied to that task, not an automatic capture API. Decoder/checker validate stored syntax, identities, URLs and duplicates. A trustworthy expected-reference input already available to a calling/verification flow can be compared there; absent such input, report unverified instead of claiming a dropped-input check ran. Do not scrape chat/prose or create an evidence sidecar merely to make the comparison appear automatic. No additional human backlink task is introduced.

### Existing evidence and subsequent implementation surfaces

- `core/work_record/parser.py:244` optional JSON pattern; `:310` single marker-block extraction; `:349` field extraction; `:368` existing comment removal needs care to preserve comment-like bytes inside relationship JSON strings; `:550` strict JSON load; `:962` render seam. Both shapes and round trips already exist.
- `core/work_record/local_backend.py:55` slug safety, `:74` taskPath validation, `:122` read, `:128` write/prose preservation, `:168` configured resolution/containment. Reuse this owner; two configured layouts are required.
- `core/checker/checker.py:892` exact v1 result, `:918` supplied-ref authority, `:935` configured backend, `:1033` bounded output. Existing resolver clients must not change meaning.
- `core/config/loader.py:139` YAML decoding and `:189` configured taskPath; current consumer runtime evidence: Minimap `package.json` is Node ESM with no production dependencies, `package/minimap/src/roadmap.js` owns JSON config/limited frontmatter, and `package/minimap/src/pallium.js` returns exact scope/local reference pairs. These were inspected as data through GitHub; no consumer code was run.
- Shared conformance fixtures live with Workflow and are consumed unchanged by both language adapters and Minimap's trusted-package test: exact marker/field selection, comments inside JSON strings, duplicate keys/fields/identities including escaped-equivalent JSON keys, malformed UTF-8 rejection without replacement, Unicode/spaces, unknown/null/empty, canonical PR URLs, unsupported versions and Relationships-only byte overflow; relevant safe YAML block/flow/quoted/alias/merge/scalar cases; two configured taskPath layouts with invalid/unsafe inputs. Minimap adds real filesystem containment, cross-worktree/dirty provenance, many-record/PR snapshot paging and UI tests. Minimap owns visible per-source partial/unsupported errors while unrelated valid source snapshots/records remain usable; this is not permission to salvage malformed relationship data or silently claim complete discovery. No broad duplicate parser or new fixture registry.
- Follow-up scope after reviewed agreement: SPEC first, optional parser/renderer field, existing checker validation, trusted decoder/packaging and shared fixtures, both templates/transition guidance/public/package mirrors. Implementing the user-authorized feature then follows actual risk/review/approval gates; no invented approval restart for each clarification, and no runtime/source product edits in this proposal update.
- Proposed checks: supplied reference preserved/dropped/changed; add/remove/multiple/no-source/legacy; same IDs in distinct providers/repos, Unicode/spaces and similarly numbered PRs; malformed/duplicate/future/oversized input; safe URLs/paths/symlinks and two taskPath layouts; dirty and conflicting worktree versions; old resolver exact output; non-Python trusted packaged consumer with no inspected-code execution; one large feature with many records/PRs and snapshot invalidation between pages. Minimap owns actual browser/refresh/performance acceptance, including finding recent and older evidence. Reuse existing parser/backend/resolver/package fixtures; do not build a generic indexing or state framework.

### Handoff

The revised sample/capture/API boundary and owner-reported pinned package recommendation are ready for the same workflow-manager/Minimap/Astra contract review. Minimap accepts the provisional Relationships-only 64 KiB bound. Exact supported configuration outcomes, shared URL/byte fixtures and the actual shipped size/packaging evidence still require the one joint decision/implementation verification. No product files changed, dependencies installed or synthetic tests run. Once the reviewed contract is agreed, proceed with already-authorized implementation under actual repo gates, not another proposal phase.

Last good proposal revision: `3ff4f525a51282a599d3ae63c1822e552b36ac9c` on `feat/work-record-source-contract`; only this record differs from main. Its post-proposal check reports reporter 0 and checker 2, solely the pending Elevated technical plan review (ebd359, independently inspected 9c60ee). Source-citation/handoff prose corrections follow that revision; Task Context/baseline are unchanged. No passing readiness, shared agreement or implementation completion is claimed. Shared root branch/head/status and original dirty-hook hash still match pickup (358586). No consumer/global installation, environment or service changes occurred.

## Result review

Workflow manager forwarded Minimap's acceptance of `60111d4d65f019158e2cf33baba60c14bef213c2` API/ownership boundary and bounded YAML subset for the one consolidated Astra contract decision. The two strict-byte fixture cases above are retained as implementation acceptance, not a new feature/review phase. Minimap reports isolated branch `feat/implement-related-work`, Work Record commit `bb0b280`, no product edits; that is owner-reported planning state, not verified implementation completion. Only the actual contract decision remains outstanding here; no new approval stop is added for these clarifications.

Astra reviewed `4ad1a889` as directionally acceptable, not final contract approval. Workflow manager supplied the corrections and Minimap boundary/package evidence by authorized app fallback on 2026-10-17: one stored JSON grammar/owned decoder, no second CLI/export, canonical supported PR URLs, honest normal agent-edit capture, zero new consumer install steps and no inspected-code execution. The two equivalent clarification entries preserve the immutable baseline and user outcomes while correcting an overbroad dependency mechanism assumption and nonexistent automatic-API implication; the final reviewer must assess that equivalence, not treat the checker as semantic approval. Minimap's YAML package research is not duplicated. Proposal revision `dcb4d99168d40251428828445344e8eb7478bed4` passed baseline/change-chain checks; reporter 0, checker 2 solely the pending Elevated technical plan review (268133). The subsequent API clarification keeps lexical path/ref grammar owned by Workflow and filesystem operations/provenance owned by Minimap; it adds no CLI, export or source execution.

Relay reconciliation reply for original assignment delivery `relay-delivery-546cbb548b014cf7ae9aa93cbb9d5ec5` failed with HTTP503 `service not initialized`; no receive, manual ACK or blind resend. Current substantive updates use the explicitly authorized app fallback, preserving recipient settings. This is delivery failure evidence, not proof of an empty inbox or failed canonical task work.

Pending shared-format agreement and subsequent review; no implementation result is claimed.

## Current implementation approval packet — 2026-10-17

Status: Astra accepted contract `60111d4d65f019158e2cf33baba60c14bef213c2` for implementation through the workflow manager. This resolves the shared-format proposal, not the High-risk human gate. Workflow manager confirmed it has no verified human approval for this specific reviewed implementation plan/capture adjustment and is the **single approval requester**. Product files remain untouched.

### Integrity correction

The two `equivalent` Task Context changes introduced in `dcb4d99168d40251428828445344e8eb7478bed4` were incorrect: making automatic capture an agent-performed edit is a requirement change. They had no human approval and no product implementation occurred under them. This revision restores current Constraints and Completion criteria exactly to their original baseline values and withdraws those unapproved entries from the active chain. The immutable baseline and Git history are unchanged; the original entries and their rationale remain inspectable at that revision, and the earlier Result review paragraph is historical, not the current verdict. No approved chain entry is removed or rewritten. The complete proposed replacement below remains outside the marker block pending exact human approval.

### Exact proposed Task Context replacements (not active)

The before values are the immutable Requirement baseline values; the following entries carry exact before/after values and are all `requirement-change`. They deliberately have **no approval object yet**. After the task owner explicitly approves these values, apply them to current Task Context and the ordered Behavior changes array with the real approval source/verbatim. Never invent an approval to satisfy the checker.

```json
[
  {
    "target": "task-context.outcome",
    "classification": "requirement-change",
    "before": "Provide the workflow manager one concrete minimal portable source-relationship contract proposal so Workflow and Minimap can agree how a human finds a feature's related Work Records and PR evidence before implementation.",
    "after": "Work Records preserve exact supplied source relationships and owning-tool PR links, and a trusted non-Python consumer can read them consistently so a human can find a feature's many related Work Records and PR evidence.",
    "reason": "Advance the completed format proposal into bounded product implementation and delivery under actual repository gates.",
    "impact": "Adds the product implementation phase; automatic capture is not delivered in this slice. Exact supplied-reference preservation and read-back remain required, with no claim to detect absent/unreceived input.",
    "alternatives": "Retain proposal-only scope with no product implementation, or separately design a real automatic capture integration (out of this bounded slice).",
    "authority": {
      "scope": "task",
      "name": "task-owner"
    }
  },
  {
    "target": "task-context.scope",
    "classification": "requirement-change",
    "before": "First-phase canonical Work Record, bounded read-only inspection of existing parser/creation tooling and authoritative requirements, and a concrete contract sample plus consumer read/compatibility proposal recorded in this same Work Record. No product implementation.",
    "after": "Implement the accepted source-relationship contract in the normative SPEC, existing Python Work Record parser/renderer and checker, one Workflow-owned pure Node ESM decoder with its bundled data-only YAML dependency and license, shared conformance fixtures, existing skill/templates/docs and packaged mirrors. Deliver the exact decoder/fixture artifact to Minimap for its separately owned discovery/index/UI integration, then verify and take this Workflow change through review, CI and merge.",
    "reason": "Advance the completed format proposal into bounded product implementation and delivery under actual repository gates.",
    "impact": "Adds the product implementation phase; automatic capture is not delivered in this slice. Exact supplied-reference preservation and read-back remain required, with no claim to detect absent/unreceived input.",
    "alternatives": "Retain proposal-only scope with no product implementation, or separately design a real automatic capture integration (out of this bounded slice).",
    "authority": {
      "scope": "task",
      "name": "task-owner"
    }
  },
  {
    "target": "task-context.constraints",
    "classification": "requirement-change",
    "before": "Agree one shared format through the workflow manager, Minimap and Astra before product implementation; no competing format, new registry, speculative framework, duplicate backlinks, export maintenance, mandatory Python/new dependency for Minimap display, or execution of viewed repository code. Reuse exact provider references; never invent identity or equate recorded state with verified delivery. Preserve existing records, owner-managed roadmap/checkouts, unrelated work, live environment, global/consumer installs, configuration and hooks. Capture supplied references naturally where supported rather than adding a remembered manual task. Do not implement or merge product/schema/runtime changes in this phase.",
    "after": "Use accepted contract 60111d4 and preserve the original Requirement baseline, legacy Work Records, configured layouts, resolver v1's exact eight-key/8192-byte output, unrelated work and owner-managed roadmap checkouts. No new registry, capture service, separate read CLI/export, speculative framework, duplicate backlinks, extra consumer install step, required Python solely for display, or execution of viewed repository code. Bundle a pinned maintained data-only YAML dependency with license and measured runtime footprint. Preserve exact provider/scope/local references; never infer identity or equate recorded state with verified delivery. First-slice capture is the agent's same initial/transition Work Record edit plus exact read-back comparison against supplied references, not automatic input capture; syntax validation cannot prove absent or unreceived references were captured. Preserve live environment, global/consumer installations, configuration and hooks; this task authorizes no live environment changes.",
    "reason": "Explicitly disclose and request approval for first-slice agent-edit capture instead of automatic capture, bundled parser distribution, and the product implementation phase.",
    "impact": "Adds the product implementation phase; automatic capture is not delivered in this slice. Exact supplied-reference preservation and read-back remain required, with no claim to detect absent/unreceived input.",
    "alternatives": "Retain proposal-only scope with no product implementation, or separately design a real automatic capture integration (out of this bounded slice).",
    "authority": {
      "scope": "task",
      "name": "task-owner"
    }
  },
  {
    "target": "task-context.completion_criteria",
    "classification": "requirement-change",
    "before": "The manager receives a concrete proposed representation and existing-code evidence covering exact provider source identity, Work Record identity and version provenance, zero/many PR links, explicit no-source versus legacy unknown, automatic capture points, and a portable passive read path. The proposal addresses one feature with many Work Records/PRs, unique PR versus relationship counts, bounded stable/version-aware reads without silently claiming completeness, and useful human feature-to-record/PR navigation. Compatibility, trust boundaries, affected surfaces, open decisions and proposed checks are explicit; implementation remains pending cross-manager/Minimap/Astra agreement and subsequent applicable reviews.",
    "after": "Both Work Record shapes round-trip the optional versioned Relationships field without changing legacy behavior. Exact supplied source references and returned PR URLs are preserved by the same normal initial/transition edit and verified by read-back where expected inputs exist; missing expected inputs remain explicitly unverified, not claimed automatic capture. Shared Python/Node/package fixtures prove identical supported metadata outcomes, strict bytes/JSON, bounded safe YAML, explicit unsupported diagnostics and two configured layouts without viewed-repository code execution or a Python display requirement. Resolver v1 regression tests remain unchanged. Minimap receives the exact trusted decoder/fixtures revision, public API, dependency/license provenance, focused results and limits for its own many-record/PR and partial-result integration. Full repository checks, independent smart plan/result review, separate applicable human approvals and architecture-review checkpoint, final CI and review threads are clear before merge; broader Minimap UI completion is not claimed by the Workflow PR.",
    "reason": "Explicitly disclose and request approval for first-slice agent-edit capture instead of automatic capture, bundled parser distribution, and the product implementation phase.",
    "impact": "Adds the product implementation phase; automatic capture is not delivered in this slice. Exact supplied-reference preservation and read-back remain required, with no claim to detect absent/unreceived input.",
    "alternatives": "Retain proposal-only scope with no product implementation, or separately design a real automatic capture integration (out of this bounded slice).",
    "authority": {
      "scope": "task",
      "name": "task-owner"
    }
  }
]
```

### Concrete implementation sequence and affected surfaces

1. **After review and human approval only:** update current Task Context/ordered change entries and State in this same record. Edit `docs/SPEC.md` FIRST: optional marker-block Relationships v1, exact identity, nullable/empty/legacy meaning, URL profile, pure decoder profile and limits. Append one rationale to `docs/DECISIONS.md`. SPEC is red and triggers `architecture-review`; there is no reason to add a second JSON schema solely for symmetry with the existing configuration schema. Existing governance/policy/CI/CODEOWNERS stay unchanged.
2. Use existing `core/work_record/parser.py` optional-field/strict-JSON/render seams for both shapes; add a small owned Relationships validator in that package only if it keeps Python validation shared, and export it through `core/work_record/__init__.py` only when a caller needs it. Preserve exact strings, duplicate decoded-key rejection, legacy records and surrounding prose. Fix JSON-field hint-comment extraction at its shared seam so comment-like bytes **inside strings** survive; retain actual template hint compatibility. Existing checker predicates validate new declarations through this owner. Unsupported/future metadata or unsupported legacy PR data yield explicit metadata diagnostics while retaining the exact source data; they must not discard a whole legacy record or break otherwise ordinary Workflow processing. Malformed declared JSON is never silently salvaged.
3. Add `core/work_record/relationships.mjs` with ONLY `decodeConfig(configBytes)` and `decodeRecord(recordBytes, {task_path, record_path})`. Copy the published self-contained Node ESM `js-yaml@5.5.0` artifact to a relative `core/work_record/vendor/js-yaml.mjs` with `LICENSE.js-yaml` and version/provenance notice. No bundler, npm install, runtime downloader, custom module loader, second parser CLI or viewed-repository execution. This is a trusted decoder of supplied data bytes; lexical configured path/ref grammar belongs here, filesystem discovery/containment belongs to Minimap.
4. Shared fixtures under `tests/work-record/fixtures/` feed Python and Node tests, not separately invented expectations. Deliver the decoder, dependency/license/provenance and shared fixtures to Minimap at the earliest **tested commit** after the gates pass, with exact import path/exports, commit and checks/limits. Minimap imports the actual artifact and adds its owned filesystem/worktree/provenance/reverse-index/paging/UI integration; no temporary shim or duplicate parser is authorized.
5. Update existing `core/templates/work-record-routine.md` / `work-record-expanded.md`, and only the relevant establish-context/operating/transition guidance in `core/skill/`; read each affected file and authoring discipline first. Initial creation writes supplied sources in the SAME edit; resume/handoff preserves/corrects them; owning-tool PR creation appends the returned URL in the SAME record/transition edit. Read back and compare exact expected references when supplied. Missing field remains legacy unknown, null means unverified, [] means established none. No extra human backlink task. Public `docs/agent-workflow/` mirrors, generated `dist/agent-workflow/`, manifests and source/package parity tests must reach the same contract.
6. Extend existing `scripts/package-skill.sh` required-path/copy rules to ship the ESM module, relative dependency and license/notice beside the vendored checker; keep existing Python runtime packaging. Validate isolated packaged import from its final relative paths, source/dist equality and license/version. Reinstall repo-local skill mirrors only through the existing scoped script after source edits, inspecting exact targets first; do not touch daily/global/consumer installs or services.
7. Run focused parser/checker/config/Node/package tests, then `bash tests/run-all.sh` with the existing trusted runtimes, fresh reporter/checker and exact revision. Reassess the final diff, independent smart result review, separate required High-risk human result/architecture review, actual PR CI and all inline findings before merge. Do not weaken thresholds or governance to make packaging fit.

### Dependency and safe-data decision to review

Official tarballs were downloaded into ignored `.local/artifact-probe/` only, then statically read (no npm install, package execution, build or global change). Canonical Node `js-yaml@5.5.0/dist/js-yaml.mjs` is self-contained, 130,603 runtime bytes with zero executable imports; MIT license is 1,084 bytes. Three Minimap runtime copies cost **6 runtime/license files and 395,061 bytes**, excluding small owner notice. By comparison `yaml@2.9.1`'s Node index CommonJS closure requires 72 files/287,807 bytes plus ISC license per copy: **219 files/865,635 bytes** across three copies. This actual published runtime closure, not whole npm unpacked metadata, favors js-yaml; do not change Minimap's >80-file rule or add a bundler.

Pinned js-yaml tarball: `https://registry.npmjs.org/js-yaml/-/js-yaml-5.5.0.tgz`; downloaded SHA512 matched SRI `sha512-paNr4LFIFPjeeSmwNYdrb8FafLLG/Cr2Af3GjbsHJ5CxIjH4r0c2emlmRdAtpPAieP1gRVzk6buBbVP5gBMGAg==`.

Proposed metadata-only YAML profile: fatal UTF-8 decode, **64 KiB config-input byte cap** (separate from the 64 KiB Relationships-value cap, NOT a whole-record cap); one data mapping/document, explicit-key duplicates rejected, unknown custom tags rejected, YAML 1.1-compatible safe scalar behavior supported only as fixed by shared fixtures. Use published library options `maxDepth: 100`, `maxAliases: 100`, `maxTotalMergeKeys: 10000`, with its safe YAML 1.1 schema. js-yaml materializes aliases by reference, not expanding/cloning them; merge work is library-bounded. A small active/visited object traversal rejects cycles after construction and visits shared nodes once; it is not a YAML parser, framework, serialized expansion or custom alias resolver. Bound unique visited objects at 10,000 as a final defense. Static evidence proves the options/reference semantics, not actual behavior: focused tests must verify limits, duplicate/merge override behavior and YAML/Python metadata parity before accepting the artifact. If these guards need more than the small traversal or incompatible semantics, STOP and report a concrete decision; do not silently reject all aliases or invent broad PyYAML parity.

`decodeConfig` verifies the metadata profile and required `version`, `workRecord`, `backend`, `local`, `taskPath` and exact types before returning the lexical path template. Missing fields have no guessed default. Unsupported version/backend/profile is explicit; `ok` is NOT whole-Workflow configuration validity. `decodeRecord` takes fatal-decoded bytes, validates one strict marker block and fields, exact lexical ref/path/state/title/Relationships data and UTF-8 Relationships budget. Keep v1 resolver's eight keys/8192 bytes completely unchanged.

Initial PR profile is canonical HTTPS GitHub pull URLs, with host/repository/number encoded only in the URL; canonical case-equivalent GitHub duplicates are rejected/avoided, source tuple equality is exact and never normalized. The implementation must distinguish invalid newly declared data from unsupported metadata in older records with exact retained sources and explicit diagnostics, not erase old records/links to force the narrow profile. Freeze precise result-object diagnostics in shared fixtures before the artifact handoff; preserve the accepted public API/status shape rather than add a parallel API. No network calls or PR-status polling.

### Verification matrix and ownership

| Observable requirement/risk | Focused evidence |
|---|---|
| Both shapes/legacy remain readable; exact source strings/prose survive | Shared fixture Python parse/render/LocalBackend round trips; absent/null/empty/many, Unicode/spaces, comment-like strings, duplicate field/key including escaped-equivalent JSON keys, malformed UTF-8, unsupported schema and Relationships-only byte boundary. |
| Supplied references/owning-tool URLs survive the actual agent edit | Fixture-backed initial/resume/handoff/PR edit and exact read-back comparison for preserved, dropped and changed expected input; mark absent expected input unverified. This validates the edit/check procedure, NOT automatic capture of all incoming references. |
| Metadata profile reads configured records without guessed defaults or unsafe YAML | Same byte fixtures in Python metadata reference tests and trusted Node: block/flow/quoted/plain, YAML 1.1 scalar cases, bounded anchors/merge, explicit duplicate keys, multiple docs/custom tags, malformed UTF-8, cycles, alias/depth/merge/config-byte overflows, required fields/types and unsupported version/backend. |
| Paths/identity are lexical data, with no fallback/execution | Existing slug/template tests ported as shared fixtures, two configured layouts, Unicode/spaces, abs/drive/dotdot/control/reparse/symlink escapes. Node tests lexical rejection; existing backend + Minimap own real filesystem containment tests. No source imports from the viewed repo. |
| Existing callers keep their contract | Existing parser/backend/checker tests plus resolver v1 exact eight-key/8192-byte, supplied-ref authority and no branch fallback regression tests unchanged; diagnostics cannot invalidate unrelated valid records. |
| Actual trusted package works without Python or install steps for display | Isolated final packaged ESM import with relative vendored dependency; compare shipped bytes/version/license/exports; consumer receives exact revision and fixtures; Minimap verifies all three runtime mirrors and partial/unsupported UI with many records/PRs. Workflow does not claim Minimap-owned checks passed. |
| Cross-repo acceptance and merge are evidenced, not inferred | Focused artifact handoff first; full 9-layer repo suite, source/dist/mirror checks, fresh genuine reporter/checker, exact-head independent smart result review, human gates, PR CI and resolved review threads. Recorded state is never proof of delivery/merge. |

### Stop conditions and approval handoff

A material format/API change returns to the owner, not a private second parser. Failed alias/merge safety/parity, unexpectedly broad package closure, missed existing caller compatibility, consumer-required runtime installation or any need to execute viewed code returns to planning. No governance thresholds or live installation may be changed under this task.

Pending: independent smart technical/architecture review of this exact packet (including integrity correction and capture adjustment), then workflow manager presents ONE combined human decision with the reviewed revision and exact replacement values. State remains Blocked; no product implementation or ready-for-implementation claim. Minimap can continue its own authorized planning, not substitute a speculative decoder. Human implementation approval must be separately evidenced from Astra's contract acceptance and from the later High-risk result review.

