"""validate_facts: enforce facts.md schema (see docs/schema/facts.schema.md).

Each `- ` bullet must end with one of:
    [source: <non-empty>]
    [asset: assets/<non-empty>]
    [asset: failed - <non-empty>]

Top of file requires `# Facts` header and `> 采集日期：YYYY-MM-DD` within first 5 lines.

Usage:
    uv run python vibe-design/tools/validate_facts.py <path-to-facts.md>

Exit 0 = compliant; non-zero = violations printed (one per offending line).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SOURCE_RE = re.compile(r"\[source:\s*([^\]]+?)\s*\]")
ASSET_OK_RE = re.compile(r"\[asset:\s*assets/([^\]\s][^\]]*?)\s*\]")
ASSET_FAIL_RE = re.compile(r"\[asset:\s*failed\s*-\s*([^\]]+?)\s*\]")
DATE_RE = re.compile(r"^>\s*采集日期[:：]\s*(\d{4}-\d{2}-\d{2})")
BARE_URL_RE = re.compile(r"(?<!\[source:\s)https?://\S+")


def validate(path: Path) -> list[str]:
    if not path.is_file():
        return [f"{path}: file not found"]
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    issues: list[str] = []

    if not lines or not lines[0].startswith("# Facts"):
        issues.append(f"{path}:1  first line must start with '# Facts'")

    if not any(DATE_RE.match(ln) for ln in lines[:5]):
        issues.append(
            f"{path}:1-5  missing '> 采集日期：YYYY-MM-DD' (must use full-width colon ：)"
        )

    for i, raw in enumerate(lines, start=1):
        if not raw.startswith("- "):
            continue
        body = raw[2:].strip()
        if not body:
            issues.append(f"{path}:{i}  empty bullet")
            continue

        has_source = bool(SOURCE_RE.search(raw))
        has_asset_ok = bool(ASSET_OK_RE.search(raw))
        has_asset_fail = bool(ASSET_FAIL_RE.search(raw))

        if not (has_source or has_asset_ok or has_asset_fail):
            issues.append(
                f"{path}:{i}  bullet missing required tag "
                f"([source: ...] | [asset: assets/...] | [asset: failed - ...]): {body[:60]}"
            )
            continue

        for m in re.finditer(r"\[source:([^\]]*)\]", raw):
            if not m.group(1).strip():
                issues.append(f"{path}:{i}  [source: ...] has empty value")

        for m in re.finditer(r"\[asset:\s*failed\s*-\s*([^\]]*)\]", raw):
            if not m.group(1).strip():
                issues.append(f"{path}:{i}  [asset: failed - ...] needs a non-empty reason")

        stripped = SOURCE_RE.sub("", raw)
        stripped = ASSET_OK_RE.sub("", stripped)
        stripped = ASSET_FAIL_RE.sub("", stripped)
        if BARE_URL_RE.search(stripped):
            issues.append(
                f"{path}:{i}  bare URL outside [source: ...]: {body[:80]}"
            )

    return issues


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write("usage: validate_facts.py <path-to-facts.md>\n")
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
