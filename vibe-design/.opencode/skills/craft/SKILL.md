---
name: craft
description: Numeric design baselines for visual deliverables — typography scale, color ratios, hierarchy vectors, composition rules, anti-AI-slop checklist. Each rule is a checkable number or judgement, not a slogan. Use when producing visual design artifacts such as logo, poster, UI mockup, or infographic. Skip for copywriting-only tasks and simple file conversion tasks.
---

# Skill · Craft（设计工艺基线）

视觉任务共享的设计知识层。每条规则给出可检查的数值或判据——不是原则口号。

brand-spec 锁定**用什么**（色板 hex、字族名、调性词）；craft 规定**怎么用好**（比例、间距、层级）。两者不重叠。

---

## 一、字排体系

### 字号阶梯

| 级别 | px 区间 | 用途 |
|---|---|---|
| Display | 48-72（海报/编辑式可推至 56-96） | 主标题、视觉锚点 |
| H1 | 32-48 | 页面标题 |
| H2 | 24-32 | 板块标题 |
| H3 | 20-24 | 子板块 |
| Body | 15-18 | 正文（中文建议 16-18） |
| Small | 13-14 | 辅助信息 |
| Caption | 11-12 | 注释、图说 |

标题与正文字号比 ≥ 2.5×。海报/编辑式场景中 Display 与 Body 的落差是设计签名——拉大而非缩小。

### 行高

| 字号段 | 行高 |
|---|---|
| ≥ 32px（Display / H1） | 1.0 - 1.2 |
| 15-18px（Body） | 1.5 - 1.6（中文 1.7 - 1.8） |
| ≤ 14px（Small / Caption） | 1.5 |

### 字距 letter-spacing

| 场景 | 值 |
|---|---|
| Body | 0 |
| Small / Caption | +0.01 - +0.02em |
| ALL CAPS | **≥ +0.06em**（必须，无例外） |
| Heading 32px+ | -0.01 - -0.02em |
| Display 48px+ | -0.02 - -0.03em |
| 编辑式 Display 56px+ | -0.02 - -0.05em |

字距是区分"AI 生成"与"专业设计"的最显著单一指标。

### 字重与配对

- 全局最多 **2 个 typeface**（1 display + 1 body）
- 三档系统：Read 400 / Emphasize 550 / Announce 600；700+ 极少使用
- Display 常用 light/regular（克制比粗体更有张力）
- 行宽：50-75ch（中文 25-35 字），CSS `max-width: 65ch`

---

## 二、色彩使用

### 四层比例

| 层 | 面积占比 | 说明 |
|---|---|---|
| Neutral（中性色） | 70-90% | 背景、正文、边框 |
| Accent（强调色） | 5-10% | CTA、关键标记 |
| Semantic（语义色） | 0-5% | 成功/警告/错误 |
| Effect（效果色） | < 1% | 阴影、光晕、微渐变 |

### 强调色纪律

- 每屏最多 **2 处**可见 accent（链接、hover/focus 环都算）
- brand-spec 色板已锁 hex——这里管的是用量和分布，不是色值本身

### 对比度底线

| 场景 | 最低对比度 |
|---|---|
| 正文（≤ 16px） | 4.5 : 1 |
| 大字（> 18px）/ UI 元素 | 3 : 1 |

### CSS 色彩

- 优先 `oklch()` 定义色彩（感知均匀，便于调和）
- 暗色主题禁纯黑 `#000` / 纯白 `#fff`——用 `#0f0f0f` / `#f0f0f0` 类近似值

---

## 三、视觉层级

### 核心三约

1. **一个主导入口点**——观者第一眼落在哪里，必须是你设计的
2. **层级间有意节奏**——相邻层级的视觉距离不均匀，有快有慢
3. **信息流可恢复**——打断后能从任意位置重新接上阅读路径

### 五向量

Scale / Weight / Spacing / Tracking / Alignment

主导元素至少**同时激活 2 个向量**（例如：放大 + 负字距；加粗 + 增加上方留白）。仅靠字号放大 = 单向量层级，效果弱。

### 三层模型

| 层 | 角色 |
|---|---|
| Primary | 入口点，视觉最重 |
| Secondary | 结构骨架，引导浏览路径 |
| Tertiary | 附属信息，安静存在 |

首屏可见层级 > 3 层通常意味着噪音。

### 层级反模式

- 渐变式字重阶梯（300 → 400 → 500 → 600 → 700）
- 均匀板块间距（每段等高 padding）
- 仅用 heading 做层级载体（忽略 spacing / tracking / alignment）
- 对称强调（左右两侧等重元素竞争注意力）
- 纯字号层级（只改 font-size，不碰其它向量）

---

## 四、构图与留白

- 留白 ≥ 画面总面积 **40%**（极简风格 ≥ 60%）
- Display 元素上下留白 ≥ **2× 当前行高**
- 间距节奏：密-疏-中 交替；**均匀间距 = 模板感**
- 一个元素做到 **120%**，其余 **80%**——禁止均匀用力
- 非对称节奏优先于对称平衡
- `text-wrap: pretty`（CSS）避免单字孤行

---

## 五、反 AI slop

### P0 硬拒绝（出现即不通过）

1. Tailwind 默认 indigo `#6366f1` 做强调色
2. 双色 "trust" 渐变铺 hero 背景
3. Emoji 充当功能图标
4. Display 位置用 brand-spec 未指定的字族
5. 圆角卡片 + 左侧 4px 彩色 border accent
6. 凭空捏造的数据指标 / 假引用 / 假头像
7. 填充式废话文案（Lorem ipsum / "赋能""打造""生态"）

### P1 软信号（累计 ≥ 3 条视为 slop）

- Hero → Features → Pricing → FAQ → CTA 模板式排序
- placeholder CDN 图片（unsplash/picsum 直链）
- `:root` 外散落 > 12 个裸 hex
- `var(--accent)` 出现 6+ 次
- Bento grid 滥用 / 千篇一律卡片网格
- AI 技术 cliché：渐变球体、数字雨、蓝色电路板、机器人面孔、cyber neon（深蓝底 + 霓虹辉光）

### 字体陷阱

Inter / Roboto / Arial / Helvetica 做 display = 零辨识度。brand-spec 已锁字族——如果 spec 就写了这些，在 body 用可以，display 位置必须用 spec 的 Display 字族。

### 注入灵魂

~80% 成熟模式 + ~20% 独特选择：

- **一个大胆视觉决策**（异常字号、破格出血、极端留白）
- **一处产品专属细节**（来自 facts.md 的真实信息，不是泛用装饰）
- 中文标点用「」不用 ""
