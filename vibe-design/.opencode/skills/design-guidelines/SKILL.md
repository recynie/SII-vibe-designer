---
name: design-guidelines
description: |
  设计方向与交付物类型参考。覆盖 5 种视觉风格方向（无品牌资产时的审美种子）和多种视觉设计产品类别（主视觉图、文创物料、宣传海报、Logo、UI mockup 等）。
  Use when planning brand-spec.md or deliverables.md — helps researcher choose visual direction and product types; helps designer find execution guidance for specific visual deliverable forms.
---

# Design Guidelines

本 skill 供 researcher 规划设计方向和交付物类型，也供 designer 查阅各产品形态的执行要点。

## 风格方向（directions/）

无品牌资产时，从以下 5 种方向中选择最匹配 brief 调性的一种，Read 对应文件获取色彩参考、字体、posture：

| 方向 | 适用场景 | 文件 |
|---|---|---|
| Modern Minimal | 科技/SaaS/工具/教育 | `directions/modern-minimal.md` |
| Editorial Magazine | 出版/媒体/文化/艺术 | `directions/editorial-magazine.md` |
| Tech Utility | 数据/工程/运维/仪表盘 | `directions/tech-utility.md` |
| Human Approachable | 消费/社区/教育/市场 | `directions/human-approachable.md` |
| Brutalist Experimental | 艺术/独立/agency/宣言 | `directions/brutalist-experimental.md` |

有品牌资产时跳过方向选择，从 facts.md 提取色彩参考/字体。

## 交付物类型（deliverables/）

Researcher 根据 brief 的目标受众、使用场景、传播渠道自主选择组合——没有固定公式。Read 对应文件获取该类型的选择指引和执行要点。

| 类型 | 产物形态 | 工具链 | 文件 |
|---|---|---|---|
| 主视觉图 (KV) | PNG 效果图 | gen_image | `deliverables/key-visual.md` |
| 文创物料 | PNG 产品效果图 | gen_image | `deliverables/merchandise.md` |
| 宣传海报 | HTML + 渲 PNG | html_screenshot | `deliverables/poster.md` |
| Logo | PNG 1024×1024 | gen_image | `deliverables/logo.md` |
| UI Mockup | HTML + 渲 PNG | html_screenshot | `deliverables/ui-mockup.md` |

以上列表仅为常见类型，不限于此。brief 暗示的其他产品形态同样可以列入 deliverables。

## Prompt 构图方法论

gen_image prompt 按以下 5 步顺序组装（提炼自 open-design `image-poster` workflow）：

1. **主体 + 构图** — 画面中有什么、在哪里、什么比例；视线和裁切
2. **光照 + 氛围** — 自然光/棚拍/情绪光；冷暖；主光+辅光+轮廓光
3. **色彩 + 质感** — brand-spec 的色彩参考；材质/肌理关键词
4. **镜头 / 景深** — 仅摄影感场景需要（"85mm portrait, shallow DOF"）
5. **反面清单** — 明确禁止的 AI slop 模式

详细 prompt 模板和 46 个实例见 `references/open-design/design-templates/image-poster/SKILL.md` 和 `references/open-design/prompt-templates/image/`。
