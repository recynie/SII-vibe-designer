---
name: ui-mockup
description: Toolchain handbook for producing a single-page UI mockup as self-contained HTML rendered to PNG — desktop landing page (1440×2400) or mobile H5 (375×812). Covers fixed-width body layout, brand-spec font reuse, gen_image for inline imagery, and screenshot invocation. Use when the deliverable spec calls for a UI mockup, landing page, H5 page, or product page in HTML→PNG form (not a poster, not a static logo).
---

# Skill · UI Mockup（介质工艺手册）

UI 介质：HTML 单页（落地页 1440×2400 / H5 375×812）+ 截图 PNG。

## 工艺要点
- 自包含 HTML，样式内嵌；body 固定宽
- 字族沿用 brand-spec `## 字体`（check_html_fonts 会拦外来字族）
- 配图先 gen_image 出到 `assets/`，HTML 相对路径引用（配图通常传 `--candidates 1`，无需多候选）
- 截图：`uv run python tools/html_screenshot.py --html ... --output ... --width ... --height ...`

## 反 slop 红线
- 圆角卡片 + 左侧 4px 彩色 accent border（最大公约数 SaaS）
- 每卡片配 emoji icon
- 渐变背景 + 白色卡片漂浮
- placeholder.com 灰图
- "赋能 / 一站式 / 全链路"出现在 hero 副标

## 正向
- 大字 + 留白 + 小段说明的层级
- 真实配图（gen_image）或诚实灰底 + "待替换"标注
