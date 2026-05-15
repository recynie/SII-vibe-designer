#!/usr/bin/env bash
# scripts/check.sh — one-shot sanity check before defense / submission.
# Runs all repo health verifications and reports a single pass/fail.
#
# Usage:
#   bash scripts/check.sh

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

if [ $fail -eq 0 ]; then
  echo "═══ ALL OK · ready for defense ═══"
  exit 0
else
  echo "═══ FAIL · fix the issues above before defense ═══"
  exit 1
fi
