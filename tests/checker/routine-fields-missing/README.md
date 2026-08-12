# routine-fields-missing — checker fixture

Marker block is well-formed but the `Target` field has been omitted.
`workrecord.exists` and `workrecord.markers_present` pass;
`workrecord.routine_fields_present` fails with a parse-error detail
explaining which field is missing.
