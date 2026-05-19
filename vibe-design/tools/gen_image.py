#!/usr/bin/env python3
"""gen_image: route image generation / image editing between MiniMax (dev) and gpt-image-2 (prod).

Backend resolution (first match wins):
  --backend CLI flag  >  api.toml [active].image
Credentials and endpoints come from api.toml [providers.<backend>] via
vibe-design/tools/api_config.py. Designer agent never picks a backend itself.

Usage:
    uv run python tools/gen_image.py \\
        --prompt "minimal logo for a coffee startup, geometric, two-tone" \\
        --output outputs/run-x/artifacts/logo/v1.png \\
        [--aspect-ratio 1:1] [--size 1024x1024] [--candidates 3]

    # Image-to-image / edit mode (OpenAI-compatible backend only):
    uv run python tools/gen_image.py \\
        --input-image outputs/run-x/artifacts/logo/v1.png \\
        --prompt "keep the same geometry, recolor strictly to navy and cyan" \\
        --output outputs/run-x/artifacts/logo/v2.png

Exit code 0 on success; prints absolute path(s) of saved file(s) to stdout,
one per line.
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import json
import mimetypes
import sys
import time
import urllib.request
import urllib.error
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import api_config


DEFAULT_UA = "vibe-design/0.1 (+https://github.com/local)"


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


def http_post_multipart(
    url: str,
    headers: dict,
    fields: dict[str, str],
    files: list[tuple[str, Path]],
    timeout: int = 600,
    max_retries: int = 5,
) -> dict:
    """POST multipart/form-data with stdlib only.

    `files` is a list of (form_field_name, path). Duplicate field names are
    allowed; OpenAI-compatible image-edit APIs use that for multiple inputs.
    """
    boundary = f"----vibe-design-{uuid.uuid4().hex}"
    chunks: list[bytes] = []

    for name, value in fields.items():
        chunks.extend([
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"),
            str(value).encode("utf-8"),
            b"\r\n",
        ])

    for field_name, path in files:
        filename = path.name
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        chunks.extend([
            f"--{boundary}\r\n".encode("utf-8"),
            (
                f'Content-Disposition: form-data; name="{field_name}"; '
                f'filename="{filename}"\r\n'
            ).encode("utf-8"),
            f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"),
            path.read_bytes(),
            b"\r\n",
        ])

    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    data = b"".join(chunks)
    h = {
        "User-Agent": DEFAULT_UA,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        **headers,
    }

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


def decode_openai_image_response(resp: dict, label: str = "OpenAI") -> bytes:
    items = resp.get("data") or []
    if not items:
        raise SystemExit(f"{label} returned no data: {json.dumps(resp)[:300]}")
    item = items[0]
    if "b64_json" in item:
        return base64.b64decode(item["b64_json"])
    if "url" in item:
        return http_get_bytes(item["url"])
    raise SystemExit(f"{label} returned unexpected shape: {json.dumps(item)[:200]}")


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
    return decode_openai_image_response(resp)


def gen_openai_edit(
    prompt: str,
    aspect_ratio: str,
    size: str | None,
    input_images: list[Path],
    mask: Path | None,
) -> bytes:
    p = api_config.get_provider("openai")
    url = p.edits_url or f"{p.base_url}/v1/images/edits"
    model = p.image_model or "gpt-image-2"
    chosen_size = size or SIZE_FROM_AR.get(aspect_ratio, "1024x1024")
    fields = {"model": model, "prompt": prompt, "n": "1", "size": chosen_size}
    files = [("image", path) for path in input_images]
    if mask is not None:
        files.append(("mask", mask))
    resp = http_post_multipart(
        url,
        {"Authorization": f"Bearer {p.key}"},
        fields,
        files,
    )
    return decode_openai_image_response(resp, label="OpenAI image edit")


def gen_candidates(
    backend: str,
    prompt: str,
    aspect_ratio: str,
    size: str | None,
    candidates: int,
    input_images: list[Path] | None = None,
    mask: Path | None = None,
) -> list[bytes]:
    """Fire *candidates* independent n=1 requests in parallel, return successful results."""
    input_images = input_images or []
    if backend == "minimax":
        if input_images or mask:
            raise SystemExit("MiniMax backend does not support --input-image / --mask in gen_image; use --backend openai.")
        fn = lambda: gen_minimax(prompt, aspect_ratio)
    elif input_images:
        fn = lambda: gen_openai_edit(prompt, aspect_ratio, size, input_images, mask)
    else:
        if mask:
            raise SystemExit("--mask requires --input-image")
        fn = lambda: gen_openai(prompt, aspect_ratio, size)

    if candidates == 1:
        return [fn()]

    results: list[bytes] = []
    errors: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=candidates) as pool:
        futures = {pool.submit(fn): i for i in range(candidates)}
        for fut in concurrent.futures.as_completed(futures):
            idx = futures[fut]
            try:
                results.append(fut.result())
            except SystemExit as e:
                errors.append(f"  candidate {idx + 1}: {e}")
                print(f"  [gen_image] candidate {idx + 1} failed: {e}", file=sys.stderr)

    if not results:
        raise SystemExit(f"All {candidates} candidates failed:\n" + "\n".join(errors))
    return results


def candidate_path(base: Path, index: int) -> Path:
    """v1.png + index 2 → v1-2.png"""
    return base.with_suffix(f"-{index}{base.suffix}")


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer") from None
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate an image for the design agent.")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--output", required=True, help="Output file path (.png)")
    ap.add_argument(
        "--input-image",
        action="append",
        default=[],
        help="Input image path for image-to-image/edit mode. Repeat for multiple reference images. OpenAI backend only.",
    )
    ap.add_argument(
        "--mask",
        default=None,
        help="Optional mask image for edit mode. Requires --input-image and OpenAI backend.",
    )
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
    ap.add_argument(
        "--candidates",
        type=positive_int,
        default=3,
        help="Number of candidate images to generate in parallel (default: 3)",
    )
    args = ap.parse_args()

    backend = args.backend or api_config.active_image_backend()
    if backend not in {"minimax", "openai"}:
        raise SystemExit(f"Unknown backend: {backend}")

    input_images = [Path(p).expanduser().resolve() for p in args.input_image]
    for p in input_images:
        if not p.is_file():
            raise SystemExit(f"input image not found: {p}")
    mask = Path(args.mask).expanduser().resolve() if args.mask else None
    if mask is not None and not mask.is_file():
        raise SystemExit(f"mask image not found: {mask}")
    if input_images and args.backend is None and backend == "minimax":
        print(
            "  [gen_image] --input-image requested; active minimax backend does not support image edits, routing to openai",
            file=sys.stderr,
        )
        backend = "openai"

    images = gen_candidates(
        backend,
        args.prompt,
        args.aspect_ratio,
        args.size,
        args.candidates,
        input_images=input_images,
        mask=mask,
    )

    base_path = Path(args.output).expanduser().resolve()
    base_path.parent.mkdir(parents=True, exist_ok=True)

    for i, image_bytes in enumerate(images, 1):
        real_ext = detect_format(image_bytes)
        out_path = candidate_path(base_path, i)
        requested_ext = out_path.suffix.lstrip(".").lower()

        if requested_ext != real_ext and not (
            requested_ext in ("jpg", "jpeg") and real_ext == "jpg"
        ):
            new_path = out_path.with_suffix(f".{real_ext}")
            print(
                f"  [gen_image] candidate {i}: backend returned {real_ext.upper()}, "
                f"requested .{requested_ext}; writing to {new_path.name} instead",
                file=sys.stderr,
            )
            out_path = new_path

        out_path.write_bytes(image_bytes)

        prompt_path = out_path.with_suffix(out_path.suffix + ".prompt.txt")
        input_lines = "".join(f"# input_image: {p}\n" for p in input_images)
        mask_line = f"# mask: {mask}\n" if mask is not None else ""
        prompt_path.write_text(
            f"# backend: {backend}\n# mode: {'image-to-image' if input_images else 'text-to-image'}\n"
            f"# format: {real_ext}\n# aspect: {args.aspect_ratio}\n"
            f"# candidate: {i}/{len(images)}\n"
            f"{input_lines}{mask_line}\n{args.prompt}\n",
            encoding="utf-8",
        )

        print(str(out_path))

    return 0


if __name__ == "__main__":
    sys.exit(main())
