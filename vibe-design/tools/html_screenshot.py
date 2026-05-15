#!/usr/bin/env python3
"""html_screenshot: render a local HTML file to PNG for critic review.

Used by the designer agent after writing a poster/UI mockup HTML so the critic
can grade the rendered visual instead of guessing from source.

Usage:
    uv run python tools/html_screenshot.py \\
        --html outputs/run-x/artifacts/poster/v1.html \\
        --output outputs/run-x/artifacts/poster/v1.png \\
        [--width 1200] [--height 1600]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def find_chromium() -> str | None:
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        p = shutil.which(name)
        if p:
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--width", type=int, default=1200)
    ap.add_argument("--height", type=int, default=1600)
    args = ap.parse_args()

    html_path = Path(args.html).resolve()
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    chromium = find_chromium()
    if chromium:
        cmd = [
            chromium,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"--window-size={args.width},{args.height}",
            f"--screenshot={out_path}",
            f"file://{html_path}",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if out_path.exists() and out_path.stat().st_size > 0:
            print(str(out_path))
            return 0
        sys.stderr.write(
            f"chromium failed (rc={proc.returncode}): {proc.stderr[:400]}\n"
            "Falling back to playwright...\n"
        )

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.stderr.write(
            "No headless chromium found and playwright not installed.\n"
            "Install with:  uv add playwright && uv run playwright install chromium\n"
        )
        return 1

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": args.width, "height": args.height})
        page.goto(f"file://{html_path}")
        page.screenshot(path=str(out_path), full_page=True)
        browser.close()

    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
