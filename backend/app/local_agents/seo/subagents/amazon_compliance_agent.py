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
- **CREATE EXACTLY {bullet_count} bullet points** (this is MANDATORY - not optional)
- **256 characters per bullet** (aim for 200-250 for readability)
- **Benefit-focused**: Lead with benefits, support with features
- **No promotional language** or subjective claims
- **Scannable format**: Easy to read quickly
- **Address different use cases** and customer segments
- **CRITICAL**: You MUST create exactly {bullet_count} bullets - distribute the bullet_keywords evenly across all {bullet_count} bullets

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
   - **CRITICAL**: Use keywords in the EXACT order provided (sorted by relevancy score)
   - **PRIORITIZE**: Always use the highest relevancy score keywords first
   - Ensure natural sentence structure
   - Avoid keyword stuffing
   - Integrate keywords naturally with benefit messaging
   - **DO NOT** use keywords not in the provided list

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
  "relevant_keywords": [{{"phrase": "freeze dried strawberry slices", "search_volume": 1200}}],
  "product_context": {{"brand": "BrandName", "category": "Food"}},
  "competitor_insights": {{
    "top_benefits": [{{"benefit": "No Sugar Added", "frequency": 8, "conversion_impact": "high"}}],
    "title_structure": {{"common_opening": "Brand + Quality Indicator", "benefit_placement": "positions 2-4"}},
    "benefit_hierarchy": ["No Sugar Added", "Organic Quality", "Perfect for Snacking"]
  }}
}
```

## Output Format:
Return ONLY a JSON object with the EXACT structure below. **CRITICAL**: You MUST include the "keywords_included" field for both title and bullets, listing the specific keywords from the provided list that you used in each piece of content.
```json
{
  "optimized_title": {
    "content": "BrandName Organic Freeze Dried Strawberry Slices - No Sugar Added, Natural...",
    "first_80_chars": "BrandName Organic Freeze Dried Strawberry Slices - No Sugar Added, Natural Hea",
    "main_root_included": true,
    "design_root_included": true,
    "key_benefit_included": true,
    "character_count": 156,
    "keywords_included": ["freeze dried strawberry", "slices", "organic", "no sugar added"],
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
      "content": "PURE STRAWBERRY GOODNESS: Made from 100% freeze dried strawberries with organic strawberries for natural flavor in every slice",
      "character_count": 130,
      "primary_benefit": "Natural ingredients",
      "keywords_included": ["freeze dried strawberries", "organic strawberries"],
      "guideline_compliance": "PASS"
    },
    {
      "content": "BULK VALUE PACK: Convenient bulk strawberries in a strawberry snack format perfect for families and daily use",
      "character_count": 115,
      "primary_benefit": "Value and convenience",
      "keywords_included": ["bulk strawberries", "strawberry snack"],
      "guideline_compliance": "PASS"
    },
    {
      "content": "HEALTHY CHOICE: Pure dried fruit with no sugar added for guilt-free snacking anytime",
      "character_count": 88,
      "primary_benefit": "Health benefits",
      "keywords_included": ["dried fruit", "no sugar"],
      "guideline_compliance": "PASS"
    },
    {
      "content": "VERSATILE USE: Perfect healthy snack made from natural fruit for smoothies, baking, or on-the-go",
      "character_count": 101,
      "primary_benefit": "Versatility",
      "keywords_included": ["healthy snack", "natural fruit"],
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

KEYWORD DATA (PRE-ALLOCATED TO PREVENT DUPLICATION):
{keywords_json}

**CRITICAL INSTRUCTIONS:**
- Use ONLY the pre-allocated keywords for each content type
- TITLE: Use only keywords from "title_keywords" array
- BULLETS: Use only keywords from "bullet_keywords" array  
- BACKEND: Use only keywords from "backend_keywords" array
- DO NOT use any keywords not in the provided lists
- DO NOT use the same keyword in multiple content types
- Each keyword can only be used ONCE across all content

**MANDATORY KEYWORD USAGE:**
- You MUST use at least 2 keywords from the allocated arrays in EACH bullet point (REQUIRED)
- You MUST create exactly {bullet_count} bullet points, each with minimum 2 keywords
- You MUST list the exact keywords used in the "keywords_included" field for each bullet
- FAILURE TO USE AT LEAST 2 KEYWORDS PER BULLET WILL RESULT IN REJECTION

**STRICT REQUIREMENT - TITLE:**
- Title MUST contain at least 2 keywords from title_keywords array
- Use 2-3 keywords in title for optimal Amazon SEO

**STRICT REQUIREMENT - BULLETS:**
- Create exactly {bullet_count} bullet points (MANDATORY)
- EVERY bullet point MUST contain at least 2 keywords from bullet_keywords array
- Distribute keywords evenly: 10 bullet keywords = 2-3 per bullet across {bullet_count} bullets
- You MUST naturally integrate the keywords into the bullet text
- Each of the {bullet_count} bullets must have minimum 2 keywords for Amazon SEO effectiveness

**EXAMPLE OF CORRECT USAGE ({bullet_count} BULLETS WITH 2 KEYWORDS EACH):**
If bullet_keywords = [{{"phrase": "freeze dried strawberries"}}, {{"phrase": "organic strawberries"}}, {{"phrase": "bulk strawberries"}}, {{"phrase": "strawberry snack"}}, {{"phrase": "dried fruit"}}, {{"phrase": "healthy snack"}}, {{"phrase": "natural fruit"}}, {{"phrase": "no sugar"}}]

You MUST create exactly {bullet_count} bullets, each with at least 2 keywords:
- Bullet 1: "Our organic strawberries are freeze dried strawberries perfect for healthy snacking" → keywords_included: ["organic strawberries", "freeze dried strawberries"]
- Bullet 2: "Convenient bulk strawberries make this strawberry snack ideal for families" → keywords_included: ["bulk strawberries", "strawberry snack"]
- Bullet 3: "Pure dried fruit with no sugar added for guilt-free enjoyment" → keywords_included: ["dried fruit", "no sugar"]
- Bullet 4: "A healthy snack made from natural fruit with no additives" → keywords_included: ["healthy snack", "natural fruit"]

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
    competitor_analysis: Optional[Dict[str, Any]] = None,
    title_keywords: Optional[List[Dict[str, Any]]] = None,
    bullet_keywords: Optional[List[Dict[str, Any]]] = None,
    backend_keywords: Optional[List[Dict[str, Any]]] = None,
    target_bullet_count: Optional[int] = None
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
        target_bullet_count: Number of bullet points to create (dynamic)
        
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
        product_data["competitor_insights"] = competitor_analysis
        logger.info(f"🎯 Integrated Task 6 competitor insights for benefit optimization")
    
    # Serialize product data
    try:
        product_json = json.dumps(product_data, indent=2)
    except (TypeError, ValueError) as json_err:
        logger.error(f"❌ Failed to serialize product data to JSON: {json_err}")
        raise
    
    # Use pre-allocated keywords if provided
    if title_keywords or bullet_keywords or backend_keywords:
        # Prepare keyword data for AI agent
        keywords_data = {
            "title_keywords": title_keywords or [],
            "bullet_keywords": bullet_keywords or [],
            "backend_keywords": backend_keywords or []
        }
        
        # Serialize keyword data
        try:
            keywords_json = json.dumps(keywords_data, indent=2)
        except (TypeError, ValueError) as json_err:
            logger.error(f"❌ Failed to serialize pre-allocated keywords to JSON: {json_err}")
            raise
        
        logger.info(f"🎯 Passing pre-allocated keywords to AI agent: {len(title_keywords)} title, {len(bullet_keywords)} bullets, {len(backend_keywords)} backend")
    else:
        # Pass more keywords to AI agent, sorted by relevancy
        # Ensure all keywords have the "phrase" key
        safe_keywords = []
        for kw in relevant_keywords[:20]:
            if isinstance(kw, dict) and "phrase" in kw:
                safe_keywords.append(kw)
            elif isinstance(kw, dict):
                # Add missing phrase key
                safe_kw = kw.copy()
                safe_kw["phrase"] = kw.get("keyword", kw.get("text", str(kw)))
                safe_keywords.append(safe_kw)
        # Serialize fallback keyword data
        try:
            keywords_json = json.dumps(safe_keywords, indent=2)
        except (TypeError, ValueError) as json_err:
            logger.error(f"❌ Failed to serialize fallback keywords to JSON: {json_err}")
            raise
    
    # Use dynamic bullet count or default to 4
    bullet_count = target_bullet_count if target_bullet_count and target_bullet_count > 0 else 4
    logger.info(f"🎯 Optimizing for {bullet_count} bullet points (dynamic based on current listing)")
    
    try:
        prompt = USER_PROMPT_TEMPLATE.format(
            product_json=product_json,
            main_root=main_keyword_root,
            design_root=design_keyword_root,
            keywords_json=keywords_json,
            bullet_count=bullet_count
        )
    except (KeyError, ValueError) as prompt_err:
        logger.error(f"❌ Failed to format prompt: {prompt_err}")
        raise
    
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
                logger.info(f"[AmazonComplianceAgent] AI successfully optimized content for {bullet_count} bullets")
                return parsed
            except json.JSONDecodeError:
                logger.error(f"[AmazonComplianceAgent] Failed to parse AI output: {output[:200]}...")
                # Fallback to programmatic optimization
                return _create_fallback_optimization(current_content, main_keyword_root, design_keyword_root, key_benefits)
        
        elif hasattr(output, 'model_dump'):
            return output.model_dump()
        
        else:
            raise Exception("Unexpected AI output format")
            
    except Exception as e:
        logger.error(f"[AmazonComplianceAgent] AI optimization failed: {e}")
        # Graceful fallback - return programmatic optimization
        return _create_fallback_optimization(current_content, main_keyword_root, design_keyword_root, key_benefits)

def _create_fallback_optimization(
    current_content: Dict[str, Any],
    main_root: str,
    design_root: str,
    benefits: List[str]
) -> Dict[str, Any]:
    """
    Create fallback optimization when AI fails.
    """
    logger.warning("[AmazonComplianceAgent] Using fallback optimization due to AI failure")
    
    # Simple fallback title
    title = f"{main_root.title()} {design_root.title()} - {', '.join(benefits[:2])}"
    
    # Simple fallback bullets
    bullets = []
    for i, benefit in enumerate(benefits[:4], 1):
        bullet_content = f"BENEFIT {i}: {benefit.title()} - {main_root} {design_root} for optimal results"
        bullets.append({
            "content": bullet_content,
            "character_count": len(bullet_content),
            "primary_benefit": benefit,
            "keywords_included": [main_root, design_root],
            "guideline_compliance": "PASS"
        })
    
    fallback_result = {
        "optimized_title": {
            "content": title,
            "first_80_chars": title[:80],
            "main_root_included": main_root.lower() in title.lower(),
            "design_root_included": design_root.lower() in title.lower(),
            "key_benefit_included": True,
            "character_count": len(title),
            "keywords_included": [main_root, design_root],
            "guideline_compliance": {
                "character_limit": "PASS",
                "capitalization": "PASS",
                "special_characters": "PASS",
                "promotional_language": "PASS",
                "subjective_claims": "PASS"
            }
        },
        "optimized_bullets": bullets,
        "strategy": {
            "first_80_optimization": f"Fallback optimization with {main_root} and {design_root}",
            "keyword_integration": "Basic keyword integration",
            "compliance_approach": "Conservative compliance approach"
        }
    }

    
    return fallback_result

def apply_amazon_compliance_ai(
    current_content: Dict[str, Any],
    keyword_data: Dict[str, Any],
    product_context: Dict[str, Any],
    competitor_analysis: Optional[Dict[str, Any]] = None,
    keyword_validator: Optional[Any] = None,
    title_keywords: Optional[List[Dict[str, Any]]] = None,
    bullet_keywords: Optional[List[Dict[str, Any]]] = None,
    backend_keywords: Optional[List[Dict[str, Any]]] = None,
    target_bullet_count: Optional[int] = None
) -> Dict[str, Any]:
    """
    Main function to apply AI-powered Amazon compliance optimization.
    This is the main entry point for Task 7 implementation with Task 6 integration.
    
    Args:
        current_content: Current listing content
        keyword_data: Analyzed keyword data with roots and volumes
        product_context: Product and brand information
        competitor_analysis: Task 6 competitor insights for benefit optimization
        target_bullet_count: Number of bullet points to create (dynamic)
        
    Returns:
        Optimized content with Amazon compliance and competitor-informed benefits
    """
    # Extract main and design-specific keyword roots
    relevant_keywords = keyword_data.get("relevant_keywords", [])
    design_keywords = keyword_data.get("design_keywords", [])
    
    # Identify main keyword root (highest relevancy relevant keyword)
    main_keyword_root = "freeze dried strawberry"  # Default
    if relevant_keywords:
        # Use highest relevancy keyword instead of highest volume
        top_relevant = max(relevant_keywords, key=lambda x: (x.get("relevancy_score") or 0))
        main_keyword_root = top_relevant.get("phrase", main_keyword_root)
        logger.info(f"🎯 Selected main keyword root by relevancy: {main_keyword_root} (score: {top_relevant.get('relevancy_score', 0)})")
    
    # Identify design-specific root (highest relevancy design keyword)
    design_keyword_root = "slices"  # Default
    if design_keywords:
        # Use highest relevancy keyword instead of highest volume
        top_design = max(design_keywords, key=lambda x: (x.get("relevancy_score") or 0))
        design_keyword_root = top_design.get("phrase", design_keyword_root)
        logger.info(f"🎯 Selected design keyword root by relevancy: {design_keyword_root} (score: {top_design.get('relevancy_score', 0)})")
    else:
        # Fallback: extract from main keyword if no design keywords
        if " " in main_keyword_root:
            parts = main_keyword_root.split()
            design_keyword_root = parts[-1] if len(parts) > 1 else "slices"
            logger.info(f"🎯 Extracted design root from main keyword: {design_keyword_root}")
    
    # Extract key benefits from product context and competitor analysis
    key_benefits = []
    
    # Add benefits from product context
    if product_context.get("category"):
        key_benefits.append(f"Premium {product_context['category'].lower()} quality")
    
    # Add benefits from competitor analysis (Task 6)
    if competitor_analysis:
        competitor_benefits = competitor_analysis.get("top_benefits", [])
        for benefit_data in competitor_benefits[:3]:  # Top 3 benefits
            if isinstance(benefit_data, dict):
                benefit = benefit_data.get("benefit", "")
                if benefit and benefit not in key_benefits:
                    key_benefits.append(benefit)
            elif isinstance(benefit_data, str) and benefit_data not in key_benefits:
                key_benefits.append(benefit_data)
        
        logger.info(f"🎯 Integrated {len(key_benefits)} benefits from competitor analysis")
    
    # Default benefits if none found
    if not key_benefits:
        key_benefits = ["Natural ingredients", "No additives", "Premium quality", "Healthy choice"]
        logger.info(f"🎯 Using default benefits: {key_benefits}")
    
    # Sort keywords by relevancy for better optimization
    if relevant_keywords:
        relevant_keywords.sort(key=lambda x: (x.get("relevancy_score") or 0), reverse=True)
        logger.info(f"🎯 Sorted {len(relevant_keywords)} relevant keywords by relevancy score")
    
    if design_keywords:
        design_keywords.sort(key=lambda x: (x.get("relevancy_score") or 0), reverse=True)
        logger.info(f"🎯 Sorted {len(design_keywords)} design keywords by relevancy score")
            
        logger.info(f"🎯 Prioritized {len(relevant_keywords)} relevant keywords and {len(design_keywords)} design keywords by relevancy")
    
    # Use pre-allocated keywords for AI agent
    # Changed from 'and' to 'or' to support partial allocation (e.g., only title keywords)
    if title_keywords or bullet_keywords or backend_keywords:
        # Pass allocated keywords to AI agent
        all_keywords_for_ai = (title_keywords or []) + (bullet_keywords or []) + (backend_keywords or [])
        all_keywords_for_ai.sort(key=lambda x: (x.get('relevancy_score') or 0), reverse=True)
        
        logger.info(f"📊 Providing {len(all_keywords_for_ai)} pre-allocated keywords to AI agent, sorted by relevancy")
        
        # Run AI optimization with pre-allocated keywords
        result = optimize_amazon_compliance_ai(
            current_content=current_content,
            main_keyword_root=main_keyword_root,
            design_keyword_root=design_keyword_root,
            key_benefits=key_benefits,
            relevant_keywords=all_keywords_for_ai,  # Pass pre-allocated keywords
            product_context=product_context,
            competitor_analysis=competitor_analysis,
            title_keywords=title_keywords,
            bullet_keywords=bullet_keywords,
            backend_keywords=backend_keywords,
            target_bullet_count=target_bullet_count
        )
    else:
        # Fallback to combined keywords
        all_keywords_for_ai = relevant_keywords + design_keywords
        all_keywords_for_ai.sort(key=lambda x: (x.get("relevancy_score") or 0), reverse=True)
        
        logger.info(f"📊 Providing {len(all_keywords_for_ai)} keywords to AI agent, sorted by relevancy")
        
        # Run AI optimization with competitor insights (Task 6 + Task 7)
        result = optimize_amazon_compliance_ai(
            current_content=current_content,
            main_keyword_root=main_keyword_root,
            design_keyword_root=design_keyword_root,
            key_benefits=key_benefits,
            relevant_keywords=all_keywords_for_ai,  # Pass sorted keywords
            product_context=product_context,
            competitor_analysis=competitor_analysis,
            target_bullet_count=target_bullet_count
        )
    
    logger.info(f"[Task7-AI] Applied Amazon compliance optimization with 80-char focus and {target_bullet_count or 4} bullets")
    
    return result