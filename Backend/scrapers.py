"""
scrapers.py — Web scrapers for Meesho and Snapdeal.
Uses ScraperAPI to bypass bot detection on cloud servers.
Returns data in the standard product dict format:
  { title, price, platform, rating, link }
"""

import requests
from bs4 import BeautifulSoup

SCRAPER_API_KEY = "a812003a764711a59ff5a7c81fe0e583"

def scraper_api_get(url: str, timeout: int = 15) -> requests.Response:
    """
    Route any URL through ScraperAPI to bypass bot detection.
    """
    api_url = "http://api.scraperapi.com"
    params = {
        "api_key": SCRAPER_API_KEY,
        "url": url,
        "render": "false",
    }
    return requests.get(api_url, params=params, timeout=timeout)


def get_meesho_data(query: str, max_results: int = 5) -> list[dict]:
    """
    Scrape Meesho search results via ScraperAPI.
    Returns list of standard product dicts.
    """
    url = f"https://www.meesho.com/search?q={query.replace(' ', '%20')}"

    try:
        response = scraper_api_get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        items = (
            soup.find_all("div", {"class": lambda x: x and "ProductList__GridCol" in x})
            or soup.find_all("div", {"class": lambda x: x and "product-card" in x.lower() if x else False})
            or soup.find_all("div", attrs={"data-testid": "product-card"})
        )

        for item in items[:max_results]:
            try:
                title_tag = item.find("p") or item.find("h4") or item.find("span")
                title = title_tag.get_text(strip=True) if title_tag else ""
                if not title or len(title) < 5:
                    continue

                price_tag = item.find("h5") or item.find("span", {"class": lambda x: x and "price" in x.lower() if x else False})
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                price = float("".join(filter(lambda c: c.isdigit() or c == ".", price_text)) or 0)
                if price <= 0:
                    continue

                results.append({
                    "title":    title,
                    "price":    price,
                    "platform": "Meesho",
                    "rating":   4.0,
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
    Scrape Snapdeal search results via ScraperAPI.
    Returns list of standard product dicts.
    """
    url = f"https://www.snapdeal.com/search?keyword={query.replace(' ', '%20')}"

    try:
        response = scraper_api_get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        items = soup.find_all("div", {"class": "product-tuple-listing"})

        for item in items[:max_results]:
            try:
                title_tag = item.find("p", {"class": "product-title"})
                title = title_tag.get_text(strip=True) if title_tag else ""
                if not title or len(title) < 5:
                    continue

                price_tag = item.find("span", {"class": "product-price"})
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                price_clean = "".join(filter(lambda c: c.isdigit(), price_text))
                price = float(price_clean) if price_clean else 0.0
                if price <= 0:
                    continue

                rating_tag = item.find("div", {"class": "filled-stars"})
                rating = 4.0
                if rating_tag and rating_tag.get("style"):
                    style = rating_tag.get("style", "")
                    width = "".join(filter(str.isdigit, style))
                    if width:
                        rating = round(int(width) / 20, 1)

                link_tag = item.find("a", {"class": "dp-widget-link"})
                link = link_tag.get("href", url) if link_tag else url
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
