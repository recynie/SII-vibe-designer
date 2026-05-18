#!/usr/bin/env python3
"""
测试 SII API (https://apicz.boyuerichdata.com) 的 LLM 能力：
1. 响应速度（多模型文本对话对比）
2. 图片理解能力（用已有的产出图片测试多模态）

凭据从 api.toml role `llm_capabilities` 读取。
"""
import json, time, base64, sys, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vibe-design" / "tools"))
import api_config

_provider = api_config.active_llm()
API_KEY = _provider.key
BASE_URL = _provider.base_url
log = lambda msg: print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def api_request(body, timeout=60):
    """调用 SII chat/completions，返回 (status, resp_dict, elapsed_seconds)"""
    url = f"{BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = time.time() - start
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw), elapsed
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        raw = e.read().decode("utf-8", errors="replace")
        try: return e.code, json.loads(raw), elapsed
        except json.JSONDecodeError: return e.code, {"error": raw}, elapsed
    except Exception as e:
        elapsed = time.time() - start
        return 0, {"error": str(e)}, elapsed


# =====================================================================
# 测试 1：响应速度 — 多个模型文本对话
# =====================================================================
print("\n" + "=" * 65)
print("  🏎️  测试 1：响应速度（纯文本）")
print("=" * 65)

speed_models = [
    ("gpt-4.1",       "GPT-4.1"),
    ("gpt-4.1-nano",  "GPT-4.1-nano"),
    ("gpt-4o-mini",   "GPT-4o-mini"),
    ("gpt-5.5",       "GPT-5.5（最新旗舰）"),
    ("gpt-5.4",       "GPT-5.4"),
    ("gpt-5.2",       "GPT-5.2"),
    ("gpt-5.1",       "GPT-5.1"),
    ("gpt-5",         "GPT-5（思考模型）"),
]

speed_results = []
for model_id, label in speed_models:
    body = {
        "model": model_id,
        "messages": [{"role": "user", "content": "请用一句话简要说明什么是设计系统（design system）。"}],
        "max_tokens": 200,
        "temperature": 0.3,
    }
    log(f"  {label} ({model_id}) ...")
    status, resp, elapsed = api_request(body, timeout=30)

    if status == 200:
        choice = resp.get("choices", [{}])[0].get("message", {})
        content = choice.get("content", "")
        finish = choice.get("finish_reason", "")
        speed_results.append((model_id, label, elapsed, True, content[:60], finish))
        log(f"    ✅ {elapsed:.2f}s | finish={finish} | {content[:50]}...")
    else:
        err = resp.get("error", {}).get("message", str(resp)[:100])
        speed_results.append((model_id, label, elapsed, False, str(err)[:60], "-"))
        log(f"    ❌ {elapsed:.2f}s | {err[:80]}")


# =====================================================================
# 测试 2：图片理解能力
# =====================================================================
print("\n" + "=" * 65)
print("  👁️  测试 2：图片理解（多模态）")
print("=" * 65)

# 找最近产出的一张图片
OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "vibe-design" / "outputs"
RECENT_RUNS = sorted(OUTPUTS_DIR.glob("run-2026*"), reverse=True)
TEST_IMAGE = None
for run_dir in RECENT_RUNS:
    pngs = list(run_dir.rglob("v1.png"))
    if pngs:
        TEST_IMAGE = str(pngs[0])
        break

if not TEST_IMAGE:
    all_pngs = list(OUTPUTS_DIR.rglob("*.png"))
    if all_pngs: TEST_IMAGE = str(all_pngs[0])

if not TEST_IMAGE:
    log("  ⏭️  无测试图片，跳过")
else:
    log(f"  📸 测试图片: {TEST_IMAGE}")
    img_size = Path(TEST_IMAGE).stat().st_size
    log(f"  📏 图片大小: {img_size/1024:.1f} KB")

    with open(TEST_IMAGE, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = Path(TEST_IMAGE).suffix.lower()
    mime = {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg","webp":"image/webp"}.get(ext, "image/png")
    log(f"  🎯 base64 长度: {len(img_b64)} chars")

    # 测试支持多模态的模型
    vision_models = [
        ("gpt-4.1", "GPT-4.1"),
        ("gpt-4o",  "GPT-4o"),
        ("gpt-5.5", "GPT-5.5"),
        ("gpt-5.4", "GPT-5.4"),
        ("gpt-5.2", "GPT-5.2"),
    ]

    vision_results = []

    for model_id, label in vision_models:
        body = {
            "model": model_id,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "请详细描述这张图片的内容，包括：\n1. 你看到了什么图形/图案/文字\n2. 主色调是什么\n3. 整体设计风格和调性\n4. 图片质量如何"},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
                ]
            }],
            "max_tokens": 500,
            "temperature": 0.3,
        }
        log(f"  {label} ({model_id}) 正在理解图片...")
        status, resp, elapsed = api_request(body, timeout=180)

        if status == 200:
            content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = resp.get("usage", {})
            pt = usage.get("prompt_tokens", "?")
            ct = usage.get("completion_tokens", "?")
            log(f"    ✅ {elapsed:.2f}s | 输入{pt}tok → 输出{ct}tok")

            # 判断是否真正理解了图片
            refusal_keywords = ["抱歉", "无法", "不能", "sorry", "cannot", "don't have", "not able",
                               "unable", "I don't", "I'm not", "i cannot", "i don't"]
            refused = any(kw in content.lower() for kw in refusal_keywords)
            if refused:
                log(f"    ⚠️  疑似未理解图片（含拒绝词）: {content[:150]}")
            else:
                log(f"    ✅ 成功理解图片")
                log(f"    描述摘要: {content[:200]}...")

            vision_results.append((model_id, label, elapsed, True, content, pt, ct))
        else:
            err = resp.get("error", {}).get("message", str(resp)[:200])
            log(f"    ❌ {elapsed:.2f}s | {err[:120]}")
            vision_results.append((model_id, label, elapsed, False, str(err), 0, 0))


# =====================================================================
# 测试 3：细节理解（logo 类 — 更考验视觉精度）
# =====================================================================
print("\n" + "=" * 65)
print("  🔍 测试 3：细节理解（logo/图形精确分析）")
print("=" * 65)

# 尝试找 logo 图片
LOGO_IMAGE = None
for run_dir in RECENT_RUNS:
    logo_dir = run_dir / "artifacts" / "logo"
    if logo_dir.exists():
        logos = list(logo_dir.glob("v1.png"))
        if logos:
            LOGO_IMAGE = str(logos[0])
            break

if LOGO_IMAGE:
    log(f"  📸 Logo 图片: {LOGO_IMAGE}")
    with open(LOGO_IMAGE, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
    log(f"  📏 大小: {Path(LOGO_IMAGE).stat().st_size/1024:.1f} KB | base64: {len(logo_b64)} chars")

    detail_prompt = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "这是品牌 Logo 设计图片。请精确回答：\n"
                        "1. 图片中包含具体的文字内容吗？写出你看到的每一个字。\n"
                        "2. 用到了哪几种颜色？请给出具体颜色名。\n"
                        "3. 图形/标志是什么形状？\n"
                        "4. 文字和图形在空间中的相对位置关系如何？\n"
                        "请尽可能具体，避免模糊描述。"
            },
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{logo_b64}"}},
        ]
    }

    for model_id in ["gpt-4.1", "gpt-5.5"]:
        body = {
            "model": model_id,
            "messages": [detail_prompt],
            "max_tokens": 800,
            "temperature": 0.2,
        }
        log(f"  {model_id} 细节分析...")
        status, resp, elapsed = api_request(body, timeout=180)

        if status == 200:
            content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = resp.get("usage", {})
            log(f"    ✅ {elapsed:.2f}s | 输入{usage.get('prompt_tokens','?')}tok → 输出{usage.get('completion_tokens','?')}tok")
            print(f"\n{'─'*50}")
            print(f"[{model_id} Logo 细节分析]")
            print(content)
            print(f"{'─'*50}\n")
        else:
            err = resp.get("error", {}).get("message", str(resp)[:200])
            log(f"    ❌ {elapsed:.2f}s | {err[:100]}")
else:
    log("  ⏭️  未找到 Logo 图片，跳过")


# =====================================================================
# 汇总报告
# =====================================================================
print("\n" + "=" * 65)
print("  📊 测试汇总")
print("=" * 65)

print(f"\n--- 响应速度 ---")
print(f"{'模型':<22} {'耗时':<8} {'状态'}")
print("-" * 45)
for _, label, elapsed, ok, extra, finish in speed_results:
    icon = "✅" if ok else "❌"
    print(f"{label:<22} {elapsed:<8.2f}s {icon}")

print(f"\n--- 图片理解 ---")
print(f"{'模型':<22} {'耗时':<8} {'状态':<6} {'Token 消耗'}")
print("-" * 55)
for r in vision_results:
    model_id, label, elapsed, ok, content, pt, ct = r
    icon = "✅" if ok else "❌"
    token_str = f"{pt}→{ct}" if pt else "-"
    print(f"{label:<22} {elapsed:<8.2f}s {icon:<6} {token_str}")

print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"中转站: {BASE_URL}")
print("=" * 65)
