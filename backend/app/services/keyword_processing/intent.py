from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

try:
    # Local agent enums (optional, for category-aware adjustments)
    from ...local_agents.keyword.schemas import KeywordCategory
except Exception:  # pragma: no cover - keep decoupled if import path differs in tests
    class KeywordCategory:  # type: ignore
        RELEVANT = "Relevant"
        DESIGN_SPECIFIC = "Design-Specific"
        IRRELEVANT = "Irrelevant"
        BRANDED = "Branded"
        SPANISH = "Spanish"
        OUTLIER = "Outlier"


@dataclass
class IntentResult:
    intent_score: int  # 0..3
    matched_aspects: List[str]
    debug: Optional[Dict] = None


# Lightweight lexicons for attributes and use-cases/benefits. Extend as needed per niche.
ATTRIBUTE_TOKENS: Set[str] = {
    # materials / build
    "stainless", "steel", "aluminum", "wood", "foam", "silicone", "plastic",
    # qualities
    "waterproof", "wipeable", "washable", "portable", "contoured", "non-slip", "anti-slip",
    "reusable", "disposable", "magnetic", "adjustable", "durable", "heavy-duty",
    # variations
    "pink", "blue", "black", "white", "silver", "gold", "xl", "large", "small",
    "mini", "travel", "compact", "with straps", "strap", "pack", "pack of",
}

USE_CASE_TOKENS: Set[str] = {
    "for",  # enables simple "for <target>" detection
    "newborn", "toddler", "kids", "baby", "nursery", "bath", "dresser", "diaper",
    "replacement", "refill", "car", "stroller", "crib", "changing", "table",
    "gift", "boy", "girl",
}

COMMERCIAL_INTENT_TOKENS: Set[str] = {
    "best", "top", "vs", "versus", "compare", "comparison", "review", "reviews",
    "cheap", "affordable", "under", "2024", "2025",
}

TRANSACTIONAL_TOKENS: Set[str] = {
    "buy", "price", "sale", "deal", "coupon", "discount",
}


def _normalize(text: Optional[str]) -> str:
    return (text or "").strip().lower()


def _tokenize(text: str) -> List[str]:
    import re
    # keep alphanumerics and simple signifiers; split on non-word
    tokens = re.split(r"[^a-z0-9\+]+", text.lower())
    return [t for t in tokens if t]


def _extract_product_type_tokens(scraped_product: Dict) -> Set[str]:
    """Extract candidate product type tokens from scraped_product title and breadcrumbs.
    Conservative: just tokenize title and common nouns. Without NLP, we approximate with all tokens >3 chars.
    """
    title = (
        ((scraped_product or {}).get("elements", {}) or {}).get("productTitle", {}).get("text")
    )
    if isinstance(title, list):
        title = title[0] if title else ""
    title = _normalize(title)
    tokens = set(t for t in _tokenize(title) if len(t) >= 4)

    # Optionally include a breadcrumb-like field if present
    bcrumb = None
    try:
        bcrumb = ((scraped_product or {}).get("elements", {}) or {}).get("breadcrumbs")
    except Exception:
        bcrumb = None
    if isinstance(bcrumb, str):
        tokens.update(t for t in _tokenize(bcrumb) if len(t) >= 4)
    elif isinstance(bcrumb, list):
        for b in bcrumb:
            tokens.update(t for t in _tokenize(str(b)) if len(t) >= 4)

    return tokens


def _has_attribute(kw: str) -> bool:
    kl = _normalize(kw)
    # simple multi-word phrases check
    if "pack of" in kl or "with straps" in kl:
        return True
    toks = set(_tokenize(kl))
    return bool(ATTRIBUTE_TOKENS & toks)


def _has_use_case_or_benefit(kw: str) -> bool:
    kl = _normalize(kw)
    # detect "for <something>" use-case
    if " for " in f" {kl} ":
        return True
    toks = set(_tokenize(kl))
    return bool(USE_CASE_TOKENS & toks)


def _matches_product_type(kw: str, product_type_tokens: Set[str]) -> bool:
    toks = set(_tokenize(kw))
    if not toks:
        return False
    # overlap with product type tokens
    return bool(product_type_tokens & toks)


def classify_intent(
    phrase: str,
    scraped_product: Optional[Dict],
    category: Optional[KeywordCategory] = None,
    brand_tokens: Optional[Set[str]] = None,
) -> IntentResult:
    """Classify keyword purchase intent per MVP scale (0..3).

    Heuristic mapping:
    - 0: Irrelevant/Outlier or no match to product type and no attribute/use-case.
    - 1: Matches exactly one of: product type, attribute, or use-case/benefit.
    - 2: Matches exactly two of the above.
    - 3: Matches all three of the above; or strong transactional modifiers present.

    Adjustments:
    - If category is IRRELEVANT or OUTLIER => 0
    - If phrase is branded-only (brand match with no other aspect) => 1
    - If strong transactional tokens appear and at least one aspect present => bump to 3 (cap at 3)
    """
    kw = _normalize(phrase)
    if not kw:
        return IntentResult(intent_score=0, matched_aspects=[], debug={"reason": "empty"})

    # Category-based early exits
    if str(getattr(category, "value", category)) in {"Irrelevant", "Outlier"}:
        return IntentResult(intent_score=0, matched_aspects=[], debug={"reason": "category"})

    product_type_tokens = _extract_product_type_tokens(scraped_product or {})

    has_type = _matches_product_type(kw, product_type_tokens)
    has_attr = _has_attribute(kw)
    has_use = _has_use_case_or_benefit(kw)

    matched: List[str] = []
    if has_type:
        matched.append("product_type")
    if has_attr:
        matched.append("attribute")
    if has_use:
        matched.append("use_case")

    # Branded-only handling
    branded_only = False
    if brand_tokens:
        toks = set(_tokenize(kw))
        if (toks & brand_tokens) and not (has_type or has_attr or has_use):
            branded_only = True

    # Compute base score from aspect coverage
    score = min(3, max(0, len(matched)))
    if branded_only and score == 0:
        score = 1

    # Transactional boosters
    if score >= 1:
        toks = set(_tokenize(kw))
        if TRANSACTIONAL_TOKENS & toks:
            score = 3
            if "transactional" not in matched:
                matched.append("transactional")

    # Commercial intent tokens don't change score directly (kept for future use)
    debug = {
        "has_type": has_type,
        "has_attr": has_attr,
        "has_use": has_use,
        "product_type_tokens_sample": list(sorted(list(product_type_tokens)))[0:10],
    }

    return IntentResult(intent_score=score, matched_aspects=matched, debug=debug)


def extract_brand_tokens(scraped_product: Optional[Dict]) -> Set[str]:
    brand = None
    try:
        brand = ((scraped_product or {}).get("elements", {}) or {}).get("brand", {}).get("text")
    except Exception:
        brand = None
    tokens: Set[str] = set()
    if isinstance(brand, str):
        tokens.update(_tokenize(brand))
    elif isinstance(brand, list):
        for b in brand:
            tokens.update(_tokenize(str(b)))
    return set(t for t in tokens if t)
