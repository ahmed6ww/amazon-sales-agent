"""
Batch Keyword Processing Service

This service handles large keyword datasets by processing them in smaller batches
to avoid timeout issues while maintaining the benefits of root-based optimization.
"""

from typing import Dict, List, Any, Optional
import logging
from .root_extraction import get_priority_roots_for_search
from app.local_agents.keyword.subagents.root_extraction_agent import extract_roots_ai

logger = logging.getLogger(__name__)


def _convert_ai_analysis_to_legacy_format(ai_analysis: Dict[str, Any], original_keywords: List[str]) -> Dict[str, Any]:
    """
    Convert AI root analysis to the legacy format expected by the research runner.
    This maintains compatibility while using AI intelligence.
    """
    keyword_roots_data = ai_analysis.get("keyword_roots", {})
    analysis_summary = ai_analysis.get("analysis_summary", {})
    category_breakdown = ai_analysis.get("category_breakdown", {})
    
    # Extract meaningful roots (AI determines meaningfulness)
    meaningful_roots = [
        root_name for root_name, root_data in keyword_roots_data.items()
        if root_data.get("is_meaningful", False)
    ]
    
    # Get priority roots from the most meaningful ones (limited for efficiency)
    priority_roots = meaningful_roots[:30]  # Top 30 most meaningful roots
    
    # Create legacy-compatible structure
    return {
        'total_keywords': len(original_keywords),
        'total_roots': len(keyword_roots_data),
        'meaningful_roots': len(meaningful_roots),
        'priority_roots': priority_roots,
        'roots': keyword_roots_data,  # Full AI analysis
        'summary': {
            'top_product_ingredients': category_breakdown.get('product_ingredient', []),
            'top_processing_methods': category_breakdown.get('attribute_processing', []),
            'top_brands': category_breakdown.get('brand', [])
        },
        'ai_enhanced': True,
        'efficiency_metrics': {
            'original_keywords': len(original_keywords),
            'meaningful_roots': len(meaningful_roots),
            'reduction_percentage': analysis_summary.get('efficiency_gain', '0% reduction'),
            'ai_powered': True
        }
    }


def process_keywords_in_batches(
    all_keywords: List[str], 
    batch_size: int = 100,
    max_priority_roots: int = 25
) -> Dict[str, Any]:
    """
    Process a large list of keywords in batches to avoid memory and timeout issues.
    
    Args:
        all_keywords: Complete list of keywords to process
        batch_size: Number of keywords to process in each batch
        max_priority_roots: Maximum number of priority roots to return
        
    Returns:
        Combined analysis results with efficiency metrics
    """
    
    if not all_keywords:
        return {
            'total_keywords': 0,
            'meaningful_roots': 0,
            'priority_roots': [],
            'efficiency_metrics': {},
            'processing_summary': 'No keywords provided'
        }
    
    # Remove duplicates while preserving order
    unique_keywords = list(dict.fromkeys([kw.strip() for kw in all_keywords if kw and kw.strip()]))
    total_unique = len(unique_keywords)
    
    logger.info(f"Processing {total_unique} unique keywords in batches of {batch_size}")
    
    # If dataset is small enough, process directly with AI
    if total_unique <= batch_size:
        logger.info("Dataset small enough for direct AI processing")
        ai_analysis = extract_roots_ai(unique_keywords)
        return _convert_ai_analysis_to_legacy_format(ai_analysis, unique_keywords)
    
    # For large datasets, use AI-powered batch processing approach
    logger.info("Large dataset detected - using AI-powered batch processing")
    
    # Step 1: Process in batches with AI analysis
    all_roots = {}
    batch_results = []
    
    for i in range(0, total_unique, batch_size):
        batch = unique_keywords[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(total_unique + batch_size - 1)//batch_size}")
        
        try:
            batch_analysis = extract_roots_ai(batch)
            batch_roots = batch_analysis.get("keyword_roots", {})
            
            # Merge roots from this batch
            for root_name, root_data in batch_roots.items():
                if root_name in all_roots:
                    # Combine variants and update frequency
                    all_roots[root_name]["variants"].extend(root_data.get("variants", []))
                    all_roots[root_name]["frequency"] += root_data.get("frequency", 0)
                    all_roots[root_name]["variants"] = list(set(all_roots[root_name]["variants"]))  # Remove duplicates
                else:
                    all_roots[root_name] = root_data.copy()
            
            batch_results.append(batch_analysis)
            
        except Exception as e:
            logger.warning(f"Batch processing failed for batch {i//batch_size + 1}: {e}")
            continue
    
    # Consolidate results
    root_analysis = {
        'total_keywords': total_unique,
        'total_roots': len(all_roots),
        'meaningful_roots': len([r for r in all_roots.values() if r.get("is_meaningful", False)]),
        'roots': all_roots,
        'ai_enhanced': True,
        'batch_processed': True
    }
    
    # Step 2: Get priority roots for efficient processing (AI-enhanced)
    meaningful_roots = [
        root_name for root_name, root_data in all_roots.items()
        if root_data.get("is_meaningful", False)
    ]
    
    # Sort by consolidation potential and semantic strength
    sorted_roots = sorted(
        meaningful_roots,
        key=lambda r: (
            all_roots[r].get("consolidation_potential", 0),
            all_roots[r].get("semantic_strength", 0),
            all_roots[r].get("frequency", 0)
        ),
        reverse=True
    )
    
    priority_roots = sorted_roots[:max_priority_roots]
    
    # Step 3: Calculate efficiency metrics
    original_count = total_unique
    priority_count = len(priority_roots)
    meaningful_roots_count = root_analysis.get('meaningful_roots', 0)
    
    efficiency_metrics = {
        'original_keywords': original_count,
        'meaningful_roots': meaningful_roots_count,
        'priority_roots': priority_count,
        'reduction_percentage': round((1 - priority_count / original_count) * 100, 1) if original_count > 0 else 0,
        'efficiency_gain': f"{round((1 - priority_count / original_count) * 100, 1)}%",
        'memory_optimization': f"~{round((1 - priority_count / original_count) * 100)}% reduction in contextual memory usage",
        'api_optimization': f"Reduced processing from {original_count} to {priority_count} terms",
        'processing_method': 'optimized_root_based'
    }
    
    # Step 4: Enhance the analysis results
    enhanced_result = {
        'total_keywords': original_count,
        'total_roots': root_analysis.get('total_roots', 0),
        'meaningful_roots': meaningful_roots_count,
        'priority_roots': priority_roots,
        'roots': root_analysis.get('roots', {}),
        'summary': root_analysis.get('summary', {}),
        'efficiency_metrics': efficiency_metrics,
        'processing_summary': f"Processed {original_count} keywords → {priority_count} priority roots ({efficiency_metrics['reduction_percentage']}% reduction)",
        'batch_info': {
            'total_keywords': original_count,
            'batch_size_used': batch_size,
            'processing_approach': 'root_optimization',
            'timeout_prevention': True
        }
    }
    
    logger.info(f"Batch processing complete: {original_count} keywords → {priority_count} priority roots")
    
    return enhanced_result


def optimize_keyword_processing_for_agents(
    revenue_keywords: List[str],
    design_keywords: List[str],
    batch_size: int = 50
) -> Dict[str, Any]:
    """
    Optimized keyword processing specifically for the agent workflow.
    Combines keywords from multiple sources and provides optimized analysis.
    
    Args:
        revenue_keywords: Keywords from revenue CSV
        design_keywords: Keywords from design CSV  
        batch_size: Batch size for processing
        
    Returns:
        Optimized analysis results for agent consumption
    """
    
    # Combine all keywords
    all_keywords = []
    source_stats = {}
    
    if revenue_keywords:
        clean_revenue = [kw.strip() for kw in revenue_keywords if kw and kw.strip()]
        all_keywords.extend(clean_revenue)
        source_stats['revenue'] = {
            'original_count': len(revenue_keywords),
            'clean_count': len(clean_revenue),
            'sample': clean_revenue[:5]
        }
    
    if design_keywords:
        clean_design = [kw.strip() for kw in design_keywords if kw and kw.strip()]
        all_keywords.extend(clean_design)
        source_stats['design'] = {
            'original_count': len(design_keywords),
            'clean_count': len(clean_design),
            'sample': clean_design[:5]
        }
    
    # Process with batch optimization
    analysis_result = process_keywords_in_batches(
        all_keywords, 
        batch_size=batch_size,
        max_priority_roots=30  # Slightly higher for multi-source data
    )
    
    # Add source statistics
    analysis_result['source_statistics'] = source_stats
    analysis_result['data_sources'] = {
        'revenue_csv': len(revenue_keywords) if revenue_keywords else 0,
        'design_csv': len(design_keywords) if design_keywords else 0,
        'total_combined': len(all_keywords)
    }
    
    return analysis_result


def create_agent_optimized_base_relevancy_scores(
    keywords: List[str],
    max_keywords_for_agent: int = 100
) -> Dict[str, int]:
    """
    Create optimized base relevancy scores for agent processing.
    Limits the number of keywords sent to agents to prevent timeouts.
    
    Args:
        keywords: List of all keywords
        max_keywords_for_agent: Maximum keywords to send to AI agents
        
    Returns:
        Dictionary of keyword -> relevancy score (limited set)
    """
    
    if not keywords:
        return {}
    
    # If we have too many keywords, use root analysis to prioritize
    if len(keywords) > max_keywords_for_agent:
        logger.info(f"Optimizing {len(keywords)} keywords for agent processing (limit: {max_keywords_for_agent})")
        
        # Get root analysis to identify most important keywords
        root_analysis = group_keywords_by_roots(keywords)
        priority_roots = get_priority_roots_for_search(root_analysis, max_roots=20)
        
        # Select keywords that contain priority roots
        selected_keywords = []
        roots_data = root_analysis.get('roots', {})
        
        for root in priority_roots:
            if root in roots_data:
                variants = roots_data[root].get('variants', [])
                selected_keywords.extend(variants[:5])  # Max 5 variants per root
        
        # Remove duplicates and limit to max
        selected_keywords = list(dict.fromkeys(selected_keywords))[:max_keywords_for_agent]
        
        logger.info(f"Selected {len(selected_keywords)} priority keywords for agent processing")
        
        # Create relevancy scores (higher for priority roots)
        base_scores = {}
        for i, keyword in enumerate(selected_keywords):
            # Score based on position (earlier = higher priority)
            score = max(1, 10 - (i // 10))  # Scores from 10 down to 1
            base_scores[keyword] = score
            
        return base_scores
    
    else:
        # Small dataset - create basic relevancy scores for all
        base_scores = {}
        for keyword in keywords:
            base_scores[keyword] = 5  # Default moderate relevancy
        return base_scores 