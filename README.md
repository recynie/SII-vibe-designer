# Vibe Design · 多智能体协同设计系统

> 基于 [opencode](https://opencode.ai/) harness 扩展的命令行设计 agent。一句话 brief 输入，多 agent 协同输出 logo / 主视觉 / 品牌文案 / UI mockup。

**状态**：✅ 端到端验证通过 · 7 次 demo run 已提交 · 完整迭代历史见 [CHANGELOG.md](./CHANGELOG.md)

> 🎯 **题目正式交付物 → [`docs/demo-runs/run-final-hardened/`](./docs/demo-runs/run-final-hardened/)**（创智学院 4 类全套、12 分钟、强化 prompt 版本）。其余 6 个 run 是泛化、技术验证或恢复实证。

| Run | Brief | 时长 | 产物 | 评分 / 备注 |
|---|---|---|---|---|
| **`docs/demo-runs/run-final-hardened/`** ★ | **创智学院（题目要求）** | 12 min | 4 类全套 | logo 27/50（颜色逼近 #0D1B2A）· copy 38 · poster 42 · ui 45 |
| `docs/demo-runs/run-20260516-004106-chuangzhi/` | 创智学院（早期版本） | 14 min | 4 类全套 | logo 28/50（v1→v2 迭代触发）· copy 40 · poster 46 · ui 44 |
| `docs/demo-runs/run-coffee-partial/` | 钝角咖啡（不同领域，泛化测试） | logo 阶段 | brief + spec + logo + critic | logo 36/50（像素级评审） |
| `docs/demo-runs/run-zhujiajiao-recovered/` | 朱家角古镇（第 3 领域） | logo 阶段 | brief + spec + plan + 6 logos + 2 reviews | 验证 milestone-16 内容审查 fallback |
| `docs/demo-runs/run-gpt-image-2-evidence/` | hex 色值复现实证 | 单次 | gpt-image-2 单图 + 直方图分析 | 实测 #000A2E 接近目标 #0D1B2A，验证生产后端 |
| `docs/demo-runs/run-solenne-gpt-image-2/` | Solenne 香水（gpt-image-2 后端） | logo 阶段 | brief + spec + plan + logo + critic | 32/50 · 第一次完整 e2e 跑生产后端，证明双后端架构透明性 |
| `docs/demo-runs/run-foundry-copy/` | Foundry Lab（纯文案任务） | 4 min | brief + spec + plan + 3 文案 + 3 reviews + final | 验证 critic 维度自适应：slogan / intro / apps 各 41-42/50 |

## 课题对照

| 题目要求 | 落点 |
|---|---|
| 至少三个智能体（规划 / 执行 / 评估）+ 独立上下文 | `vibe-design/.opencode/agent/` 下 4 个 agent：planner（primary）+ researcher / designer / critic（subagent） |
| 必要的设计工具（文生图/图生图等） | `vibe-design/tools/gen_image.py` 双后端文生图 + OpenAI-compatible 图生图/编辑 + `html_screenshot.py` |
| Agent Harness 框架 | opencode 1.4 现成框架（题目允许） |
| 任务调度 / 信息传递 / 上下文管理 / 错误处理 / 迭代优化 | opencode 原生 + critic 闭环（5 维度评分 + v1→v2 迭代） |
| 命令行交互 | opencode TUI + 自定义命令 `/design` |
| 创意文案生成 | designer 加载 `copywriting` skill |
| "请为创智学院做一套品牌形象设计"端到端 | `docs/demo-runs/run-20260516-004106-chuangzhi/` 完整 14 分钟跑通 |
| ≤3 页技术 PPT + 架构图 | `docs/presentation/` 三页 HTML 幻灯片 |

## 系统架构

```
            user: /design <brief>
                      │
                      ▼
            ┌────────────────────┐
            │ Planner (primary)  │  调度、汇总、迭代闭环
            └──┬────────┬──────┬─┘
               │        │      │
       @researcher @designer @critic   subagents · 独立上下文 · 串行调度
                      │
              ┌───────┴────────┐
              │                │
        gen_image.py    html_screenshot.py
        (minimax /     (Playwright /
         gpt-image-2)  Chromium)
```

详见 `docs/architecture.md`。

## 快速开始

```bash
# 1. 安装依赖（playwright 用于 html_screenshot，gen_image.py 只用标准库）
uv sync
uv run playwright install chromium

# 2. 配置 API 凭据
#   - api.toml：Python 脚本读，含 [active] llm/image + [providers.*]
cp api.toml.example api.toml
# 编辑 api.toml，填入真实 key
#   - .env：opencode 读（{env:MINIMAX_API_KEY}），照旧维护
cp .env.example .env
# 编辑 .env，至少填 MINIMAX_API_KEY

# 3. 进入项目目录
cd vibe-design

# 4. 启动 opencode（--pure 跳过外部插件干扰；.env 自动注入环境）
opencode --pure

# 5. 在 TUI 输入：
/design 请为创智学院做一套品牌形象设计

# 或非交互一次性跑完：
opencode run --pure --agent planner '请为创智学院做一套品牌形象设计'
```

输出落 `vibe-design/outputs/<run-id>/`。

## 健全性检查

```bash
# 检查 README / CHANGELOG 的事实陈述与实际仓库一致
uv run python vibe-design/tools/verify_facts.py

# 单独测试图像生成端点
uv run python vibe-design/tools/gen_image.py \
  --prompt "minimal flat vector logo, geometric, navy + cyan, no slop" \
  --output /tmp/test.png --backend minimax  # or --backend openai

# 图生图 / 编辑（OpenAI-compatible edits；默认建议单候选）
uv run python vibe-design/tools/gen_image.py \
  --input-image /tmp/test.png \
  --prompt "preserve the geometry, recolor strictly to navy and cyan" \
  --output /tmp/test-edit.png --backend openai --candidates 1
```

## 端到端验证

### Run 1 · 创智学院（题目要求的 brief）

`docs/demo-runs/run-20260516-004106-chuangzhi/` — 14 分钟全流程：

| 任务 | 工具链 | Critic 评分 |
|---|---|---|
| Logo 主标志（mark/wordmark/combo） | gen_image | v1 19/50 → v2 28/50（颜色生成限制） |
| 品牌文案（slogan + 简介 + 应用文案） | LLM 直接 Write | 40/50 ✅ |
| 主视觉海报（HTML + 配图） | gen_image + HTML + screenshot | 46/50 ✅ |
| 官网首页 mockup（落地页） | HTML + screenshot | 44/50 ✅ |

**自主迭代触发**：critic 发现 v1 logo 颜色与 brand-spec 不符，自动启动 v2 prompt 强化（加 `STRICTLY use #1A2B4A`）。v2 仍受底层模型限制时，planner 正确选择"非阻塞继续后续任务 + final 标注问题"——人在环路设计的实际表现。

### Run 2 · 钝角咖啡（验证泛化）

完全不同领域 brief，系统响应也完全不同：
- brand-spec 推断出深炭灰 + 焦糖棕（vs SII 的墨蓝 + 青绿）
- 参考方向选原研哉东方极简（vs SII 的 Pentagram 信息建筑派）
- 反 slop 禁区针对工业风加了"过度圆润边角"

证明系统不依赖训练语料里的特定主题。

## 性能与资源开销

> 下表是 2026-05 中旬跑的 4 个 demo run（**当时**主 LLM = MiniMax-M2.7-highspeed，图像 = minimax `image-01`）。当前主 LLM 已切到 SII `gpt-5.5`，单 turn 时延与 thinking 占比都明显变化；下表保留作历史参照，不代表现状。

| Run | 时长 | 文件 | 总大小 | 图像数 | LLM turns（粗估） |
|---|---|---|---|---|---|
| 创智学院（v1） | 14 min | 32 | 1.5M | 10 PNG | ~14（researcher 1 + planner 6 + designer 4 + critic 4） |
| 创智学院（hardened） | 12 min | 31 | 1.2M | 8 PNG | ~14 |
| 钝角咖啡 | logo 阶段 | 11 | 208K | 3 PNG | ~5（researcher 1 + planner 2 + designer 1 + critic 1） |
| 朱家角古镇 | logo 阶段 | 19 | 544K | 6 PNG | ~7 |

观察（基于 MiniMax-M2 时代的实测）：

- **完整 4 类产物 ~12-14 分钟**，单 logo 任务 ~2-3 分钟（含 LLM thinking + 图像生成 + critic 评审）
- **subagent 串行调度** 是主要时延源——MiniMax-M2 reasoning 单 turn 平均 30-60 秒（GPT-5.5 单 turn 显著更快，但同 brief 端到端时长尚未系统重测）
- **gen_image 单图 ~5-15 秒**（minimax）/ ~30 秒+（gpt-image-2 含中转站）
- **token 开销**：MiniMax-M2 thinking 占 70%+ tokens；GPT-5.5 下 thinking 占比显著降低

## 项目结构

```
SII-assignment/
├── api.toml                      # Python 脚本的 API 凭据（gitignore），schema 见 api.toml.example
├── api.toml.example              # 凭据 schema 模板
├── .env                          # opencode 用的环境变量（{env:MINIMAX_API_KEY}），gitignore
├── scripts/
│   ├── test_api.py               # 夏令营 API 中转站可用性测试（读 api.toml）
│   ├── test_llm_capabilities.py  # LLM 能力对比（读 api.toml）
│   └── test_sii_vision.py        # 视觉理解对比（读 api.toml）
├── docs/
│   ├── architecture.md           # 完整系统设计文档
│   ├── presentation/             # 答辩 PPT（3 页 HTML 幻灯片）
│   │   ├── index.html            # 浏览器键盘翻页入口
│   │   ├── 01-architecture.html
│   │   ├── 02-sequence.html
│   │   ├── 03-demo.html
│   │   └── assets/               # 静态截图 PNG（导出用）
│   └── demo-runs/                # 提交版的真实 run 产物
│       └── run-20260516-004106-chuangzhi/
└── vibe-design/                  # 实际系统代码
    ├── opencode.json             # provider 配置（当前主 LLM = SII gpt-5.5；MiniMax 备用）
    ├── .opencode/
    │   ├── agent/                # 4 个 agent markdown
    │   │   ├── planner.md
    │   │   ├── researcher.md
    │   │   ├── designer.md
    │   │   └── critic.md
    │   ├── command/design.md     # /design 自定义命令
    │   └── skills/               # 4 个领域 skill（designer 路由用）
    │       ├── logo.md
    │       ├── poster.md
    │       ├── copywriting.md
    │       └── ui-mockup.md
    ├── tools/                    # Python CLI（agent 通过 bash 调用）
    │   ├── gen_image.py          # 双后端文生图 + OpenAI-compatible 图生图/编辑
    │   └── html_screenshot.py    # HTML → PNG
    ├── examples/                 # 3 条不同领域 brief
    │   ├── brief-sii-academy.md
    │   ├── brief-zhujiajiao.md
    │   └── brief-coffee-startup.md
    └── outputs/                  # 每次 run 一个子目录（gitignore）
```

## 模型与图像后端

| 用途 | 当前模型 | 备注 |
|---|---|---|
| 所有 agent LLM | **SII `gpt-5.5`** | OpenAI 兼容，opencode `@ai-sdk/openai` provider；key 走 `.env` 的 `SII_API_KEY` |
| `small_model`（轻量调用） | SII `gpt-4.1-nano` | 同上 |
| 图像生成 · 默认 | **`gpt-image-2`**（findcg 中转站） | `api.toml [active].image = "openai"` |
| 图像生成 · 开发省钱 | MiniMax `image-01` | `gen_image --backend minimax` 或 `[active].image = "minimax"` |
| LLM 备用 | MiniMax `MiniMax-M2.7-highspeed` | opencode.json 已声明，把顶层 `model` 改回去即切换；需要 `MINIMAX_API_KEY` |

切换图像后端：改 `api.toml [active].image = "openai"`（默认）/ `"minimax"`，或 `gen_image --backend minimax` 单次覆盖。文生图对 LLM 屏蔽后端；图生图 / 编辑通过 `--input-image` 使用 OpenAI-compatible `images/edits`，若当前 active image 是 minimax，工具会自动路由到 openai。

## 关键设计决策

1. **串行调度**：原因是 MiniMax-M2 reasoning 在 subagent 并行下会挂起；切到 GPT-5.5 后挂起未再复现，但 planner prompt 仍保留"一次只调一个"以收敛 race 风险
2. **文件即上下文契约**：subagent 间不互相 @；只通过 `brief.md / brand-spec.md / v?.review.md` 传递信息
3. **Critic 同时审图与 prompt**：很多 slop 根因在 prompt（generic 词、缺禁忌项），看 prompt 才能给出"改 prompt / 改版式 / 换素材"分层建议
4. **Critic ImageMagick fallback**：MiniMax-M2 不支持视觉输入时的设计；GPT-5.5 已支持图像理解，critic 可以同时跑机器校验 + 直接看图，但当前 prompt 仍以 ImageMagick 为主——尚未为视觉模型重写 critic
5. **`--pure` 跳过外部插件**：用户全局插件注入的"parallelize"提示会干扰 subagent，加 `--pure` 启动隔离

## 已知局限

- **`gpt-image-2` 对深色 hex 复现优于 minimax `image-01`，但仍非像素级精确**（实测 ΔE 3-8 区间，散色由 JPEG 压缩 / 抗锯齿引入，非主动配色失误）
- **critic 当前 prompt 仍假定 LLM 看不到图**（ImageMagick + brand-spec 文字对照），GPT-5.5 的视觉理解能力**未被启用**——是优化空间不是 bug
- 早期 MiniMax-M2 时代的两个局限：**不支持图像输入** / **subagent 偶发 5+ 分钟长 thinking**（`--pure` 缓解）——切到 GPT-5.5 后均未再复现，保留备查

## 答辩演示

```bash
# 浏览器打开 3 页 PPT，← / → 翻页，F 全屏
xdg-open docs/presentation/index.html
```
