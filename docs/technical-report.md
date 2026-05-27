# Vibe Design 技术说明文档

## 1. 系统定位

Vibe Design 是一个基于 opencode harness 构建的多智能体协同设计系统。系统接收自然语言设计 brief，将其转换为结构化事实、品牌规范和交付物清单，再通过独立上下文的设计、评审与迭代 agent 生成最终设计交付结果。

系统目标不是替代专业设计软件，而是验证一条可执行、可复盘、可扩展的 AI For Design 工作流：

- 将模糊 brief 转换为可追踪的设计约束。
- 将设计任务拆分为可调度的交付物单元。
- 使用文件作为 agent 间上下文契约，降低隐式聊天记忆带来的漂移。
- 将生成、机器校验、视觉评审和迭代闭环分离。
- 在端到端命令行流程中产出 `final.md` 和可审阅的视觉 artifact。

当前系统面向品牌形象、主视觉、宣传海报、文创物料、官网或 H5 mockup 等平面与界面设计任务。

### 1.1 为什么设计为多 Agent 系统

课程实训要求使用多 agent 架构，但多 agent 并非仅为了满足形式上的"多"。我们的设计思路是：**多 agent 相比于单 agent 有什么结构优势？如何设计才能发挥这些优势？**

单 agent 在处理完整设计 pipeline 时存在三个结构性缺陷：

- **角色认知冲突**：同一上下文中同时承担设计者和评审者角色时，模型倾向于为自己的产出辩护，而非诚实评估。将设计者与评审者分离为不同 agent（designer 与 critic），各自拥有独立上下文，评审者无从"知道"设计者的生成意图，只能基于实物 artifact 进行判断——这从根本上切断了自我辩护的路径。
- **事实调研与创作决策耦合**：单 agent 容易将想象事实伪装为调研结果，或将设计偏好伪装为客观约束。将 researcher 独立出来，强制其所有事实标注来源（`[source: URL]`），并通过 webfetch 权限使其成为唯一能访问外部信息的 agent——这使得事实输入与设计输出的边界可以被机器校验。
- **Scope creep 缺乏外部制衡**：单 agent 倾向于不断扩展任务以覆盖更多可能性，而非收敛到最小可行交付。将设计范围决策交给 researcher（写 `deliverables.md`），将流程执行交给 planner（只调度不增删），scope 变更必须经过显式的文件修改才能生效。

核心设计原则是：**将认知冲突外化为 agent 角色边界，用文件协议取代上下文记忆，使每一步决策可追溯、可复盘。**

## 2. 整体设计

### 2.1 Harness 基础：opencode 提供的能力

opencode 是本课程指定的 agent harness。我们充分使用了其提供的以下能力：

- **subagent 独立上下文**：每个 agent（planner / researcher / designer / critic）拥有独立的 LLM 会话上下文，互不干扰。这是实现角色边界隔离的基础。
- **自定义 agent prompt**：通过 `.opencode/agent/<name>.md` 为每个 agent 编写领域特定的角色 prompt，定义其职责边界、工作流程和禁止事项。
- **权限控制系统**：全局和 agent 级权限配置（`opencode.json`），控制 webfetch、bash、skill 等能力的分配。这是实现"基于角色的能力最小化"的机制。
- **自定义命令**：`/design` 命令作为用户入口，将自然语言 brief 转发给 planner。
- **多 provider 支持**：通过 npm `@ai-sdk/*` package 接入 OpenAI-compatible 后端，允许在同一套 prompt 下切换模型。
- **文件读写与 bash 执行**：agent 可以读写文件、执行 shell 命令，这是实现"文件契约"和调用 Python 工具的基础。

opencode 提供了 agent runtime 的通用能力。我们的工作集中在**设计领域的任务建模和 agent 协作协议**上——即下面要展开的核心设计。

### 2.2 多 Agent 的角色分工

系统包含四个 agent，各自承担设计流程中的不同角色：

**Planner**——流程调度者

Planner 是唯一的主控 agent（primary mode）。用户通过 `/design <brief>` 将任务描述交给 planner，planner 拥有对完整任务的上下文理解和目标认知。它负责初始化运行目录、调用 researcher 获取设计依据、按 `deliverables.md` 调度 designer/critic 的并行或串行执行、处理版本迭代和 escalate 决策、最终汇总到 `final.md`。

为什么需要一个 planner，而不是让其他 agent 按固定顺序串行执行？两个原因：

- **固定顺序的 agent 流是脆弱的**：若 designer 遇到 API 429 限流或内容审查拒绝，固定流程无法自行处理。planner 拥有完整的错误处理知识（检测错误类型 → 选择重试/切换策略/escalate → 继续剩余任务），使 pipeline 在真实网络环境中保持鲁棒。
- **固定顺序要求用户了解系统内部细节**：用户只需描述"我要什么"，planner 负责将其翻译为 researcher 的调研任务、designer 的创作任务、critic 的评审任务，并自主决定并行/串行调度策略。

值得注意的是，我们没有使用 CLI 状态机来管理工作流。状态机虽确定性强，但很难处理意外情况——例如文件被误删导致状态机状态与真实文件系统不一致，或 API 返回非预期错误时状态机缺少灵活的重试/跳过逻辑。planner 作为 LLM agent，能够基于当前文件系统的真实状态做出决策，而非依赖预先编码的状态转移表。

**Researcher**——事实调研者

Researcher 拥有 webfetch 权限，是唯一能访问外部信息的 agent。它将用户的模糊 brief 转换为三份结构化文件：`facts.md`（来源标注的事实）、`brand-spec.md`（色彩/字体/调性规范）、`deliverables.md`（显式/隐式/拒绝交付物清单）。Researcher 不做设计创作，只做信息收集和结构化。

**Designer**——设计执行者

Designer 根据 `deliverables.md` 中的交付物规格，选择合适的工具链生成视觉产物：图像类产物调用 `gen_image.py` 进行文生图，UI/排版类产物编写 HTML 并通过 `html_screenshot.py` 渲染为 PNG。Designer 拥有 `craft` 和 `design-guidelines` skill，但不允许 webfetch——所有设计参考必须来自 researcher 产出的上游文件。生成后需要进行视觉自检，读取实际图像检查裁切、乱码、调性偏离等硬伤。

**Critic**——设计评审者

Critic 执行机器校验（通过 `validate.py` 检查 HTML 字族合规等硬门槛），然后读取实物 artifact 文件进行视觉评审。Critic 不给分、不判通过——只输出结构化的严重度、证据和修改方向。这一定位确保 planner 是唯一决策者，而非橡皮图章。Critic 不允许 webfetch，也不允许修改设计文件。

### 2.3 权限分配：基于角色的能力最小化

每个 agent 的权限配置服务于其角色定位，遵循"只给完成任务所需的最小能力"原则：

| Agent | webfetch | 允许的 skill | 设计意图 |
|---|---|---|---|
| planner | deny | `ask-user` | 不搜索事实（交给 researcher），但需要向用户澄清需求意图 |
| researcher | allow | `design-guidelines` | 唯一能访问外部信息的 agent，防止其他 agent 编造"事实" |
| designer | deny | `craft`、`design-guidelines` | 设计执行不需要外部搜索，所有参考来自上游文件 |
| critic | deny | `craft` | 评审只基于实物 artifact 和上游 spec，不引入外部标准 |

全局配置额外设置 `external_directory: deny`——这是来自实测的教训：非交互端到端运行中，agent 若尝试写入 `/tmp` 等外部路径会触发 opencode 权限确认弹窗，无人响应时挂起整个 run。

### 2.4 Agent 间的信息交流：文件作为上下文契约

多 agent 系统的核心设计问题之一是 agent 间如何交换信息。常见的方案包括共享向量数据库、基于聊天历史的 chain-of-thought 传递、或自定义 RPC 通信协议。我们的选择是**文件**——使用 Markdown 文件作为 agent 间的唯一上下文契约。

这一选择的优势是结构性而非偶然的：

- **通用于所有 LLM**：无论模型是否支持 function calling、是否支持结构化输出，文件读写是所有 LLM 通过 bash 或 edit 工具都能执行的最基础操作。不依赖任何特定的通信协议或中间件。
- **便于人类审阅和定位问题**：每次 run 落盘为完整目录树。当输出不符合预期时，人类可以打开 `facts.md` 检查 researcher 是否编造了事实，打开 `brand-spec.md` 检查色彩推断是否合理，打开 `v1.review.md` 查看 critic 发现了什么问题——问题定位路径清晰。
- **便于版本管理**：每个 run 的所有中间文件（facts、brand-spec、deliverables、plan、review、final、artifact）都在同一个 `outputs/<run-id>/` 目录下，天然支持 git diff 和版本对比。尽管项目当前未实现自动化版本管理，但文件结构为此提供了基础。
- **便于控制权限**：文件系统自带读写权限，与 opencode 的权限系统配合，可以精确控制哪个 agent 能写哪些文件。

各文件在 agent 间的流向：

| 文件 | 写入者 | 消费者 | 作用 |
|---|---|---|---|
| `facts.md` | researcher | planner / designer / critic | 保存 brief 信号、公开事实、来源标注和本地素材记录 |
| `brand-spec.md` | researcher | designer / critic | 保存色彩参考、字体、调性、视觉气质和反 slop 禁区 |
| `deliverables.md` | researcher | planner / designer / critic | 定义本次 run 的显式、隐式、拒绝交付物，驱动 planner 调度 |
| `plan.md` | planner | planner / 用户 | 将 `deliverables.md` 条目映射到 artifact 路径 |
| `v?.prompt.txt` | designer / 工具 | critic / 用户 | 保存图像生成 prompt，供评审时回溯 |
| `v?.review.md` | critic | planner / designer / 用户 | 机器判定 + 实物观察 + 结构化问题列表 |
| `final.md` | planner | 用户 | 汇总最终交付物、状态和运行元信息 |

为保证 agent 间信息传递的可靠性，上游文件的格式有严格要求。例如 `facts.md` 中每条事实必须标注 `[source: URL]` 或 `[asset: assets/...]`，`brand-spec.md` 中每个字段必须标注 `[from-fact: ...]` 或 `[inferred: ...]`。这些格式要求通过独立的 CLI 校验工具（如 `validate.py`）进行自动化检查，格式不符的文件不能进入下一阶段——这保证了任意一个 agent 的输入输出在格式层面是确定的。

### 2.5 交付物驱动的 Scope 控制

Researcher 产出的 `deliverables.md` 采用四段式结构（显式 / 隐式 / 拒绝 / 决策依据），是整个 pipeline 的调度依据。Planner 严格按照 `deliverables.md` 中的条目调度 designer 和 critic，不新增、不删除。有疑虑时，planner 将问题写入 `escalate.md`，请求外部决策而非自行修改交付范围。

这一设计将 scope 决策（"做什么"）和流程执行（"怎么做"）解耦。Researcher（拥有事实调研能力）负责 scope 决策，Planner（拥有调度和容错能力）负责流程执行。两者的耦合会导致 planner"觉得应该多做点什么"而扩展交付范围——这本质上是 LLM 对 generate-then-evaluate 循环中产生的新上下文的本能回应。

`deliverables.md` 支持两个层级的抽象：

- **单产物交付物**：一个独立的视觉产物（如 logo 或一条品牌文案）。
- **多子产物交付物**：一个主交付物包含多个子产物（如"科技招生系列文创套装"包含帆布袋、T 恤、贴纸等 6 个子产物）。所有子产物由同一个 designer 上下文顺序处理，保持视觉一致性。

## 3. 工具层设计

### 3.1 为什么使用 CLI 而非 opencode Tool Call

opencode 支持通过 LLM tool call 机制为 agent 提供工具。但本项目选择了 CLI（命令行界面）作为工具接口。这一决策基于以下对比：

| 维度 | CLI 工具 | opencode Tool Call |
|---|---|---|
| 调试体验 | 独立于 opencode 运行，可单独测试和调试 | 必须与 opencode 联合调试，定位问题困难 |
| 中间结果可见性 | stdout/stderr 直接输出，agent 能读取完整日志 | 只能获取最终返回值，中间过程不可见 |
| LLM 兼容性 | 任何 LLM 都理解命令行输入输出 | 依赖模型对 tool call schema 的理解能力 |
| 错误传播 | 退出码 + 明确的 stderr 信息，agent 可据此决策 | 错误序列化在 tool response 中，格式因框架而异 |

CLI 工具对 LLM 来说是一种天然友好的接口：模型在训练数据中已经见过大量命令行使用场景，理解退出码、stdout、stderr、文件路径等概念。相比之下，tool call 虽然自带 schema 校验等优势，但引入了与具体 harness 耦合的复杂度和调试成本。

### 3.2 核心工具

**`gen_image.py`——图像生成**

统一的文生图 CLI，屏蔽了 MiniMax `image-01` 和 OpenAI `gpt-image-2` 两个后端的差异。支持候选图机制（`--candidates N`），通过 Python `ThreadPoolExecutor` 并行发起 N 次独立 API 调用，让 designer 在同一轮中横向择优，减少迭代轮次。自动检测后端返回的实际图像格式（PNG / JPEG / WebP），并写入 `.prompt.txt` 记录生成用的 prompt 供评审回溯。

```bash
uv run python tools/gen_image.py \
  --prompt "minimal logo for a tech institute, geometric, two-tone" \
  --output outputs/<RUN_ID>/artifacts/logo/v1.png \
  --aspect-ratio 1:1 \
  --candidates 3
```

**`html_screenshot.py`——HTML 转 PNG**

将 designer 编写的 HTML 文件渲染为 PNG 截图。使 agent 能"看"到 HTML 排版的实际效果——很多排版问题（底部表单截断、文字遮挡、信息层级混乱）只有渲染成图像后才能真正被发现。优先使用系统 Chromium headless 模式，无系统浏览器时回退至 Playwright Chromium。

```bash
uv run python tools/html_screenshot.py \
  --html outputs/<RUN_ID>/artifacts/poster/v1.html \
  --output outputs/<RUN_ID>/artifacts/poster/v1.png \
  --width 1200 --height 1600
```

**`validate.py`——聚合校验**

Critic 的一键入口，根据 artifact 扩展名自动路由：`.html` → 运行 `check_html_fonts.py` 字族硬门槛；`.png` / `.md` → 标注 N/A（无机器硬门槛，由 critic 视觉/文本评审）。退出码 0 = 全过，1 = 硬门槛失败，2 = 文件路径错。

```bash
uv run python tools/validate.py review outputs/<RUN_DIR> --artifact artifacts/<slug>/v1.html
```

**`check_html_fonts.py`——HTML 字族合规检查**

解析 HTML 中的 `font-family` 声明和 Google Fonts 引用，与 `brand-spec.md` 的「字体」段进行白名单比对。通用回退字族（`serif`、`sans-serif` 等）自动放行。这是系统唯一的自动硬门槛——因为判定可靠（正则解析 + 白名单比对不会误判），且修复成本极低（改一行 CSS）。

### 3.3 生成产物的双重类型

系统支持两种视觉产物类型，互为补充：

- **图像类**（logo、KV、文创 mockup、效果图）：通过 `gen_image.py` 生成。利用 AI 图像模型在纹理、光影、构图上的多样性，适合需要视觉氛围和品牌感的产物。
- **HTML 排版类**（落地页、H5、网页 mockup、品牌规范页）：通过 designer 编写 HTML → `html_screenshot.py` 渲染为 PNG。利用 HTML/CSS 的确定性布局能力，适合需要精确控制文字定位、信息层级和版式的产物。

HTML 类产物的关键价值在于：渲染后的 PNG 使 agent 能够"看到"最终的视觉结果。critic 读取渲染截图后，可以识别文字遮挡、表单截断、间距失衡等只有看图才能发现的问题，并将反馈写入 review.md——designer 据此修改 HTML 并重新渲染，形成迭代闭环。

## 4. 实验结果

### 4.1 大规模文创设计：12 类产品 × 多轮迭代

最具代表性的实验是 `run-sii-merch`（上海创智学院文创产品设计）。该任务要求为创智学院设计两组不同风格的文创产品，每组覆盖 6 个产品类别（帆布袋、T 恤、贴纸、徽章、笔记本、水杯），共 12 个设计方向。每个子产物需同时输出照片风格 mockup 效果图和可印刷的平面设计稿。

系统将两个风格系列分别建模为多子产物交付物，每个系列由一个 designer 在独立上下文中顺序生成 6 个子产物。同时还有两条独立的单产物交付物（系列口号文案和印刷应用规范页）并行执行。

该实验最终产出了 101 个文件，包括 50 张 PNG 图像、36 份 prompt 记录、5 份 review 文件、2 份 HTML。整个设计过程持续约 2 小时，其间：

- 12 个子产物的图像生成涉及大量的 `gen_image.py` API 调用，系统通过候选图机制（每个产物 3 个候选）进行横向择优。
- 印刷应用规范页经历了完整的迭代闭环：v1 被 critic 通过 `validate.py` 检测出字族不合规（HTML 中使用了 `source han sans cn` 而非 spec 规定的 `sourcehansanscn-regular`），触发 BLOCKER。Planner 调度 designer 修复 CSS 后生成 v2，v2 字族检查通过，critic 评审通过。
- 在整个 ~2 小时运行周期中，系统遇到网络问题时 planner 能够自主重试，无需人工干预即可完成全部设计计划。

这个实验验证了三个核心能力：
- **多子产物模型的有效性**：12 个产品在两个 designer 上下文中保持了各系列内部的视觉一致性。
- **迭代闭环的完整运行**：从 machine check 失败 → BLOCKER → designer 修复 → 再评审通过的流程自动化运行。
- **长时间运行的鲁棒性**：系统在 ~2 小时的持续运行中自主处理了网络波动。

### 4.2 核心实证发现

从多个实验的累积数据中，有三个重要发现直接影响了系统设计：

**图像模型不适合像素级色板硬约束。** 我们在 M5 阶段曾将 `check_palette_compliance.py`（ΔE76 Lab 距离计算）作为硬阻断条件。实测发现同一 prompt 在不同后端下的色彩偏差显著：MiniMax `image-01` 最深像素 ΔE 约 50，gpt-image-2 约 22。两个后端均无法稳定复现目标 hex。将色彩作为硬阻断会导致每个图像交付物都被迫 escalate。当前方案是：色彩检查降级为视觉参考，由 critic 判断整体色调是否与 brand-spec 同方向（冷暖、明度、饱和度），只有明显改变品牌调性时才列为问题。

**`external_directory: deny` 是端到端运行的基石。** 朱家角实验中，designer 尝试将中间文件写入 `/tmp/`，触发 opencode 权限弹窗，非交互 runner 无人响应导致挂起。将全局 `external_directory` 设为 `deny` 后，外部路径写入直接失败，配合 designer prompt 中"所有产物必须落到 `outputs/<RUN_ID>/` 下"的约束，消除了这类死锁。

**Critic 读图能力改变了评审质量。** 早期 critic 只能通过 ImageMagick 间接提取色值，无法判断构图、层级、裁切等视觉维度。引入视觉读取后，critic 能识别只有看图才能发现的问题——如落地页底部表单截断、文字遮挡、信息层级混乱——并将这些写成可执行的修改反馈。

## 5. 讨论

### 5.1 设计决策回顾

回顾整个系统的技术路线，有几个关键决策值得展开：

**Planner 作为 LLM agent 管理流程 vs 状态机。** 状态机在确定性环境中是可靠的，但 AI pipeline 的运行环境是不确定的——API 可能返回 429/1027/超时，文件可能被误操作，subagent 可能无产出。Planner 作为 LLM agent 能够理解错误的语义并做出上下文相关的决策：429 → 等 30s 重试；1027 内容审查 → 切换纯英文 prompt 重试；subagent 无产出 → 告知用户而非死等。这种灵活性是状态机难以实现的。

**Agent 的职责边界通过 prompt 而非代码约束。** 系统的核心约束——researcher 不设计、designer 不改上游、critic 不打分、planner 不增删交付物——全部通过 agent prompt 中的"明确不做"段和"禁止事项"段定义。这不是最优方案——代码级约束更可靠——但在当前 harness 能力下，prompt 约束配合文件协议和权限控制已经形成了一个可工作的三角约束体系。

**多维度的质量保障体系。** 系统从三个层面保障输出质量：格式层面（CLI 工具进行 schema 校验和字族检查）、视觉层面（critic 读图评审，designer 视觉自检）、流程层面（最多 3 版迭代、BLOCKER 必须修复或 escalate、escalate 需要落盘）。这三个层面相互独立，任何单一层面失效都不会导致整个质量保障崩溃。

### 5.2 已知限制

- `gen_image.py --input-image`（图生图）和局部编辑能力在 prompt 中已有约定，但当前主要验证路径仍是文生图，图生图需要进一步校准。
- PNG 类 artifact 缺少可靠的自动硬门槛，只能依赖 designer 自检和 critic 视觉评审。
- 部分历史测试脚本包含早期 skill 和评分尺度断言，需要按当前实现清理。
- `docs/architecture.md` 保留了部分历史架构描述，需要与当前 prompt 实现同步。

### 5.3 后续优化方向

- **视觉质量自动化**：为 HTML 截图增加自动视觉检查——截图尺寸验证、主体裁切检测、空白区域异常检测。这是 critic 目前只能通过人工视觉完成的检查项，自动化后可实现 BLOCKER 级别的硬门槛。
- **失败模式结构化**：将 critic review 中的常见失败类型（字族不合规、构图偏离、色彩方向错误、文字不可读等）归类并统计，形成可量化的质量问题分布，用于评估不同模型和 prompt 版本的输出质量趋势。
- **图生图能力完善**：为基于已有 logo 的应用延展（如将 logo 应用到 T 恤、帆布袋等载体）建立可重复的测试，验证 `--input-image` 路径的稳定性。
- **横向对比能力**：将 demo run 的元信息标准化（模型、brief 类型、运行时长、迭代次数、BLOCKER 次数），便于定量对比不同模型、不同工具链和不同 prompt 策略的效果。
