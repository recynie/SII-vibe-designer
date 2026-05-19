# 宣传海报 (Poster)

产物形态：HTML 排版 + html_screenshot 渲 PNG。

## 选择指引（researcher 参考）

适合产出海报的场景：活动宣传、招生招聘、产品发布、展览通知、信息图。

Researcher 在 deliverables 规格中须指定：尺寸（宽×高）、用途。

常见尺寸参考：

| 用途 | 宽×高 | 方向 |
|---|---|---|
| 竖版活动海报（默认） | 1200×1600 | portrait |
| A4 宣传单页 | 1240×1754 | portrait |
| 横版 banner | 1920×1080 | landscape |
| 社交媒体方图 | 1080×1080 | square |
| 移动端长图 | 750×1334 | portrait |

deliverables 未指定时默认 1200×1600。

## 执行要点（designer 参考）

### 视觉四层

写 HTML 前先定四层各放什么：

1. **Eye-catcher** — 主视觉图或粗体视觉元素（占画面最大面积）
2. **Headline** — 大字主信息
3. **Supporting info** — 日期、地点、次要信息
4. **CTA** — 行动号召、网址、二维码区

### 构图

- 竖版：视觉流从上到下，eye-catcher 占上 1/3 ~ 1/2，headline 紧随，CTA 沉底
- 横版：左图右文，或上图下文；视觉锚点在左上 1/3
- 方图：中心辐射或对角线构图

### 工艺要点

- HTML 自包含，所有样式内嵌
- 先写 HTML 再调 html_screenshot
- 配图用 gen_image 出到 scratch/，HTML 用相对路径引用（配图传 `--candidates 1`）
- 字族沿用 brand-spec `## 字体`

### 渲图调用

```bash
uv run python tools/html_screenshot.py \
  --html <html> --output <png> --width <W> --height <H>
```

### 反 slop

- 多色块拼贴 ≠ 设计
- slogan 重复 3 遍当装饰
- 居中 + 居中副标 = PPT
- `linear-gradient(135deg, purple, pink)` 当背景

更多海报变体参考见 `references/open-design/design-templates/magazine-poster/SKILL.md`。
