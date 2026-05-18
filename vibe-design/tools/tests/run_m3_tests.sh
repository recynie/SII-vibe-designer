#!/usr/bin/env bash
# M3 verification: static checks on planner.md to ensure scope was narrowed.
# Real end-to-end opencode runs are out of scope here (need TUI); these checks
# guarantee the prompt no longer carries the deleted template / quotas.

set -u

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
PLANNER="$ROOT/vibe-design/.opencode/agent/planner.md"
PY="${PYTHON:-python3}"

pass=0
fail=0

assert_no() {
  local label="$1" pattern="$2"
  if ! grep -Pq "$pattern" "$PLANNER"; then
    echo "  PASS  no '$label'"
    pass=$((pass+1))
  else
    echo "  FAIL  planner.md still contains pattern '$label':"
    grep -nP "$pattern" "$PLANNER" | sed 's/^/      | /'
    fail=$((fail+1))
  fi
}

assert_yes() {
  local label="$1" pattern="$2"
  if grep -Pq "$pattern" "$PLANNER"; then
    echo "  PASS  has '$label'"
    pass=$((pass+1))
  else
    echo "  FAIL  planner.md missing pattern '$label'"
    fail=$((fail+1))
  fi
}

echo "== planner.md scope checks =="
# 删除的固定四件套表（行内同时含 logo + 主视觉 + 文案 + UI mockup 的旧表格）
assert_no "fixed four-pack table" '^\| logo 主标志.*\|$'
# 删除的"至少 4 个子任务"条款
assert_no "≥4 subtasks quota"      '至少\s*4\s*个子任务'
# 删除的旧 skill 路由表
assert_no "old skill router table" '\| skill \|$'
# planner 不能 webfetch
assert_yes "webfetch deny in frontmatter" '^\s*webfetch:\s*deny\s*$'
# 必须读 deliverables.md 调度
assert_yes "reads deliverables.md"        'deliverables\.md'
# 必须按 mode 路由
assert_yes "routes by mode"               '(create 模式|reuse 模式|按\s*mode)'
# 必须能 escalate
assert_yes "escalate.md exit hatch"       'escalate\.md'
# plan.md 是映射不是生成
assert_yes "plan.md as mapping"           '映射|不增不删'
# subagent 串行纪律保留
assert_yes "strict serial scheduling"     '严格串行|绝不并行|不要并行'
# critic / designer 闭环保留
assert_yes "designer→critic loop"         'critic'

# planner 必须明确"escalate 不退出 session、用 Write 落盘、继续跑剩下条目"
assert_yes "escalate uses Write tool"     '用 Write 工具'
assert_yes "escalate doesn't stop session" '继续调度 deliverables 中的剩余条目'
assert_yes "final.md still required after escalate" '所有任务跑完.*final\.md'
# 收 researcher 回报后必须自跑校验（不可跳）
assert_yes "validates upstream before plan.md"  '必须自跑.*schema 校验'
# planner final.md 模板必须用 /25 而非旧 0-50（M5 v2 同步）
assert_no "no leftover ?/50 in final.md template"  '\?/50'

# RUN_ID 必须强约束：只能来自 bash 脚本输出，禁止手写
assert_yes "RUN_ID hard constraint exists"   'RUN_ID 强约束|不可手写|禁止.*手写.*语义化'
assert_yes "<RUN_ID> placeholder warning"    '占位符.*替换|<RUN_ID>.*替换'

# planner 上游校验只调一次聚合脚本，不再分别调 3 个 validate_*
assert_yes "planner uses validate.py upstream"  'validate\.py upstream'
assert_no  "planner no longer calls separate upstream validators" '^\s+uv run python tools/validate_(facts|brand_spec|deliverables)\.py'

# 其它 agent frontmatter
DESIGNER="$ROOT/vibe-design/.opencode/agent/designer.md"
CRITIC="$ROOT/vibe-design/.opencode/agent/critic.md"
RESEARCHER="$ROOT/vibe-design/.opencode/agent/researcher.md"

assert_designer_no_webfetch() {
  if grep -Pq '^\s*webfetch:\s*deny\s*$' "$DESIGNER"; then
    echo "  PASS  designer webfetch deny"
    pass=$((pass+1))
  else
    echo "  FAIL  designer webfetch not denied"
    fail=$((fail+1))
  fi
}
assert_designer_no_webfetch

if grep -Pq '^\s*webfetch:\s*allow\s*$' "$RESEARCHER"; then
  echo "  PASS  researcher webfetch allow"
  pass=$((pass+1))
else
  echo "  FAIL  researcher webfetch not allow"
  fail=$((fail+1))
fi

if grep -Pq '^\s*webfetch:\s*deny\s*$' "$CRITIC"; then
  echo "  PASS  critic webfetch deny"
  pass=$((pass+1))
else
  echo "  FAIL  critic webfetch not deny"
  fail=$((fail+1))
fi

echo
echo "== summary: $pass passed, $fail failed =="
[ $fail -eq 0 ] || exit 1
