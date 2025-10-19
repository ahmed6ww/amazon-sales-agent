"""
SEO Keyword Content Filter - Validates keywords_included fields in SEO output
"""
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


def validate_and_correct_keywords_included(seo_output: Dict[str, Any], keyword_data: Dict[str, Any] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Validate that keywords in 'keywords_included' actually exist in the content.
    Deduplicate keywords ONLY between bullets (bullet-to-bullet).
    
    IMPORTANT: Title and bullets are completely separate - no cross-deduplication.
    Only prevent the same keyword from appearing in multiple bullets.
    
    Args:
        seo_output: SEO optimization output dict
        keyword_data: Keyword data containing search volumes (from prepare_keyword_data_for_analysis)
    """
    from .helper_methods import extract_keywords_from_content
    
    logger.info("🔧 [SEO VALIDATION] Validating keywords_included fields...")
    
    corrected = seo_output.copy()
    stats = {"title": {"claimed": 0, "actual": 0}, "bullets": {"claimed": 0, "actual": 0, "unique": 0}, 
             "bullet_to_bullet_duplicates": 0}
    
    # Build keyword volumes map for volume calculation
    keyword_volumes = {}
    if keyword_data:
        # Extract volumes from relevant and design keywords
        for item in keyword_data.get("relevant_keywords", []) + keyword_data.get("design_keywords", []):
            phrase = item.get("phrase", "")
            volume = item.get("search_volume", 0)
            if phrase:
                keyword_volumes[phrase.lower()] = volume
        logger.info(f"   Built keyword volumes map with {len(keyword_volumes)} entries")
    else:
        logger.warning("   No keyword_data provided - volume calculations will be 0")
    
    # Validate title (no deduplication for title)
    if "optimized_title" in corrected:
        title_content = corrected["optimized_title"].get("content", "")
        claimed = corrected["optimized_title"].get("keywords_included", [])
        actual, _ = extract_keywords_from_content(title_content, claimed)
        
        corrected["optimized_title"]["keywords_included"] = actual
        stats["title"] = {"claimed": len(claimed), "actual": len(actual)}
        
        if len(claimed) != len(actual):
            logger.warning(f"⚠️  Title: Removed {len(claimed) - len(actual)} invalid keywords")
        
        logger.info(f"   Title has {len(actual)} keywords")
    
    # Track keywords used in bullets for bullet-to-bullet deduplication
    bullet_keywords_used = {}  # Maps keyword -> bullet index
    
    # Validate bullets (ONLY bullet-to-bullet deduplication)
    if "optimized_bullets" in corrected:
        for i, bullet in enumerate(corrected["optimized_bullets"]):
            content = bullet.get("content", "")
            claimed = bullet.get("keywords_included", [])
            actual, volume = extract_keywords_from_content(content, claimed, keyword_volumes)
            
            # Separate into first-use keywords and duplicates from other bullets
            unique_to_bullet = []
            duplicated_from_other_bullets = []
            unique_volume = 0
            
            for kw in actual:
                kw_lower = kw.lower()
                
                if kw_lower not in bullet_keywords_used:
                    # First time seeing this keyword across all bullets - KEEP and COUNT
                    unique_to_bullet.append(kw)
                    bullet_keywords_used[kw_lower] = i
                else:
                    # Already used in another bullet - SHOW but DON'T COUNT
                    duplicated_from_other_bullets.append(kw)
                    stats["bullet_to_bullet_duplicates"] += 1
                    logger.debug(f"   Bullet {i+1}: Keyword '{kw}' already in Bullet {bullet_keywords_used[kw_lower] + 1} (show yellow)")
            
            # Calculate volume for UNIQUE keywords only
            unique_volume = sum(keyword_volumes.get(kw.lower(), 0) for kw in unique_to_bullet)
            
            # All keywords shown (including duplicates), but duplicates marked yellow
            final_keywords = unique_to_bullet + duplicated_from_other_bullets
            
            corrected["optimized_bullets"][i]["keywords_included"] = final_keywords
            corrected["optimized_bullets"][i]["keywords_duplicated_from_other_bullets"] = duplicated_from_other_bullets
            corrected["optimized_bullets"][i]["unique_keywords_count"] = len(unique_to_bullet)
            corrected["optimized_bullets"][i]["total_search_volume"] = unique_volume
            
            stats["bullets"]["claimed"] += len(claimed)
            stats["bullets"]["actual"] += len(final_keywords)
            stats["bullets"]["unique"] += len(unique_to_bullet)
            
            logger.debug(f"   Bullet {i+1}: {len(unique_to_bullet)} unique + {len(duplicated_from_other_bullets)} duplicates = {len(final_keywords)} total")
    
    logger.info(f"✅ [SEO VALIDATION] Title: {stats['title']['actual']}/{stats['title']['claimed']}, " +
                f"Bullets: {stats['bullets']['actual']}/{stats['bullets']['claimed']} ({stats['bullets']['unique']} unique), " +
                f"Bullet-to-bullet duplicates (shown yellow): {stats['bullet_to_bullet_duplicates']}")
    
    return corrected, stats