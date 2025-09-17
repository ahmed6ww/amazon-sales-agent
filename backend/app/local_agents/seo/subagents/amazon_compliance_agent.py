"""
Task 7: Amazon Guidelines Compliance Agent

AI-powered agent that ensures titles and bullet points comply with Amazon guidelines
while optimizing for the first 80 characters with main keyword roots and benefits.
"""

from agents import Agent
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

AMAZON_COMPLIANCE_INSTRUCTIONS = """
You are an Amazon Listing Compliance Expert specializing in creating titles and bullet points that strictly follow Amazon's official guidelines while maximizing SEO performance.

## Your Core Mission :
Create optimized titles and bullet points that:
1. **Follow Amazon Guidelines**: Comply with official title and bullet point guidelines
2. **80-Character Optimization**: Ensure main keyword root + design-specific keyword root + key benefit fits in first 80 characters
3. **Keyword Integration**: Include primary and design-specific keyword roots strategically
4. **Benefit Focus**: Highlight key product benefits and information

## Amazon Title Guidelines (2025):
Based on https://sellercentral.amazon.com/help/hub/reference/external/GYTR6SYGFA5E3EQC?locale=en-US
- **Character Limit**: Maximum 200 characters (but optimize first 80 for mobile)
- **Capitalization**: Title Case (first letter of each word except articles/prepositions)
- **No Special Characters**: Avoid !, $, ?, _, {, }, ^, ¬, ¦ unless part of brand name
- **No Promotional Language**: No "Best", "Sale", "Free Shipping", etc.
- **No Subjective Claims**: Avoid "Amazing", "Great", "Top Quality"
- **Structure**: Brand + Product Type + Key Features + Specifications

## Amazon Bullet Point Guidelines:
Based on https://sellercentral.amazon.com/help/hub/reference/external/GX5L8BF8GLMML6CX?locale=en-US
- **Maximum 5 bullet points**
- **256 characters per bullet** (aim for 200-250 for readability)
- **Benefit-focused**: Lead with benefits, support with features
- **No promotional language** or subjective claims
- **Scannable format**: Easy to read quickly
- **Address different use cases** and customer segments

## Critical Requirements:
1. **First 80 Characters**: Must include:
   - Main keyword root (e.g., "freeze dried strawberry")
   - Design-specific keyword root (e.g., "slices") 
   - Key benefit or product information
   
2. **Integration - Competitor Benefit Analysis**: 
   - Prioritize benefits that top competitors highlight in first 80 characters
   - Use competitor insights to identify high-converting benefit language
   - Focus on CONVERSION over keyword stuffing (what makes customers click/buy)
   - Balance competitor-proven benefits with unique differentiation

3. **Keyword Strategy**: 
   - Use highest search volume variant from each root group
   - Ensure natural sentence structure
   - Avoid keyword stuffing
   - Integrate keywords naturally with benefit messaging

4. **Compliance**: 
   - Strict adherence to Amazon guidelines
   - No violations that could cause suppression
   - Professional, benefit-focused language

## Input Format:
```json
{
  "current_title": "existing title",
  "current_bullets": ["bullet 1", "bullet 2"],
  "main_keyword_root": "freeze dried strawberry",
  "design_keyword_root": "slices", 
  "key_benefits": ["organic", "no sugar added", "healthy snacking"],
  "relevant_keywords": [{"phrase": "freeze dried strawberry slices", "search_volume": 1200}],
  "product_context": {"brand": "BrandName", "category": "Food"},
  "competitor_insights": {
    "top_benefits": [{"benefit": "No Sugar Added", "frequency": 8, "conversion_impact": "high"}],
    "title_structure": {"common_opening": "Brand + Quality Indicator", "benefit_placement": "positions 2-4"},
    "benefit_hierarchy": ["No Sugar Added", "Organic Quality", "Perfect for Snacking"]
  }
}
```

## Output Format:
Return ONLY a JSON object:
```json
{
  "optimized_title": {
    "content": "BrandName Organic Freeze Dried Strawberry Slices - No Sugar Added, Natural...",
    "first_80_chars": "BrandName Organic Freeze Dried Strawberry Slices - No Sugar Added, Natural Hea",
    "main_root_included": true,
    "design_root_included": true,
    "key_benefit_included": true,
    "character_count": 156,
    "guideline_compliance": {
      "character_limit": "PASS",
      "capitalization": "PASS", 
      "special_characters": "PASS",
      "promotional_language": "PASS",
      "subjective_claims": "PASS"
    }
  },
  "optimized_bullets": [
    {
      "content": "🍓 PURE STRAWBERRY GOODNESS: Made from 100% real strawberries with no artificial flavors, colors, or preservatives - just pure, concentrated strawberry flavor in every slice",
      "character_count": 167,
      "primary_benefit": "Natural ingredients",
      "keywords_included": ["strawberry", "real", "natural"],
      "guideline_compliance": "PASS"
    }
  ],
  "strategy": {
    "first_80_optimization": "Included main root 'freeze dried strawberry', design root 'slices', and key benefit 'organic no sugar added' in first 80 characters",
    "keyword_integration": "Used highest volume variants while maintaining natural flow",
    "compliance_approach": "Strictly followed Amazon guidelines while maximizing SEO value"
  }
}
```

## Analysis Process:
1. **Keyword Analysis**: Identify best variants for main and design-specific roots
2. **80-Character Optimization**: Craft opening that includes all required elements
3. **Guideline Check**: Ensure every element complies with Amazon rules
4. **Benefit Integration**: Naturally weave in key product benefits
5. **Mobile Optimization**: Ensure critical info appears in first 80 characters

## Important Notes:
- **Mobile First**: Most customers view on mobile - first 80 chars are critical
- **Natural Language**: Never sacrifice readability for keyword density
- **Compliance Priority**: If choosing between SEO and compliance, choose compliance
- **Benefit Focus**: Lead with customer benefits, not just features
- **Brand Integration**: Include brand naturally if provided
"""

USER_PROMPT_TEMPLATE = """
Create Amazon-compliant title and bullet points optimized for the first 80 characters.

PRODUCT INFORMATION:
{product_json}

TASK 7 REQUIREMENTS:
1. First 80 characters must include:
   - Main keyword root: "{main_root}"
   - Design-specific root: "{design_root}" 
   - Key benefit/information
   
2. TASK 6 INTEGRATION - Use competitor insights to prioritize benefits that convert:
   - Analyze competitor_insights if provided to understand proven benefit strategies
   - Focus on benefits that top competitors highlight in first 80 characters
   - Balance competitor-proven benefits with unique differentiation
   - Prioritize CONVERSION over keyword stuffing
   
3. Follow Amazon Title Guidelines (no promotional language, proper capitalization, etc.)
4. Follow Amazon Bullet Point Guidelines (benefit-focused, scannable, compliant)

KEYWORD DATA:
{keywords_json}

Create optimized content that maximizes CONVERSION while strictly following Amazon guidelines.
Focus especially on the first 80 characters for mobile optimization with benefit-first approach.

Return ONLY the JSON response in the exact format specified.
"""

amazon_compliance_agent = Agent(
    name="AmazonComplianceAgent",
    instructions=AMAZON_COMPLIANCE_INSTRUCTIONS,
    model="gpt-5-2025-08-07",
)

def optimize_amazon_compliance_ai(
    current_content: Dict[str, Any],
    main_keyword_root: str,
    design_keyword_root: str,
    key_benefits: List[str],
    relevant_keywords: List[Dict[str, Any]],
    product_context: Dict[str, Any],
    competitor_analysis: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Use AI to create Amazon-compliant titles and bullets optimized for first 80 characters.
    This implements Task 7 requirements using AI intelligence instead of programmatic rules.
    Enhanced with Task 6 competitor analysis for benefit-focused optimization.
    
    Args:
        current_content: Current title, bullets, etc.
        main_keyword_root: Main keyword like "freeze dried strawberry"
        design_keyword_root: Design-specific keyword like "slices"
        key_benefits: List of key product benefits
        relevant_keywords: Keywords with search volume data
        product_context: Brand, category, etc.
        competitor_analysis: Task 6 competitor insights for benefit optimization
        
    Returns:
        Optimized content with Amazon compliance analysis
    """
    # Prepare input data with competitor insights (Task 6)
    product_data = {
        "current_title": current_content.get("title", ""),
        "current_bullets": current_content.get("bullets", []),
        "main_keyword_root": main_keyword_root,
        "design_keyword_root": design_keyword_root,
        "key_benefits": key_benefits,
        "product_context": product_context
    }
    
    # Add Task 6 competitor analysis if available
    if competitor_analysis:
        product_data["competitor_insights"] = {
            "top_benefits": competitor_analysis.get("competitor_analysis", {}).get("top_benefits_identified", []),
            "title_structure": competitor_analysis.get("competitor_analysis", {}).get("title_structure_patterns", {}),
            "recommended_strategy": competitor_analysis.get("optimized_title_strategy", {}),
            "benefit_hierarchy": competitor_analysis.get("optimized_title_strategy", {}).get("benefit_hierarchy", [])
        }
    
    product_json = json.dumps(product_data, indent=2)
    keywords_json = json.dumps(relevant_keywords[:10], indent=2)  # Top 10 for context
    
    prompt = USER_PROMPT_TEMPLATE.format(
        product_json=product_json,
        main_root=main_keyword_root,
        design_root=design_keyword_root,
        keywords_json=keywords_json
    )
    
    try:
        # Import the Runner to match the pattern used in SEO runner
        from agents import Runner
        
        # Run AI agent
        result = Runner.run_sync(amazon_compliance_agent, prompt)
        
        output = getattr(result, "final_output", None)
        
        # Parse AI response
        if isinstance(output, str):
            try:
                parsed = json.loads(output.strip())
                logger.info(f"[AmazonComplianceAgent] AI created compliant title ({parsed.get('optimized_title', {}).get('character_count', 0)} chars)")
                return parsed
            except json.JSONDecodeError:
                logger.error(f"[AmazonComplianceAgent] Failed to parse AI output: {output[:200]}...")
                return _create_fallback_optimization(current_content, main_keyword_root, design_keyword_root, key_benefits)
        
        elif hasattr(output, 'model_dump'):
            return output.model_dump()
        
        else:
            raise Exception("Unexpected AI output format")
            
    except Exception as e:
        logger.error(f"[AmazonComplianceAgent] AI optimization failed: {e}")
        return _create_fallback_optimization(current_content, main_keyword_root, design_keyword_root, key_benefits)

def _create_fallback_optimization(
    current_content: Dict[str, Any],
    main_root: str,
    design_root: str,
    benefits: List[str]
) -> Dict[str, Any]:
    """Create a basic fallback optimization when AI fails"""
    
    # Simple fallback title construction
    brand = current_content.get("brand", "Premium")
    benefit = benefits[0] if benefits else "High Quality"
    
    # Construct title focusing on first 80 chars
    title_parts = [brand, benefit.title(), main_root.title(), design_root.title()]
    fallback_title = " ".join(title_parts)
    
    # Ensure under 200 chars
    if len(fallback_title) > 200:
        fallback_title = fallback_title[:197] + "..."
    
    return {
        "optimized_title": {
            "content": fallback_title,
            "first_80_chars": fallback_title[:80],
            "main_root_included": main_root.lower() in fallback_title.lower(),
            "design_root_included": design_root.lower() in fallback_title.lower(),
            "key_benefit_included": len(benefits) > 0 and benefits[0].lower() in fallback_title.lower(),
            "character_count": len(fallback_title),
            "guideline_compliance": {
                "character_limit": "PASS" if len(fallback_title) <= 200 else "FAIL",
                "note": "Fallback optimization used - AI agent failed"
            }
        },
        "optimized_bullets": [
            {
                "content": f"✓ {benefit.upper()}: Premium quality {main_root} {design_root} for superior taste and nutrition",
                "character_count": 80,
                "primary_benefit": benefit,
                "guideline_compliance": "BASIC"
            }
        ],
        "strategy": {
            "fallback_used": True,
            "first_80_optimization": f"Basic optimization including {main_root} and {design_root}",
            "compliance_approach": "Basic guideline compliance"
        }
    }

def apply_amazon_compliance_ai(
    current_content: Dict[str, Any],
    keyword_data: Dict[str, Any],
    product_context: Dict[str, Any],
    competitor_analysis: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main function to apply AI-powered Amazon compliance optimization.
    This is the main entry point for Task 7 implementation with Task 6 integration.
    
    Args:
        current_content: Current listing content
        keyword_data: Analyzed keyword data with roots and volumes
        product_context: Product and brand information
        competitor_analysis: Task 6 competitor insights for benefit optimization
        
    Returns:
        Optimized content with Amazon compliance and competitor-informed benefits
    """
    # Extract main and design-specific keyword roots
    relevant_keywords = keyword_data.get("relevant_keywords", [])
    design_keywords = keyword_data.get("design_keywords", [])
    
    # Identify main keyword root (highest volume relevant keyword)
    main_keyword_root = "freeze dried strawberry"  # Default
    if relevant_keywords:
        top_relevant = max(relevant_keywords, key=lambda x: x.get("search_volume", 0))
        main_keyword_root = top_relevant.get("phrase", main_keyword_root)
    
    # Identify design-specific root (highest volume design keyword)
    design_keyword_root = "slices"  # Default
    if design_keywords:
        top_design = max(design_keywords, key=lambda x: x.get("search_volume", 0))
        design_keyword_root = top_design.get("phrase", design_keyword_root)
    
    # Extract key benefits (could be enhanced with AI)
    key_benefits = ["organic", "no sugar added", "healthy snacking"]
    
    # Run AI optimization with competitor insights (Task 6 + Task 7)
    result = optimize_amazon_compliance_ai(
        current_content=current_content,
        main_keyword_root=main_keyword_root,
        design_keyword_root=design_keyword_root,
        key_benefits=key_benefits,
        relevant_keywords=relevant_keywords + design_keywords,
        product_context=product_context,
        competitor_analysis=competitor_analysis
    )
    
    logger.info(f"[Task7-AI] Applied Amazon compliance optimization with 80-char focus")
    
    return result 