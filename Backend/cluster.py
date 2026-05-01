"""
cluster.py — Greedy product clustering using fuzzy similarity.

Algorithm
─────────
1. For each product compute its normalised title and brand.
2. Iterate products. For each, check existing cluster *representatives*.
3. If similarity(normalised_product, normalised_rep) >= THRESHOLD
   AND brands match (or both are None) → assign to that cluster.
4. Otherwise → start a new cluster.
5. After clustering, pick the best deal (lowest price, tie-break: rating).
"""

from __future__ import annotations
from typing import TypedDict
from matcher import normalize, extract_brand, similarity

# Minimum similarity score to join an existing cluster
SIMILARITY_THRESHOLD = 75


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


def _enrich(product: Product) -> dict:
    """Attach normalised title and brand to a product dict copy."""
    p = dict(product)
    
    # Use .get() to avoid KeyError if 'title' is missing
    title_text = p.get("title", "")
    
    p["_norm"] = normalize(title_text)
    p["_brand"] = extract_brand(title_text)
    return p


def cluster_products(products: list[Product]) -> list[ClusterResult]:
    """
    Group products into clusters and return cluster summaries.
    """
    enriched = [_enrich(p) for p in products]

    # Each cluster: {"rep": enriched_product, "members": [enriched_product, ...]}
    clusters: list[dict] = []

    for product in enriched:
        placed = False
        best_score = 0.0
        best_cluster_idx = -1

        # Find the most similar existing cluster
        for idx, cluster in enumerate(clusters):
            rep = cluster["rep"]

            # Brand guard: skip if brands are known and don't match
            if (
                product["_brand"] is not None
                and rep["_brand"] is not None
                and product["_brand"] != rep["_brand"]
            ):
                continue

            score = similarity(product["_norm"], rep["_norm"])
            if score >= SIMILARITY_THRESHOLD and score > best_score:
                best_score = score
                best_cluster_idx = idx

        if best_cluster_idx >= 0:
            clusters[best_cluster_idx]["members"].append(product)
            placed = True

        if not placed:
            clusters.append({"rep": product, "members": [product]})

    return [_summarise(c["members"]) for c in clusters]


def _summarise(members: list[dict]) -> ClusterResult:
    """
    Build a ClusterResult from a list of cluster members.
    Best deal = lowest price; tie-break by highest rating.
    """
    # Choose best deal
    best = min(members, key=lambda p: (p.get("price", float('inf')), -p.get("rating", 0)))

    # Choose the longest title as the display name for the group
    best_p = max(members, key=lambda p: len(p.get("title", "")))
    cluster_name = best_p.get("title", "Unknown Product")

    brand = next((p["_brand"] for p in members if p["_brand"]), None)

    # Fixed Indentation here (4 spaces)
    items = [
        {
            "title": p.get("title", "No Title"),
            "price": p.get("price", 0),
            "platform": p.get("platform", "Unknown"),
            "rating": p.get("rating", 0),
            "link": p.get("link", "#"),
            "is_best_deal": (p is best),
        }
        for p in members
    ]

    # Fixed Indentation here (4 spaces)
    return ClusterResult(
        cluster_name=cluster_name,
        brand=brand,
        items=items,
        best_platform=best.get("platform", "Unknown"),
        best_price=best.get("price", 0),
        best_link=best.get("link", "#"),
        best_rating=best.get("rating", 0),
        platforms_available=list({p.get("platform") for p in members if p.get("platform")}),
    )


def filter_by_query(products: list[Product], query: str) -> list[Product]:
    """
    Return products whose normalised title contains at least one token
    from the normalised query.  Handles both specific and category queries.
    """
    norm_query = normalize(query)
    query_tokens = set(norm_query.split())

    if not query_tokens:
        return products  # empty query → return all

    def matches(p: Product) -> bool:
        norm_title = normalize(p["title"])
        # Accept if any query token appears in the title
        return any(token in norm_title for token in query_tokens)

    filtered = [p for p in products if matches(p)]
    # Fall back to all products if nothing matched (broad search)
    return filtered if filtered else products
