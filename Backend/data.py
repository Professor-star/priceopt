"""
data.py — Live product fetcher.
Amazon  → RapidAPI "Real-Time Amazon Data"
Flipkart → RapidAPI "Real-Time Flipkart Data" (/product-search endpoint)
"""

import requests

RAPIDAPI_KEY = "d265579416mshbf2b42ba49a784ap1fa184jsn40d0859896a6"

AMAZON_HEADERS = {
    "x-rapidapi-key":  RAPIDAPI_KEY,
    "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com",
}

FLIPKART_HEADERS = {
    "x-rapidapi-key":  RAPIDAPI_KEY,
    "x-rapidapi-host": "real-time-flipkart-data2.p.rapidapi.com",
}


def fetch_amazon(query: str, max_results: int = 8) -> list[dict]:
    """Fetch real Amazon.in products via RapidAPI."""
    try:
        r = requests.get(
            "https://real-time-amazon-data.p.rapidapi.com/search",
            headers=AMAZON_HEADERS,
            params={"query": query, "country": "IN", "page": "1"},
            timeout=10,
        )
        r.raise_for_status()
        items = r.json().get("data", {}).get("products", [])
    except Exception as e:
        print(f"[Amazon error] {e}")
        return []

    products = []
    for item in items[:max_results]:
        try:
            raw = item.get("product_price") or item.get("product_original_price") or "0"
            price = float(raw.replace("₹", "").replace(",", "").strip() or 0)
            if price <= 0:
                continue
            products.append({
                "title":    item.get("product_title", "Unknown"),
                "price":    price,
                "platform": "Amazon",
                "rating":   round(float(item.get("product_star_rating") or 0), 1),
                "link":     item.get("product_url", "https://amazon.in"),
            })
        except:
            continue

    print(f"[Amazon] {len(products)} products for '{query}'")
    return products


def fetch_flipkart(query: str, max_results: int = 8) -> list[dict]:
    """Fetch real Flipkart products via RapidAPI /product-search endpoint."""
    try:
        r = requests.get(
            "https://real-time-flipkart-data2.p.rapidapi.com/product-search",
            headers=FLIPKART_HEADERS,
            params={"q": query, "page": "1", "sort_by": "RELEVANCE"},
            timeout=10,
        )
        print(f"[Flipkart] status: {r.status_code}")
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[Flipkart error] {e}")
        return []

    # Print keys to debug response structure
    print(f"[Flipkart] response keys: {list(data.keys())}")

    # Try all possible response structures
    items = (
        data.get("products") or
        data.get("data", {}).get("products", []) if isinstance(data.get("data"), dict) else [] or
        data.get("results") or
        data.get("items") or
        []
    )

    if not items:
        print(f"[Flipkart] raw sample: {str(data)[:400]}")
        return []

    products = []
    for item in items[:max_results]:
        try:
            title = (
                item.get("title") or item.get("name") or
                item.get("productName") or item.get("product_title") or ""
            )
            if not title or len(title) < 5:
                continue

            raw = (
                item.get("price") or item.get("currentPrice") or
                item.get("discountedPrice") or item.get("mrp") or
                item.get("selling_price") or item.get("finalPrice") or "0"
            )
            price = float(str(raw).replace("₹", "").replace(",", "").strip() or 0)
            if price <= 0:
                continue

            raw_r = item.get("rating") or item.get("averageRating") or item.get("productRating") or 4.0
            rating = float(str(raw_r).split()[0] or 4.0)

            link = (
                item.get("url") or item.get("productUrl") or
                item.get("link") or item.get("product_url") or ""
            )
            if link and not link.startswith("http"):
                link = "https://www.flipkart.com" + link
            if not link:
                link = "https://www.flipkart.com"

            products.append({
                "title":    title,
                "price":    price,
                "platform": "Flipkart",
                "rating":   round(min(float(rating), 5.0), 1),
                "link":     link,
            })
        except:
            continue

    print(f"[Flipkart] {len(products)} products for '{query}'")
    return products


def fetch_all_products(query: str) -> list[dict]:
    amazon   = fetch_amazon(query)
    flipkart = fetch_flipkart(query)
    combined = amazon + flipkart
    if not combined:
        print("[Warning] Both failed — mock fallback")
        combined = [
            {"title": f"{query.title()} Product A", "price": 999.0, "platform": "Amazon",   "rating": 4.0, "link": "https://amazon.in"},
            {"title": f"{query.title()} Product B", "price": 899.0, "platform": "Flipkart", "rating": 3.9, "link": "https://www.flipkart.com"},
        ]
    return combined

PRODUCTS = []
