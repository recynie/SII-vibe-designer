#!/usr/bin/env python3
"""
测试 SII API 的 LLM 能力：
1. 文本响应速度（TTFT + 总耗时）
2. 推理/创意能力（简单推理题）
3. 图片理解能力（用项目产出图片测试多模态）

凭据从 api.toml role `llm_capabilities` 读取，禁止硬编码。
"""
import json
import sys
import time
import base64
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vibe-design" / "tools"))
import api_config

_provider = api_config.active_llm()
API_KEY = _provider.key
BASE_URL = _provider.base_url
TIMEOUT = 120

# 用于视觉测试的项目产出图片
REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_IMAGE = REPO_ROOT / "docs/demo-runs/run-final-hardened/artifacts/poster/v1.png"
TEST_IMAGE_LOGO = REPO_ROOT / "docs/demo-runs/run-final-hardened/artifacts/logo/v1-mark.png"


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def encode_image_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def api_chat(model: str, messages: list, timeout: int = TIMEOUT) -> tuple:
    """
    调用 chat/completions，返回 (status, response_dict, elapsed_seconds)
    """
    url = f"{BASE_URL}/chat/completions"
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.3,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            elapsed = time.time() - start
            try:
                return resp.status, json.loads(raw), elapsed
            except json.JSONDecodeError:
                return resp.status, {"raw": raw}, elapsed
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw), elapsed
        except json.JSONDecodeError:
            return e.code, {"raw": raw}, elapsed
    except Exception as e:
        elapsed = time.time() - start
        return 0, {"error": str(e)}, elapsed


def extract_content(resp: dict) -> str:
    """从 chat/completions 响应中提取文本内容"""
    choices = resp.get("choices", [])
    if choices and isinstance(choices[0], dict):
        msg = choices[0].get("message", {})
        return msg.get("content", "")
    return ""


def extract_error(resp: dict) -> str:
    err = resp.get("error", {})
    if isinstance(err, dict):
        return err.get("message", str(err))
    return str(err) if err else str(resp.get("raw", "unknown error"))


# ============================================================
# 要测试的模型列表
# ============================================================
MODELS_TEXT = [
    "gpt-4.1",
    "gpt-4.1-mini",
    "claude-sonnet-4-5-20250929",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
]

# 支持多模态（图片理解）的模型
MODELS_VISION = [
    "gpt-4.1",
    "gpt-4.1-mini",
    "claude-sonnet-4-5-20250929",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
]


# ============================================================
# 测试 1：文本响应速度 + 基本能力
# ============================================================
def test_text_speed():
    log("=" * 70)
    log("测试 1：文本响应速度 + 基本推理能力")
    log("=" * 70)

    prompt = "一个农夫带着一只狼、一只羊和一棵白菜过河。船每次只能载农夫和另一样东西。如果农夫不在，狼会吃羊，羊会吃白菜。请给出过河方案，用中文简洁回答。"

    results = []
    for model in MODELS_TEXT:
        log(f"  测试 {model} ...")
        messages = [{"role": "user", "content": prompt}]
        status, resp, elapsed = api_chat(model, messages)

        if 200 <= status < 300:
            content = extract_content(resp)
            usage = resp.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            results.append({
                "model": model,
                "status": "✅",
                "elapsed": elapsed,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "tokens_per_sec": completion_tokens / elapsed if elapsed > 0 else 0,
                "response_preview": content[:120],
            })
            log(f"    ✅ {elapsed:.2f}s | {completion_tokens} tokens | {completion_tokens/elapsed:.1f} tok/s")
        else:
            error = extract_error(resp)
            results.append({
                "model": model,
                "status": "❌",
                "elapsed": elapsed,
                "error": error[:100],
            })
            log(f"    ❌ HTTP {status} ({elapsed:.2f}s): {error[:80]}")

    return results


# ============================================================
# 测试 2：图片理解能力（用项目产出海报）
# ============================================================
def test_vision_poster():
    log("")
    log("=" * 70)
    log("测试 2：图片理解能力（项目产出海报 poster/v1.png）")
    log("=" * 70)

    if not TEST_IMAGE.exists():
        log(f"  ⚠️  测试图片不存在: {TEST_IMAGE}")
        return []

    img_b64 = encode_image_base64(TEST_IMAGE)
    log(f"  图片大小: {TEST_IMAGE.stat().st_size / 1024:.1f} KB")

    prompt_text = "请分析这张设计海报：1) 描述画面主要内容和构图；2) 分析色彩搭配；3) 评价整体设计质量（调性、信息层级、视觉气质）。用中文回答。"

    results = []
    for model in MODELS_VISION:
        log(f"  测试 {model} (vision) ...")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}",
                        },
                    },
                ],
            }
        ]
        status, resp, elapsed = api_chat(model, messages, timeout=180)

        if 200 <= status < 300:
            content = extract_content(resp)
            usage = resp.get("usage", {})
            completion_tokens = usage.get("completion_tokens", 0)
            # 判断是否真正理解了图片（回复中应包含对画面的具体描述）
            has_visual_desc = len(content) > 50 and any(
                kw in content for kw in ["颜色", "色", "图", "画", "设计", "文字", "背景", "元素", "构图", "海报"]
            )
            results.append({
                "model": model,
                "status": "✅",
                "vision_works": has_visual_desc,
                "elapsed": elapsed,
                "completion_tokens": completion_tokens,
                "response_preview": content[:200],
            })
            vision_icon = "👁️" if has_visual_desc else "⚠️ 可能未理解图片"
            log(f"    ✅ {elapsed:.2f}s | {vision_icon} | {content[:80]}")
        else:
            error = extract_error(resp)
            results.append({
                "model": model,
                "status": "❌",
                "vision_works": False,
                "elapsed": elapsed,
                "error": error[:100],
            })
            log(f"    ❌ HTTP {status} ({elapsed:.2f}s): {error[:80]}")

    return results


# ============================================================
# 测试 3：图片理解能力（用项目产出 logo）
# ============================================================
def test_vision_logo():
    log("")
    log("=" * 70)
    log("测试 3：图片理解能力（项目产出 logo/v1-mark.png）")
    log("=" * 70)

    if not TEST_IMAGE_LOGO.exists():
        log(f"  ⚠️  测试图片不存在: {TEST_IMAGE_LOGO}")
        return []

    img_b64 = encode_image_base64(TEST_IMAGE_LOGO)
    log(f"  图片大小: {TEST_IMAGE_LOGO.stat().st_size / 1024:.1f} KB")

    prompt_text = "这是一个品牌 logo 图标。请描述：1) logo 的图形元素和形状；2) 使用的颜色；3) 传达的品牌气质和调性。用中文简洁回答。"

    results = []
    for model in MODELS_VISION:
        log(f"  测试 {model} (vision/logo) ...")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}",
                        },
                    },
                ],
            }
        ]
        status, resp, elapsed = api_chat(model, messages, timeout=180)

        if 200 <= status < 300:
            content = extract_content(resp)
            usage = resp.get("usage", {})
            completion_tokens = usage.get("completion_tokens", 0)
            has_visual_desc = len(content) > 30 and any(
                kw in content for kw in ["颜色", "色", "图", "形", "圆", "线", "标", "品牌", "logo", "Logo"]
            )
            results.append({
                "model": model,
                "status": "✅",
                "vision_works": has_visual_desc,
                "elapsed": elapsed,
                "completion_tokens": completion_tokens,
                "response_preview": content[:200],
            })
            vision_icon = "👁️" if has_visual_desc else "⚠️ 可能未理解图片"
            log(f"    ✅ {elapsed:.2f}s | {vision_icon} | {content[:80]}")
        else:
            error = extract_error(resp)
            results.append({
                "model": model,
                "status": "❌",
                "vision_works": False,
                "elapsed": elapsed,
                "error": error[:100],
            })
            log(f"    ❌ HTTP {status} ({elapsed:.2f}s): {error[:80]}")

    return results


# ============================================================
# 汇总报告
# ============================================================
def print_summary(text_results, vision_poster_results, vision_logo_results):
    print("\n")
    print("=" * 80)
    print("                    SII API LLM 能力测试报告")
    print(f"                    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 文本速度
    print("\n┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│ 1. 文本响应速度 + 推理能力                                                  │")
    print("├──────────────────────────────┬────────┬──────────┬───────────┬──────────────┤")
    print(f"│ {'模型':<28}│ {'状态':<6}│ {'耗时':<8} │ {'速度':<9} │ {'tokens':<12}│")
    print("├──────────────────────────────┼────────┼──────────┼───────────┼──────────────┤")
    for r in text_results:
        model = r["model"][:28]
        status = r["status"]
        elapsed = f"{r['elapsed']:.2f}s"
        if r["status"] == "✅":
            speed = f"{r['tokens_per_sec']:.1f} t/s"
            tokens = f"{r['completion_tokens']}"
        else:
            speed = "N/A"
            tokens = "N/A"
        print(f"│ {model:<28}│ {status:<5} │ {elapsed:<8} │ {speed:<9} │ {tokens:<12}│")
    print("└──────────────────────────────┴────────┴──────────┴───────────┴──────────────┘")

    # 视觉能力 - 海报
    print("\n┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│ 2. 图片理解能力（海报分析）                                                  │")
    print("├──────────────────────────────┬────────┬──────────┬───────────┬──────────────┤")
    print(f"│ {'模型':<28}│ {'状态':<6}│ {'耗时':<8} │ {'视觉理解':<8}│ {'tokens':<12}│")
    print("├──────────────────────────────┼────────┼──────────┼───────────┼──────────────┤")
    for r in vision_poster_results:
        model = r["model"][:28]
        status = r["status"]
        elapsed = f"{r['elapsed']:.2f}s"
        if r["status"] == "✅":
            vision = "👁️ 是" if r["vision_works"] else "❌ 否"
            tokens = f"{r['completion_tokens']}"
        else:
            vision = "N/A"
            tokens = "N/A"
        print(f"│ {model:<28}│ {status:<5} │ {elapsed:<8} │ {vision:<8}│ {tokens:<12}│")
    print("└──────────────────────────────┴────────┴──────────┴───────────┴──────────────┘")

    # 视觉能力 - Logo
    print("\n┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│ 3. 图片理解能力（Logo 分析）                                                 │")
    print("├──────────────────────────────┬────────┬──────────┬───────────┬──────────────┤")
    print(f"│ {'模型':<28}│ {'状态':<6}│ {'耗时':<8} │ {'视觉理解':<8}│ {'tokens':<12}│")
    print("├──────────────────────────────┼────────┼──────────┼───────────┼──────────────┤")
    for r in vision_logo_results:
        model = r["model"][:28]
        status = r["status"]
        elapsed = f"{r['elapsed']:.2f}s"
        if r["status"] == "✅":
            vision = "👁️ 是" if r["vision_works"] else "❌ 否"
            tokens = f"{r['completion_tokens']}"
        else:
            vision = "N/A"
            tokens = "N/A"
        print(f"│ {model:<28}│ {status:<5} │ {elapsed:<8} │ {vision:<8}│ {tokens:<12}│")
    print("└──────────────────────────────┴────────┴──────────┴───────────┴──────────────┘")

    # 详细视觉回复
    print("\n" + "=" * 80)
    print("详细视觉分析回复（截取前 200 字）")
    print("=" * 80)
    all_vision = [("海报", vision_poster_results), ("Logo", vision_logo_results)]
    for label, results in all_vision:
        print(f"\n--- {label} ---")
        for r in results:
            if r["status"] == "✅" and r.get("response_preview"):
                print(f"\n[{r['model']}]")
                print(f"  {r['response_preview']}")
            elif r["status"] == "❌":
                print(f"\n[{r['model']}] ❌ {r.get('error', 'unknown')}")

    # 结论
    print("\n" + "=" * 80)
    print("结论")
    print("=" * 80)
    vision_capable = []
    vision_incapable = []
    for r in vision_poster_results:
        if r["status"] == "✅" and r.get("vision_works"):
            vision_capable.append(r["model"])
        elif r["status"] == "✅" and not r.get("vision_works"):
            vision_incapable.append(r["model"])
        elif r["status"] == "❌":
            vision_incapable.append(f"{r['model']} (API 错误)")

    print(f"\n  支持图片理解的模型: {', '.join(vision_capable) if vision_capable else '无'}")
    print(f"  不支持/未确认的模型: {', '.join(vision_incapable) if vision_incapable else '无'}")

    if vision_capable:
        # 找最快的视觉模型
        fastest = min(
            [r for r in vision_poster_results if r["status"] == "✅" and r.get("vision_works")],
            key=lambda x: x["elapsed"],
        )
        print(f"\n  推荐用于 critic 视觉评审的模型: {fastest['model']} (海报分析耗时 {fastest['elapsed']:.2f}s)")
    print("")


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    log("SII API LLM 能力测试开始")
    log(f"测试图片: {TEST_IMAGE}")
    log(f"测试图片: {TEST_IMAGE_LOGO}")
    log("")

    text_results = test_text_speed()
    vision_poster_results = test_vision_poster()
    vision_logo_results = test_vision_logo()

    print_summary(text_results, vision_poster_results, vision_logo_results)
