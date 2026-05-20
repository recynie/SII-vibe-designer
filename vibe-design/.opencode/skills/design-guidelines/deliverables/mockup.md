# Mockup（合成图）

产物形态：以 PNG 效果图为主，走 gen_image；部分 UI 场景走 HTML + html_screenshot 渲 PNG。

Mockup 的核心是"设计应用在真实载体上的效果呈现"——不是孤立的设计稿，而是设计在各场景中的落地预演。涵盖三大类：校园与空间导视、办公与学术周边、新媒体端界面。

## 选择指引（researcher 参考）

Mockup 适合需要展示品牌落地效果的场景：机构形象展示、办公物料、新媒体阵地。Researcher 根据 brief 的受众和使用场景，从以下三类中选择相关子类型。

### A. 校园与空间导视合成图

| 子类型 | 形态 | 说明 |
|---|---|---|
| 学院大门铭牌 | gen_image PNG | 建筑外立面铭牌效果，石材/金属质感，日间户外光 |
| 实验室门牌 | gen_image PNG | 室内门侧挂牌，亚克力/金属材质，室内走廊光 |
| 校园指示牌 | gen_image PNG | 户外立式导视牌，含方向箭头和建筑名称，校园环境 |

### B. 办公与学术周边合成图

| 子类型 | 形态 | 说明 |
|---|---|---|
| 研究员工作牌（ID Card） | gen_image PNG | 横版卡面，含照片位、姓名、机构 logo，挂绳可见 |
| 名片 | gen_image PNG | 标准名片比例，品牌色+logo+信息，桌面平铺俯拍 |
| 信纸 | gen_image PNG | A4 信纸效果，页眉 logo + 页脚信息，桌面或手持 |
| 录取通知书套件 | gen_image PNG | 信封+内页展开，含 logo 和装饰元素，仪式感光照 |
| 实验服（白大褂）胸前 Logo 刺绣 | gen_image PNG | 白色实验服左胸位置刺绣 logo，近距离细节展示 |
| 学院定制帆布袋 | gen_image PNG | 帆布袋正面印有 logo/图案，柔和棚拍或街拍场景 |

### C. 新媒体端界面合成图

| 子类型 | 形态 | 说明 |
|---|---|---|
| 微信公众号首图排版 | HTML + 渲染 PNG | 900×500 公众号封面，标题+品牌视觉+二维码区 |
| 官网首页 UI 视觉概念图 | HTML + 渲染 PNG | 1440×全高，含导航、hero、内容分区、footer |

Researcher 在 deliverables 中为每个 mockup 条目指定子类型和尺寸。多个 mockup 通常适合用 sub-items 语法归入一个主条目。

## 执行要点（designer 参考）

### 路由判断

| 子类型 | 工具链 |
|---|---|
| 大门铭牌、门牌、指示牌、工作牌、名片、信纸、通知书套件、实验服、帆布袋 | gen_image |
| 公众号首图、官网首页 | HTML + html_screenshot |

### 校园与空间导视合成图 · Prompt 要点

- **材质描述优先**：写 `brushed stainless steel nameplate mounted on red brick wall, daylight` 而非 `signage`
- **环境背景**：给出安装位置和场景光——户外自然光、室内走廊荧光灯、校园绿地背景
- **文字处理**：中文机构名称写 `containing the Chinese characters "<机构名>"`，不依赖模型自行生成
- **构图**：正面或轻微透视角度，铭牌/门牌/指示牌占画面 60-70%

示例结构（大门铭牌）：`A brushed stainless steel institutional nameplate mounted on a stone pillar at a campus entrance. The nameplate contains "学院名称" engraved in gold serif characters. Natural daylight from upper left, shallow DOF focusing on the lettering. Clean campus background slightly blurred.`

### 办公与学术周边 · Prompt 要点

- **工作牌 / 名片**：俯拍或 45 度角，桌面或手持，柔和棚拍光。描述卡面布局（logo 位置、信息区块）
- **信纸**：A4 比例，可纯白纸面或带淡色页眉页脚，桌面平铺，一角可微卷增加真实感。用品牌色点缀页眉线和 logo
- **录取通知书套件**：信封正面 + 内页展开，仪式感——蜡封、缎带、烫金文字等装饰元素可选。暖光，轻微阴影增加厚度感
- **实验服**：白色实验服左胸位置，logo 以刺绣质感呈现（thread texture on fabric），近距离特写，浅景深突出刺绣细节
- **帆布袋**：正面视角为主，帆布材质纹理可见，品牌设计印刷在袋面，柔和棚拍光，背景简洁

### 新媒体端界面 · Prompt / HTML 要点

- **公众号首图**：
  - 尺寸：900×500
  - HTML 自包含，所有样式内嵌
  - 视觉分层：品牌主视觉（左 2/3）+ 标题区（右 1/3），或中心构图
  - 二维码区置于右下角，留 20px 安全边距
  - 字族沿用 brand-spec `## 字体`

- **官网首页 UI 视觉概念图**：
  - 尺寸：1440×2400（默认）
  - 不要求可交互——这是视觉概念图，呈现整体设计和信息架构
  - 包含：顶部导航、hero 区、2-3 个内容分区、footer
  - 导航项和文案使用 placeholder 真实感文字（如"人才培养""科研平台""招生信息"），不用 lorem ipsum
  - 配图用 gen_image 出到 scratch/，HTML 相对路径引用

### UI 类调用

```bash
uv run python tools/html_screenshot.py \
  --html <html> --output <png> --width <W> --height <H>
```

### gen_image 类调用

```bash
uv run python tools/gen_image.py \
  --prompt "<英文 prompt>" \
  --output outputs/<RUN_ID>/artifacts/<slug>/v1.png \
  --aspect-ratio <deliverables 规格中的比例>
```

### 通用反 slop

- 场景合成图：不要悬浮物体（产品悬浮在无接触面的渐变背景上）、不要过饱和 HDR 滤镜
- 导视类：不要假国际范装饰线条、不要写实到看不清文字
- UI 类：不要圆角卡片 + 左侧 4px 彩色 accent border 作为唯一设计语言、不要 emoji icon 填充每个卡片、不要 placeholder.com 灰图占位
- 通用：不要"赋能 / 一站式 / 全链路"出现在任何 mockup 中
