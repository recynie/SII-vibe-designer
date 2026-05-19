# UI Mockup

产物形态：HTML 单页 + html_screenshot 渲 PNG。

## 选择指引（researcher 参考）

适合产出 UI mockup 的场景：落地页、H5 首屏、产品页、注册页。与海报的区别：mockup 模拟可交互的页面结构，有导航、分区、CTA 按钮等 UI 元素。

常见尺寸：

| 类型 | 宽×高 |
|---|---|
| 桌面落地页 | 1440×2400 |
| 移动端 H5 | 375×812 |

## 执行要点（designer 参考）

### 工艺要点

- 自包含 HTML，样式内嵌；body 固定宽
- 字族沿用 brand-spec `## 字体`
- 配图先 gen_image 出到 scratch/，HTML 用相对路径引用（传 `--candidates 1`）
- 截图：`uv run python tools/html_screenshot.py --html ... --output ... --width ... --height ...`

### 反 slop

- 圆角卡片 + 左侧 4px 彩色 accent border（最大公约数 SaaS）
- 每卡片配 emoji icon
- 渐变背景 + 白色卡片漂浮
- placeholder.com 灰图
- "赋能 / 一站式 / 全链路"出现在 hero 副标

### 正向

- 大字 + 留白 + 小段说明的层级
- 真实配图（gen_image）或诚实灰底 + "待替换"标注

更多落地页参考见 `references/open-design/design-templates/saas-landing/SKILL.md`。
