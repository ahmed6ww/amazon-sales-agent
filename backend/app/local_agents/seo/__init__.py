"""
SEO Agent Package

This package contains the Amazon SEO optimization agent with tools for:
- Listing optimization (title, bullets, backend keywords)
- SEO gap analysis and competitive positioning
- Content recommendations and keyword integration
- Performance improvement scoring
"""

from .agent import seo_agent
from .schemas import (
    SEOOptimization,
    TitleOptimization,
    BulletPointOptimization,
    BackendKeywordOptimization,
    SEOAnalysisResult,
    ContentGap,
    CompetitiveAdvantage,
    SEOScore
)
from .tools import (
    tool_optimize_title,
    tool_optimize_bullet_points,
    tool_optimize_backend_keywords,
    tool_analyze_seo_gaps
)
from .prompts import SEO_AGENT_INSTRUCTIONS
from .helper_methods import (
    optimize_product_title,
    generate_bullet_points,
    create_backend_keywords,
    analyze_content_gaps,
    calculate_seo_score,
    identify_competitive_advantages
)
from .runner import SEORunner

__all__ = [
    "seo_agent",
    "SEORunner",
    "optimize_product_title",
    "generate_bullet_points",
    "create_backend_keywords",
    "analyze_content_gaps",
    "calculate_seo_score",
    "identify_competitive_advantages",
    "SEOOptimization",
    "TitleOptimization",
    "BulletPointOptimization",
    "BackendKeywordOptimization",
    "SEOAnalysisResult",
    "ContentGap",
    "CompetitiveAdvantage",
    "SEOScore",
    "tool_optimize_title",
    "tool_optimize_bullet_points",
    "tool_optimize_backend_keywords",
    "tool_analyze_seo_gaps",
    "SEO_AGENT_INSTRUCTIONS"
] 