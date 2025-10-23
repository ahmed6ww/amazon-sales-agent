#!/usr/bin/env python3
"""
Test script to verify backend filtering implementation
"""

from app.local_agents.research.runner import ResearchRunner
from app.services.file_processing.csv_processor import parse_csv_generic
import json

def test_backend_filtering():
    print('=== Backend Filtering Test ===')
    
    # Load CSV data
    revenue_data = parse_csv_generic('csv/Freeze dried strawberry top revenue.csv')
    design_data = parse_csv_generic('csv/freeze dried strawberry relevant designs.csv')
    
    print(f'Revenue CSV: {len(revenue_data.get("data", []))} keywords')
    print(f'Design CSV: {len(design_data.get("data", []))} keywords')
    
    if not revenue_data.get('success') or not design_data.get('success'):
        print(f"CSV loading failed:")
        print(f"  Revenue: {revenue_data.get('error', 'Unknown')}")
        print(f"  Design: {design_data.get('error', 'Unknown')}")
        return None
    
    # Test just the filtering logic without the full research run
    from app.services.keyword_processing.batch_processor import create_agent_optimized_base_relevancy_scores
    
    revenue_keywords = []
    for row in revenue_data.get('data', []):
        kw = row.get('Keyword Phrase', '')
        if kw and isinstance(kw, str):
            revenue_keywords.append(kw.strip())
    
    design_keywords = []
    for row in design_data.get('data', []):
        kw = row.get('Keyword Phrase', '')
        if kw and isinstance(kw, str):
            design_keywords.append(kw.strip())
    
    # Combine and deduplicate
    all_keywords = list(dict.fromkeys(revenue_keywords + design_keywords))
    print(f'Total unique keywords: {len(all_keywords)}')
    
    # Test relevancy computation directly
    def _compute_relevancy_scores(rows, competitor_asins):
        scores = {}
        if not rows or not competitor_asins:
            return scores
        
        asin_set = [a for a in competitor_asins if isinstance(a, str) and len(a) == 10 and a.startswith('B0')]
        if not asin_set:
            return scores
        
        for row in rows:
            kw = str(row.get('Keyword Phrase', '')).strip()
            if not kw:
                continue
                
            ranks_in_top10 = 0
            for asin in asin_set:
                try:
                    rank_val = row.get(asin)
                    if rank_val is None or rank_val == '-':
                        continue
                    rank_num = int(float(rank_val))
                    if rank_num > 0 and rank_num <= 10:
                        ranks_in_top10 += 1
                except Exception:
                    continue
            
            score10 = int(round((ranks_in_top10 / max(1, len(asin_set))) * 10.0))
            scores[kw] = max(scores.get(kw, 0), score10)
        
        return scores
    
    def _extract_asins_from_rows(rows):
        seen = set()
        for row in rows:
            for k in row.keys():
                if isinstance(k, str) and k.startswith('B0') and len(k) == 10:
                    seen.add(k)
        return list(seen)
    
    # Extract ASINs and compute scores
    rev_asins = _extract_asins_from_rows(revenue_data.get('data', []))
    des_asins = _extract_asins_from_rows(design_data.get('data', []))
    combined_asins = list(set(rev_asins + des_asins))
    
    print(f'Revenue ASINs: {len(rev_asins)}')
    print(f'Design ASINs: {len(des_asins)}')
    print(f'Combined ASINs: {len(combined_asins)}')
    
    # Compute relevancy scores
    revenue_scores = _compute_relevancy_scores(revenue_data.get('data', []), combined_asins)
    design_scores = _compute_relevancy_scores(design_data.get('data', []), combined_asins)
    
    # Combine scores
    base_relevancy = revenue_scores.copy()
    for k, v in design_scores.items():
        base_relevancy[k] = max(base_relevancy.get(k, 0), v)
    
    print(f'Keywords with relevancy scores: {len(base_relevancy)}')
    
    # Apply filtering (>= 2)
    min_relevancy_threshold = 2
    high_relevancy_keywords = [
        keyword for keyword, score in base_relevancy.items() 
        if score >= min_relevancy_threshold
    ]
    
    print(f'High-relevancy keywords (>= {min_relevancy_threshold}): {len(high_relevancy_keywords)}')
    
    # Test agent optimization
    agent_scores = create_agent_optimized_base_relevancy_scores(
        high_relevancy_keywords, 
        max_keywords_for_agent=1000
    )
    
    print(f'Keywords sent to agents: {len(agent_scores)}')
    
    # Score distribution
    score_counts = {}
    for score in base_relevancy.values():
        score_counts[score] = score_counts.get(score, 0) + 1
    
    print('\n=== Score Distribution ===')
    for score in sorted(score_counts.keys(), reverse=True):
        count = score_counts[score]
        percentage = (count / len(base_relevancy)) * 100
        print(f'Score {score}: {count} keywords ({percentage:.1f}%)')
    
    print(f'\n=== Filtering Summary ===')
    print(f'Original keywords: {len(all_keywords)}')
    print(f'Keywords with scores: {len(base_relevancy)}')
    print(f'High-relevancy (>=2): {len(high_relevancy_keywords)}')
    print(f'Sent to agents: {len(agent_scores)}')
    
    if len(base_relevancy) > 0:
        filtering_ratio = len(high_relevancy_keywords) / len(base_relevancy)
        print(f'Filtering ratio: {filtering_ratio:.1%}')
    
    return {
        'original_keywords': len(all_keywords),
        'scored_keywords': len(base_relevancy),
        'high_relevancy': len(high_relevancy_keywords),
        'agent_keywords': len(agent_scores),
        'score_distribution': score_counts
    }

if __name__ == "__main__":
    test_backend_filtering()
