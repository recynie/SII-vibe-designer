# 主视觉图 (Key Visual)

产物形态：PNG 效果图，走 gen_image。

与 logo 的区别：KV 不是扁平矢量标志，而是场景化、氛围化、叙事化的视觉图像。可以是摄影感、插画风、艺术化。

## 选择指引（researcher 参考）

适合产出 KV 的场景：品牌门面、活动主视觉、招生/招聘宣传、社交媒体封面配图、官网 hero 区配图。

Researcher 在 deliverables 规格中须指定：用途、宽高比、视觉风格倾向。

常见宽高比参考：

| 用途 | 推荐宽高比 | 说明 |
|---|---|---|
| 社交场景 / 通用 | 1:1 | 方图，适配多平台 |
| 竖版海报配图 | 3:4 | 竖向构图 |
| 横幅 / hero 区 | 16:9 | 宽幅，主体偏侧留文字空间 |
| 文章封面 | 4:3 | 传统比例 |

## 执行要点（designer 参考）

### Prompt 写作

按 SKILL.md 的 5 步法组装 prompt。KV 与 logo 的 prompt 差异：

- **场景描述优先**：写 `students walking through a glass-walled corridor with warm afternoon light` 而非 `academic atmosphere`
- **颜色做氛围**：brand-spec 的 hex 用于整体色调/光照倾向，不是平涂填色
- **构图指令具体**：`subject centered with negative space on right for text overlay`
- **末尾约束**：`STRICTLY use color palette tones from #X and #Y — NO purple gradients, NO neon glow, NO default AI blue`

### 调用

```bash
uv run python tools/gen_image.py \
  --prompt "<英文 prompt>" \
  --output outputs/<RUN_ID>/artifacts/<slug>/v1.png \
  --aspect-ratio <deliverables 规格中的宽高比>
```

### 反 slop

- AI 技术 cliché：渐变球体、数字雨、蓝色电路板、机器人面孔、cyber neon
- 通用 stock photo 感：握手、一群人指着笔记本电脑、天空+云
- 过饱和 HDR 风格
- 扁平矢量风（那是 logo 的领域）

更多 prompt 示例见 `references/open-design/prompt-templates/image/`。
