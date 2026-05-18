"""api_config: shared loader for repo-wide API credentials.

Reads `api.toml` at repo root. All Python tools / scripts go through this
module — credentials never touch os.environ.

Schema (see api.toml.example for the canonical version):

    [active]
    llm   = "sii"      # which provider chat/test scripts use
    image = "openai"   # which provider gen_image uses

    [providers.<name>]
    key         = "sk-..."
    base_url    = "https://..."
    images_url  = "https://.../v1/images/generations"   # optional, openai-style
    edits_url   = "https://.../v1/images/edits"         # optional
    image_model = "gpt-image-2"                         # optional

Usage:
    from api_config import active_llm, active_image, get_provider

    p = active_llm()             # provider currently selected as [active].llm
    p = active_image()           # provider currently selected as [active].image
    p = get_provider("minimax")  # by name (when you need a specific one)

    p.name / p.key / p.base_url / p.images_url / p.image_model / ...

Public helpers raise SystemExit with a human message when something is
missing — scripts can let it propagate.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover — pyproject pins >=3.12
    import tomli as tomllib  # type: ignore[no-redef]


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOML_PATH = REPO_ROOT / "api.toml"


@dataclass(frozen=True)
class Provider:
    name: str
    key: str
    base_url: str
    images_url: Optional[str] = None
    edits_url: Optional[str] = None
    image_model: Optional[str] = None


_cache: dict | None = None


def load_config() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    if not TOML_PATH.is_file():
        raise SystemExit(
            f"No API config found. Copy api.toml.example -> {TOML_PATH} and fill keys."
        )
    with TOML_PATH.open("rb") as f:
        cfg = tomllib.load(f)
    cfg.setdefault("providers", {})
    cfg.setdefault("active", {})
    _cache = cfg
    return cfg


def get_provider(name: str) -> Provider:
    cfg = load_config()
    raw = cfg["providers"].get(name)
    if not raw:
        raise SystemExit(
            f"provider '{name}' not in {TOML_PATH} [providers]; "
            f"available: {sorted(cfg['providers'].keys())}"
        )
    if not raw.get("key") or "REPLACE" in str(raw["key"]):
        raise SystemExit(
            f"provider '{name}' has no real key (placeholder still in {TOML_PATH})"
        )
    if not raw.get("base_url"):
        raise SystemExit(f"provider '{name}' missing base_url")
    return Provider(
        name=name,
        key=raw["key"],
        base_url=str(raw["base_url"]).rstrip("/"),
        images_url=raw.get("images_url"),
        edits_url=raw.get("edits_url"),
        image_model=raw.get("image_model"),
    )


def _active(slot: str) -> Provider:
    cfg = load_config()
    name = cfg.get("active", {}).get(slot)
    if not name:
        raise SystemExit(
            f"[active].{slot} not set in {TOML_PATH}; pick one of "
            f"{sorted(cfg['providers'].keys())}"
        )
    return get_provider(name)


def active_llm() -> Provider:
    """Provider currently selected as [active].llm (chat / test scripts)."""
    return _active("llm")


def active_image() -> Provider:
    """Provider currently selected as [active].image (gen_image)."""
    return _active("image")


def active_image_backend() -> str:
    """Just the name string — useful for `# backend: <name>` annotations."""
    return active_image().name


__all__ = [
    "Provider",
    "load_config",
    "get_provider",
    "active_llm",
    "active_image",
    "active_image_backend",
    "TOML_PATH",
]
