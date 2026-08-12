# expanded-incomplete — checker fixture

Record correctly declares `(Elevated, Moderate)` — so the expanded
shape is expected — but the Discovery field is missing. The parser
rejects the record with a `missing required expanded-path field(s):
Discovery` error. The checker surfaces this through the markers /
fields predicates.
