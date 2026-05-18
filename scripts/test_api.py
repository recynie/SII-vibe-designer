#!/usr/bin/env python3
"""
测试 2026 夏令营商用 API 手册中各端点的可用性。

凭据从仓库根目录 `api.toml` 的 role `camp_audit`（默认 -> sii provider）读取，
缺失或仍是占位符直接报错。
"""
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vibe-design" / "tools"))
import api_config

_provider = api_config.active_llm()
API_KEY = _provider.key
BASE_URL = _provider.base_url
TIMEOUT = 60  # 秒
# ==========================

results = []


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def api_request(method, path, body=None, timeout=TIMEOUT, extra_headers=None):
    """发送 HTTP 请求并返回 (status_code, response_body_dict_or_str)"""
    if path.startswith("/"):
        url = f"{BASE_URL.rstrip('/')}{path}"
    else:
        url = path
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw
    except Exception as e:
        return 0, str(e)


def test_endpoint(name, method, path, body, timeout=TIMEOUT, extra_headers=None):
    """测试单个端点并记录结果"""
    log(f"测试: {name} ...")
    start = time.time()
    status, resp = api_request(method, path, body, timeout, extra_headers)
    elapsed = time.time() - start

    success = 200 <= status < 300
    result = {
        "name": name,
        "status": status,
        "success": success,
        "elapsed": f"{elapsed:.2f}s",
    }

    if success:
        # 提取关键信息
        if isinstance(resp, dict):
            model = resp.get("model", "")
            if model:
                result["model"] = model
            # chat completions
            choices = resp.get("choices", [])
            if choices and isinstance(choices[0], dict):
                msg = choices[0].get("message", {})
                content = msg.get("content", "")
                if content:
                    result["response_preview"] = content[:100]
            # embeddings
            data = resp.get("data", [])
            if data and isinstance(data[0], dict) and "embedding" in data[0]:
                result["embedding_dim"] = len(data[0]["embedding"])
            # images
            if data and isinstance(data[0], dict) and ("url" in data[0] or "b64_json" in data[0]):
                result["image_generated"] = True
        log(f"  ✅ 成功 (HTTP {status}, {elapsed:.2f}s)")
    else:
        error_msg = ""
        if isinstance(resp, dict):
            error_msg = resp.get("error", {}).get("message", "") if isinstance(resp.get("error"), dict) else str(resp.get("error", ""))
        else:
            error_msg = str(resp)[:200]
        result["error"] = error_msg
        log(f"  ❌ 失败 (HTTP {status}, {elapsed:.2f}s): {error_msg[:100]}")

    results.append(result)
    return success, resp


# ============================================================
# 1. chat/completions - GPT 模型
# ============================================================
test_endpoint(
    "1.1 chat/completions - gpt-4.1",
    "POST", "/chat/completions",
    {
        "model": "gpt-4.1",
        "messages": [{"role": "user", "content": "Say hello in one word."}],
        "max_tokens": 50,
        "temperature": 0.5,
    }
)

# ============================================================
# 1. chat/completions - Claude 模型
# ============================================================
test_endpoint(
    "1.2 chat/completions - claude-sonnet-4-5-20250929",
    "POST", "/chat/completions",
    {
        "model": "claude-sonnet-4-5-20250929",
        "messages": [{"role": "user", "content": "repeat me: hello"}],
        "max_tokens": 50,
    }
)

# ============================================================
# 1. chat/completions - Gemini 模型
# ============================================================
test_endpoint(
    "1.3 chat/completions - gemini-3-flash-preview",
    "POST", "/chat/completions",
    {
        "model": "gemini-3-flash-preview",
        "messages": [{"role": "user", "content": "Say hello in one word."}],
        "max_tokens": 50,
    }
)

# ============================================================
# 2. responses 端点 - GPT-5 系列
# ============================================================
test_endpoint(
    "2. responses - gpt-5.2",
    "POST", "/responses",
    {
        "model": "gpt-5.2",
        "input": "Say hello in one sentence.",
    }
)

# ============================================================
# 3. embeddings 端点
# ============================================================
test_endpoint(
    "3. embeddings - text-embedding-3-small",
    "POST", "/embeddings",
    {
        "model": "text-embedding-3-small",
        "input": "Hello world",
        "encoding_format": "float",
    }
)

# ============================================================
# 4. images/generations 端点 - GPT 生图
# ============================================================
test_endpoint(
    "4.1 images/generations - gpt-image-2",
    "POST", "/images/generations",
    {
        "model": "gpt-image-2",
        "prompt": "A simple red circle on white background",
        "n": 1,
        "size": "1024x1024",
    },
    timeout=600,
)

# ============================================================
# 4. images/generations 端点 - 豆包生图
# ============================================================
test_endpoint(
    "4.2 images/generations - doubao-seedream-4-0-250828",
    "POST", "/images/generations",
    {
        "model": "doubao-seedream-4-0-250828",
        "prompt": "一只在月球上喝咖啡的猫",
    },
    timeout=600,
)

# ============================================================
# 6. Claude 原生端点 messages
# ============================================================
test_endpoint(
    "6. Claude messages 原生端点",
    "POST", "/messages",
    {
        "model": "claude-sonnet-4-5-20250929",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 50,
    },
    extra_headers={"anthropic-version": "2023-06-01"},
)

# ============================================================
# 7. Gemini 原生端点 v1beta/models
# ============================================================
log("测试: 7. Gemini 原生端点 v1beta ...")
start = time.time()
gemini_url = BASE_URL.replace("/v1", "") + "/v1beta/models/gemini-2.5-flash:generateContent"
gemini_body = {
    "contents": [
        {
            "parts": [
                {"text": "Say hello in one word."}
            ]
        }
    ]
}
gemini_headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
gemini_data = json.dumps(gemini_body).encode("utf-8")
gemini_req = urllib.request.Request(gemini_url, data=gemini_data, headers=gemini_headers, method="POST")
try:
    with urllib.request.urlopen(gemini_req, timeout=TIMEOUT) as resp:
        raw = resp.read().decode("utf-8")
        status = resp.status
        try:
            gemini_resp = json.loads(raw)
        except json.JSONDecodeError:
            gemini_resp = raw
except urllib.error.HTTPError as e:
    status = e.code
    raw = e.read().decode("utf-8", errors="replace")
    try:
        gemini_resp = json.loads(raw)
    except json.JSONDecodeError:
        gemini_resp = raw
except Exception as e:
    status = 0
    gemini_resp = str(e)

elapsed = time.time() - start
success = 200 <= status < 300
result = {
    "name": "7. Gemini 原生端点 v1beta/models",
    "status": status,
    "success": success,
    "elapsed": f"{elapsed:.2f}s",
}
if success:
    log(f"  ✅ 成功 (HTTP {status}, {elapsed:.2f}s)")
    if isinstance(gemini_resp, dict):
        candidates = gemini_resp.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                result["response_preview"] = parts[0].get("text", "")[:100]
else:
    error_msg = ""
    if isinstance(gemini_resp, dict):
        error_msg = str(gemini_resp.get("error", ""))[:200]
    else:
        error_msg = str(gemini_resp)[:200]
    result["error"] = error_msg
    log(f"  ❌ 失败 (HTTP {status}, {elapsed:.2f}s): {error_msg[:100]}")
results.append(result)


# ============================================================
# 汇总报告
# ============================================================
print("\n" + "=" * 70)
print("                    API 可用性测试报告")
print("=" * 70)
print(f"{'序号':<4} {'端点名称':<45} {'状态':<6} {'耗时':<8} {'结果'}")
print("-" * 70)
for i, r in enumerate(results, 1):
    status_icon = "✅" if r["success"] else "❌"
    extra = ""
    if r.get("model"):
        extra = f"model={r['model']}"
    elif r.get("embedding_dim"):
        extra = f"dim={r['embedding_dim']}"
    elif r.get("image_generated"):
        extra = "图片已生成"
    elif r.get("response_preview"):
        extra = r["response_preview"][:40]
    elif r.get("error"):
        extra = r["error"][:40]
    print(f"{i:<4} {r['name']:<45} {r['status']:<6} {r['elapsed']:<8} {status_icon} {extra}")

print("-" * 70)
total = len(results)
passed = sum(1 for r in results if r["success"])
print(f"\n总计: {total} 个端点, {passed} 个成功, {total - passed} 个失败")
print("=" * 70)
