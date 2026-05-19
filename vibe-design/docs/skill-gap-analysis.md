# Skill Gap Analysis — 参考项目可提取内容

> 基于 `references/open-design/`、`references/huashu-design/` 的全量扫描，评估可融入 `vibe-design/.opencode/skills/` 的内容。

## 现有 Skills 概览

| Skill | 职责 | 核心机制 |
|---|---|---|
| `craft` | 设计工艺基线 + 反 AI slop 检查清单 | 字排/色彩/层级/构图数值基线 |
| `design-guidelines` | 产物类型参考手册 | 按 deliverable 类型提供规格、工艺要点、工具链指引 |

**共性模式**：craft 提供跨产物的设计质量底线，design-guidelines 按产物类型提供具体指引。

---

## 🟢 强烈推荐引入（完整可落地内容）

### 1. 设计工艺基线 — `references/open-design/craft/`

四份文件含精确、可检查的数值规则，不是原则性口号。

#### 1.1 `craft/typography.md` — 字体排印规则

| 规则域 | 关键内容 |
|---|---|
| 字号体系 | 7 级（Display → Caption），每级给出 px 区间 |
| 行高 | 按字号分段：≤14px → 1.6，15–20px → 1.5，21–32px → 1.35，≥33px → 1.15–1.25 |
| **字距（最高价值）** | ALL CAPS 必须 ≥0.06em tracking；Display 需负字距；Body 保持 0 |
| 字体配对 | 全局最多 2 个 typeface；1 display + 1 body |
| 行宽 | 50–75ch（中文 25–35 字） |
| 字重 | 三档系统：400 / 550 / 600，禁渐变式 300→400→500→600→700 |

> **影响范围**：logo lockup、poster、ui-mockup 的 CSS 全部受益。字距表是区分"AI 生成"与"专业设计"的最显著单一指标。

#### 1.2 `craft/typography-hierarchy.md` — 排版层级

- **三合约**：一个主导入口点 → 层级间有意节奏 → 信息流可恢复
- **五向量**：scale / weight / spacing / tracking / alignment，主导元素至少激活两个
- **三层模型**：Primary / Secondary / Tertiary
- **反模式**：均匀字重阶梯、均匀间距、对称强调
- **lint 清单**：可直接移植为 critic 检查项

> **影响范围**：poster（构图扁平是当前最大弱点）、ui-mockup、critic 评审标准。

#### 1.3 `craft/color.md` — 色彩使用规则

| 规则 | 数值 |
|---|---|
| 四层结构 | neutral 70–90% / accent 5–10% / semantic 0–5% / effect <1% |
| 强调色纪律 | 每屏最多 2 处可见 accent |
| 对比度底线 | 正文 4.5:1，大字/UI 3:1 |
| **反默认色** | Tailwind indigo `#6366f1` = AI slop 第一特征；双色"信任"渐变 = 第二特征 |
| 暗色主题 | 禁纯黑 `#000` / 纯白 `#fff` |

> **影响范围**：logo 配色、poster 色彩分布、ui-mockup 全局。

#### 1.4 `craft/anti-ai-slop.md` — 反 AI 泛化规则

**P0 七宗罪**（硬拒绝）：

1. 默认 indigo 主色
2. 双色 "trust" 渐变
3. emoji 做图标
4. Display 位置用错字体
5. 圆角卡片 + 彩色左边框
6. 凭空捏造的数据指标
7. 填充式废话文案

**P1 软信号**：模板式节块排序、placeholder CDN 图片、accent 过度使用

**注入灵魂公式**：80% 成熟模式 + 20% 独特选择（一个大胆视觉决策 / 微文案里的人格 / 一个令人记住的微交互 / 一个产品专属细节）

> **影响范围**：全部产物 + critic。这是**单文件价值最高**的参考——每条规则可直接变为 critic 的硬性拒绝门槛。

---

### 2. Brief→设计规格转换器 — `references/open-design/skills/design-brief/SKILL.md`

这是扫描到的唯一有**完整实现**（~300 行逻辑）的 open-design skill。

**核心机制**：

- **I-Lang 协议**：8 个正交维度

  | 维度 | 示例值 |
  |---|---|
  | palette | `navy_and_white`, `earth_tones` |
  | accent | `coral`, `electric_blue` |
  | typography | `geometric_sans`, `humanist_serif` |
  | display_font | `DM_Serif_Display`, `Space_Grotesk` |
  | layout | `asymmetric`, `centered`, `editorial_grid` |
  | mood | `calm`, `bold`, `playful` |
  | density | `airy`, `balanced`, `dense` |
  | constraints | 自由文本（如"必须兼容深色模式"） |

- **NL→结构化映射表**：将模糊描述（"简洁""暗色""活泼"）对应到维度具体值
- **符号→token 解析**：`palette=navy_and_white` → 精确 hex / font stack / spacing px
- **默认值策略**：基于 mood 的自动回退，并在透明度报告中列出哪些维度被自动填充
- **DESIGN.md 模板**：9 节设计系统文档（视觉主题 / 色板 / 字体 / 组件 / 布局 / 景深 / Do's & Don'ts / 响应式 / Agent 提示指南）
- **brief-preview.html**：实时色卡 + 字体样张 + 间距尺 + 组件预览

> **影响范围**：planner agent。当前 planner 从一句话 brief 到 brand-spec 的映射缺少结构化中间层，8 维度框架可消除歧义、减少幻觉。

---

### 3. 华数设计参考 — `references/huashu-design/references/`

三份文件含可直接移植的中文设计场景规则。

#### 3.1 `critique-guide.md` — 设计评审框架

- **5 维评分**（各 1–10）：

  | 维度 | 权重说明 |
  |---|---|
  | 理念对齐 | brief 意图是否被准确表达 |
  | 视觉层级 | 信息优先级是否通过视觉手段传达 |
  | 工艺质量 | 字距/对齐/色彩/留白的精确度 |
  | 功能性 | 是否完成了预定交付物的功能目标 |
  | 原创性 | 是否跳出 AI 默认模式 |

- **场景权重矩阵**：海报优先视觉层级，App UI 优先功能性
- **10 大常见设计错误清单**（AI cliché / 字号层级缺失 / 配色过载 / 间距不一致…）
- **结构化评审输出模板**

> **影响范围**：critic agent——可直接作为评审标准的骨架。

#### 3.2 `design-styles.md` — 20 种设计风格库

- **5 大流派**：信息建筑 / 动态诗学 / 极简主义 / 实验先锋 / 东方哲学
- 每种风格含：哲学陈述 / 核心视觉特征 / **AI prompt DNA 片段** / 代表作品
- **场景×风格兼容矩阵**（web / PPT / PDF / 信息图 / 封面 / AI 生图）
- Prompt 书写指导：描述氛围而非布局
- 执行路径选择：HTML vs AI 生图 vs 混合

> **影响范围**：planner（风格推荐）+ designer（prompt DNA 种子用于 logo / poster 生成）。

#### 3.3 `content-guidelines.md` — 内容质量规则

- **四类陷阱**：
  - 视觉陷阱：渐变滥用 / 左边框强调卡片 / emoji 装饰 / 劣质 SVG
  - 字体陷阱：禁 Inter / Roboto / Arial，要求有辨识度的配对
  - 配色陷阱：禁凭空发明颜色，使用 oklch，引用已知色板
  - 布局陷阱：bento grid 滥用 / 千篇一律的 landing page
- **各介质最小规格**：幻灯片最小 24px / 网页最小 14px / 对比度阈值
- **内容原则**：无填充内容 / 先问再加 / 先建系统再出稿

> **影响范围**：designer + critic。与 `anti-ai-slop.md` 互补，更聚焦中文设计语境。

---

## 🟡 选择性引用（提取子集有价值）

| 来源 | 可提取内容 | 适用对象 |
|---|---|---|
| `craft/typography-hierarchy-editorial.md` | Display 戏剧性尺度跳跃（56–96px，与 body 3–5× 落差）；留白作为首要层级载体 | poster skill |
| `craft/laws-of-ux.md` | ~8 条与视觉构图相关的定律：Hick（3–5 主选项）、Gestalt（邻近/相似）、Jakob（惯例遵循）、Von Restorff（对比吸引注意）、Miller（7±2）、Aesthetic-Usability（好看=好用感知） | ui-mockup skill |
| `craft/accessibility-baseline.md` | 对比度精确阈值（4.5:1 正文 / 3:1 大字）；触控区域最小 24×24（AA）/ 44×44（AAA）；语义 HTML（heading / landmark / form label） | ui-mockup + logo skill |
| `huashu-design/SKILL.md` | 品牌资产采集协议（5 步：ask → search → download → verify → spec）；设计方向顾问流程（8 阶段，推荐 3 个差异化方向）；事实核查原则 | planner + researcher agent |
| `huashu-design/workflow.md` | 变体策略（保守→大胆的维度探索）；4-pass 迭代模型（假设占位 → 真实组件 → 细节打磨 → 验证交付） | planner agent 流程设计 |

---

## 🔴 不推荐引入

| 来源 | 原因 |
|---|---|
| `open-design/skills/` 下 12 个 stub | brand-guidelines / creative-director / copywriting / imagegen / enhance-prompt / image-enhancer / ad-creative / marketing-psychology / color-expert / taste-skill / screenshot / full-page-screenshot 均为**目录元数据 stub**（YAML + GitHub 链接），无 prompt、无逻辑、无可用内容 |
| `craft/animation-discipline.md` | 本项目全部产物为静态（PNG / HTML 截图），动画规则不适用 |
| `huashu-design/` 中 iOS / 视频 / React 相关部分 | 执行层技术栈不同（本项目不涉及 iOS 原型、视频导出、React 组件） |

---

## 建议新增 Skill 清单

| 优先级 | 新 Skill | 内容来源 | 服务 Agent | 核心价值 |
|---|---|---|---|---|
| **P0** | `craft-baseline.md` | `craft/typography.md` + `craft/color.md` + `craft/anti-ai-slop.md` 融合精选 | designer（全局约束层） | 字距表 + 四层色彩结构 + 七宗罪 = 产物质量基线 |
| **P0** | `critique-rubric.md` | `huashu-design/critique-guide.md` + `craft/typography-hierarchy.md` 评分维度 | critic | 5 维评分 + 层级 lint 清单 = 结构化评审标准 |
| **P1** | `design-brief.md` | `open-design/skills/design-brief/SKILL.md` 适配 | planner | 8 维度 I-Lang + NL→token 映射 = brief 到 spec 的结构化桥梁 |
| **P1** | `style-library.md` | `huashu-design/design-styles.md` 的 20 风格 + prompt DNA | planner + designer | 风格推荐 + 生图 prompt 种子库 |
| **P2** | 各现有 skill 补丁 | `craft/typography-hierarchy-editorial.md`（poster）、`craft/laws-of-ux.md` 子集（ui-mockup）、`craft/accessibility-baseline.md` 子集（ui-mockup + logo） | designer | 在现有 skill 的「工艺要点」段落中追加具体数值规则 |
