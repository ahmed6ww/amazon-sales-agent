"""
SEO Agent Tools

OpenAI Agents SDK tools for SEO optimization functionality.
"""

# from agents import CodeInterpreter  # Not needed for these tools
from typing import Dict, Any, List

from .helper_methods import (
    optimize_product_title,
    generate_bullet_points,
    create_backend_keywords,
    analyze_content_gaps,
    identify_competitive_advantages
)
from .schemas import TitleOptimization, BulletPointOptimization, BackendKeywordOptimization


def tool_optimize_title(
    current_title: str,
    critical_keywords: List[str],
    high_priority_keywords: List[str],
    product_info: Dict[str, Any],
    character_limit: int = 200
) -> TitleOptimization:
    """
    Optimize Amazon product title for maximum search visibility and conversion.
    
    Args:
        current_title: Current product title
        critical_keywords: Critical keywords (intent score 3) to integrate
        high_priority_keywords: High priority keywords (intent score 2)
        product_info: Product information dictionary
        character_limit: Amazon character limit for marketplace
    
    Returns:
        TitleOptimization: Complete title optimization results
    """
    
    return optimize_product_title(
        current_title=current_title,
        critical_keywords=critical_keywords,
        high_priority_keywords=high_priority_keywords,
        product_info=product_info,
        character_limit=character_limit
    )


def tool_optimize_bullet_points(
    current_bullets: List[str],
    critical_keywords: List[str],
    high_priority_keywords: List[str],
    product_info: Dict[str, Any],
    customer_insights: Dict[str, Any] = None
) -> BulletPointOptimization:
    """
    Generate optimized bullet points with strategic keyword integration.
    
    Args:
        current_bullets: Current bullet points
        critical_keywords: Critical keywords to integrate
        high_priority_keywords: High priority keywords
        product_info: Product information and features
        customer_insights: Customer pain points and preferences
    
    Returns:
        BulletPointOptimization: Complete bullet point optimization results
    """
    
    if customer_insights is None:
        customer_insights = {}
    
    return generate_bullet_points(
        current_bullets=current_bullets,
        critical_keywords=critical_keywords,
        high_priority_keywords=high_priority_keywords,
        product_info=product_info,
        customer_insights=customer_insights
    )


def tool_optimize_backend_keywords(
    title: str,
    bullets: List[str],
    critical_keywords: List[str],
    high_priority_keywords: List[str],
    medium_priority_keywords: List[str],
    opportunity_keywords: List[str],
    character_limit: int = 250
) -> BackendKeywordOptimization:
    """
    Create optimized backend keyword strategy for maximum search coverage.
    
    Args:
        title: Optimized product title
        bullets: Optimized bullet points
        critical_keywords: Critical keywords from scoring
        high_priority_keywords: High priority keywords
        medium_priority_keywords: Medium priority keywords
        opportunity_keywords: High-opportunity keywords
        character_limit: Backend keyword character limit
    
    Returns:
        BackendKeywordOptimization: Complete backend keyword optimization
    """
    
    return create_backend_keywords(
        title=title,
        bullets=bullets,
        critical_keywords=critical_keywords,
        high_priority_keywords=high_priority_keywords,
        medium_priority_keywords=medium_priority_keywords,
        opportunity_keywords=opportunity_keywords,
        character_limit=character_limit
    )


def tool_analyze_seo_gaps(
    current_listing: Dict[str, Any],
    keyword_analysis: Dict[str, Any],
    scoring_analysis: Dict[str, Any],
    competitor_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Analyze SEO gaps and identify competitive advantages.
    
    Args:
        current_listing: Current listing content and structure
        keyword_analysis: Keyword analysis results
        scoring_analysis: Scoring analysis results
        competitor_data: Competitor analysis data
    
    Returns:
        Dict containing content gaps and competitive advantages
    """
    
    if competitor_data is None:
        competitor_data = {}
    
    # Analyze content gaps
    content_gaps = analyze_content_gaps(
        current_listing=current_listing,
        keyword_analysis=keyword_analysis,
        scoring_analysis=scoring_analysis,
        competitor_data=competitor_data
    )
    
    # Identify competitive advantages
    competitive_advantages = identify_competitive_advantages(
        product_info=current_listing,
        keyword_analysis=keyword_analysis,
        competitor_data=competitor_data
    )
    
    return {
        "content_gaps": content_gaps,
        "competitive_advantages": competitive_advantages,
        "gap_count": len(content_gaps),
        "advantage_count": len(competitive_advantages),
        "priority_gaps": [gap for gap in content_gaps if gap.priority == "critical"],
        "quick_wins": [gap for gap in content_gaps if gap.estimated_impact > 80]
    } 