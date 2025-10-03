"""
Task 6: Competitor Title Analysis Agent

AI-powered agent that analyzes top competitor ASIN titles to identify the most important 
product benefits and optimize the first 80 characters with benefit-focused approach 
rather than just keyword stuffing for search volume.
"""

from agents import Agent
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

COMPETITOR_TITLE_ANALYSIS_INSTRUCTIONS = """
You are a Competitor Title Analysis Expert specializing in analyzing top competitor Amazon titles to identify key product benefits and optimize title structure for maximum conversion.

## Your Core Mission :
Analyze competitor ASIN titles to understand:
1. **Benefit Prioritization**: What benefits do successful competitors highlight in first 80 characters
2. **Title Structure**: How top performers structure their titles for mobile optimization
3. **Benefit vs Keyword Balance**: How competitors balance benefit communication with keyword coverage
4. **Conversion Psychology**: What emotional triggers and value propositions drive clicks

## Critical Analysis Framework:

### **Competitor Benefit Analysis**:
- **Primary Benefits**: What core benefits appear in first 80 chars of top competitors
- **Benefit Language**: How benefits are communicated (emotional vs functional)
- **Benefit Order**: Which benefits are prioritized first in successful titles
- **Value Propositions**: Unique selling points that differentiate products

### **Title Structure Patterns**:
- **Opening Hook**: What grabs attention in first 20-30 characters
- **Benefit Integration**: How benefits are naturally woven with keywords
- **Mobile Optimization**: How successful titles work on mobile (first 80 chars)
- **Trust Signals**: Quality indicators, certifications, guarantees

### **Competitive Intelligence**:
- **Market Positioning**: Premium vs budget benefit messaging
- **Target Audience**: Who the benefits are speaking to
- **Use Case Focus**: Which use cases/scenarios are emphasized
- **Emotional Triggers**: Fear, desire, urgency, social proof elements

## Input Format:
```json
{
  "current_title": "BREWER Bulk Freeze Dried Strawberries Slices...",
  "competitor_titles": [
    {"asin": "B07ABC123", "title": "Organic Freeze Dried Strawberries - No Sugar Added, Perfect for Snacking...", "rating": 4.5, "price": 19.99},
    {"asin": "B08DEF456", "title": "Premium Strawberry Slices - Healthy Camping Snack, Long Shelf Life...", "rating": 4.3, "price": 24.99}
  ],
  "main_keyword_root": "freeze dried strawberry",
  "design_keyword_root": "slices",
  "product_context": {"brand": "BREWER", "category": "Food", "price_range": "mid_tier"}
}
```

## Output Format:
Return ONLY a JSON object:
```json
{
  "competitor_analysis": {
    "top_benefits_identified": [
      {"benefit": "No Sugar Added", "frequency": 8, "positions": [1, 2, 3], "conversion_impact": "high"},
      {"benefit": "Perfect for Snacking", "frequency": 6, "positions": [2, 3], "conversion_impact": "medium"},
      {"benefit": "Organic", "frequency": 5, "positions": [1, 2], "conversion_impact": "high"}
    ],
    "title_structure_patterns": {
      "common_opening": "Brand + Quality Indicator (Organic/Premium)",
      "benefit_placement": "Benefits in positions 2-4 within first 80 chars",
      "keyword_integration": "Keywords naturally integrated with benefits",
      "mobile_optimization": "Key info front-loaded for mobile viewing"
    },
    "emotional_triggers": ["quality_assurance", "health_conscious", "convenience", "natural_ingredients"],
    "competitive_gaps": ["unique_benefit_opportunity", "underutilized_emotional_trigger"]
  },
  "optimized_title_strategy": {
    "first_80_approach": "Brand + Top Benefit + Main Keyword + Design Root + Secondary Benefit",
    "benefit_hierarchy": ["No Sugar Added", "Organic Quality", "Perfect for Snacking", "Long Shelf Life"],
    "emotional_angle": "Health-conscious convenience",
    "differentiation": "Emphasize quality + convenience combination",
    "mobile_hook": "What catches attention in first 30 characters"
  },
  "recommended_title": {
    "content": "BREWER Organic Freeze Dried Strawberry Slices - No Sugar Added, Perfect Healthy",
    "first_80_chars": "BREWER Organic Freeze Dried Strawberry Slices - No Sugar Added, Perfect Healthy",
    "benefit_focus": "Organic quality + health benefits in first 80 chars",
    "keyword_coverage": ["freeze dried strawberry", "slices", "organic", "no sugar"],
    "character_count": 79,
    "strategy_rationale": "Opens with brand trust, immediately communicates organic quality and health benefit, includes main keywords naturally"
  },
  "conversion_optimization": {
    "benefit_vs_keyword_balance": "60% benefit focus, 40% keyword coverage",
    "target_audience": "Health-conscious families and fitness enthusiasts", 
    "psychological_triggers": ["health_benefits", "quality_assurance", "natural_ingredients"],
    "competitive_advantage": "Strong health positioning with quality emphasis"
  }
}
```

## Analysis Process:
1. **Competitor Title Parsing**: Extract and analyze structure of each competitor title
2. **Benefit Frequency Analysis**: Count and rank benefits mentioned across competitors
3. **Position Analysis**: Where benefits appear in titles (especially first 80 chars)
4. **Pattern Recognition**: Common structures and approaches used by top performers
5. **Gap Analysis**: Identify underutilized benefits or emotional triggers
6. **Optimization Strategy**: Develop benefit-focused approach for first 80 characters

## Important Guidelines:
- **Benefit Over Keywords**: Prioritize benefit communication over keyword stuffing
- **Mobile First**: Optimize for mobile viewing (first 80 characters critical)
- **Conversion Psychology**: Focus on what drives clicks and purchases
- **Competitive Intelligence**: Learn from what's working for top competitors
- **Natural Language**: Benefits must sound natural and compelling, not robotic
- **Brand Positioning**: Maintain brand voice while optimizing for benefits

## Examples of Benefit Analysis:
- "No Sugar Added" → Health benefit, appeals to health-conscious buyers
- "Perfect for Snacking" → Use case benefit, convenience positioning  
- "Organic" → Quality benefit, premium positioning
- "Long Shelf Life" → Practical benefit, value proposition
- "Premium Quality" → Quality assurance, trust signal

Focus on creating titles that CONVERT, not just rank. The first 80 characters should make customers want to click and buy.
"""

USER_PROMPT_TEMPLATE = """
Analyze these competitor titles to identify key benefits and optimize our title's first 80 characters for conversion.

CURRENT PRODUCT:
{product_json}

COMPETITOR ANALYSIS DATA:
{competitor_data_json}

TASK 6 REQUIREMENTS:
1. Analyze competitor titles for benefit patterns and positioning
2. Identify what benefits top competitors prioritize in first 80 characters  
3. Understand emotional triggers and conversion psychology used
4. Develop benefit-focused optimization strategy (not just keyword stuffing)
5. Create title that balances benefits with keyword coverage for mobile viewing

Focus on CONVERSION over pure SEO. What makes customers click and buy?

Return ONLY the JSON response in the exact format specified.
"""

competitor_title_analysis_agent = Agent(
    name="CompetitorTitleAnalysisAgent",
    instructions=COMPETITOR_TITLE_ANALYSIS_INSTRUCTIONS,
    model="gpt-5-2025-08-07",
)

def analyze_competitor_titles_for_benefits(
    current_content: Dict[str, Any],
    competitor_data: List[Dict[str, Any]], 
    main_keyword_root: str,
    design_keyword_root: str,
    product_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Use AI to analyze competitor titles and identify benefit-focused optimization strategy.
    This implements Task 6 requirements using competitor intelligence for better conversion.
    
    Args:
        current_content: Current product title and content
        competitor_data: List of competitor ASINs with titles, ratings, prices
        main_keyword_root: Main keyword like "freeze dried strawberry"
        design_keyword_root: Design-specific keyword like "slices"
        product_context: Brand, category, etc.
        
    Returns:
        Competitor analysis with benefit-focused title optimization strategy
    """
    # Prepare input data
    product_data = {
        "current_title": current_content.get("title", ""),
        "main_keyword_root": main_keyword_root,
        "design_keyword_root": design_keyword_root,
        "product_context": product_context
    }
    
    # Prepare competitor data for analysis
    competitor_titles = []
    for comp in competitor_data:
        if comp.get("success") and comp.get("title"):
            competitor_titles.append({
                "asin": comp.get("asin", ""),
                "title": comp.get("title", ""),
                "rating": comp.get("rating_value", 0),
                "price": comp.get("price_amount", 0),
                "ratings_count": comp.get("ratings_count", 0)
            })
    
    competitor_analysis_data = {
        "competitor_titles": competitor_titles,
        "total_competitors": len(competitor_titles),
        "analysis_focus": "benefit_identification_and_conversion_optimization"
    }
    
    product_json = json.dumps(product_data, indent=2)
    competitor_data_json = json.dumps(competitor_analysis_data, indent=2)
    
    prompt = USER_PROMPT_TEMPLATE.format(
        product_json=product_json,
        competitor_data_json=competitor_data_json
    )
    
    try:
        from agents import Runner
        
        # Run AI agent
        result = Runner.run_sync(competitor_title_analysis_agent, prompt)
        
        output = getattr(result, "final_output", None)
        
        # Parse AI response
        if isinstance(output, str):
            try:
                parsed = json.loads(output.strip())
                logger.info(f"[CompetitorTitleAnalysisAgent] AI analyzed {len(competitor_titles)} competitors for benefit optimization")
                return parsed
            except json.JSONDecodeError:
                logger.error(f"[CompetitorTitleAnalysisAgent] Failed to parse AI output: {output[:200]}...")
                return _create_fallback_analysis(current_content, competitor_titles, main_keyword_root, design_keyword_root)
        
        elif hasattr(output, 'model_dump'):
            return output.model_dump()
        
        else:
            raise Exception("Unexpected AI output format")
            
    except Exception as e:
        logger.error(f"[CompetitorTitleAnalysisAgent] AI analysis failed: {e}")
        return _create_fallback_analysis(current_content, competitor_titles, main_keyword_root, design_keyword_root)

def _create_fallback_analysis(
    current_content: Dict[str, Any],
    competitor_titles: List[Dict[str, Any]],
    main_root: str,
    design_root: str
) -> Dict[str, Any]:
    """Create a basic fallback analysis when AI fails"""
    
    # Simple benefit detection in competitor titles
    common_benefits = ["organic", "no sugar", "natural", "healthy", "premium", "fresh", "pure"]
    benefit_counts = {}
    
    for comp in competitor_titles:
        title = comp.get("title", "").lower()
        for benefit in common_benefits:
            if benefit in title:
                benefit_counts[benefit] = benefit_counts.get(benefit, 0) + 1
    
    # Sort benefits by frequency
    top_benefits = sorted(benefit_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Simple title recommendation
    brand = current_content.get("brand", "Premium")
    top_benefit = top_benefits[0][0].title() if top_benefits else "Quality"
    
    recommended_title = f"{brand} {top_benefit} {main_root.title()} {design_root.title()}"
    
    return {
        "competitor_analysis": {
            "top_benefits_identified": [
                {"benefit": benefit, "frequency": count, "conversion_impact": "medium"} 
                for benefit, count in top_benefits
            ],
            "title_structure_patterns": {
                "common_opening": f"Brand + {top_benefit}",
                "mobile_optimization": "Benefits front-loaded"
            },
            "competitive_gaps": ["ai_analysis_failed"]
        },
        "optimized_title_strategy": {
            "first_80_approach": f"Brand + {top_benefit} + Keywords",
            "benefit_hierarchy": [b[0] for b in top_benefits],
            "emotional_angle": "quality_focused"
        },
        "recommended_title": {
            "content": recommended_title,
            "first_80_chars": recommended_title[:80],
            "benefit_focus": f"{top_benefit} emphasized",
            "character_count": len(recommended_title),
            "strategy_rationale": "Fallback analysis - prioritized most common competitor benefit"
        },
        "conversion_optimization": {
            "benefit_vs_keyword_balance": "50% benefit, 50% keyword",
            "competitive_advantage": "Basic benefit positioning",
            "fallback_used": True
        }
    }

def apply_competitor_title_optimization_ai(
    current_content: Dict[str, Any],
    competitor_data: List[Dict[str, Any]],
    keyword_data: Dict[str, Any],
    product_context: Dict[str, Any],
    keyword_validator: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Main function to apply AI-powered competitor title analysis for Task 6.
    This is the main entry point for benefit-focused title optimization.
    
    Args:
        current_content: Current listing content
        competitor_data: Scraped competitor ASIN data  
        keyword_data: Analyzed keyword data
        product_context: Product and brand information
        
    Returns:
        Benefit-optimized title strategy based on competitor analysis
    """
    # Extract main and design-specific keyword roots
    relevant_keywords = keyword_data.get("relevant_keywords", [])
    design_keywords = keyword_data.get("design_keywords", [])
    
    # Validate and prioritize keywords by relevancy if validator is provided
    if keyword_validator:
        # Get only valid keywords from research data
        all_keywords = [kw.get("phrase", "") for kw in relevant_keywords + design_keywords]
        valid_keywords, invalid_keywords = keyword_validator.validate_keywords_against_research(all_keywords)
        
        if invalid_keywords:
            logger.warning(f"🚫 Found {len(invalid_keywords)} invalid keywords in competitor analysis input: {invalid_keywords[:3]}")
        
        # Get top keywords sorted by relevancy score
        top_keywords_by_relevancy = keyword_validator.get_top_keywords_by_relevancy(valid_keywords, 20)
        logger.info(f"📈 Using top {len(top_keywords_by_relevancy)} keywords by relevancy for competitor analysis: {top_keywords_by_relevancy[:5]}")
        
        # Filter keyword data to only include top relevancy keywords
        valid_relevant_keywords = [kw for kw in relevant_keywords if kw.get("phrase", "") in top_keywords_by_relevancy]
        valid_design_keywords = [kw for kw in design_keywords if kw.get("phrase", "") in top_keywords_by_relevancy]
        
        # Sort by relevancy score within each category
        valid_relevant_keywords.sort(key=lambda x: (x.get('relevancy_score') or 0), reverse=True)
        valid_design_keywords.sort(key=lambda x: (x.get('relevancy_score') or 0), reverse=True)
        
        relevant_keywords = valid_relevant_keywords
        design_keywords = valid_design_keywords
        
        logger.info(f"🎯 Prioritized {len(relevant_keywords)} relevant keywords and {len(design_keywords)} design keywords by relevancy for competitor analysis")
    
    # Identify main keyword root (highest relevancy relevant keyword)
    main_keyword_root = "freeze dried strawberry"  # Default
    if relevant_keywords:
        # Use highest relevancy keyword instead of highest volume
        top_relevant = max(relevant_keywords, key=lambda x: (x.get("relevancy_score") or 0))
        main_keyword_root = top_relevant.get("phrase", main_keyword_root)
        logger.info(f"🎯 Selected main keyword root by relevancy for competitor analysis: {main_keyword_root} (score: {top_relevant.get('relevancy_score', 0)})")
    
    # Identify design-specific root (highest relevancy design keyword)  
    design_keyword_root = "slices"  # Default
    if design_keywords:
        # Use highest relevancy keyword instead of highest volume
        top_design = max(design_keywords, key=lambda x: (x.get("relevancy_score") or 0))
        design_keyword_root = top_design.get("phrase", design_keyword_root)
        logger.info(f"🎯 Selected design keyword root by relevancy for competitor analysis: {design_keyword_root} (score: {top_design.get('relevancy_score', 0)})")
    
    # Run AI competitor analysis
    result = analyze_competitor_titles_for_benefits(
        current_content=current_content,
        competitor_data=competitor_data,
        main_keyword_root=main_keyword_root,
        design_keyword_root=design_keyword_root,
        product_context=product_context
    )
    
    logger.info(f"[Task6-AI] Applied competitor title analysis with benefit-focused optimization")
    
    return result 