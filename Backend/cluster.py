from matcher import similarity, normalize, extract_brand

SIMILARITY_THRESHOLD = 60  # Match products with 60% similarity or higher

def cluster_products(products: list[dict]) -> list[dict]:
    """
    Group products from multiple platforms into clusters.
    
    Strategy:
    1. Use Amazon as the primary source (always show Amazon products)
    2. For each Amazon product, find matching Snapdeal/Meesho products
    3. Return clusters with amazon_item, snapdeal_item, meesho_item fields
    4. Calculate best price and savings across platforms
    """
    
    if not products:
        return []
    
    # Separate products by platform
    amazon_products = [p for p in products if p.get("platform") == "Amazon"]
    snapdeal_products = [p for p in products if p.get("platform") == "Snapdeal"]
    meesho_products = [p for p in products if p.get("platform") == "Meesho"]
    
    # If no Amazon products, we can't cluster (Amazon is primary)
    if not amazon_products:
        print("[Cluster] Warning: No Amazon products found, returning empty clusters")
        return []
    
    clusters = []
    used_snapdeal = set()  # Track which Snapdeal products have been matched
    used_meesho = set()    # Track which Meesho products have been matched
    
    # Main loop: iterate through Amazon products (primary source)
    for amazon_item in amazon_products:
        amazon_title = amazon_item.get("title", "")
        amazon_normalized = normalize(amazon_title)
        amazon_brand = extract_brand(amazon_title)
        
        # Find best matching Snapdeal product
        snapdeal_match = None
        best_snapdeal_score = 0
        best_snapdeal_idx = -1
        
        for idx, snapdeal_item in enumerate(snapdeal_products):
            if idx in used_snapdeal:
                continue
            
            snapdeal_title = snapdeal_item.get("title", "")
            snapdeal_normalized = normalize(snapdeal_title)
            score = similarity(amazon_normalized, snapdeal_normalized)
            
            if score > best_snapdeal_score:
                best_snapdeal_score = score
                snapdeal_match = snapdeal_item
                best_snapdeal_idx = idx
        
        # Only use Snapdeal match if similarity is high enough
        if best_snapdeal_score < SIMILARITY_THRESHOLD:
            snapdeal_match = None
            best_snapdeal_idx = -1
        else:
            used_snapdeal.add(best_snapdeal_idx)
        
        # Find best matching Meesho product (optional, for future enhancement)
        meesho_match = None
        best_meesho_score = 0
        best_meesho_idx = -1
        
        for idx, meesho_item in enumerate(meesho_products):
            if idx in used_meesho:
                continue
            
            meesho_title = meesho_item.get("title", "")
            meesho_normalized = normalize(meesho_title)
            score = similarity(amazon_normalized, meesho_normalized)
            
            if score > best_meesho_score:
                best_meesho_score = score
                meesho_match = meesho_item
                best_meesho_idx = idx
        
        if best_meesho_score < SIMILARITY_THRESHOLD:
            meesho_match = None
            best_meesho_idx = -1
        else:
            used_meesho.add(best_meesho_idx)
        
        # Build the cluster
        cluster = build_cluster(
            amazon_item=amazon_item,
            snapdeal_item=snapdeal_match,
            meesho_item=meesho_match,
            amazon_normalized=amazon_normalized,
            snapdeal_score=best_snapdeal_score,
            meesho_score=best_meesho_score,
            brand=amazon_brand
        )
        
        clusters.append(cluster)
    
    print(f"[Cluster] Created {len(clusters)} clusters from {len(amazon_products)} Amazon products")
    return clusters


def build_cluster(
    amazon_item: dict,
    snapdeal_item: dict | None,
    meesho_item: dict | None,
    amazon_normalized: str,
    snapdeal_score: float,
    meesho_score: float,
    brand: str | None
) -> dict:
    """Build a single cluster object with all required fields for frontend."""
    
    # Collect all items in this cluster
    items = [amazon_item]
    if snapdeal_item:
        items.append(snapdeal_item)
    if meesho_item:
        items.append(meesho_item)
    
    # Determine platforms available
    platforms_available = ["Amazon"]
    if snapdeal_item:
        platforms_available.append("Snapdeal")
    if meesho_item:
        platforms_available.append("Meesho")
    
    # Find best price and best platform
    prices = [item.get("price", float("inf")) for item in items]
    best_price = min(prices)
    best_idx = prices.index(best_price)
    best_item = items[best_idx]
    best_platform = best_item.get("platform")
    
    # Calculate savings (if best is not Amazon)
    amazon_price = amazon_item.get("price", float("inf"))
    savings = 0
    savings_percent = 0
    
    if best_price < amazon_price and best_price > 0:
        savings = round(amazon_price - best_price, 2)
        savings_percent = round((savings / amazon_price) * 100, 1)
    
    # Generate cluster name from Amazon product title
    # (Just use the title, optionally shorten if too long)
    amazon_title = amazon_item.get("title", "Product")
    cluster_name = amazon_title[:100] if len(amazon_title) > 100 else amazon_title
    
    return {
        "cluster_name": cluster_name,
        "brand": brand,
        "platforms_available": platforms_available,
        "amazon_item": amazon_item,
        "snapdeal_item": snapdeal_item,
        "meesho_item": meesho_item,
        "items": items,
        "best_price": best_price,
        "best_platform": best_platform,
        "best_item": best_item,
        "savings": savings,
        "savings_percent": savings_percent,
        "snapdeal_match_score": snapdeal_score,
        "meesho_match_score": meesho_score,
    }
