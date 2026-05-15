# Skill · UI Mockup

Designer 加载本 skill 时，做一页落地页 / H5 / app 首屏的 HTML。**不是真实可上线的网站**——是设计稿。

## 输出规格

按 brief 决定形态，二选一：

### 落地页（默认）
- HTML：`outputs/<RUN_ID>/artifacts/ui/landing.html`
- 截图：`outputs/<RUN_ID>/artifacts/ui/landing.png`
- 视口：1440×2400（桌面落地页竖向）

### H5 / 移动端
- HTML：`outputs/<RUN_ID>/artifacts/ui/h5.html`
- 截图：`outputs/<RUN_ID>/artifacts/ui/h5.png`
- 视口：375×812（iPhone 13）；用 viewport meta 缩放
- HTML body 固定 375px 宽，截图按 750×1624（2x）出

## 必含板块

落地页至少包含：
1. **顶部 Nav**（logo 角标 + 1-3 个链接占位，不写真实跳转）
2. **Hero**（大主标题 + 副标题 + 一个 CTA + 配图占位或真图）
3. **核心价值 × 3**（三栏，每栏一个简短卡片）
4. **底部 Footer**（极简版权一行）

H5 至少包含：
1. 全屏 hero（标题 + 副标题）
2. 关键信息块 × 2（垂直排列）
3. 底部 CTA

## HTML 骨架（落地页版）

```html
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>落地页 · <品牌></title>
<!--
  设计依据：
  - 主色 <HEX>: brand-spec.md Primary
  - Hero 配图: artifacts/ui/assets/hero.png（用 gen_image 出，prompt 见同文件）
  - 字体配对: Noto Serif SC (display) / Noto Sans SC (body)
  - 反 slop: 不用左侧 accent border 卡片、不用 emoji 图标、不用紫渐变
-->
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@700;900&family=Noto+Sans+SC:wght@400;500&display=swap');
  :root {
    --primary: #...; --bg: #...; --ink: #...; --accent: #...;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    width: 1440px;
    background: var(--bg);
    color: var(--ink);
    font-family: 'Noto Sans SC', system-ui, sans-serif;
    text-wrap: pretty;
  }
  nav { padding: 24px 80px; display: flex; justify-content: space-between; align-items: center; }
  .hero { padding: 120px 80px 96px; display: grid; grid-template-columns: 1.2fr 1fr; gap: 64px; align-items: center; }
  .hero h1 { font-family: 'Noto Serif SC', serif; font-weight: 900; font-size: 88px; line-height: 1.05; letter-spacing: -0.02em; margin: 0 0 24px; }
  .hero p { font-size: 22px; line-height: 1.5; max-width: 540px; margin: 0 0 40px; color: color-mix(in oklch, var(--ink) 75%, transparent); }
  .cta { display: inline-block; padding: 16px 36px; background: var(--primary); color: var(--bg); font-weight: 500; text-decoration: none; }
  .values { padding: 96px 80px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 48px; }
  .values article h3 { font-family: 'Noto Serif SC', serif; font-size: 28px; margin: 0 0 12px; }
  footer { padding: 48px 80px; font-size: 14px; color: color-mix(in oklch, var(--ink) 50%, transparent); border-top: 1px solid color-mix(in oklch, var(--ink) 12%, transparent); }
</style>
</head>
<body>
  <nav>...</nav>
  <section class="hero">
    <div>
      <h1>...</h1>
      <p>...</p>
      <a class="cta" href="#">...</a>
    </div>
    <img src="assets/hero.png" alt="主视觉" style="width:100%; aspect-ratio: 4/5; object-fit: cover;">
  </section>
  <section class="values">
    <article><h3>...</h3><p>...</p></article>
    <article><h3>...</h3><p>...</p></article>
    <article><h3>...</h3><p>...</p></article>
  </section>
  <footer>...</footer>
</body>
</html>
```

## 配图

如果 hero 需要配图，先调 gen_image：

```bash
mkdir -p outputs/<RUN_ID>/artifacts/ui/assets
uv run python tools/gen_image.py \
  --prompt "<editorial photography style prompt>" \
  --output outputs/<RUN_ID>/artifacts/ui/assets/hero.png \
  --aspect-ratio 4:3
```

## 截图

```bash
# 落地页
uv run python tools/html_screenshot.py \
  --html outputs/<RUN_ID>/artifacts/ui/landing.html \
  --output outputs/<RUN_ID>/artifacts/ui/landing.png \
  --width 1440 --height 2400

# H5
uv run python tools/html_screenshot.py \
  --html outputs/<RUN_ID>/artifacts/ui/h5.html \
  --output outputs/<RUN_ID>/artifacts/ui/h5.png \
  --width 375 --height 812
```

## 反 slop 自检

UI 类高频翻车：
- ❌ 圆角卡片 + 左侧 4px 彩色 border accent（最大公约数 SaaS 设计）
- ❌ 每个卡片配 emoji icon
- ❌ 渐变背景 + 白色卡片漂浮
- ❌ 用 placeholder.com / via.placeholder.com 的灰色占位图
- ❌ "赋能"、"一站式"、"全链路"出现在 hero 副标题
- ❌ 把 hero 配图做成 SVG 几何拼贴（这是 figma 默认模板风）

正向：
- ✅ 大字 + 留白 + 小段说明的层级清晰版式
- ✅ 真实配图（用 gen_image）或诚实灰色 placeholder（写明"待真实图替换"）
- ✅ 严格遵守 brand-spec.md 的 4-5 个色值
