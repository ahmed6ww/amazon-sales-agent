"""
SEO Optimization Helper Methods

Utility functions for SEO analysis and optimization.
"""

import re
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict


def extract_keywords_from_content(content: str, keywords_list: List[str]) -> Tuple[List[str], int]:
    """
    Extract keywords found in content and return them with count.
    
    Args:
        content: Text content to analyze
        keywords_list: List of keywords to search for
        
    Returns:
        Tuple of (found_keywords, count)
    """
    if not content:
        return [], 0
        
    content_lower = content.lower()
    found_keywords = []
    
    for keyword in keywords_list:
        if keyword.lower() in content_lower:
            found_keywords.append(keyword)
            
    return found_keywords, len(found_keywords)


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


def analyze_content_piece(content: str, keywords_list: List[str]) -> Dict[str, Any]:
    """
    Analyze a specific piece of content (title, bullet, etc.) for SEO metrics.
    
    Args:
        content: The content string to analyze
        keywords_list: List of relevant keyword phrases
        
    Returns:
        Analysis dict with metrics
    """
    if not content:
        return {
            "content": "",
            "keywords_found": [],
            "keyword_count": 0,
            "character_count": 0,
            "keyword_density": 0.0,
            "opportunities": []
        }
    
    found_keywords, count = extract_keywords_from_content(content, keywords_list)
    char_count = len(content)
    
    # Calculate keyword density (keywords per 100 characters)
    density = (count / char_count * 100) if char_count > 0 else 0
    
    # Find opportunities (keywords not included)
    opportunities = [kw for kw in keywords_list if kw not in found_keywords][:5]
    
    return {
        "content": content,
        "keywords_found": found_keywords,
        "keyword_count": count,
        "character_count": char_count,
        "keyword_density": round(density, 2),
        "opportunities": opportunities
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
        
        # Categorize keywords
        if category == "Relevant":
            relevant_keywords.append(item)
        elif category == "Design-Specific":
            design_keywords.append(item)
            
        # High intent keywords (score 2-3)
        if intent_score >= 2:
            high_intent_keywords.append(item)
            
        # High volume keywords (>500 searches)
        if search_volume > 500:
            high_volume_keywords.append(item)
            
        # Aggregate root volumes
        if root:
            root_volumes[root] += search_volume
    
    return {
        "relevant_keywords": relevant_keywords,
        "design_keywords": design_keywords,
        "high_intent_keywords": high_intent_keywords,
        "high_volume_keywords": high_volume_keywords,
        "root_volumes": dict(root_volumes),
        "total_keywords": len(keyword_items)
    }


def format_keywords_for_prompt(keywords: List[Dict[str, Any]], limit: int = 20) -> str:
    """
    Format keywords for inclusion in prompt template.
    
    Args:
        keywords: List of keyword dicts
        limit: Maximum number of keywords to include
        
    Returns:
        Formatted string for prompt
    """
    if not keywords:
        return "None"
        
    lines = []
    for i, kw in enumerate(keywords[:limit]):
        phrase = kw.get("phrase", "")
        intent = kw.get("intent_score", 0)
        volume = kw.get("search_volume", 0)
        lines.append(f"- {phrase} (Intent: {intent}, Volume: {volume})")
        
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