"""Verify all demo-panel links resolve to existing files.

Used as part of milestone-26 to ensure the index.html demo panel
points at real URLs that won't 404 during the defense.
"""

from __future__ import annotations

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

INDEX = Path("docs/presentation/index.html").resolve()
PRESENTATION_DIR = INDEX.parent


def main() -> int:
    if not INDEX.exists():
        print(f"Missing {INDEX}")
        return 1

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(f"file://{INDEX}")
        page.evaluate("openDemo()")
        page.wait_for_selector(".demo-panel", state="visible")

        # Collect all hrefs on demo cards
        hrefs = page.eval_on_selector_all(
            ".demo-grid a", "els => els.map(a => a.getAttribute('href'))"
        )
        browser.close()

    print(f"Found {len(hrefs)} demo links\n")
    bad = []
    for href in hrefs:
        target = (PRESENTATION_DIR / href).resolve()
        ok = target.exists()
        marker = "OK " if ok else "404"
        print(f"  [{marker}] {href}  →  {target.relative_to(Path.cwd()) if ok else target}")
        if not ok:
            bad.append(href)

    if bad:
        print(f"\nFAIL: {len(bad)} broken link(s)")
        return 1
    print(f"\nOK: all {len(hrefs)} demo links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
