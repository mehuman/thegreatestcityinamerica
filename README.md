# Multi-City Status Website

A static site that scrapes external data sources (burn bans, CSO overflows, etc.) per city and publishes to GitHub Pages. Simple, white, quick-to-scan pages.

## Run the build locally

From the repo root:

```bash
pip install -r requirements.txt
python -m src.build
```

Output is written to `docs/`. Serve locally with any static server, e.g.:

```bash
python -m http.server 8000 --directory docs
```

Then open http://localhost:8000 .

## Adding a new city

1. Create a directory: `cities/<city-slug>/sources/`
2. Add at least one source config file (YAML) in `sources/`. Example:

```yaml
name: Display name for the source
url: https://example.com/status-page
adapter: optional-adapter-name   # or use selector: ".css-selector"
```

3. If the site needs custom parsing, add an **adapter** in `src/scrape.py` (decorated with `@adapter("name")`) and reference it in the YAML.

The build discovers cities by scanning `cities/*` and sources by scanning `cities/<city>/sources/*.yaml`.

## Adding a new data source

1. Add a new YAML file under `cities/<city>/sources/`, e.g. `cities/portland/sources/lights-out.yaml`.
2. Required keys: `name`, `url`.
3. Use `selector` for a simple CSS selector to the status element, or `adapter` for a named scraper (implemented in `src/scrape.py`).

Example:

```yaml
name: Lights out for migrating birds
url: https://example.org/bird-status
adapter: my-bird-adapter
```

## Deployment

The site is built and deployed via **GitHub Actions**:

- **Triggers**: On every push to `main`, and **once an hour** on a schedule.
- **Steps**: Checkout → Set up Python → Install dependencies → Run `python -m src.build` → Upload `docs/` as a GitHub Pages artifact → Deploy.

Configure the repo to use **GitHub Pages** from the “GitHub Actions” source (Settings → Pages → Source: GitHub Actions). No need to commit `docs/` to the repo; the workflow generates it and deploys it.

For a **project** site, the live URL is `https://<user>.github.io/<repo-name>/` (e.g. `https://mehuman.github.io/thegreatestcityinamerica/`). The workflow sets `BASE_URL` to the repo name so links to cities (e.g. Portland at `/thegreatestcityinamerica/portland/`) resolve correctly.

## Project layout

- `cities/<city>/sources/*.yaml` — One config file per data source
- `src/config.py` — Discover cities and load YAML configs
- `src/scrape.py` — Fetch URLs and extract status (selectors + adapters)
- `src/template.py` — Jinja2 rendering for city and index pages
- `src/build.py` — Entry point: scrape all, render, write `docs/`
- `docs/` — Generated static output (for GitHub Pages)
