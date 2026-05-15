# Vibe Design · 多智能体协同设计系统

> 基于 [opencode](https://opencode.ai/) harness 扩展的命令行设计 agent。一句话 brief 输入，多 agent 协同输出 logo / 主视觉 / 品牌文案 / UI mockup。

## 课题对照

| 题目要求 | 落点 |
|---|---|
| 至少三个智能体（规划 / 执行 / 评估）+ 独立上下文 | `vibe-design/.opencode/agent/` 下 4 个 agent：planner（primary）+ researcher / designer / critic（subagent） |
| 必要的设计工具（文生图等） | `vibe-design/tools/gen_image.py` 双后端文生图 + `html_screenshot.py` |
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
# 1. 安装依赖
uv sync
uv add playwright && uv run playwright install chromium

# 2. 配置 .env（已配好 MiniMax + gpt-image-2 凭证）

# 3. 进入项目目录
cd vibe-design

# 4. 启动 opencode（--pure 跳过外部插件干扰）
opencode --pure

# 5. 在 TUI 输入：
/design 请为创智学院做一套品牌形象设计

# 或非交互一次性跑完：
opencode run --pure --agent planner '请为创智学院做一套品牌形象设计'
```

输出落 `vibe-design/outputs/<run-id>/`。

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

## 项目结构

```
SII-assignment/
├── .env                          # MiniMax + gpt-image-2 凭证（gitignore）
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
    ├── opencode.json             # MiniMax provider 配置
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
    │   ├── gen_image.py          # 双后端文生图
    │   └── html_screenshot.py    # HTML → PNG
    ├── examples/                 # 3 条不同领域 brief
    │   ├── brief-sii-academy.md
    │   ├── brief-zhujiajiao.md
    │   └── brief-coffee-startup.md
    └── outputs/                  # 每次 run 一个子目录（gitignore）
```

## 模型与图像后端

| 用途 | 模型 | 备注 |
|---|---|---|
| 所有 agent LLM | **MiniMax-M2** | OpenAI 兼容 `v1/chat/completions`，opencode `@ai-sdk/openai-compatible` provider |
| 图像生成 · 开发 | MiniMax `image-01` | 便宜，迭代 prompt 用 |
| 图像生成 · 交付 | **gpt-image-2** | 高质量，最终 run 用 |

切换：`export DESIGN_IMAGE_BACKEND=openai`（默认）/ `=minimax`。**LLM 完全感知不到**，同一份 agent prompt 跑两个后端。

## 关键设计决策

1. **串行调度**：MiniMax-M2 reasoning 在 subagent 并行下会挂起，强制 planner 一次只调一个
2. **文件即上下文契约**：subagent 间不互相 @；只通过 `brief.md / brand-spec.md / v?.review.md` 传递信息
3. **Critic 同时审图与 prompt**：很多 slop 根因在 prompt（generic 词、缺禁忌项），看 prompt 才能给出"改 prompt / 改版式 / 换素材"分层建议
4. **Critic ImageMagick fallback**：MiniMax-M2 不支持视觉输入，critic 用 `identify -format %[hex:u]` 提取颜色与 brand-spec 比对
5. **`--pure` 跳过外部插件**：用户全局插件注入的"parallelize"提示会干扰 subagent，加 `--pure` 启动隔离

## 已知局限

- **MiniMax image-01 对深色 hex 复现不严格**（如 #1A2B4A 墨蓝会被生成为浅蓝/浅青）。生产场景下应切到 gpt-image-2 后端
- **MiniMax-M2 不支持图像输入**，critic 只能用 ImageMagick 间接验证颜色，无法做整体视觉评分
- **subagent 偶发长 thinking**（5+ 分钟无产出），通过 `--pure` 缓解

## 答辩演示

```bash
# 浏览器打开 3 页 PPT，← / → 翻页，F 全屏
xdg-open docs/presentation/index.html
```
