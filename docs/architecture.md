# Vibe Design · 系统设计

基于 opencode harness 扩展的多智能体平面设计系统。接收自然语言 brief，自主完成需求理解、任务拆解、设计生成与评估优化，输出通用品牌设计结果（logo / 主视觉 / 文创 / 文案 / 简单 UI 等）。

题目里的"创智学院"和"朱家角"只是测试输入。系统不绑定任何特定主题，目录与代码不出现这两个名字。

---

## 1. 角色与边界

opencode 已提供 subagent（独立上下文）、plugin（自定义工具）、custom command、session/file 操作、任务调度、错误处理。**我们不重写 harness，只做扩展**：

| 工作 | 由谁负责 |
|---|---|
| 调度、上下文隔离、工具调用、错误处理 | opencode 原生 |
| 设计领域工具（`gen_image`、`save_artifact`） | 自写 plugin |
| 设计领域知识（4 个 agent 的 prompt） | 自写 markdown agent |
| 入口体验（`/design <brief>`） | 自写 custom command |

---

## 2. Agent 拓扑

```
            user: /design <brief>
                      │
                      ▼
            ┌────────────────────┐
            │ Planner (primary)  │  默认入口；拆任务、调度、汇总
            └──┬────────┬──────┬─┘
               │        │      │
        @researcher @designer @critic   subagents（独立上下文）
```

**Planner**（primary，主控）
- 解析 brief → 拆成具体子任务（logo / 主视觉 / 文案 / 应用物料）
- `@researcher` 收集背景 → 落 `brief.md` + `brand-spec.md`
- 对每个子任务循环：`@designer` → `@critic` → 不过则二次迭代 → 仍不过则向用户提问
- 最终汇总到 `outputs/<run-id>/`

**Researcher**（subagent）
- WebSearch + WebFetch 收集主题信息、参考、风格关键词
- 输出 `brief.md`（核心信息、受众、调性、约束）+ `brand-spec.md`（色板、字体、关键词）

**Designer**（subagent，单 agent + skill 路由）
- 调 `gen_image` 出图、写 HTML 排版、写文案
- 根据子任务类型加载不同 skill prompt（参考 `huashu-design`：logo / 海报 / 文案）
- 不出 HTML 草图（介质不匹配时草图无意义）；图直接出，HTML 直接写

**Critic**（subagent）
- 输入：实物（图片或 HTML 截图）+ designer 用的 prompt + brief
- 5 维评分：品牌契合 / 信息层级 / 视觉品味 / 反 AI slop / 任务符合度，每项 0-10
- 输出：总分 + 改进建议（区分"改 prompt"还是"改素材/版式"）+ 是否通过
- **同时审阅图像和 prompt**——很多问题根因在 prompt（如"加 emoji"导致俗气），让 critic 看 prompt 才能给出有效改法

---

## 3. 迭代策略

不同介质用不同迭代方式。**草图只在 draft 和 final 同介质时才有意义**。

| 产出 | 迭代方式 | 上限 |
|---|---|---|
| 图（logo / 插画 / 产品图） | designer 出图 → critic 评图+prompt → designer 改 prompt 重出 | 2 轮，超出向用户提问 |
| HTML 排版（海报版式 / UI mockup） | designer 直接出完整版 → playwright 截图 → critic 评 → designer 改样式 | 2 轮 |
| 文案 | designer 出 3 个变体 → critic 选优 + 给修改建议 → designer 改一轮 | 1 轮 |

`critic.md` 写明："基于已写盘的实物打分，不要凭空预测。改进建议要分清是 prompt 问题还是版式问题。"

---

## 4. 模型与图像后端

| 用途 | 模型 | 备注 |
|---|---|---|
| 所有 agent LLM | **MiniMax**（`MINIMAX_BASE_URL`） | opencode 顶层配置 |
| 图像生成（开发期） | MiniMax 文生图 | 迭代 prompt 时省钱 |
| 图像生成（正式 run） | **gpt-image-2**（默认） | 答辩与最终交付用 |

`gen_image` plugin 签名对 LLM 屏蔽后端：

```ts
gen_image({ prompt, output_path, aspect_ratio?, size? })
```

后端由 plugin 启动时读 `DESIGN_IMAGE_BACKEND` 环境变量决定（`openai`（默认） / `minimax`）。Designer prompt 里就一句"调 `gen_image`"，开发与正式跑同一份 agent 逻辑，避免后端切换引入差异。

---

## 5. 目录结构

```
vibe-design/                      # 项目根
├── opencode.json                 # 注册 agents + plugin + custom command + 模型
├── .opencode/
│   ├── plugins/
│   │   ├── gen-image.ts          # 自定义工具，路由 minimax / gpt-image-2
│   │   └── save-artifact.ts      # 写 outputs/<run-id>/ 的辅助
│   ├── agent/
│   │   ├── planner.md            # primary
│   │   ├── researcher.md         # subagent
│   │   ├── designer.md           # subagent + skill 路由说明
│   │   └── critic.md             # subagent
│   ├── command/
│   │   └── design.md             # /design <brief>
│   └── skills/                   # designer 加载的领域 prompt
│       ├── logo.md
│       ├── poster.md
│       ├── copywriting.md
│       └── ui-mockup.md
├── examples/                     # 三条不同领域 brief 验证泛化
│   ├── brief-sii-academy.md      # 题目要求的"创智学院"测试
│   ├── brief-zhujiajiao.md       # 参考案例的"朱家角"测试
│   └── brief-coffee-startup.md   # 第三条不同领域 brief
├── outputs/                      # 每次 run 一个子目录（gitignore）
└── docs/
    ├── architecture.md           # 本文件
    └── presentation/             # 答辩 PPT，与系统解耦
```

---

## 6. 关键文件契约

**`brief.md`**（researcher 写，下游读）
- 主题、目标受众、调性关键词、必含/禁含元素、交付清单

**`brand-spec.md`**（researcher 写，designer / critic 都读）
- 主色 / 辅色 HEX、字体建议、视觉气质、参考方向

**`outputs/<run-id>/`**
```
brief.md
brand-spec.md
plan.md                # planner 拆出的子任务清单
artifacts/
  logo/
    v1.png  v1.prompt.txt  v1.review.md
    v2.png  v2.prompt.txt  v2.review.md
  poster/
    v1.html  v1.png  v1.review.md
  copy/
    taglines-v1.md  taglines-v1.review.md
final.md               # planner 的最终交付说明
```

每个 artifact 同时保留 prompt 和 review，方便 critic 审阅、用户复盘、答辩展示。

---

## 7. 实施顺序

1. `opencode.json` + `.env` 接通 MiniMax，确认 opencode 能跑通基础对话
2. `gen-image.ts` plugin（先 MiniMax 后端） + `save-artifact.ts`，命令行测两次
3. `designer.md` + `critic.md`，跑通"出图 → 评 → 改"最小回路
4. 加 `researcher.md` + `planner.md`，串成完整链路
5. `/design` 命令 + `examples/brief-sii-academy.md` 端到端
6. 三条 example 都跑，验证"换主题就能跑"
7. 切 `DESIGN_IMAGE_BACKEND=openai` 用 gpt-image-2 出最终交付
8. 写答辩 PPT（≤3 页，重点架构图）

---

## 8. 交付物对照题目

| 题目要求 | 落点 |
|---|---|
| 至少三个智能体（Planner / Designer / Critic）+ 独立上下文 | §2，opencode subagent 天然独立 |
| 必要的设计工具（文生图等） | `gen-image.ts` plugin |
| Agent Harness 框架 | opencode（题目允许直接用现成开源） |
| 任务调度 / 信息传递 / 上下文管理 / 错误处理 / 迭代优化 | opencode 原生 + `critic` 闭环（§3） |
| 命令行交互 | opencode TUI + `/design` 命令 |
| 创意文案生成 | designer 加载 `copywriting.md` skill |
| "请为创智学院做一套品牌形象设计" 端到端 | `examples/brief-sii-academy.md` |
| ≤3 页技术 PPT + 架构图 | `docs/presentation/` |
