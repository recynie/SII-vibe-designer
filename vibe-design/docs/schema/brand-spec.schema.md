# Schema · brand-spec.md

`brand-spec.md` 是 researcher 在 facts.md 之后产出的第二份结构化文件。**它是约束不是模板**：色板 / 字族 / 调性是硬锁，流派 / 构图 / 装饰由 designer 自由发挥。

## 顶层结构

```markdown
# Brand Spec · <主题名>

# 严格度: light | strict

## 色板
- Primary: #XXXXXX [from-fact: <事实片段>]
- Secondary: #XXXXXX [inferred: <理由>]
- Background: #XXXXXX [inferred: 中性底色搭配]
- Ink: #XXXXXX [inferred: 高对比正文色]
- Accent: #XXXXXX [inferred: 强调点]

## 字体
- Display: <字族名> [from-fact: <事实片段>]
- Body: <字族名> [inferred: 系统原生避免授权]

## 调性
- 关键词1, 关键词2, 关键词3

## 视觉气质
- 形容词1, 形容词2, 形容词3

## 反 slop 禁区
- 禁项1
- 禁项2
```

## 字段标签语法

每个**带值字段**（色板每条、字体每条）必须以下列两种标签之一收尾：

| 标签 | 含义 | 形态 |
|---|---|---|
| `[from-fact: <片段>]` | 该字段来自 facts.md，`<片段>` 是 facts.md 中的关键词或子串，校验时会回查 | `[from-fact: PMS 281 C]` |
| `[inferred: <理由>]` | 字段为推断，必须给一句理由 | `[inferred: 高对比正文色]` |

调性 / 视觉气质 / 反 slop 三段不需要逐项标签（它们本身就是设计判断）。

## 严格度声明

文件顶部必须出现 `# 严格度: light` 或 `# 严格度: strict` 行：

- `strict`：deliverables.md 中行数 ≥ 4 时使用——所有色板字段必须给出，所有 from-fact 引用必须可在 facts.md 找到
- `light`：deliverables.md 中行数 < 4 时使用——允许部分字段为空（用 `-` 占位），降低 over-spec 噪音

## 校验规则（`tools/validate_brand_spec.py`）

1. 第一行必须以 `# Brand Spec` 开头
2. 必须出现一行符合 `^# 严格度:\s*(light|strict)\s*$` 的声明
3. 必须包含 `## 色板` `## 字体` `## 调性` 四个一级章节（顺序可调，但都要有）
4. `## 色板` 下每行 `- <角色>: #HEX` 必须命中 `[from-fact: ...]` 或 `[inferred: ...]` 标签之一
5. `## 字体` 下每行 `- <角色>: <名>` 同上
6. 所有 `[from-fact: <片段>]` 引用必须能在同 RUN_DIR 的 `facts.md` 中找到子串匹配（区分大小写不严格，去除首尾空白）
7. 所有 hex 必须形如 `#` 后跟 3 或 6 位 16 进制（不接受 `rgba()` / `oklch()` 等）
8. 如果某 `## 色板` 行声明 `[from-fact: <片段>]` 且该 fact 中含完整 6 位 hex（如 `#1A73E8`），spec 行的 hex 必须与 fact 中的 hex 完全一致

## 严格度联动

- `strict` 模式：色板 5 条必须齐全（Primary / Secondary / Background / Ink / Accent）
- `light` 模式：色板至少给 Primary 与 Background；其它可写 `- Secondary: -`（值为单破折号，跳过标签校验）

## 示例（合规 · strict）

```markdown
# Brand Spec · 创智学院

# 严格度: strict

## 色板
- Primary: #1A73E8 [from-fact: 主色 #1A73E8]
- Secondary: #00A86B [inferred: 成长绿表达进阶]
- Background: #FAFBFC [inferred: 近白底保证可读]
- Ink: #1F2937 [inferred: 深灰高对比]
- Accent: #F59E0B [inferred: 能量橙提示 CTA]

## 字体
- Display: Noto Serif SC [inferred: 中文学术调性]
- Body: Noto Sans SC [inferred: 系统原生]

## 调性
- 专业, 进取, 现代, 清晰

## 视觉气质
- 高对比, 留白克制, 几何精简

## 反 slop 禁区
- 紫渐变
- emoji 图标
```

## 示例（违规）

```markdown
# Brand Spec · X
（缺严格度声明）

## 色板
- Primary: #FFF [inferred: 太亮]   ← 仅 3 位 hex 不合 hex 严格写法（不强制）
- Secondary: #00A86B               ← 缺标签
- Ink: #ABC123 [from-fact: 黑色]   ← 引用片段在 facts.md 找不到
```

校验脚本必须分别报告：缺严格度、缺标签、from-fact 失配。
