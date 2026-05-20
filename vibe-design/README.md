# vibe-design

基于 opencode harness 扩展的多智能体平面设计系统。

## 用途

接收一句自然语言 brief（如「请为某品牌做一套品牌形象设计」），自动产出 logo / 主视觉 / 文创物料 / 简单 UI 等视觉设计交付物。

## 快速开始

1. 仓库根目录的 `api.toml` 已配置 Python 脚本要用的 provider 与 `[active]` 选择器（参考 `../api.toml.example`）。
2. `vibe-design/.env` 已配置 opencode 要用的环境变量；手动启动 opencode 前需要显式加载。
3. 进入项目目录并加载环境变量：
   ```bash
   cd vibe-design
   set -a; . ./.env; set +a
   ```
4. 启动 opencode（`--pure` 跳过全局插件，避免 workflow rules 注入干扰 subagent）：
   ```bash
   opencode --pure
   ```
5. 在 TUI 中输入：
   ```
   /design 请为创智学院做一套品牌形象设计
   ```

   或非交互一次性跑完：
   ```bash
   opencode run --pure --agent planner '请为创智学院做一套品牌形象设计'
   ```

输出落 `outputs/<run-id>/`。

## 模型

- **LLM（当前）**：所有 agent 用 SII 中转站的 **`gpt-5.5`**（顶层 `model`）+ `gpt-4.1-nano`（`small_model`），OpenAI 兼容，配置在 `opencode.json`。
- **图像（默认）**：`gpt-image-2`（findcg 中转站），由 `api.toml [active].image = "openai"` 选中。
- **图像（开发省钱后端）**：MiniMax `image-01`，`api.toml [active].image = "minimax"` 或 `gen_image --backend minimax` 切换。
- **LLM 备用**：opencode.json 同时声明了 `minimax-cn-coding-plan/MiniMax-M2.7-highspeed`，把顶层 `model` 改回该值并提供 `MINIMAX_API_KEY` 即切换。

> 早期版本（2026-05 之前的 demo run）跑的是 MiniMax-M2，CHANGELOG 记录了当时的局限（reasoning 长 thinking、不支持视觉、1027 内容审查等）。当前 GPT-5.5 多数局限已消失，下文 README 的「实测发现」段以备查为主。

切换图像后端（任一即可）：

```bash
# 改 api.toml 里的 [active].image = "minimax" / "openai"，或 gen_image CLI 临时覆盖：
uv run python tools/gen_image.py --backend minimax ...
```

## 架构

```
user → /design <brief>
        │
        ▼
   Planner (primary)  ── 拆任务、调度、汇总
        │
   ┌────┼────┐
   ▼    ▼    ▼
 researcher designer critic   subagents（独立上下文）
```

详见 `../docs/architecture.md`。

## 工具脚本

`tools/` 下的 Python CLI 由 agent 通过 bash 调用：

- `api_config.py` — Python 脚本共用的 API 凭据加载器（只读 `api.toml`）
- `gen_image.py` — 文生图，路由 MiniMax / gpt-image-2，凭据走 `api_config`
- `html_screenshot.py` — HTML 渲成 PNG，用于 critic 评审版式

## 例子

`examples/` 三条不同领域的 brief，用于验证系统通用性：

- `brief-sii-academy.md` — 题目要求的"创智学院品牌形象设计"
- `brief-zhujiajiao.md` — 参考案例的"朱家角文旅"
- `brief-coffee-startup.md` — 第三个不同领域的 brief
