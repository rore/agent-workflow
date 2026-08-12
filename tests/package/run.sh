#!/usr/bin/env bash
# tests/package/run.sh
#
# Layer entry point invoked by tests/run-all.sh. Runs all four package
# checks in order — cheapest first, most expensive last. Each one
# catches a class of failure the previous ones cannot:
#
#   check-package.sh         — committed dist/ matches what the
#                              packager produces (drift detection)
#   check-references.sh      — every internal markdown reference in
#                              the dist resolves inside the dist
#                              (completeness)
#   check-install-probe.sh   — required-file manifest, frontmatter,
#                              and script invokability (sanity)
#   check-e2e-bootstrap.sh   — full mechanical bootstrap into a temp
#                              consumer repo, ending in the Phase 6
#                              self-probe checker run (end-to-end)
#
# Any failure short-circuits the layer.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$HERE/check-package.sh"
bash "$HERE/check-references.sh"
bash "$HERE/check-install-probe.sh"
bash "$HERE/check-e2e-bootstrap.sh"
