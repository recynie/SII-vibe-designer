# Schema · facts.md

`facts.md` 是 researcher 调研产出的第一份结构化文件。每条事实必须可追溯到来源或本地落盘资源；下游 `brand-spec.md` 的 `[from-fact: ...]` 引用必须能在本文件中找到原文。

## 顶层结构

```markdown
# Facts · <主题名>

> 采集日期：YYYY-MM-DD
> RUN_ID：<run-...>

## <分类一，例：基础信息>

- <一行事实> [source: <URL 或 "brief">]
- <一行事实> [asset: assets/<filename>]

## <分类二，例：视觉资产>

- <一行事实> [asset: failed - <原因>]
```

## 行级语法

每条事实**单行**且必须以下列三种标签之一收尾（行内可同时出现 `[source]` 与 `[asset]`，但至少有一个）：

| 标签 | 含义 | 形态 |
|---|---|---|
| `[source: <ref>]` | 引用来源；`<ref>` 可为完整 URL、`brief`、或简短描述 | `[source: https://...]` / `[source: brief]` |
| `[asset: <path>]` | 已下载到本地的资源相对路径，必须以 `assets/` 起头 | `[asset: assets/logo.svg]` |
| `[asset: failed - <reason>]` | 试过下载但失败；`<reason>` 不能为空 | `[asset: failed - 403 forbidden]` |

不允许出现裸 URL（必须包在 `[source: ...]` 内）。不允许 `[source]` 内容为空。

## 校验规则（`tools/validate_facts.py`）

1. 第一行必须以 `# Facts` 开头
2. 顶部 5 行内必须出现 `> 采集日期：YYYY-MM-DD`
3. 每条以 `- ` 起头的行必须命中至少一个合法标签：
   - `[source: <非空>]`
   - `[asset: assets/<非空>]`
   - `[asset: failed - <非空>]`
4. `[asset: assets/<path>]` 引用的本地文件**应当存在**于 `outputs/<RUN_ID>/assets/` 下；校验脚本若拿不到 RUN_DIR 上下文，仅检查路径串格式
5. 标签语法错误（缺冒号 / 缺空格 / 标签嵌套）报错并打印行号

## 示例（合规）

```markdown
# Facts · 创智学院

> 采集日期：2026-05-16
> RUN_ID：run-20260516-120000-chuangzhi-academy

## 基础信息

- 创智学院（SII）位于上海徐汇区 [source: https://sii.edu.cn]
- 定位为 AI 研究型教育机构 [source: brief]

## 视觉资产

- 官方主 logo SVG 已下载 [asset: assets/sii-logo.svg]
- Pantone 主色 PMS 281 C [source: https://sii.edu.cn/brand]
- 招生页 banner 抓取失败 [asset: failed - 404 not found]
```

## 示例（违规，三处）

```markdown
# Facts · X

（缺少采集日期行）

## 基础

- 一条没有任何标签的事实
- 裸 URL https://example.com 不被接受
- [asset: failed -]   ← 原因为空
```

校验脚本对违规样本应退出非 0，并打印每条违规所在行号与具体原因。
