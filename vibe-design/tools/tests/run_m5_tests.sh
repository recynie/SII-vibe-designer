#!/usr/bin/env bash
# M5 verification: critic.md is structured around three sections (machine /
# palette-reference / subjective) with palette as advisory only, and uses
# the 0-5 per-axis scale.

set -u

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
TOOLS="$ROOT/vibe-design/tools"
PY="${PYTHON:-python3}"
CRITIC="$ROOT/vibe-design/.opencode/agent/critic.md"

pass=0
fail=0

check() { local label="$1" rc="$2"; if [ "$rc" -eq 0 ]; then echo "  PASS  $label"; pass=$((pass+1)); else echo "  FAIL  $label"; fail=$((fail+1)); fi; }

echo "== critic.md three-section structure =="
grep -q '^## 机器判定' "$CRITIC"; check "has '## 机器判定' section"     $?
grep -q '^## 色板参考' "$CRITIC"; check "has '## 色板参考' advisory section" $?
grep -q '^## 主观打分' "$CRITIC"; check "has '## 主观打分' section"     $?
grep -q '^## 改进建议' "$CRITIC"; check "has '## 改进建议' section"     $?
grep -q '机器硬门槛结果' "$CRITIC"; check "machine-gate verdict line present" $?

echo
echo "== palette is advisory, not blocking =="
grep -Pq '色板.{0,8}(不阻断|不参与|不再.*触发|不再.*单独|不影响.*主观)' "$CRITIC"; check "palette explicitly marked non-blocking" $?
grep -Pq '字族.{0,12}(必跑|必过|硬门槛)' "$CRITIC"; check "fonts still hard-gated" $?

echo
echo "== 0-5 scoring scale =="
grep -Pq '\bx/5\b' "$CRITIC"; check "per-axis range is x/5" $?
grep -Pq '\*\*xx/25\*\*' "$CRITIC"; check "total range is xx/25" $?
grep -Pq '总分.{0,4}≥\s*18' "$CRITIC"; check "pass threshold ≥18 total" $?
grep -Pq '无单项\s*≤\s*2' "$CRITIC"; check "no-axis ≤2 floor" $?
! grep -Pq '\bx/10\b|\bxx/50\b|≥\s*35' "$CRITIC"; check "no leftover 0-10 / /50 / ≥35 references" $?

echo
echo "== machine pipeline: schema mandatory, fonts mandatory, palette advisory =="
$PY "$TOOLS/validate_facts.py"        "$ROOT/vibe-design/tools/tests/mocks/compliant/facts.md"        >/dev/null 2>&1; check "validate_facts compliant" $?
$PY "$TOOLS/validate_brand_spec.py"   "$ROOT/vibe-design/tools/tests/mocks/compliant/brand-spec.md" --facts "$ROOT/vibe-design/tools/tests/mocks/compliant/facts.md" >/dev/null 2>&1; check "validate_brand_spec compliant" $?
$PY "$TOOLS/check_html_fonts.py"      --html "$ROOT/vibe-design/tools/tests/mocks/compliant/landing.html" --spec "$ROOT/vibe-design/tools/tests/mocks/compliant/brand-spec.md" >/dev/null 2>&1; check "check_html_fonts compliant" $?

# Palette check still runs and still reports stray colors; that's fine — critic
# is now expected to surface this in the advisory section without blocking.
$PY "$TOOLS/check_palette_compliance.py" --image "$ROOT/vibe-design/outputs/mock-m5-violation/artifacts/logo/v1.png" --spec "$ROOT/vibe-design/outputs/mock-m5-violation/brand-spec.md" >/dev/null 2>&1
[ $? -ne 0 ]; check "palette violation still reported by tool (advisory-fed)" $?

echo
echo "== subjective axes preserved =="
grep -q '调性体现' "$CRITIC"; check "axis: 调性体现"   $?
grep -q '视觉气质' "$CRITIC"; check "axis: 视觉气质"   $?
grep -Pq '单件构图|构图品质' "$CRITIC"; check "axis: 单件构图" $?
grep -q '信息层级' "$CRITIC"; check "axis: 信息层级"   $?
grep -q '任务完成度' "$CRITIC"; check "axis: 任务完成度" $?

echo
echo "== review.md must be written to disk =="
grep -Pq '唯一产物.*v\?\.review\.md.*落盘|没落盘.*=.*没评' "$CRITIC"; check "critic.md states review.md write-to-disk is the only artifact" $?

PLANNER="$ROOT/vibe-design/.opencode/agent/planner.md"
grep -Pq 'MISSING_REVIEW_FILE|test -f .*review\.md' "$PLANNER"; check "planner.md gates on review.md existence after @critic" $?

echo
echo "== summary: $pass passed, $fail failed =="
[ $fail -eq 0 ] || exit 1
