"""
SEO Optimization Helper Methods

Utility functions for SEO analysis and optimization.
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


def extract_keywords_from_content(content: str, keywords_list: List[str], keyword_volumes: Dict[str, int] = None) -> Tuple[List[str], int]:
    """
    Enhanced keyword extraction that finds all keywords present in content,
    including partial matches and sub-phrases.
    
    TASK 2 ENHANCEMENT: If content is "freeze dried strawberry slices", this will also find:
    - "freeze dried strawberries" (sub-phrase match)
    - "dried strawberries" (sub-phrase match)  
    - "strawberry slices" (sub-phrase match)
    
    Args:
        content: Text content to analyze
        keywords_list: List of keywords to search for
        keyword_volumes: Optional dict mapping keywords to search volumes
        
    Returns:
        Tuple of (found_keywords, total_search_volume)
    """
    if not content:
        return [], 0
        
    content_lower = content.lower().strip()
    found_keywords = []
    found_keywords_set = set()
    total_volume = 0
    
    logger.debug(f"[KEYWORD_EXTRACTION] Analyzing content: '{content[:100]}{'...' if len(content) > 100 else ''}'")
    logger.debug(f"[KEYWORD_EXTRACTION] Searching for {len(keywords_list)} keywords")
    
    # Sort keywords by length (longest first) to catch full phrases before sub-phrases
    sorted_keywords = sorted(keywords_list, key=len, reverse=True)
    
    for keyword in sorted_keywords:
        if not keyword:
            continue
            
        keyword_lower = keyword.lower().strip()
        
        # Skip if already found (avoid duplicates)
        if keyword_lower in found_keywords_set:
            continue
        
        # ================================================================
        # METHOD 1: Word-Boundary Match (Fixed - Issue #1)
        # Use regex word boundaries to prevent false substring matches
        # Example: "make up sponges foundation" will NOT match "make up blending sponges for foundation"
        # ================================================================
        # Use word-boundary regex to match whole phrases only
        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
        if re.search(pattern, content_lower):
            found_keywords.append(keyword)
            found_keywords_set.add(keyword_lower)
            
            # Add volume if available
            if keyword_volumes and keyword in keyword_volumes:
                volume = keyword_volumes[keyword]
                total_volume += volume
                logger.debug(f"[KEYWORD_EXTRACTION] ✅ Word-boundary match: '{keyword}' (volume: {volume})")
            else:
                logger.debug(f"[KEYWORD_EXTRACTION] ✅ Word-boundary match: '{keyword}'")
            continue
        
        # ================================================================
        # METHOD 2: Sequential Proximity Match (for plural/singular variations)
        # ================================================================
        # Only match if tokens appear in EXACT ORDER with tight proximity
        # Example: "makeup sponge set" MATCHES "makeup sponges set" (adjacent plural)
        # Example: "makeup sponges foundation" DOES NOT MATCH "makeup sponge...sponges for foundation"
        # ================================================================
        keyword_tokens = keyword_lower.split()
        
        if len(keyword_tokens) > 1:
            # Find each token (or its plural/singular variant) in sequence
            last_position = -1
            all_sequential = True
            
            for token in keyword_tokens:
                # Look for this token AFTER the last found position
                search_start = last_position + 1
                remaining_content = content_lower[search_start:]
                
                # Try to find token or its variants
                found_position = -1
                
                # Direct match
                if token in remaining_content:
                    found_position = search_start + remaining_content.find(token)
                else:
                    # Try plural/singular variants
                    variants = []
                    
                    # Singular variants (sponges -> sponge)
                    if token.endswith('ies') and len(token) > 4:
                        variants.append(token[:-3] + 'y')
                    elif token.endswith('es') and len(token) > 3:
                        variants.append(token[:-2])
                    elif token.endswith('s') and len(token) > 2:
                        variants.append(token[:-1])
                    
                    # Plural variants (sponge -> sponges)
                    if token.endswith('y') and len(token) > 2:
                        variants.append(token[:-1] + 'ies')
                    variants.append(token + 'es')
                    variants.append(token + 's')
                    
                    # Check variants
                    for variant in variants:
                        if variant in remaining_content:
                            found_position = search_start + remaining_content.find(variant)
                            break
                
                # If token not found in sequence, fail
                if found_position == -1:
                    all_sequential = False
                    break
                
                # Check proximity: next token must be within 20 characters (about 3-4 words)
                if last_position != -1:
                    distance = found_position - last_position
                    if distance > 20:  # Too far apart
                        all_sequential = False
                        break
                
                last_position = found_position
            
            # If all tokens found in sequence with tight proximity
            if all_sequential:
                found_keywords.append(keyword)
                found_keywords_set.add(keyword_lower)
                
                if keyword_volumes and keyword in keyword_volumes:
                    volume = keyword_volumes[keyword]
                    total_volume += volume
                    logger.debug(f"[KEYWORD_EXTRACTION] ✅ Sequential match: '{keyword}' (volume: {volume})")
                else:
                    logger.debug(f"[KEYWORD_EXTRACTION] ✅ Sequential match: '{keyword}'")
                continue
                
        # ================================================================
        # METHOD 3: Hyphen Variations
        # ================================================================
        if '-' in keyword_lower:
            keyword_no_hyphen = keyword_lower.replace('-', ' ')
            if keyword_no_hyphen in content_lower and keyword_lower not in content_lower:
                found_keywords.append(keyword)
                found_keywords_set.add(keyword_lower)
                
                if keyword_volumes and keyword in keyword_volumes:
                    volume = keyword_volumes[keyword]
                    total_volume += volume
                    logger.debug(f"[KEYWORD_EXTRACTION] ✅ Hyphen variant: '{keyword}' (volume: {volume})")
                else:
                    logger.debug(f"[KEYWORD_EXTRACTION] ✅ Hyphen variant: '{keyword}'")
                continue
        
        # Not found
        logger.debug(f"[KEYWORD_EXTRACTION] ❌ Not found: '{keyword}'")
    
    logger.info(f"[KEYWORD_EXTRACTION] Found {len(found_keywords)} keywords (volume: {total_volume:,})")
    logger.info(f"[KEYWORD_EXTRACTION] Keywords: {found_keywords[:5]}{'...' if len(found_keywords) > 5 else ''}")
    
    return found_keywords, total_volume


def calculate_keyword_coverage_from_analysis(
    title_analysis: Any, 
    bullets_analysis: List[Any], 
    backend_keywords: List[str], 
    relevant_keywords: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate keyword coverage from analysis results (no duplicates).
    
    Args:
        title_analysis: Title analysis result
        bullets_analysis: List of bullet analysis results (filtered)
        backend_keywords: List of backend keywords
        relevant_keywords: List of keyword dicts with phrase, intent_score, search_volume
        
    Returns:
        Coverage analysis dict
    """
    # Collect all unique keywords found (no duplicates)
    found_keywords = []
    
    # Add title keywords
    if hasattr(title_analysis, 'keywords_found'):
        found_keywords.extend(title_analysis.keywords_found)
    
    # Add bullet keywords (already filtered for duplicates)
    for bullet_analysis in bullets_analysis:
        if hasattr(bullet_analysis, 'keywords_found'):
            found_keywords.extend(bullet_analysis.keywords_found)
    
    # Add backend keywords (if any found in backend content)
    # Note: Backend keywords are typically not in the scraped data, so this is usually empty
    backend_content = " ".join(backend_keywords).lower()
    keyword_phrases = [kw.get("phrase", "") for kw in relevant_keywords]
    backend_found, _ = extract_keywords_from_content(backend_content, keyword_phrases)
    found_keywords.extend(backend_found)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_found_keywords = []
    for kw in found_keywords:
        if kw.lower() not in seen:
            unique_found_keywords.append(kw)
            seen.add(kw.lower())
    
    # Analyze high-intent and high-volume misses
    missing_high_intent = []
    missing_high_volume = []
    
    for kw in relevant_keywords:
        phrase = kw.get("phrase", "")
        intent_score = kw.get("intent_score", 0)
        search_volume = kw.get("search_volume", 0)
        
        if phrase not in unique_found_keywords:
            if intent_score >= 2:
                missing_high_intent.append(phrase)
            if search_volume and search_volume > 500:  # Null-safe check
                missing_high_volume.append(phrase)
    
    coverage_percentage = (len(unique_found_keywords) / len(keyword_phrases) * 100) if keyword_phrases else 0
    
    return {
        "total_keywords": len(keyword_phrases),
        "covered_keywords": len(unique_found_keywords),
        "coverage_percentage": round(coverage_percentage, 1),
        "missing_high_intent": missing_high_intent[:10],  # Top 10
        "missing_high_volume": missing_high_volume[:10]   # Top 10
    }


def calculate_keyword_coverage(current_content: Dict[str, Any], relevant_keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate keyword coverage across current listing content.
    
    Args:
        current_content: Dict with title, bullets, backend_keywords
        relevant_keywords: List of keyword dicts with phrase, intent_score, search_volume
        
    Returns:
        Coverage analysis dict
    """
    # Combine all current content
    title = current_content.get("title", "")
    bullets = current_content.get("bullets", [])
    backend = current_content.get("backend_keywords", [])
    
    all_content = title + " " + " ".join(bullets) + " " + " ".join(backend)
    
    # Extract keyword phrases
    keyword_phrases = [kw.get("phrase", "") for kw in relevant_keywords]
    
    # Find covered keywords
    found_keywords, _ = extract_keywords_from_content(all_content, keyword_phrases)
    
    # Analyze high-intent and high-volume misses
    missing_high_intent = []
    missing_high_volume = []
    
    for kw in relevant_keywords:
        phrase = kw.get("phrase", "")
        intent_score = kw.get("intent_score", 0)
        search_volume = kw.get("search_volume", 0)
        
        if phrase not in found_keywords:
            if intent_score >= 2:
                missing_high_intent.append(phrase)
            if search_volume > 500:
                missing_high_volume.append(phrase)
    
    coverage_percentage = (len(found_keywords) / len(keyword_phrases) * 100) if keyword_phrases else 0
    
    return {
        "total_keywords": len(keyword_phrases),
        "covered_keywords": len(found_keywords),
        "coverage_percentage": round(coverage_percentage, 1),
        "missing_high_intent": missing_high_intent[:10],  # Top 10
        "missing_high_volume": missing_high_volume[:10]   # Top 10
    }


def analyze_root_coverage(current_content: Dict[str, Any], root_volumes: Dict[str, int]) -> Dict[str, Any]:
    """
    Analyze coverage of root keywords.
    
    Args:
        current_content: Dict with title, bullets, backend_keywords
        root_volumes: Dict mapping root keywords to their volumes
        
    Returns:
        Root coverage analysis
    """
    # Combine all current content
    title = current_content.get("title", "")
    bullets = current_content.get("bullets", [])
    backend = current_content.get("backend_keywords", [])
    
    all_content = (title + " " + " ".join(bullets) + " " + " ".join(backend)).lower()
    
    # Check which roots are covered
    covered_roots = []
    missing_roots = []
    
    for root, volume in root_volumes.items():
        if root.lower() in all_content:
            covered_roots.append(root)
        else:
            missing_roots.append(root)
    
    coverage_percentage = (len(covered_roots) / len(root_volumes) * 100) if root_volumes else 0
    
    return {
        "total_roots": len(root_volumes),
        "covered_roots": len(covered_roots),
        "coverage_percentage": round(coverage_percentage, 1),
        "missing_roots": missing_roots,
        "root_volumes": root_volumes
    }


def analyze_content_piece(content: str, keywords_list: List[str], keyword_volumes: Dict[str, int] = None) -> Dict[str, Any]:
    """
    Analyze a specific piece of content (title, bullet, etc.) for SEO metrics.
    TASK 2: Now includes search volume calculation.
    
    Args:
        content: The content string to analyze
        keywords_list: List of relevant keyword phrases
        keyword_volumes: Optional dict mapping keywords to search volumes
        
    Returns:
        Analysis dict with metrics including total_search_volume
    """
    if not content:
        return {
            "content": "",
            "keywords_found": [],
            "keyword_count": 0,
            "character_count": 0,
            "keyword_density": 0.0,
            "opportunities": [],
            "total_search_volume": 0
        }
    
    logger.info(f"[CONTENT_ANALYSIS] Analyzing content piece: '{content[:50]}{'...' if len(content) > 50 else ''}'")
    logger.info(f"[CONTENT_ANALYSIS] Searching for {len(keywords_list)} keywords")
    
    # Use enhanced extraction with volume calculation (Task 2)
    found_keywords, total_volume = extract_keywords_from_content(content, keywords_list, keyword_volumes)
    char_count = len(content)
    
    # Calculate keyword density (keywords per 100 characters)
    density = (len(found_keywords) / char_count * 100) if char_count > 0 else 0
    
    # Find opportunities (keywords not included)
    opportunities = [kw for kw in keywords_list if kw not in found_keywords][:5]
    
    # Note: Validation removed - extract_keywords_from_content() already validates matches
    # using advanced matching (sub-phrase, plural/singular, hyphen variations).
    # Re-validating with simple substring check was rejecting valid advanced matches.
    
    logger.info(f"[CONTENT_ANALYSIS] ✅ Final result: {len(found_keywords)} keywords (volume: {total_volume:,})")
    
    return {
        "content": content,
        "keywords_found": found_keywords,
        "keyword_count": len(found_keywords),
        "character_count": char_count,
        "keyword_density": round(density, 2),
        "opportunities": opportunities,
        "total_search_volume": total_volume
    }


def prepare_keyword_data_for_analysis(keyword_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Prepare keyword data in the format needed for SEO analysis.
    
    Args:
        keyword_items: List of keyword dicts from scoring agent
        
    Returns:
        Organized keyword data for analysis
    """
    relevant_keywords = []
    design_keywords = []
    branded_keywords = []
    high_intent_keywords = []
    high_volume_keywords = []
    
    # Collect root volumes
    root_volumes = defaultdict(int)
    
    for item in keyword_items:
        category = item.get("category", "")
        intent_score = item.get("intent_score", 0)
        search_volume = item.get("search_volume", 0)
        root = item.get("root", "")
        phrase = item.get("phrase", "")
        
        # Handle None values safely
        if search_volume is None:
            search_volume = 0
        if intent_score is None:
            intent_score = 0
        
        # FILTER: Only process keywords with actual search volume
        if search_volume > 0:
            # Categorize keywords
            if category == "Relevant":
                relevant_keywords.append(item)
            elif category == "Design-Specific":
                design_keywords.append(item)
            elif category == "Branded":
                branded_keywords.append(item)
                
            # High intent keywords (score 2-3)
            if intent_score >= 2:
                high_intent_keywords.append(item)
                
            # High volume keywords (>500 searches)
            if search_volume > 500:
                high_volume_keywords.append(item)
                
            # Task 13: Use AI agent for root relevance filtering (with programmatic fallback)
            if root:
                root_volumes[root] += search_volume  # Collect all volumes first
    
    # Apply AI-powered Task 13 filtering after collecting all data
    try:
        from app.local_agents.scoring.subagents.root_relevance_agent import apply_root_filtering_ai
        # Use AI to filter root volumes based on keyword relevance
        filtered_root_volumes = apply_root_filtering_ai(keyword_items)
        logger.info(f"[Task13-AI] Applied AI root filtering: {len(root_volumes)} -> {len(filtered_root_volumes)} roots")
    except Exception as e:
        logger.warning(f"[Task13-AI] AI filtering failed, using programmatic fallback: {e}")
        # Fallback to programmatic filtering
        filtered_root_volumes = {}
        for item in keyword_items:
            root = item.get("root", "")
            category = item.get("category", "")
            search_volume = item.get("search_volume", 0)
            # Handle None values safely
            if search_volume is None:
                search_volume = 0
            # FILTER: Only process keywords with actual search volume
            if search_volume > 0 and root and category in ["Relevant", "Design-Specific"]:
                filtered_root_volumes[root] = filtered_root_volumes.get(root, 0) + search_volume
    
    return {
        "relevant_keywords": relevant_keywords,
        "design_keywords": design_keywords,
        "branded_keywords": branded_keywords,
        "high_intent_keywords": high_intent_keywords,
        "high_volume_keywords": high_volume_keywords,
        "root_volumes": filtered_root_volumes,  # Use AI-filtered volumes
        "total_keywords": len(keyword_items)
    }


def format_keywords_for_prompt(keywords: List[Dict[str, Any]], limit: int = 20) -> str:
    """
    Format keywords for prompt, sorted by search volume descending.
    
    Args:
        keywords: List of keyword dicts
        limit: Maximum number of keywords to include
        
    Returns:
        Formatted string for prompt with keywords ranked by volume (#1 = highest)
    """
    if not keywords:
        return "None"
    
    # Sort by search volume descending, then intent score descending (Issue #3 fix)
    sorted_keywords = sorted(
        keywords, 
        key=lambda x: (x.get("search_volume", 0) or 0, x.get("intent_score", 0) or 0), 
        reverse=True
    )
        
    lines = []
    for i, kw in enumerate(sorted_keywords[:limit], 1):
        phrase = kw.get("phrase", "")
        intent = kw.get("intent_score", 0)
        volume = kw.get("search_volume", 0)
        
        # Handle None values safely
        if intent is None:
            intent = 0
        if volume is None:
            volume = 0
            
        # Format with rank number and prominent volume display
        lines.append(f"{i}. {phrase} (Volume: {volume:,}, Intent: {intent})")
        
    if len(keywords) > limit:
        lines.append(f"... and {len(keywords) - limit} more")
        
    return "\n".join(lines)


def calculate_character_usage(current_content: Dict[str, Any]) -> Dict[str, int]:
    """
    Calculate character usage for different content types.
    
    Args:
        current_content: Dict with title, bullets, backend_keywords
        
    Returns:
        Character usage breakdown
    """
    title = current_content.get("title", "")
    bullets = current_content.get("bullets", [])
    backend = current_content.get("backend_keywords", [])
    
    return {
        "title_chars": len(title),
        "bullets_total_chars": sum(len(bullet) for bullet in bullets),
        "bullets_avg_chars": int(sum(len(bullet) for bullet in bullets) / len(bullets)) if bullets else 0,
        "backend_chars": len(" ".join(backend)),
        "total_chars": len(title) + sum(len(bullet) for bullet in bullets) + len(" ".join(backend))
    } 