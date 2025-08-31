"""
SEO Agent

OpenAI Agents SDK implementation for Amazon SEO optimization.
"""

from agents import Agent, ModelSettings
from dotenv import load_dotenv, find_dotenv

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
    identify_competitive_advantages,
    calculate_seo_score
)

load_dotenv(find_dotenv())  # Load environment variables from .env file


# Create the SEO Agent with comprehensive optimization instructions
seo_agent = Agent(
    name="SEOAgent",
    instructions=SEO_AGENT_INSTRUCTIONS,
    tools=[
        tool_optimize_title,
        tool_optimize_bullet_points,
        tool_optimize_backend_keywords,
        tool_analyze_seo_gaps
    ],
    model_settings=ModelSettings(
        temperature=0.2,  # Low temperature for consistent optimization
        max_tokens=4000
    )
) 