# AGENTS.md

This file is the workspace map and operating guide for agents working in this repository. Read it before changing files so you understand which part of the system you are touching.

## Git

### Tags

Add a git tag for each major version of this system.

A major version means the system can pass the end-to-end pipeline. Minor output quality issues are acceptable, but the system must be available and able to produce `final.md`.

## Writing Agent Prompts And Skills

语言清晰、明确，减少意义不明的简写，用技术性的语言撰写 agent prompt 和 skills。
不要引入不必要的说明。
修改 agent prompt 前，思考：agent 需要了解这部分内容吗？

Prompt / skill changes should preserve the core contract:

- `researcher` writes facts/spec/deliverables; it does not design.
- `planner` schedules from `deliverables.md`; it does not add or remove deliverables.
- `designer` creates artifacts; it does not alter upstream facts/spec/deliverables.
- `critic` reviews written artifacts; it does not redesign or patch them.

## E2E Run

如果用户要求运行 e2e 或端到端测试，默认使用下面的任务：

> 请为创智学院做一套品牌形象设计。

Preferred command from repo root:

```bash
uv run e2e-test --brief "请为创智学院做一套品牌形象设计"
```

The runner loads `vibe-design/.env`, invokes `opencode run --command design`, prints progress heartbeats while opencode is quiet, and exits 0 only when a new run produces `final.md`.

## Overview

This repository contains **Vibe Design**, a multi-agent collaborative design system built on opencode harness. A user provides a short natural-language design brief. The system researches the subject, derives a brand specification, plans deliverables, creates visual artifacts, reviews them, iterates when needed, and writes a final delivery summary.

The core pipeline uses four opencode agents:

| Agent | Role |
|---|---|
| `planner` | Primary orchestrator. Initializes run directories, clarifies user intent, calls subagents, maps deliverables to artifact paths, handles retries/escalation, writes `final.md`. |
| `researcher` | Subagent for brief understanding and fact gathering. Writes `facts.md`, `brand-spec.md` with color references, `deliverables.md`, and downloads assets. |
| `designer` | Subagent for artifact production. Calls `gen_image.py` for image deliverables or writes HTML and screenshots it for UI/poster deliverables. |
| `critic` | Subagent for review. Runs machine checks, reads the actual artifact, lists structured issues with severity/evidence/fix direction, and writes `v?.review.md`; planner decides whether to revise. |

The project supports single deliverables and multi-sub-artifact deliverables. Example: one “brand merchandise design” deliverable can contain a logo, T-shirt mockup, tote bag mockup, and mug mockup under one parent artifact directory.

This is a course practicum project for an AI For Design assignment.

## Workspace Map

### Root

| Path | Description |
|---|---|
| `README.md` | Main project description. Explains design principles, architecture, data contracts, implementation, quick start, tests, demo runs, and known limits. |
| `AGENTS.md` | This workspace guide for agents. Update when the repository map or maintenance rules change. |
| `CLAUDE.md` | Thin pointer to `AGENTS.md` for Claude-style agents. |
| `CHANGELOG.md` | Iteration history and historical implementation notes. |
| `pyproject.toml` | Python project config. Declares Python 3.12+, `playwright`, `pillow`, and the `e2e-test` script entry point. |
| `.python-version` | Python version pin, currently 3.12. |
| `uv.lock` | uv lock file. It is currently gitignored by `.gitignore`; check worktree state before assuming it is tracked. |
| `.env.example` | opencode environment variable template. Copy to `.env` and `vibe-design/.env` as needed. Python scripts do not read `.env`. |
| `api.toml` | Local-only Python credential config, gitignored. It is the sole credential source for Python tools/scripts. |
| `api.toml.example` | Schema/template for `api.toml`, including `[active].llm`, `[active].image`, and provider tables. |
| `.gitignore` | Ignores local credentials, virtualenvs, runtime outputs, references, and caches. |

### `vibe-design/` — System Core

| Path | Description |
|---|---|
| `vibe-design/README.md` | Short local README for running the opencode project directly. Some details may lag the root README; prefer root README for system-level documentation. |
| `vibe-design/opencode.json` | opencode provider and default model config. Current default model and small_model are `findcg-openai/gpt-5.5`; SII, MiniMax, and FindCG Claude providers are also declared. |
| `vibe-design/.gitignore` | Ignores `outputs/`, local opencode cache, Python caches, and local virtualenv/node modules. |
| `vibe-design/.opencode/agent/planner.md` | Primary orchestrator prompt. Uses `ask-user`; no webfetch. |
| `vibe-design/.opencode/agent/researcher.md` | Research prompt. Uses webfetch and `design-guidelines`; writes `facts.md`, `brand-spec.md`, `deliverables.md`. |
| `vibe-design/.opencode/agent/designer.md` | Artifact production prompt. Uses `craft` and `design-guidelines`; routes deliverables to gen_image or HTML screenshot. |
| `vibe-design/.opencode/agent/critic.md` | Review prompt. Uses `craft`; runs `validate.py`, reads artifacts, writes structured issue lists to `v?.review.md`. |
| `vibe-design/.opencode/command/design.md` | `/design` entry command. Sends the brief to `planner`. |
| `vibe-design/.opencode/skills/ask-user/` | Skill for clarifying user design requirements. Ask about intent and scope, not searchable facts. |
| `vibe-design/.opencode/skills/craft/` | Design craft baseline, anti-slop checklist, and local OFL font assets under `fonts/`. |
| `vibe-design/.opencode/skills/design-guidelines/` | Visual direction and deliverable type references used by researcher/designer. |
| `vibe-design/examples/` | Example briefs: SII academy brand, SII admission landing page, Zhujiajiao tourism brand. |
| `vibe-design/outputs/` | Runtime output directory, gitignored. One subdirectory per run. |
| `vibe-design/docs/schema/` | Markdown schemas for `facts.md`, `brand-spec.md`, and `deliverables.md`. |
| `vibe-design/docs/skill-gap-analysis.md` | Notes on current skill coverage and gaps. |

### `vibe-design/tools/` — Python Tools

| Path | Description |
|---|---|
| `api_config.py` | Shared loader for repo-root `api.toml`. Used by Python tools and scripts. |
| `gen_image.py` | Image generation CLI. Routes to MiniMax or OpenAI-compatible backends, generates candidate images in parallel, detects actual returned format, writes `.prompt.txt` beside each candidate. |
| `html_screenshot.py` | Renders a local HTML file to PNG through system Chromium or Playwright. |
| `check_html_fonts.py` | Parses `brand-spec.md` allowed fonts and checks HTML `font-family` usage. |
| `validate.py` | Critic-facing review aggregator. Currently runs HTML font hard gate; PNG/MD are N/A for machine checks. |
| `verify_facts.py` | Cross-checks quantity claims in README/CHANGELOG-like docs against actual repo state. |
| `tools/tests/test_gen_image.py` | Unit tests for `gen_image.candidate_path`. |
| `tools/tests/test_tools.sh` | Older shell tests for validation tools; currently references removed palette scripts and needs updating before use. |
| `tools/tests/test_agent_prompts.sh` | Older prompt invariant test; currently references old skills/modes and needs updating before use. |
| `tools/tests/mocks/` | Mock compliant/violation HTML and brand specs for tool tests. |

### `scripts/` — Repository-Level Scripts

| Path | Description |
|---|---|
| `scripts/run_e2e.py` | End-to-end runner. Loads `vibe-design/.env`, runs `opencode run --command design`, streams through a PTY, scans `outputs/` for progress, and checks for `final.md`. Exposed as `uv run e2e-test`. |
| `scripts/test_opencode_skill_permissions.py` | Config-level skill permission matrix test. Calls `opencode --pure debug agent`; does not call LLM APIs. |
| `scripts/test_api.py` | API availability test for the active LLM provider from `api.toml [active].llm`. Calls real endpoints. |
| `scripts/test_llm_capabilities.py` | LLM speed, reasoning, and vision capability checks. Calls real endpoints. |
| `scripts/test_sii_vision.py` | SII/OpenAI-compatible model text and vision checks against existing output images. Calls real endpoints. |
| `scripts/test_sii_imagegen.py` | Image-generation latency check for SII/OpenAI-compatible endpoint. Calls real endpoints. |
| `scripts/test_sii_image_gen.py` | Related image-generation endpoint test variant. Calls real endpoints. |
| `scripts/__init__.py` | Package marker for script entry point packaging. |

### `docs/` — Documentation And Deliverables

| Path | Description |
|---|---|
| `docs/architecture.md` | Detailed system architecture and historical design decisions. Some model/history statements may need synchronization with root README after architecture changes. |
| `docs/technical-report.md` | Technical report for course/presentation use. Describes overall design, system architecture, implementation details, and experiment-result analysis. |
| `docs/release-notes.md` | Release notes for handoff/presentation context. |
| `docs/task/` | Original AI For Design assignment PDF and Markdown. |
| `docs/APIs/` | Summer-camp commercial API manual and API availability test report. |
| `docs/presentation/` | Three-page HTML presentation and exported PNG screenshots for defense. Entry: `index.html`. |
| `docs/demo-runs/` | Historical and final run artifacts. Current worktree has 3 run/evidence directories, including `run-final-hardened/`. |

Current `docs/demo-runs/` directories:

- `run-final-hardened/`
- `run-zhujiajiao-recovered/`
- `run-gpt-image-2-evidence/`

### `references/` — External Reference Corpus

`references/` is gitignored and contains cloned or copied external resources used for design-system, opencode, skills, presentation, and workflow research. Do not treat these as first-party implementation unless a task explicitly asks to mine references.

Important subtrees currently present:

| Path | Description |
|---|---|
| `references/open-design/` | Large design-agent reference corpus: skills, design systems, prompt templates, tools. |
| `references/open-codesign/` | Multi-model design-tool reference. |
| `references/Deep-Research-skills/` | Research workflow and structured skill references. |
| `references/awesome-claude-design/` | DESIGN.md brand/design-system examples. |
| `references/awesome-design-md/` | Additional brand design systems. |
| `references/awesome-design-skills/` | Curated design skills. |
| `references/awesome-claude-skills/` | General Claude skills list. |
| `references/anthropics-skills/` | Anthropic official skills reference. |
| `references/skywork-skills/` | Skywork skills, including design/search/PPT examples. |
| `references/logo-designer-skill/` | SVG logo design plugin reference. |
| `references/logo-generator-skill/` | Logo generator reference. |
| `references/claude-skills/` | General Claude skills, including UI/design review references. |
| `references/opencode/` | opencode framework source/reference docs. |
| `references/huashu-design/` | Huashu design references. |
| `references/flow-guarantees/` | Flow guarantee references. |
| `references/ppt-master/` | PPT generation reference. |

### `.agents/skills/` — Local Codex Skills

These are agent-assistance skills for this repository, not Vibe Design runtime skills. Use them only when the user request matches their description.

| Path | Description |
|---|---|
| `.agents/skills/zoom-out/` | Codebase map / higher-level perspective helper. |
| `.agents/skills/grill-me/` | Stress-test a plan through questioning. |
| `.agents/skills/grill-with-docs/` | Stress-test plans against project docs and update docs. |
| `.agents/skills/handoff/` | Create handoff documents. |
| `.agents/skills/prototype/` | Build throwaway prototypes. |
| `.agents/skills/research*/` | Structured research outline/deep/report helper skills. |
| `.agents/skills/to-prd/` | Convert context into a PRD. |
| `.agents/skills/write-a-skill/` | Create new agent skills. |

### `.ralph/` And `.worktrees/`

| Path | Description |
|---|---|
| `.ralph/` | Local planning/state notes for prior work. Treat as workspace metadata unless the user asks about it. |
| `.worktrees/` | Local git worktrees. Do not scan or edit by default; they can contain stale copies of repository files and will confuse fact gathering. |

## Development Environment

| Item | Current Value |
|---|---|
| Python | 3.12, pinned by `.python-version`; code uses Python 3.12-compatible stdlib features. |
| Package manager | `uv` |
| Virtualenv | `.venv/`, created by `uv sync`, gitignored |
| Dependencies | `pyproject.toml` currently declares `playwright>=1.59` and `pillow>=12.2.0` |
| Browser runtime | `uv run playwright install chromium` for HTML screenshot fallback |
| Common command | `uv sync` |
| E2E command | `uv run e2e-test --brief "请为创智学院做一套品牌形象设计"` |

## Credentials

| File | Consumer | Notes |
|---|---|---|
| `api.toml` | Python tools/scripts | Only credential source for Python. Select active LLM/image providers with `[active]`. |
| `.env` / `vibe-design/.env` | opencode | Supplies provider env vars referenced by `opencode.json`, such as `FINDCG_OPENAI_API_KEY`, `SII_API_KEY`, `MINIMAX_API_KEY`, `FINDCG_CLAUDE_API_KEY`. |

Do not hardcode credentials in scripts, prompts, README examples, or committed outputs.

## Maintenance Rules

Update `AGENTS.md` when any of the following happens:

- New files or directories are created.
- Existing files or directories are moved, copied, or deleted.
- A file or directory changes purpose.
- Agent responsibilities, skill permissions, schemas, or tool contracts change.
- README claims about counts, models, demo runs, tools, or examples become stale.

Update `README.md` when user-facing behavior, setup steps, architecture, model/provider defaults, or known limitations change.

After documentation changes, prefer running:

```bash
uv run python vibe-design/tools/verify_facts.py
```

If it fails because the checker is too narrow or stale, either update the checker or avoid unsupported count phrasing in docs.
