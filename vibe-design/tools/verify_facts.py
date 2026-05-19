"""verify_facts: cross-check fact claims in README / CHANGELOG / defense-qa.md
against the actual repo state.

Catches drift like:
- README says '5 demo runs' but there are actually 6 directories
- defense-qa says '2 Python tools' but there are 3 .py files
- README count of agents/skills mismatches actual file count

Designed to fail loudly before defense day. Run after any commit that
adds/removes demo runs, agents, skills, tools.

Usage:
    uv run python vibe-design/tools/verify_facts.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DOCS = [
    ROOT / "README.md",
    ROOT / "CHANGELOG.md",
    ROOT / "docs/defense-qa.md",
]


def actual() -> dict[str, int]:
    """Count what's actually in the repo right now."""
    return {
        "agents": len(list((ROOT / "vibe-design/.opencode/agent").glob("*.md"))),
        "skills": len(list((ROOT / "vibe-design/.opencode/skills").glob("*/SKILL.md"))),
        "commands": len(list((ROOT / "vibe-design/.opencode/command").glob("*.md"))),
        "tools": len(list((ROOT / "vibe-design/tools").glob("*.py"))),
        "demo_runs": len([d for d in (ROOT / "docs/demo-runs").iterdir() if d.is_dir()]),
        "examples": len(list((ROOT / "vibe-design/examples").glob("*.md"))),
    }


CLAIM_PATTERNS = [
    # (regex, doc_phrase, actual_key) — capture group 1 is the integer
    (r"(\d+)\s*个\s*agent", "X 个 agent", "agents"),
    (r"(\d+)\s*个\s*skill", "X 个 skill", "skills"),
    (r"(\d+)\s*个\s*命令", "X 个命令", "commands"),
    (r"(\d+)\s*个\s*Python\s*工具", "X 个 Python 工具", "tools"),
    (r"(\d+)\s*个\s*tools?", "X tool(s)", "tools"),
    (r"(\d+)\s*次\s*demo\s*run", "X 次 demo run", "demo_runs"),
    (r"(\d+)\s*次\s*完整", "X 次完整", "demo_runs"),
    (r"(\d+)\s*次\s*e2e", "X 次 e2e", "demo_runs"),
    (r"覆盖\s*(\d+)\s*个\s*领域", "X 个领域", None),  # informational only
]


def check_doc(path: Path, real: dict[str, int]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    for pattern, label, key in CLAIM_PATTERNS:
        if key is None:
            continue
        for m in re.finditer(pattern, text):
            # Skip claims wrapped in quotes — these are historical
            # snapshots being narrated, not present claims about the repo.
            # Look at the 4 chars before the match for a quote.
            before = text[max(0, m.start() - 4) : m.start()]
            if any(q in before for q in ("“", "「", '"', "'", "「")):
                continue
            claimed = int(m.group(1))
            actual_count = real[key]
            # report mismatches; allow exact match
            if claimed != actual_count:
                # find line for friendlier output
                line_no = text[: m.start()].count("\n") + 1
                snippet = text[max(0, m.start() - 30) : min(len(text), m.end() + 30)].replace("\n", " ")
                issues.append(
                    f"  {path.name}:{line_no}  '{label}' claims {claimed}, actual {actual_count}\n"
                    f"      … {snippet} …"
                )
    return issues


def main() -> int:
    real = actual()
    print(f"Actual repo state: {real}\n")

    all_issues: list[str] = []
    for doc in DOCS:
        if not doc.exists():
            print(f"  skip (missing): {doc.relative_to(ROOT)}")
            continue
        issues = check_doc(doc, real)
        if issues:
            all_issues.extend(issues)
            print(f"  ⚠ {doc.relative_to(ROOT)}  ({len(issues)} mismatches)")
            for i in issues:
                print(i)
        else:
            print(f"  ✓ {doc.relative_to(ROOT)}")

    print()
    if all_issues:
        print(f"FAIL: {len(all_issues)} fact drift(s) detected")
        return 1
    print("OK: all fact claims match repo state")
    return 0


if __name__ == "__main__":
    sys.exit(main())
