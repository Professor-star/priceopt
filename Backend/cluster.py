from matcher import similarity, normalize, extract_brand

SIMILARITY_THRESHOLD = 70  # Raised back to 70 since we improved matcher logic

def cluster_products(products: list[dict]) -> list[dict]:
    """
    Group products from multiple platforms into clusters.
    Uses improved matching logic to avoid false positives.
    """
    
    print(f"[Cluster DEBUG] cluster_products() called with {len(products)} total products")
    
    if not products:
        print("[Cluster] No products provided to cluster")
        return []
    
    # Separate products by platform
    amazon_products = [p for p in products if p.get("platform") == "Amazon"]
    snapdeal_products = [p for p in products if p.get("platform") == "Snapdeal"]
    meesho_products = [p for p in products if p.get("platform") == "Meesho"]
    
    print(f"[Cluster DEBUG] Platform breakdown: Amazon={len(amazon_products)}, Snapdeal={len(snapdeal_products)}, Meesho={len(meesho_products)}")
    
    if not amazon_products:
        print("[Cluster] WARNING: No Amazon products found, returning empty clusters")
        return []
    
    clusters = []
    used_snapdeal = set()
    used_meesho = set()
    
    # Main loop: iterate through Amazon products (primary source)
    for idx, amazon_item in enumerate(amazon_products):
        try:
            amazon_title = amazon_item.get("title", "")
            if not amazon_title:
                print(f"[Cluster DEBUG] Amazon item {idx} has no title, skipping")
                continue
            
            amazon_normalized = normalize(amazon_title)
            amazon_brand = extract_brand(amazon_title)
            
            print(f"[Cluster DEBUG] Processing Amazon #{idx}: '{amazon_title[:60]}...'")
            print(f"[Cluster DEBUG]   Brand: {amazon_brand}, Normalized: '{amazon_normalized[:60]}...'")
            
            # Find best matching Snapdeal product
            snapdeal_match = None
            best_snapdeal_score = 0
            best_snapdeal_idx = -1
            
            if snapdeal_products:
                for sd_idx, snapdeal_item in enumerate(snapdeal_products):
                    if sd_idx in used_snapdeal:
                        continue
                    
                    snapdeal_title = snapdeal_item.get("title", "")
                    score = similarity(amazon_title, snapdeal_title)
                    
                    if score > best_snapdeal_score:
                        best_snapdeal_score = score
                        snapdeal_match = snapdeal_item
                        best_snapdeal_idx = sd_idx
                
                if best_snapdeal_score >= SIMILARITY_THRESHOLD:
                    used_snapdeal.add(best_snapdeal_idx)
                    print(f"[Cluster DEBUG]   ✓ Snapdeal match accepted (score: {best_snapdeal_score:.1f}%)")
                else:
                    snapdeal_match = None
                    print(f"[Cluster DEBUG]   ✗ Snapdeal best match below threshold (score: {best_snapdeal_score:.1f}% < {SIMILARITY_THRESHOLD}%)")
            
            # Find best matching Meesho product
            meesho_match = None
            best_meesho_score = 0
            best_meesho_idx = -1
            
            if meesho_products:
                for m_idx, meesho_item in enumerate(meesho_products):
                    if m_idx in used_meesho:
                        continue
                    
                    meesho_title = meesho_item.get("title", "")
                    score = similarity(amazon_title, meesho_title)
                    
                    if score > best_meesho_score:
                        best_meesho_score = score
                        meesho_match = meesho_item
                        best_meesho_idx = m_idx
                
                if best_meesho_score >= SIMILARITY_THRESHOLD:
                    used_meesho.add(best_meesho_idx)
                    print(f"[Cluster DEBUG]   ✓ Meesho match accepted (score: {best_meesho_score:.1f}%)")
                else:
                    meesho_match = None
                    print(f"[Cluster DEBUG]   ✗ Meesho best match below threshold (score: {best_meesho_score:.1f}% < {SIMILARITY_THRESHOLD}%)")
            
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
            print(f"[Cluster DEBUG] ✓ Cluster created\n")
            
        except Exception as e:
            print(f"[Cluster ERROR] Error processing Amazon product {idx}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"[Cluster] SUCCESS: Created {len(clusters)} clusters")
    print(f"[Cluster] Snapdeal: {len(used_snapdeal)} products matched")
    print(f"[Cluster] Meesho: {len(used_meesho)} products matched")
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
    """Build a single cluster object."""
    
    items = [amazon_item]
    if snapdeal_item:
        items.append(snapdeal_item)
    if meesho_item:
        items.append(meesho_item)
    
    platforms_available = ["Amazon"]
    if snapdeal_item:
        platforms_available.append("Snapdeal")
    if meesho_item:
        platforms_available.append("Meesho")
    
    prices = [item.get("price", float("inf")) for item in items]
    best_price = min(prices)
    best_idx = prices.index(best_price)
    best_item = items[best_idx]
    best_platform = best_item.get("platform")
    
    amazon_price = amazon_item.get("price", float("inf"))
    savings = 0
    savings_percent = 0
    
    if best_price < amazon_price and best_price > 0:
        savings = round(amazon_price - best_price, 2)
        savings_percent = round((savings / amazon_price) * 100, 1)
    
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
