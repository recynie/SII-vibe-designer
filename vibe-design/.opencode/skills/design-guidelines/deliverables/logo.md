# Logo

产物形态：1024×1024 PNG，1:1，flat vector 风。走 gen_image。

## 选择指引（researcher 参考）

适合产出 logo 的场景：新品牌创建、品牌升级。有官方 logo 素材时直接在规格中引用 `assets/<filename>`，不需要重新生成。

## 执行要点（designer 参考）

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

### Prompt 写作

- 描述概念而非描述结果：写 `a shield formed by two overlapping leaves` 而非 `a logo that represents security and nature`
- 结构：`<主体> + <关键词> + <配色> + <构图> + <质感>`
- 色彩描述：用品牌主色和强调色描述图形层级，例如 `deep navy primary shape with cyan accent details`
- 末尾必加：`flat vector, scalable, on solid background, no gradients, no emoji, no photorealistic textures, no faces`
- 中文品牌名：`containing the Chinese characters "<名>"`（不要让模型自己生中文）

### 形态自检

负空间要显式描述；线条粗细全局统一；16×16 看不清的细节不该存在。

### 调用

```bash
uv run python tools/gen_image.py \
  --prompt "<英文 prompt>" \
  --output outputs/<RUN_ID>/artifacts/<slug>/v1.png \
  --aspect-ratio 1:1
```

### 反 slop

- 假国际范装饰（星月、emoji 风插图）
- 细密线条（缩小后糊成一团）
- 写实材质（金属/玻璃质感——那是渲染图不是 logo）
