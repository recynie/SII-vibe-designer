#!/usr/bin/env bash
# Test that Python validation tools work correctly.
# Runs check_html_fonts and the validate.py aggregator against compliant and violation mock data.

set -u

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
TOOLS="$ROOT/vibe-design/tools"
COMPLIANT="$ROOT/vibe-design/tools/tests/mocks/compliant"
VIOLATION="$ROOT/vibe-design/tools/tests/mocks/violation"
PY="${PYTHON:-python3}"

pass=0
fail=0

expect_pass() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "  PASS  (exit 0) $label"
    pass=$((pass+1))
  else
    echo "  FAIL  (expected 0, got $?) $label"
    "$@" 2>&1 | sed 's/^/      | /'
    fail=$((fail+1))
  fi
}

expect_fail() {
  local label="$1"; shift
  local out
  out="$("$@" 2>&1)"
  local rc=$?
  if [ $rc -ne 0 ] && [ -n "$out" ]; then
    echo "  PASS  (exit $rc) $label"
    pass=$((pass+1))
  else
    echo "  FAIL  (expected non-0 with output, got $rc) $label"
    echo "$out" | sed 's/^/      | /'
    fail=$((fail+1))
  fi
}

echo "== check_html_fonts =="
expect_pass "compliant HTML passes"  "$PY" "$TOOLS/check_html_fonts.py" --html "$COMPLIANT/landing.html" --spec "$COMPLIANT/brand-spec.md"
expect_fail "violation HTML fails"   "$PY" "$TOOLS/check_html_fonts.py" --html "$VIOLATION/landing.html" --spec "$COMPLIANT/brand-spec.md"

echo
echo "== validate.py review aggregator =="
expect_pass "aggregator passes compliant HTML" "$PY" "$TOOLS/validate.py" review "$COMPLIANT" --artifact "$COMPLIANT/landing.html"

echo
echo "== summary: $pass passed, $fail failed =="
[ $fail -eq 0 ] || exit 1
