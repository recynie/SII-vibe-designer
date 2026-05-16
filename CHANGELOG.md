# Changelog

主要节点。详细演进见 `git log --oneline`。

## 系统骨架

- 项目骨架 + opencode.json 配 MiniMax-M2 provider
- 4 个 agent（planner / researcher / designer / critic）+ 4 个 skill（logo / poster / copywriting / ui-mockup）
- `tools/gen_image.py` 双后端文生图（minimax / gpt-image-2，env 切换）
- `tools/html_screenshot.py` HTML → PNG（playwright/chromium）
- `/design` custom command
- 3 条 example brief：SII / 朱家角 / 钝角咖啡

## 架构纪律

- **opencode --pure 必须用**：跳过用户全局插件 `oh-my-opencode-slim` 注入的 "parallelize" workflow rules，否则 subagent 长时间挂起
- **subagent 严格串行调度**：MiniMax-M2 reasoning 在并行下偶发 5+ 分钟无产出
- **文件即上下文契约**：subagent 间不互相 @，全部信息流经 `brief.md` / `brand-spec.md` / `v?.review.md`
- **designer 类型路由**：copywriting 走 Write，logo/poster 走 bash + gen_image，避免决策犹豫
- **critic 用 ImageMagick 间接验证颜色**：MiniMax-M2 不支持视觉输入，用 `identify -format %[hex:u]` 提取实际色值与 brand-spec 比对

## 实测发现

- **MiniMax image-01 对深色 hex 复现不严格**：墨蓝 #0D1B2A 会被生成为浅蓝/米白。强约束 prompt（`STRICTLY use only #XXX` + 颜色名 + hex 双标）能让色彩从完全偏离逼近到接近目标
- **gpt-image-2 显著严格**：实测最深像素 #000A2E 与目标 #0D1B2A 距离仅 ~22；minimax 同 prompt 下 ~50
- **MiniMax-M2 内容审查偶发**（`output new_sensitive 1027`）：朱家角文旅 brief 触发；fallback 是 designer 切换纯英文 prompt + hex+色名（"sage green #4A7C59" 而非"竹青"）
- **critic 维度自适应是特性**：copy 任务自主换成「克制 / 动手气质 / 精准 / 记忆点 / 调性统一」等更贴切的轴；视觉任务保留标准 5 维。critic.md 已显式允许

## 7 个 demo runs

- `run-final-hardened/` — ★ 题目正式交付：创智学院强化版 12 min 4 类全套
- `run-20260516-004106-chuangzhi/` — 创智学院早期版本 14 min（critic 触发 v2 自主迭代实证）
- `run-coffee-partial/` — 钝角咖啡（不同领域，像素级 critic）
- `run-zhujiajiao-recovered/` — 朱家角（第 3 个领域，验证内容审查 fallback）
- `run-gpt-image-2-evidence/` — gpt-image-2 单图实证（直方图对比）
- `run-solenne-gpt-image-2/` — Solenne 香水（gpt-image-2 后端首次完整 pipeline）
- `run-foundry-copy/` — Foundry Lab 纯文案（critic 维度自适应实证）
