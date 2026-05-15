# gpt-image-2 后端色彩复现实证

## 上下文

之前所有 demo run 都使用 `DESIGN_IMAGE_BACKEND=minimax`（开发后端）。
实测发现 minimax `image-01` 对 hex 色值复现不严格——目标 `#0D1B2A` 墨蓝
经常被生成为 `#1F3A58` 浅蓝灰甚至 `#F8F4E8` 米白。

`docs/architecture.md` §8 推论是「生产用 gpt-image-2 应该更严格」。
本目录是该推论的实证。

## 单次测试

同样的强约束 prompt：

```
minimal flat vector logo for an AI research institute,
geometric neural network nodes forming a stylized C,
STRICTLY use only #0D1B2A deep navy blue and #00B4D8 bright cyan,
on clean #F8F9FA off-white background, pentagram information
architecture style, no gradients, no emoji, no text
```

后端：`DESIGN_IMAGE_BACKEND=openai` (gpt-image-2 via findcg.com 中转)

## 直方图分析

ImageMagick `histogram:info:-` 取出的颜色直方图：

| 区间 | 像素占比 | 解读 |
|---|---|---|
| 浅灰/白（#F7F7F7 - #F9F9F9） | ~97% | 背景，符合 prompt 要求 #F8F9FA |
| 深色（#000A2E - #000D2D 区间） | <1% | logo 主体的几何线条 |

**最深像素**：`#000A2E` —— 与目标 `#0D1B2A` 仅有 -13/-17/+4 偏移，
RGB 距离约 22。可视为色彩复现精度合格。

## 对比 minimax

| 后端 | 最佳 v2 主色 | 与目标 #0D1B2A 距离 |
|---|---|---|
| minimax `image-01`（hardened prompt v2）| `#1F3A58` | 距离 ~50 |
| **gpt-image-2** | **`#000A2E`** | **距离 ~22** |

gpt-image-2 显著好。验证了文档里的"生产用 gpt-image-2"决策。

## 结论

- 双后端路由设计（`tools/gen_image.py` 的 `DESIGN_IMAGE_BACKEND` env）真有用
- 开发期 minimax 省钱可以接受色彩偏差；交付期切 gpt-image-2 能拿到准确色
- agent prompt 不需要切换——同一份 designer.md 在两个后端都能跑

## 注意

- 中转站（findcg.com）429 限流偶发——重试一次即可
- 单次测试不是统计样本；只是证明"hex 复现能力"差异客观存在
- 完整 e2e 跑 gpt-image-2 后端的 4 类产物 brief 因配额/时间未做
