"""check_palette_compliance: verify an artifact's dominant hex colors fall within
brand-spec.md palette (ΔE76 in Lab space < threshold).

Pipeline:
1. Run extract_artifact_palette on the image.
2. Parse hex values out of brand-spec.md `## 色板` section.
3. For each extracted hex, find nearest spec hex by ΔE76.
4. Fail if the dominant color (largest cluster) is farther than threshold,
   OR if more than `--max-strays` of the top 8 are out of palette.

Neutral colors (background-ish very-light or very-dark / near-grey) are
excluded from the stray count by default — pages with white space shouldn't
be punished for it.

Usage:
    uv run python vibe-design/tools/check_palette_compliance.py \\
        --image artifact.png --spec brand-spec.md \\
        [--threshold 5.0] [--max-strays 2]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HEX_RE = re.compile(r"#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b")


def hex_to_rgb(hx: str) -> tuple[int, int, int]:
    h = hx.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_lab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = (c / 255.0 for c in rgb)

    def srgb_to_linear(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 1.0
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e76(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    l1, a1, b1 = rgb_to_lab(c1)
    l2, a2, b2 = rgb_to_lab(c2)
    return ((l1 - l2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2) ** 0.5


def is_neutral(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    mx, mn = max(rgb), min(rgb)
    if mx - mn <= 12 and (mx >= 235 or mx <= 30):
        return True
    return False


def parse_palette(spec_path: Path) -> list[str]:
    text = spec_path.read_text(encoding="utf-8")
    in_palette = False
    hexes: list[str] = []
    for raw in text.splitlines():
        if raw.startswith("## "):
            in_palette = raw.strip().endswith("色板")
            continue
        if in_palette:
            for m in HEX_RE.finditer(raw):
                v = "#" + m.group(1).lower()
                if len(v) == 4:
                    v = "#" + "".join(c * 2 for c in v[1:])
                if v not in hexes:
                    hexes.append(v)
    return hexes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--spec", required=True, help="brand-spec.md")
    ap.add_argument("--threshold", type=float, default=5.0)
    ap.add_argument("--max-strays", type=int, default=2)
    args = ap.parse_args()

    spec_path = Path(args.spec)
    img_path = Path(args.image)
    if not img_path.is_file():
        sys.stderr.write(f"image not found: {img_path}\n")
        return 2
    if not spec_path.is_file():
        sys.stderr.write(f"spec not found: {spec_path}\n")
        return 2

    palette = parse_palette(spec_path)
    if not palette:
        print(f"FAIL: no palette hexes parsed from {spec_path}")
        return 1

    extractor = Path(__file__).parent / "extract_artifact_palette.py"
    proc = subprocess.run(
        [sys.executable, str(extractor), str(img_path), "--top", "8", "--k", "5"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(f"extract_artifact_palette failed: {proc.stderr}\n")
        return 2
    data = json.loads(proc.stdout.strip().splitlines()[-1])
    artifact_hexes: list[str] = data["combined"][:8]

    palette_rgbs = [hex_to_rgb(h) for h in palette]
    issues: list[str] = []
    strays: list[tuple[str, float, str]] = []
    dominant = artifact_hexes[0] if artifact_hexes else None

    for hx in artifact_hexes:
        rgb = hex_to_rgb(hx)
        if is_neutral(rgb):
            continue
        nearest = min(((p, delta_e76(rgb, p_rgb)) for p, p_rgb in zip(palette, palette_rgbs)), key=lambda t: t[1])
        nearest_hex, dist = nearest
        if dist > args.threshold:
            strays.append((hx, dist, nearest_hex))

    if dominant:
        dom_rgb = hex_to_rgb(dominant)
        if not is_neutral(dom_rgb):
            nearest_hex, dist = min(
                ((p, delta_e76(dom_rgb, p_rgb)) for p, p_rgb in zip(palette, palette_rgbs)),
                key=lambda t: t[1],
            )
            if dist > args.threshold:
                issues.append(
                    f"dominant color {dominant} is ΔE {dist:.1f} from nearest palette {nearest_hex} (>{args.threshold})"
                )

    if len(strays) > args.max_strays:
        issues.append(
            f"{len(strays)} stray colors out of palette (max {args.max_strays}): "
            + ", ".join(f"{h}→{n}(ΔE{d:.1f})" for h, d, n in strays)
        )

    print(f"palette ({len(palette)}): {', '.join(palette)}")
    print(f"artifact top: {', '.join(artifact_hexes)}")
    if issues:
        for msg in issues:
            print(f"  ✗ {msg}")
        print(f"\nFAIL: {len(issues)} palette violation(s)")
        return 1
    print("OK: palette compliant")
    return 0


if __name__ == "__main__":
    sys.exit(main())
