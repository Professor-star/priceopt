import requests
from bs4 import BeautifulSoup
import time

SCRAPER_API_KEY = "a812003a764711a59ff5a7c81fe0e583"

def scraper_api_get(url: str, timeout: int = 15) -> requests.Response:
    """Make a request through ScraperAPI to bypass blocks."""
    try:
        response = requests.get("http://api.scraperapi.com", params={
            "api_key": SCRAPER_API_KEY,
            "url": url,
            "render": "false",
        }, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.Timeout:
        print(f"[ScraperAPI] Timeout on {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ScraperAPI] Error: {e}")
        return None

def get_snapdeal_data(query: str, max_results: int = 10) -> list[dict]:
    """Scrape Snapdeal for products."""
    url = f"https://www.snapdeal.com/search?keyword={query.replace(' ', '%20')}"
    
    try:
        print(f"[Snapdeal] Fetching: {url}")
        response = scraper_api_get(url)
        
        if not response:
            print(f"[Snapdeal] Failed to fetch - no response")
            return []
        
        if response.status_code != 200:
            print(f"[Snapdeal] HTTP {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        
        # Try multiple selectors for robustness
        items = (
            soup.find_all("div", {"class": lambda x: x and "product-tuple-listing" in x})
            or soup.find_all("div", {"class": lambda x: x and "productCardImg" in x if x else False})
            or soup.find_all("div", attrs={"data-productid": True})
        )
        
        print(f"[Snapdeal] Found {len(items)} product elements")
        
        for item in items[:max_results]:
            try:
                # Try to extract title
                title_tag = (
                    item.find("p", {"class": "product-title"})
                    or item.find("p", {"class": lambda x: x and "productTitle" in x if x else False})
                    or item.find("a", {"class": lambda x: x and "productCardImg" in x if x else False})
                )
                title = title_tag.get_text(strip=True) if title_tag else ""
                
                if not title or len(title) < 5:
                    continue
                
                # Try to extract price
                price_tag = (
                    item.find("span", {"class": "product-price"})
                    or item.find("span", {"class": lambda x: x and "discountedPriceText" in x if x else False})
                    or item.find("span", {"class": lambda x: x and "price" in x.lower() if x else False})
                )
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                price_clean = "".join(filter(lambda c: c.isdigit(), price_text))
                price = float(price_clean) if price_clean else 0.0
                
                if price <= 0:
                    continue
                
                # Try to extract rating
                rating = 4.0
                rating_tag = item.find("div", {"class": lambda x: x and "filled-stars" in x if x else False})
                if rating_tag and rating_tag.get("style"):
                    width = "".join(filter(str.isdigit, rating_tag.get("style", "")))
                    if width:
                        rating = round(int(width) / 20, 1)
                
                # Extract product link
                link_tag = item.find("a", {"class": lambda x: x and "productCardImg" in x if x else False})
                link = link_tag.get("href", url) if link_tag else url
                if link and not link.startswith("http"):
                    link = "https://www.snapdeal.com" + link
                
                results.append({
                    "title": title,
                    "price": price,
                    "platform": "Snapdeal",
                    "rating": min(rating, 5.0),
                    "link": link
                })
                
            except Exception as e:
                print(f"[Snapdeal] Error parsing item: {e}")
                continue
        
        print(f"[Snapdeal] Scraped {len(results)} products for '{query}'")
        return results
        
    except Exception as e:
        print(f"[Snapdeal] Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_meesho_data(query: str, max_results: int = 10) -> list[dict]:
    """Scrape Meesho for products."""
    url = f"https://www.meesho.com/search?q={query.replace(' ', '%20')}"
    
    try:
        print(f"[Meesho] Fetching: {url}")
        response = scraper_api_get(url)
        
        if not response:
            print(f"[Meesho] Failed to fetch - no response")
            return []
        
        if response.status_code != 200:
            print(f"[Meesho] HTTP {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        
        # Try multiple selectors for robustness
        items = (
            soup.find_all("div", {"class": lambda x: x and "ProductList__GridCol" in x if x else False})
            or soup.find_all("div", {"class": lambda x: x and "product-card" in x.lower() if x else False})
            or soup.find_all("div", attrs={"data-testid": "product-card"})
            or soup.find_all("div", {"class": lambda x: x and "productContainer" in x if x else False})
        )
        
        print(f"[Meesho] Found {len(items)} product elements")
        
        for item in items[:max_results]:
            try:
                # Try to extract title
                title_tag = (
                    item.find("p")
                    or item.find("h4")
                    or item.find("span", {"class": lambda x: x and "productTitle" in x if x else False})
                )
                title = title_tag.get_text(strip=True) if title_tag else ""
                
                if not title or len(title) < 5:
                    continue
                
                # Try to extract price
                price_tag = (
                    item.find("h5")
                    or item.find("span", {"class": lambda x: x and "price" in x.lower() if x else False})
                )
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                price_clean = "".join(filter(lambda c: c.isdigit(), price_text))
                price = float(price_clean) if price_clean else 0.0
                
                if price <= 0:
                    continue
                
                results.append({
                    "title": title,
                    "price": price,
                    "platform": "Meesho",
                    "rating": 4.0,
                    "link": url
                })
                
            except Exception as e:
                print(f"[Meesho] Error parsing item: {e}")
                continue
        
        print(f"[Meesho] Scraped {len(results)} products for '{query}'")
        return results
        
    except Exception as e:
        print(f"[Meesho] Error: {e}")
        import traceback
        traceback.print_exc()
        return []
