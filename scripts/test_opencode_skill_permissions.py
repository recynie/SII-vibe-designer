#!/usr/bin/env python3
"""Verify per-agent opencode skill permissions.

This test is intentionally config-level and does not call any LLM API. It asks
opencode for each resolved agent config, then applies opencode's permission
precedence rule: the last matching rule wins.

Run from the repository root:

    python3 scripts/test_opencode_skill_permissions.py
"""

from __future__ import annotations

import fnmatch
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "vibe-design"
SKILLS_DIR = PROJECT / ".opencode" / "skills"

EXPECTED_ALLOWED = {
    "planner": set(),
    "researcher": set(),
    "designer": {"craft", "logo", "poster", "ui-mockup", "copywriting"},
    "critic": {"craft", "copywriting"},
}


def discover_project_skills() -> set[str]:
    skills: set[str] = set()
    for skill_md in SKILLS_DIR.glob("*/SKILL.md"):
        name: str | None = None
        in_frontmatter = False
        for line in skill_md.read_text(encoding="utf-8").splitlines():
            if line.strip() == "---":
                if in_frontmatter:
                    break
                in_frontmatter = True
                continue
            if in_frontmatter and line.startswith("name:"):
                name = line.split(":", 1)[1].strip()
                break
        skills.add(name or skill_md.parent.name)
    return skills


def resolved_agent(agent: str) -> dict:
    proc = subprocess.run(
        ["opencode", "--pure", "debug", "agent", agent],
        cwd=PROJECT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"opencode debug agent {agent!r} failed with exit {proc.returncode}\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return json.loads(proc.stdout)


def effective_skill_action(permission_rules: list[dict], skill_name: str) -> str:
    """Return effective action for skill_name using opencode's last-match rule."""
    matched: str | None = None
    for rule in permission_rules:
        if rule.get("permission") != "skill":
            continue
        pattern = rule.get("pattern", "*")
        if fnmatch.fnmatchcase(skill_name, pattern):
            matched = rule.get("action", "ask")
    return matched or "ask"


def main() -> int:
    skills = discover_project_skills()
    if not skills:
        print(f"FAIL: no project skills discovered under {SKILLS_DIR}", file=sys.stderr)
        return 1

    failures: list[str] = []
    print(f"Project skills: {', '.join(sorted(skills))}\n")

    for agent, expected_allowed in EXPECTED_ALLOWED.items():
        info = resolved_agent(agent)
        permissions = info.get("permission", [])
        actual_allowed = {
            skill for skill in skills if effective_skill_action(permissions, skill) == "allow"
        }
        denied_or_asked = skills - actual_allowed

        print(f"[{agent}]")
        print(f"  allowed: {', '.join(sorted(actual_allowed)) or '(none)'}")
        print(f"  blocked: {', '.join(sorted(denied_or_asked)) or '(none)'}")

        if actual_allowed != expected_allowed:
            failures.append(
                f"{agent}: expected allowed {sorted(expected_allowed)}, got {sorted(actual_allowed)}"
            )

    if failures:
        print("\nFAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nPASS: per-agent skill permissions match the expected matrix.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
