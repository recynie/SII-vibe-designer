# Skill · Poster（介质工艺手册）

Poster 介质：HTML 竖版（默认 1200×1600）+ html_screenshot 渲 PNG。

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
