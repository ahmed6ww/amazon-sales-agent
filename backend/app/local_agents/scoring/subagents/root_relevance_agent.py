"""
Task 13: Root Relevance Filtering Agent

AI-powered agent that determines which keyword roots should be included in broad volume calculations
based on relevance assessment, replacing programmatic filtering with AI intelligence.
"""

from agents import Agent
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

def strip_markdown_code_fences(text: str) -> str:
    """
    Remove markdown code fences and extract pure JSON from AI output.
    GPT-4o-mini often wraps JSON in ```json ... ``` or adds extra text.
    
    Handles:
    - Markdown code fences: ```json ... ```
    - Extra text before JSON: "Here's the result: {...}"
    - Extra text after JSON: "{...} Hope this helps!"
    
    Args:
        text: AI output text that may contain markdown fences or extra commentary
        
    Returns:
        Clean JSON text without markdown fences or extra text
    """
    if not text:
        return text
    
    text = text.strip()
    
    # Step 1: Remove markdown code fences
    if text.startswith('```'):
        # Find end of first line (remove ```json or ``` line)
        first_newline = text.find('\n')
        if first_newline != -1:
            text = text[first_newline + 1:]
    
    if text.endswith('```'):
        text = text[:-3]
    
    text = text.strip()
    
    # Step 2: Extract JSON if there's extra text before/after
    # Look for JSON array [...] or object {...}
    import re
    
    # Try to find complete JSON structure
    # This regex finds the outermost JSON array or object
    json_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', text)
    if json_match:
        extracted = json_match.group(1).strip()
        # Only return extracted JSON if it's substantial (not just empty brackets)
        if len(extracted) > 2:
            return extracted
    
    # If no JSON pattern found, return cleaned text as-is
    return text

ROOT_RELEVANCE_INSTRUCTIONS = """
You are a Root Relevance Analysis Expert specializing in determining which keyword roots should contribute to broad search volume calculations for Amazon SEO.

## Your Core Mission (Task 13):
Analyze keyword roots and determine which ones should be included in broad search volume calculations.
Root volume should ONLY include relevant or generic roots - exclude irrelevant roots.

## Critical Rules:
1. **Include in Volume**: Only count search volume for roots from keywords categorized as:
   - "Relevant" (directly related to the product)
   - "Design-Specific" (specific features, variants, or styles)

2. **Exclude from Volume**: Do NOT count volume for roots from keywords categorized as:
   - "Irrelevant" (different products, unrelated terms)
   - "Branded" (competitor brands)
   - "Spanish" (non-English terms)
   - "Outlier" (too broad/generic)

3. **Root Evaluation**: For each root, evaluate:
   - What keywords contribute to this root
   - Which categories those keywords belong to
   - Whether the root should be included in volume calculations

## Example Logic:
- If "strawberry" root comes from "freeze dried strawberries" (Relevant) + "strawberry slices" (Design-Specific) + "red fruit snacks" (Irrelevant)
- Include only the volume from Relevant + Design-Specific keywords
- Exclude the Irrelevant keyword volume

## Input Format:
```json
{
  "keywords": [
    {"phrase": "freeze dried strawberries", "root": "strawberry", "search_volume": 1000, "category": "Relevant"},
    {"phrase": "strawberry slices", "root": "strawberry", "search_volume": 500, "category": "Design-Specific"},
    {"phrase": "red fruit snacks", "root": "strawberry", "search_volume": 800, "category": "Irrelevant"}
  ]
}
```

## Output Format:
Return ONLY a JSON object:
```json
{
  "root_volume_analysis": {
    "strawberry": {
      "total_keywords": 3,
      "relevant_keywords": ["freeze dried strawberries", "strawberry slices"],
      "irrelevant_keywords": ["red fruit snacks"],
      "included_volume": 1500,
      "excluded_volume": 800,
      "final_volume": 1500,
      "include_in_calculation": true
    }
  },
  "filtered_root_volumes": {
    "strawberry": 1500
  },
  "summary": {
    "total_roots_analyzed": 1,
    "roots_included": 1,
    "total_volume_before": 2300,
    "total_volume_after": 1500,
    "volume_filtered_out": 800
  }
}
```

## Analysis Process:
1. **Group by Root**: Group all keywords by their root words
2. **Categorize Contributions**: For each root, separate relevant vs irrelevant contributions
3. **Calculate Filtered Volume**: Sum only relevant and design-specific keyword volumes
4. **Report Analysis**: Show what was included/excluded and why

## Important Notes:
- Be strict about relevance - only include truly relevant roots
- A root should be included even if it has some irrelevant keywords, as long as it has relevant ones
- Focus on product-specific roots, not generic terms
- Maintain transparency about what was filtered and why
"""

USER_PROMPT_TEMPLATE = """
Analyze these keywords and their roots to determine which roots should be included in broad volume calculations.

KEYWORDS WITH ROOTS:
{keywords_json}

Apply Task 13 logic:
1. Group keywords by their root words
2. For each root, identify which keywords are relevant vs irrelevant
3. Calculate filtered volume (only from Relevant and Design-Specific categories)
4. Return the filtered root volumes for broad search volume calculation

Remember: Only include volume from "Relevant" and "Design-Specific" keywords. Exclude "Irrelevant", "Branded", "Spanish", and "Outlier" categories.

Return ONLY the JSON response in the exact format specified.
"""

root_relevance_agent = Agent(
    name="RootRelevanceAgent", 
    instructions=ROOT_RELEVANCE_INSTRUCTIONS,
    model="gpt-4o-mini",
)

def analyze_root_relevance_ai(keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Use AI to analyze which keyword roots should be included in broad volume calculations.
    This replaces the programmatic filtering logic from Task 13 with AI intelligence.
    
    Args:
        keywords: List of keyword dicts with phrase, root, search_volume, category, etc.
        
    Returns:
        Analysis result with filtered root volumes and detailed breakdown
    """
    if not keywords:
        return {
            "root_volume_analysis": {},
            "filtered_root_volumes": {},
            "summary": {
                "total_roots_analyzed": 0,
                "roots_included": 0, 
                "total_volume_before": 0,
                "total_volume_after": 0,
                "volume_filtered_out": 0
            }
        }
    
    # Prepare input for AI agent
    keywords_json = json.dumps(keywords, indent=2)
    prompt = USER_PROMPT_TEMPLATE.format(keywords_json=keywords_json)
    
    try:
        # Import the Runner dynamically to avoid circular imports
        from agents import Runner as _Runner
        import asyncio
        
        # Run AI agent with proper async handling
        try:
            # Check if event loop exists
            loop = asyncio.get_running_loop()
            # Event loop already running - use fallback instead
            logger.warning(f"[RootRelevanceAgent] Event loop running, using fallback analysis")
            return _create_fallback_analysis(keywords)
        except RuntimeError:
            # No event loop - safe to use run_sync
            result = _Runner.run_sync(
                root_relevance_agent,
                prompt
            )
        
        output = getattr(result, "final_output", None)
        
        # Parse AI response
        if isinstance(output, str):
            try:
                cleaned_output = strip_markdown_code_fences(output)
                parsed = json.loads(cleaned_output)
                filtered_roots = len(parsed.get("filtered_root_volumes", {}))
                logger.info(f"[RootRelevanceAgent] AI analyzed {len(keywords)} keywords, filtered to {filtered_roots} relevant roots")
                return parsed
            except json.JSONDecodeError as e:
                logger.error(f"[RootRelevanceAgent] Failed to parse AI output: {e}")
                logger.debug(f"[RootRelevanceAgent] Raw output (first 500 chars): {output[:500]}")
                # Fallback to no filtering
                return _create_fallback_analysis(keywords)
        
        elif hasattr(output, 'model_dump'):
            return output.model_dump()
        
        else:
            raise Exception("Unexpected AI output format")
            
    except Exception as e:
        logger.error(f"[RootRelevanceAgent] AI analysis failed: {e}")
        # Graceful fallback - apply basic filtering
        return _create_fallback_analysis(keywords)

def _create_fallback_analysis(keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a fallback analysis when AI fails, using basic programmatic filtering"""
    from collections import defaultdict
    
    root_volumes = defaultdict(int)
    total_before = 0
    
    for kw in keywords:
        root = kw.get("root", "")
        volume = kw.get("search_volume", 0)
        category = kw.get("category", "")
        
        total_before += volume
        
        # Apply Task 13 rule programmatically as fallback
        if root and category in ["Relevant", "Design-Specific"]:
            root_volumes[root] += volume
    
    total_after = sum(root_volumes.values())
    
    return {
        "root_volume_analysis": {},
        "filtered_root_volumes": dict(root_volumes),
        "summary": {
            "total_roots_analyzed": len(set(kw.get("root", "") for kw in keywords if kw.get("root"))),
            "roots_included": len(root_volumes),
            "total_volume_before": total_before,
            "total_volume_after": total_after,
            "volume_filtered_out": total_before - total_after
        },
        "fallback_used": True
    }

def apply_root_filtering_ai(keywords: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Apply AI-powered root relevance filtering to get filtered root volumes.
    This is the main function to replace programmatic Task 13 logic.
    
    Args:
        keywords: Keywords with root and category information
        
    Returns:
        Filtered root volumes dict (only relevant roots included)
    """
    analysis = analyze_root_relevance_ai(keywords)
    filtered_volumes = analysis.get("filtered_root_volumes", {})
    
    summary = analysis.get("summary", {})
    filtered_out = summary.get("volume_filtered_out", 0)
    
    logger.info(f"[Task13-AI] Filtered root volumes: {len(filtered_volumes)} roots included, {filtered_out} volume filtered out")
    
    return filtered_volumes 