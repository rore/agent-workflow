# markers-broken — checker fixture

Work Record exists but the marker block is unterminated (missing the
end marker). `workrecord.exists` passes; `workrecord.markers_present`
fails with a parse-error detail; field and state predicates fail with
"skipped — Work Record could not be parsed."
