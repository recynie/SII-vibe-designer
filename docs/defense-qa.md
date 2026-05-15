# 答辩 Q&A 备忘

预想答辩老师可能问的问题，提前准备的回答框架。不用背，只需现场抓重点。

---

## Q1. 你为什么选 opencode 做 harness，不自己写？

**短答**：题目允许直接使用现成开源 harness。opencode 1.4 已经覆盖了所有必需能力（subagent 独立上下文 / 任务调度 / 工具调用 / 错误处理 / 自定义 agent + skill + command），用现成框架让我们能把全部精力放在**设计领域知识**和**实测发现**上，而不是重复造轮子。

**关键点**：用 opencode 不等于"没工程"——我们的 4 个 agent + 4 个 skill + 1 个命令 + 4 个 Python 工具（gen_image / html_screenshot / verify_demo_panel / verify_facts）完全是自己设计的，opencode 只是 plumbing。

---

## Q2. 4 个 agent 各自做什么，为什么不是 3 个？

题目要求"至少 3 个"。我们设计了 4 个：

- **planner**（primary）—— 拆任务、调度、汇总
- **researcher**（subagent）—— 一次性把 brief 转成 brand-spec.md（独立 step，避免 planner 的 context 被搜索结果污染）
- **designer**（subagent）—— 出图 / 写 HTML / 写文案，按 skill 路由
- **critic**（subagent）—— 5 维度评审 + ImageMagick 像素级核对

为什么不合并 researcher 进 planner？**实测后发现**——researcher 涉及 WebSearch + 大量 markdown 写作，独立 subagent 让 planner 的主上下文保持精简，调度更稳定。

---

## Q3. critic 的 5 维度评分是怎么定的？

**核心 5 维度**（critic.md 标准定义，logo / poster 类视觉任务用这套）：

| 维度 | 检查什么 | 关键质问 |
|---|---|---|
| ① 品牌契合度 | 调性关键词 / 色板严格性 / 受众匹配 | "色是真用了 #1A2B4A，还是只用了'接近'?" |
| ② 信息层级 | 视觉重量 vs 信息重要度 / 留白 | "一眼看到的是不是最重要的信息？" |
| ③ 视觉品味 | 字体配对 / 色彩和谐 / 细节经得起放大 | "细节像不像设计师做的，不像 AI 默认产出？" |
| ④ 反 AI slop（一票否决） | 紫渐变 / emoji 图标 / Inter 当 display / SVG 画人 | 任一项命中即 ≤3 分，整体不通过 |
| ⑤ 任务完成度 | brief 要求是否覆盖 / HTML 是否能渲染 | "brief 里要的都做了吗？" |

**通过门槛**：总分 ≥ 35（5 项均值 7+）且无任何一项 ≤ 4。

**自适应**：critic 在 copy 任务上自主换成了「记忆点 / 语言精准度 / 情感共鸣 / 可扩展性」（见 `run-final-hardened/artifacts/copy/v1.review.md`，38/50 通过）；UI 把 "视觉品味" 换成 "视觉设计"。这是 LLM 推理结合任务类型的正常行为——`critic.md` 没硬编码字段名，只规定 5 个维度的"评判精神"。

**为什么是这 5 个不是别的**：前 3 维是设计本身的"质量基准线"，第 4 维是 AI 时代特有的"反平庸"门控（这是从 huashu-design 等开源 design skill 借鉴的最重要思想），第 5 维确保不偏离需求。

---

## Q4. 系统能避开 AI slop 吗？怎么避的？

两层防线：

1. **prompt 工程**：designer.md 显式列禁忌项（紫渐变、emoji 图标、generic stock、凭空品牌色等），每个 gen_image prompt 末尾都加 `no purple gradients, no emoji, no generic SVG faces`。
2. **critic 一票否决**：第 ④ 维度命中任一 slop 项就 ≤3 分，整体不通过 → 触发 v2 迭代。

**实测有效性**：所有 6 次 demo run 没有出现紫渐变 / emoji 图标。logo run-coffee-partial 的 critic v1 review 第 ④ 维 8/10，主动指出"未命中 slop 但视觉品味需提升"。

---

## Q5. 双图像后端怎么切换？谁决定？

`tools/gen_image.py` 读环境变量 `DESIGN_IMAGE_BACKEND`：
- `minimax`（开发，便宜）—— `image-01` 模型
- `openai`（默认/正式）—— `gpt-image-2` 模型

**LLM 完全感知不到**——designer 的 prompt 里只有"调 gen_image"。同一份 agent 配置在两个后端都能跑（milestone-30 Solenne run 实证）。

**实测差异**（milestone-21 evidence run）：
- minimax `#1F3A58` (与目标 #0D1B2A 距离 ~50)
- gpt-image-2 `#000A2E` (距离 ~22)

gpt-image-2 严格度高 2x+ 但中转站慢 4x+。

---

## Q6. 创智学院 brief 一定能跑通吗？跑了几次？

**6 次 e2e 提交**（完整 4 类 + 部分阶段 + 单图实证），全部产物已 commit：

1. `run-20260516-004106-chuangzhi/` — 创智学院完整版 14 min
2. `run-final-hardened/` — 创智学院强化版 12 min
3. `run-coffee-partial/` — 钝角咖啡（不同领域，logo 阶段）
4. `run-zhujiajiao-recovered/` — 朱家角（第 3 个领域 + 内容审查恢复实证）
5. `run-gpt-image-2-evidence/` — gpt-image-2 单图实证（hex 复现精度对比）
6. `run-solenne-gpt-image-2/` — Solenne 香水（gpt-image-2 后端首次完整 e2e 验证）

**从未跑炸过**——critic 不通过会触发 v2 迭代，2 轮上限会触发用户提问，从不死循环。

---

## Q7. 系统怎么知道 brief 写的是什么领域，调用对应风格？

不知道——也不需要。系统的工作方式是：

1. **researcher 用 LLM 推理领域** —— 收到"朱家角古镇"自然推断出"江南水乡 / 文旅"调性
2. **brand-spec.md 是 LLM 生成的中间表示**：色板、字体、参考方向、反 slop 禁区都是它写的，下游 designer / critic 只读这一份
3. **designer 按 skill 路由**：planner 给定子任务（logo / poster / copywriting / ui-mockup）+ 对应 skill 文件，designer 加载 skill 知识

也就是说**领域响应是 LLM 推理 + 文件传递**，不是硬编码 if-else。

实证：4 个不同领域（教育 / 咖啡 / 文旅 / 香水）的 brand-spec.md 各自给出截然不同的色板和参考方向。

---

## Q8. 系统的"已知局限"是什么？

诚实列出：

1. **MiniMax image-01 对深色 hex 严格度不够**：生产场景应切 gpt-image-2
2. **MiniMax-M2 不支持视觉输入**：critic 用 ImageMagick `identify` 间接验证颜色
3. **MiniMax-M2 中文内容审查偶发**（"output new_sensitive 1027"）：朱家角 brief 触发过；fallback 是 designer 切换纯英文 prompt
4. **gpt-image-2 通过 findcg.com 中转**：429 限流偶发，且整体慢 4x+
5. **subagent 偶发长 thinking**：`opencode --pure` 跳过外部插件干扰可缓解

每一条都在 `docs/architecture.md §8` 文档化，并在实际 demo run 中遇到过 + 解决方案落地。

---

## Q9. 这是个一次性 demo 还是真的能用？

**可复现性已实测**：

- `pyproject.toml` + `.env.example` 让 fresh clone `uv sync` 即可
- `tools/verify_demo_panel.py` 用 playwright 自动化检查 PPT 链接
- 同一 brief 在不同时间跑出来的 brand-spec.md 风格稳定（创智学院两次 run 都是 Pentagram 信息建筑派 + 墨蓝青色）

**不可保证**：每次跑的 logo 像素值不同（图像生成不确定性），但调性、色板、参考方向、产物结构稳定。

---

## Q10. 答辩演示怎么放？

打开 `docs/presentation/index.html`：

- ←/→ 翻页（3 页：架构 / 时序 / Demo）
- F 全屏
- **D 键打开 demo 面板**——一键跳转到任意 demo run 的 brief.md / final.md / README.md

如果老师想看具体的产物（logo 图、海报 HTML、文案 md），D 键面板的 6 个卡片直接到位。

---

## 后备：如果系统现场跑不出来

`docs/demo-runs/` 里 6 次完整 / 部分 run 的所有产物都 commit 了。即使现场网络/API key 失败，也能直接展示历史交付物。

每个 run 都有 `brief.md / brand-spec.md / plan.md / artifacts/.../v?.review.md`，能完整复现"这次 run 系统是怎么思考的"。
