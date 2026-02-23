"""Fetch URLs and extract status text using selector or named adapter."""
import re
import requests
from bs4 import BeautifulSoup

ADAPTERS = {}


def adapter(name: str):
    """Register a scraper adapter function."""

    def decorator(fn):
        ADAPTERS[name] = fn
        return fn

    return decorator


def fetch(url: str) -> str:
    """GET URL and return response text. Raises on failure."""
    resp = requests.get(url, timeout=30, headers={"User-Agent": "status-site-scraper/1.0"})
    resp.raise_for_status()
    return resp.text


def extract_with_selector(html: str, selector: str) -> str:
    """Extract text from first element matching CSS selector."""
    soup = BeautifulSoup(html, "html.parser")
    el = soup.select_one(selector)
    if not el:
        return "Unavailable"
    return el.get_text(separator=" ", strip=True) or "Unavailable"


def scrape_source(config: dict) -> str:
    """Scrape one source: fetch URL, apply adapter or selector, return status text."""
    url = config.get("url") or ""
    adapter_name = config.get("adapter")
    selector = config.get("selector")
    try:
        html = fetch(url)
    except Exception:
        return "Error fetching page"
    if adapter_name and adapter_name in ADAPTERS:
        try:
            return ADAPTERS[adapter_name](html) or "Unavailable"
        except Exception:
            return "Error parsing page"
    if selector:
        return extract_with_selector(html, selector)
    return "Unavailable"


# --- Adapter: Multnomah County wood burning ("Can I Burn Today?") ---


@adapter("multco-wood-burning")
def multco_wood_burning(html: str) -> str:
    """Extract the burn status under 'Can I Burn Today?' on multco.us."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["h2", "h3", "h4", "strong", "b"]):
        text = tag.get_text(strip=True)
        if "Can I Burn Today?" in text or "Can I burn today?" in text:
            # Next meaningful block: walk siblings or parent's next sibling
            parent = tag.parent
            if parent:
                parts = []
                for sib in parent.find_next_siblings():
                    t = sib.get_text(separator=" ", strip=True)
                    if t and len(t) > 10:
                        parts.append(t)
                        if len(parts) >= 2:
                            break
                if parts:
                    return " ".join(parts[:2])
            # Or the tag might wrap the heading; look for next element with status
            n = tag.find_next()
            while n:
                t = n.get_text(separator=" ", strip=True)
                if t and ("Restriction" in t or "burn" in t.lower() or "Limit" in t or "No " in t):
                    return t[:500]
                n = n.find_next() if hasattr(n, "find_next") else None
            break
    # Fallback: find any element containing "No Restrictions" or "Limit burning"
    for tag in soup.find_all(string=re.compile(r"(No Restrictions|Limit burning|burning restriction)", re.I)):
        parent = tag.parent if hasattr(tag, "parent") else None
        if parent:
            return parent.get_text(separator=" ", strip=True)[:500]
    return "Unavailable"


# --- Adapter: Portland Big Pipe (CSO advisories) ---


@adapter("portland-big-pipe")
def portland_big_pipe(html: str) -> str:
    """Extract CSO advisory status: no advisories vs overflow advisory."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    # "Current CSO Advisories:" followed by "There are no current advisories" or advisory text
    if "Current CSO Advisories" in text or "CSO Advisories" in text:
        if "no current advisories" in text.lower() or "there are no current advisories" in text.lower():
            return "No current advisories. Big Pipe has not overflowed."
        # Look for advisory text (e.g. "CSO Advisory: ...")
        for line in text.split("."):
            if "advisory" in line.lower() and "overflow" in line.lower():
                return line.strip() + "."
            if "CSO" in line and "advisory" in line.lower():
                return line.strip() + "."
        return "Check site for current advisory status."
    return "Unavailable"
