import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from scrapers import get_meesho_data, get_snapdeal_data
from data import fetch_all_products
from cluster import cluster_products  # ← REMOVE ClusterResult from here
from matcher import extract_brand

app = Flask(__name__)
CORS(app)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "mode": "live", "platforms": ["Amazon", "Meesho", "Snapdeal"]})

@app.route("/brands")
def brands():
    known = ["Apple", "Samsung", "Sony", "Nike", "Adidas", "Puma", "Boat",
             "OnePlus", "Realme", "Xiaomi", "JBL", "Bose", "HP", "Dell", "Lenovo"]
    return jsonify(sorted(known))

@app.route("/search")
def search():
    query        = request.args.get("q", "").strip()
    sort         = request.args.get("sort", "price_asc").strip()
    brand_filter = request.args.get("brand", "").strip().lower()

    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    amazon_products   = fetch_all_products(query)
    meesho_products   = get_meesho_data(query)
    snapdeal_products = get_snapdeal_data(query)
    products = amazon_products + meesho_products + snapdeal_products

    print(f"[Search] '{query}' → Amazon:{len(amazon_products)} Meesho:{len(meesho_products)} Snapdeal:{len(snapdeal_products)}")

    if brand_filter:
        products = [p for p in products
                    if brand_filter in (extract_brand(p.get("title", "")) or "").lower()
                    or brand_filter in p.get("title", "").lower()]

    if not products:
        return jsonify({"query": query, "total_clusters": 0, "clusters": [], "message": "No products found."})

    clusters = cluster_products(products)
    reverse = sort == "price_desc"
    clusters.sort(key=lambda c: c.get("best_price", 0), reverse=reverse)

    return jsonify({"query": query, "total_clusters": len(clusters), "clusters": clusters})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
