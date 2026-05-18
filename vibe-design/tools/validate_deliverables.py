"""validate_deliverables: enforce deliverables.md schema (see docs/schema/deliverables.schema.md).

Required sections (in order): 显式 / 隐式 / 拒绝 / 决策依据.

Row syntax:
  显式 / 隐式:  - <name> | mode: create|reuse | <spec>
  拒绝:        - <name> | <reason>
  决策依据:    - <free text>  (must have at least one bullet)

Usage:
    uv run python vibe-design/tools/validate_deliverables.py <path>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_ORDER = ["显式", "隐式", "拒绝", "决策依据"]
MAX_TOTAL_PRODUCTS = 5  # 显式 + 隐式 合计上限
MAX_IMPLICIT = 2  # 隐式上限
SECTION_RE = re.compile(r"^##\s+(\S.*)$")
PROD_ROW_RE = re.compile(r"^-\s+([^|]+?)\s*\|\s*mode:\s*(create|reuse)\s*\|\s*(.+?)\s*$")
REJECT_ROW_RE = re.compile(r"^-\s+([^|]+?)\s*\|\s*(.+?)\s*$")


def section_spans(lines: list[str]) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    current: tuple[str, int] | None = None
    for i, raw in enumerate(lines, start=1):
        m = SECTION_RE.match(raw)
        if m:
            if current is not None:
                spans.append((current[0], current[1], i - 1))
            current = (m.group(1).strip(), i + 1)
    if current is not None:
        spans.append((current[0], current[1], len(lines)))
    return spans


def validate(path: Path) -> list[str]:
    if not path.is_file():
        return [f"{path}: file not found"]
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    issues: list[str] = []

    if not lines or not lines[0].startswith("# Deliverables"):
        issues.append(f"{path}:1  first line must start with '# Deliverables'")

    spans = section_spans(lines)
    names_in_order = [s[0] for s in spans]
    for required in REQUIRED_ORDER:
        if required not in names_in_order:
            issues.append(f"{path}:1  missing section '## {required}'")

    if all(name in names_in_order for name in REQUIRED_ORDER):
        order_idx = [names_in_order.index(n) for n in REQUIRED_ORDER]
        if order_idx != sorted(order_idx):
            issues.append(
                f"{path}:1  sections must appear in order: 显式 → 隐式 → 拒绝 → 决策依据"
            )

    section_map: dict[str, tuple[int, int]] = {n: (s, e) for n, s, e in spans}
    seen_names: dict[str, int] = {}
    explicit_count = 0
    implicit_count = 0

    for sec in ("显式", "隐式"):
        if sec not in section_map:
            continue
        s, e = section_map[sec]
        rows = [(i, lines[i - 1]) for i in range(s, e + 1) if i - 1 < len(lines) and lines[i - 1].startswith("- ")]
        if sec == "显式" and len(rows) == 0:
            issues.append(f"{path}:{s}  section '## 显式' must have at least one row")
        if sec == "显式":
            explicit_count = len(rows)
        else:
            implicit_count = len(rows)
        for line_no, raw in rows:
            m = PROD_ROW_RE.match(raw)
            if not m:
                issues.append(
                    f"{path}:{line_no}  malformed row in '{sec}', expected "
                    f"'- <name> | mode: create|reuse | <spec>': {raw[:80]}"
                )
                continue
            name = m.group(1).strip()
            mode = m.group(2)
            spec = m.group(3).strip()
            if not spec:
                issues.append(f"{path}:{line_no}  spec is empty for '{name}'")
            if mode == "reuse" and "assets/" not in spec:
                issues.append(
                    f"{path}:{line_no}  reuse mode for '{name}' should reference an assets/ path in spec"
                )
            if name in seen_names:
                issues.append(
                    f"{path}:{line_no}  duplicate deliverable name '{name}' (also at line {seen_names[name]})"
                )
            else:
                seen_names[name] = line_no

    if implicit_count > MAX_IMPLICIT:
        issues.append(
            f"{path}:1  implicit deliverables exceed limit "
            f"({implicit_count} > {MAX_IMPLICIT}); move overflow to '## 拒绝'"
        )
    total = explicit_count + implicit_count
    if total > MAX_TOTAL_PRODUCTS:
        issues.append(
            f"{path}:1  total deliverables exceed limit "
            f"({total} > {MAX_TOTAL_PRODUCTS} = 显式 {explicit_count} + 隐式 {implicit_count}); "
            f"move secondary items to '## 拒绝' with reason"
        )

    if "拒绝" in section_map:
        s, e = section_map["拒绝"]
        for i in range(s, e + 1):
            if i - 1 >= len(lines):
                continue
            raw = lines[i - 1]
            if not raw.startswith("- "):
                continue
            if PROD_ROW_RE.match(raw):
                issues.append(
                    f"{path}:{i}  reject row should not carry 'mode:'; just '- <name> | <reason>'"
                )
                continue
            m = REJECT_ROW_RE.match(raw)
            if not m:
                issues.append(
                    f"{path}:{i}  malformed reject row, expected '- <name> | <reason>': {raw[:80]}"
                )
                continue
            if not m.group(2).strip():
                issues.append(f"{path}:{i}  reject reason is empty")

    if "决策依据" in section_map:
        s, e = section_map["决策依据"]
        bullets = [i for i in range(s, e + 1) if i - 1 < len(lines) and lines[i - 1].startswith("- ")]
        if not bullets:
            issues.append(f"{path}:{s}  '## 决策依据' must contain at least one '- ...' bullet")

    return issues


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write("usage: validate_deliverables.py <path>\n")
        return 2
    issues = validate(Path(sys.argv[1]))
    for msg in issues:
        print(msg)
    if issues:
        print(f"\nFAIL: {len(issues)} violation(s)")
        return 1
    print(f"OK: {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
