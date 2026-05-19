---
name: asset-prep
description: Toolchain handbook for reuse mode — processing existing assets under outputs/<RUN_ID>/assets/ with local commands into versioned artifacts and a v1.notes.md log. Forbids calling gen_image. Use when the deliverable spec declares mode: reuse and references an existing assets/<filename> source (logo re-export, resize, canvas fit, background fill, crop, etc.) — not for creating new imagery from scratch.
---

# Skill · Asset-Prep（reuse 模式工艺手册）

reuse 介质：用本地命令处理 `outputs/<RUN_ID>/assets/` 已有素材。**禁调 gen_image**（reuse 的核心是不重新生成）。

## 工艺要点

- 输入素材路径来自 deliverables.md `mode: reuse` 那行规格里的 `assets/<filename>` 引用。
- 输出落 `artifacts/<slug>/v1.<ext>`；同目录写 `v1.notes.md` 记录处理步骤（替代 prompt.txt）。
- 处理完用 Read 读取输出图，目视确认：内容完整、构图未破坏、颜色与 brand-spec 大体一致、没有明显调性跑偏。
- 处理完成后通过 Read 看图确认颜色与 brand-spec 大体一致。

## 常用操作

```bash
# SVG → PNG，固定尺寸
convert -density 300 -background none outputs/<RUN_ID>/assets/source.svg \
        -resize 1024x1024 \
        outputs/<RUN_ID>/artifacts/logo/v1.png

# PNG 等比缩放并居中填充到目标画布
convert outputs/<RUN_ID>/assets/source.png -resize 1024x1024^ -gravity center -extent 1024x1024 \
        outputs/<RUN_ID>/artifacts/logo/v1.png

# 加纯色背景（使用 brand-spec 中的背景色；只做明确需要的底色补齐）
convert outputs/<RUN_ID>/assets/source.png -background "#FAFBFC" -alpha remove -alpha off \
        outputs/<RUN_ID>/artifacts/logo/v1.png

# 裁切到指定区域（width×height + x_offset + y_offset）
convert outputs/<RUN_ID>/assets/source.png -crop 1024x1024+0+0 +repage \
        outputs/<RUN_ID>/artifacts/logo/v1.png
```

## v1.notes.md 模板

```markdown
# reuse notes · v1
- 输入：outputs/<RUN_ID>/assets/<filename>
- 操作链：<一句话每步>
- 关键参数：<density / resize / crop / background>
- 自检：已用 Read 查看输出图；颜色与 brand-spec 大体一致/存在明显偏离：<一句话说明>
```

## 反 slop 红线

- 不要为了“美化”叠滤镜（高斯模糊 / 锐化 / 暗角）——reuse 是保真处理。
- 不要在 reuse 输出上加额外 watermark / emoji / 装饰。
- 输出尺寸要严格按 deliverables 规格，不要“我觉得方一点更好”。
- 颜色只需与品牌调性大体一致，不追求像素级精确。

## 失败处理

- 本地处理命令报错（例如 SVG 渲染策略限制）→ 改用可用的等价命令或库；仍失败 → 写 `BLOCKED.md` 让 planner 决定回退到 create。
- 输入素材不在 assets/ 里 → 直接报错回 planner，不要去网上重新搜。
