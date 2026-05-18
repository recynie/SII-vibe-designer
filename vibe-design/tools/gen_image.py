#!/usr/bin/env python3
"""gen_image: route image generation between MiniMax (dev) and gpt-image-2 (prod).

Backend resolution (first match wins):
  --backend CLI flag  >  api.toml [active].image
Credentials and endpoints come from api.toml [providers.<backend>] via
vibe-design/tools/api_config.py. Designer agent never picks a backend itself.

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
import sys
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import api_config


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
    p = api_config.get_provider("minimax")
    payload = {
        "model": p.image_model or "image-01",
        "prompt": prompt,
        "n": 1,
        "aspect_ratio": aspect_ratio,
        "response_format": "url",
    }
    resp = http_post_json(
        f"{p.base_url}/v1/image_generation",
        {"Authorization": f"Bearer {p.key}", "Content-Type": "application/json"},
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


# Magic bytes for image formats actually returned by upstream APIs.
# Order matters only for documentation; checks are mutually exclusive.
_MAGIC = (
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),               # JPEG (JFIF, EXIF, raw)
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"RIFF", "webp_partial"),              # WEBP needs WEBP at offset 8
)


def detect_format(data: bytes) -> str:
    """Return canonical extension ('png' / 'jpg' / 'webp' / 'gif') from magic bytes.

    Raises SystemExit if bytes don't look like a supported image — better to
    fail loudly than save a corrupt file with a misleading extension.
    """
    for prefix, ext in _MAGIC:
        if not data.startswith(prefix):
            continue
        if ext == "webp_partial":
            if len(data) >= 12 and data[8:12] == b"WEBP":
                return "webp"
            continue
        return ext
    head = data[:16].hex() if data else "(empty)"
    raise SystemExit(f"unrecognized image format; first bytes = {head}")


def gen_openai(prompt: str, aspect_ratio: str, size: str | None) -> bytes:
    p = api_config.get_provider("openai")
    url = p.images_url or f"{p.base_url}/v1/images/generations"
    model = p.image_model or "gpt-image-2"
    chosen_size = size or SIZE_FROM_AR.get(aspect_ratio, "1024x1024")
    payload = {"model": model, "prompt": prompt, "n": 1, "size": chosen_size}
    resp = http_post_json(
        url,
        {"Authorization": f"Bearer {p.key}", "Content-Type": "application/json"},
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
        help="Override api.toml [active].image for a single call",
    )
    args = ap.parse_args()

    backend = args.backend or api_config.active_image_backend()
    if backend not in {"minimax", "openai"}:
        raise SystemExit(f"Unknown backend: {backend}")

    if backend == "minimax":
        image_bytes = gen_minimax(args.prompt, args.aspect_ratio)
    else:
        image_bytes = gen_openai(args.prompt, args.aspect_ratio, args.size)

    real_ext = detect_format(image_bytes)
    out_path = Path(args.output).expanduser().resolve()
    requested_ext = out_path.suffix.lstrip(".").lower()

    # If the upstream returned a different format than the user requested, prefer
    # the real format (silently re-suffix) so downstream tools that key off the
    # extension don't get fooled. Warn so the caller notices.
    if requested_ext != real_ext and not (
        requested_ext in ("jpg", "jpeg") and real_ext == "jpg"
    ):
        new_path = out_path.with_suffix(f".{real_ext}")
        print(
            f"  [gen_image] backend returned {real_ext.upper()}, requested .{requested_ext}; "
            f"writing to {new_path.name} instead",
            file=sys.stderr,
        )
        out_path = new_path

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(image_bytes)

    prompt_path = out_path.with_suffix(out_path.suffix + ".prompt.txt")
    prompt_path.write_text(
        f"# backend: {backend}\n# format: {real_ext}\n# aspect: {args.aspect_ratio}\n\n{args.prompt}\n",
        encoding="utf-8",
    )

    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
