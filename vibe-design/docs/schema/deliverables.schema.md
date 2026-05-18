# Schema · deliverables.md

`deliverables.md` 是 researcher 在 facts.md / brand-spec.md 之后产出的第三份结构化文件，给 planner 当调度清单。**四段式**结构：显式 / 隐式 / 拒绝 / 决策依据。

## 顶层结构

```markdown
# Deliverables · <主题名>

## 显式
- <名称> | mode: create | <一句话规格>
- <名称> | mode: reuse | <一句话规格 + 引用 assets/ 路径>

## 隐式
- <名称> | mode: create | <一句话规格 + 推断理由>

## 拒绝
- <名称> | <为什么不做>

## 决策依据
- 显式条目来自 brief 第 N 句 / facts.md「<片段>」
- 隐式条目的依据 / 拒绝条目的依据
```

## 行级语法

### 显式 / 隐式 段

每行必须形如：

```
- <名称> | mode: <create|reuse> | <规格说明>
```

- `<名称>` 非空、不含 `|` 字符
- `mode:` 严格小写，仅接受 `create` 或 `reuse`；`reuse` 模式的规格里**应当**引用 `assets/` 下某文件
- `<规格说明>` 一句话，说明用途、尺寸、关键约束（不要写做法）

### 拒绝段

每行必须形如：

```
- <名称> | <理由>
```

不带 mode（拒绝项不会被生产）。理由不能为空。

### 决策依据段

自由文本，不强校验，但必须非空（用于事后审计）。

## 校验规则（`tools/validate_deliverables.py`）

1. 第一行必须以 `# Deliverables` 开头
2. 必须包含四个一级章节：`## 显式` `## 隐式` `## 拒绝` `## 决策依据`（顺序固定）
3. 显式段至少 1 条
4. 显式 / 隐式段每行必须能拆分为 3 段（`<名称>` / `mode: <c|r>` / `<规格>`），且 mode 仅接受 `create` 或 `reuse`
5. 拒绝段每行必须能拆分为 2 段（`<名称>` / `<理由>`）
6. 决策依据段必须有至少 1 条 `- ` 起头的行
7. 显式 + 隐式段中，名称去重（不接受同名两条）
8. **隐式段 ≤ 2 条**；超过则报错
9. **显式 + 隐式合计 ≤ 5 条**；超过则报错（次要物料移到拒绝段并写"超出 5 件上限"）

## 示例（合规）

```markdown
# Deliverables · 创智学院

## 显式
- Logo 主标志 | mode: reuse | 直接使用官方 SVG (assets/sii-logo.svg)，导出 1024×1024 PNG
- 招生页落地页 | mode: create | 1440×2400 落地页，hero + 三栏价值 + footer
- Slogan | mode: create | 14 字内中文 × 3 变体

## 隐式
- 品牌一段简介 | mode: create | 80-120 字第三人称；用户未明说但宣传场景必备

## 拒绝
- 短视频脚本 | brief 未提及视频媒介，超出本 run 平面设计范围

## 决策依据
- 显式条目来自 brief 第 1 句「请为创智学院做一套品牌形象设计」
- Logo 走 reuse：facts.md 已抓到官方 SVG，重新生成有失真风险
- 招生页 / Slogan 是 brief 显式列出的"主视觉海报、文案"映射
- 简介属隐式：宣传海报的副本必备，但 brief 未点名
```

## 示例（违规，多类）

```markdown
# Deliverables · X

## 显式
- Logo | mode: CREATE | 缺规格      ← mode 大小写错
- 海报 mode reuse                    ← 缺 | 分隔
- Logo | mode: create | 同名重复

## 隐式
（空段）

## 拒绝
- 视频                                 ← 理由空

## 决策依据
（空）
```

校验脚本必须分别报告：mode 大小写、分隔符缺失、显式段空、拒绝段无理由、决策依据空。
