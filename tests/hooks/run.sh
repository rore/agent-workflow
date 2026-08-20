#!/usr/bin/env bash
# tests/hooks/run.sh — deterministic tests for the agent-workflow Claude Code hooks.
# Exercises the decision function of check-plan (gate) plus the seed/reinforce
# JSON output and fail-open behavior. Offline; no network, no jq.
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
H="core/skill/hooks"

if [[ -n "${PYTHON:-}" ]]; then PY="$PYTHON"
elif command -v python  >/dev/null 2>&1; then PY=python
elif command -v python3 >/dev/null 2>&1; then PY=python3
else echo "error: no python interpreter found on PATH" >&2; exit 1; fi

fail=0
mk(){ "$PY" -c "import json,sys; print(json.dumps({'tool_name':'ExitPlanMode','cwd':'.','tool_input':{'plan':sys.argv[1]}}))" "$1"; }
gate(){ local desc="$1" want="$2" payload="$3"
  printf '%s' "$payload" | PYTHON="$PY" bash "$H/check-plan.sh" >/dev/null 2>/dev/null
  local rc=$?
  if [[ "$rc" == "$want" ]]; then echo "  ok: $desc [$rc]"; else echo "  FAIL: $desc (got $rc want $want)"; fail=1; fi
}

echo "[ gate decisions ]"
gate "src/ edit, no Work Record step -> DENY"      2 "$(mk '1. Edit src/main/java/Foo.java
2. tests')"
gate "src/ edit WITH step -> ALLOW"                0 "$(mk '1. Invoke /agent-workflow to create the Work Record
2. Edit src/main/java/Foo.java')"
gate "docs-only plan (no src/) -> ALLOW"           0 "$(mk 'Update docs/x.md; fix typo')"
gate "Work Record only in prose -> ALLOW"          0 "$(mk 'Refactor in src/ tree; see the Work Record process doc')"
gate 'nasty chars (quotes/newline/brace/backslash) + src/, no step -> DENY' 2 "$(mk 'Plan "quoted", brace { } backslash \ path src/x.java')"
gate "malformed JSON -> ALLOW (fail-open)"         0 "not json at all"
gate "empty stdin -> ALLOW (fail-open)"            0 ""

echo "[ gate honors configured guardedPaths (sidecar) ]"
# Copy the real gate into a temp dir and drop sidecars next to it — the hook
# reads guarded-paths.json next to check-plan.py, so this exercises the true
# config path without leaving a sidecar in the source tree.
GH="$(mktemp -d)"
cp "$H/check-plan.py" "$H/check-plan.sh" "$GH/"
gate_at(){ local dir="$1" desc="$2" want="$3" payload="$4"
  printf '%s' "$payload" | PYTHON="$PY" bash "$dir/check-plan.sh" >/dev/null 2>/dev/null
  local rc=$?
  if [[ "$rc" == "$want" ]]; then echo "  ok: $desc [$rc]"; else echo "  FAIL: $desc (got $rc want $want)"; fail=1; fi
}
sc(){ printf '%s' "$1" > "$GH/guarded-paths.json"; }
sc '{"guardedPaths":["core/","scripts/"]}'
gate_at "$GH" "configured core/ edit, no step -> DENY"          2 "$(mk '1. Edit core/checker.py')"
gate_at "$GH" "configured core/ edit WITH step -> ALLOW"        0 "$(mk '1. Invoke /agent-workflow (Work Record); 2. Edit core/checker.py')"
gate_at "$GH" "configured scripts/ edit, no step -> DENY"       2 "$(mk '1. Edit scripts/foo.py')"
gate_at "$GH" "boundary: score/ does NOT trip core/ -> ALLOW"   0 "$(mk '1. Edit score/tally.py')"
gate_at "$GH" "src/ not guarded when config=core/ -> ALLOW"     0 "$(mk '1. Edit src/main/java/Foo.java')"
sc '{"guardedPaths":["Core/"]}'
gate_at "$GH" "case-insensitive prefix (Core/ ~ core/) -> DENY" 2 "$(mk '1. Edit core/x.py')"
sc 'not json {'
gate_at "$GH" "malformed sidecar -> default src/ DENY"          2 "$(mk '1. Edit src/main/java/Foo.java')"
gate_at "$GH" "malformed sidecar -> core/ not guarded ALLOW"    0 "$(mk '1. Edit core/x.py')"
sc '{"guardedPaths":[]}'
gate_at "$GH" "empty guardedPaths -> default src/ DENY"         2 "$(mk '1. Edit src/x.java')"
rm -rf "$GH"

echo "[ gate fail-open when python absent ]"
env PATH="/usr/bin:/bin" bash "$H/check-plan.sh" </dev/null >/dev/null 2>&1
rc=$?; if [[ "$rc" == "0" ]]; then echo "  ok: no-python -> ALLOW [0]"; else echo "  FAIL: no-python (got $rc want 0)"; fail=1; fi

echo "[ seed/reinforce emit valid additionalContext JSON ]"
for hk in seed-workflow:UserPromptSubmit reinforce-workflow:PostToolUse; do
  s="${hk%%:*}"; ev="${hk##*:}"
  got=$(echo '{}' | bash "$H/$s.sh" | "$PY" -c "import json,sys; print(json.load(sys.stdin)['hookSpecificOutput']['hookEventName'])" 2>/dev/null)
  if [[ "$got" == "$ev" ]]; then echo "  ok: $s -> $got"; else echo "  FAIL: $s (got '$got' want '$ev')"; fail=1; fi
done


echo "[ opencode plugin: seed parity + fail-open shape ]"
# The OpenCode plugin is the runtime-analog of seed-workflow.sh. Its SEED const
# MUST stay byte-identical to the hook's CTX, so an agent under OpenCode gets the
# same Work-Record rule. Extraction relies on both being single-line double-quoted
# strings with no " or \ (enforced by seed-workflow.sh's own comment).
OCP="core/skill/opencode/agent-workflow.mjs"
if [[ -f "$OCP" ]]; then
  ctx="$(sed -n 's/^CTX="\(.*\)"$/\1/p' "$H/seed-workflow.sh")"
  seed="$(sed -n 's/^const SEED = "\(.*\)";$/\1/p' "$OCP")"
  if [[ -n "$ctx" && "$seed" == "$ctx" ]]; then echo "  ok: plugin SEED matches seed-workflow.sh CTX"; else echo "  FAIL: SEED/CTX parity drift"; fail=1; fi
  grep -q 'experimental.chat.system.transform' "$OCP" && echo "  ok: injects via experimental.chat.system.transform" || { echo "  FAIL: missing system.transform hook"; fail=1; }
  if grep -q 'try {' "$OCP" && grep -q 'catch' "$OCP"; then echo "  ok: fail-open (try/catch present)"; else echo "  FAIL: no try/catch fail-open guard"; fail=1; fi
  grep -q 'Array.isArray(output.system)' "$OCP" && echo "  ok: guards output.system shape" || { echo "  FAIL: missing output.system guard"; fail=1; }
else
  echo "  FAIL: $OCP missing"; fail=1
fi


echo "[ settings installer ]"
INST="$H/install-settings.py"
TMP="$(mktemp -d)"
# create from absent
"$PY" "$INST" --settings "$TMP/s.json" >/dev/null 2>&1
if "$PY" -c "import json,sys; d=json.load(open(sys.argv[1])); import sys as s; sys.exit(0 if set(d['hooks'])>={'UserPromptSubmit','PreToolUse','PostToolUse'} else 1)" "$TMP/s.json"; then echo "  ok: create-from-absent"; else echo "  FAIL: create-from-absent"; fail=1; fi
# idempotent: second run adds nothing
before="$("$PY" -c "import json,sys;print(json.dumps(json.load(open(sys.argv[1])),sort_keys=True))" "$TMP/s.json")"
"$PY" "$INST" --settings "$TMP/s.json" >/dev/null 2>&1
after="$("$PY" -c "import json,sys;print(json.dumps(json.load(open(sys.argv[1])),sort_keys=True))" "$TMP/s.json")"
if [[ "$before" == "$after" ]]; then echo "  ok: idempotent (second run no-op)"; else echo "  FAIL: idempotent"; fail=1; fi
# merge preserves existing hooks + refuses invalid
printf '%s' '{"permissions":{"allow":["x"]},"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"echo hi"}]}]}}' > "$TMP/m.json"
"$PY" "$INST" --settings "$TMP/m.json" >/dev/null 2>&1
if "$PY" -c "import json,sys; d=json.load(open(sys.argv[1])); cmds=[h['command'] for g in d['hooks']['PreToolUse'] for h in g['hooks']]; import sys as s; s.exit(0 if ('echo hi' in cmds and any('check-plan.sh' in c for c in cmds) and 'permissions' in d) else 1)" "$TMP/m.json"; then echo "  ok: merge preserves existing"; else echo "  FAIL: merge preserves existing"; fail=1; fi
printf '%s' 'not json {' > "$TMP/bad.json"
"$PY" "$INST" --settings "$TMP/bad.json" >/dev/null 2>&1
if [[ $? == "1" && "$(cat "$TMP/bad.json")" == "not json {" ]]; then echo "  ok: refuse-invalid (exit 1, unchanged)"; else echo "  FAIL: refuse-invalid"; fail=1; fi
rm -rf "$TMP"


echo "[ installer resolves guardedPaths sidecar from agent-workflow.yaml ]"
ST="$(mktemp -d)"
# no agent-workflow.yaml at repo root -> exit 0, no sidecar written (gate defaults src/)
"$PY" "$INST" --settings "$ST/.claude/settings.json" >/dev/null 2>&1
rc=$?
if [[ "$rc" == 0 && ! -f "$ST/.claude/hooks/guarded-paths.json" ]]; then echo "  ok: no yaml -> exit 0, no sidecar"; else echo "  FAIL: no-yaml degradation (rc=$rc)"; fail=1; fi
# yaml with hooks.guardedPaths at repo root (parent of .claude) -> sidecar written there
if "$PY" -c "import yaml" >/dev/null 2>&1; then
  printf 'version: 1\nhooks:\n  guardedPaths:\n    - "core/"\n    - "scripts/"\n' > "$ST/agent-workflow.yaml"
  "$PY" "$INST" --settings "$ST/.claude/settings.json" >/dev/null 2>&1
  if "$PY" -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get('guardedPaths')==['core/','scripts/'] else 1)" "$ST/.claude/hooks/guarded-paths.json" 2>/dev/null; then
    echo "  ok: sidecar written from yaml (repo-root resolution)"
  else
    echo "  FAIL: sidecar content/location from yaml"; fail=1
  fi
else
  echo "  skip: pyyaml unavailable (installer degrades to default src/)"
fi
rm -rf "$ST"


echo "[ e2e: packaged (dist) hooks execute + installer wiring ]"
DIST="dist/agent-workflow/hooks"
if [[ -d "$DIST" ]]; then
  # run the PACKAGED gate copy (what a consumer installs), not the source
  d_deny="$(mk '1. Edit src/main/java/Foo.java')"
  d_allow="$(mk '1. Invoke /agent-workflow (Work Record) then edit src/main/java/Foo.java')"
  printf '%s' "$d_deny"  | PYTHON="$PY" bash "$DIST/check-plan.sh" >/dev/null 2>&1
  [[ $? == 2 ]] && echo "  ok: packaged gate DENY" || { echo "  FAIL: packaged gate DENY"; fail=1; }
  printf '%s' "$d_allow" | PYTHON="$PY" bash "$DIST/check-plan.sh" >/dev/null 2>&1
  [[ $? == 0 ]] && echo "  ok: packaged gate ALLOW" || { echo "  FAIL: packaged gate ALLOW"; fail=1; }
  echo '{}' | bash "$DIST/seed-workflow.sh" | "$PY" -c "import json,sys;json.load(sys.stdin)" 2>/dev/null     && echo "  ok: packaged seed valid JSON" || { echo "  FAIL: packaged seed JSON"; fail=1; }
  # installer wires the packaged gate into a consumer-shaped settings.json
  E2E="$(mktemp -d)"; mkdir -p "$E2E/.claude/hooks"; cp "$DIST"/* "$E2E/.claude/hooks/"
  "$PY" "$DIST/install-settings.py" --settings "$E2E/.claude/settings.json" >/dev/null 2>&1
  "$PY" -c "import json,sys; d=json.load(open(sys.argv[1])); cmds=[h['command'] for e in d['hooks'].values() for g in e for h in g['hooks']]; import sys as s; s.exit(0 if (any('check-plan.sh' in c for c in cmds) and all('.claude/hooks/' in c for c in cmds)) else 1)" "$E2E/.claude/settings.json"     && echo "  ok: installer registers .claude/hooks/ commands" || { echo "  FAIL: installer wiring"; fail=1; }
  rm -rf "$E2E"
else
  echo "  skip: dist not built"
fi


echo "[ dogfood: this repo's .claude hooks match dist + registered ]"
if [[ -d .claude/hooks && -f .claude/settings.json ]]; then
  drift=0
  for f in dist/agent-workflow/hooks/*; do
    b="$(basename "$f")"
    if ! diff -q --strip-trailing-cr "$f" ".claude/hooks/$b" >/dev/null 2>&1; then echo "  FAIL: .claude/hooks/$b differs from dist"; drift=1; fail=1; fi
  done
  [[ $drift == 0 ]] && echo "  ok: .claude/hooks match dist"
  "$PY" -c "import json,sys; d=json.load(open('.claude/settings.json')); cmds=[h['command'] for e in d['hooks'].values() for g in e for h in g['hooks']]; import sys as s; s.exit(0 if all(any(n in c for c in cmds) for n in ('seed-workflow.sh','check-plan.sh','reinforce-workflow.sh')) else 1)"     && echo "  ok: settings.json registers all 3 hooks" || { echo "  FAIL: settings.json missing hook registration"; fail=1; }
else
  echo "  skip: no dogfood .claude hooks"
fi


echo "[ merge-agents-section: reconcile marker block, preserve prose ]"
MERGE="$H/merge-agents-section.py"
MT="$(mktemp -d)"
printf 'OLD SECTION v1\n' > "$MT/tmpl.md"
printf '# My repo notes\n\nPrologue prose.\n\n<!-- agent-workflow:agents-section:start -->\nSTALE BODY\n<!-- agent-workflow:agents-section:end -->\n\nEpilogue prose.\n' > "$MT/CLAUDE.md"
BEFORE_PRO="$(sed -n '1,4p' "$MT/CLAUDE.md")"
# new template content
printf 'NEW SECTION v2\nwith an added line\n' > "$MT/tmpl.md"
"$PY" "$MERGE" --file "$MT/CLAUDE.md" --template "$MT/tmpl.md" >/dev/null 2>&1
rc=$?
mid="$(sed -n '/agents-section:start/,/agents-section:end/p' "$MT/CLAUDE.md" | sed '1d;$d')"
if [[ $rc == 0 && "$mid" == "$(cat "$MT/tmpl.md")" ]]; then echo "  ok: marker block refreshed to template"; else echo "  FAIL: block not refreshed (rc=$rc)"; fail=1; fi
if grep -q "Prologue prose." "$MT/CLAUDE.md" && grep -q "Epilogue prose." "$MT/CLAUDE.md" && grep -q "# My repo notes" "$MT/CLAUDE.md"; then echo "  ok: surrounding prose preserved"; else echo "  FAIL: prose not preserved"; fail=1; fi
# idempotent: second run makes no change
cp "$MT/CLAUDE.md" "$MT/CLAUDE.before"
"$PY" "$MERGE" --file "$MT/CLAUDE.md" --template "$MT/tmpl.md" >/dev/null 2>&1
if diff -q "$MT/CLAUDE.before" "$MT/CLAUDE.md" >/dev/null 2>&1; then echo "  ok: idempotent (re-run no-op)"; else echo "  FAIL: not idempotent"; fail=1; fi
# no markers -> no change, exit 0
printf 'just prose, no markers\n' > "$MT/plain.md"
"$PY" "$MERGE" --file "$MT/plain.md" --template "$MT/tmpl.md" >/dev/null 2>&1
if [[ $? == 0 && "$(cat "$MT/plain.md")" == "just prose, no markers" ]]; then echo "  ok: no markers -> untouched, exit 0"; else echo "  FAIL: no-markers handling"; fail=1; fi
# malformed (end before start) -> exit 3, no change
printf '<!-- agent-workflow:agents-section:end -->\nx\n<!-- agent-workflow:agents-section:start -->\n' > "$MT/bad.md"
"$PY" "$MERGE" --file "$MT/bad.md" --template "$MT/tmpl.md" >/dev/null 2>&1
[[ $? == 3 ]] && echo "  ok: malformed markers -> exit 3" || { echo "  FAIL: malformed not detected"; fail=1; }
rm -rf "$MT"


echo "[ lint: no inline flow-sequence guardedPaths in skill source/templates ]"
if grep -rn "guardedPaths: \[" core/skill core/templates >/dev/null 2>&1; then
  echo "  FAIL: inline 'guardedPaths: [' found (must be block sequence for Spotless)"; grep -rn "guardedPaths: \[" core/skill core/templates; fail=1
else
  echo "  ok: guardedPaths is block-sequence everywhere"
fi

if [[ "$fail" != "0" ]]; then echo; echo "hooks tests FAILED"; exit 1; fi
echo; echo "all hooks tests ok"
