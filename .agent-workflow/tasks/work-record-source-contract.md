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

**Discovery:** Pending. Task Context, exact baseline and provisional classification are established before reading product code.

**Material assumptions:** Existing Work Record/parser/creation surfaces can support one passive portable representation without consumer runtime coupling; discovery may disprove this and must report the smallest alternative. Current phase permits proposal only, not adoption of a normative contract.

**Plan:** Pending bounded discovery and the manager's shared-format agreement process. No product implementation may begin from this provisional record.

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

## Result review

Pending shared-format agreement and subsequent review; no implementation result is claimed.
