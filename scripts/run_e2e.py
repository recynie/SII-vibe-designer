#!/usr/bin/env python3
"""
Vibe Design — End-to-End Test Runner
=====================================

Runs the full multi-agent design pipeline via ``opencode run --command design``
and reports results.

Key behavior:
  * Explicitly loads env vars from ``vibe-design/.env`` (opencode's ``run``
    sub-command does NOT auto-load ``.env`` files).
  * Streams opencode output in real-time using a PTY so Node.js doesn't
    line-buffer everything.
  * Prints progress heartbeats by scanning ``vibe-design/outputs/`` while
    opencode is quiet, so stalled runs are easy to diagnose.
  * On completion, locates the run directory under ``vibe-design/outputs/``,
    lists produced artefacts, and exits 0 only when ``final.md`` exists.

Usage examples::

    # inline brief
    uv run e2e-test --brief "请为创智学院做一套品牌形象设计"

    # brief from file (relative to repo root)
    uv run e2e-test --brief-file vibe-design/examples/brief-sii-academy.md

    # override model & idle timeout
    uv run e2e-test --brief-file vibe-design/examples/brief-coffee-startup.md \
        --model sii-openai/gpt-4.1 --idle-timeout 600
"""

from __future__ import annotations

import argparse
import errno
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# Resolve repo root regardless of cwd.  The script lives at <repo>/scripts/.
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
VIBE_DIR = REPO_ROOT / "vibe-design"
DOTENV_PATH = VIBE_DIR / ".env"
OPENCODE_JSON = VIBE_DIR / "opencode.json"
OUTPUTS_DIR = VIBE_DIR / "outputs"
PROGRESS_INTERVAL_SECONDS = 30
IDLE_TIMEOUT_SECONDS = 300  # kill if no output for 5 minutes
PROGRESS_ROOT_FILES = ("facts.md", "brand-spec.md", "deliverables.md", "plan.md", "final.md", "escalate.md")


# ---------------------------------------------------------------------------
# .env loader (no external deps)
# ---------------------------------------------------------------------------

def load_dotenv(path: Path) -> dict[str, str]:
    """Parse a simple .env file and return a dict of KEY=VALUE pairs.

    Supports:
      * ``KEY=VALUE``  /  ``KEY="VALUE"``  /  ``KEY='VALUE'``
      * ``export KEY=VALUE``
      * ``# comments`` and blank lines
    """
    env: dict[str, str] = {}
    if not path.is_file():
        return env
    with open(path) as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            # strip optional leading "export "
            if line.startswith("export "):
                line = line[len("export "):]
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # unquote
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            env[key] = value
    return env


# ---------------------------------------------------------------------------
# Default model from opencode.json
# ---------------------------------------------------------------------------

def default_model() -> str:
    """Read the default model identifier from opencode.json."""
    try:
        with open(OPENCODE_JSON) as fh:
            cfg = json.load(fh)
        return cfg.get("model", "sii-openai/gpt-5.5")
    except Exception:
        return "sii-openai/gpt-5.5"


def new_run_dirs(existing_runs: set[str]) -> list[Path]:
    """Return run directories created after this test started."""
    if not OUTPUTS_DIR.is_dir():
        return []
    return [
        d for d in OUTPUTS_DIR.iterdir()
        if d.is_dir() and d.name.startswith("run-") and d.name not in existing_runs
    ]


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


class ProgressReporter:
    """Periodic, file-system based progress reporter for quiet opencode runs."""

    def __init__(self, existing_runs: set[str]) -> None:
        self.existing_runs = existing_runs
        self.started_at = time.monotonic()
        self.last_print_at = 0.0
        self.last_signature = ""

    def poll(self, *, force: bool = False) -> None:
        now = time.monotonic()
        if not force and now - self.last_print_at < PROGRESS_INTERVAL_SECONDS:
            return

        run_dir = self._current_run_dir()
        signature = self._signature(run_dir)
        if force and signature == self.last_signature and now - self.last_print_at < 1.0:
            return
        if not force and signature == self.last_signature and now - self.last_print_at < PROGRESS_INTERVAL_SECONDS:
            return

        self.last_print_at = now
        self.last_signature = signature
        self._print(run_dir, elapsed=int(now - self.started_at))

    def _current_run_dir(self) -> Path | None:
        candidates = new_run_dirs(self.existing_runs)
        if candidates:
            return max(candidates, key=lambda d: d.stat().st_mtime)
        return None

    def _signature(self, run_dir: Path | None) -> str:
        if run_dir is None:
            return "no-run"
        try:
            files = sorted(
                f"{f.relative_to(run_dir)}:{f.stat().st_size}:{int(f.stat().st_mtime)}"
                for f in run_dir.rglob("*")
                if f.is_file()
            )
        except OSError:
            return f"{run_dir}:scan-error"
        return "|".join(files)

    def _print(self, run_dir: Path | None, *, elapsed: int) -> None:
        print()
        if run_dir is None:
            print(f"⏱️  Progress +{elapsed}s — waiting for planner to create a run directory")
            sys.stdout.flush()
            return

        files = sorted((f for f in run_dir.rglob("*") if f.is_file()), key=lambda f: f.stat().st_mtime)
        present = {f.name for f in files if f.parent == run_dir}
        artifact_files = [f for f in files if "artifacts" in f.relative_to(run_dir).parts]
        reviews = [f for f in artifact_files if f.name.endswith(".review.md")]
        images = [f for f in artifact_files if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
        html = [f for f in artifact_files if f.suffix.lower() == ".html"]
        markdown = [f for f in artifact_files if f.suffix.lower() == ".md" and not f.name.endswith(".review.md")]

        print(f"⏱️  Progress +{elapsed}s — {self._stage(present, artifact_files, reviews)}")
        print(f"    Run      : {display_path(run_dir)}")
        print(f"    Upstream : {self._root_status(present)}")
        print(
            "    Artifacts: "
            f"{len(artifact_files)} files, {len(reviews)} reviews, "
            f"{len(images)} images, {len(html)} html, {len(markdown)} markdown"
        )
        if files:
            latest = ", ".join(str(f.relative_to(run_dir)) for f in files[-4:])
            print(f"    Latest   : {latest}")
        sys.stdout.flush()

    @staticmethod
    def _root_status(present: set[str]) -> str:
        return " · ".join(
            f"{name} {'✓' if name in present else '-'}"
            for name in PROGRESS_ROOT_FILES
        )

    @staticmethod
    def _stage(present: set[str], artifact_files: list[Path], reviews: list[Path]) -> str:
        if "final.md" in present:
            return "final.md produced"
        if reviews:
            return "designer/critic loop in progress"
        if artifact_files:
            return "designer artifacts appearing"
        if "plan.md" in present:
            return "plan written; waiting for designer/critic"
        if {"facts.md", "brand-spec.md", "deliverables.md"}.issubset(present):
            return "upstream files ready; waiting for validation/plan"
        if present.intersection({"facts.md", "brand-spec.md", "deliverables.md"}):
            return "researcher writing upstream files"
        return "run directory created; waiting for researcher output"


# ---------------------------------------------------------------------------
# PTY-based streaming subprocess
# ---------------------------------------------------------------------------

def run_with_pty(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    idle_timeout: int,
    progress: ProgressReporter | None = None,
) -> int:
    """Spawn *cmd* in a PTY so Node.js thinks it has a real terminal and
    flushes stdout eagerly.  Streams all output to the caller's stdout in
    real-time.  Returns the child exit code, or 124 on idle timeout.
    """
    try:
        import pty as _pty  # noqa: F401
        return _run_pty(cmd, cwd=cwd, env=env, idle_timeout=idle_timeout, progress=progress)
    except ImportError:
        return _run_plain(cmd, cwd=cwd, env=env, idle_timeout=idle_timeout)


def _run_pty(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    idle_timeout: int,
    progress: ProgressReporter | None,
) -> int:
    """PTY-based implementation (Linux / macOS)."""
    import pty

    master_fd, slave_fd = pty.openpty()

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=slave_fd,
        stderr=slave_fd,
    )
    os.close(slave_fd)

    last_output_at = time.monotonic()
    timed_out = False

    try:
        while True:
            idle_elapsed = time.monotonic() - last_output_at
            if idle_elapsed >= idle_timeout:
                timed_out = True
                break

            ready, _, _ = select.select([master_fd], [], [], 1.0)
            if ready:
                try:
                    data = os.read(master_fd, 4096)
                except OSError as exc:
                    if exc.errno == errno.EIO:
                        break
                    raise
                if not data:
                    break
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()
                last_output_at = time.monotonic()

            if progress:
                progress.poll()

            ret = proc.poll()
            if ret is not None:
                while True:
                    rd, _, _ = select.select([master_fd], [], [], 0.1)
                    if not rd:
                        break
                    try:
                        data = os.read(master_fd, 4096)
                    except OSError:
                        break
                    if not data:
                        break
                    sys.stdout.buffer.write(data)
                    sys.stdout.buffer.flush()
                break
    finally:
        os.close(master_fd)

    if progress:
        progress.poll(force=True)

    if timed_out:
        idle_min = idle_timeout // 60
        print(f"\n⏰  Idle timeout ({idle_min}min without output) – killing opencode.", file=sys.stderr)
        proc.kill()
        proc.wait()
        return 124

    if proc.poll() is None:
        proc.wait()

    return proc.returncode


def _run_plain(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    idle_timeout: int,
) -> int:
    """Fallback: plain subprocess (no PTY). Uses idle_timeout as a hard cap."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            timeout=idle_timeout,
        )
        return proc.returncode
    except subprocess.TimeoutExpired:
        idle_min = idle_timeout // 60
        print(f"\n⏰  Idle timeout ({idle_min}min) reached.", file=sys.stderr)
        return 124


# ---------------------------------------------------------------------------
# Summary printer
# ---------------------------------------------------------------------------

def print_summary(run_dir: Path | None, exit_code: int) -> None:
    """Print a human-readable summary of the run."""

    SEP = "─" * 60
    print(f"\n{SEP}")
    print("📋  E2E Run Summary")
    print(SEP)

    if run_dir is None:
        print("  Run directory : ⚠️  not found (no run-* dir in outputs/)")
        print(f"  opencode exit : {exit_code}")
        print(f"  Result        : ❌ FAIL")
        print(SEP)
        return

    try:
        display_path = str(run_dir.relative_to(REPO_ROOT))
    except ValueError:
        display_path = str(run_dir)
    print(f"  Run directory : {display_path}")
    print(f"  opencode exit : {exit_code}")

    # list files
    files = sorted(f.relative_to(run_dir) for f in run_dir.rglob("*") if f.is_file())
    print(f"  Files produced: {len(files)}")
    for f in files:
        size = (run_dir / f).stat().st_size
        marker = "  "
        if f.name == "final.md":
            marker = "✅"
        elif f.suffix in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
            marker = "🖼 "
        elif f.suffix == ".md":
            marker = "📄"
        elif f.suffix == ".html":
            marker = "🌐"
        print(f"    {marker} {f}  ({_human_size(size)})")

    has_final = any(f.name == "final.md" for f in files)
    if has_final:
        print(f"  Result        : ✅ PASS — final.md produced")
    else:
        print(f"  Result        : ❌ FAIL — final.md missing")

    print(SEP)


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="e2e-test",
        description=(
            "Vibe Design end-to-end test runner.\n\n"
            "Loads env vars from vibe-design/.env, invokes the full multi-agent\n"
            "design pipeline via `opencode run --command design`, streams output\n"
            "in real-time, and reports artefact summary on completion.\n\n"
            "Exit code 0 iff final.md was produced."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  uv run e2e-test --brief '请为创智学院做一套品牌形象设计'\n"
            "  uv run e2e-test --brief-file vibe-design/examples/brief-sii-academy.md\n"
            "  uv run e2e-test --brief-file vibe-design/examples/brief-coffee-startup.md "
            "--model sii-openai/gpt-4.1 --idle-timeout 600\n"
        ),
    )

    brief_group = p.add_mutually_exclusive_group(required=True)
    brief_group.add_argument(
        "--brief",
        type=str,
        help="Design brief text (inline).",
    )
    brief_group.add_argument(
        "--brief-file",
        type=str,
        metavar="PATH",
        help="Path to a file containing the design brief (e.g. vibe-design/examples/brief-sii-academy.md).",
    )

    p.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"Override the LLM model (provider/model). Default: from opencode.json ({default_model()}).",
    )
    p.add_argument(
        "--idle-timeout",
        type=int,
        default=None,
        metavar="SECS",
        help=f"Kill if no output for this many seconds (default: {IDLE_TIMEOUT_SECONDS}).",
    )
    p.add_argument(
        "--env-file",
        type=str,
        default=str(DOTENV_PATH),
        metavar="PATH",
        help=f"Path to .env file to load (default: {DOTENV_PATH.relative_to(REPO_ROOT)}).",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    # Ensure stdout/stderr can handle all Unicode (Chinese run-dir names, etc.)
    # without crashing on surrogates from filesystem paths.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(errors="replace")

    parser = build_parser()
    args = parser.parse_args(argv)

    # ---- resolve brief text ------------------------------------------------
    if args.brief_file:
        brief_path = Path(args.brief_file)
        if not brief_path.is_absolute():
            # resolve relative to cwd (typical: repo root)
            brief_path = Path.cwd() / brief_path
        if not brief_path.is_file():
            parser.error(f"Brief file not found: {brief_path}")
        brief_text = brief_path.read_text(encoding="utf-8").strip()
        if not brief_text:
            parser.error(f"Brief file is empty: {brief_path}")
    else:
        brief_text = args.brief.strip()
        if not brief_text:
            parser.error("--brief text must not be empty")

    # ---- load .env into a merged environment dict --------------------------
    env_path = Path(args.env_file)
    if not env_path.is_file():
        print(f"⚠️  Warning: env file not found at {env_path}", file=sys.stderr)
        dotenv_vars: dict[str, str] = {}
    else:
        dotenv_vars = load_dotenv(env_path)
        loaded_keys = ", ".join(sorted(dotenv_vars.keys()))
        print(f"🔑  Loaded env vars from {env_path.relative_to(REPO_ROOT)}: {loaded_keys}")

    child_env = {**os.environ, **dotenv_vars}

    # Force color output in opencode even through the PTY.  Remove NO_COLOR
    # first to avoid Bun's warning about conflicting color settings.
    child_env.pop("NO_COLOR", None)
    child_env.setdefault("FORCE_COLOR", "1")

    # opencode uses process.env.PWD to resolve its config directory, but
    # Popen(cwd=...) doesn't update PWD — fix it so opencode finds
    # vibe-design/.opencode/ (commands, agents, skills).
    child_env["PWD"] = str(VIBE_DIR)

    # ---- build the opencode command ----------------------------------------
    model = args.model or default_model()
    cmd = ["opencode", "run", "--command", "design", "--model", model, brief_text]

    idle_timeout = args.idle_timeout or IDLE_TIMEOUT_SECONDS

    print(f"🚀  Starting Vibe Design e2e run")
    print(f"    Model   : {model}")
    print(f"    Idle timeout: {idle_timeout}s ({idle_timeout // 60}min without output)")
    print(f"    Progress: every {PROGRESS_INTERVAL_SECONDS}s")
    print(f"    Brief   : {brief_text[:120]}{'…' if len(brief_text) > 120 else ''}")
    print(f"    CWD     : {VIBE_DIR}")
    print(f"    Command : {' '.join(cmd[:-1])} …")
    print()
    sys.stdout.flush()

    # record what run dirs exist before, so we can find the new one after
    existing_runs = set()
    if OUTPUTS_DIR.is_dir():
        existing_runs = {d.name for d in OUTPUTS_DIR.iterdir() if d.is_dir() and d.name.startswith("run-")}

    # ---- run ---------------------------------------------------------------
    progress = ProgressReporter(existing_runs)
    exit_code = run_with_pty(cmd, cwd=VIBE_DIR, env=child_env, idle_timeout=idle_timeout, progress=progress)

    # ---- find the new run directory ----------------------------------------
    run_dir: Path | None = None
    if OUTPUTS_DIR.is_dir():
        new_dirs = new_run_dirs(existing_runs)
        if new_dirs:
            # pick newest by mtime
            run_dir = max(new_dirs, key=lambda d: d.stat().st_mtime)

    # ---- summary -----------------------------------------------------------
    print_summary(run_dir, exit_code)

    # ---- exit code ---------------------------------------------------------
    has_final = False
    if run_dir:
        has_final = any(f.name == "final.md" for f in run_dir.rglob("*") if f.is_file())

    sys.exit(0 if has_final else 1)


if __name__ == "__main__":
    main()
