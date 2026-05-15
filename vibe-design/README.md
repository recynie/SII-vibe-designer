# vibe-design

基于 opencode harness 扩展的多智能体平面设计系统。

## 用途

接收一句自然语言 brief（如「请为某品牌做一套品牌形象设计」），自动产出 logo / 主视觉 / 文案 / 简单 UI 等设计交付物。

## 快速开始

1. 仓库根目录的 `.env` 已配置 MiniMax + gpt-image-2 凭证。
2. 进入项目目录：
   ```bash
   cd vibe-design
   ```
3. 启动 opencode（`--pure` 跳过全局插件，避免 workflow rules 注入干扰 subagent）：
   ```bash
   opencode --pure
   ```
4. 在 TUI 中输入：
   ```
   /design 请为创智学院做一套品牌形象设计
   ```

   或非交互一次性跑完：
   ```bash
   opencode run --pure --agent planner '请为创智学院做一套品牌形象设计'
   ```

输出落 `outputs/<run-id>/`。

## 模型

- **LLM**：所有 agent 用 MiniMax-M2（OpenAI 兼容，配置在 `opencode.json`）。
- **图像（开发）**：MiniMax `image-01`，便宜快速，用于 prompt 迭代。
- **图像（正式）**：`gpt-image-2`，质量高，用于最终交付。

切换图像后端：

```bash
export DESIGN_IMAGE_BACKEND=minimax  # 开发
export DESIGN_IMAGE_BACKEND=openai   # 正式（默认）
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

- `gen_image.py` — 文生图，路由 MiniMax / gpt-image-2
- `html_screenshot.py` — HTML 渲成 PNG，用于 critic 评审版式

## 例子

`examples/` 三条不同领域的 brief，用于验证系统通用性：

- `brief-sii-academy.md` — 题目要求的"创智学院品牌形象设计"
- `brief-zhujiajiao.md` — 参考案例的"朱家角文旅"
- `brief-coffee-startup.md` — 第三个不同领域的 brief
