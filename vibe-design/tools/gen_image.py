#!/usr/bin/env python3
"""gen_image: route image generation between MiniMax (dev) and gpt-image-2 (prod).

Backend selected by env DESIGN_IMAGE_BACKEND ∈ {minimax, openai}, default openai.
Designer agent calls this CLI; it never picks the backend itself.

Usage:
    uv run python tools/gen_image.py \\
        --prompt "minimal logo for a coffee startup, geometric, two-tone" \\
        --output outputs/run-x/artifacts/logo/v1.png \\
        [--aspect-ratio 1:1] [--size 1024x1024]

Exit code 0 on success; prints absolute path of saved file to stdout.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

ENV_FILE_CANDIDATES = [
    Path(__file__).resolve().parent.parent.parent / ".env",
    Path(__file__).resolve().parent.parent / ".env",
]


def load_env() -> None:
    """Lightweight .env loader (no python-dotenv dependency).

    First env file found wins; values already in os.environ are not overwritten.
    """
    for p in ENV_FILE_CANDIDATES:
        if not p.is_file():
            continue
        for raw in p.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val
        return


DEFAULT_UA = "vibe-design/0.1 (+https://github.com/local)"


import time


def http_post_json(url: str, headers: dict, body: dict, timeout: int = 600, max_retries: int = 5) -> dict:
    data = json.dumps(body).encode("utf-8")
    h = {"User-Agent": DEFAULT_UA, **headers}
    last_exc = None
    for attempt in range(1, max_retries + 1):
        req = urllib.request.Request(url, data=data, headers=h, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, OSError, TimeoutError) as e:
            last_exc = e
            if isinstance(e, urllib.error.HTTPError) and 400 <= e.code < 500 and e.code != 429:
                msg = e.read().decode("utf-8", errors="replace")
                raise SystemExit(f"HTTP {e.code} from {url}: {msg[:500]}")
            if attempt < max_retries:
                wait = min(30 * attempt, 120)
                print(f"  [retry {attempt}/{max_retries}] {type(e).__name__}, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
    raise SystemExit(f"All {max_retries} retries failed: {last_exc}")


def http_get_bytes(url: str, timeout: int = 180) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def gen_minimax(prompt: str, aspect_ratio: str) -> bytes:
    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        raise SystemExit("MINIMAX_API_KEY not set")
    base = os.environ.get("MINIMAX_BASE_URL", "https://api.minimaxi.com").rstrip("/")
    payload = {
        "model": "image-01",
        "prompt": prompt,
        "n": 1,
        "aspect_ratio": aspect_ratio,
        "response_format": "url",
    }
    resp = http_post_json(
        f"{base}/v1/image_generation",
        {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        payload,
    )
    base_resp = resp.get("base_resp") or {}
    if base_resp.get("status_code") not in (0, None):
        raise SystemExit(f"MiniMax error: {base_resp.get('status_msg')}")
    urls = (resp.get("data") or {}).get("image_urls") or []
    if not urls:
        raise SystemExit(f"MiniMax returned no images: {json.dumps(resp)[:300]}")
    return http_get_bytes(urls[0])


SIZE_FROM_AR = {
    "1:1": "1024x1024",
    "3:4": "1024x1536",
    "4:3": "1536x1024",
    "16:9": "1536x1024",
    "9:16": "1024x1536",
}


def gen_openai(prompt: str, aspect_ratio: str, size: str | None) -> bytes:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY not set")
    url = os.environ.get(
        "OPENAI_IMAGES_URL",
        os.environ.get("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/")
        + "/v1/images/generations",
    )
    model = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
    chosen_size = size or SIZE_FROM_AR.get(aspect_ratio, "1024x1024")
    payload = {"model": model, "prompt": prompt, "n": 1, "size": chosen_size}
    resp = http_post_json(
        url,
        {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        payload,
    )
    items = resp.get("data") or []
    if not items:
        raise SystemExit(f"OpenAI returned no data: {json.dumps(resp)[:300]}")
    item = items[0]
    if "b64_json" in item:
        return base64.b64decode(item["b64_json"])
    if "url" in item:
        return http_get_bytes(item["url"])
    raise SystemExit(f"OpenAI returned unexpected shape: {json.dumps(item)[:200]}")


def main() -> int:
    load_env()
    ap = argparse.ArgumentParser(description="Generate an image for the design agent.")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--output", required=True, help="Output file path (.png)")
    ap.add_argument(
        "--aspect-ratio",
        default="1:1",
        choices=list(SIZE_FROM_AR.keys()),
    )
    ap.add_argument("--size", default=None, help="Override exact size, e.g. 1024x1024")
    ap.add_argument(
        "--backend",
        default=None,
        choices=["minimax", "openai"],
        help="Override DESIGN_IMAGE_BACKEND for a single call",
    )
    args = ap.parse_args()

    backend = args.backend or os.environ.get("DESIGN_IMAGE_BACKEND", "openai").lower()
    if backend not in {"minimax", "openai"}:
        raise SystemExit(f"Unknown backend: {backend}")

    if backend == "minimax":
        image_bytes = gen_minimax(args.prompt, args.aspect_ratio)
    else:
        image_bytes = gen_openai(args.prompt, args.aspect_ratio, args.size)

    out_path = Path(args.output).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(image_bytes)

    prompt_path = out_path.with_suffix(out_path.suffix + ".prompt.txt")
    prompt_path.write_text(
        f"# backend: {backend}\n# aspect: {args.aspect_ratio}\n\n{args.prompt}\n",
        encoding="utf-8",
    )

    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
