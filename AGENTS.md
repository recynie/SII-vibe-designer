# AGENTS.md

This file serves as a workspace map and high-level overview for any agent operating in this repository. Use it to locate files, understand project structure, and orient yourself before diving into details.

## Overview

当前代码库是一个多智能体协同设计系统（Vibe Design），基于 opencode harness 构建。用户输入一句话 brief，系统通过 planner / researcher / designer / critic 四个 agent 协同输出 logo、主视觉海报、品牌文案、UI mockup 等品牌设计产物。这是一个课程实训作业项目。

## Workspace Map

### 根目录

| 路径 | 说明 |
|---|---|
| `README.md` | 项目整体说明，包含架构概览、快速开始、demo run 汇总、已知局限等 |
| `CHANGELOG.md` | 完整迭代历史记录 |
| `pyproject.toml` | Python 项目配置（依赖：pillow、playwright） |
| `uv.lock` | uv 锁文件 |
| `.env` | 仅本地，**唯一**的 API key 存放处；其它代码与文档不应出现真实 key |
| `scripts/test_api.py` | API 端点可用性测试脚本（强制从 `.env` 读 `OPENAI_API_KEY`） |

### `vibe-design/` — 系统核心代码

| 路径 | 说明 |
|---|---|
| `vibe-design/opencode.json` | opencode provider 配置（MiniMax-M2 等） |
| `vibe-design/.opencode/agent/` | 四个 agent 的 prompt 定义（planner / researcher / designer / critic） |
| `vibe-design/.opencode/command/design.md` | `/design` 自定义命令定义 |
| `vibe-design/.opencode/skills/` | designer 使用的领域 skill（logo / poster / copywriting / ui-mockup / asset-prep） |
| `vibe-design/tools/gen_image.py` | 双后端文生图工具（minimax image-01 / gpt-image-2） |
| `vibe-design/tools/html_screenshot.py` | HTML → PNG 截图工具（Playwright + Chromium） |
| `vibe-design/examples/` | 示例 brief（创智学院 / 朱家角古镇 / 咖啡品牌） |
| `vibe-design/outputs/` | 运行产物输出目录（gitignore） |
| `vibe-design/MILESTONES.md` | 开发里程碑记录 |
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
| `references/opencode/` | opencode 框架参考文档 |
| `references/huashu-design/` | 华数设计相关参考 |
| `references/open-codesign/` | open-codesign 项目参考 |
| `references/open-design/` | open-design 项目参考 |
| `references/flow-guarantees/` | 流程保障相关参考 |
| `references/ppt-master/` | PPT 制作参考 |

### `scripts/` — 仓库级辅助脚本

| 路径 | 说明 |
|---|---|
| `scripts/test_api.py` | API 端点可用性测试脚本（从 `.env` 读 `OPENAI_API_KEY`） |

## Maintenance

当下述任意一种情况发生时，应当更新 `AGENTS.md`：

- 创建新的文件或目录
- 修改文件内容导致其描述过时
- 移动或复制文件/目录
- 文件/目录的主要用途发生变更
