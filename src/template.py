"""HTML templates: city page and index. Simple white, Apple-like theme."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_city_page(city_name: str, city_slug: str, sources: list[dict]) -> str:
    """Render one city's status page. sources = [ { name, status, url? }, ... ]."""
    t = _env.get_template("city.html")
    return t.render(city_name=city_name, city_slug=city_slug, sources=sources)


def render_index(cities: list[tuple[str, str]]) -> str:
    """Render root index. cities = [ (slug, display_name), ... ]."""
    t = _env.get_template("index.html")
    return t.render(cities=cities)
