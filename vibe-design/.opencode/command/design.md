---
description: Vibe Design 入口。把整段 brief 交给 planner，启动多智能体协同设计。
agent: planner
---

# /design

设计 brief: $ARGUMENTS

请按 planner 的 5 步流程执行（调研 → 拆任务 → 逐任务 designer/critic 闭环 → 汇总 final.md → 给用户两段式回复）。

如果 $ARGUMENTS 为空，提示用户「请在 /design 后跟一句设计需求，例如：/design 请为创智学院做一套品牌形象设计」。
