#!/usr/bin/env bash
# scripts/check.sh — one-shot sanity check before defense / submission.
# Runs all repo health verifications and reports a single pass/fail.
#
# Usage:
#   bash scripts/check.sh         # normal: runs the 3 gates
#   bash scripts/check.sh --self  # also self-test verify_facts by injecting
#                                  a temporary fact drift and confirming it's
#                                  caught + auto-reverted

set -e
cd "$(dirname "$0")/.."

echo "═══ Vibe Design · Sanity Check ═══"
echo

fail=0

echo "─── 1/3 verify_facts: README / CHANGELOG / defense-qa cross-check ───"
if uv run python vibe-design/tools/verify_facts.py; then
  echo
else
  fail=1
  echo
fi

echo "─── 2/3 verify_demo_panel: PPT D-key panel link resolution ───"
if uv run python vibe-design/tools/verify_demo_panel.py; then
  echo
else
  fail=1
  echo
fi

echo "─── 3/3 git working tree clean? ───"
if [ -z "$(git status --porcelain)" ]; then
  echo "  ✓ working tree clean"
  echo
else
  echo "  ⚠ uncommitted changes:"
  git status --short | sed 's/^/    /'
  echo
  fail=1
fi

if [ "$1" = "--self" ]; then
  echo "─── self-test: inject artificial drift to README, confirm caught ───"
  cp README.md README.md.checktmp
  sed -i 's/7 次 demo run 已提交/9999 次 demo run 已提交/' README.md
  if uv run python vibe-design/tools/verify_facts.py 2>/dev/null | grep -q "claims 9999"; then
    echo "  ✓ verify_facts caught injected drift"
  else
    echo "  ⚠ verify_facts did NOT catch injected drift — gate is broken"
    fail=1
  fi
  mv README.md.checktmp README.md
  if uv run python vibe-design/tools/verify_facts.py 2>/dev/null | tail -1 | grep -q "OK"; then
    echo "  ✓ post-restore: verify_facts reports OK again"
  else
    echo "  ⚠ post-restore: verify_facts still reports issues"
    fail=1
  fi
  echo
fi

if [ $fail -eq 0 ]; then
  echo "═══ ALL OK · ready for defense ═══"
  exit 0
else
  echo "═══ FAIL · fix the issues above before defense ═══"
  exit 1
fi

