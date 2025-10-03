#!/usr/bin/env python3
"""
Check if all keywords are being extracted from both CSV files.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path('..') / 'backend'
sys.path.insert(0, str(backend_path))
from app.services.file_processing.csv_processor import parse_csv_generic

def check_keyword_extraction():
    # Parse CSVs
    revenue_result = parse_csv_generic(str(backend_path / 'csv' / 'Freeze dried strawberry top revenue.csv'))
    design_result = parse_csv_generic(str(backend_path / 'csv' / 'freeze dried strawberry relevant designs.csv'))

    revenue_data = revenue_result['data']
    design_data = design_result['data']

    print('=== REVENUE CSV ANALYSIS ===')
    print(f'Total rows: {len(revenue_data)}')
    print('First 10 keywords:')
    for i, row in enumerate(revenue_data[:10]):
        keyword = row.get('Keyword Phrase', '')
        print(f'  {i+1:2d}. "{keyword}"')

    print()
    print('=== DESIGN CSV ANALYSIS ===')
    print(f'Total rows: {len(design_data)}')
    print('First 10 keywords:')
    for i, row in enumerate(design_data[:10]):
        keyword = row.get('Keyword Phrase', '')
        print(f'  {i+1:2d}. "{keyword}"')

    print()
    print('=== KEYWORD EXTRACTION TEST ===')
    # Test the extraction logic from the script
    revenue_keywords = []
    for row in revenue_data:
        kw = row.get('Keyword Phrase', '')
        if kw and isinstance(kw, str):
            revenue_keywords.append(kw.strip())

    design_keywords = []
    for row in design_data:
        kw = row.get('Keyword Phrase', '')
        if kw and isinstance(kw, str):
            design_keywords.append(kw.strip())

    print(f'Revenue keywords extracted: {len(revenue_keywords)}')
    print(f'Design keywords extracted: {len(design_keywords)}')
    print(f'Total keywords: {len(revenue_keywords) + len(design_keywords)}')

    # Check for duplicates
    all_keywords = revenue_keywords + design_keywords
    unique_keywords = list(dict.fromkeys(all_keywords))
    print(f'Unique keywords: {len(unique_keywords)}')
    print(f'Duplicate keywords: {len(all_keywords) - len(unique_keywords)}')

    # Show some duplicates
    print()
    print('=== DUPLICATE CHECK ===')
    seen = set()
    duplicates = []
    for kw in all_keywords:
        if kw in seen:
            duplicates.append(kw)
        else:
            seen.add(kw)
    
    if duplicates:
        print(f'Duplicate keywords found: {len(duplicates)}')
        print('First 10 duplicates:')
        for i, dup in enumerate(duplicates[:10]):
            print(f'  {i+1:2d}. "{dup}"')
    else:
        print('No duplicate keywords found')

    # Check what the relevancy calculation is actually processing
    print()
    print('=== RELEVANCY PROCESSING LIMIT ===')
    print('The script is only processing the first 50 keywords from each CSV due to this line:')
    print('  for row in csv_data[:top_n]:  # top_n = 50')
    print('This means only 100 keywords total are being scored, not all 648!')
    
    # Show what keywords are actually being processed
    print()
    print('=== ACTUAL KEYWORDS BEING PROCESSED ===')
    print('Revenue CSV (first 50):')
    for i, kw in enumerate(revenue_keywords[:50]):
        print(f'  {i+1:2d}. "{kw}"')
    
    print()
    print('Design CSV (first 50):')
    for i, kw in enumerate(design_keywords[:50]):
        print(f'  {i+1:2d}. "{kw}"')

if __name__ == "__main__":
    check_keyword_extraction()


