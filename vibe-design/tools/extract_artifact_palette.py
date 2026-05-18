"""extract_artifact_palette: extract dominant hex colors from a PNG/JPG.

Output is two lists, both lowercase #RRGGBB:
- top_n: most frequent quantized colors
- kmeans: visually dominant centroids

Combined and de-duplicated for downstream check_palette_compliance.

Usage:
    uv run python vibe-design/tools/extract_artifact_palette.py <image> [--top 8] [--k 5]

Output (stdout, JSON):
    {"top": ["#1a73e8", ...], "kmeans": ["#1a73e8", ...], "combined": [...]}
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.stderr.write("PIL not available; install with `uv add pillow`\n")
    sys.exit(2)


def quantize_hex(rgb: tuple[int, int, int], step: int = 16) -> str:
    r, g, b = (max(0, min(255, (c // step) * step)) for c in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"


def top_colors(img: Image.Image, n: int) -> list[str]:
    img = img.convert("RGB").resize((128, 128))
    px = list(img.getdata())
    counts = Counter(quantize_hex(p) for p in px)
    return [hx for hx, _ in counts.most_common(n)]


def kmeans_colors(img: Image.Image, k: int, iters: int = 10) -> list[str]:
    """Lightweight k-means on a downsampled image. No sklearn dependency."""
    import random

    img = img.convert("RGB").resize((96, 96))
    pixels = list(img.getdata())
    if len(pixels) < k:
        return [f"#{r:02x}{g:02x}{b:02x}" for (r, g, b) in pixels]

    random.seed(42)
    centroids = random.sample(pixels, k)
    for _ in range(iters):
        clusters: list[list[tuple[int, int, int]]] = [[] for _ in range(k)]
        for p in pixels:
            best = 0
            best_d = float("inf")
            for ci, c in enumerate(centroids):
                d = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 + (p[2] - c[2]) ** 2
                if d < best_d:
                    best_d = d
                    best = ci
            clusters[best].append(p)
        new_centroids: list[tuple[int, int, int]] = []
        for ci, cl in enumerate(clusters):
            if not cl:
                new_centroids.append(centroids[ci])
                continue
            r = sum(p[0] for p in cl) // len(cl)
            g = sum(p[1] for p in cl) // len(cl)
            b = sum(p[2] for p in cl) // len(cl)
            new_centroids.append((r, g, b))
        if new_centroids == centroids:
            break
        centroids = new_centroids
    weights = [(len(cl), c) for cl, c in zip(clusters, centroids)]
    weights.sort(reverse=True)
    return [f"#{r:02x}{g:02x}{b:02x}" for _, (r, g, b) in weights]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", help="path to PNG/JPG")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()

    p = Path(args.image)
    if not p.is_file():
        sys.stderr.write(f"file not found: {p}\n")
        return 2

    img = Image.open(p)
    top = top_colors(img, args.top)
    km = kmeans_colors(img, args.k)
    combined: list[str] = []
    for h in top + km:
        if h not in combined:
            combined.append(h)

    json.dump({"top": top, "kmeans": km, "combined": combined}, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
