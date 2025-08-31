#!/usr/bin/env python3
"""
Test script for the Keyword Agent implementation.
Tests the agent with real Helium10 CSV data.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.file_processing.csv_processor import parse_csv_generic
from app.local_agents.keyword.runner import KeywordRunner
from app.local_agents.keyword.helper_methods import categorize_keywords_from_csv

def test_keyword_agent():
    """Test the keyword agent with real CSV data"""
    
    print("🚀 Testing Keyword Agent Implementation")
    print("=" * 50)
    
    # Load the CSV data
    csv_file_path = "US_AMAZON_cerebro_B00O64QJOC_2025-08-21.csv"
    
    print(f"📁 Loading CSV data from: {csv_file_path}")
    
    # Parse CSV
    csv_result = parse_csv_generic(csv_file_path)
    
    if not csv_result["success"]:
        print(f"❌ Failed to parse CSV: {csv_result['error']}")
        return
    
    csv_data = csv_result["data"]
    print(f"✅ Loaded {len(csv_data)} keywords from CSV")
    
    # Test direct helper method first
    print("\n🔧 Testing direct helper methods...")
    
    try:
        result = categorize_keywords_from_csv(csv_data[:10])  # Test with first 10 keywords
        
        print(f"✅ Direct processing successful!")
        print(f"   - Total keywords: {result.total_keywords}")
        print(f"   - Processed keywords: {result.processed_keywords}")
        print(f"   - Filtered keywords: {result.filtered_keywords}")
        print(f"   - Processing time: {result.processing_time:.2f}s")
        print(f"   - Data quality score: {result.data_quality_score}%")
        
        # Show category distribution
        print("\n📊 Category Distribution:")
        for category, stats in result.category_stats.items():
            print(f"   - {category.value}: {stats.keyword_count} keywords")
        
        # Show top opportunities
        if result.top_opportunities:
            print(f"\n🎯 Top Opportunities:")
            for opp in result.top_opportunities[:3]:
                print(f"   - {opp}")
        
        # Show root word analysis
        if result.root_word_analysis:
            print(f"\n🌳 Top Root Words:")
            for rwa in result.root_word_analysis[:3]:
                print(f"   - '{rwa.root_word}': {rwa.total_search_volume} volume, {rwa.keyword_count} keywords")
        
    except Exception as e:
        print(f"❌ Direct processing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Test with KeywordRunner (direct processing)
    print("\n🏃 Testing KeywordRunner (direct processing)...")
    
    try:
        runner = KeywordRunner()
        runner_result = runner.run_direct_processing(csv_data[:5])  # Test with first 5 keywords
        
        if runner_result["success"]:
            print("✅ KeywordRunner direct processing successful!")
            result = runner_result["result"]
            print(f"   - Keywords processed: {result.processed_keywords}")
            print(f"   - Categories found: {len(result.category_stats)}")
        else:
            print(f"❌ KeywordRunner failed: {runner_result['error']}")
            
    except Exception as e:
        print(f"❌ KeywordRunner test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Keyword Agent testing completed!")
    print("\nNext steps:")
    print("1. ✅ Keyword Agent implemented and tested")
    print("2. 🔄 Next: Implement Scoring Agent")
    print("3. 🔄 Next: Implement SEO Agent")
    print("4. 🔄 Next: Create main orchestration workflow")

if __name__ == "__main__":
    test_keyword_agent() 