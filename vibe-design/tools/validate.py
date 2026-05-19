"""validate: per-artifact machine review (font compliance only).

    uv run python tools/validate.py review <RUN_DIR> --artifact <path>
        Auto-routes by artifact extension:
            .html → check_html_fonts (mandatory)
            .png  → no machine visual checks (critic reads image directly)
            .md   → no machine checks (N/A)
        Prints a markdown block ready to paste into v?.review.md's
        "## 机器判定" section.

Exit codes:
    0 → all hard gates pass (fonts).
    1 → at least one hard gate fails.
    2 → file not found / usage error.

Designed so critic agent makes exactly one CLI call per artifact review.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import check_html_fonts


def cmd_review(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    artifact = Path(args.artifact)
    if not run_dir.is_dir():
        sys.stderr.write(f"run dir not found: {run_dir}\n")
        return 2
    if not artifact.is_file():
        sys.stderr.write(f"artifact not found: {artifact}\n")
        return 2

    spec = run_dir / "brand-spec.md"

    ext = artifact.suffix.lower()
    is_html = ext == ".html"
    is_image = ext == ".png"
    is_text = ext == ".md"

    fonts_passed: bool | None = None
    fonts_lines: list[str] = []
    if is_html:
        fonts_passed, fonts_lines, _ = check_html_fonts.check(artifact, spec)

    print("### 字族（HTML 类硬门槛 / 其它 N/A）")
    if is_html:
        status = "PASS" if fonts_passed else "FAIL"
        print(f"- check_html_fonts: {status}")
        for line in fonts_lines:
            print(f"  - {line}")
    else:
        reason = "纯位图（无 HTML）" if is_image else ("纯文（无 HTML）" if is_text else "N/A")
        print(f"- check_html_fonts: N/A ({reason})")
    print()

    hard_gate_pass = fonts_passed is None or fonts_passed
    print(f"**机器硬门槛结果：{'全过' if hard_gate_pass else '不通过'}**")
    print()

    return 0 if hard_gate_pass else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_rv = sub.add_parser("review", help="run per-artifact machine checks")
    p_rv.add_argument("run_dir")
    p_rv.add_argument("--artifact", required=True, help="artifact file (.png / .html / .md)")
    p_rv.set_defaults(func=cmd_review)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
