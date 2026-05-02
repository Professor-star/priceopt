"""
cluster.py — Strict cross-platform product matching for PriceOpt.

Algorithm
─────────
1. Separate products by platform.
2. For each Amazon product, find the best matching Snapdeal product
   using normalised title similarity + brand guard.
3. Only keep pairs where similarity >= STRICT_THRESHOLD.
4. Build a clean comparison result with one link per platform.
5. Single-platform products are discarded (no comparison possible).
"""

from __future__ import annotations
from typing import TypedDict
from matcher import normalize, extract_brand, similarity

# Strict threshold — only match if truly similar
STRICT_THRESHOLD = 55


class Product(TypedDict):
    title: str
    price: float
    platform: str
    rating: float
    link: str


class ClusterResult(TypedDict):
    cluster_name: str
    brand: str | None
    items: list[dict]
    best_platform: str
    best_price: float
    best_link: str
    best_rating: float
    platforms_available: list[str]
    amazon_item: dict | None
    snapdeal_item: dict | None
    savings: float
    savings_percent: float


def _enrich(product: Product) -> dict:
    """Attach normalised title and brand to a product dict copy."""
    p = dict(product)
    title_text = p.get("title", "")
    p["_norm"] = normalize(title_text)
    p["_brand"] = extract_brand(title_text)
    return p


def _make_item(p: dict) -> dict:
    """Build a clean item dict for the response."""
    return {
        "title":    p.get("title", "No Title"),
        "price":    p.get("price", 0),
        "platform": p.get("platform", "Unknown"),
        "rating":   p.get("rating", 0),
        "link":     p.get("link", "#"),
    }


def cluster_products(products: list[Product]) -> list[ClusterResult]:
    """
    Match Amazon products with Snapdeal products.
    Returns only cross-platform matched pairs.
    """
    enriched = [_enrich(p) for p in products]

    amazon   = [p for p in enriched if p.get("platform") == "Amazon"]
    snapdeal = [p for p in enriched if p.get("platform") == "Snapdeal"]
    meesho   = [p for p in enriched if p.get("platform") == "Meesho"]

    results: list[ClusterResult] = []
    used_snapdeal = set()
    used_meesho   = set()

    for amz in amazon:
        best_score   = 0.0
        best_sd      = None
        best_sd_idx  = -1

        # Find best matching Snapdeal product
        for idx, sd in enumerate(snapdeal):
            if idx in used_snapdeal:
                continue

            # Brand guard — skip if brands are known and conflict
            if (
                amz["_brand"] is not None
                and sd["_brand"] is not None
                and amz["_brand"] != sd["_brand"]
            ):
                continue

            score = similarity(amz["_norm"], sd["_norm"])
            if score >= STRICT_THRESHOLD and score > best_score:
                best_score  = score
                best_sd     = sd
                best_sd_idx = idx

        # Find best matching Meesho product
        best_mee     = None
        best_mee_idx = -1
        best_mee_score = 0.0

        for idx, mee in enumerate(meesho):
            if idx in used_meesho:
                continue

            if (
                amz["_brand"] is not None
                and mee["_brand"] is not None
                and amz["_brand"] != mee["_brand"]
            ):
                continue

            score = similarity(amz["_norm"], mee["_norm"])
            if score >= STRICT_THRESHOLD and score > best_mee_score:
                best_mee_score = score
                best_mee       = mee
                best_mee_idx   = idx

        # Only create a cluster if we matched at least one other platform
        if best_sd is None and best_mee is None:
            continue

        used_snapdeal.add(best_sd_idx) if best_sd_idx >= 0 else None
        used_meesho.add(best_mee_idx)  if best_mee_idx >= 0 else None

        # Build items list — Amazon first, then Snapdeal, then Meesho
        items = [_make_item(amz)]
        if best_sd:
            items.append(_make_item(best_sd))
        if best_mee:
            items.append(_make_item(best_mee))

        # Find best deal (lowest price)
        best = min(items, key=lambda x: x.get("price", float("inf")))
        worst = max(items, key=lambda x: x.get("price", float("inf")))

        savings = worst.get("price", 0) - best.get("price", 0)
        savings_pct = round((savings / worst["price"]) * 100) if worst.get("price", 0) > 0 else 0

        # Mark best deal in items
        for item in items:
            item["is_best_deal"] = (item is best)

        # Use Amazon title as cluster name (usually more detailed)
        cluster_name = amz.get("title", "Unknown Product")
        brand = amz.get("_brand") or (best_sd.get("_brand") if best_sd else None)

        platforms = [i["platform"] for i in items]

        results.append(ClusterResult(
            cluster_name      = cluster_name,
            brand             = brand,
            items             = items,
            best_platform     = best.get("platform", "Unknown"),
            best_price        = best.get("price", 0),
            best_link         = best.get("link", "#"),
            best_rating       = best.get("rating", 0),
            platforms_available = platforms,
            amazon_item       = _make_item(amz),
            snapdeal_item     = _make_item(best_sd) if best_sd else None,
            savings           = round(savings, 2),
            savings_percent   = savings_pct,
        ))

    return results


def filter_by_query(products: list[Product], query: str) -> list[Product]:
    """
    Return products whose normalised title contains at least one token
    from the normalised query.
    """
    norm_query   = normalize(query)
    query_tokens = set(norm_query.split())

    if not query_tokens:
        return products

    def matches(p: Product) -> bool:
        norm_title = normalize(p.get("title", ""))
        return any(token in norm_title for token in query_tokens)

    filtered = [p for p in products if matches(p)]
    return filtered if filtered else products
