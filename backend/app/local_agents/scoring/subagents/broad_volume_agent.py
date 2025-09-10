from agents import Agent
from typing import Any, Dict, List, Set, Optional
import re
import logging

logger = logging.getLogger(__name__)

BROAD_VOLUME_INSTRUCTIONS = """
Role: Compute broad search volume per root word.
- Identify a simple root token for each keyword (e.g., main noun excluding stopwords/brands).
- Sum search_volume across all keywords sharing that root.
Return: the original list with `root` field per item and a separate map `broad_search_volume_by_root`.
No sorting; no external data.

Input: List of keyword items with phrase, search_volume, etc.
Output: Same list with added `root` field + separate `broad_search_volume_by_root` summary.

Instructions:
1. For each keyword phrase, identify the main root word (usually the primary noun)
2. Exclude common stopwords, brand names, and modifiers 
3. Normalize to lowercase
4. Group keywords by their root and sum search volumes
5. Return original items with `root` field added and summary map

Example:
Input: [{"phrase": "wireless mouse", "search_volume": 1000}, {"phrase": "gaming mouse", "search_volume": 800}]
Output: 
- Items: [{"phrase": "wireless mouse", "search_volume": 1000, "root": "mouse"}, {"phrase": "gaming mouse", "search_volume": 800, "root": "mouse"}]
- Summary: {"mouse": 1800}
"""

USER_PROMPT_TEMPLATE = """
Analyze these keywords and identify root words for broad volume calculation:

KEYWORDS:
{items}

For each keyword:
1. Identify the main root word (primary noun, excluding modifiers/brands)
2. Normalize to lowercase
3. Sum search volumes by root

Return ONLY a JSON object with this exact structure:
{{
  "items": [
    {{"phrase": "original phrase", "search_volume": number, "root": "identified_root", "category": "original_category", "relevancy_score": number, "intent_score": number, "title_density": number, "cpr": number, "competition": {{}}}},
    ...
  ],
  "broad_search_volume_by_root": {{
    "root1": total_volume,
    "root2": total_volume
  }}
}}

Ensure all original fields are preserved in each item. Only add the "root" field."""

broad_volume_agent = Agent(
    name="BroadVolumeSubagent",
    instructions=BROAD_VOLUME_INSTRUCTIONS,
    model="gpt-5-2025-08-07",
)

# Common stopwords for root word extraction
STOPWORDS: Set[str] = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it',
    'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'with', 'the', 'this', 'these',
    'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
    'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
    'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'being', 'been', 'have', 'has',
    'had', 'having', 'do', 'does', 'did', 'doing', 'would', 'should', 'could', 'ought', 'best',
    'top', 'new', 'old', 'big', 'small', 'high', 'low'
}

# Common modifiers that should be excluded from root words
MODIFIERS: Set[str] = {
    'premium', 'deluxe', 'pro', 'professional', 'heavy', 'duty', 'portable', 'mini', 'compact',
    'large', 'small', 'xl', 'medium', 'lightweight', 'wireless', 'wired', 'bluetooth', 'usb',
    'rechargeable', 'battery', 'powered', 'electric', 'manual', 'automatic', 'digital', 'analog',
    'smart', 'advanced', 'basic', 'standard', 'commercial', 'industrial', 'home', 'office',
    'outdoor', 'indoor', 'waterproof', 'water', 'resistant', 'proof', 'anti', 'non', 'ultra',
    'super', 'multi', 'dual', 'single', 'double', 'triple', 'adjustable', 'foldable', 'collapsible'
}

def extract_root_word(phrase: str, brand_tokens: Optional[Set[str]] = None) -> str:
    """
    Extract the main root word from a keyword phrase using deterministic rules.
    
    Args:
        phrase: The keyword phrase to analyze
        brand_tokens: Set of brand names to exclude
    
    Returns:
        The identified root word (normalized to lowercase)
    """
    if not phrase:
        return ""
    
    # Normalize and tokenize
    phrase_lower = phrase.lower().strip()
    tokens = re.findall(r'\b\w+\b', phrase_lower)
    
    if not tokens:
        return ""
    
    # Filter out stopwords, modifiers, and brand tokens
    brand_tokens = brand_tokens or set()
    brand_tokens_lower = {token.lower() for token in brand_tokens}
    
    filtered_tokens = []
    for token in tokens:
        if (token not in STOPWORDS and 
            token not in MODIFIERS and 
            token not in brand_tokens_lower and
            len(token) > 2):  # Exclude very short words
            filtered_tokens.append(token)
    
    if not filtered_tokens:
        # Fallback: use the longest original token
        return max(tokens, key=len) if tokens else ""
    
    # Prioritize nouns (heuristic: longer words often nouns, words at end of phrase)
    # For now, take the longest meaningful token as a simple heuristic
    root = max(filtered_tokens, key=len)
    
    # Handle plural forms (basic stemming)
    if root.endswith('s') and len(root) > 3:
        potential_singular = root[:-1]
        # Simple check: if removing 's' gives a reasonable word
        if len(potential_singular) >= 3:
            root = potential_singular
    
    return root

def calculate_broad_volume_deterministic(
    items: List[Dict[str, Any]], 
    brand_tokens: Optional[Set[str]] = None
) -> Dict[str, Any]:
    """
    Deterministic broad volume calculation without LLM.
    
    Args:
        items: List of keyword items with phrase and search_volume
        brand_tokens: Set of brand names to exclude from root extraction
    
    Returns:
        Dict with enhanced items and broad_search_volume_by_root summary
    """
    if not items:
        return {"items": [], "broad_search_volume_by_root": {}}
    
    enhanced_items = []
    root_volume_map: Dict[str, int] = {}
    
    for item in items:
        phrase = item.get('phrase', '')
        search_volume = item.get('search_volume', 0)
        
        # Extract root word
        root = extract_root_word(phrase, brand_tokens)
        
        # Add root to item
        enhanced_item = {**item, 'root': root}
        enhanced_items.append(enhanced_item)
        
        # Accumulate volume by root
        if root and isinstance(search_volume, (int, float)):
            root_volume_map[root] = root_volume_map.get(root, 0) + int(search_volume)
    
    return {
        "items": enhanced_items,
        "broad_search_volume_by_root": root_volume_map
    }

def calculate_broad_volume_llm(
    items: List[Dict[str, Any]], 
    brand_tokens: Optional[Set[str]] = None
) -> Dict[str, Any]:
    """
    LLM-based broad volume calculation using the broad_volume_agent.
    
    Args:
        items: List of keyword items with phrase and search_volume
        brand_tokens: Set of brand names to exclude from root extraction
    
    Returns:
        Dict with enhanced items and broad_search_volume_by_root summary
    """
    if not items:
        return {"items": [], "broad_search_volume_by_root": {}}
    
    try:
        from agents import Runner as _Runner
        import json as _json
        
        logger.info(f"[BroadVolumeAgent] Processing {len(items)} items with LLM")
        
        # Prepare prompt
        items_json = _json.dumps(items, separators=(",", ":"))
        prompt = USER_PROMPT_TEMPLATE.format(items=items_json)
        
        # Run LLM agent
        try:
            result = _Runner.run_sync(
                broad_volume_agent,
                prompt,
                metadata={
                    "component": "BroadVolumeAgent",
                    "items_count": len(items),
                }
            )
        except TypeError:
            # Older SDK signature
            result = _Runner.run_sync(broad_volume_agent, prompt)
        
        output = getattr(result, "final_output", None)
        
        # Parse LLM response with robust JSON extraction
        if isinstance(output, str):
            logger.debug(f"[BroadVolumeAgent] Raw LLM output preview: {output[:500]}")
            
            # Try direct JSON parsing first
            try:
                parsed = _json.loads(output.strip())
                if isinstance(parsed, dict) and "items" in parsed and "broad_search_volume_by_root" in parsed:
                    logger.info(f"[BroadVolumeAgent] LLM successfully processed {len(parsed['items'])} items")
                    return parsed
            except _json.JSONDecodeError:
                pass
            
            # Try to extract JSON from text if direct parsing fails
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, output, re.DOTALL)
            
            for match in reversed(matches):  # Try largest JSON blocks first
                try:
                    parsed = _json.loads(match)
                    if isinstance(parsed, dict) and "items" in parsed and "broad_search_volume_by_root" in parsed:
                        logger.info(f"[BroadVolumeAgent] LLM successfully processed {len(parsed['items'])} items via extraction")
                        return parsed
                except _json.JSONDecodeError:
                    continue
            
            # Log the problematic output for debugging
            logger.error(f"[BroadVolumeAgent] Could not parse LLM output. Full output: {output}")
            raise Exception(f"LLM returned unparseable JSON: {output[:200]}...")
        
        elif hasattr(output, 'model_dump'):
            # Handle structured output
            try:
                parsed = output.model_dump()
                if isinstance(parsed, dict) and "items" in parsed and "broad_search_volume_by_root" in parsed:
                    logger.info(f"[BroadVolumeAgent] LLM successfully processed {len(parsed['items'])} items via model_dump")
                    return parsed
            except Exception as e:
                logger.error(f"[BroadVolumeAgent] Failed to extract from structured output: {e}")
                raise Exception(f"Failed to extract structured LLM output: {e}")
        
        # No fallback - AI analysis only
        raise Exception("LLM failed to produce valid broad volume analysis")
        
    except Exception as e:
        logger.error(f"[BroadVolumeAgent] LLM calculation failed: {e}")
        raise Exception(f"AI-only broad volume calculation failed: {e}")

def calculate_broad_volume(
    items: List[Dict[str, Any]], 
    brand_tokens: Optional[Set[str]] = None,
    use_llm: bool = True
) -> Dict[str, Any]:
    """
    Main function to calculate broad search volume by root words using AI analysis only.
    
    Args:
        items: List of keyword items with phrase and search_volume
        brand_tokens: Set of brand names to exclude from root extraction
        use_llm: Whether to use LLM agent (True) or raise error (False not supported)
    
    Returns:
        Dict with enhanced items and broad_search_volume_by_root summary
    """
    if not use_llm:
        raise ValueError("AI-only analysis mode: deterministic calculation not allowed")
    
    return calculate_broad_volume_llm(items, brand_tokens)
