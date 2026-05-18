#!/usr/bin/env python3
"""
测试 SII API 生图延迟（gpt-image-2）

凭据从 api.toml [providers.sii] 读取（不再用 .env）。
"""
import json, time, base64, sys, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vibe-design" / "tools"))
import api_config

_provider = api_config.get_provider("sii")
API_KEY = _provider.key
BASE_URL = _provider.base_url
log = lambda msg: print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def images_generate(model, prompt, n=1, size="1024x1024", timeout=600):
    url = f"{BASE_URL}/images/generations"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    body = {"model": model, "prompt": prompt, "n": n, "size": size}
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


print("\n" + "=" * 60)
print("  🎨 测试 SII 生图延迟")
print("=" * 60)

# 简单 prompt，减少变量
prompt = "A minimalist logo for a tech startup, clean white background, simple geometric shapes"

log(f"模型: gpt-image-2")
log(f"Prompt: {prompt}")
log(f"开始请求...")

status, resp, elapsed = images_generate("gpt-image-2", prompt, timeout=600)

if status == 200:
    data = resp.get("data", [])
    if data:
        # 检查返回类型
        if "url" in data[0]:
            img_type = "url"
            img_val = data[0]["url"][:80]
        elif "b64_json" in data[0]:
            b64 = data[0]["b64_json"]
            img_type = f"base64 ({len(b64)/1024:.0f} KB)"
            img_val = b64[:40]
        else:
            img_type = "unknown"
            img_val = str(data[0])[:80]

        log(f"  ✅ 成功! 耗时: {elapsed:.1f}s")
        log(f"  返回类型: {img_type}")
        log(f"  revised_prompt: {data[0].get('revised_prompt','-')[:120]}")

        # 保存图片
        out_dir = Path(__file__).resolve().parent.parent / "vibe-design" / "outputs" / "test-image"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"sii-gpt-image-2-test.png"

        if "b64_json" in data[0]:
            img_bytes = base64.b64decode(data[0]["b64_json"])
            out_path.write_bytes(img_bytes)
            log(f"  已保存: {out_path} ({len(img_bytes)/1024:.1f} KB)")
        elif "url" in data[0]:
            # 下载
            urllib.request.urlretrieve(data[0]["url"], out_path)
            log(f"  已下载保存: {out_path}")

    else:
        log(f"  ⚠️ 无 data 返回: {str(resp)[:200]}")
else:
    err = resp.get("error", {}).get("message", str(resp)[:200])
    log(f"  ❌ 失败 (HTTP {status}, {elapsed:.1f}s): {err}")

print("=" * 60)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 60)
