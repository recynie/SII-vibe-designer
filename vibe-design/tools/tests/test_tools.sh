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

# Create a tiny valid PNG for gen_image CLI guard tests.
DUMMY_PNG="$(mktemp /tmp/vibe-test-XXXXXX.png)"
"$PY" -c "
from PIL import Image
Image.new('RGBA', (4, 4), (0, 0, 0, 0)).save('$DUMMY_PNG')
" 2>/dev/null || printf '\x89PNG\r\n\x1a\n' > "$DUMMY_PNG"

echo "== gen_image CLI guards =="
expect_pass "gen_image help mentions input-image" bash -c "'$PY' '$TOOLS/gen_image.py' --help | grep -q -- --input-image"
expect_fail "minimax rejects image-to-image" "$PY" "$TOOLS/gen_image.py" --backend minimax --input-image "$DUMMY_PNG" --prompt "edit" --output /tmp/gen-image-i2i-guard.png --candidates 1
expect_fail "mask requires input image" "$PY" "$TOOLS/gen_image.py" --backend openai --mask "$DUMMY_PNG" --prompt "edit" --output /tmp/gen-image-mask-guard.png --candidates 1
expect_fail "candidates must be positive" "$PY" "$TOOLS/gen_image.py" --backend minimax --prompt "edit" --output /tmp/gen-image-candidates-guard.png --candidates 0
rm -f "$DUMMY_PNG"

echo
echo "== check_html_fonts =="
expect_pass "compliant HTML passes"  "$PY" "$TOOLS/check_html_fonts.py" --html "$COMPLIANT/landing.html" --spec "$COMPLIANT/brand-spec.md"
expect_fail "violation HTML fails"   "$PY" "$TOOLS/check_html_fonts.py" --html "$VIOLATION/landing.html" --spec "$COMPLIANT/brand-spec.md"

echo
echo "== validate.py review aggregator =="
expect_pass "aggregator passes compliant HTML" "$PY" "$TOOLS/validate.py" review "$COMPLIANT" --artifact "$COMPLIANT/landing.html"

echo
echo "== summary: $pass passed, $fail failed =="
[ $fail -eq 0 ] || exit 1
