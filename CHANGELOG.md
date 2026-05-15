# Changelog

13 个 milestone 的演进，记录关键决策与实测发现。

---

## milestone-1 · scaffold + tools

初始项目骨架 + Python 图像生成 CLI。

- `vibe-design/` 项目根，`opencode.json` 配 MiniMax-M2 provider
- 4 个 agent（planner / researcher / designer / critic）+ 4 个 skill
- `tools/gen_image.py` 双后端路由（DESIGN_IMAGE_BACKEND env）
- 实测 minimax + gpt-image-2 端点都通

## milestone-2 · serial scheduling for planner

诊断到 MiniMax-M2 reasoning 在并行 subagent 调度下挂起 5+ 分钟。

修复：planner.md 强制串行（`一次只 @ 一个 subagent`），designer.md 加紧迫感纪律。

## milestone-2 · end-to-end pipeline verified

第一次完整端到端跑通（最小验证版 logo + slogan）：2 分 30 秒。

发现 `--pure` 必须用——用户全局 `oh-my-opencode-slim` 注入"parallelize"workflow rules 干扰 subagent。

## milestone-3 · presentation slides + full pipeline running

3 页 HTML 答辩 PPT（1920×1080）。完整版 pipeline 同时启动。

## milestone-4 · full e2e run with all 4 deliverables + critic loop

14 分钟跑完全套：

| 任务 | 评分 |
|---|---|
| Logo（v1 → v2 自主迭代） | 19/50 → 28/50 |
| Copy | 40/50 ✅ |
| Poster | 46/50 ✅ |
| UI Mockup | 44/50 ✅ |

发现 MiniMax-M2 不支持视觉输入；critic 自主选用 ImageMagick `identify -format %[hex:u]` 提取颜色 hex 与 brand-spec 比对。

## milestone-5 · presentation deck + generalization validation

钝角咖啡 brief（完全不同领域）跑通到 logo critic 阶段：

- 色板：深炭灰 + 焦糖棕（vs SII 墨蓝 + 青绿）
- 参考方向：原研哉东方极简（vs SII Pentagram 信息建筑派）
- 反 slop 禁区针对工业风加了"过度圆润边角"

证明系统真在做领域推理，不是模板填空。

## milestone-6 · sync architecture.md with implementation reality

文档同步实测：

- 移除原计划的 TS plugin 描述（实际用 Python CLI）
- §8 新章节"实测发现与已知限制"
- §9 交付物对照实际路径

## milestone-7 · harden agents based on empirical findings

- critic.md：明确写入"用 `identify -format` 提取实际 hex 与 brand-spec 比对"作为评审固定步骤
- designer.md：prompt 写作指引强调 `STRICTLY use only #XXX` 强约束（实测 MiniMax image-01 对软描述会"美化"成偏色）

## milestone-8 · hardened-prompt run validates iteration improvement

12 分钟重跑创智学院 brief，验证 hardening 真起效：

| 变体 | v1 主色 | v2 主色 | 与目标 #0D1B2A 的距离 |
|---|---|---|---|
| logo mark | `#F8F4E8` 米白 | **`#1F3A58`** 深蓝灰 | 显著缩小 |

Planner 在 v2 仍未通过时显示**自我反思**："我注意到自己陷入了过度分析"，主动决定标记限制 + 继续后续任务，体现 agent 自主意识。

Poster 42/50 · Copy 38/50 · UI 45/50 全部通过。

## milestone-9 · README status badge + run summary table

主 README 顶部加状态标识 + 3 次 demo run 评分对照表，让读者一眼看到系统真跑过。

## milestone-10 · 3rd domain brief validates researcher generalization

朱家角古镇 brief 跑 researcher 阶段（1 分钟）：

- 色板：黛青 #1A2634 + 朱砂 #C41E3A + 宣纸白 #F5F2EB（呼应"朱家角"地名典故）
- 字体：思源宋体 Display（vs SII / Coffee 都用 Sans display）
- 调性：水墨留白 + 江南雅致 + 当代极简

3 个独立 brief 三个截然不同的输出，researcher 真在做领域推理。

## milestone-11 · reproducibility assets for fresh clone

- `pyproject.toml` 加真实 deps（playwright）
- `.env.example` 文档化所需 key + 后端切换
- 删除 `main.py` boilerplate

Fresh clone 验证：`uv sync` + `cp .env.example .env` 即可让 tools 工作。

## milestone-11b · README quickstart matches .env.example

quickstart 步骤改成"`cp .env.example .env` 后填 key"，与新增的模板对齐。

## milestone-12 · ignore source assignment markdown

题目原 brief markdown 加进 .gitignore（已有 PDF 版本，平等处理 MD）。工作树第一次零未提交。

## milestone-13 · zhujiajiao content moderation block

朱家角完整 pipeline 跑出 brief.md + brand-spec.md + plan.md 后，designer logo 阶段被 MiniMax 内容审查反复拦截（`output new_sensitive 1027`，推测"朱砂"+"墨"等中文词组合触发）。

`docs/architecture.md` "已知限制"加了这一条。绕过策略：改写 prompt 避开触发词 / 切换非 MiniMax LLM / 在 final.md 让用户人工补做。

---

## 最终交付

- **代码**：4 agent + 4 skill + 1 command + 2 Python tool + 3 example brief
- **文档**：README.md + docs/architecture.md
- **PPT**：3 页 1920×1080 HTML 幻灯片（浏览器键盘翻页）
- **Demo runs**（4 个，覆盖 3 个领域）：
  - `run-20260516-004106-chuangzhi/` — 创智学院完整版（14 min）
  - `run-final-hardened/` — 创智学院强化版（12 min）
  - `run-coffee-partial/` — 钝角咖啡（logo 阶段）
  - `run-zhujiajiao-blocked/` — 朱家角古镇（researcher + plan，designer 被内容审查拦）
