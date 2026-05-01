"""
scrapers.py — Web scrapers for Meesho and Snapdeal.
Uses BeautifulSoup with realistic browser headers to avoid bot detection.
Returns data in the standard product dict format:
  { title, price, platform, rating, link }
"""

import requests
from bs4 import BeautifulSoup

# ── Shared browser-like headers ────────────────────────────────────────────
BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def get_meesho_data(query: str, max_results: int = 5) -> list[dict]:
    """
    Scrape Meesho search results.
    Returns list of standard product dicts.
    """
    url = f"https://www.meesho.com/search?q={query.replace(' ', '%20')}"
    headers = {**BASE_HEADERS, "Referer": "https://www.meesho.com/"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        # Try multiple selectors — Meesho changes their CSS classes frequently
        items = (
            soup.find_all("div", {"class": lambda x: x and "ProductList__GridCol" in x})
            or soup.find_all("div", {"class": lambda x: x and "product-card" in x.lower() if x else False})
            or soup.find_all("div", attrs={"data-testid": "product-card"})
        )

        for item in items[:max_results]:
            try:
                # Title — Meesho uses <p> tags for product names
                title_tag = item.find("p") or item.find("h4") or item.find("span")
                title = title_tag.get_text(strip=True) if title_tag else ""
                if not title or len(title) < 5:
                    continue

                # Price — Meesho uses <h5> for price
                price_tag = item.find("h5") or item.find("span", {"class": lambda x: x and "price" in x.lower() if x else False})
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                price = float("".join(filter(lambda c: c.isdigit() or c == ".", price_text)) or 0)
                if price <= 0:
                    continue

                results.append({
                    "title":    title,
                    "price":    price,
                    "platform": "Meesho",
                    "rating":   4.0,          # Meesho doesn't show ratings in search
                    "link":     url,
                })
            except Exception:
                continue

        print(f"[Meesho] scraped {len(results)} products for '{query}'")
        return results

    except Exception as e:
        print(f"[Meesho error] {e}")
        return []


def get_snapdeal_data(query: str, max_results: int = 5) -> list[dict]:
    """
    Scrape Snapdeal search results.
    Returns list of standard product dicts.
    """
    url = f"https://www.snapdeal.com/search?keyword={query.replace(' ', '%20')}"
    headers = {**BASE_HEADERS, "Referer": "https://www.snapdeal.com/"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        # Standard Snapdeal product container
        items = soup.find_all("div", {"class": "product-tuple-listing"})

        for item in items[:max_results]:
            try:
                # Title
                title_tag = item.find("p", {"class": "product-title"})
                title = title_tag.get_text(strip=True) if title_tag else ""
                if not title or len(title) < 5:
                    continue

                # Price
                price_tag = item.find("span", {"class": "product-price"})
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                price = float("".join(filter(lambda c: c.isdigit() or c == ".", price_text)) or 0)
                if price <= 0:
                    continue

                # Rating
                rating_tag = item.find("div", {"class": "filled-stars"})
                rating = 4.0  # Default if not found
                if rating_tag and rating_tag.get("style"):
                    # Snapdeal uses width % to show rating e.g. "width:80%" = 4 stars
                    style = rating_tag.get("style", "")
                    width = "".join(filter(str.isdigit, style))
                    if width:
                        rating = round(int(width) / 20, 1)  # Convert % to 5-star scale

                # Link
                link_tag = item.find("a", {"class": "dp-widget-link"})
                link = link_tag["href"] if link_tag and link_tag.get("href") else url
                if link and not link.startswith("http"):
                    link = "https://www.snapdeal.com" + link

                results.append({
                    "title":    title,
                    "price":    price,
                    "platform": "Snapdeal",
                    "rating":   min(rating, 5.0),
                    "link":     link,
                })
            except Exception:
                continue

        print(f"[Snapdeal] scraped {len(results)} products for '{query}'")
        return results

    except Exception as e:
        print(f"[Snapdeal error] {e}")
        return []
