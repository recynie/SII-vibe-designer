# Vibe Design · 答辩 PPT

3 页幻灯片，1920×1080，HTML 实现可在浏览器键盘翻页。

## 浏览方式

```bash
# 任一现代浏览器打开
open docs/presentation/index.html  # macOS
xdg-open docs/presentation/index.html  # Linux
```

← / → 翻页，F 全屏。

## 内容

| # | 标题 | 重点 |
|---|---|---|
| 01 | 系统架构 | Planner + 3 subagents + 2 tools 拓扑图 |
| 02 | 调度时序 | 串行调度时序图 + 5 条关键设计纪律 |
| 03 | Demo | 实跑创智学院 brief 的真实视觉产出（logo + critic 评分 + 运行指标） |

## 静态截图

`assets/01-architecture.png` / `02-sequence.png` / `03-demo.png` 是各页 1920×1080 PNG，
导出场景（如打印 / 提交 zip）使用。

```bash
# 重新渲染
uv run python ../../vibe-design/tools/html_screenshot.py \
  --html 01-architecture.html --output assets/01-architecture.png \
  --width 1920 --height 1080
```
