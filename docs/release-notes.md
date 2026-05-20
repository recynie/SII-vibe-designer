# Release Notes

## v1.1 — 视觉读图增强（2026-05-19）

Critic 和 Designer 获得视觉理解能力，评审和自检不再"盲猜"。

### 改进

- **Critic 读图评审**：机器校验通过后，critic 用 Read 工具读取实物 PNG（opencode 自动转 base64 送视觉输入），基于实际看到的图像内容打主观分。评分备注必须引用具体视觉观察（如"表单被截断""主体偏左"），禁止写空话
- **Designer 视觉自检**：生成 PNG 后立即 Read 查看，检查内容截断、调性跑偏、元素缺失等一眼可见的硬伤，就地修复后再交给 critic，减少不必要的 v2 迭代
- **Planner 调度模板同步**：critic 调度指令明确要求"Read 读取实物文件，基于视觉观察打分"

### 验证

- M1-M5 回归测试 89/89 全过
- 端到端验证：critic 准确识别落地页 PNG 底部表单被截断（任务完成度 2/5），这是只有真正看图才能发现的问题

### 改动文件

- `vibe-design/.opencode/agent/critic.md` — 新增 ② 读取实物步骤，更新主观打分指导语和纪律段
- `vibe-design/.opencode/agent/designer.md` — 新增视觉自检段
- `vibe-design/.opencode/agent/planner.md` — critic 调度模板补充读图指令

---

## v1.0 — M1-M5 框架完成（2026-05-17）

从经验驱动的 prompt 迭代转向结构化的 schema 校验 + 机器评审 + 主观评分分离体系。7 个 demo run 验证通过，81 项自动化测试覆盖。

### M1 · Schema 定义 + 校验工具

- 定义 facts / brand-spec / deliverables 三份结构化 schema
- 6 个独立校验脚本：`validate_facts.py`、`validate_brand_spec.py`、`validate_deliverables.py`、`extract_artifact_palette.py`、`check_palette_compliance.py`（ΔE76 Lab 距离）、`check_html_fonts.py`
- mock 测试套件（compliant / violation）

### M2 · Researcher 重构

- facts → brand-spec → deliverables 顺序锁死，资源优先（`[from-fact:]` 先于 `[inferred:]`）
- 严格度自适应（deliverables ≥ 4 → strict，否则 light）
- 资源下载到 `assets/`，自跑 M1 校验后才回报 planner

### M3 · Planner 收窄到 process 层

- 删除"四件套"硬性条款，改为读 `deliverables.md` 按 `mode: create|reuse` 路由
- Planner 不增删 deliverables，疑虑写 `escalate.md`
- fast-skip 档：critic 反馈无法通过 prompt 修复时直接 escalate，不浪费 v2 轮次

### M4 · Designer 双模式 + Skills 退化

- 显式 `create` vs `reuse` 双分支路由
- 4 个旧 skill 退化为介质工艺手册（总字节 -76.3%），删除 prompt 填空模板
- 新增 `asset-prep` skill（ImageMagick 食谱）

### M5 · Critic 机器化 + 主观分离

- 评分流程顺序固定：schema 硬门槛 → 字族硬门槛 → 色板参考（不阻断） → 5 维度主观打分
- 色板检查降级为参考：ΔE 数据写入 review 但不单独阻断通过
- 评分尺度 0-5（锚定含义），通过门槛 ≥ 18/25 且无单项 ≤ 2
- `validate.py` 一键聚合校验，critic 只需一次 CLI 调用

### 端到端验证 & Demo Runs

- 7 个 demo run 覆盖 4 个领域（创智学院 / 钝角咖啡 / 朱家角 / Solenne 香水）+ gpt-image-2 后端 + 内容审查 fallback
- 解决 external_directory 死锁、escalate 未落盘、评分尺度残留等实测问题
- Deliverables 上限规则（显式 + 隐式 ≤ 5）防止 researcher 过度扩展

### 基础设施

- milestone-5 至 milestone-52 的文档、答辩材料、sanity check 脚本
- `verify_facts.py` 跨文档事实一致性检查
- `scripts/check.sh` 一键答辩前健全性门控

---

## v0.1 — 首次端到端跑通（2026-05-16）

从零搭建多智能体协同设计系统，完成首次全流程验证。

### 系统骨架

- 基于 opencode 1.4 harness，4 个 agent：planner（primary）/ researcher / designer / critic（subagent）
- `tools/gen_image.py` 双后端文生图（MiniMax `image-01` / `gpt-image-2`）
- `tools/html_screenshot.py` HTML → PNG（Playwright / Chromium）
- `/design` 自定义命令入口

### 架构决策

- subagent 严格串行调度（MiniMax-M2 并行会挂起）
- 文件即上下文契约：agent 间不互相 @，信息流经 `facts.md` / `brand-spec.md` / `v?.review.md`
- designer 类型路由：logo/poster 等视觉产物走 gen_image，HTML 类产物走 html_screenshot
- critic 用 ImageMagick 间接验证颜色（MiniMax-M2 不支持视觉输入）

### 首次端到端

- 创智学院完整视觉交付：logo / 主视觉海报 / 官网首页 mockup
- Critic 闭环验证：v1 logo 颜色不符 → 自动启动 v2 prompt 强化
- 发现 MiniMax image-01 对深色 hex 复现不严格（ΔE ~50 vs gpt-image-2 的 ~22）
