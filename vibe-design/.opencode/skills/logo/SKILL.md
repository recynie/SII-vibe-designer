---
name: logo
description: Design decisions and toolchain handbook for producing a 1024×1024 flat-vector logo PNG via gen_image. Covers logo type selection (wordmark/lettermark/pictorial/abstract/combination/emblem), concept-first prompt writing, shape self-check, English prompt structure, strict color locking, anti-slop tail terms, and Chinese brand name handling. Use when the deliverable spec calls for a logo, brand mark, or icon as a static PNG (not HTML, not photoreal product shot).
---

# Skill · Logo（介质工艺手册）

Logo 介质：1024×1024 PNG，1:1，flat vector 风。

## 设计决策

### 类型选择

先选类型，再写 prompt：

| 类型 | 适用场景 |
|---|---|
| Wordmark | 品牌名本身有辨识度（字体即标志） |
| Lettermark | 名称过长，取首字母 |
| Pictorial mark | 有强关联具象物（动物、建筑、器物） |
| Abstract mark | 科技/抽象概念，无具象对应 |
| Combination mark | 需要图文并排的通用场景 |
| Emblem | 传统/学术/官方机构（徽章式） |

### 概念优先

描述概念而非描述结果：写 `"a shield formed by two overlapping leaves"` 而非 `"a logo that represents security and nature"`。具象视觉描述 > 抽象形容词。

### 形态自检

负空间要显式描述；线条粗细全局统一；16×16 看不清的细节不该存在。

## 工艺要点
- gen_image prompt 用全英文，结构 `<主体> + <关键词> + <配色> + <构图> + <质感>`
- 颜色强约束：`STRICTLY use only #X for X, #Y for Y - NO other colors, NO color shifts`
- 末尾必加：`flat vector, scalable, on solid background, no gradients, no emoji, no photorealistic textures, no faces`
- 中文品牌：写 `containing the Chinese characters "<名>"`，不要让模型自己生中文（90% 出错字）

## 调用模板

```bash
uv run python tools/gen_image.py \
  --prompt "<英文 prompt>" \
  --output outputs/<RUN_ID>/artifacts/logo/v1.png \
  --aspect-ratio 1:1
```

默认并行生成 3 候选（`v1-1.png` / `v1-2.png` / `v1-3.png`）。Read 全部候选，选最佳 `mv` 为 `v1.png`。

## 反 slop 红线
- 假国际范装饰（星月、emoji 风插图）
- 细密线条（vector 后糊）
- 写实材质（金属/玻璃质感）——这是渲染图不是 logo
- Inter / Arial 当 display
