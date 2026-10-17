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

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** First-phase edits are only a blue-zone Work Record; judgment raises risk for a proposed cross-consumer metadata contract and meaningful compatibility uncertainty. No normative/schema/runtime change is authorized now. Any later contract implementation must be separately scoped and reclassified against SPEC/schema red zones before edits.

**Discovery:** Parser already supports optional strict JSON fields on both shapes and exact duplicate-key rejection; baseline.source is immutable free text, not relationships. LocalBackend owns configured path containment and prose-preserving writes. Resolver v1 returns identity/path/state only, has an exact eight-key 8192-byte contract, and must remain unchanged. There is no structured source/PR creation input today: agents copy templates and edit records. Minimap is an existing dependency-free Node ESM runtime with JSON roadmap config and a purpose-specific frontmatter parser, not an evidenced general Workflow YAML reader. Portable config decoding is therefore a real agreement decision, not solved by saying JSON.parse. Existing parser, resolver, package and configurable-layout tests provide seams; see proposal/evidence below.

**Material assumptions:** An optional Relationships JSON field fits existing parser/renderer ownership; shared fixtures and review must validate field extraction, including comment-like text inside JSON strings. A Workflow-owned portable reader can fit Minimap's existing trusted package, but full configured-location/YAML compatibility is not yet established: Minimap must confirm its supported decoding path or the managers must explicitly settle that limitation before adoption. No Python subprocess, second maintained export, regex guess at general YAML, or implicit dependency is accepted as a substitute. Current phase permits proposal only, not normative adoption.

**Plan:** Return the concrete field/read/capture proposal below with source evidence and the unresolved portable configuration binding. The workflow manager coordinates one agreement with Minimap/Astra; no parallel competing format or product code now. After agreement, separately scope SPEC-first normative work, reclassify contract/schema risk, establish implementation plan/verification and required reviews/approvals, then implement parser/render/capture/read/package surfaces together. This first phase stops at the planning handoff.

**Verification plan:**
- Proposed source identity, Work Record provenance, PR multiplicity and compatibility -> concrete samples compared against existing parser/creation evidence and authoritative requirements.
- Portable passive consumption, natural capture and many-related-work semantics -> trace minimal producer/consumer paths and list bounded scenario checks and unresolved decisions for cross-manager agreement.
- Canonical baseline, classification and isolation before discovery -> first record commit plus genuine reporter/checker result and unchanged shared-root branch/head/hooks evidence.
- Shared agreement before implementation -> manager handoff with exact feature/Work Record/revision; independent contract review follows agreement, not a self-approved format.

**Plan review:** Pending shared proposal and agreement; no implementation approved.

**Approvals:** Not required for this Elevated proposal phase. Product contract/schema implementation is not approved by this record.

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

## Contract proposal — not agreed or normative

Recommend one optional `Relationships` strict-JSON field inside the existing Work Record marker block. It is separate from Requirement baseline and is the sole maintained relationship data. Example below is illustrative metasyntax, not actual provider references or a PR created by this task:

```text
**Relationships:**
{"schema_version":1,"sources":[{"provider":"minimap","scope_ref":"<exact provider-returned namespace>","local_ref":"<exact provider-returned item identity>","url":null}],"pull_requests":[{"provider":"github","host":"github.com","repository":"rore/agent-workflow","number":53,"url":"https://github.com/rore/agent-workflow/pull/53"}]}
```

| Case | Proposed semantics |
|---|---|
| Supplied source | Exact `(provider, scope_ref, local_ref)` tuple; for Minimap copy CLI values verbatim. No case-folding, Unicode normalization, title/substring matching or reconstructing missing parts. `url` is optional safe navigation only, never identity. Other source providers use their authoritative namespace/item pair, not Minimap-specific parsing. |
| Deliberate no source | `sources: []`, only when known. |
| Unverified source | `sources: null`; absence of a supplied item alone must not silently manufacture a declaration. |
| Legacy | Missing Relationships remains parseable; read as legacy/unknown, never authoritative empty sources or PRs inferred from prose. |
| PR references | Zero/many exact hosting-provider, host, repository and positive provider-owned PR number/ID tuples; example GitHub tuple uses provider-supplied canonical repository name and number. Other host/provider shapes must be agreed explicitly, not guessed from a display URL. `pull_requests: []` means no recorded links, not proof that no PR exists. |
| Duplicates/invalid/future | Reject duplicate exact identities and JSON keys, malformed types, unsupported schema versions, unsafe navigation URLs and unsafe paths. Preserve existing bytes; do not repair or truncate silently. Unknown metadata stays unknown. |
| Relationship edits | Add/change/remove explicitly in this field; never rewrite baseline, retain duplicate backlinks, poll PR status, or infer feature completion. |

Keep canonical `agent-workflow:<slug>` unchanged. Derive location from the selected checkout's configured `taskPath`, not a stored second path, current branch when an identity is supplied, common Git directory or newest-record search. Do not store mutable checkout/state/version copies inside Relationships. Read results bind the record to selected checkout/source context, actual Git revision where available, and hashes of the exact config/record bytes; changed dirty bytes remain distinguishable even at the same HEAD. Separate conflicting worktree versions instead of merging links.

### Passive read surface and open agreement decision

Preserve the exact resolver-v1 command/result/limits. Add a separately negotiated relationship-read operation owned by Workflow, not extra keys silently added to v1. Proposed result: contract name/version, found/absent/invalid/unsupported/legacy outcome, canonical Work Record ref, configured relative path, observed record title/state (not proof of readiness/delivery), selected source/revision/content provenance, and validated relationship data. A malformed/oversized result is an explicit outcome, not an empty related-work list.

Preferred portable packaging candidate: a small Workflow-owned Node ESM data reader included in Minimap's existing trusted distribution and covered by the same conformance fixtures as the Python parser/resolver. Minimap must not implement its own independent Markdown parser, run a reader supplied by the inspected repository, add Python for rendering, maintain JSON sidecars/backlinks, or dynamically load repository code. The owner reader needs only the documented metadata/read profile, not a duplicate workflow checker; full validation/readiness remains Workflow's existing checker. Shared marker/field/JSON extraction must have one documented owner/grammar and conformance evidence, including duplicate markers/fields/JSON keys and comments inside string values.

**Unresolved before agreement:** Minimap currently reads `roadmap.config.json` and limited frontmatter, while Workflow uses PyYAML `safe_load` plus schema validation for `agent-workflow.yaml`. The concrete portable decoder/locator binding must support the agreed configured layouts without silently treating a hand-written subset as all valid YAML. Minimap must confirm a safe existing decoding mechanism, or both managers must explicitly agree a documented unsupported-config outcome/compatibility boundary or another allowed transport. A new YAML parser/dependency, mirrored configuration/export to maintain, Python fallback required for display, or hardcoded default location is not approved here. The preferred module is a proposal, not evidence that this compatibility problem is already solved.

Keep Workflow's read operation per known record; Minimap owns discovery, reverse lookup, cache generations and feature paging. Each read/field has an agreed finite byte limit and an explicit overflow outcome, never silent truncation; propose 64 KiB relationship data initially, to be agreed with Minimap before code. Do not impose an arbitrary feature-wide record count. Feature pages should use Minimap's existing immutable cache/snapshot generation with stable ordering and an opaque continuation tied to source/generation; if invalidated, report refresh-required rather than mixing pages. Distinguish canonical records from checkout versions, relationship count from unique PR count, and incomplete discovery from zero matches. No per-PR remote query is needed. Human-facing title/recorded state and clear record-to-PR grouping come first; IDs/provenance are details.

### Natural capture, not another backlink ritual

There is no trustworthy structured creation-input API today. Integrate relationship arguments/expected-reference checks into the owning Work Record creation/write/transition surface instead of inventing a second registry. When source input already exists, the normal record write stores it and compares exact expected tuples; PR creation/linking uses the authoritative PR result in the same existing transition update. Agent guidance must route supplied references to this normal action, not ask humans for a separate backlink edit. A check with no trustworthy expected input reports unverified; it cannot claim to detect a reference never supplied to it or infer identity from chat/prose. Decide the smallest CLI/library entry point after agreement; no new ceremony or evidence file merely for comparison.

### Existing evidence and subsequent implementation surfaces

- `core/work_record/parser.py:244` optional JSON pattern; `:307` single marker-block extraction; `:350` field extraction; `:369` existing comment removal needs care to preserve comment-like bytes inside relationship JSON strings; `:538` strict JSON duplicate-key handling; `:974` render seam. Both shapes and round trips already exist.
- `core/work_record/local_backend.py:54` slug safety, `:74` taskPath validation, `:122` read, `:128` write/prose preservation, `:161` configured resolution/containment. Reuse this owner; two configured layouts are required.
- `core/checker/checker.py:892` exact v1 result, `:918` supplied-ref authority, `:935` configured backend, `:1033` bounded output. Existing resolver clients must not change meaning.
- `core/config/loader.py:139` YAML decoding and `:189` configured taskPath; current consumer runtime evidence: Minimap `package.json` is Node ESM with no production dependencies, `package/minimap/src/roadmap.js` owns JSON config/limited frontmatter, and `package/minimap/src/pallium.js` returns exact scope/local reference pairs. These were inspected as data through GitHub; no consumer code was run.
- Follow-up scope after agreement: SPEC first, optional parser/renderer field, write/capture/checker read surface, trusted portable owner reader/packaging and shared conformance fixtures, both templates/transition guidance/public/package mirrors. Normative SPEC/schema changes imply High-risk reclassification and the corresponding reviews/approval; this phase does not grant them.
- Proposed checks: supplied reference preserved/dropped/changed; add/remove/multiple/no-source/legacy; same IDs in distinct providers/repos, Unicode/spaces and similarly numbered PRs; malformed/duplicate/future/oversized input; safe URLs/paths/symlinks and two taskPath layouts; dirty and conflicting worktree versions; old resolver exact output; non-Python trusted packaged consumer with no inspected-code execution; one large feature with many records/PRs and snapshot invalidation between pages. Minimap owns actual browser/refresh/performance acceptance, including finding recent and older evidence. Reuse existing parser/backend/resolver/package fixtures; do not build a generic indexing or state framework.

### Handoff

The first proposal is ready for workflow-manager/Minimap/Astra discussion, not approved implementation. Portable config binding and final limits/handshake remain explicit decisions. Workflow manager owns canonical feature progress and returns agreement before a separately reviewed implementation plan. No product files changed; no tests or synthetic load run. Current branch and canonical record are above; the next action is manager contract reconciliation, not coding.

## Result review

Pending shared-format agreement and subsequent review; no implementation result is claimed.
