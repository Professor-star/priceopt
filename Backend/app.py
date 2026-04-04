"""
app.py — Flask REST API for the Product Price Optimiser (live data).
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS

from data import fetch_all_products
from cluster import cluster_products, ClusterResult
from matcher import extract_brand

app = Flask(__name__)
CORS(app)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "mode": "live"})


@app.route("/brands")
def brands():
    known = [
        "Apple", "Samsung", "Sony", "Nike", "Adidas",
        "Puma", "Boat", "OnePlus", "Realme", "Xiaomi",
        "JBL", "Bose", "HP", "Dell", "Lenovo",
    ]
    return jsonify(sorted(known))


@app.route("/search")
def search():
    query:        str = request.args.get("q", "").strip()
    sort:         str = request.args.get("sort", "price_asc").strip()
    brand_filter: str = request.args.get("brand", "").strip().lower()

    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    products = fetch_all_products(query)

    if brand_filter:
        products = [
            p for p in products
            if brand_filter in (extract_brand(p["title"]) or "").lower()
            or brand_filter in p["title"].lower()
        ]

    if not products:
        return jsonify({
            "query": query,
            "total_clusters": 0,
            "clusters": [],
            "message": "No products found.",
        })

    clusters: list[ClusterResult] = cluster_products(products)
    reverse = sort == "price_desc"
    clusters.sort(key=lambda c: c["best_price"], reverse=reverse)

    return jsonify({
        "query": query,
        "total_clusters": len(clusters),
        "clusters": [dict(c) for c in clusters],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
