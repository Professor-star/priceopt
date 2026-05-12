from matcher import normalize, extract_brand

def cluster_products(products: list[dict]) -> list[dict]:
    """
    Create product clusters from Amazon products.
    Currently Amazon-only due to scraper limitations.
    """
    
    print(f"[Cluster] Processing {len(products)} Amazon products")
    
    if not products:
        return []
    
    clusters = []
    
    for idx, product in enumerate(products):
        try:
            title = product.get("title", "")
            if not title:
                continue
            
            normalized = normalize(title)
            brand = extract_brand(title)
            
            cluster = {
                "cluster_name": title[:100],
                "brand": brand,
                "platforms_available": ["Amazon"],
                "amazon_item": product,
                "snapdeal_item": None,
                "meesho_item": None,
                "items": [product],
                "best_price": product.get("price", 0),
                "best_platform": "Amazon",
                "best_item": product,
                "savings": 0,
                "savings_percent": 0,
                "snapdeal_match_score": 0,
                "meesho_match_score": 0,
            }
            
            clusters.append(cluster)
            
        except Exception as e:
            print(f"[Cluster ERROR] {e}")
            continue
    
    print(f"[Cluster] Created {len(clusters)} clusters")
    return clusters
