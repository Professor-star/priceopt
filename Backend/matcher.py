import re
from rapidfuzz import fuzz

STOPWORDS = {
    "for", "and", "the", "with", "of", "in", "a", "an", "to",
    "men", "women", "boys", "girls", "unisex",
    "black", "white", "blue", "red", "green", "grey", "midnight",
    "starlight", "phantom", "bold",
    "gb", "tb", "5g", "4g", "wireless", "bluetooth",
}

KNOWN_BRANDS = [
    "nike", "adidas", "puma", "reebok", "new balance", "under armour",
    "apple", "samsung", "sony", "boat", "jbl", "bose",
    "oneplus", "realme", "xiaomi", "oppo", "vivo",
    "lg", "lenovo", "hp", "dell", "asus", "ptron", "campus",
    "zebbronics", "soundcore", "anker", "skullcandy", "sennheiser",
]

def normalize(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^a-z0-9\s]", " ", title)
    tokens = title.split()
    tokens = [t for t in tokens if t not in STOPWORDS]
    return " ".join(tokens)

def extract_brand(title: str) -> str | None:
    lower = title.lower()
    for brand in sorted(KNOWN_BRANDS, key=len, reverse=True):
        if brand in lower:
            return brand
    return None

def extract_key_specs(title: str) -> set:
    """
    Extract key product specifications from title.
    Examples: "sony wh-1000xm5", "boat rockers 450", "₹499"
    This helps match the same product across platforms.
    """
    title_lower = title.lower()
    specs = set()
    
    # Extract model numbers (e.g., WH-1000XM5, EHS64)
    model_numbers = re.findall(r'[a-z]+-?\d+[a-z]*', title_lower)
    specs.update(model_numbers)
    
    # Extract prices if mentioned
    prices = re.findall(r'₹?\d{3,}', title_lower)
    specs.update(prices)
    
    # Extract key product types
    product_types = ['wired', 'wireless', 'earbuds', 'headphones', 'earphones', 'neckband', 'over-ear', 'in-ear']
    for ptype in product_types:
        if ptype in title_lower:
            specs.add(ptype)
    
    return specs

def similarity(title1: str, title2: str) -> float:
    """
    Improved similarity matching with multiple checks.
    
    Returns a score from 0-100 based on:
    1. Brand match (must match for high confidence)
    2. Product type match (must have overlap)
    3. Text similarity (fuzzy matching)
    4. Key specs match
    """
    
    norm1 = normalize(title1)
    norm2 = normalize(title2)
    
    # Extract brands
    brand1 = extract_brand(title1)
    brand2 = extract_brand(title2)
    
    # Brand mismatch is a strong signal they're different products
    # UNLESS both are generic/no brand
    if brand1 and brand2 and brand1 != brand2:
        print(f"[Matcher DEBUG] Brand mismatch: {brand1} vs {brand2}")
        return 0  # Completely different brands = different products
    
    # Extract key specs
    specs1 = extract_key_specs(title1)
    specs2 = extract_key_specs(title2)
    
    # Check if specs overlap (model numbers, prices)
    spec_overlap = specs1.intersection(specs2)
    if specs1 and specs2 and not spec_overlap:
        # If both have specs but no overlap, likely different products
        print(f"[Matcher DEBUG] Spec mismatch: {specs1} vs {specs2}")
        pass  # Don't hard reject, but we'll lower the score
    
    # Calculate text similarity
    text_similarity = max(
        fuzz.token_sort_ratio(norm1, norm2),
        fuzz.partial_ratio(norm1, norm2),
        fuzz.token_set_ratio(norm1, norm2)
    )
    
    # If text similarity is very high but specs don't overlap, be cautious
    if spec_overlap:
        # Specs match — this is likely the same product
        return text_similarity
    elif text_similarity > 85:
        # Very high text similarity even without spec overlap
        return text_similarity * 0.9  # Slightly reduce confidence
    else:
        # Low text similarity — keep it low
        return text_similarity * 0.8  # Further reduce confidence

