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

主 README 顶部加状态标识 + 当时已有的 demo run 评分对照表（彼时 3 个），让读者一眼看到系统真跑过。后续 milestone 持续追加，最终为 6 个。

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
  - `run-zhujiajiao-recovered/` — 朱家角古镇（验证 milestone-16 内容审查 fallback）

---

## milestone-16 · content-moderation recovery in designer/planner

`milestone-13` 揭露的 MiniMax `output new_sensitive (1027)` 不仅文档化，还要 agent 真能恢复。

- `designer.md` 加 fallback：触发审查时用纯英文 + hex + 英文色名（"sage green #4A7C59" 而非"竹青"），简化 thinking chain，2 次连续触发后写 `BLOCKED.md` 标注阻塞
- `planner.md` 加配套 escalation：第一次让 designer 自恢复，第二次写 BLOCKED.md 跳过任务继续

## milestone-17 · zhujiajiao recovered run validates milestone-16 fallback

实跑朱家角 brief 验证 fallback：

- 同一 brief 在 milestone-16 之前会被审查阻塞，之后**完全跑通到 logo v2 阶段**
- Designer 自主切换到纯英文 prompt（"Fangsheng Bridge" / "sage green"），未再触发审查
- Logo v1 + v2 各 3 个变体生成，每轮都有 critic 评审
- v2 仍因色彩复现问题不通过，Planner 规范地停下问用户 (a)/(b)/(c)——这次**没**像创智学院那次自我反思后强行继续

记号：`run-zhujiajiao-blocked/` 被替换为 `run-zhujiajiao-recovered/`。

## milestone-18 · README + CHANGELOG sync

README 主表 + CHANGELOG 末尾的 demo run 引用从 `run-zhujiajiao-blocked` 更新为 `run-zhujiajiao-recovered`，与实际提交目录一致。

## milestone-19 · PPT slide-2 第 6 条设计纪律

`docs/presentation/02-sequence.html` 关键设计纪律从 5 条扩到 6 条，新增第 ⑥ 条「内容审查可恢复」，把 milestone-16 + 17 的故事链（发现问题 → designer fallback 设计 → 实跑验证）写进答辩 PPT。同步重新渲染 `02-sequence.png`。

## milestone-20 · CHANGELOG 记录 milestone-18 + 19

CHANGELOG 之前停在 milestone-17，本次补完 18（README 同步）和 19（PPT 第 6 纪律）。

## milestone-21 · gpt-image-2 hex 色彩复现实证

`docs/architecture.md` §8 推论"生产用 gpt-image-2 严格"——本 milestone 用单次实测证明：

| 后端 | 同 prompt 下最深像素 | 与目标 #0D1B2A 距离（RGB） |
|---|---|---|
| minimax `image-01`（hardened v2）| `#1F3A58` | ~50 |
| **gpt-image-2** | **`#000A2E`** | **~22** |

新增 `docs/demo-runs/run-gpt-image-2-evidence/`：单图 + prompt + 直方图分析 README。证明 `DESIGN_IMAGE_BACKEND` env 切换的双后端架构真正有差异化价值——designer.md prompt 不需要切换，同一份逻辑跑两个后端。

## milestone-22 ~ 23 · README 同步 + 性能/成本数据

- 22: README run table 加入 gpt-image-2-evidence 行 + CHANGELOG 衔接 milestone-20+21
- 23: README 加性能小节，列 4 个 demo run 的实测时长（12-14 min 完整 4 类产物）+ 文件数 + 大小 + LLM turns 粗估，方便答辩 Q&A

## milestone-24 ~ 26 · 答辩演示工具链

- 24: PPT `index.html` 加 D 键 demo 面板（半透明蓝 overlay + 白卡片网格），一键跳转任意 demo run。Esc 关闭
- 25: 修复面板死链——`run-coffee-partial` 和 `run-zhujiajiao-recovered` 没 final.md，改链 brief.md
- 26: 写 `tools/verify_demo_panel.py` —— playwright 模拟 D 键打开面板、抓所有 hrefs、解析检查文件存在性。一行命令验证答辩 PPT 不会出现死链

## milestone-27 ~ 29 · README 文档完善

- 27/29: README 状态徽章不再硬编码 milestone 数（自动追随 git log，不再每 commit 都要更）
- 28: README 加 Sanity check 子节，列 verify_demo_panel.py + gen_image.py 命令

## milestone-30 ~ 31 · gpt-image-2 完整 e2e 验证

- 30: Solenne 香水品牌 brief 在 `DESIGN_IMAGE_BACKEND=openai` 后端跑通完整 researcher → planner → designer → critic 闭环，证明双后端架构在 pipeline 层面也透明（agent prompts 不变）。logo 32/50（颜色仍偏离），用 ImageMagick 像素级评审。
- 31: README run table + PPT D-key 面板都同步到 6 个 demo runs。verify_demo_panel.py 保证全链可达。

## milestone-32 ~ 38 · 答辩准备深化

- 32: CHANGELOG 批量补完 milestone-22..31
- 33: 新写 `docs/defense-qa.md` 10 题预设答案，避免现场翻 critic.md
- 34: README 链接到 defense-qa.md
- 35: 手工对账发现 defense-qa Q1 / Q6 事实漂移（当时写的"2 个 Python 工具"、"4 次 e2e"），修复
- 36: 新写 `tools/verify_facts.py` —— 自动跨文档检查"X 个 agent / skill / 工具 / demo run"等数字与仓库实际一致。首次跑出 3 个未发现漂移，全修
- 37: README 文档化 verify_facts.py
- 38: 新写 `scripts/check.sh` —— 一键跑 verify_facts + verify_demo_panel + 工作树清洁检查，输出 `═══ ALL OK · ready for defense ═══`

## milestone-39 ~ 41 · 答辩材料润色

- 39: architecture.md 目录树更新：原本只列了 agent-callable 的工具，加上了 verify_demo_panel + verify_facts 这两个内部质检工具并标注它们的不同用途
- 40: README run table 把 `run-final-hardened/` 标为 ★ **题目正式交付物**，避免老师从字母序第一个开始看
- 41: PPT D-key 面板的 final-hardened 卡片视觉突出（橙色 #FF6B35 边框 + grid-column: 1/-1 全宽 + ★ 前缀）。histogram 实测 5412 像素 #FF6B35 显著

## milestone-42 ~ 46 · critic 维度自适应实证

- 42: defense-qa Q3 加入"critic 在 copy 任务自适应换维度"的解释，对齐实测行为
- 43: critic.md 显式说"copy 任务允许换维度，但 ① ④ ⑤ 必须保留"
- 44: 跑 Foundry Lab 纯文案 brief 实测 milestone-43 规则——结果发现 critic **完全换了 5 个新维度**（克制 / 动手气质 / 精准 / 记忆点 / 调性统一），LLM 行为不遵守"必须保留"。但实测 LLM 选的轴更贴切。决策：让 critic.md 反过来——完全允许文案换轴，反 slop 作为隐性原则。`run-foundry-copy/` 提交为第 7 个 demo run（4 min e2e，三任务全过 41-42/50）
- 45: README 表 + PPT 面板同步到 7 demo runs
- 46: defense-qa.md verify_facts 抓出 3 处 "6 次" 残留，全部更新 + 把 7 个 run 列表重排（题目正式交付列首位）

