"""Build static site: scrape all sources, render HTML, write to docs/."""
from pathlib import Path

from .config import load_all
from .scrape import scrape_source
from . import template

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"


def slug_to_name(slug: str) -> str:
    """Turn city slug into display name (e.g. portland -> Portland)."""
    return slug.replace("-", " ").title()


def main() -> None:
    all_cities = load_all()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    cities_list: list[tuple[str, str]] = []

    for city_slug, source_configs in all_cities.items():
        if not source_configs:
            continue
        city_name = slug_to_name(city_slug)
        sources = []
        for cfg in source_configs:
            status = scrape_source(cfg)
            sources.append({
                "name": cfg.get("name", "Unknown"),
                "status": status,
                "url": cfg.get("url"),
            })
        html = template.render_city_page(city_name, city_slug, sources)
        out_dir = DOCS_DIR / city_slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        cities_list.append((city_slug, city_name))

    index_html = template.render_index(cities_list)
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")


if __name__ == "__main__":
    main()
