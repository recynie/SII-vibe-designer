# Vibe Design · 项目介绍 PPT

5 页幻灯片，1920×1080，HTML 实现可在浏览器键盘翻页。

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
| 01 | 项目概览 | 系统定位、核心思路、题目覆盖、模型栈 |
| 02 | 系统架构 | 4-agent 拓扑图 + 职责分界表 + 扩展哲学 |
| 03 | 数据流与迭代 | 6 步 pipeline + Critic 5 维度评分 + 文件即契约 |
| 04 | 关键设计决策 | 6 条从实测中来的设计纪律（串行调度 / 文件契约 / 反 slop 等） |
| 05 | 实跑 Demo | 创智学院端到端产出 + 7 次 run + 3 领域泛化 |

## 截图

`screenshots/` 下有各页 1920×1080 PNG。

```bash
# 重新渲染全部截图
for i in 01-title 02-architecture 03-dataflow 04-decisions 05-demo; do
  uv run python vibe-design/tools/html_screenshot.py \
    --html docs/presentation/${i}.html \
    --output docs/presentation/screenshots/${i}.png \
    --width 1920 --height 1080
done
```
