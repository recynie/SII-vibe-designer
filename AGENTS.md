# AGENTS.md

This file serves as a workspace map and high-level overview for any agent operating in this repository. Use it to locate files, understand project structure, and orient yourself before diving into details.

## Git

### Tags
Add tag for *major versions* of this system.
Major version means that the system can:
- pass end-to-end pipeline. Minor problems are allowed, but the system must be available.

## File Writing for agnet prompt and skills
语言清晰、明确，减少意义不明的简写，用技术性的语言撰写agent prompt和skills。
不要引入不必要的说明。
修改agent prompt前，思考：agent需要了解这部分内容吗？

## E2E run

如果用户要求运行e2e或端到端测试，使用下面的任务：

> 请为创智学院做一套品牌形象设计。

## Overview

当前代码库是一个多智能体协同设计系统（Vibe Design），基于 opencode harness 构建。用户输入一句话 brief，系统通过 planner / researcher / designer / critic 四个 agent 协同输出 logo、主视觉海报、品牌文案、UI mockup 等品牌设计产物。支持多子产物交付物（一个 design 下包含多个子产物，如品牌文创设计包含 logo + T恤 + 帆布袋效果图）。这是一个课程实训作业项目。

## Workspace Map

### 根目录

| 路径 | 说明 |
|---|---|
| `README.md` | 项目整体说明，包含架构概览、快速开始、demo run 汇总、已知局限等 |
| `CHANGELOG.md` | 完整迭代历史记录 |
| `pyproject.toml` | Python 项目配置（依赖：playwright） |
| `uv.lock` | uv 锁文件 |
| `.venv/` | uv 虚拟环境（Python 3.12.3），通过 `uv sync` 创建，已 gitignore |
| `.env` | 仅本地，opencode 用 — `opencode.json` 里 `{env:MINIMAX_API_KEY}` 走这里。Python 脚本不再读它 |
| `api.toml` | 仅本地（gitignore），**Python 脚本的唯一**凭据源；`[active] llm/image` 选当前 provider |
| `api.toml.example` | `api.toml` 的 schema 模板 |
| `scripts/test_api.py` | 夏令营 API 中转站可用性测试（`api.toml [active].llm`） |

### `vibe-design/` — 系统核心代码

| 路径 | 说明 |
|---|---|
| `vibe-design/opencode.json` | opencode provider 配置（当前主 LLM = SII `gpt-5.5`；MiniMax provider 备用） |
| `vibe-design/.opencode/agent/` | 四个 agent 的 prompt 定义（planner / researcher / designer / critic） |
| `vibe-design/.opencode/command/design.md` | `/design` 自定义命令定义 |
| `vibe-design/.opencode/skills/` | designer 使用的领域 skill（craft / design-guidelines） |
| `vibe-design/tools/api_config.py` | Python 脚本共用的 API 凭据加载器（只读 `api.toml`） |
| `vibe-design/tools/gen_image.py` | 双后端文生图 + OpenAI-compatible 图生图/编辑工具，后端由 `api.toml [active].image` 决定；`--input-image` 进入编辑模式 |
| `vibe-design/tools/html_screenshot.py` | HTML → PNG 截图工具（Playwright + Chromium） |
| `vibe-design/examples/` | 示例 brief（创智学院 / 朱家角古镇） |
| `vibe-design/outputs/` | 运行产物输出目录（gitignore） |
| `vibe-design/docs/schema/` | 数据 schema 定义 |

### `docs/` — 文档与交付物

| 路径 | 说明 |
|---|---|
| `docs/architecture.md` | 完整系统架构设计文档 |
| `docs/task/` | 课题原始要求（PDF + Markdown） |
| `docs/APIs/` | 夏令营商用 API 手册及可用性测试报告 |
| `docs/presentation/` | 答辩 PPT（3 页 HTML 幻灯片 + 静态截图）（AI生成，未经验证） |
| `docs/demo-runs/` | 所有 demo run 的完整产物（7 个 run，含正式交付 `run-final-hardened/`） |

### `references/` — 参考资料

| 路径 | 说明 |
|---|---|
| `references/README.md` | 设计资源索引（Skills/Design Systems/Prompt 模板）|
| `references/open-design/` | nexu-io/open-design — 109 Skills / 151 Design Systems / 111 Templates |
| `references/open-codesign/` | OpenCoworkAI/open-codesign — 多模型设计工具 |
| `references/Deep-Research-skills/` | Weizhena/Deep-Research-skills — Claude Code/OpenCode/Codex 深度调研 workflow、web-search agent 与结构化 research skills 参考 |
| `references/awesome-claude-design/` | 按美学风格分类的 DESIGN.md 品牌系统 |
| `references/awesome-design-md/` | VoltAgent 品牌设计系统（71个） |
| `references/awesome-design-skills/` | Design Skills 精选（68个） |
| `references/awesome-claude-skills/` | Claude Skills 精选列表（11K+ Stars） |
| `references/anthropics-skills/` | Anthropic 官方 Skills（含 canvas-design/brand-guidelines） |
| `references/skywork-skills/` | Skywork AI 设计场景（logo/poster/branding/infographic） |
| `references/logo-designer-skill/` | SVG Logo 设计插件（迭代式设计） |
| `references/logo-generator-skill/` | Logo 生成器（中英双语） |
| `references/claude-skills/` | 通用 Claude Skills（含 svg-logo-designer） |
| `references/opencode/` | opencode 框架参考文档 |
| `references/huashu-design/` | 华数设计相关参考 |
| `references/flow-guarantees/` | 流程保障相关参考 |
| `references/ppt-master/` | PPT 制作参考 |

### `scripts/` — 仓库级辅助脚本

| 路径 | 说明 |
|---|---|
| `scripts/run_e2e.py` | 端到端测试 runner；调 `opencode run --command design`，加载 `vibe-design/.env`，流式输出并扫描 `outputs/` 打印进度心跳 |
| `scripts/test_api.py` | 夏令营 API 中转站可用性测试（`api.toml [active].llm`） |
| `scripts/test_opencode_skill_permissions.py` | opencode 各 agent 的 skill 权限矩阵配置测试（不调用 LLM API） |
| `scripts/test_llm_capabilities.py` | LLM 速度/推理/视觉能力测试（`api.toml [active].llm`） |
| `scripts/test_sii_vision.py` | 多模型视觉理解对比（`api.toml [active].llm`） |
| `scripts/test_sii_imagegen.py` / `test_sii_image_gen.py` | 生图延迟测试（`api.toml [providers.sii]` / `[providers.openai]`） |

## Development Environment

| 项目 | 当前值 |
|---|---|
| Python | 3.12.3（系统 `/usr/bin/python3.12`，项目 `.python-version` 锁定）|
| uv | 0.8.2 |
| 虚拟环境 | `.venv/`（基于 `.venv/bin/python3.12`，通过 `uv sync` 管理）|
| 依赖声明 | `pyproject.toml`（`[project]` 段），lock 文件 `uv.lock` |
| 常见操作 | `uv sync` — 同步环境；`uv add <pkg>` — 添加依赖；`uv run <cmd>` — 在 venv 中执行命令 |

## Maintenance

当下述任意一种情况发生时，应当更新 `AGENTS.md`：

- 创建新的文件或目录
- 修改文件内容导致其描述过时
- 移动或复制文件/目录
- 文件/目录的主要用途发生变更
