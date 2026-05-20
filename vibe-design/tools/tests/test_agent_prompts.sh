#!/usr/bin/env bash
# Test that current agent prompts and runtime skills keep their core contracts.

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

check() {
  local label="$1" rc="$2"
  if [ "$rc" -eq 0 ]; then
    echo "  PASS  $label"
    pass=$((pass+1))
  else
    echo "  FAIL  $label"
    fail=$((fail+1))
  fi
}

check_not() {
  local label="$1" rc="$2"
  if [ "$rc" -ne 0 ]; then
    echo "  PASS  $label"
    pass=$((pass+1))
  else
    echo "  FAIL  $label"
    fail=$((fail+1))
  fi
}

echo "== agent frontmatter =="
grep -Pq '^\s*webfetch:\s*deny\s*$'  "$PLANNER";    check "planner webfetch deny"      $?
grep -Pq '^\s*webfetch:\s*deny\s*$'  "$DESIGNER";   check "designer webfetch deny"     $?
grep -Pq '^\s*webfetch:\s*deny\s*$'  "$CRITIC";     check "critic webfetch deny"       $?
grep -Pq '^\s*webfetch:\s*allow\s*$' "$RESEARCHER"; check "researcher webfetch allow"  $?

echo
echo "== planner =="
grep -q 'deliverables\.md' "$PLANNER";               check "reads deliverables.md"       $?
grep -q 'ask-user' "$PLANNER";                       check "uses ask-user skill"         $?
grep -q 'plan\.md' "$PLANNER";                       check "writes plan.md"              $?
grep -Pq '不增不删|不在 deliverables\.md 之外加交付物' "$PLANNER"; check "does not change scope" $?
grep -q 'task_status' "$PLANNER";                    check "tracks background tasks"     $?
grep -q 'v<n+1>' "$PLANNER";                         check "has retry version flow"      $?
grep -q 'escalate\.md' "$PLANNER";                   check "escalate.md exit hatch"      $?
grep -q 'BLOCKER' "$PLANNER";                        check "routes BLOCKER issues"       $?
grep -q 'MAJOR' "$PLANNER";                          check "routes MAJOR issues"         $?
grep -q 'MINOR / NIT' "$PLANNER";                    check "can accept minor issues"     $?
grep -Pq '不要打分|不做最终通过判定' "$PLANNER";       check "critic no-score contract"    $?

echo
echo "== critic =="
grep -q '^## 评审流程' "$CRITIC";                    check "has review process"          $?
grep -q '^### ① 机器判定' "$CRITIC";                 check "has machine gate step"       $?
grep -q '^### ② 提取设计预期' "$CRITIC";             check "extracts design expectations" $?
grep -q '^### ③ 读取实物' "$CRITIC";                 check "reads artifact step"         $?
grep -q '^### ④ 问题评审' "$CRITIC";                 check "has issue review step"       $?
grep -q '^## 严重度定义' "$CRITIC";                  check "defines severity"            $?
grep -q '^## review.md 模板' "$CRITIC";              check "has review template"         $?
grep -q '^## 问题清单' "$CRITIC";                    check "template has issue list"     $?
grep -q '^## 给 Planner 的决策依据' "$CRITIC";       check "template has planner basis"  $?
grep -Pq 'validate\.py review' "$CRITIC";            check "uses validate.py review"     $?
grep -Pq 'BLOCKER.*MAJOR.*MINOR.*NIT|BLOCKER / MAJOR / MINOR / NIT' "$CRITIC"; check "severity labels present" $?
grep -Pq '不打分|不写总分' "$CRITIC";                check "forbids scoring"             $?
grep -Pq '不做最终通过判定|不给最终' "$CRITIC";       check "forbids final pass verdict"  $?
grep -Pq '唯一产物.*v\?\.review\.md.*落盘|没落盘.*=.*没评' "$CRITIC"; check "review.md write-to-disk" $?
grep -q '^## 主观打分' "$CRITIC";                    check_not "no subjective score section" $?
grep -Pq '\*\*xx/25\*\*|总分.{0,4}≥\s*18|无单项\s*≤\s*2' "$CRITIC"; check_not "no score threshold" $?

echo
echo "== designer =="
grep -q 'gen_image\.py' "$DESIGNER";                 check "uses gen_image.py"           $?
grep -q 'html_screenshot\.py' "$DESIGNER";           check "uses html_screenshot.py"     $?
grep -q '候选评审' "$DESIGNER";                       check "reviews candidates"          $?
grep -q '视觉自检' "$DESIGNER";                       check "does visual self-check"      $?
grep -q 'brand-spec\.md' "$DESIGNER";                check "reads brand-spec.md"         $?
grep -q 'deliverables\.md' "$DESIGNER";              check "reads deliverables.md"       $?
grep -q 'BLOCKER' "$DESIGNER";                       check "handles BLOCKER review"      $?
grep -q 'MAJOR' "$DESIGNER";                         check "handles MAJOR review"        $?
grep -Pq 'MINOR.*NIT' "$DESIGNER";                   check "handles minor review issues" $?

echo
echo "== researcher =="
grep -q 'facts\.md' "$RESEARCHER";                   check "writes facts.md"             $?
grep -q 'brand-spec\.md' "$RESEARCHER";              check "writes brand-spec.md"        $?
grep -q 'deliverables\.md' "$RESEARCHER";            check "writes deliverables.md"      $?
grep -q 'design-guidelines' "$RESEARCHER";           check "uses design-guidelines skill" $?

echo
echo "== skills =="
test -f "$SKILLS/ask-user/SKILL.md";                 check "ask-user skill exists"       $?
test -f "$SKILLS/craft/SKILL.md";                    check "craft skill exists"          $?
test -d "$SKILLS/craft/fonts";                       check "craft fonts exist"           $?
test -f "$SKILLS/design-guidelines/SKILL.md";        check "design-guidelines skill exists" $?

echo
echo "== summary: $pass passed, $fail failed =="
[ $fail -eq 0 ] || exit 1
