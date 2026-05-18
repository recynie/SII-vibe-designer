#!/usr/bin/env bash
# M2 verification: run all M1 validators against the four mock-m2-* runs.
# Verifies that researcher's expected output shape passes every schema check.
# At least 1 deliverables.md should have a `mode: reuse` row.
# At least 1 deliverables.md should have a non-empty 拒绝 row.

set -u

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
TOOLS="$ROOT/vibe-design/tools"
RUNS=(mock-m2-sii-brand mock-m2-sii-admission mock-m2-zhujiajiao mock-m2-coffee)
PY="${PYTHON:-python3}"

pass=0
fail=0

run_one() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "  PASS  $label"
    pass=$((pass+1))
  else
    echo "  FAIL  $label"
    "$@" 2>&1 | sed 's/^/      | /'
    fail=$((fail+1))
  fi
}

for run in "${RUNS[@]}"; do
  RD="$ROOT/vibe-design/outputs/$run"
  echo "== $run =="
  run_one "validate_facts"        "$PY" "$TOOLS/validate_facts.py"        "$RD/facts.md"
  run_one "validate_brand_spec"   "$PY" "$TOOLS/validate_brand_spec.py"   "$RD/brand-spec.md" --facts "$RD/facts.md"
  run_one "validate_deliverables" "$PY" "$TOOLS/validate_deliverables.py" "$RD/deliverables.md"
done

echo
echo "== M2 specific checks =="
reuse_count=0
reject_count=0
for run in "${RUNS[@]}"; do
  if grep -q 'mode:\s*reuse' "$ROOT/vibe-design/outputs/$run/deliverables.md"; then
    reuse_count=$((reuse_count+1))
  fi
  if awk '/^## 拒绝/{f=1;next} /^## /{f=0} f && /^- /{print; exit 0} END{exit f?0:1}' \
        "$ROOT/vibe-design/outputs/$run/deliverables.md" >/dev/null 2>&1; then
    reject_count=$((reject_count+1))
  fi
done
[ "$reuse_count" -ge 1 ] && echo "  PASS  ≥1 deliverables has mode: reuse  (got $reuse_count)" && pass=$((pass+1)) || { echo "  FAIL  no deliverables uses mode: reuse"; fail=$((fail+1)); }
[ "$reject_count" -ge 1 ] && echo "  PASS  ≥1 deliverables has non-empty 拒绝 (got $reject_count)" && pass=$((pass+1)) || { echo "  FAIL  no deliverables has 拒绝 row"; fail=$((fail+1)); }

light_count=0
for run in "${RUNS[@]}"; do
  if grep -q '^# 严格度: light' "$ROOT/vibe-design/outputs/$run/brand-spec.md"; then
    light_count=$((light_count+1))
  fi
done
[ "$light_count" -ge 1 ] && echo "  PASS  ≥1 spec uses light strictness     (got $light_count)" && pass=$((pass+1)) || { echo "  FAIL  no light-mode spec sample"; fail=$((fail+1)); }

echo
echo "== summary: $pass passed, $fail failed =="
[ $fail -eq 0 ] || exit 1
