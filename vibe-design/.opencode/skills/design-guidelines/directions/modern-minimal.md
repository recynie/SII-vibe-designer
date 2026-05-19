# Direction · Modern Minimal

参考：Linear, Vercel, Notion 2024, Stripe docs

## 氛围

安静、精确、软件原生。系统字体、干净中性基底，加上小范围但可见的产品色（primary + secondary + status/accent）。界面感强而非灰度无色。交互状态、插画、图表、产品场景承载色彩。

## 色板

| 角色 | hex | 说明 |
|---|---|---|
| Background | #FAFBFE | 近白微蓝 |
| Surface | #FFFFFF | 纯白 |
| Ink | #1A1D2E | 深蓝墨 |
| Muted | #7C819A | 中灰蓝 |
| Border | #E8EAF0 | 浅灰蓝 |
| Accent | #3B5BDB | 钴蓝 |

## 字体

- Display: -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, sans-serif
- Body: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif

## Posture

- Display 字距 -0.02em
- 仅 hairline 边框，不用阴影（下拉/弹窗除外）
- 等宽数字 `font-variant-numeric: tabular-nums`
- 磨砂导航栏，内容主导布局；产品插画、设备 mockup 或数据可视化仅在澄清产品时使用
- 受控色彩系统：primary action + 一个 secondary signal + status colors；避免无色输出，但不要每个卡片都加渐变
