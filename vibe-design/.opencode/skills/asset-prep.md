# Skill · Asset-Prep（reuse 模式工艺手册）

reuse 介质：bash + ImageMagick 处理 `outputs/<RUN_ID>/assets/` 已有素材。**禁调 gen_image**（reuse 的核心是不重新生成）。

## 工艺要点
- 输入素材路径来自 deliverables.md `mode: reuse` 那行规格里的 `assets/<filename>` 引用
- 输出落 `artifacts/<slug>/v1.<ext>`；同目录写 `v1.notes.md` 记录处理步骤（替代 prompt.txt）
- 处理完跑 `tools/check_palette_compliance.py` 自检，色板偏了立刻调

## ImageMagick 常用操作

```bash
# SVG → PNG，固定尺寸
convert -density 300 -background none assets/sii-logo.svg -resize 1024x1024 \
        artifacts/logo/v1.png

# PNG 等比缩放并居中填充到目标画布
convert assets/source.png -resize 1024x1024^ -gravity center -extent 1024x1024 \
        artifacts/logo/v1.png

# 替换主色（在 -fuzz 容差内把旧 hex 替为新 hex）
convert assets/source.png -fuzz 8% -fill "#1A73E8" -opaque "#0050B5" \
        artifacts/logo/v1.png

# 加纯色背景
convert assets/source.png -background "#FAFBFC" -alpha remove -alpha off \
        artifacts/logo/v1.png

# 裁切到指定区域（width×height + x_offset + y_offset）
convert assets/source.png -crop 1024x1024+0+0 +repage \
        artifacts/logo/v1.png
```

## v1.notes.md 模板

```markdown
# reuse notes · v1
- 输入：assets/<filename>
- 操作链：<一句话每步>
- 关键参数：<density / fuzz / hex>
- 自检：check_palette_compliance 已跑（结果：通过/出现 X 散色）
```

## 反 slop 红线
- 不要为了"美化"叠滤镜（高斯模糊 / 锐化 / 暗角）——reuse 是保真处理
- 不要在 reuse 输出上加额外 watermark / emoji / 装饰
- 输出尺寸要严格按 deliverables 规格，不要"我觉得方一点更好"

## 失败处理
- ImageMagick 报错（policy.xml 拦 SVG）→ 改用 `--density` 或 librsvg；仍失败 → 写 `BLOCKED.md` 让 planner 决定回退到 create
- 输入素材不在 assets/ 里 → 直接报错回 planner，不要去网上重新搜
