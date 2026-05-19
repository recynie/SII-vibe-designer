#!/usr/bin/env bash
# Test that agent prompts and skill files have correct structural invariants.
# Verifies frontmatter, required sections, scoring config, and system deps.

set -u

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
AGENTS="$ROOT/vibe-design/.opencode/agent"
SKILLS="$ROOT/vibe-design/.opencode/skills"
PLANNER="$AGENTS/planner.md"
DESIGNER="$AGENTS/designer.md"
CRITIC="$AGENTS/critic.md"
RESEARCHER="$AGENTS/researcher.md"

pass=0
fail=0
OLD_MODE_WORD="re""use"
OLD_POLICY_WORD="pol""icy"
OLD_ASSET_SKILL="asset-""prep"
OLD_CREATE_MODE="create ""模式"
OLD_MODE_PREFIX="mode"":"
OLD_EXACT_USE="exact""-use"
OLD_ASSET_RULES="资产""规则"
REMOVED_PATTERN="${OLD_CREATE_MODE}|${OLD_MODE_WORD} 模式|${OLD_MODE_PREFIX} create|${OLD_MODE_PREFIX} ${OLD_MODE_WORD}|${OLD_EXACT_USE}|${OLD_POLICY_WORD}|${OLD_ASSET_RULES}|${OLD_ASSET_SKILL}"

check() {
  local label="$1" rc="$2"
  if [ "$rc" -eq 0 ]; then echo "  PASS  $label"; pass=$((pass+1));
  else echo "  FAIL  $label"; fail=$((fail+1)); fi
}

check_not() {
  local label="$1" rc="$2"
  if [ "$rc" -ne 0 ]; then echo "  PASS  $label"; pass=$((pass+1));
  else echo "  FAIL  $label"; fail=$((fail+1)); fi
}

# -- Agent frontmatter: webfetch permissions --

echo "== agent frontmatter =="
grep -Pq '^\s*webfetch:\s*deny\s*$'  "$PLANNER";    check "planner webfetch deny"    $?
grep -Pq '^\s*webfetch:\s*deny\s*$'  "$DESIGNER";   check "designer webfetch deny"   $?
grep -Pq '^\s*webfetch:\s*deny\s*$'  "$CRITIC";     check "critic webfetch deny"     $?
grep -Pq '^\s*webfetch:\s*allow\s*$' "$RESEARCHER"; check "researcher webfetch allow" $?

# -- Planner invariants --

echo
echo "== planner =="
grep -q 'deliverables\.md' "$PLANNER";                          check "reads deliverables.md"         $?
grep -q 'assets/' "$PLANNER";                                   check "passes assets to designer"     $?
! grep -Pq "$REMOVED_PATTERN|按\s*mode" "$PLANNER";             check "planner has no mode routing"    $?
grep -q 'escalate\.md' "$PLANNER";                              check "escalate.md exit hatch"        $?
grep -Pq '映射|不增不删' "$PLANNER";                             check "plan.md as mapping"            $?
grep -Pq '并行|background.*true' "$PLANNER";                     check "parallel dispatch documented"  $?
grep -Pq '依赖分析|依赖.*必须等' "$PLANNER";                      check "dependency analysis documented" $?
grep -q 'critic' "$PLANNER";                                    check "designer→critic loop"          $?
grep -Pq 'RUN_ID 强约束|不可手写|禁止.*手写.*语义化' "$PLANNER"; check "RUN_ID hard constraint"         $?

# -- Critic invariants --

echo
echo "== critic =="
grep -q '^## 机器判定'   "$CRITIC"; check "has '## 机器判定' section"     $?
grep -q '^## 实物观察'   "$CRITIC"; check "has '## 实物观察' section"     $?
grep -q '^## 主观打分'   "$CRITIC"; check "has '## 主观打分' section"     $?
grep -q '^## 改进建议'   "$CRITIC"; check "has '## 改进建议' section"     $?
grep -q '机器硬门槛结果' "$CRITIC"; check "machine-gate verdict present"  $?

grep -Pq '字族.{0,12}(必跑|必过|硬门槛)' "$CRITIC"; check "fonts hard-gated"           $?

grep -Pq '\bx/5\b'        "$CRITIC"; check "per-axis range x/5"   $?
grep -Pq '\*\*xx/25\*\*'  "$CRITIC"; check "total range xx/25"    $?
grep -Pq '总分.{0,4}≥\s*18' "$CRITIC"; check "pass threshold ≥18" $?
grep -Pq '无单项\s*≤\s*2'   "$CRITIC"; check "no-axis ≤2 floor"   $?

grep -q '调性体现'                "$CRITIC"; check "axis: 调性体现"   $?
grep -q '视觉气质'                "$CRITIC"; check "axis: 视觉气质"   $?
grep -Pq '单件构图|构图品质'      "$CRITIC"; check "axis: 单件构图"   $?
grep -q '信息层级'                "$CRITIC"; check "axis: 信息层级"   $?
grep -q '任务完成度'              "$CRITIC"; check "axis: 任务完成度" $?

grep -Pq 'validate\.py review'   "$CRITIC"; check "uses validate.py review"          $?
grep -Pq '唯一产物.*v\?\.review\.md.*落盘|没落盘.*=.*没评' "$CRITIC"; check "review.md write-to-disk" $?

# -- Designer invariants --

echo
echo "== designer =="
grep -q 'assets/<filename>' "$DESIGNER"; check "documents asset references"  $?
grep -Pq '不生成相似替代品|不编造不存在的素材路径' "$DESIGNER"; check "prevents asset fabrication" $?
grep -Pq 'ImageMagick|convert' "$DESIGNER"; check "documents ImageMagick" $?
grep -q 'gen_image.py'      "$DESIGNER"; check "documents gen_image"         $?
grep -q 'html_screenshot.py' "$DESIGNER"; check "documents html screenshot"  $?
! grep -Pq "$REMOVED_PATTERN" "$DESIGNER"; check "designer has no removed concepts" $?

# -- Skills invariants --

echo
echo "== skills =="
for s in logo poster copywriting ui-mockup; do
  ! grep -Pq '<!doctype html>|<style>|font-family\s*:' "$SKILLS/$s/SKILL.md"
  check "skills/$s no HTML skeleton/font-family" $?
done
test ! -e "$SKILLS/asset-""prep";                  check "asset conversion skill removed"   $?

# -- System dependencies --

echo
echo "== system deps =="
command -v convert >/dev/null; check "ImageMagick convert available" $?

echo
echo "== summary: $pass passed, $fail failed =="
[ $fail -eq 0 ] || exit 1
