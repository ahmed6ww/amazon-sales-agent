#!/usr/bin/env python3
"""
Filter keywords by relevancy score from CSV files.

This script:
1. Reads both CSV files from backend/csv/
2. Calculates relevancy scores for keywords
3. Filters keywords with relevancy score >= 5
4. Creates a new CSV with filtered results

Expected flow:
647 keywords → relevancy calculation → filter (>=5) → ~200-300 keywords
"""

import sys
import os
import csv
from typing import Dict, List, Any
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.file_processing.csv_processor import parse_csv_generic


def calculate_relevancy_scores(csv_data: List[Dict[str, Any]], competitor_asins: List[str], top_n: int = 50) -> Dict[str, int]:
    """
    Calculate relevancy scores based on keyword rankings in top 10.
    
    Formula: (ranks_in_top10 / total_competitors) * 10
    
    Args:
        csv_data: List of CSV rows with keyword data
        competitor_asins: List of competitor ASINs
        top_n: Maximum number of keywords to process
        
    Returns:
        Dictionary of keyword -> relevancy score (0-10)
    """
    scores: Dict[str, int] = {}
    
    if not csv_data or not competitor_asins:
        return scores
    
    # Filter valid ASINs (B0 format, 10 characters)
    asin_set = [
        a for a in competitor_asins 
        if isinstance(a, str) and len(a) == 10 and a.startswith('B0')
    ][:top_n]
    
    if not asin_set:
        return scores
    
    print(f"Processing {len(csv_data)} keywords against {len(asin_set)} competitors...")
    
    for row in csv_data:
        kw = str(row.get('Keyword Phrase', '')).strip()
        if not kw:
            continue
            
        ranks_in_top10 = 0
        
        # Count how many competitors rank in top 10 for this keyword
        for asin in asin_set:
            try:
                rank_val = row.get(asin)
                if rank_val is None:
                    continue
                    
                rank_num = int(float(rank_val))
                if rank_num > 0 and rank_num <= 10:  # Top 10 ranking
                    ranks_in_top10 += 1
                    
            except (ValueError, TypeError):
                continue
        
        # Calculate score (0-10 scale)
        score10 = int(round((ranks_in_top10 / max(1, len(asin_set))) * 10.0))
        scores[kw] = max(scores.get(kw, 0), score10)  # Keep max score across CSVs
        
    return scores


def extract_competitor_asins(csv_data: List[Dict[str, Any]]) -> List[str]:
    """
    Extract competitor ASINs from CSV headers.
    
    Args:
        csv_data: List of CSV rows
        
    Returns:
        List of ASIN strings
    """
    seen_asins = set()
    
    # Check all rows for ASINs
    for row in csv_data:
        for key in row.keys():
            if isinstance(key, str) and key.startswith('B0') and len(key) == 10:
                seen_asins.add(key)
    
    # Return stable order, limited to reasonable number
    return list(seen_asins)[:50]


def filter_keywords_by_relevancy(threshold: int = 5) -> Dict[str, Any]:
    """
    Main function to filter keywords by relevancy score.
    
    Args:
        threshold: Minimum relevancy score (default: 5)
        
    Returns:
        Dictionary with filtering results and statistics
    """
    # File paths
    revenue_csv_path = backend_path / "csv" / "Freeze dried strawberry top revenue.csv"
    design_csv_path = backend_path / "csv" / "freeze dried strawberry relevant designs.csv"
    
    print("=== Keyword Relevancy Filtering ===")
    print(f"Revenue CSV: {revenue_csv_path}")
    print(f"Design CSV: {design_csv_path}")
    print(f"Relevancy threshold: >= {threshold}")
    print()
    
    # Parse CSV files
    print("1. Parsing CSV files...")
    revenue_result = parse_csv_generic(str(revenue_csv_path))
    design_result = parse_csv_generic(str(design_csv_path))
    
    if not revenue_result.get('success'):
        raise ValueError(f"Failed to parse revenue CSV: {revenue_result.get('error')}")
    if not design_result.get('success'):
        raise ValueError(f"Failed to parse design CSV: {design_result.get('error')}")
    
    revenue_data = revenue_result.get('data', [])
    design_data = design_result.get('data', [])
    
    print(f"   Revenue CSV: {len(revenue_data)} keywords")
    print(f"   Design CSV: {len(design_data)} keywords")
    print(f"   Total keywords: {len(revenue_data) + len(design_data)}")
    print()
    
    # Extract competitor ASINs
    print("2. Extracting competitor ASINs...")
    revenue_asins = extract_competitor_asins(revenue_data)
    design_asins = extract_competitor_asins(design_data)
    
    # Combine ASINs (remove duplicates)
    all_asins = list(set(revenue_asins + design_asins))
    print(f"   Revenue ASINs: {len(revenue_asins)}")
    print(f"   Design ASINs: {len(design_asins)}")
    print(f"   Combined ASINs: {len(all_asins)}")
    print()
    
    # Calculate relevancy scores
    print("3. Calculating relevancy scores...")
    revenue_scores = calculate_relevancy_scores(revenue_data, all_asins)
    design_scores = calculate_relevancy_scores(design_data, all_asins)
    
    # Combine scores (keep max for same keyword)
    combined_scores = revenue_scores.copy()
    for kw, score in design_scores.items():
        combined_scores[kw] = max(combined_scores.get(kw, 0), score)
    
    print(f"   Revenue keywords scored: {len(revenue_scores)}")
    print(f"   Design keywords scored: {len(design_scores)}")
    print(f"   Total unique keywords: {len(combined_scores)}")
    print()
    
    # Filter by threshold
    print(f"4. Filtering keywords with relevancy >= {threshold}...")
    filtered_scores = {kw: score for kw, score in combined_scores.items() if score >= threshold}
    
    print(f"   Keywords before filtering: {len(combined_scores)}")
    print(f"   Keywords after filtering: {len(filtered_scores)}")
    print(f"   Filtering ratio: {len(filtered_scores)/len(combined_scores):.1%}")
    print()
    
    # Show score distribution
    print("5. Score distribution:")
    score_counts = {}
    for score in combined_scores.values():
        score_counts[score] = score_counts.get(score, 0) + 1
    
    for score in sorted(score_counts.keys(), reverse=True):
        count = score_counts[score]
        percentage = (count / len(combined_scores)) * 100
        print(f"   Score {score}: {count} keywords ({percentage:.1f}%)")
    print()
    
    # Create filtered CSV
    print("6. Creating filtered CSV...")
    output_path = Path(__file__).parent / f"filtered_keywords_relevancy_{threshold}.csv"
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        if filtered_scores:
            # Use all available columns from the first row
            sample_row = revenue_data[0] if revenue_data else design_data[0]
            fieldnames = ['Keyword Phrase', 'Relevancy Score'] + list(sample_row.keys())
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for keyword, score in sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True):
                # Find the original row data for this keyword
                row_data = None
                for row in revenue_data + design_data:
                    if row.get('Keyword Phrase', '').strip() == keyword:
                        row_data = row.copy()
                        break
                
                if row_data:
                    row_data['Relevancy Score'] = score
                    # Only write fields that exist in fieldnames
                    filtered_row = {k: v for k, v in row_data.items() if k in fieldnames}
                    writer.writerow(filtered_row)
                else:
                    # Create minimal row if not found
                    writer.writerow({
                        'Keyword Phrase': keyword,
                        'Relevancy Score': score
                    })
    
    print(f"   Output file: {output_path}")
    print(f"   Filtered keywords saved: {len(filtered_scores)}")
    print()
    
    # Show top keywords
    print("7. Top filtered keywords:")
    top_keywords = sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (keyword, score) in enumerate(top_keywords, 1):
        print(f"   {i:2d}. {keyword} (score: {score})")
    print()
    
    return {
        'total_keywords': len(combined_scores),
        'filtered_keywords': len(filtered_scores),
        'filtering_ratio': len(filtered_scores) / len(combined_scores),
        'threshold': threshold,
        'output_file': str(output_path),
        'score_distribution': score_counts,
        'top_keywords': top_keywords
    }


if __name__ == "__main__":
    # Run the filtering
    results = filter_keywords_by_relevancy(threshold=4)
    
    print("=== SUMMARY ===")
    print(f"Total keywords processed: {results['total_keywords']}")
    print(f"Keywords with relevancy >= 5: {results['filtered_keywords']}")
    print(f"Filtering efficiency: {results['filtering_ratio']:.1%}")
    print(f"Output file: {results['output_file']}")
    
    # Save results as JSON for analysis
    import json
    results_json_path = Path(__file__).parent / "filtering_results.json"
    with open(results_json_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {results_json_path}")
