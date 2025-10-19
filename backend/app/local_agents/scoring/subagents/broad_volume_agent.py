from agents import Agent
from typing import Any, Dict, List, Set, Optional
import re
import logging

logger = logging.getLogger(__name__)

BROAD_VOLUME_INSTRUCTIONS = """
Role: Compute broad search volume per root word.
- Identify a simple root token for each keyword (e.g., main noun excluding stopwords/brands).
- Sum search_volume across all keywords sharing that root, but ONLY for relevant or design-specific keywords.
Return: the original list with `root` field per item and a separate map `broad_search_volume_by_root`.
No sorting; no external data.

Input: List of keyword items with phrase, search_volume, category, etc.
Output: Same list with added `root` field + separate `broad_search_volume_by_root` summary.

Instructions:
1. For each keyword phrase, identify the main root word (usually the primary noun)
2. Exclude common stopwords, brand names, and modifiers 
3. Normalize to lowercase
4. Group keywords by their root and sum search volumes
5. IMPORTANT: Only include search volumes for keywords with category "Relevant" or "Design-Specific" in the broad_search_volume_by_root calculation
6. Return original items with `root` field added and summary map

 
Example:
Input: [{"phrase": "wireless mouse", "search_volume": 1000, "category": "Relevant"}, {"phrase": "gaming mouse", "search_volume": 800, "category": "Irrelevant"}]
Output: 
- Items: [{"phrase": "wireless mouse", "search_volume": 1000, "root": "mouse", "category": "Relevant"}, {"phrase": "gaming mouse", "search_volume": 800, "root": "mouse", "category": "Irrelevant"}]
- Summary: {"mouse": 1000}  // Only the relevant keyword's volume is included
"""

USER_PROMPT_TEMPLATE = """
Analyze these keywords and identify root words for broad volume calculation:

KEYWORDS:
{items}

For each keyword:
1. Identify the main root word (primary noun, excluding modifiers/brands)
2. Normalize to lowercase
3. Sum search volumes by root
4. CRITICAL: For the broad_search_volume_by_root summary, only include search volumes from keywords with category "Relevant" or "Design-Specific". Exclude "Irrelevant" keywords from the volume totals.

Return ONLY a JSON object with this exact structure:
{{
  "items": [
    {{"phrase": "original phrase", "search_volume": number, "root": "identified_root", "category": "original_category", "relevancy_score": number, "intent_score": number, "title_density": number, "cpr": number, "competition": {{}}}},
    ...
  ],
  "broad_search_volume_by_root": {{
    "root1": total_volume_from_relevant_keywords_only,
    "root2": total_volume_from_relevant_keywords_only
  }}
}}

Ensure all original fields are preserved in each item. Only add the "root" field.
IMPORTANT: The broad_search_volume_by_root should only sum volumes from "Relevant" and "Design-Specific" categories.

NOTE: This instruction is now enhanced with AI-powered Task 13 filtering for better relevance assessment."""

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
    
    # Handle plural forms (Task 11: Use enhanced normalization)
    from app.services.keyword_processing.root_extraction import normalize_word
    root = normalize_word(root)
    
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
    LLM-based broad volume calculation using simple approach - NO MULTI-BATCH COMPLEXITY.
    
    Args:
        items: List of keyword items with phrase and search_volume
        brand_tokens: Set of brand names to exclude from root extraction
    
    Returns:
        Dict with enhanced items and broad_search_volume_by_root summary
    """
    if not items:
        return {"items": [], "broad_search_volume_by_root": {}}
    
    logger.info(f"[BroadVolumeAgent] Processing {len(items)} items with simple LLM")
    
    # Simple approach - just process directly with a small delay
    import time
    time.sleep(1)  # Simple rate limiting
    
    # Use the original simple approach
    from agents import Runner as _Runner
    import json as _json
    
    prompt = USER_PROMPT_TEMPLATE.format(
        items=_json.dumps(items or [], separators=(",", ":")),
    )
    
    result = _Runner.run_sync(broad_volume_agent, prompt)
    
    # Parse and return results
    if result and hasattr(result, 'final_output'):
        output = result.final_output
        if output:
            try:
                parsed_result = _json.loads(output)
                if isinstance(parsed_result, dict):
                    return parsed_result
            except _json.JSONDecodeError:
                logger.warning("[BroadVolumeAgent] Failed to parse broad volume result")
    elif result and hasattr(result, 'content'):
        try:
            parsed_result = _json.loads(result.content)
            if isinstance(parsed_result, dict):
                return parsed_result
        except _json.JSONDecodeError:
            logger.warning("[BroadVolumeAgent] Failed to parse broad volume result")
    
    # Fallback: return original items with simple root extraction
    logger.warning("[BroadVolumeAgent] Broad volume calculation failed, using fallback")
    fallback_items = []
    broad_search_volume_by_root = {}
    
    for item in items:
        fallback_item = item.copy()
        phrase = item.get("phrase", "").lower()
        
        # Simple root extraction - take first meaningful word
        words = phrase.split()
        root = words[0] if words else phrase
        fallback_item["root"] = root
        
        # Only include relevant/design-specific keywords in volume calculation
        category = item.get("category", "")
        if category in ["Relevant", "Design-Specific"]:
            search_volume = item.get("search_volume", 0)
            if root in broad_search_volume_by_root:
                broad_search_volume_by_root[root] += search_volume
            else:
                broad_search_volume_by_root[root] = search_volume
        
        fallback_items.append(fallback_item)
    
    return {
        "items": fallback_items,
        "broad_search_volume_by_root": broad_search_volume_by_root
    }

def _calculate_broad_volume_in_batches(
    items: List[Dict[str, Any]], 
    brand_tokens: Optional[Set[str]] = None
) -> Dict[str, Any]:
    """Process broad volume calculation using multi-batch processing for large datasets."""
    
    def process_batch(batch_items: List[Dict[str, Any]], batch_id: str) -> Dict[str, Any]:
        """Process a single batch of items for broad volume calculation."""
        return _calculate_broad_volume_direct(batch_items, brand_tokens)
    
    def combine_batch_results(batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine results from all batches."""
        combined_items = []
        combined_volume_map = {}
        
        for batch_result in batch_results:
            # Combine items
            combined_items.extend(batch_result.get("items", []))
            
            # Combine volume maps
            volume_map = batch_result.get("broad_search_volume_by_root", {})
            for root, volume in volume_map.items():
                combined_volume_map[root] = combined_volume_map.get(root, 0) + volume
        
        return {
            "items": combined_items,
            "broad_search_volume_by_root": combined_volume_map
        }
    
    # Use multi-batch processor
    result = multi_batch_processor.process_batches(
        items=items,
        process_func=process_batch,
        combine_func=combine_batch_results,
        agent_name="BroadVolumeAgent",
        item_name="keywords"
    )
    
    logger.info(f"[BroadVolumeAgent] Multi-batch processing complete: {len(result['items'])} items processed")
    return result

def _calculate_broad_volume_direct(
    items: List[Dict[str, Any]], 
    brand_tokens: Optional[Set[str]] = None
) -> Dict[str, Any]:
    """Process broad volume calculation directly for small datasets."""
    request_id = f"broad_volume_{uuid.uuid4().hex[:8]}"
    
    try:
        # Start monitoring
        monitor.log_request_start("BroadVolumeAgent", request_id, len(items))
        
        # Apply rate limiting
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(rate_limiter.wait_for_rate_limit())
        loop.close()
        
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
                    "request_id": request_id,
                }
            )
        except TypeError:
            # Older SDK signature
            result = _Runner.run_sync(broad_volume_agent, prompt)
        
        output = getattr(result, "final_output", None)
        
        # Parse LLM response with robust JSON extraction
        parsed_result = _parse_broad_volume_output(output, items)
        
        # Log success
        monitor.log_success("BroadVolumeAgent", request_id, len(items))
        rate_limiter.reset_retry_count(request_id)
        
        logger.info(f"[BroadVolumeAgent] LLM successfully processed {len(parsed_result['items'])} items")
        return parsed_result
        
    except Exception as e:
        # Log error
        monitor.log_error("BroadVolumeAgent", request_id, str(e))
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
