#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the complete API pipeline with real CSV data containing 420+ keywords.
This will demonstrate proper keyword allocation with multiple bullet points.
"""

import requests
import json
import time
import sys
import io

# Fix Windows console encoding for emojis
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_api_with_full_csv():
    """Test the API endpoint with full CSV files."""
    
    print("="*70)
    print("🚀 TESTING COMPLETE 4-AGENT PIPELINE WITH FULL CSV DATA")
    print("="*70)
    
    # API endpoint
    url = "http://localhost:8000/api/v1/amazon-sales-intelligence"
    
    # ASIN for the freeze-dried strawberries product
    asin = "B0D5BL35MS"
    marketplace = "US"
    
    # Paths to CSV files
    revenue_csv_path = "backend/csv/Freeze dried strawberry top revenue.csv"
    design_csv_path = "backend/csv/freeze dried strawberry relevant designs.csv"
    
    print(f"\n📋 Test Configuration:")
    print(f"   ASIN: {asin}")
    print(f"   Marketplace: {marketplace}")
    print(f"   Revenue CSV: {revenue_csv_path}")
    print(f"   Design CSV: {design_csv_path}")
    
    # Wait for server to be ready
    print("\n⏳ Waiting for server to start...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:8000/")
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except requests.exceptions.ConnectionError:
            if i < 9:
                time.sleep(2)
            else:
                print("❌ Server failed to start. Please check if port 8000 is available.")
                return False
    
    # Prepare files for upload
    try:
        with open(revenue_csv_path, 'rb') as revenue_file, \
             open(design_csv_path, 'rb') as design_file:
            
            files = {
                'revenue_csv': ('revenue.csv', revenue_file, 'text/csv'),
                'design_csv': ('design.csv', design_file, 'text/csv')
            }
            
            data = {
                'asin_or_url': asin,
                'marketplace': marketplace
            }
            
            print(f"\n🔄 Sending request to API...")
            print(f"   This may take 30-60 seconds with large CSV files...")
            
            # Make the API request
            response = requests.post(url, data=data, files=files, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n" + "="*70)
                print("✅ API REQUEST SUCCESSFUL!")
                print("="*70)
                
                # Extract SEO analysis
                seo_analysis = result.get('seo_analysis', {})
                if seo_analysis.get('success'):
                    analysis = seo_analysis.get('analysis', {})
                    current_seo = analysis.get('current_seo', {})
                    optimized_seo = analysis.get('optimized_seo', {})
                    
                    # Show current state
                    print("\n📊 CURRENT SEO STATE:")
                    keyword_coverage = current_seo.get('keyword_coverage', {})
                    print(f"   Total Keywords Analyzed: {keyword_coverage.get('total_keywords', 0)}")
                    print(f"   Keyword Coverage: {keyword_coverage.get('coverage_percentage', 0)}%")
                    print(f"   Keywords in Title: {current_seo.get('title_analysis', {}).get('keyword_count', 0)}")
                    
                    # Show optimized results
                    print("\n✨ OPTIMIZED SEO CONTENT:")
                    print("\n📝 TITLE:")
                    optimized_title = optimized_seo.get('optimized_title', {})
                    print(f"   {optimized_title.get('content', 'N/A')}")
                    print(f"   Characters: {optimized_title.get('character_count', 0)}/200")
                    print(f"   Keywords: {len(optimized_title.get('keywords_included', []))}")
                    
                    title_keywords = optimized_title.get('keywords_included', [])
                    if title_keywords:
                        print(f"\n   Keywords in Title:")
                        for i, kw in enumerate(title_keywords, 1):
                            print(f"      {i}. {kw}")
                    
                    # Show bullet points
                    optimized_bullets = optimized_seo.get('optimized_bullets', [])
                    print(f"\n📌 BULLET POINTS: {len(optimized_bullets)}")
                    
                    for i, bullet in enumerate(optimized_bullets, 1):
                        content = bullet.get('content', '')
                        char_count = bullet.get('character_count', len(content))
                        keywords = bullet.get('keywords_included', [])
                        
                        print(f"\n   Bullet #{i}: ({char_count} chars)")
                        print(f"   {content}")
                        print(f"   Keywords ({len(keywords)}): {', '.join(keywords)}")
                    
                    # Show backend keywords
                    backend_keywords = optimized_seo.get('optimized_backend_keywords', [])
                    if backend_keywords:
                        print(f"\n🔑 BACKEND KEYWORDS: {len(backend_keywords)}")
                        for i, kw in enumerate(backend_keywords, 1):
                            print(f"   {i}. {kw}")
                    
                    # Show improvement metrics
                    comparison = analysis.get('comparison', {})
                    if comparison:
                        print("\n📈 IMPROVEMENT METRICS:")
                        coverage_improvement = comparison.get('coverage_improvement', {})
                        print(f"   Coverage: {coverage_improvement.get('before_coverage_pct', 0)}% → {coverage_improvement.get('after_coverage_pct', 0)}%")
                        
                        volume_improvement = comparison.get('volume_improvement', {})
                        print(f"   Search Volume: {volume_improvement.get('estimated_volume_before', 0)} → {volume_improvement.get('estimated_volume_after', 0)}")
                        print(f"   New Keywords Added: {len(coverage_improvement.get('new_keywords_added', []))}")
                    
                    # Save result
                    with open('api_full_pipeline_result.json', 'w') as f:
                        json.dump(result, f, indent=2)
                    
                    print("\n" + "="*70)
                    print("✅ SUCCESS! Full pipeline with 420+ keywords completed!")
                    print("📁 Results saved to: api_full_pipeline_result.json")
                    print("="*70)
                    
                    return True
                else:
                    print(f"❌ SEO Analysis Failed: {seo_analysis.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"\n❌ API Request Failed!")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False
                
    except FileNotFoundError as e:
        print(f"\n❌ CSV File Not Found: {e}")
        print("   Please ensure the CSV files exist in backend/csv/")
        return False
    except requests.exceptions.Timeout:
        print("\n❌ Request Timeout!")
        print("   The API took too long to respond (>5 minutes).")
        print("   This might happen with very large CSV files.")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_with_full_csv()
    sys.exit(0 if success else 1)

