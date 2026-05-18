# Vibe Design v2 · Milestones

vibe-design 当前的固定四件套交付与"模板填空式 designer"问题，需要一次结构性重构。
本文件把重构拆成**最少必要的 milestone**，每条独立可验证、相对自洽。
原则：**规划简洁，能让实现专注**。每个 milestone 完成即可独立产生价值，不依赖未完成的下一步。

---

## 重构骨架（一句话）

> 把"决策权"从 prompt 纪律下沉到结构化文件 + 机器化校验。
> researcher 写 schema、planner 只调度、designer 在约束内自由设计、critic 先跑脚本再打分。

完成后的 4 角色 + 3 份 schema + 双模式：

| 角色 | 决策范围 | 不允许做的事 |
|---|---|---|
| researcher | facts.md / brand-spec.md / deliverables.md + assets/ 下载 | 不出视觉；不做 process 调度 |
| planner | 调度、循环、escalate、汇总 | 不增删 deliverables；不做 design 决策 |
| designer | 单件 artifact 构图/构思/工程；create vs reuse 双模式 | 不改 spec；不动 deliverables |
| critic | 机器化校验 + 主观评分 | 不重做、不补做 |

更详细的边界讨论散落在对话历史，本文件只承诺"完工标准"。

---

## M1 · Schema 定义 + 校验工具

**目标**：把三份结构化输出的格式钉死，并写出能自动判合规的脚本。这一层是后续所有 milestone 的契约层。

**交付物**：

- `docs/schema/facts.schema.md` — facts.md 字段、标签语法（`[source: ...]` / `[asset: ...]` / `[asset: failed - ...]`）
- `docs/schema/brand-spec.schema.md` — brand-spec.md 字段、`[from-fact: ...]` / `[inferred: ...]` 标签语法、严格度声明（`# 严格度: light | strict`）
- `docs/schema/deliverables.schema.md` — 四段式（显式 / 隐式 / 拒绝 / 决策依据），每条 `mode: create | reuse`
- `tools/validate_facts.py` — facts.md 每行带合法标签
- `tools/validate_brand_spec.py` — 每字段带标签；`[from-fact]` 引用必须在 facts.md 真存在；hex 与 facts 抓到的 hex 一致
- `tools/validate_deliverables.py` — 四段齐全、每条有 mode
- `tools/extract_artifact_palette.py` — 用 PIL/imagemagick 抽 artifact 主要 hex（前 8 名 + k-means）
- `tools/check_palette_compliance.py` — artifact hex 必须在 brand-spec 列出色板内（容差 ΔE < 5）
- `tools/check_html_fonts.py` — HTML 类 artifact `font-family` 声明只用 brand-spec 列出字族

**验证**：

- 手写两组 mock 文件（一组合规、一组各类违规），所有脚本对前者退出码 0、对后者退出码非 0 且打印具体违规行号
- 每个脚本独立可跑、不依赖 agent 调度

**范围内**：脚本本体 + schema 文档 + mock 测试样本
**范围外**：把脚本接进 critic 的评分流程（属于 M5）

**依赖**：无（这是基底）

---

## M2 · Researcher 重构

**目标**：合并原先 scout + researcher 职责，按"事实 → 规格 → 交付物"顺序产出三份结构化文件，资源落盘到 `assets/`。

**交付物**：

- `.opencode/agent/researcher.md` 重写：
  - 工作顺序锁死 facts → brand-spec → deliverables（先封章再下一份）
  - 资源优先规则：brand-spec 字段先扫 facts，命中取，未命中才推断；推断不得与 facts 冲突
  - `webfetch: allow`；其它 agent 在 frontmatter 改为 `webfetch: deny`
  - 资源下载到 `outputs/<RUN_ID>/assets/`，facts.md 标 `[asset: assets/<filename>]`
  - 严格度自适应：deliverables 行数 ≥ 4 → `strict`；< 4 → `light`，写在 spec 顶部
- `outputs/` 下产生的所有新 run，三份文件都能通过 M1 校验

**验证**：

- 跑现有 3 条 example brief（SII / 朱家角 / 钝角咖啡）+ 1 条新写的"招生页"单交付 brief
- 4 份输出全部通过 `validate_facts.py` / `validate_brand_spec.py` / `validate_deliverables.py`
- 至少 1 份 deliverables.md 出现 `mode: reuse`（已知品牌如 SII 的 logo）
- 至少 1 份 deliverables.md 的"拒绝项"非空

**范围内**：researcher prompt + 资源下载逻辑 + frontmatter 权限调整
**范围外**：planner / designer / critic 对新 schema 的消费（属 M3 / M4 / M5）

**依赖**：M1（schema 已定义）

---

## M3 · Planner 收窄到 process 层

**目标**：planner 不再做交付物决策，只读 deliverables.md 逐条调度。删除固定模板。

**交付物**：

- `.opencode/agent/planner.md` 重写：
  - 删除"logo / 海报 / 文案 / UI mockup"四件套表
  - 删除"至少 4 个子任务"硬性条款
  - 改为读 `deliverables.md`，按 mode 路由：`create` → designer 创作链；`reuse` → designer asset-prep 链
  - 不增不删交付物；要补的内容写到 `outputs/<RUN_ID>/escalate.md` 给用户决断
  - 保留循环控制（max 2 轮）+ 错误处理矩阵（429 / 1027 / gen_image fail）
- `outputs/<RUN_ID>/plan.md` 内容简化为"deliverables 行 → 子任务"映射记录，不再生成新内容

**验证**：

- 跑一条**单交付** brief（"为创智学院做招生宣传页"）→ planner 不强加 logo / poster / 整套品牌任务
- 跑一条**多交付** brief（"整套品牌形象设计"）→ planner 按 deliverables 列出的逐项调度，不自己加项
- planner 没有 webfetch 调用（grep 跑日志）

**范围内**：planner.md + plan.md 的简化模板
**范围外**：designer 的 reuse 模式实现（属 M4）；planner 自己跑校验脚本（不做，校验属 critic）

**依赖**：M2（deliverables.md 必须可读）

---

## M4 · Designer 双模式 + Skills 退化

**目标**：designer 在 brand-spec 约束内获得真实创作自由；skills 从 prompt 模板退化为介质工艺手册。

**交付物**：

- `.opencode/agent/designer.md` 重写：
  - 显式 create vs reuse 双分支
  - create 模式：现有的 gen_image / HTML / 写文案路径
  - reuse 模式：bash 走 imagemagick 处理 `assets/` 已有资源，禁调 gen_image
  - brand-spec 明确为"约束不是模板"：色板 / 字族 / 反 slop / 调性硬锁；流派参考 / 构图 / 字重 / 装饰自由
- `.opencode/skills/{logo,poster,copywriting,ui-mockup}.md` 退化：
  - 删除 prompt 填空模板和 HTML 骨架
  - 保留：介质常见手法、反 slop 红线、工程注意事项（gen_image prompt 工程结构、html_screenshot 调用细节）
- 新增 `.opencode/skills/asset-prep.md` — reuse 模式专用工艺手册（imagemagick 常用裁切/调色/嵌入操作）

**验证**：

- 跑含 reuse 项的 brief，designer 在该项**没调** gen_image，只调 imagemagick（grep 日志确认）
- 跑同主题两次，design 结果在色板 / 字族 / 调性维度一致，但流派 / 构图明显不同（说明自由度回归）
- skills 文件总字数 ≥ 旧版 70% 减少（反映退化为参考文档）

**范围内**：designer.md + 4 个旧 skill 退化 + 新增 asset-prep.md
**范围外**：critic 评分逻辑（属 M5）

**依赖**：M2（deliverables.md 提供 mode 字段）

---

## M5 · Critic 机器化 + 主观分离

**目标**：critic 先跑 M1 脚本判机器规则，再做主观审美判断；review.md 物理分离两类反馈。

**交付物**：

- `.opencode/agent/critic.md` 重写：
  - 评分流程：① 跑 `validate_*` 系列校验上游 schema → ② 跑 `check_palette_compliance.py` / `check_html_fonts.py` 校验本件 artifact → ③ 任一非 0 直接判不通过 → ④ 全过才进主观打分
  - 主观打分轴收窄：调性体现、视觉气质形容词体现、单件构图品质、信息层级（去掉机器化能验的"色板合规"等）
- `review.md` 模板新版：顶部"机器判定"段（跑了哪些脚本、结果），中部"主观打分"段，底部"改进建议"按机器/主观分类
- 通过门槛保持总分 ≥ 35 + 无单项 ≤ 4；机器判定不过直接归"不通过"，不进主观打分

**验证**：

- 故意构造一个 designer 违规产物（用 spec 外 hex 出图）→ critic 必须在机器判定段标违规、不靠"色彩偏暖"这种含糊话
- 故意构造合规但审美差的产物 → critic 机器段全过、主观段给低分
- review.md 文本里"机器判定"和"主观打分"两段物理分离，能 grep 出来

**范围内**：critic.md + review.md 模板
**范围外**：自动重试 / 升级逻辑（属 planner 已有职责）

**依赖**：M1（脚本可调）+ M4（designer 产出可被评）

---

## M6 · 系统层硬化（可选）

**目标**：把"哪个 agent 能写哪条路径"从 prompt 纪律升级为 opencode plugin hook 强制。

仅当先期调研结论是"opencode plugin API 能拿到 caller agent name + file path"时才做。否则保留 prompt + 路径约定为最终上限。

**交付物**：

- 调研报告：`docs/opencode-plugin-feasibility.md`（一页纸，结论 + 试验代码）
- 如可行：`.opencode/plugin/path-guard.{ts,js}` 实现 pre-write hook
  - researcher 才能写 `facts.md` / `brand-spec.md` / `deliverables.md` / `assets/*`
  - planner 才能写 `plan.md` / `escalate.md` / `final.md`
  - designer 才能写 `artifacts/*/v?.{png,html,md,prompt.txt}`
  - critic 才能写 `artifacts/*/v?.review.md`
- 配套测试：故意让 designer 试写 `brand-spec.md` → 应被 hook 拒绝

**验证**：

- 上述跨界测试都被拒
- 正常 run 不被误拦（跑 1 条 example brief 端到端通过）

**范围内**：plugin 调研 + hook 实现 + 测试样本
**范围外**：如调研结论不可行，本 milestone 直接关闭，不做妥协实现

**依赖**：M2 / M3 / M4 / M5 全部完成（路径约定稳定后再上锁）

---

## 执行原则

1. **顺序**：M1 → M2 → {M3, M4 并行可} → M5 → (M6 可选)。M3 和 M4 都消费 M2 输出、互不干扰，可并行
2. **每个 milestone 只做承诺的范围**：发现"顺手能改"的事写进对应 milestone 的"未来"段或新 milestone，不就地扩张
3. **每个 milestone 完工 = 验证段全过**：验证不写在 docstring 里，写成可跑的命令或 mock 文件
4. **不写 v3 之前的 v2.5**：发现需要的能力没规划，先停下评估是改 milestone 还是新增，不在现有 milestone 里塞
5. **每完成一个 milestone 更新 CHANGELOG.md**，但不需要更新本文件——MILESTONES.md 是计划，CHANGELOG 是结果

---

## 不在 v2 范围内的事

明确拒绝、避免规划膨胀：

- 多语言支持（v1 中文已稳，不展开）
- 设计版本管理 / diff 视图
- 并行调度（MiniMax-M2 实测必须串行）
- 用户交互式中途修改 brief（一次性 brief → 一次性交付）
- 跨 run 资产复用 / 缓存
- 自动 PPT / 报告生成（属答辩工作不属系统能力）
