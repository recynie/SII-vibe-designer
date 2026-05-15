# Skill · Logo 设计

Designer 加载本 skill 时，目标产出是品牌主标志的位图（PNG），1024×1024。

## 输出规格

- 路径：`outputs/<RUN_ID>/artifacts/logo/v1.png`
- 同目录写 `v1.prompt.txt` 记录 prompt + backend
- aspect-ratio 用 `1:1`

## 必产出 3 个变体

logo 是品牌识别度的根基，一次出 3 个变体让 Planner / 用户挑：
- `v1-mark.png` — 仅图形标（无文字）
- `v1-wordmark.png` — 文字标（中文/英文 brand 名 + 简单图形修饰）
- `v1-combo.png` — 图形 + 文字组合标

## Prompt 模板

通用骨架（按 brand-spec.md 填空）：

```
flat vector logo for "<品牌名>", <关键词1>, <关键词2>, <关键词3>,
two-tone using <Primary HEX> and <Secondary HEX>,
on a clean off-white background <Background HEX>,
geometric and timeless, scalable, designed in the style of <参考方向 e.g. Pentagram / Field.io>,
no gradients, no emoji, no photorealistic textures, no faces, no generic SVG humans,
no purple gradient, no Web 2.0 glossy effects.
```

针对中文品牌：用 `containing the Chinese characters "<中文品牌名>"` 而不是依赖模型自己生中文（图像模型中文常出错），如果品牌名是音译/中英混合则两版都试。

## 反 slop 自检

logo 类高频翻车点：
- 出现"假国际范"装饰：星星、月亮、emoji 风插图
- 出现细密线条（vector 后会糊）
- 出现写实材质（金属、玻璃质感）——这些不是 logo 是渲染图
- 出现错的字（图像模型 90% 中文是错字，少出文字）

## 设计依据写入 prompt.txt

格式：

```
# backend: <env>
# aspect: 1:1
# variant: mark | wordmark | combo
# 设计依据:
# - 使用 brand-spec.md Primary <HEX> 表达 <调性关键词>
# - 参考方向: <设计师/流派>
# - 形态选择: <为什么是这个图形/字形>

<完整英文 prompt>
```

## 二轮迭代（v2）

如果 critic 给出 prompt 层改进（例如"减一个图形元素"、"换更深的主色"）：
- 修改 prompt 重新调 gen_image
- v2.prompt.txt 顶部写 `# v2: <改了什么>`

如果 critic 给出素材层（"换图"）但实际是图本身的问题：
- 不重写整个 prompt，**只改 prompt 里 critic 指出的关键词**
