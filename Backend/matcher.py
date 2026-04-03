"""
matcher.py — Text normalisation and fuzzy-similarity utilities.

Pipeline:
  raw title → lowercase → remove special chars → remove stopwords
            → extract brand → similarity score via rapidfuzz
"""

import re
from rapidfuzz import fuzz

# ── Stopwords ──────────────────────────────────────────────────────────────
STOPWORDS = {
    "for", "and", "the", "with", "of", "in", "a", "an", "to",
    "men", "women", "boys", "girls", "unisex",
    "black", "white", "blue", "red", "green", "grey", "midnight",
    "starlight", "phantom", "bold",
    "gb", "tb", "5g", "4g", "wireless", "bluetooth",
}

# ── Known brands (lowercase) ───────────────────────────────────────────────
KNOWN_BRANDS = [
    "nike", "adidas", "puma", "reebok", "new balance", "under armour",
    "apple", "samsung", "sony", "boat", "jbl", "bose",
    "oneplus", "realme", "xiaomi", "oppo", "vivo",
    "lg", "lenovo", "hp", "dell", "asus",
]


def normalize(title: str) -> str:
    """
    Normalize a product title for comparison.
    Steps: lowercase → strip special chars → remove stopwords.
    """
    title = title.lower()
    title = re.sub(r"[^a-z0-9\s]", " ", title)   # remove punctuation/hyphens
    tokens = title.split()
    tokens = [t for t in tokens if t not in STOPWORDS]
    return " ".join(tokens)


def extract_brand(title: str) -> str | None:
    """
    Return the first known brand found in the (lowercased) title, or None.
    Multi-word brands are checked before single-word brands.
    """
    lower = title.lower()
    # Sort by length descending so "new balance" beats "new"
    for brand in sorted(KNOWN_BRANDS, key=len, reverse=True):
        if brand in lower:
            return brand
    return None


def similarity(title1: str, title2: str) -> float:
    """
    Compute fuzzy similarity between two *already-normalized* titles.
    Uses token_sort_ratio so word order doesn't matter.
    Returns a float in [0, 100].
    """
    return fuzz.token_sort_ratio(title1, title2)
