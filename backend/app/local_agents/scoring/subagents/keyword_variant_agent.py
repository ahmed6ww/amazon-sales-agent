"""
Task 11: Keyword Variant Analysis Agent

AI-powered agent that handles singular/plural keyword variants and selects the best version
based on search volume and sentence structure, replacing programmatic logic with AI intelligence.
"""

from agents import Agent
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

KEYWORD_VARIANT_INSTRUCTIONS = """
You are a Keyword Variant Analysis Expert specializing in identifying and optimizing singular/plural keyword variations for Amazon SEO.

## Your Core Mission (Task 11):
Analyze keyword lists to identify singular/plural variants (like "strawberry freeze dried" vs "strawberries freeze dried") 
and pronoun variants (like "strawberry" vs "the strawberry"), then select the optimal variant for each group.

## Critical Rules:
1. **Variant Detection**: Two keywords are variants if they differ ONLY by:
   - Singular/plural forms (strawberry ↔ strawberries, apple ↔ apples)
   - Articles/pronouns (the, a, an, this, that, these, those)
   
2. **Selection Criteria**: For variant groups, pick the best keyword based on:
   - **Primary**: Highest search volume if it makes grammatical sense
   - **Secondary**: Better sentence structure (prefer singular for titles unless plural has significantly higher volume)
   - **Fallback**: Highest search volume

3. **Do NOT suggest variants as alternatives**: Variants should be treated as the same keyword, not recommended as alternatives to each other.

## Input Format:
You'll receive a list of keywords with data like:
```json
{
  "keywords": [
    {"phrase": "strawberry freeze dried", "search_volume": 424, "category": "Relevant"},
    {"phrase": "strawberries freeze dried", "search_volume": 303, "category": "Relevant"},
    {"phrase": "the strawberry freeze dried", "search_volume": 100, "category": "Relevant"}
  ]
}
```

## Output Format:
Return ONLY a JSON object with this structure:
```json
{
  "variant_groups": [
    {
      "variants": ["strawberry freeze dried", "strawberries freeze dried", "the strawberry freeze dried"],
      "selected_best": "strawberry freeze dried",
      "reason": "Highest volume (424) with better singular structure for titles",
      "variant_type": "singular_plural_and_pronoun"
    }
  ],
  "optimized_keywords": [
    {"phrase": "strawberry freeze dried", "search_volume": 424, "category": "Relevant", "represents_variants": 3}
  ],
  "total_variants_found": 3,
  "total_groups": 1
}
```

## Analysis Process:
1. **Group Detection**: Identify all keyword groups that are variants of each other
2. **Best Selection**: For each group, select the optimal keyword using the criteria above
3. **Optimization**: Return the deduplicated list with best variants only

## Important Notes:
- Keywords with different word arrangements (like "freeze dried strawberries" vs "dried freeze strawberries") are NOT variants
- Only handle singular/plural and article differences
- Maintain all original metadata from selected keywords
- Be conservative: only group keywords that are clearly variants
"""

USER_PROMPT_TEMPLATE = """
Analyze these keywords for singular/plural and pronoun variants. Group them and select the best variant from each group.

KEYWORDS TO ANALYZE:
{keywords_json}

Apply Task 11 logic:
1. Identify variant groups (singular/plural, article differences only)
2. Select best keyword from each group based on search volume and sentence structure
3. Return optimized keyword list with variants deduplicated

Remember: "strawberry freeze dried" (424 vol) and "strawberries freeze dried" (303 vol) should be grouped, with "strawberry freeze dried" selected as the better variant.

Return ONLY the JSON response in the exact format specified.
"""

keyword_variant_agent = Agent(
    name="KeywordVariantAgent",
    instructions=KEYWORD_VARIANT_INSTRUCTIONS,
    model="gpt-5-nano-2025-08-07",
    output_type=None,
)

def analyze_keyword_variants_ai(keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Use AI to analyze keyword variants and select the best from each group.
    This replaces the programmatic logic from Task 11 with AI intelligence.
    
    Args:
        keywords: List of keyword dicts with phrase, search_volume, etc.
        
    Returns:
        Analysis result with variant groups and optimized keyword list
    """
    if not keywords:
        return {
            "variant_groups": [],
            "optimized_keywords": [],
            "total_variants_found": 0,
            "total_groups": 0
        }
    
    # Prepare input for AI agent
    keywords_json = json.dumps(keywords, indent=2)
    prompt = USER_PROMPT_TEMPLATE.format(keywords_json=keywords_json)
    
    try:
        # Import the Runner dynamically to avoid circular imports
        try:
            from agents.runner import Runner as _Runner
        except ImportError:
            # Fallback for different SDK versions
            from agents import Runner
        
        # Run AI agent
        result = Runner.run_sync(
            keyword_variant_agent,
            prompt
        )
        
        output = getattr(result, "final_output", None)
        
        # Parse AI response
        if isinstance(output, str):
            try:
                parsed = json.loads(output.strip())
                logger.info(f"[KeywordVariantAgent] AI successfully analyzed {len(keywords)} keywords, found {parsed.get('total_groups', 0)} variant groups")
                return parsed
            except json.JSONDecodeError:
                logger.error(f"[KeywordVariantAgent] Failed to parse AI output: {output[:200]}...")
                # Fallback to no variants detected
                return {
                    "variant_groups": [],
                    "optimized_keywords": keywords,
                    "total_variants_found": 0,
                    "total_groups": 0,
                    "error": "AI output parsing failed"
                }
        
        elif hasattr(output, 'model_dump'):
            return output.model_dump()
        
        else:
            raise Exception("Unexpected AI output format")
            
    except Exception as e:
        logger.error(f"[KeywordVariantAgent] AI analysis failed: {e}")
        # Graceful fallback - return original keywords without variant analysis
        return {
            "variant_groups": [],
            "optimized_keywords": keywords,
            "total_variants_found": 0,
            "total_groups": 0,
            "error": f"AI agent failed: {str(e)}"
        }

def apply_variant_optimization_ai(keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply AI-powered variant optimization to a keyword list.
    This is the main function to replace programmatic Task 11 logic.
    
    Args:
        keywords: Original keyword list
        
    Returns:
        Optimized keyword list with variants deduplicated and best ones selected
    """
    analysis = analyze_keyword_variants_ai(keywords)
    optimized = analysis.get("optimized_keywords", keywords)
    
    logger.info(f"[Task11-AI] Optimized {len(keywords)} keywords -> {len(optimized)} (removed {len(keywords) - len(optimized)} variants)")
    
    return optimized 