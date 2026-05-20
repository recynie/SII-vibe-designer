# 文创物料 (Merchandise)

产物形态：PNG 产品效果图，走 gen_image。画面呈现设计作品应用在实体产品上的效果。

## 选择指引（researcher 参考）

适合产出文创的场景：校园活动周边、品牌赠品、会议物料、文化衍生品、电商产品展示。

常见产品类型参考（不限于此）：帆布袋、马克杯、T恤、笔记本、徽章/胸针、手机壳、贴纸、雨伞、文件夹、卡套。Researcher 根据 brief 的受众和使用场景自由选择合适的产品类型。

文创通常适合使用多条目（一个主条目下列多个子产品效果图），Researcher 在规格中说明每个子产品的类型和呈现角度。

## 执行要点（designer 参考）

### 两步 Prompt 法

1. **描述产品实体**：材质、角度、光照、放置表面
2. **描述品牌设计在产品上的呈现**：印刷内容、位置、颜色

示例结构：`A white canvas tote bag, front view, flat lay on light wooden surface, soft studio lighting. The bag front is printed with [brand logo/pattern] using the brand color mood, covering 60% of the front area. Clean white background, no other objects.`

### 通用要点

- 光照：柔和棚拍，干净背景（白色、浅灰或原木表面）
- 角度：正面视角为主（清晰度优先）；45 度角可增加纵深感
- 产品底色：通常白色/本色，品牌设计作为印刷内容呈现
- 色彩提示：`The printed design uses the brand primary color mood with an accent on a white product base`
- 多产品效果图时用 `--candidates 1` 控制调用量

### 调用

```bash
uv run python tools/gen_image.py \
  --prompt "<英文 prompt>" \
  --output outputs/<RUN_ID>/artifacts/<slug>/v1.png \
  --aspect-ratio 1:1 \
  --candidates 1
```

### 反 slop

- 产品悬浮在渐变背景上（要有接触面）
- 细节过度密集（小产品上塞满复杂图案）
- 不真实的产品比例或材质
- 多产品杂乱堆砌（一张图专注一个产品）
