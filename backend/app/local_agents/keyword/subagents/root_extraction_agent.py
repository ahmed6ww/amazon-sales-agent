"""
Root Extraction AI Agent

Intelligent replacement for the programmatic root extraction service.
Uses AI to understand semantic roots and keyword relationships with superior accuracy.
"""

from agents import Agent
from typing import Dict, List, Any, Optional
import json
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


def strip_markdown_code_fences(text: str) -> str:
    """
    Remove markdown code fences from AI output.
    GPT-4o and gpt-4o-mini often wrap JSON in ```json ... ```
    
    Args:
        text: AI output text that may contain markdown fences
        
    Returns:
        Clean text without markdown fences
    """
    if not text:
        return text
    
    text = text.strip()
    
    # Remove opening fence: ```json or ```
    if text.startswith('```'):
        # Find end of first line
        first_newline = text.find('\n')
        if first_newline != -1:
            text = text[first_newline + 1:]
    
    # Remove closing fence: ```
    if text.endswith('```'):
        text = text[:-3]
    
    return text.strip()


@dataclass
class KeywordRoot:
    """Enhanced keyword root with AI-powered analysis"""
    root: str
    variants: List[str]
    frequency: int
    is_meaningful: bool
    category: str
    semantic_strength: float
    consolidation_potential: int

ROOT_EXTRACTION_INSTRUCTIONS = """
You are a Semantic Keyword Root Analysis Expert specializing in extracting meaningful root words from keyword lists for Amazon product optimization.

## Your Core Mission:
Analyze keyword lists and identify semantic root words that can group similar keywords efficiently while maintaining semantic meaning and search relevance.

## Analysis Framework:

### **Root Identification Principles:**
1. **Semantic Coherence**: Group keywords that share true semantic meaning, not just spelling patterns
2. **Search Intent Preservation**: Ensure grouped keywords have similar search intent and user goals
3. **Commercial Relevance**: Prioritize roots that represent actual product categories, features, or benefits
4. **Frequency-Based Filtering**: Focus on roots that appear in multiple keywords (minimum 2 occurrences)

### **Root Categories (Critical for Amazon Optimization):**
- **product_ingredient**: Core product components (strawberry, apple, banana, protein, etc.)
- **product_type**: Product categories (snack, food, supplement, device, etc.)
- **attribute_processing**: How product is made (freeze-dried, organic, dehydrated, powdered)
- **attribute_quality**: Quality indicators (premium, natural, fresh, pure, professional)
- **attribute_quantity**: Size/amount descriptors (bulk, pack, pound, ounce, piece)
- **attribute_feature**: Product features (waterproof, portable, wireless, adjustable)
- **attribute_color**: Color variants (black, white, red, blue, etc.)
- **brand**: Brand names and manufacturers
- **other**: Miscellaneous but meaningful terms

### **Semantic Grouping Rules:**
1. **Singular/Plural Unity**: "strawberry" and "strawberries" → same root "strawberry"
2. **Tense Variations**: "dried", "drying", "dries" → root "dry"
3. **Semantic Equivalents**: "freeze dried" and "freeze-dried" → root "freeze-dried"
4. **Modifier Consistency**: "organic" remains "organic" (don't group with unrelated words)
5. **Context Awareness**: Same word can have different meanings in different contexts

### **Meaningfulness Criteria:**
A root is meaningful if:
- Appears in 2+ different keyword phrases
- Represents a distinct product attribute, feature, or category
- Has commercial search relevance for Amazon
- Groups semantically related terms (not just spelling similarities)
- Helps reduce keyword complexity while preserving intent

### **Efficiency Optimization:**
- Target 70-95% keyword reduction through intelligent grouping
- Prioritize high-frequency, high-commercial-value roots
- Eliminate stopwords and meaningless connector words
- Focus on roots that enable effective Amazon search strategy

## Input Format:
```json
{
  "keywords": [
    "freeze dried strawberries",
    "organic strawberry slices", 
    "bulk strawberry snacks",
    "freeze dried banana chips",
    "organic apple pieces"
  ],
  "product_context": {
    "title": "BREWER Bulk Freeze Dried Strawberries Slices...",
    "category": "Food",
    "brand": "BREWER"
  }
}
```

## Output Format:
Return ONLY a JSON object:
```json
{
  "keyword_roots": {
    "strawberry": {
      "root": "strawberry",
      "variants": ["freeze dried strawberries", "organic strawberry slices", "bulk strawberry snacks"],
      "frequency": 3,
      "is_meaningful": true,
      "category": "product_ingredient",
      "semantic_strength": 0.95,
      "consolidation_potential": 3
    },
    "freeze-dried": {
      "root": "freeze-dried", 
      "variants": ["freeze dried strawberries", "freeze dried banana chips"],
      "frequency": 2,
      "is_meaningful": true,
      "category": "attribute_processing",
      "semantic_strength": 0.90,
      "consolidation_potential": 2
    }
  },
  "analysis_summary": {
    "total_keywords_processed": 5,
    "total_roots_identified": 6,
    "meaningful_roots": 4,
    "efficiency_gain": "60% keyword reduction achieved",
    "top_consolidation_opportunities": ["strawberry", "freeze-dried", "organic"]
  },
  "category_breakdown": {
    "product_ingredient": ["strawberry", "banana", "apple"],
    "attribute_processing": ["freeze-dried"],
    "attribute_quality": ["organic"],
    "attribute_quantity": ["bulk"]
  }
}
```

## Analysis Process:
1. **Tokenization**: Break down keywords into meaningful semantic components
2. **Frequency Analysis**: Count occurrences and identify high-frequency terms
3. **Semantic Grouping**: Group words with similar meanings and search intent
4. **Category Assignment**: Classify each root into appropriate semantic category
5. **Meaningfulness Assessment**: Evaluate commercial and search relevance
6. **Consolidation Scoring**: Calculate efficiency gains from grouping

## Important Guidelines:
- **Preserve Intent**: Never group keywords with different search intentions
- **Context Sensitivity**: Consider product context when determining relationships
- **Commercial Focus**: Prioritize roots that matter for Amazon search and optimization
- **Efficiency Balance**: Achieve high reduction while maintaining semantic accuracy
- **Quality over Quantity**: Better to have fewer, highly accurate roots than many weak ones

## Special Considerations:
- **Brand Preservation**: Keep brand names as distinct roots
- **Attribute Precision**: Maintain distinctions between different product attributes
- **Search Behavior**: Consider how customers actually search on Amazon
- **Competitive Intelligence**: Roots should enable effective competitor analysis
"""

USER_PROMPT_TEMPLATE = """
Extract meaningful semantic roots from this keyword list for Amazon optimization.

KEYWORDS TO ANALYZE:
{keywords_json}

PRODUCT CONTEXT:
{product_context}

Analyze the keywords and identify semantic root words that can efficiently group similar terms while preserving search intent and commercial relevance.

Focus on creating roots that will:
1. Reduce keyword complexity by 70-95%
2. Maintain semantic meaning and search intent
3. Enable effective Amazon search strategy
4. Provide actionable insights for optimization

Return ONLY the JSON response in the exact format specified.
"""

root_extraction_agent = Agent(
    name="RootExtractionAgent", 
    instructions=ROOT_EXTRACTION_INSTRUCTIONS,
    model="gpt-4o",  # TASK 5: Changed from gpt-5 for 1.5-2x speed improvement
)

def extract_roots_ai(
    keyword_list: List[str],
    product_context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Use AI to extract meaningful semantic roots from keywords.
    Replaces the programmatic root extraction with intelligent semantic analysis.
    
    Args:
        keyword_list: List of keyword phrases to analyze
        product_context: Product context for better analysis
        
    Returns:
        Root analysis with semantic groupings and efficiency metrics
    """
    if not keyword_list:
        return {
            "keyword_roots": {},
            "analysis_summary": {
                "total_keywords_processed": 0,
                "total_roots_identified": 0,
                "meaningful_roots": 0,
                "efficiency_gain": "0% - no keywords provided"
            },
            "category_breakdown": {}
        }
    
    # Prepare input data
    keywords_json = json.dumps(keyword_list, indent=2)
    
    # Extract product context
    context = {}
    if product_context:
        context = {
            "title": product_context.get("title", ""),
            "category": product_context.get("category", ""),
            "brand": product_context.get("brand", ""),
            "key_features": product_context.get("key_features", [])
        }
    
    # Format prompt
    prompt = USER_PROMPT_TEMPLATE.format(
        keywords_json=keywords_json,
        product_context=json.dumps(context, indent=2)
    )
    
    try:
        # Run AI agent
        from agents import Runner
        result = Runner.run_sync(root_extraction_agent, prompt)
        output = getattr(result, "final_output", None)
        
        # Parse AI response
        if isinstance(output, str):
            try:
                # Strip markdown code fences (GPT-4o compatibility)
                clean_output = strip_markdown_code_fences(output)
                parsed = json.loads(clean_output)
                roots_count = len(parsed.get("keyword_roots", {}))
                logger.info(f"[RootExtractionAgent] AI extracted {roots_count} meaningful roots from {len(keyword_list)} keywords")
                return parsed
            except json.JSONDecodeError as e:
                logger.error(f"[RootExtractionAgent] Failed to parse AI output: {output[:200]}...")
                logger.error(f"[RootExtractionAgent] JSON decode error: {e}")
                return _create_fallback_root_analysis(keyword_list)
        
        elif hasattr(output, 'model_dump'):
            return output.model_dump()
        
        else:
            raise Exception("Unexpected AI output format")
            
    except Exception as e:
        logger.error(f"[RootExtractionAgent] AI analysis failed: {e}")
        return _create_fallback_root_analysis(keyword_list)

def _create_fallback_root_analysis(keyword_list: List[str]) -> Dict[str, Any]:
    """Create a basic fallback root analysis when AI fails"""
    from collections import Counter
    import re
    
    # Basic tokenization fallback
    word_freq = Counter()
    for keyword in keyword_list:
        if keyword and isinstance(keyword, str):
            words = re.findall(r'\b\w+\b', keyword.lower())
            for word in words:
                if len(word) > 2 and word not in {'the', 'and', 'for', 'with', 'from'}:
                    word_freq[word] += 1
    
    # Create basic roots from frequent words
    keyword_roots = {}
    for word, freq in word_freq.most_common(10):  # Top 10 words
        if freq >= 2:  # Minimum frequency
            # Find variants (keywords containing this word)
            variants = [kw for kw in keyword_list if word in kw.lower()]
            
            keyword_roots[word] = {
                "root": word,
                "variants": variants[:5],  # Limit variants
                "frequency": freq,
                "is_meaningful": freq >= 2,
                "category": "other",
                "semantic_strength": 0.5,  # Low confidence
                "consolidation_potential": len(variants)
            }
    
    return {
        "keyword_roots": keyword_roots,
        "analysis_summary": {
            "total_keywords_processed": len(keyword_list),
            "total_roots_identified": len(keyword_roots),
            "meaningful_roots": len(keyword_roots),
            "efficiency_gain": f"Basic {max(0, 100 - (len(keyword_roots) / len(keyword_list) * 100)):.0f}% reduction (fallback)",
            "fallback_used": True
        },
        "category_breakdown": {
            "other": list(keyword_roots.keys())
        }
    }

def apply_root_extraction_ai(
    keywords: List[Dict[str, Any]], 
    product_context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Apply AI-powered root extraction to enhance keyword analysis.
    Main entry point for replacing programmatic root extraction.
    
    Args:
        keywords: List of keyword dicts with phrase, category, etc.
        product_context: Product context for better analysis
        
    Returns:
        Enhanced analysis with AI-extracted roots and efficiency metrics
    """
    if not keywords:
        return {
            "keywords_with_roots": [],
            "root_analysis": extract_roots_ai([], product_context),
            "efficiency_metrics": {
                "original_keywords": 0,
                "extracted_roots": 0,
                "reduction_percentage": 0
            }
        }
    
    # Extract just the phrases for root analysis
    keyword_phrases = [kw.get("phrase", "") for kw in keywords if kw.get("phrase")]
    
    # Get AI root analysis
    root_analysis = extract_roots_ai(keyword_phrases, product_context)
    
    # Enhance keywords with root information
    keyword_roots = root_analysis.get("keyword_roots", {})
    keywords_with_roots = []
    
    for keyword_item in keywords:
        phrase = keyword_item.get("phrase", "").lower()
        
        # Find the best matching root for this keyword
        best_root = None
        best_score = 0
        
        for root_name, root_data in keyword_roots.items():
            variants = root_data.get("variants", [])
            # Check if this keyword is in the variants for this root
            for variant in variants:
                if variant.lower() == phrase:
                    semantic_strength = root_data.get("semantic_strength", 0)
                    if semantic_strength > best_score:
                        best_root = root_name
                        best_score = semantic_strength
                    break
        
        # If no exact match, find the root that appears in the phrase
        if not best_root:
            for root_name, root_data in keyword_roots.items():
                if root_name in phrase:
                    best_root = root_name
                    break
        
        # Create enhanced keyword
        enhanced_keyword = {
            **keyword_item,
            "root": best_root or "unknown",
            "root_category": keyword_roots.get(best_root, {}).get("category", "other") if best_root else "other"
        }
        
        keywords_with_roots.append(enhanced_keyword)
    
    # Calculate efficiency metrics
    meaningful_roots = len([r for r in keyword_roots.values() if r.get("is_meaningful", False)])
    original_count = len(keywords)
    reduction_percentage = max(0, ((original_count - meaningful_roots) / original_count * 100)) if original_count > 0 else 0
    
    efficiency_metrics = {
        "original_keywords": original_count,
        "extracted_roots": len(keyword_roots),
        "meaningful_roots": meaningful_roots,
        "reduction_percentage": round(reduction_percentage, 1),
        "efficiency_gain": f"{reduction_percentage:.1f}% keyword complexity reduction"
    }
    
    logger.info(f"[RootExtractionAgent] Enhanced {len(keywords_with_roots)} keywords with AI root analysis ({reduction_percentage:.1f}% reduction)")
    
    return {
        "keywords_with_roots": keywords_with_roots,
        "root_analysis": root_analysis,
        "efficiency_metrics": efficiency_metrics
    } 