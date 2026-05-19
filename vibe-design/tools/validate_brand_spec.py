"""validate_brand_spec: enforce brand-spec.md schema (see docs/schema/brand-spec.schema.md).

Checks:
1. First line starts with `# Brand Spec`.
2. Sections `## 色板` `## 字体` `## 调性` all present.
3. Each `- <role>: <value>` bullet under 色板/字体 carries
   `[from-fact: ...]` or `[inferred: ...]` (skipped if value is single `-`).
4. `[from-fact: <fragment>]` references resolve in the sibling `facts.md`
   (passed via --facts; if omitted, only the tag presence is checked).
5. hex values in 色板 are `#XXX` or `#XXXXXX`.
6. If a 色板 row carries `[from-fact: <fragment>]` and that fragment in facts.md
   contains a 6-digit hex, the spec hex must equal it (case-insensitive).
7. All 5 palette roles (Primary/Secondary/Background/Ink/Accent) must be present with real values.

Usage:
    uv run python vibe-design/tools/validate_brand_spec.py <brand-spec.md> [--facts <facts.md>]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PALETTE_ROLES = ["Primary", "Secondary", "Background", "Ink", "Accent"]
HEX_RE = re.compile(r"#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})\b")
TAG_FROM_FACT = re.compile(r"\[from-fact:\s*([^\]]+?)\s*\]")
TAG_INFERRED = re.compile(r"\[inferred:\s*([^\]]+?)\s*\]")
SECTION_RE = re.compile(r"^##\s+(\S.*)$")
ROW_RE = re.compile(r"^- ([^:]+):\s*(.*)$")


def parse_sections(lines: list[str]) -> dict[str, list[tuple[int, str]]]:
    out: dict[str, list[tuple[int, str]]] = {}
    current: str | None = None
    for i, raw in enumerate(lines, start=1):
        m = SECTION_RE.match(raw)
        if m:
            current = m.group(1).strip()
            out.setdefault(current, [])
            continue
        if current is not None:
            out[current].append((i, raw))
    return out


def validate_row(role: str, value: str) -> list[str]:
    issues: list[str] = []
    if value.strip() == "-":
        return issues
    has_from = bool(TAG_FROM_FACT.search(value))
    has_inf = bool(TAG_INFERRED.search(value))
    if not (has_from or has_inf):
        issues.append(f"row '{role}' missing [from-fact: ...] or [inferred: ...] tag")
    return issues


def check_hex_match_with_facts(spec_value: str, facts_text: str) -> str | None:
    m_tag = TAG_FROM_FACT.search(spec_value)
    if not m_tag:
        return None
    fragment = m_tag.group(1).strip()
    if fragment not in facts_text:
        return f"[from-fact: {fragment}] not found in facts.md"
    spec_hex_m = HEX_RE.search(spec_value)
    if not spec_hex_m:
        return None
    spec_hex = spec_hex_m.group(0).lower()
    idx = facts_text.find(fragment)
    window = facts_text[max(0, idx - 80) : idx + len(fragment) + 80]
    fact_hex_matches = HEX_RE.findall(window)
    if not fact_hex_matches:
        return None
    fact_hexes = ["#" + h.lower() for h in fact_hex_matches]
    if len(spec_hex) == 7 and spec_hex not in fact_hexes:
        return (
            f"hex {spec_hex} disagrees with facts.md neighborhood of "
            f"'{fragment}' (saw {fact_hexes[0]})"
        )
    return None


def validate(spec_path: Path, facts_path: Path | None) -> list[str]:
    if not spec_path.is_file():
        return [f"{spec_path}: file not found"]
    text = spec_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    issues: list[str] = []

    if not lines or not lines[0].startswith("# Brand Spec"):
        issues.append(f"{spec_path}:1  first line must start with '# Brand Spec'")

    sections = parse_sections(lines)
    for required in ("色板", "字体", "调性"):
        if required not in sections:
            issues.append(f"{spec_path}:1  missing section '## {required}'")

    facts_text = facts_path.read_text(encoding="utf-8") if facts_path and facts_path.is_file() else ""

    palette_seen: dict[str, str] = {}
    for section_name in ("色板", "字体"):
        rows = sections.get(section_name, [])
        for line_no, raw in rows:
            if not raw.startswith("- "):
                continue
            m = ROW_RE.match(raw)
            if not m:
                issues.append(f"{spec_path}:{line_no}  malformed row, expected '- <role>: <value>'")
                continue
            role = m.group(1).strip()
            value = m.group(2).strip()
            for issue in validate_row(role, value):
                issues.append(f"{spec_path}:{line_no}  {issue}")
            if section_name == "色板":
                palette_seen[role] = value
                if value != "-" and not HEX_RE.search(value):
                    issues.append(f"{spec_path}:{line_no}  palette row '{role}' missing hex value")
                if facts_text:
                    msg = check_hex_match_with_facts(value, facts_text)
                    if msg:
                        issues.append(f"{spec_path}:{line_no}  {msg}")

    for role in PALETTE_ROLES:
        if role not in palette_seen or palette_seen.get(role, "").strip() == "-":
            issues.append(
                f"{spec_path}:1  palette role '{role}' missing or empty — all 5 roles must be filled"
            )

    return issues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="path to brand-spec.md")
    ap.add_argument("--facts", default=None, help="path to facts.md (for from-fact resolution)")
    args = ap.parse_args()

    spec_path = Path(args.spec)
    facts_path = Path(args.facts) if args.facts else None
    if facts_path is None:
        sibling = spec_path.parent / "facts.md"
        if sibling.is_file():
            facts_path = sibling

    issues = validate(spec_path, facts_path)
    for msg in issues:
        print(msg)
    if issues:
        print(f"\nFAIL: {len(issues)} violation(s)")
        return 1
    print(f"OK: {spec_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
