# shape-mismatch-elevated-as-compact — checker fixture

Marker block is well-formed and carries every routine field. But it
declares `Risk: Elevated` — and `(Elevated, Simple)` demands the
expanded shape. The parser routes to the expanded validator, finds
the expanded-only fields missing, raises `WorkRecordParseError`. The
checker surfaces that as the named predicate
`workrecord.shape_matches_classification = false` so a reviewer reads
"shape mismatches classification" rather than digging through the
markers / fields detail.
