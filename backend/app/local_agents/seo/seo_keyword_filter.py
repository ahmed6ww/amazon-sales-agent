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
        # Extract volumes from relevant, design-specific, and branded keywords
        for item in (keyword_data.get("relevant_keywords", []) + 
                     keyword_data.get("design_keywords", []) +
                     keyword_data.get("branded_keywords", [])):
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
        
        # ALWAYS check ALL keywords in title (Relevant + Design-Specific + Branded)
        if keyword_data:
            # Build complete list of keywords to check (including branded)
            all_possible_phrases = []
            for item in (keyword_data.get("relevant_keywords", []) + 
                         keyword_data.get("design_keywords", []) +
                         keyword_data.get("branded_keywords", [])):
                phrase = item.get("phrase", "")
                if phrase:
                    all_possible_phrases.append(phrase)
            
            # Detect ALL keywords actually present in title
            if all_possible_phrases:
                actual, _ = extract_keywords_from_content(title_content, all_possible_phrases, keyword_volumes)
            else:
                actual, _ = extract_keywords_from_content(title_content, claimed)
        else:
            # Fallback: use what AI claimed if no keyword_data available
            actual, _ = extract_keywords_from_content(title_content, claimed)
        
        corrected["optimized_title"]["keywords_included"] = actual
        stats["title"] = {"claimed": len(claimed), "actual": len(actual)}
        
        if len(claimed) != len(actual):
            logger.info(f"   Title: Detected {len(actual)} keywords (AI claimed {len(claimed)})")
        
        logger.info(f"   Title has {len(actual)} keywords")
    
    # Track title keywords for title-to-bullet duplicate detection
    title_keywords_used = set()
    if "optimized_title" in corrected:
        title_kws = corrected["optimized_title"].get("keywords_included", [])
        title_keywords_used = set(kw.lower() for kw in title_kws)
        logger.info(f"   Tracking {len(title_keywords_used)} title keywords for duplicate detection")
    
    # Track keywords used in bullets for bullet-to-bullet deduplication
    bullet_keywords_used = {}  # Maps keyword -> bullet index
    
    # Validate bullets (ONLY bullet-to-bullet deduplication)
    if "optimized_bullets" in corrected:
        for i, bullet in enumerate(corrected["optimized_bullets"]):
            content = bullet.get("content", "")
            claimed = bullet.get("keywords_included", [])
            
            # ALWAYS check ALL keywords in content (Relevant + Design-Specific + Branded)
            # Don't rely on what AI claimed - detect everything actually present
            if keyword_data:
                # Build complete list of keywords to check (including branded)
                all_possible_phrases = []
                for item in (keyword_data.get("relevant_keywords", []) + 
                             keyword_data.get("design_keywords", []) +
                             keyword_data.get("branded_keywords", [])):
                    phrase = item.get("phrase", "")
                    if phrase:
                        all_possible_phrases.append(phrase)
                
                # Detect ALL keywords actually present in content
                if all_possible_phrases:
                    actual, volume = extract_keywords_from_content(content, all_possible_phrases, keyword_volumes)
                    logger.debug(f"   Bullet {i+1}: Detected {len(actual)} keywords in content")
                else:
                    logger.error(f"   ❌ No keyword list available for detection")
                    actual, volume = [], 0
            else:
                # Fallback: use what AI claimed if no keyword_data available
                actual, volume = extract_keywords_from_content(content, claimed, keyword_volumes)
            
            # Separate into unique, title duplicates, and bullet duplicates
            unique_to_bullet = []
            duplicated_from_title = []
            duplicated_from_other_bullets = []
            unique_volume = 0
            
            for kw in actual:
                kw_lower = kw.lower()
                
                # Check if it's a title duplicate FIRST (priority over bullet duplicates)
                if kw_lower in title_keywords_used:
                    duplicated_from_title.append(kw)
                    logger.debug(f"   Bullet {i+1}: Keyword '{kw}' already in title (show yellow)")
                # Then check bullet-to-bullet duplicates
                elif kw_lower in bullet_keywords_used:
                    duplicated_from_other_bullets.append(kw)
                    stats["bullet_to_bullet_duplicates"] += 1
                    logger.debug(f"   Bullet {i+1}: Keyword '{kw}' already in Bullet {bullet_keywords_used[kw_lower] + 1} (show yellow)")
                # Otherwise it's unique to this bullet
                else:
                    unique_to_bullet.append(kw)
                    bullet_keywords_used[kw_lower] = i
                    # Calculate volume for unique keywords only
                    unique_volume += keyword_volumes.get(kw_lower, 0)
            
            # All keywords shown (unique + title duplicates + bullet duplicates)
            final_keywords = unique_to_bullet + duplicated_from_title + duplicated_from_other_bullets
            
            corrected["optimized_bullets"][i]["keywords_included"] = final_keywords
            corrected["optimized_bullets"][i]["keywords_duplicated_from_title"] = duplicated_from_title  # NEW FIELD
            corrected["optimized_bullets"][i]["keywords_duplicated_from_other_bullets"] = duplicated_from_other_bullets
            corrected["optimized_bullets"][i]["unique_keywords_count"] = len(unique_to_bullet)
            corrected["optimized_bullets"][i]["total_search_volume"] = unique_volume
            
            stats["bullets"]["claimed"] += len(claimed)
            stats["bullets"]["actual"] += len(final_keywords)
            stats["bullets"]["unique"] += len(unique_to_bullet)
            
            logger.debug(f"   Bullet {i+1}: {len(unique_to_bullet)} unique + {len(duplicated_from_other_bullets)} duplicates = {len(final_keywords)} total")
    
    # Calculate title duplicate count
    title_dupe_count = sum(len(b.get('keywords_duplicated_from_title', [])) for b in corrected.get('optimized_bullets', []))
    
    logger.info(f"✅ [SEO VALIDATION] Title: {stats['title']['actual']}/{stats['title']['claimed']}, " +
                f"Bullets: {stats['bullets']['actual']}/{stats['bullets']['claimed']} ({stats['bullets']['unique']} unique), " +
                f"Title duplicates: {title_dupe_count}, " +
                f"Bullet-to-bullet duplicates: {stats['bullet_to_bullet_duplicates']}")
    
    return corrected, stats