#!/usr/bin/env bash
# Run all M1 validators against mock samples.
# Compliant set: every script must exit 0.
# Violation set: every script must exit non-0 and print at least one line.

set -u

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
TOOLS="$ROOT/vibe-design/tools"
COMPLIANT="$ROOT/vibe-design/tools/tests/mocks/compliant"
VIOLATION="$ROOT/vibe-design/tools/tests/mocks/violation"
PY="${PYTHON:-python3}"

# Ensure mock PNGs exist (PIL is imported by extract anyway).
"$PY" "$ROOT/vibe-design/tools/tests/mocks/_make_pngs.py" >/dev/null

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

echo "== compliant set =="
expect_pass "validate_facts compliant"          "$PY" "$TOOLS/validate_facts.py"          "$COMPLIANT/facts.md"
expect_pass "validate_brand_spec compliant"     "$PY" "$TOOLS/validate_brand_spec.py"     "$COMPLIANT/brand-spec.md" --facts "$COMPLIANT/facts.md"
expect_pass "validate_deliverables compliant"   "$PY" "$TOOLS/validate_deliverables.py"   "$COMPLIANT/deliverables.md"
expect_pass "extract_artifact_palette runs"     "$PY" "$TOOLS/extract_artifact_palette.py" "$COMPLIANT/artifact.png"
expect_pass "check_palette_compliance compliant" "$PY" "$TOOLS/check_palette_compliance.py" --image "$COMPLIANT/artifact.png" --spec "$COMPLIANT/brand-spec.md"
expect_pass "check_html_fonts compliant"        "$PY" "$TOOLS/check_html_fonts.py"        --html "$COMPLIANT/landing.html"  --spec "$COMPLIANT/brand-spec.md"

echo
echo "== violation set =="
expect_fail "validate_facts violation"          "$PY" "$TOOLS/validate_facts.py"          "$VIOLATION/facts.md"
expect_fail "validate_brand_spec violation"     "$PY" "$TOOLS/validate_brand_spec.py"     "$VIOLATION/brand-spec.md" --facts "$COMPLIANT/facts.md"
expect_fail "validate_deliverables violation"   "$PY" "$TOOLS/validate_deliverables.py"   "$VIOLATION/deliverables.md"
expect_fail "validate_deliverables overflow"     "$PY" "$TOOLS/validate_deliverables.py"   "$VIOLATION/deliverables-overflow.md"
expect_fail "check_palette_compliance violation" "$PY" "$TOOLS/check_palette_compliance.py" --image "$VIOLATION/artifact.png" --spec "$COMPLIANT/brand-spec.md"
expect_fail "check_html_fonts violation"        "$PY" "$TOOLS/check_html_fonts.py"        --html "$VIOLATION/landing.html"  --spec "$COMPLIANT/brand-spec.md"

echo
echo "== summary: $pass passed, $fail failed =="
[ $fail -eq 0 ] || exit 1
