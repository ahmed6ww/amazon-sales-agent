"""
SEO Keyword Content Filter - Validates keywords_included fields in SEO output
"""
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


def validate_and_correct_keywords_included(seo_output: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Validate that keywords in 'keywords_included' actually exist in the content.
    Remove any false claims and deduplicate across title/bullets.
    """
    from .helper_methods import extract_keywords_from_content
    
    logger.info("🔧 [SEO VALIDATION] Validating keywords_included fields...")
    
    corrected = seo_output.copy()
    stats = {"title": {"claimed": 0, "actual": 0}, "bullets": {"claimed": 0, "actual": 0}, "duplicates": 0}
    used_keywords = set()
    
    # Validate title
    if "optimized_title" in corrected:
        title_content = corrected["optimized_title"].get("content", "")
        claimed = corrected["optimized_title"].get("keywords_included", [])
        actual, _ = extract_keywords_from_content(title_content, claimed)
        
        for kw in actual:
            used_keywords.add(kw.lower())
        
        corrected["optimized_title"]["keywords_included"] = actual
        stats["title"] = {"claimed": len(claimed), "actual": len(actual)}
        
        if len(claimed) != len(actual):
            logger.warning(f"⚠️  Title: Removed {len(claimed) - len(actual)} invalid keywords")
    
    # Validate bullets (with deduplication)
    if "optimized_bullets" in corrected:
        for i, bullet in enumerate(corrected["optimized_bullets"]):
            content = bullet.get("content", "")
            claimed = bullet.get("keywords_included", [])
            actual, _ = extract_keywords_from_content(content, claimed)
            
            # Remove duplicates
            deduplicated = []
            for kw in actual:
                if kw.lower() not in used_keywords:
                    deduplicated.append(kw)
                    used_keywords.add(kw.lower())
                else:
                    stats["duplicates"] += 1
            
            corrected["optimized_bullets"][i]["keywords_included"] = deduplicated
            stats["bullets"]["claimed"] += len(claimed)
            stats["bullets"]["actual"] += len(deduplicated)
    
    logger.info(f"✅ [SEO VALIDATION] Title: {stats['title']['actual']}/{stats['title']['claimed']}, Bullets: {stats['bullets']['actual']}/{stats['bullets']['claimed']}, Duplicates removed: {stats['duplicates']}")
    
    return corrected, stats