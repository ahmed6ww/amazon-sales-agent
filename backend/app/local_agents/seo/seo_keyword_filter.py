"""
SEO Keyword Content Filter - Validates keywords_included fields in SEO output
"""
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


def validate_and_correct_keywords_included(seo_output: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Validate that keywords in 'keywords_included' actually exist in the content.
    Remove any false claims and deduplicate ONLY within bullets (bullet-to-bullet duplication).
    
    NOTE: Title-to-bullet deduplication is handled by Task 4 post-processing in amazon_compliance_agent.py
    This validation ONLY prevents the same keyword from appearing in multiple bullets.
    """
    from .helper_methods import extract_keywords_from_content
    
    logger.info("🔧 [SEO VALIDATION] Validating keywords_included fields...")
    
    corrected = seo_output.copy()
    stats = {"title": {"claimed": 0, "actual": 0}, "bullets": {"claimed": 0, "actual": 0}, "duplicates": 0}
    bullet_keywords_used = set()  # Track keywords used in bullets (NOT title)
    
    # Validate title
    if "optimized_title" in corrected:
        title_content = corrected["optimized_title"].get("content", "")
        claimed = corrected["optimized_title"].get("keywords_included", [])
        actual, _ = extract_keywords_from_content(title_content, claimed)
        
        corrected["optimized_title"]["keywords_included"] = actual
        stats["title"] = {"claimed": len(claimed), "actual": len(actual)}
        
        if len(claimed) != len(actual):
            logger.warning(f"⚠️  Title: Removed {len(claimed) - len(actual)} invalid keywords")
    
    # Validate bullets (ONLY bullet-to-bullet deduplication)
    if "optimized_bullets" in corrected:
        for i, bullet in enumerate(corrected["optimized_bullets"]):
            content = bullet.get("content", "")
            claimed = bullet.get("keywords_included", [])
            actual, _ = extract_keywords_from_content(content, claimed)
            
            # Remove bullet-to-bullet duplicates only (NOT title duplicates - Task 4 handles that)
            deduplicated = []
            for kw in actual:
                kw_lower = kw.lower()
                if kw_lower not in bullet_keywords_used:
                    deduplicated.append(kw)
                    bullet_keywords_used.add(kw_lower)
                else:
                    # This keyword was already used in another bullet
                    stats["duplicates"] += 1
                    logger.debug(f"   Bullet {i+1}: Removed duplicate '{kw}' (already in another bullet)")
            
            corrected["optimized_bullets"][i]["keywords_included"] = deduplicated
            stats["bullets"]["claimed"] += len(claimed)
            stats["bullets"]["actual"] += len(deduplicated)
    
    logger.info(f"✅ [SEO VALIDATION] Title: {stats['title']['actual']}/{stats['title']['claimed']}, Bullets: {stats['bullets']['actual']}/{stats['bullets']['claimed']}, Bullet-to-bullet duplicates removed: {stats['duplicates']}")
    
    return corrected, stats