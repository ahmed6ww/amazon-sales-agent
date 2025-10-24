"""
Task 13: Root Relevance Filtering Agent

AI-powered agent that determines which keyword roots should be included in broad volume calculations
based on relevance assessment, replacing programmatic filtering with AI intelligence.
"""

from agents import Agent, ModelSettings
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
    model="gpt-5-nano-2025-08-07",  # gpt-5-mini
    model_settings=ModelSettings(
        max_tokens=8000,  # Handle large keyword lists
        timeout=240.0,     # 4 minutes for complex analysis
    ),
    output_type=None,
)

def analyze_root_relevance_ai(keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Use AI to analyze which keyword roots should be included in broad volume calculations.
    This replaces the programmatic filtering logic from Task 13 with AI intelligence.
    Implements batching to prevent token limits and timeouts with large keyword sets.
    
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
    
    # Import dependencies
    from agents import Runner as _Runner
    import asyncio
    import time
    from collections import defaultdict
    
    # Check if event loop exists
    try:
        loop = asyncio.get_running_loop()
        logger.warning(f"[RootRelevanceAgent] Event loop running, using fallback analysis")
        return _create_fallback_analysis(keywords)
    except RuntimeError:
        pass  # No event loop - safe to use run_sync
    
    # ========================================================================
    # BATCHING: Split keywords to prevent token limits and timeouts
    # ========================================================================
    BATCH_SIZE = 60  # Keywords per batch (root analysis is lighter than full categorization)
    total_keywords = len(keywords)
    num_batches = (total_keywords + BATCH_SIZE - 1) // BATCH_SIZE
    
    if total_keywords > BATCH_SIZE:
        logger.info(f"[RootRelevanceAgent] 📦 Processing {total_keywords} keywords in {num_batches} batch(es) (size: {BATCH_SIZE})")
    
    # Aggregated results from all batches
    combined_root_volumes = defaultdict(int)
    combined_root_analysis = {}
    total_volume_before = 0
    total_volume_after = 0
    
    for batch_idx in range(num_batches):
        start_idx = batch_idx * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, total_keywords)
        batch_keywords = keywords[start_idx:end_idx]
        batch_label = f"Batch {batch_idx + 1}/{num_batches}"
        
        if total_keywords > BATCH_SIZE:
            logger.info(f"[RootRelevanceAgent] 🔄 {batch_label}: Processing {len(batch_keywords)} keywords")
        
        try:
            # Rate limiting between batches
            if batch_idx > 0:
                time.sleep(1)
            
            # Prepare prompt for this batch
            keywords_json = json.dumps(batch_keywords, indent=2)
            prompt = USER_PROMPT_TEMPLATE.format(keywords_json=keywords_json)
            
            # Run AI agent for this batch
            result = _Runner.run_sync(root_relevance_agent, prompt)
            output = getattr(result, "final_output", None)
            
            # Parse AI response
            batch_result = None
            if isinstance(output, str):
                try:
                    cleaned_output = strip_markdown_code_fences(output)
                    batch_result = json.loads(cleaned_output)
                except json.JSONDecodeError as e:
                    logger.warning(f"[RootRelevanceAgent] {batch_label} JSON parse failed: {e}")
                    raise
            elif hasattr(output, 'model_dump'):
                batch_result = output.model_dump()
            else:
                raise Exception("Unexpected AI output format")
            
            # Merge batch results into combined results
            if batch_result:
                # Merge filtered root volumes
                batch_volumes = batch_result.get("filtered_root_volumes", {})
                for root, volume in batch_volumes.items():
                    combined_root_volumes[root] += volume
                
                # Merge root analysis (for detailed breakdown)
                batch_analysis = batch_result.get("root_volume_analysis", {})
                for root, analysis in batch_analysis.items():
                    if root not in combined_root_analysis:
                        combined_root_analysis[root] = analysis
                    else:
                        # Merge analysis for same root from different batches
                        existing = combined_root_analysis[root]
                        existing["total_keywords"] = existing.get("total_keywords", 0) + analysis.get("total_keywords", 0)
                        existing["included_volume"] = existing.get("included_volume", 0) + analysis.get("included_volume", 0)
                        existing["excluded_volume"] = existing.get("excluded_volume", 0) + analysis.get("excluded_volume", 0)
                        existing["final_volume"] = existing.get("final_volume", 0) + analysis.get("final_volume", 0)
                        existing.setdefault("relevant_keywords", []).extend(analysis.get("relevant_keywords", []))
                        existing.setdefault("irrelevant_keywords", []).extend(analysis.get("irrelevant_keywords", []))
                
                # Aggregate summary stats
                batch_summary = batch_result.get("summary", {})
                total_volume_before += batch_summary.get("total_volume_before", 0)
                total_volume_after += batch_summary.get("total_volume_after", 0)
                
                if total_keywords > BATCH_SIZE:
                    logger.info(f"[RootRelevanceAgent] ✅ {batch_label} complete ({len(batch_volumes)} roots analyzed)")
            else:
                raise ValueError("Batch parsing failed")
        
        except Exception as e:
            logger.error(f"[RootRelevanceAgent] ❌ {batch_label} failed: {e}")
            # Fallback: Use programmatic filtering for failed batch
            logger.warning(f"[RootRelevanceAgent] ⚠️  {batch_label} using fallback filtering")
            fallback_result = _create_fallback_analysis(batch_keywords)
            fallback_volumes = fallback_result.get("filtered_root_volumes", {})
            for root, volume in fallback_volumes.items():
                combined_root_volumes[root] += volume
            total_volume_before += fallback_result.get("summary", {}).get("total_volume_before", 0)
            total_volume_after += fallback_result.get("summary", {}).get("total_volume_after", 0)
    
    # Build final combined result
    final_result = {
        "root_volume_analysis": combined_root_analysis,
        "filtered_root_volumes": dict(combined_root_volumes),
        "summary": {
            "total_roots_analyzed": len(combined_root_volumes),
            "roots_included": len(combined_root_volumes),
            "total_volume_before": total_volume_before,
            "total_volume_after": total_volume_after,
            "volume_filtered_out": total_volume_before - total_volume_after,
            "batches_processed": num_batches
        }
    }
    
    logger.info(f"[RootRelevanceAgent] ✅ All batches complete: {len(combined_root_volumes)} roots included, {final_result['summary']['volume_filtered_out']} volume filtered out")
    
    return final_result

def _create_fallback_analysis(keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a fallback analysis when AI fails, using basic programmatic filtering"""
    from collections import defaultdict
    
    root_volumes = defaultdict(int)
    total_before = 0
    
    for kw in keywords:
        root = kw.get("root", "")
        volume = kw.get("search_volume", 0) or 0  # Handle None values
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