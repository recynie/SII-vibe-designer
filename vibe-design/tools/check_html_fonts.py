"""check_html_fonts: verify HTML artifacts use only font families declared in brand-spec.md `## 字体`.

Parses every `font-family: ...;` declaration and any `<link href="...fonts.googleapis.com..."`
import in the HTML. Each family name found must intersect (case-insensitive,
whitespace-tolerant) the spec's font list. Generic fallbacks (`serif`, `sans-serif`,
`monospace`, `system-ui`, `ui-serif`, `ui-sans-serif`, `ui-monospace`) are always allowed.

Usage:
    uv run python vibe-design/tools/check_html_fonts.py --html <file> --spec <brand-spec.md>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

GENERIC = {
    "serif", "sans-serif", "monospace", "cursive", "fantasy",
    "system-ui", "ui-serif", "ui-sans-serif", "ui-monospace", "ui-rounded",
    "inherit", "initial", "unset",
}

FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;}\n]+)", re.IGNORECASE)
GOOGLE_FONTS_RE = re.compile(r"fonts\.googleapis\.com/css2?\?family=([^&'\")\s]+)")


def normalize(name: str) -> str:
    return name.strip().strip("'\"").replace("+", " ").lower()


def parse_spec_fonts(spec_path: Path) -> list[str]:
    text = spec_path.read_text(encoding="utf-8")
    in_section = False
    fonts: list[str] = []
    for raw in text.splitlines():
        if raw.startswith("## "):
            in_section = raw.strip().endswith("字体")
            continue
        if in_section and raw.startswith("- "):
            body = raw[2:]
            value = body.split(":", 1)[-1] if ":" in body else body
            value = re.sub(r"\[(?:from-fact|inferred):[^\]]*\]", "", value)
            for tok in re.split(r"[,/、]", value):
                tok = tok.strip().strip("'\"")
                tok = re.sub(r"\(.+?\)", "", tok)
                tok = tok.strip()
                if tok and tok.lower() not in GENERIC:
                    fonts.append(tok.lower())
    seen: list[str] = []
    for f in fonts:
        if f not in seen:
            seen.append(f)
    return seen


def fonts_in_html(html: str) -> set[str]:
    found: set[str] = set()
    for m in FONT_FAMILY_RE.finditer(html):
        for tok in m.group(1).split(","):
            n = normalize(tok)
            if n and n not in GENERIC:
                found.add(n)
    for m in GOOGLE_FONTS_RE.finditer(html):
        for fam in m.group(1).split("|"):
            base = fam.split(":", 1)[0]
            n = normalize(base)
            if n and n not in GENERIC:
                found.add(n)
    return found


def matches_any(used: str, allowed: list[str]) -> bool:
    used_norm = used.lower()
    for a in allowed:
        a_norm = a.lower()
        if used_norm == a_norm:
            return True
        if used_norm in a_norm or a_norm in used_norm:
            return True
    return False


def check(html_path: Path, spec_path: Path) -> tuple[bool, list[str], dict]:
    """Run the font check and return (passed, summary_lines, raw_data).

    summary_lines mirror the human-readable stdout main() prints.
    raw_data exposes parsed details for callers that want to render their own.
    """
    if not html_path.is_file():
        return False, [f"html not found: {html_path}"], {"error": "html_not_found"}
    if not spec_path.is_file():
        return False, [f"spec not found: {spec_path}"], {"error": "spec_not_found"}

    allowed = parse_spec_fonts(spec_path)
    if not allowed:
        return False, [f"no fonts parsed from {spec_path} 字体 section"], {
            "allowed": [], "used": [], "bad": [],
        }

    html = html_path.read_text(encoding="utf-8")
    used = sorted(fonts_in_html(html))
    bad = [u for u in used if not matches_any(u, allowed)]

    lines = [
        f"spec fonts: {', '.join(allowed)}",
        f"html uses:  {', '.join(used) or '(none)'}",
    ]
    if bad:
        for u in bad:
            lines.append(f"  ✗ '{u}' not in spec 字体")
        lines.append(f"FAIL: {len(bad)} font(s) outside spec")
        return False, lines, {"allowed": allowed, "used": used, "bad": bad}
    lines.append("OK: html fonts comply with spec")
    return True, lines, {"allowed": allowed, "used": used, "bad": []}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()

    passed, lines, data = check(Path(args.html), Path(args.spec))
    if data.get("error") == "html_not_found":
        sys.stderr.write(lines[0] + "\n")
        return 2
    if data.get("error") == "spec_not_found":
        sys.stderr.write(lines[0] + "\n")
        return 2

    for line in lines:
        print(line)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
