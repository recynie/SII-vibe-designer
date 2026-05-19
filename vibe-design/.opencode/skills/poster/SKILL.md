---
name: poster
description: Design decisions and toolchain handbook for producing a portrait poster, key visual, or infographic as a self-contained HTML rendered to PNG via html_screenshot (default 1200×1600). Covers visual 4-layer structure (eye-catcher/headline/supporting/CTA), portrait composition flow, embedded-style HTML structure, gen_image for inline assets, brand-spec font reuse, and anti-slop red lines. Use when the deliverable spec calls for a poster, key visual, KV, or infographic in HTML→PNG form (not a logo PNG, not an interactive UI page).
---

# Skill · Poster（介质工艺手册）

Poster 介质：HTML 竖版（默认 1200×1600）+ html_screenshot 渲 PNG。

## 设计决策

### 视觉四层

写 HTML 前先定四层各放什么，再动手写 div：

1. **Eye-catcher** — 主视觉图或粗体视觉元素（占画面最大面积）
2. **Headline** — 大字主信息
3. **Supporting info** — 日期、地点、次要信息
4. **CTA** — 行动号召、网址、二维码区

### 竖版构图

视觉流从上到下：eye-catcher 占上 1/3 ~ 1/2，headline 紧随，CTA 沉底。描述构图时用具体方位（"标题填满上三分之一"），不用抽象词。

## 工艺要点
- HTML 自包含，所有样式内嵌
- 先写 HTML 再调 html_screenshot；输出 PNG 与 HTML 同 stem
- 配图用 gen_image 出，存 `assets/<n>.png`，HTML 用相对路径引用
- 字体配对沿用 brand-spec.md `## 字体`，不自行引入新字族（check_html_fonts 会拦）

## 渲图调用
```bash
uv run python tools/html_screenshot.py \
  --html <html> --output <png> --width 1200 --height 1600
```

## 反 slop 红线
- 多色块拼贴 ≠ 设计
- slogan 重复 3 遍当装饰
- 居中 + 居中副标 = PPT
- `linear-gradient(135deg, purple, pink)` 当背景
