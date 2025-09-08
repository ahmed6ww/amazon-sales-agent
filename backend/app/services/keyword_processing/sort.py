from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .intent import classify_intent, extract_brand_tokens


INTENT_ORDER: List[int] = [3, 2, 1, 0]


def sort_keywords_by_intent(
    keyword_items: List[Dict[str, Any]],
    scraped_product: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """Given KeywordAnalysisResult.items-like list, compute intent 0..3 and sort.

    Expects each item to have at least: {"phrase": str, "category": str, "base_relevancy_score": int}
    Returns a dict with:
      - flat_sorted: list of items including intent_score, sorted by intent desc, relevancy desc, phrase asc
      - by_intent: {"3": [...], "2": [...], "1": [...], "0": [...]} preserving the same item structure
      - counts: {"3": n3, "2": n2, "1": n1, "0": n0}
    """
    brand_tokens = extract_brand_tokens(scraped_product)

    enriched: List[Dict[str, Any]] = []
    for it in (keyword_items or []):
        phrase = (it or {}).get("phrase")
        category = (it or {}).get("category")
        score = (it or {}).get("base_relevancy_score")
        res = classify_intent(phrase=phrase or "", scraped_product=scraped_product or {}, category=category, brand_tokens=brand_tokens)
        enriched.append({
            **it,
            "intent_score": res.intent_score,
            "_intent_debug": res.debug,
        })

    def sort_key(x: Dict[str, Any]) -> Tuple[int, int, str]:
        return (
            int(x.get("intent_score", 0)),
            int(x.get("base_relevancy_score", 0)),
            str(x.get("phrase", ""))
        )

    flat_sorted = sorted(enriched, key=sort_key, reverse=True)

    by_intent: Dict[str, List[Dict[str, Any]]] = {str(k): [] for k in INTENT_ORDER[::-1]}
    counts: Dict[str, int] = {str(k): 0 for k in INTENT_ORDER[::-1]}
    for row in flat_sorted:
        k = str(int(row.get("intent_score", 0)))
        by_intent.setdefault(k, []).append(row)
        counts[k] = counts.get(k, 0) + 1

    return {
        "flat_sorted": flat_sorted,
        "by_intent": by_intent,
        "counts": counts,
    }
