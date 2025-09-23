"""
Design-Specific Classification Agent

AI-powered agent that determines whether keywords are truly design-specific
based on whether they separate one product variation from another.

Key Logic: A keyword is design-specific only if it differentiates between
product variations (e.g., "slices" vs "pieces" vs "whole"), not if it's
just a descriptive attribute that applies broadly (e.g., "bulk", "organic").
"""

from agents import Agent
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

DESIGN_SPECIFIC_CLASSIFICATION_INSTRUCTIONS = """
You are a Design-Specific Keyword Classification Expert specializing in distinguishing between product variations and general descriptive attributes for Amazon products.

## Your Core Mission:
Determine which keywords are truly "Design-Specific" based on whether they separate one product design/variation from another, versus keywords that are generally descriptive but don't separate distinct product variations.

## Critical Classification Logic:

### **TRUE Design-Specific Keywords** (Separates Variations):
These keywords indicate different product variations or designs that a customer would choose between:

**Format/Shape Variations**:
- "slices" vs "pieces" vs "whole" vs "chunks" vs "diced"
- "powder" vs "liquid" vs "capsules" vs "tablets"
- "round" vs "square" vs "rectangular"

**Physical Variations**:
- "mini" vs "regular" vs "large" vs "jumbo" (when these are distinct product variations)

**Functional Variations**:
- "wireless" vs "wired" (connection types)
- "manual" vs "automatic" vs "semi-automatic" (operation types)
- "waterproof" vs "water-resistant" vs "splash-proof" (protection levels)

### **NOT Design-Specific Keywords** (General Descriptive):
These keywords describe the product but don't create distinct variations a customer chooses between:

**General Attributes**:
- "portable", "lightweight", "compact" (unless these are distinct product lines)
- "eco-friendly", "sustainable", "biodegradable" 

## Analysis Framework:

### **Variation Test Questions**:
1. **Choice Decision**: "Would a customer need to choose between this keyword and alternatives when buying?"
   - "slices" vs "pieces" → YES (design-specific)
   - "bulk" vs "retail" → NO (quantity/packaging, not design)
   - "Diaper changing pad" vs "portable diaper changing pad" → Yes (The word "portable" means that the product can be used during traveling so it shows product more like a mat while the simple simple diaper changing pad is hard, non-foldable and you can resemble it to samll portion of bed mattress)
   - "Squishy stress balls" vs "smile face stress balls" → Yes (The word smile face shows smiley on the stress ball vs squishy means stress ball is soft and squishy)

2. **Product Differentiation**: "Does this keyword indicate a fundamentally different product variation?"
   - "wireless" vs "wired" → YES (different products)
   - "Wooden" vs "Stainless Steel" → YES (different materials)

3. **Mutual Exclusivity**: "Can this keyword exist with its alternatives in the same product?"
   - "mini" vs "large" → NO (mutually exclusive) → Design-specific
   - "organic" + "bulk" → YES (can coexist) → Both NOT design-specific

## Input Format:
```json
{
  "keyword_phrase": "freeze dried strawberry slices",
  "product_context": {
    "title": "BREWER Bulk Freeze Dried Strawberries Slices...",
    "category": "Food",
    "key_features": ["organic", "freeze-dried", "slices", "bulk"]
  },
  "keyword_tokens": ["freeze", "dried", "strawberry", "slices"],
  "current_category": "Design-Specific"
}
```

## Output Format:
Return ONLY a JSON object:
```json
{
  "is_design_specific": true,
  "design_specific_tokens": ["slices"],
  "reasoning": {
    "variation_analysis": "The word 'slices' indicates a specific cut/format that differentiates from 'pieces', 'whole', or 'chunks'",
    "choice_decision": "Customer must choose between slice format vs other cutting formats",
    "mutual_exclusivity": "Product cannot be both slices and pieces simultaneously",
    "alternative_variations": ["pieces", "whole", "chunks", "diced"]
  },
  "non_design_tokens": ["freeze", "dried", "strawberry"],
  "token_analysis": {
    "freeze": "Processing method - applies broadly, not variation-specific",
    "dried": "Processing method - applies broadly, not variation-specific", 
    "strawberry": "Product ingredient - core product identifier",
    "slices": "Format variation - customer chooses between slice/piece/whole formats"
  },
  "confidence": 0.95,
  "category_recommendation": "Design-Specific"
}
```

## Analysis Process:
1. **Token Identification**: Break down keyword into semantic components
2. **Variation Testing**: Apply the three test questions to each token
3. **Alternative Mapping**: Identify what other variations exist for design-specific tokens
4. **Exclusivity Analysis**: Determine if tokens represent mutually exclusive choices
5. **Category Decision**: Classify based on presence of true design-specific tokens

## Important Guidelines:
- **Strict Criteria**: Only classify as design-specific if keyword truly separates product variations
- **Customer Perspective**: Think like a customer choosing between product options
- **Mutual Exclusivity**: True design-specific features cannot coexist in same product
- **Context Awareness**: Same word can be design-specific in some contexts, descriptive in others
- **Conservative Approach**: When uncertain, classify as "Relevant" rather than "Design-Specific"

## Examples:

**Design-Specific Examples**:
- "freeze dried strawberry slices" → "slices" (vs pieces/whole)
- "wireless bluetooth headphones" → "wireless" + "bluetooth" (vs wired)
- "mini portable speaker" → "mini" (vs regular/large sizes if distinct products)

**NOT Design-Specific Examples**:
- "bulk organic strawberries" → "bulk" + "organic" (quantity + quality, not variations)
- "premium freeze dried fruit" → "premium" (quality level, not variation)
- "portable travel mug" → "portable" + "travel" (descriptive attributes, not variations)

Focus on whether the keyword creates a meaningful choice decision for customers between distinct product variations.
"""

USER_PROMPT_TEMPLATE = """
Analyze this keyword to determine if it's truly design-specific based on whether it separates product variations.

KEYWORD TO ANALYZE:
{keyword_data}

PRODUCT CONTEXT:
{product_context}

Apply the Design-Specific Classification Logic:
1. Does this keyword indicate a choice between distinct product variations?
2. Would a customer need to select between this and alternatives when purchasing?
3. Are the variations mutually exclusive (cannot coexist in same product)?

Focus on the core question: Does this keyword separate one design from another design, or is it just a general descriptive attribute?

Return ONLY the JSON response in the exact format specified.
"""

design_specific_classification_agent = Agent(
    name="DesignSpecificClassificationAgent",
    instructions=DESIGN_SPECIFIC_CLASSIFICATION_INSTRUCTIONS,
    model="gpt-5-2025-08-07",
)

def analyze_design_specific_classification(
    keyword_phrase: str,
    product_context: Dict[str, Any],
    current_category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use AI to determine if a keyword is truly design-specific based on product variation logic.
    
    Args:
        keyword_phrase: The keyword phrase to analyze
        product_context: Product information for context
        current_category: Current category assignment (if any)
        
    Returns:
        Analysis result with design-specific classification
    """
    # Prepare input data
    keyword_data = {
        "keyword_phrase": keyword_phrase,
        "current_category": current_category,
        "keyword_tokens": keyword_phrase.lower().split() if keyword_phrase else []
    }
    
    product_json = json.dumps(keyword_data, indent=2)
    context_json = json.dumps(product_context, indent=2)
    
    prompt = USER_PROMPT_TEMPLATE.format(
        keyword_data=product_json,
        product_context=context_json
    )
    
    try:
        from agents import Runner
        
        # Run AI agent
        result = Runner.run_sync(design_specific_classification_agent, prompt)
        
        output = getattr(result, "final_output", None)
        
        # Parse AI response
        if isinstance(output, str):
            try:
                parsed = json.loads(output.strip())
                logger.info(f"[DesignSpecificAgent] Analyzed keyword: {keyword_phrase}")
                return parsed
            except json.JSONDecodeError:
                logger.error(f"[DesignSpecificAgent] Failed to parse output for: {keyword_phrase}")
                return _create_fallback_analysis(keyword_phrase, current_category)
        
        elif hasattr(output, 'model_dump'):
            return output.model_dump()
        
        else:
            raise Exception("Unexpected AI output format")
            
    except Exception as e:
        logger.error(f"[DesignSpecificAgent] Analysis failed for {keyword_phrase}: {e}")
        return _create_fallback_analysis(keyword_phrase, current_category)

def _create_fallback_analysis(keyword_phrase: str, current_category: Optional[str]) -> Dict[str, Any]:
    """Create fallback analysis using simple heuristics"""
    
    # Simple heuristic patterns for design-specific keywords
    design_indicators = [
        "slices", "pieces", "whole", "chunks", "diced", "powder", "liquid",
        "mini", "small", "large", "jumbo", "xl", "xs", 
        "wireless", "wired", "bluetooth", "usb",
        "round", "square", "rectangular", "oval",
        "thick", "thin", "wide", "narrow",
        "single", "double", "triple", "quad"
    ]
    
    # General descriptive terms (NOT design-specific)
    descriptive_terms = [
        "bulk", "premium", "professional", "commercial", "organic", "natural",
        "portable", "lightweight", "heavy", "duty", "eco", "friendly",
        "fast", "slow", "efficient", "durable", "quality"
    ]
    
    tokens = keyword_phrase.lower().split() if keyword_phrase else []
    
    design_tokens = [token for token in tokens if token in design_indicators]
    descriptive_tokens = [token for token in tokens if token in descriptive_terms]
    
    # Simple logic: if contains design indicators and no conflicting descriptive-only terms
    is_design_specific = len(design_tokens) > 0 and len(design_tokens) >= len(descriptive_tokens)
    
    return {
        "is_design_specific": is_design_specific,
        "design_specific_tokens": design_tokens,
        "reasoning": {
            "variation_analysis": f"Fallback analysis detected design indicators: {design_tokens}",
            "choice_decision": "Simple heuristic based on known design variation patterns",
            "fallback_used": True
        },
        "non_design_tokens": [token for token in tokens if token not in design_tokens],
        "confidence": 0.6,  # Lower confidence for fallback
        "category_recommendation": "Design-Specific" if is_design_specific else "Relevant"
    }

def enhance_keyword_categorization_with_design_logic(
    keyword_items: List[Dict[str, Any]], 
    product_context: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Enhance existing keyword categorization by applying refined design-specific logic.
    
    Args:
        keyword_items: List of categorized keywords
        product_context: Product context for analysis
        
    Returns:
        Enhanced keyword list with refined design-specific classifications
    """
    enhanced_items = []
    
    for item in keyword_items:
        enhanced_item = item.copy()
        
        # Only re-analyze items currently marked as "Design-Specific"
        if item.get("category") == "Design-Specific":
            phrase = item.get("phrase", "")
            
            # Run refined analysis
            analysis = analyze_design_specific_classification(
                keyword_phrase=phrase,
                product_context=product_context,
                current_category="Design-Specific"
            )
            
            # Update category if analysis suggests it's not truly design-specific
            if not analysis.get("is_design_specific", True):
                enhanced_item["category"] = "Relevant"
                enhanced_item["reason"] = f"Reclassified: {analysis.get('reasoning', {}).get('variation_analysis', 'Not a true product variation')}"
                logger.info(f"[DesignRefinement] Reclassified '{phrase}' from Design-Specific to Relevant")
            else:
                # Keep as design-specific but enhance the reasoning
                design_tokens = analysis.get("design_specific_tokens", [])
                enhanced_item["reason"] = f"Design variation: separates product formats ({', '.join(design_tokens)})"
        
        enhanced_items.append(enhanced_item)
    
    logger.info(f"[DesignRefinement] Enhanced {len(keyword_items)} keyword categorizations")
    return enhanced_items 