"""Load and discover city source configs from cities/*/sources/*.yaml."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

CITIES_DIR = Path(__file__).resolve().parent.parent / "cities"


def discover_cities() -> list[str]:
    """Return sorted list of city slugs (directory names under cities/)."""
    if not CITIES_DIR.exists():
        return []
    return sorted(
        d.name for d in CITIES_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
    )


def load_source_config(city: str, filename: str) -> Optional[dict]:
    """Load a single source YAML. Returns None if file missing or invalid."""
    path = CITIES_DIR / city / "sources" / filename
    if not path.exists() or path.suffix not in (".yaml", ".yml"):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None
        return data
    except (yaml.YAMLError, OSError):
        return None


def load_sources_for_city(city: str) -> list[dict]:
    """Load all source configs for a city. Each dict has name, url, optional selector, optional adapter."""
    sources_dir = CITIES_DIR / city / "sources"
    if not sources_dir.exists() or not sources_dir.is_dir():
        return []
    configs = []
    for path in sorted(sources_dir.iterdir()):
        if path.suffix not in (".yaml", ".yml"):
            continue
        data = load_source_config(city, path.name)
        if data and data.get("name") and data.get("url"):
            configs.append(data)
    return configs


def load_all() -> dict[str, list[dict]]:
    """Return { city_slug: [ source_config, ... ] } for all cities."""
    return {city: load_sources_for_city(city) for city in discover_cities()}
