# 反 AI Slop 完整检查清单

所有视觉产物（gen_image / HTML / 素材转换）出图后对照本清单逐项检查。

## P0 硬拒绝（出现即不通过）

1. Tailwind 默认 indigo `#6366f1` 做强调色
2. 双色 "trust" 渐变铺 hero 背景
3. Emoji 充当功能图标
4. Display 位置用 brand-spec 未指定的字族
5. 圆角卡片 + 左侧 4px 彩色 border accent
6. 凭空捏造的数据指标 / 假引用 / 假头像
7. 填充式废话文案（Lorem ipsum / "赋能""打造""生态"）

## P1 软信号（累计 ≥ 3 条视为 slop）

- Hero → Features → Pricing → FAQ → CTA 模板式排序
- placeholder CDN 图片（unsplash/picsum 直链）
- `:root` 外散落 > 12 个裸 hex
- `var(--accent)` 出现 6+ 次
- Bento grid 滥用 / 千篇一律卡片网格
- AI 技术 cliché：渐变球体、数字雨、蓝色电路板、机器人面孔、cyber neon（深蓝底 + 霓虹辉光）

## 字体陷阱

Inter / Roboto / Arial / Helvetica 做 display = 零辨识度。brand-spec 已锁字族——如果 spec 就写了这些，在 body 用可以，display 位置必须用 spec 的 Display 字族。

## 图像生成专项

- 假国际范装饰（星月、emoji 风插图）
- 细密线条（缩小后糊成一团）
- 写实材质出现在 logo（金属/玻璃质感——那是渲染图不是标志）
- 通用 stock photo 感：握手、一群人指着笔记本电脑、天空+云
- 过饱和 HDR 风格
- 产品悬浮在渐变背景上（要有接触面）

## HTML 排版专项

- 多色块拼贴 ≠ 设计
- slogan 重复 3 遍当装饰
- 居中 + 居中副标 = PPT
- `linear-gradient(135deg, purple, pink)` 当背景
- 渐变背景 + 白色卡片漂浮
- placeholder.com 灰图

## gen_image prompt 尾部约束模板

Logo 类：`flat vector, scalable, on solid background, no gradients, no emoji, no photorealistic textures, no faces`

KV / 效果图类：`use the brand color mood for lighting and accents, clean composition, no extra fingers, no warped text`

## 注入灵魂

~80% 成熟模式 + ~20% 独特选择：

- **一个大胆视觉决策**（异常字号、破格出血、极端留白）
- **一处产品专属细节**（来自 facts.md 的真实信息，不是泛用装饰）
- 中文标点用「」不用 ""

---

## Canvas 精炼原则

来源：Anthropic canvas-design skill。

- **减少而非增加**：能删除的元素永远优先于添加新元素。添加一个图形能提高质量的话，删除一个多余元素通常能提高更多。
- **过度设计信号**：≥ 5种不同颜色同时活跃、3+种字号共存、≥ 2种装饰性图形（非信息承载）。
- **工艺感缺失信号**：均匀间距、对称布局、默认字距、无视觉层级断裂点、元素之间无"有意的张力"。
- **目标是"经得起反复观看"**——每个对齐、间距、颜色选择都应体现顶级工艺水平，看起来像花了无数小时打磨的作品。
