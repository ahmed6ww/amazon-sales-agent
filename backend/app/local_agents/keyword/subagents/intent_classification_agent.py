"""
Intent Classification AI Agent

Intelligent replacement for the programmatic intent classification service.
Uses AI to understand purchase intent with superior accuracy vs hardcoded rules.
"""

from agents import Agent, ModelSettings
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

INTENT_CLASSIFICATION_INSTRUCTIONS = """
You are a Purchase Intent Analysis Expert specializing in classifying keyword search intent for Amazon product listings.

## Your Core Mission:
Analyze keyword phrases and assign accurate purchase intent scores (0-3) based on buyer readiness and search purpose.

## Intent Scale (Critical - Follow Exactly):
- **0**: Irrelevant/Outlier - No relation to the product or completely off-topic searches
- **1**: Low Intent - General research, brand-only searches, or single aspect match (product type OR attribute OR use case)
- **2**: Medium Intent - Shows buying consideration, matches exactly two aspects (product type + attribute, or product type + use case, etc.)
- **3**: High Intent - Strong purchase signals, matches all three aspects (product type + attribute + use case) OR has transactional modifiers

## Analysis Framework:

### **Product Type Matching:**
- Does the keyword relate to the actual product category?
- Examples: "freeze dried strawberries" vs "banana chips" (for strawberry product)
- Consider product variants and similar items within the category

### **Attribute Detection:**
- Material qualities: organic, natural, premium, fresh, dried, frozen
- Physical attributes: size, color, texture, packaging format
- Processing methods: freeze-dried, dehydrated, powdered, sliced
- Quality indicators: waterproof, durable, portable, compact

### **Use Case/Benefit Matching:**
- Target audience: kids, adults, babies, professionals
- Usage scenarios: travel, baking, snacking, camping, office
- Benefits: healthy, convenient, long-lasting, nutritious
- Applications: smoothies, cereals, cooking, emergency food

### **Transactional Intent Signals:**
- Strong buy signals: "buy", "purchase", "order", "best price", "cheapest"
- Decision making: "vs", "compare", "review", "top rated", "best"
- Urgency: "fast shipping", "prime", "today", "now"
- Specificity: exact product names, model numbers, specific quantities

### **Brand Consideration:**
- Brand-only searches with no other aspects = Intent 1
- Brand + product aspects = Use normal scoring rules
- Competitor brand searches = Usually Intent 0 (irrelevant)

### **Category-Based Adjustments:**
- If keyword is pre-categorized as "Irrelevant" or "Outlier" → Force Intent 0
- If keyword is "Design-Specific" → Usually Intent 2-3 (shows specific product interest)
- If keyword is "Branded" → Follow brand consideration rules above

## Input Format:
```json
{
  "keyword_phrase": "organic freeze dried strawberry slices",
  "product_context": {
    "title": "BREWER Bulk Freeze Dried Strawberries Slices...",
    "category": "Food",
    "brand": "BREWER",
    "key_features": ["organic", "freeze-dried", "slices", "bulk"]
  },
  "keyword_category": "Relevant",
  "brand_tokens": ["brewer", "organic"]
}
```

## Output Format:
Return ONLY a JSON object:
```json
{
  "intent_score": 2,
  "matched_aspects": ["product_type", "attribute"],
  "reasoning": {
    "product_type_match": true,
    "product_type_explanation": "Matches freeze-dried strawberries product exactly",
    "attribute_match": true,
    "attribute_explanation": "Contains organic and slice attributes relevant to product",
    "use_case_match": false,
    "use_case_explanation": "No specific use case mentioned",
    "transactional_signals": [],
    "brand_analysis": "Generic search, not brand-specific",
    "category_impact": "Relevant category supports intent analysis"
  },
  "confidence": 0.95
}
```

## Analysis Process:
1. **Product Context Analysis**: Extract key product attributes from product context
2. **Keyword Decomposition**: Break down the keyword into semantic components
3. **Aspect Matching**: Check each of the three main aspects (type, attribute, use case)
4. **Intent Scoring**: Apply the 0-3 scale based on aspect matches and signals
5. **Transactional Boost**: Check for strong purchase intent modifiers
6. **Category Verification**: Apply category-based adjustments if needed

## Important Guidelines:
- **Be Conservative**: When uncertain between scores, choose the lower score
- **Context Matters**: Same keyword can have different intent for different products
- **User Journey**: Consider where in the buying journey this search occurs
- **Semantic Understanding**: Look beyond exact word matches to understand intent
- **Commercial vs Informational**: Distinguish between research and purchase intent

## Examples for Reference:
- "freeze dried strawberries" (product match) → Intent 1
- "organic freeze dried strawberries bulk" (product + attributes) → Intent 2  
- "freeze dried strawberries for camping snacks" (product + attribute + use case) → Intent 3
- "buy freeze dried strawberries prime shipping" (transactional signals) → Intent 3
- "banana chips" (different product entirely) → Intent 0
- "freeze dried strawberries vs dehydrated" (comparison research) → Intent 2
"""

USER_PROMPT_TEMPLATE = """
Analyze the purchase intent for this keyword phrase.

KEYWORD TO ANALYZE:
{keyword_data}

PRODUCT CONTEXT:
{product_context}

Provide detailed intent analysis with the exact JSON format specified in your instructions.
Focus on understanding the buyer's search purpose and readiness to purchase.

Return ONLY the JSON response.
"""

intent_classification_agent = Agent(
    name="IntentClassificationAgent",
    instructions=INTENT_CLASSIFICATION_INSTRUCTIONS,
    model="gpt-5-nano-2025-08-07",
    model_settings=ModelSettings(),
    output_type=None,
)

def classify_intent_ai(
    phrase: str,
    scraped_product: Optional[Dict],
    category: Optional[str] = None,
    brand_tokens: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Use AI to classify keyword purchase intent with superior accuracy.
    Replaces the programmatic intent classification with intelligent analysis.
    
    Args:
        phrase: The keyword phrase to analyze
        scraped_product: Product context from scraping
        category: Pre-assigned keyword category (Relevant, Design-Specific, etc.)
        brand_tokens: List of brand terms for brand analysis
        
    Returns:
        Intent analysis with score, reasoning, and confidence
    """
    if not phrase or not phrase.strip():
        return {
            "intent_score": 0,
            "matched_aspects": [],
            "reasoning": {"error": "Empty keyword phrase"},
            "confidence": 1.0
        }
    
    # Prepare keyword data
    keyword_data = {
        "keyword_phrase": phrase.strip(),
        "keyword_category": category or "Unknown",
        "brand_tokens": brand_tokens or []
    }
    
    # Extract product context
    product_context = {}
    if scraped_product:
        elements = scraped_product.get("elements", {})
        
        product_context = {
            "title": elements.get("productTitle", {}).get("text", [""])[0] if elements.get("productTitle", {}).get("text") else "",
            "category": scraped_product.get("category", ""),
            "brand": elements.get("productOverview_feature_div", {}).get("kv", {}).get("Brand", ""),
            "key_features": []
        }
        
        # Extract key features from title and bullets
        title = product_context["title"].lower() if product_context["title"] else ""
        bullets = elements.get("feature-bullets", {}).get("bullets", [])
        
        # Simple feature extraction (AI will do the intelligent analysis)
        if title:
            product_context["key_features"] = [word for word in title.split() if len(word) > 3][:10]
    
    # Format prompt
    prompt = USER_PROMPT_TEMPLATE.format(
        keyword_data=json.dumps(keyword_data, indent=2),
        product_context=json.dumps(product_context, indent=2)
    )
    
    try:
        # Run AI agent
        from agents import Runner
        result = Runner.run_sync(intent_classification_agent, prompt)
        output = getattr(result, "final_output", None)
        
        # Parse AI response
        if isinstance(output, str):
            try:
                parsed = json.loads(output.strip())
                intent_score = parsed.get("intent_score", 0)
                logger.info(f"[IntentClassificationAgent] AI classified '{phrase}' as intent {intent_score}")
                return parsed
            except json.JSONDecodeError:
                logger.error(f"[IntentClassificationAgent] Failed to parse AI output: {output[:200]}...")
                return _create_fallback_intent_analysis(phrase, category)
        
        elif hasattr(output, 'model_dump'):
            return output.model_dump()
        
        else:
            raise Exception("Unexpected AI output format")
            
    except Exception as e:
        logger.error(f"[IntentClassificationAgent] AI analysis failed for '{phrase}': {e}")
        return _create_fallback_intent_analysis(phrase, category)

def _create_fallback_intent_analysis(phrase: str, category: Optional[str] = None) -> Dict[str, Any]:
    """Create a basic fallback intent analysis when AI fails"""
    
    # Simple fallback logic based on category
    if category in ["Irrelevant", "Outlier"]:
        intent_score = 0
    elif category == "Design-Specific":
        intent_score = 2
    elif category == "Relevant":
        intent_score = 1
    elif category == "Branded":
        intent_score = 1
    else:
        intent_score = 1  # Default conservative score
    
    return {
        "intent_score": intent_score,
        "matched_aspects": [],
        "reasoning": {
            "fallback_used": True,
            "category_based_scoring": category,
            "explanation": "AI analysis failed, used category-based fallback"
        },
        "confidence": 0.3  # Low confidence for fallback
    }

def apply_intent_classification_ai(
    keywords: List[Dict[str, Any]],
    scraped_product: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Apply AI-powered intent classification to a list of keywords.
    Main entry point for replacing programmatic intent classification.
    
    Args:
        keywords: List of keyword dicts with phrase, category, etc.
        scraped_product: Product context for analysis
        
    Returns:
        Keywords enhanced with AI-powered intent scores and analysis
    """
    if not keywords:
        return []
    
    enhanced_keywords = []
    
    # Extract brand tokens from product context
    brand_tokens = []
    if scraped_product:
        brand = scraped_product.get("elements", {}).get("productOverview_feature_div", {}).get("kv", {}).get("Brand", "")
        if brand:
            brand_tokens = [brand.lower()]
    
    for keyword_item in keywords:
        phrase = keyword_item.get("phrase", "")
        category = keyword_item.get("category", "")
        
        # Get AI intent analysis
        intent_analysis = classify_intent_ai(
            phrase=phrase,
            scraped_product=scraped_product,
            category=category,
            brand_tokens=brand_tokens
        )
        
        # Create enhanced keyword item
        enhanced_item = {
            **keyword_item,
            "intent_score": intent_analysis.get("intent_score", 0),
            "intent_analysis": intent_analysis
        }
        
        enhanced_keywords.append(enhanced_item)
    
    logger.info(f"[IntentClassificationAgent] Enhanced {len(enhanced_keywords)} keywords with AI intent analysis")
    
    return enhanced_keywords 