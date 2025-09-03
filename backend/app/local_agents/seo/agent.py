"""
SEO Agent

OpenAI Agents SDK implementation for Amazon SEO optimization.
"""

from agents import Agent, ModelSettings
from agents.tool import function_tool
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
from .prompts import SEO_AGENT_INSTRUCTIONS
from .helper_methods import (
    optimize_product_title,
    generate_bullet_points,
    create_backend_keywords,
    analyze_content_gaps,
    identify_competitive_advantages,
    calculate_seo_score
)

# Define SEO tools to enforce AI-only processing
@function_tool
def tool_optimize_title(product_info_json: str, critical_keywords_json: str, high_priority_keywords_json: str, character_limit: int = 200) -> str:
    import json
    info = json.loads(product_info_json)
    crit = json.loads(critical_keywords_json)
    high = json.loads(high_priority_keywords_json)
    from .helper_methods import optimize_product_title
    res = optimize_product_title(
        current_title=str(info.get("title", "")),
        critical_keywords=crit,
        high_priority_keywords=high,
        product_info=info,
        character_limit=character_limit,
    )
    return res.model_dump_json()

@function_tool
def tool_generate_bullets(product_info_json: str, critical_keywords_json: str, high_priority_keywords_json: str) -> str:
    import json
    info = json.loads(product_info_json)
    crit = json.loads(critical_keywords_json)
    high = json.loads(high_priority_keywords_json)
    from .helper_methods import generate_bullet_points
    res = generate_bullet_points(
        current_bullets=list(info.get("bullets", [])),
        critical_keywords=crit,
        high_priority_keywords=high,
        product_info=info,
        customer_insights={},
    )
    return res.model_dump_json()

@function_tool
def tool_backend_keywords(title: str, bullets_json: str, critical_keywords_json: str, high_priority_keywords_json: str, medium_priority_keywords_json: str, opportunity_keywords_json: str, character_limit: int = 250) -> str:
    import json
    bullets = json.loads(bullets_json)
    crit = json.loads(critical_keywords_json)
    high = json.loads(high_priority_keywords_json)
    med = json.loads(medium_priority_keywords_json)
    opp = json.loads(opportunity_keywords_json)
    from .helper_methods import create_backend_keywords
    res = create_backend_keywords(
        title=title,
        bullets=bullets,
        critical_keywords=crit,
        high_priority_keywords=high,
        medium_priority_keywords=med,
        opportunity_keywords=opp,
        character_limit=character_limit,
    )
    return res.model_dump_json()

@function_tool
def tool_analyze_gaps(current_listing_json: str, keyword_analysis_json: str, scoring_analysis_json: str, competitor_data_json: str = "{}") -> str:
    import json
    listing = json.loads(current_listing_json)
    kw = json.loads(keyword_analysis_json)
    sc = json.loads(scoring_analysis_json)
    comp = json.loads(competitor_data_json)
    from .helper_methods import analyze_content_gaps, identify_competitive_advantages
    gaps = analyze_content_gaps(listing, kw, sc, comp)
    advantages = identify_competitive_advantages(listing, kw, comp)
    return json.dumps({"content_gaps": [g.model_dump() for g in gaps], "competitive_advantages": [a for a in advantages]})

load_dotenv(find_dotenv())  # Load environment variables from .env file


# Create the SEO Agent WITH tools for AI-only processing
seo_agent = Agent(
    name="SEOAgent",
    instructions=SEO_AGENT_INSTRUCTIONS,
    model="gpt-5-2025-08-07",  # Tool-compatible
    tools=[
        tool_optimize_title,
        tool_generate_bullets,
        tool_backend_keywords,
        tool_analyze_gaps,
    ],
    model_settings=ModelSettings(
        max_tokens=4000,
        tool_choice="required",
    )
) 