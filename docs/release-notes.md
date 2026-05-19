# Release Notes

## v1.2 — 视觉评审简化（2026-05-19）

视觉类评审统一改为 critic 直接看图判断。颜色要求为与 brand-spec 大体一致，不要求像素级精确。

### 改进

- **Critic 直接看图**：critic 使用 Read 读取 PNG / 截图后，基于实物观察评估调性、构图、信息层级和颜色大体一致性。
- **validate.py 简化**：机器层只保留 HTML 字族硬门槛；PNG 和纯文不做机器视觉判断。
- **Designer / asset-prep 自检同步**：产物完成后通过 Read 目视检查颜色、构图、内容完整性。
- **测试同步**：移除旧的颜色工具测试断言，保留字族与 prompt 结构断言。

### 改动文件

- `vibe-design/.opencode/agent/critic.md` — 重写为“机器字族校验 → Read 实物 → 主观评分”流程
- `vibe-design/tools/validate.py` — 简化机器校验聚合逻辑
- `vibe-design/.opencode/agent/designer.md`、`planner.md`、`skills/asset-prep/SKILL.md` — 同步颜色目视判断规则

---

## v1.1 — 视觉读图增强（2026-05-19）

Critic 和 Designer 获得视觉理解能力，评审和自检不再“盲猜”。

### 改进

- **Critic 读图评审**：机器校验通过后，critic 用 Read 工具读取实物 PNG，基于实际看到的图像内容打主观分。评分备注必须引用具体视觉观察（如“表单被截断”“主体偏左”），禁止写空话
- **Designer 视觉自检**：生成 PNG 后立即 Read 查看，检查内容截断、调性跑偏、元素缺失等一眼可见的硬伤，就地修复后再交给 critic，减少不必要的 v2 迭代
- **Planner 调度模板同步**：critic 调度指令明确要求“Read 读取实物文件，基于视觉观察打分”

### 验证

- M1-M5 回归测试 89/89 全过
- 端到端验证：critic 准确识别落地页 PNG 底部表单被截断（任务完成度 2/5），这是只有真正看图才能发现的问题

### 改动文件

- `vibe-design/.opencode/agent/critic.md` — 新增读取实物步骤，更新主观打分指导语和纪律段
- `vibe-design/.opencode/agent/designer.md` — 新增视觉自检段
- `vibe-design/.opencode/agent/planner.md` — critic 调度模板补充读图指令

---

## v1.0 — M1-M5 框架完成（2026-05-17）

从经验驱动的 prompt 迭代转向结构化的 schema 校验 + 必要机器校验 + 主观评分分离体系。7 个 demo run 验证通过，81 项自动化测试覆盖。

### M1 · Schema 定义 + 校验工具

- 定义 facts / brand-spec / deliverables 三份结构化 schema
- 独立校验脚本：`validate_facts.py`、`validate_brand_spec.py`、`validate_deliverables.py`、`check_html_fonts.py`
- mock 测试套件（compliant / violation）

### M2 · Researcher 重构

- facts → brand-spec → deliverables 顺序锁死，资源优先（`[from-fact:]` 先于 `[inferred:]`）
- 严格度自适应（deliverables ≥ 4 → strict，否则 light）
- 资源下载到 `assets/`，自跑 M1 校验后才回报 planner

### M3 · Planner 收窄到 process 层

- 删除“四件套”硬性条款，改为读 `deliverables.md` 按 `mode: create|reuse` 路由
- Planner 不增删 deliverables，疑虑写 `escalate.md`
- fast-skip 档：critic 反馈无法通过 prompt 修复时直接 escalate，不浪费 v2 轮次

### M4 · Designer 双模式 + Skills 退化

- 显式 `create` vs `reuse` 双分支路由
- 4 个旧 skill 退化为介质工艺手册（总字节 -76.3%），删除 prompt 填空模板
- 新增 `asset-prep` skill（本地素材处理手册）

### M5 · Critic 机器化 + 主观分离

- 评分流程顺序固定：schema / 字族硬门槛 → 读取实物 → 5 维度主观打分
- 评分尺度 0-5（锚定含义），通过门槛 ≥ 18/25 且无单项 ≤ 2
- `validate.py` 一键聚合必要校验，critic 只需一次 CLI 调用

### 端到端验证 & Demo Runs

- 7 个 demo run 覆盖 4 个领域（创智学院 / 钝角咖啡 / 朱家角 / Solenne 香水）+ 纯文案任务 + gpt-image-2 后端 + 内容审查 fallback
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
- designer 类型路由：copywriting 走 Write，logo/poster 走 gen_image
- critic 基于已写盘实物评审

### 首次端到端

- 创智学院完整 4 类交付：logo / 品牌文案 / 主视觉海报 / 官网首页 mockup
- Critic 闭环验证：v1 logo 调性不足 → 自动启动 v2 prompt 强化
- 发现部分图像后端对深色品牌调性的复现不稳定，生产场景优先使用 gpt-image-2
