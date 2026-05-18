#!/usr/bin/env python3
"""
测试 SII API 生图延迟（对比 findcg）。
取巧：用更短 timeout + 只测一轮对比。

凭据从 api.toml [providers.sii] / [providers.openai] 读取（不再用 .env）。
"""
import json, time, base64, urllib.request, urllib.error, signal, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vibe-design" / "tools"))
import api_config

log = lambda msg: print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def request_with_timeout(url, data, headers, timeout):
    """带超时的 HTTP 请求"""
    import threading

    result = {"status": 0, "resp": None, "elapsed": 0}

    def do_request():
        start = time.time()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result["elapsed"] = time.time() - start
                result["status"] = resp.status
                result["resp"] = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            result["elapsed"] = time.time() - start
            result["status"] = e.code
            result["resp"] = {"error": e.read().decode("utf-8", errors="replace")[:200]}
        except Exception as e:
            result["elapsed"] = time.time() - start
            result["status"] = 0
            result["resp"] = {"error": str(e)[:200]}

    thread = threading.Thread(target=do_request)
    thread.start()
    thread.join(timeout=timeout + 10)
    if thread.is_alive():
        return {"status": -1, "resp": {"error": f"TIMEOUT ({timeout}s exceeded)"}, "elapsed": timeout}

    return result


def test_provider(label, base_url, api_key, model="gpt-image-2", prompt=None, timeout=600):
    if not api_key:
        log(f"  ⏭️  {label}：无 API key")
        return None

    url = f"{base_url.rstrip('/')}/images/generations"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    prompt = prompt or "A simple minimalist coffee brand logo, warm brown tones, white background, clean lines"
    body = {"model": model, "prompt": prompt, "n": 1, "size": "1024x1024"}
    data = json.dumps(body).encode("utf-8")

    log(f"  请求 {label}（{model}）... 超时={timeout}s")
    result = request_with_timeout(url, data, headers, timeout)

    elapsed = result["elapsed"]
    status = result["status"]
    resp = result["resp"]

    if status == -1:
        log(f"  ⏰ {label} 超时 >{elapsed}s")
        return {"label": label, "elapsed": elapsed, "success": False, "error": "TIMEOUT"}

    if 200 <= status < 300:
        data_list = resp.get("data", [])
        if data_list and "b64_json" in data_list[0]:
            img_size_kb = len(data_list[0]["b64_json"]) * 3 / 4 / 1024
            log(f"  ✅ {label} 成功 | {elapsed:.1f}s | {img_size_kb:.0f}KB b64_json")
        else:
            log(f"  ✅ {label} 成功 | {elapsed:.1f}s | keys={list(data_list[0].keys()) if data_list else 'no data'}")
        return {"label": label, "elapsed": elapsed, "success": True}
    else:
        err_msg = resp.get("error", str(resp)[:100]) if isinstance(resp, dict) else str(resp)[:100]
        log(f"  ❌ {label} 失败 | {elapsed:.1f}s | HTTP {status}: {err_msg}")
        return {"label": label, "elapsed": elapsed, "success": False, "error": err_msg}


_sii = api_config.get_provider("sii")
_openai = api_config.get_provider("openai")
sii_key = _sii.key
findcg_key = _openai.key
SII_URL = _sii.base_url
FINDCG_URL = _openai.base_url + "/v1"
PROMPT = "极简咖啡品牌 logo，暖棕色系，白色背景，线条风格，包含文字 '钝角咖啡'"

print("\n" + "=" * 65)
print("  🖼️  SII vs findcg 生图延迟对比")
print("=" * 65)
log(f"  Prompt: {PROMPT[:50]}...\n")


# 先跑 findcg（快）
r_findcg = test_provider("findcg", FINDCG_URL, findcg_key, timeout=120)

print()
# 再跑 SII（可能慢，但单独跑）
r_sii = test_provider("SII (apicz)", SII_URL, sii_key, timeout=600)

print("\n" + "=" * 65)
print("  📊 对比结果")
print("=" * 65)
for r in [r_findcg, r_sii]:
    if r:
        icon = "✅" if r["success"] else "❌"
        extra = r.get("error", "") if not r["success"] else ""
        print(f"  {r['label']:<18} {r['elapsed']:<8.1f}s {icon} {extra}")

if r_findcg and r_sii and r_findcg["success"] and r_sii["success"]:
    ratio = r_sii["elapsed"] / r_findcg["elapsed"]
    print(f"\n  SII 是 findcg 的 {ratio:.1f}x 慢")
elif r_sii and not r_sii["success"]:
    print(f"\n  ⚠️  SII 生图超时或失败（已等待 {r_sii['elapsed']:.0f}s）")
    print(f"  错误: {r_sii.get('error', '未知')}")

print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 65)
