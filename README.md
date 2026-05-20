# Vibe Design · 多智能体协同设计系统

Vibe Design 是一个基于 opencode harness 的命令行设计系统。用户输入一句自然语言 brief，系统把它转成可追溯事实、品牌约束和交付物清单，再由多个独立上下文 agent 协同完成视觉产物生成、机器校验、主观评审和迭代汇总。

当前系统聚焦课程实训场景中的 AI For Design：品牌形象、主视觉、宣传海报、文创物料、官网或 H5 mockup 等平面与界面设计交付物。正式题目 brief 为：

> 请为创智学院做一套品牌形象设计。

正式 demo 产物位于 [`docs/demo-runs/run-final-hardened/`](./docs/demo-runs/run-final-hardened/)。

## 设计原则

### 1. Harness 不重写，只扩展设计能力

opencode 已经提供 agent 定义、subagent 独立上下文、自定义命令、工具调用、文件读写、权限控制和 provider 接入。本项目不重新实现 agent harness，而是在它之上补齐四类设计能力：

| 层级 | 本项目实现 |
|---|---|
| 工作流入口 | `vibe-design/.opencode/command/design.md` |
| 设计角色 | `planner / researcher / designer / critic` 四个 agent prompt |
| 设计工具 | `gen_image.py`、`html_screenshot.py`、`validate.py` 等 Python CLI |
| 领域知识 | `craft`、`design-guidelines`、`ask-user` 三个 opencode skill |

### 2. 文件即上下文契约

agent 之间不依赖隐式聊天记忆传递关键决策。Researcher 先落三份上游文件，后续 agent 只读这些文件推进：

| 文件 | 作用 |
|---|---|
| `facts.md` | 可追溯事实、来源、下载到本地的资产记录 |
| `brand-spec.md` | 色彩参考、字族、调性、视觉气质、反 slop 禁区 |
| `deliverables.md` | 显式/隐式/拒绝交付物清单，planner 的唯一调度依据 |

每个 artifact 目录继续保留 `v?.prompt.txt` 和 `v?.review.md`，使设计生成、评审依据和迭代原因可复盘。

### 3. 先确定交付物，再并行执行

系统不再固定输出 “logo + 海报 + UI”。Researcher 按 brief 选择 1-5 个交付物，并支持多子产物条目，例如一个「品牌文创设计」下包含 logo、T 恤、帆布袋和马克杯效果图。Planner 只按 `deliverables.md` 调度，不额外增删交付物。

独立交付物可以并行启动 designer 和 critic；存在产物依赖时按依赖顺序执行。默认建议每批最多 2 个 designer，避免图像 API 并发限制。

### 4. 机器硬门槛和问题评审分层

`validate.py` 只做可靠的机器硬门槛，目前主要是 HTML 字族是否符合 `brand-spec.md`。视觉质量由 critic 直接读取实物图片或 HTML 截图后检查，以整体色调和品牌气质判断颜色方向，并输出可执行问题清单。

Critic 不再给主观分或最终通过结论，而是列出 `BLOCKER / MAJOR / MINOR / NIT` 严重度的问题、证据和修改方向。Planner 读取 review 后决定是否让 designer 重做：`BLOCKER` 必须修复或 escalate，`MAJOR` 默认重做，只有 `MINOR / NIT` 通常接受并记录。

### 5. 图像后端对 agent 透明

Designer 只调用统一 CLI：

```bash
uv run python tools/gen_image.py \
  --prompt "<English prompt>" \
  --output outputs/<run-id>/artifacts/<slug>/v1.png \
  --aspect-ratio 1:1
```

`gen_image.py` 根据 `api.toml [active].image` 或 `--backend` 路由到 MiniMax `image-01` 或 OpenAI-compatible `gpt-image-2`。同一份 agent prompt 可以在开发省钱后端和正式生图后端之间切换。

## 系统架构

```text
user: /design <brief>
          │
          ▼
┌────────────────────┐
│ Planner (primary)  │  初始化 run、澄清需求、调度、迭代、汇总
└──┬────────┬────────┘
   │        │
   │        └─ designer / critic 可按交付物依赖并行
   │
   ▼
Researcher (subagent)
  ├─ facts.md
  ├─ brand-spec.md
  ├─ deliverables.md
  └─ assets/
          │
          ▼
Designer (subagent)
  ├─ gen_image.py          -> PNG 候选 + prompt 旁证
  └─ html_screenshot.py    -> HTML mockup/poster 渲染 PNG
          │
          ▼
Critic (subagent)
  ├─ validate.py           -> 字族等机器硬门槛
  └─ Read artifact         -> 直接看图/源码，写 v?.review.md
          │
          ▼
Planner
  ├─ 按 critic 问题严重度判断是否 v1 -> v2 -> v3
  ├─ BLOCKER/MAJOR 不可修或超轮次：escalate.md
  └─ final.md
```

完整架构说明见 [`docs/architecture.md`](./docs/architecture.md)。

## Agent 职责

| Agent | opencode mode | 权限重点 | 职责 |
|---|---|---|---|
| `planner` | primary | 无 webfetch；仅可用 `ask-user` skill | 建 run 目录，澄清需求，调用 researcher，按 deliverables 写 plan，调度 designer/critic，处理迭代和汇总 |
| `researcher` | subagent | 可 webfetch；可用 `design-guidelines` | 调研公开事实和 brief 信号，下载必要资产，写 `facts.md / brand-spec.md / deliverables.md` |
| `designer` | subagent | 不 webfetch；可用 `craft`、`design-guidelines` | 按交付物形态调用生图或写 HTML，生成可评审 artifact，自检并选择最佳候选 |
| `critic` | subagent | 不 webfetch；可用 `craft` | 先跑机器校验，再读实物，列出结构化问题、严重度、证据和修改方向，不打分、不决定是否通过 |

## 数据与输出结构

一次 run 输出到 `vibe-design/outputs/<run-id>/`。典型结构：

```text
outputs/run-YYYYMMDD-HHMM-<task>/
├── facts.md
├── brand-spec.md
├── deliverables.md
├── plan.md
├── final.md
├── escalate.md              # 只有需要用户决断或无法修复时出现
├── assets/                  # researcher 下载的官方或参考素材
├── scratch/                 # designer 中间文件
└── artifacts/
    ├── <slug>/
    │   ├── v1-1.png
    │   ├── v1-1.png.prompt.txt
    │   ├── v1.png
    │   └── v1.review.md
    └── <parent-slug>/       # 多子产物交付物
        ├── <sub-slug>/v1.png
        └── v1.review.md
```

Schema 文档在 `vibe-design/docs/schema/`：

| Schema | 约束 |
|---|---|
| `facts.schema.md` | 每条事实必须带 `[source: ...]` 或 `[asset: ...]` |
| `brand-spec.schema.md` | 色彩参考/字体字段必须带 `[from-fact: ...]` 或 `[inferred: ...]` |
| `deliverables.schema.md` | 四段式结构，显式+隐式主条目 ≤ 5，隐式 ≤ 2，支持 2-6 个 sub-items |

## 具体实现

### opencode 配置

`vibe-design/opencode.json` 注册了多个 provider。当前默认：

| 用途 | 当前配置 |
|---|---|
| 主 LLM | `findcg-openai/gpt-5.5` |
| small_model | `findcg-openai/gpt-5.5` |
| 备用 LLM | `sii-openai/*`、`minimax-cn-coding-plan/MiniMax-M2.7-highspeed`、`findcg-claude/*` |
| 权限 | edit/bash/webfetch/skill 按 agent frontmatter 再收窄；外部目录 deny |

opencode 的 key 来自 `.env` / `vibe-design/.env` 中的环境变量，例如 `FINDCG_OPENAI_API_KEY`、`SII_API_KEY`、`MINIMAX_API_KEY`。

### Python 工具

| 文件 | 用途 |
|---|---|
| `vibe-design/tools/api_config.py` | Python 脚本统一读取仓库根目录 `api.toml` |
| `vibe-design/tools/gen_image.py` | MiniMax / OpenAI-compatible 双后端生图，支持候选并发、格式检测、prompt 旁证 |
| `vibe-design/tools/html_screenshot.py` | 用系统 Chromium 或 Playwright 把本地 HTML 渲染成 PNG |
| `vibe-design/tools/check_html_fonts.py` | 检查 HTML `font-family` 是否在 `brand-spec.md` 字体段内 |
| `vibe-design/tools/validate.py` | critic 调用的 per-artifact 机器校验聚合入口 |
| `vibe-design/tools/verify_facts.py` | 校验 README / CHANGELOG 中数量类事实是否和仓库状态一致 |

### Skills

| Skill | 作用 |
|---|---|
| `ask-user` | Planner 在初始化阶段澄清用户需求，只问需求不问可搜索事实 |
| `craft` | Designer/Critic 共用的设计工艺基线：字排、色彩比例、层级、构图、反 AI slop |
| `design-guidelines` | Researcher/Designer 共用的风格方向和交付物类型指南 |

`craft/fonts/` 内置多组 OFL 字体，HTML artifact 应引用本地字体，不依赖 Google Fonts CDN。

## 快速开始

### 1. 安装依赖

```bash
uv sync
uv run playwright install chromium
```

Python 版本由 `.python-version` 锁定为 3.12；依赖声明在 `pyproject.toml`，当前包含 `playwright` 和 `pillow`。

### 2. 配置凭据

```bash
cp api.toml.example api.toml
cp .env.example .env
cp .env.example vibe-design/.env
```

`api.toml` 是 Python 脚本的唯一凭据源，包含：

```toml
[active]
llm = "sii"
image = "openai"
```

`.env` / `vibe-design/.env` 供 opencode provider 的 `{env:...}` 占位符读取。非交互 e2e runner 默认显式加载 `vibe-design/.env`。

### 3. 交互式运行

```bash
cd vibe-design
set -a; . ./.env; set +a
opencode --pure
```

在 TUI 中输入：

```text
/design 请为创智学院做一套品牌形象设计
```

`--pure` 用于跳过用户全局 opencode 插件，避免外部 workflow rules 干扰本项目的 agent 调度。

### 4. 非交互端到端运行

推荐使用仓库级 runner，它会加载 `vibe-design/.env`、流式输出 opencode 日志、每 30 秒扫描 `outputs/` 打印进度，并以是否产出 `final.md` 作为通过条件：

```bash
uv run e2e-test --brief "请为创智学院做一套品牌形象设计"
```

也可以从示例 brief 文件运行：

```bash
uv run e2e-test --brief-file vibe-design/examples/brief-sii-academy.md
```

## 验证与测试

```bash
# 配置级：检查每个 agent 的 skill 权限矩阵，不调用 LLM
python3 scripts/test_opencode_skill_permissions.py

# 工具单测：gen_image 候选路径逻辑
uv run python vibe-design/tools/tests/test_gen_image.py

# 事实漂移检查：README / CHANGELOG 数量陈述 vs 仓库状态
uv run python vibe-design/tools/verify_facts.py

# 图像端点烟测
uv run python vibe-design/tools/gen_image.py \
  --prompt "minimal flat vector logo, geometric, navy and cyan, no text" \
  --output /tmp/vibe-test.png \
  --backend openai \
  --candidates 1
```

仓库还保留了 API 能力测试脚本：`scripts/test_api.py`、`scripts/test_llm_capabilities.py`、`scripts/test_sii_vision.py`、`scripts/test_sii_imagegen.py`、`scripts/test_sii_image_gen.py`。这些会真实调用外部 API。

注意：`vibe-design/tools/tests/test_tools.sh` 和 `test_agent_prompts.sh` 中仍包含早期工具/skill 名称断言，当前实现已有漂移，运行前需要先更新测试脚本。

## Demo Runs

当前工作树的 `docs/demo-runs/` 中保存了 3 个历史 run 或实证目录：

| Run | 说明 |
|---|---|
| `run-final-hardened/` | 正式交付 run，创智学院品牌形象设计 |
| `run-gpt-image-2-evidence/` | 单图实证，用于观察 gpt-image-2 色值表现 |
| `run-zhujiajiao-recovered/` | 朱家角文旅品牌测试，恢复后的部分产物 |

答辩 HTML 幻灯片在 `docs/presentation/`，入口为 `docs/presentation/index.html`。

## 项目结构

```text
SII-assignment/
├── README.md
├── AGENTS.md
├── CHANGELOG.md
├── pyproject.toml
├── api.toml.example
├── .env.example
├── scripts/
│   ├── run_e2e.py
│   ├── test_opencode_skill_permissions.py
│   └── test_*.py
├── docs/
│   ├── architecture.md
│   ├── task/
│   ├── APIs/
│   ├── presentation/
│   └── demo-runs/
├── references/
│   └── ... external design / opencode / skill references
└── vibe-design/
    ├── opencode.json
    ├── README.md
    ├── examples/
    ├── docs/schema/
    ├── tools/
    ├── outputs/               # gitignored runtime output
    └── .opencode/
        ├── agent/
        ├── command/
        └── skills/
```

## 已知限制

- 图像模型更适合控制整体色调、明度、饱和度和品牌气质；critic 以大体色调一致性判断视觉结果。
- `gen_image.py --input-image` 在 designer prompt 中已有约定，但当前脚本实现主要覆盖文生图候选生成；图生图/编辑能力仍需补齐或校准。
- 旧测试脚本和部分历史文档仍带有早期固定交付物、旧 skill、旧评分尺度的痕迹，需要逐步清理。
- 外部 API 会出现 429、内容审查或长时间无响应；e2e runner 提供 idle timeout 和进度心跳，但不会替代业务级重试策略。
