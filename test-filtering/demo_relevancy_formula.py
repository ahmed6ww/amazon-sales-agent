#!/usr/bin/env python3
"""
Demonstrate the relevancy formula in action with sample keywords.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path('..') / 'backend'
sys.path.insert(0, str(backend_path))
from app.services.file_processing.csv_processor import parse_csv_generic

def demo_relevancy_formula():
    # Parse CSVs
    revenue_result = parse_csv_generic(str(backend_path / 'csv' / 'Freeze dried strawberry top revenue.csv'))
    revenue_data = revenue_result['data']

    # Extract ASINs
    asins = []
    for row in revenue_data[:5]:
        for key in row.keys():
            if isinstance(key, str) and key.startswith('B0') and len(key) == 10:
                asins.append(key)

    asins = list(set(asins))[:5]  # Get 5 unique ASINs
    print('=== RELEVANCY FORMULA DEMONSTRATION ===')
    print(f'Competitor ASINs: {asins}')
    print()

    # Show formula for sample keywords
    sample_keywords = ['freeze dried strawberry', 'freeze dried apples', 'strawberry slices']

    for keyword in sample_keywords:
        print(f'Keyword: "{keyword}"')
        
        # Find the row for this keyword
        keyword_row = None
        for row in revenue_data:
            if row.get('Keyword Phrase', '').strip() == keyword:
                keyword_row = row
                break
        
        if keyword_row:
            ranks_in_top10 = 0
            print('  Rankings:')
            
            for asin in asins:
                rank_val = keyword_row.get(asin)
                if rank_val is not None:
                    try:
                        rank_num = int(float(rank_val))
                        if rank_num > 0 and rank_num <= 10:
                            ranks_in_top10 += 1
                            print(f'    {asin}: Rank {rank_num} ✓ (top 10)')
                        else:
                            print(f'    {asin}: Rank {rank_num} ✗ (not top 10)')
                    except:
                        print(f'    {asin}: Invalid rank value')
                else:
                    print(f'    {asin}: No ranking data')
            
            # Calculate score
            score = int(round((ranks_in_top10 / max(1, len(asins))) * 10.0))
            print(f'  Formula: ({ranks_in_top10} ranks in top 10 / {len(asins)} competitors) × 10 = {score}')
            print(f'  Relevancy Score: {score}')
        else:
            print('  Keyword not found in revenue CSV')
        print()

if __name__ == "__main__":
    demo_relevancy_formula()


