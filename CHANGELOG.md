# Changelog

主要节点。详细演进见 `git log --oneline`。

> 历史快照：下方条目记录当时的状态，未回填后续变更。当前主 LLM 已从 `MiniMax-M2.7-highspeed` 切到 SII `gpt-5.5`（见 `vibe-design/opencode.json`）；MiniMax 相关条目反映的是切换前的实测。最新状态请看 README 头部。

## 当前增量

- deliverables 条目移除交付物模式字段，只保留 `<名称> | <规格>`
- researcher 在规格中直接引用需要使用的 `assets/<filename>`
- planner 不再按模式分支调度 designer
- designer 统一根据规格和本地 assets 选择 ImageMagick / gen_image / HTML / markdown
- 删除 `asset-prep` skill，素材转换说明内联到 designer prompt
- `tools/gen_image.py` 新增 OpenAI-compatible 图生图 / 编辑模式（`--input-image` / `--mask`）
- 视觉评审移除色板机器校验，颜色改为 critic 直接看图判断大体一致性

## 系统骨架

- 项目骨架 + opencode.json 配 MiniMax-M2 provider
- 4 个 agent（planner / researcher / designer / critic）+ 4 个 skill（logo / poster / copywriting / ui-mockup）
- `tools/gen_image.py` 双后端文生图（minimax / gpt-image-2，env 切换）
- `tools/html_screenshot.py` HTML → PNG（playwright/chromium）
- `/design` custom command
- 3 条 example brief：SII / 朱家角 / 钝角咖啡

## 架构纪律

- **opencode --pure 必须用**：跳过用户全局插件 `oh-my-opencode-slim` 注入的 "parallelize" workflow rules，否则 subagent 长时间挂起
- **subagent 严格串行调度**：MiniMax-M2 reasoning 在并行下偶发 5+ 分钟无产出
- **文件即上下文契约**：subagent 间不互相 @，全部信息流经 `brief.md` / `brand-spec.md` / `v?.review.md`
- **designer 类型路由**：copywriting 走 Write，logo/poster 走 bash + gen_image，避免决策犹豫
- **critic 用 ImageMagick 间接验证颜色**：MiniMax-M2 不支持视觉输入，用 `identify -format %[hex:u]` 提取实际色值与 brand-spec 比对

## 实测发现

- **MiniMax image-01 对深色 hex 复现不严格**：墨蓝 #0D1B2A 会被生成为浅蓝/米白。强约束 prompt（`STRICTLY use only #XXX` + 颜色名 + hex 双标）能让色彩从完全偏离逼近到接近目标
- **gpt-image-2 显著严格**：实测最深像素 #000A2E 与目标 #0D1B2A 距离仅 ~22；minimax 同 prompt 下 ~50
- **MiniMax-M2 内容审查偶发**（`output new_sensitive 1027`）：朱家角文旅 brief 触发；fallback 是 designer 切换纯英文 prompt + hex+色名（"sage green #4A7C59" 而非"竹青"）
- **critic 维度自适应是特性**：copy 任务自主换成「克制 / 动手气质 / 精准 / 记忆点 / 调性统一」等更贴切的轴；视觉任务保留标准 5 维。critic.md 已显式允许

## v2 重构

### M1 · Schema 定义 + 校验工具

- 三份 schema 文档落到 `vibe-design/docs/schema/`：facts / brand-spec / deliverables
  - facts 行级标签语法：`[source: ...]` / `[asset: assets/...]` / `[asset: failed - ...]`
  - brand-spec 字段标签：`[from-fact: ...]` / `[inferred: ...]`；顶部 `# 严格度: light|strict`
  - deliverables 四段式（显式/隐式/拒绝/决策依据），每条 `mode: create|reuse`
- 6 个独立可跑的工具脚本：
  - `tools/validate_facts.py` / `validate_brand_spec.py` / `validate_deliverables.py`
  - `tools/extract_artifact_palette.py`（PIL，top-N + 轻量 k-means，无 sklearn 依赖）
  - `tools/check_palette_compliance.py`（ΔE76 Lab 距离，threshold=5，主导色 + 散色双判）
  - `tools/check_html_fonts.py`（解析 `font-family:` 与 google fonts link，比对 spec `## 字体`）
- mock 测试样本：`tools/tests/mocks/{compliant,violation}/` 各一组（含 PNG 与 HTML）
- 一键测试：`bash tools/tests/run_m1_tests.sh`，11/11 通过；合规集全 0 退出，违规集全非 0 退出

### M2 · Researcher 重构

- 重写 `vibe-design/.opencode/agent/researcher.md`：facts → brand-spec → deliverables 顺序锁死
  - 资源优先规则：先扫 facts 命中（`[from-fact: ...]`），未命中才推断（`[inferred: ...]`）
  - 严格度自适应：deliverables 行数 ≥ 4 → strict，否则 light，写在 spec 顶部 `# 严格度: ...`
  - 资源下载到 `outputs/<RUN_ID>/assets/`，facts.md 标 `[asset: assets/...]` 或 `[asset: failed - ...]`
  - 自跑 M1 校验后才回报 planner
- frontmatter 权限调整：`webfetch: allow` 仅 researcher，planner/designer 改为 `deny`（critic 早已 deny）
- 新增 4 份 mock 输出（含 `mock-m2-sii-admission` light 模式样本），全部过 M1 校验
- 新增 `examples/brief-sii-admission.md`：单交付招生页 brief，验证 deliverables 不被强加四件套
- 一键回归：`bash tools/tests/run_m2_tests.sh`，15/15 通过（含 reuse mode / 拒绝段非空 / light 严格度三项 M2 专属断言）

### M3 · Planner 收窄到 process 层

- 重写 `vibe-design/.opencode/agent/planner.md`：删除"四件套"表与"≥4 个子任务"硬性条款
- 改为读 `deliverables.md` 按 `mode: create|reuse` 路由 designer
  - create → 走原有 gen_image / HTML / 文案路径
  - reuse → 走 imagemagick + assets/ 已有素材
- planner 不增删 deliverables；觉得需要补的内容写到 `outputs/<RUN_ID>/escalate.md` 让用户决断
- `plan.md` 变成"deliverables 行 → 子任务 + 目标路径"的极简映射，不再生成新内容
- 保留循环控制（max 2 轮）+ 错误处理矩阵（429 / 1027 / gen_image fail）+ subagent 严格串行纪律
- `bash tools/tests/run_m3_tests.sh` 13/13 通过（含 frontmatter webfetch 权限检查 + 旧模板清除核对）

### M4 · Designer 双模式 + Skills 退化

- 重写 `vibe-design/.opencode/agent/designer.md`：显式 `create` vs `reuse` 双分支
  - create：现有 gen_image / HTML / 写文案路径
  - reuse：bash + ImageMagick 处理 `assets/` 已有素材，禁调 gen_image，落 `v1.notes.md`
- brand-spec 重新表述为"约束不是模板"——色板/字族/调性/反 slop 硬锁，流派/构图/装饰自由
- 4 个旧 skill 退化为介质工艺手册：删 prompt 填空模板与 HTML 骨架，保留介质常见手法、反 slop 红线、工程注意事项
  - 总字节 12410 → 2945（−76.3%，超过 ≥70% 减少要求）
- 新增 `vibe-design/.opencode/skills/asset-prep.md`：reuse 模式 ImageMagick 食谱（SVG→PNG / 缩放 / 替主色 / 加底色 / 裁切）
- `bash tools/tests/run_m4_tests.sh` 15/15 通过（含 designer 分支 / skills 退化 / asset-prep / 系统 convert 烟囱测试）

### M5 · Critic 机器化 + 主观分离

- 重写 `vibe-design/.opencode/agent/critic.md`：评分流程顺序固定
  - ① 上游 schema 校验（validate_facts / validate_brand_spec / validate_deliverables）
  - ② 本件 artifact 机器校验（check_palette_compliance / check_html_fonts，按介质选）
  - ③ 机器全过才进主观打分
- 主观打分轴收窄为：调性体现 / 视觉气质 / 单件构图 / 信息层级 / 任务完成度——色板合规已被机器②覆盖，主观段不再扣分
- review.md 模板物理分离：`## 机器判定` → `## 主观打分` → `## 判定` → `## 改进建议`，改进建议按"机器层 / 主观层"分类
- 通过门槛：机器①②任一不过直接「不通过」；机器全过则总分 ≥ 35 且无单项 ≤ 4
- `bash tools/tests/run_m5_tests.sh` 9/9 通过：违规产物（#FF00AA）机器层失败、合规产物（#1A73E8）机器层通过；critic.md 三段结构与门槛断言齐

### M1–M5 全回归

`bash tools/tests/run_m{1..5}_tests.sh` 累计 63/63 全过。M6 暂未启动（标记为可选，依赖 plugin API 调研结论）。

### 端到端验证（2026-05-16/17）

- **创智学院招生页（单交付）**：`run-20260516-222745` ~7 min 端到端跑通；researcher → planner → designer create → critic v1 FAIL → designer v2 → critic v2 FAIL → escalate.md + final.md。M1-M5 全链路实证
- **朱家角品牌形象（多交付，题目原句）**：`run-20260517-072636` ~10 min 端到端跑通；2 件交付（logo-main reuse + hero-poster create），fast-skip 与 escalate-and-continue 双闭环验证
- 改动：
  - **researcher prompt 加硬上限**：`显式 + 隐式 ≤ 5`、`隐式 ≤ 2`、模糊 brief 优先 4 类核心、延展物料强制进拒绝段
  - **schema 与 validate_deliverables.py 同步加上限规则**：超限直接 FAIL，新增 `tools/tests/mocks/violation/deliverables-overflow.md` mock + M1 测试断言
  - **designer.md 工艺路由表重写**：按"产物形态"（纯 PNG / HTML 排版 / 纯文）而非介质名分类，researcher 在 deliverables 规格里点明形态对照路由
  - **planner.md 加 fast-skip 档**：critic 反馈是"压缩伪影 / anti-aliasing / 模型 prompt 约束力不足"等 designer 救不了的失败 → 直接 escalate-and-continue 跳过 v2，节省 LLM 来回
  - **planner.md 强化 escalate 三步纪律**：必须用 Write 工具落 escalate.md（不是聊天文本）、跳过该件继续调度剩余 deliverables、所有任务跑完仍要写 final.md。修复了上一轮 zhujiajiao run 因 escalate 写进 thinking 文本导致 session 提前退出
  - M3 测试加 3 条断言（13 → 16 项）保住这些修复
- 已知遗留（下一轮迭代素材）：
  - ~~researcher 在显式段写 `- （无——...）` 不合法 row 但 planner 没自跑校验、直接接力~~ ✅ 已修：planner.md 加"必须自跑三件 schema 校验"硬性条款 + M3 测试断言
  - ~~critic.md / researcher.md 脚本路径写的是 `vibe-design/tools/...`，cwd 已在 vibe-design 时会变 `vibe-design/vibe-design/...`~~ ✅ 已修：所有 prompt 中 `vibe-design/tools/...` 替换为 `tools/...`（cwd=vibe-design 假设统一）
  - AI 图像模型对色板 hex 的遵循度低（即使 prompt 写 ZERO tolerance + 列出 5 色仍 8 个散色）；fast-skip 已能正确识别，但本质需要上游降级——可考虑 designer 生成后跑 imagemagick `-fuzz` quantize 到 spec 5 色作为 post-processing；属下一轮工艺改进
- 全回归：M1-M5 累计 68/68（M1=12 / M2=15 / M3=17 / M4=15 / M5=9）

### M5 评分体系 v2 调整（2026-05-17）

回应 e2e 实测：AI 图像模型对色板 hex 的天然遵循度有限，机器层把色板当硬门槛会让每张图都被迫 escalate。重新分级：

- **色板检查降级为参考**：`check_palette_compliance` 仍然跑、仍然写到 review.md，但**不再阻断**主观打分、也不再单独触发"不通过"。需要扣分时由 critic 在主观「调性体现」维度引用色板观察作为依据，不再机械按 ΔE 数字判定
- **字族保留硬门槛**：`check_html_fonts` 必跑必过——HTML 类改一行 CSS 就修，没理由放过
- **schema 保留硬门槛**：上游三件套 validate_* 仍是硬门槛
- **5 维度评分尺度从 0-10 改为 0-5**：每分含义清晰锚定（5 优 / 4 良 / 3 合格 / 2 不足 / 1 差 / 0 未做）；通过门槛改为总分 ≥ 18/25 且无单项 ≤ 2
- **review.md 模板物理三段**：`## 机器判定`（schema + 字族）→ `## 色板参考`（不阻断）→ `## 主观打分`（5 × 0-5）
- planner.md fast-skip 段同步更新：色板偏离不再触发 fast-skip（因为色板本身已不会让 review 不通过）
- `tools/tests/run_m5_tests.sh` 9 → **21** 项断言：覆盖三段结构、色板非阻断、字族仍硬门槛、0-5 尺度无残留 0-10 引用
- 全回归累计 **68 → 80**（M1=12 / M2=15 / M3=17 / M4=15 / M5=21）

### 端到端验证（M5 v2 + 评分体系修订后，2026-05-17）

- **朱家角第 1 次（zjj5）端到端死锁**：`run-20260517-181050-zhujiajiao-EXTERNAL-DIR-PERMISSION-DEADLOCK/` ——designer 试图把中间产物写到 `/tmp/poster-main-v1-bg.png`，触发 opencode `external_directory: ask` 权限弹窗，非交互模式无人响应导致挂死。已识别并归档为反例
- **修复**：
  - `opencode.json` permission 加 `external_directory: deny`，让外部目录写入直接失败而非询问
  - `designer.md` 加"写盘路径硬约束"段：所有产物必须落到 `outputs/<RUN_ID>/artifacts/<slug>/`；中间产物用 `scratch/` 子目录而非 `/tmp`
  - `planner.md` final.md 模板修复 `/50 → /25`（旧评分尺度残留），M3 测试加 `no leftover ?/50` 断言
- **朱家角第 2 次（zjj6）端到端通跑**：`run-20260517-182725-上海朱家角品牌形象设计/` ~7 min 跑完
  - 2 件交付：Logo 主标志 24/25 通过 + 品牌文案 16/25 通过
  - **色板降级生效**：Logo 色板 FAIL 7 个散色（ΔE 7-23），critic 写"调性方向正确不阻断"，主观打分 24/25 通过——**首次实证降级后图像类交付能正常通过**
  - planner 收 researcher 回报后自跑 schema 校验、发现 brand-spec 3 处违规、自己 Edit 修到全 PASS 才进入 plan.md
  - final.md 落盘干净退出，无 escalate
  - 注：本轮 researcher 把"主视觉海报"和"落地页"挪到拒绝段（理由"超出 5 件上限"，但实际只列了 2 件 < 5）——是新规则的过度收敛，是值得调 prompt 的下一轮素材
- 全回归累计 **80 → 81**（M1=12 / M2=15 / M3=18 / M4=15 / M5=21）

## 7 个 demo runs

- `run-final-hardened/` — ★ 题目正式交付：创智学院强化版 12 min 4 类全套
- `run-20260516-004106-chuangzhi/` — 创智学院早期版本 14 min（critic 触发 v2 自主迭代实证）
- `run-coffee-partial/` — 钝角咖啡（不同领域，像素级 critic）
- `run-zhujiajiao-recovered/` — 朱家角（第 3 个领域，验证内容审查 fallback）
- `run-gpt-image-2-evidence/` — gpt-image-2 单图实证（直方图对比）
- `run-solenne-gpt-image-2/` — Solenne 香水（gpt-image-2 后端首次完整 pipeline）
- `run-foundry-copy/` — Foundry Lab 纯文案（critic 维度自适应实证）
