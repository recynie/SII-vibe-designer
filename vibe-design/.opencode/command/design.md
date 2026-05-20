---
description: Vibe Design 入口。把整段 brief 交给 planner，启动多智能体协同设计。
agent: planner
---

# /design

设计 brief: $ARGUMENTS

加载`ask-user` skill ，向用户对齐任务设计要求。将讨论结果进行要点总结

如果 $ARGUMENTS 为空，提示用户「请在 /design 后跟一句设计需求，例如：/design 请为创智学院做一套品牌形象设计」。
