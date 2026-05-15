# Skill · 海报 / 主视觉

Designer 加载本 skill 时，目标是一张主视觉海报（HTML，竖版 A2 比例）+ 渲染截图。

## 输出规格

- HTML：`outputs/<RUN_ID>/artifacts/poster/v1.html`（自包含，一切内嵌）
- 截图：`outputs/<RUN_ID>/artifacts/poster/v1.png`（用 `html_screenshot.py` 渲染）
- 配图（如需）：先调 `gen_image.py` 出图，存 `outputs/<RUN_ID>/artifacts/poster/assets/<n>.png`，HTML 用相对路径引用

## 海报构成

1. **主标题**（中文 brand 名或活动名，必须最大）
2. **副标题 / slogan**（一行，从 copy/v1.md 的 slogan 里挑或与之协同）
3. **核心信息**（1-2 行场景化文字，不是堆数据）
4. **配图**（可选）：1 张主视觉图，用 gen_image 出
5. **logo 角标**（如有 logo 已生成，引用 `../logo/v1-combo.png`）

## HTML 模板骨架

```html
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>主视觉 · <品牌></title>
<!--
  设计依据：
  - 主色 <HEX>：来自 brand-spec.md Primary
  - 字体配对：<Display> / <Body>
  - 版式参考：<例：Kenya Hara 留白克制 / Pentagram 信息建筑>
-->
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700;900&family=Noto+Sans+SC:wght@300;400;700&display=swap');
  :root {
    --primary: #...;     /* brand-spec.md 主色 */
    --bg: #...;
    --ink: #...;
    --accent: #...;
  }
  html, body { margin: 0; padding: 0; }
  body {
    width: 1200px; height: 1600px;       /* 竖版 A2-ish */
    background: var(--bg);
    color: var(--ink);
    font-family: 'Noto Sans SC', system-ui, sans-serif;
    text-wrap: pretty;
    padding: 96px 80px;
    box-sizing: border-box;
    display: grid;
    grid-template-rows: auto 1fr auto;
  }
  .display {
    font-family: 'Noto Serif SC', serif;
    font-weight: 900;
    font-size: 144px;
    line-height: 1.05;
    letter-spacing: -0.02em;
  }
  /* 其余 grid / 留白 / 版式自行设计 */
</style>
</head>
<body>
  <header>
    <!-- logo 角标 + 标签 -->
  </header>
  <main>
    <h1 class="display">…</h1>
    <p class="lede">…</p>
    <!-- 配图（可选） -->
  </main>
  <footer>
    <!-- 极小号信息 / 边距收尾 -->
  </footer>
</body>
</html>
```

## 截图固定流程

写完 HTML 一定执行：

```bash
uv run python tools/html_screenshot.py \
  --html outputs/<RUN_ID>/artifacts/poster/v1.html \
  --output outputs/<RUN_ID>/artifacts/poster/v1.png \
  --width 1200 --height 1600
```

## 反 slop 自检

海报类高频翻车：
- ❌ 多个色块拼贴（拼贴 ≠ 设计）
- ❌ 把 slogan 重复 3 遍当装饰
- ❌ 居中对齐 + 下方居中副标题——这是 PPT 不是 poster
- ❌ Inter / Arial 当主标题字体——中文场景必须用 Noto Serif/Sans SC 或类似衬线/无衬线对
- ❌ 用 `linear-gradient(135deg, #purple, #pink)` 当背景

正向：
- ✅ 一个超大主标题 + 大量留白 + 一两条小信息
- ✅ 配图占据明确区域，与文字区隔开
- ✅ 严格用 brand-spec.md 的 4-5 个色值，不发明新色
