#!/usr/bin/env python3
"""
Test script for the Scoring Agent

This script tests the scoring agent's functionality with sample data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.local_agents.scoring import ScoringRunner
from app.local_agents.keyword import KeywordRunner
from app.services.file_processing.csv_processor import parse_csv_generic


def test_scoring_agent():
    """Test the scoring agent with sample data."""
    print("🎯 Testing Scoring Agent...")
    print("=" * 50)
    
    try:
        # Step 1: Load sample data using keyword agent
        print("📊 Loading sample CSV data...")
        csv_file = "US_AMAZON_cerebro_B00O64QJOC_2025-08-21.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return
        
        # Parse CSV
        csv_result = parse_csv_generic(csv_file)
        
        if not csv_result.get("success", False):
            print(f"❌ Failed to parse CSV: {csv_result.get('error', 'Unknown error')}")
            return
        
        csv_data = csv_result["data"]
        print(f"✅ Loaded {len(csv_data)} keywords from CSV")
        
        # Step 2: Run keyword analysis first (required for scoring)
        print("\n🔍 Running keyword analysis...")
        keyword_runner = KeywordRunner()
        
        # Limit to first 20 keywords if we have more than that
        test_data = csv_data[:20] if len(csv_data) > 20 else csv_data
        keyword_result = keyword_runner.run_direct_processing(test_data)
        
        # Check if result is successful
        if not keyword_result.get("success", False):
            print(f"❌ Keyword analysis failed: {keyword_result.get('error', 'Unknown error')}")
            return
        
        # Extract the actual result
        keyword_analysis = keyword_result["result"]
        
        print(f"✅ Keyword analysis completed:")
        print(f"   - Total keywords: {keyword_analysis.total_keywords}")
        print(f"   - Categories found: {len(keyword_analysis.category_stats)}")
        
        # Step 3: Run scoring analysis
        print("\n🎯 Running scoring analysis...")
        scoring_runner = ScoringRunner()
        scoring_result = scoring_runner.run_direct_processing(keyword_analysis)
        
        print(f"✅ Scoring analysis completed:")
        print(f"   - Total keywords analyzed: {scoring_result.total_keywords_analyzed}")
        print(f"   - Critical keywords: {len(scoring_result.critical_keywords)}")
        print(f"   - High priority: {len(scoring_result.high_priority_keywords)}")
        print(f"   - Medium priority: {len(scoring_result.medium_priority_keywords)}")
        print(f"   - Low priority: {len(scoring_result.low_priority_keywords)}")
        print(f"   - Filtered: {len(scoring_result.filtered_keywords)}")
        
        # Step 4: Display top results
        print("\n🏆 TOP CRITICAL KEYWORDS:")
        for i, keyword in enumerate(scoring_result.critical_keywords[:5], 1):
            print(f"   {i}. {keyword.keyword_phrase}")
            print(f"      Intent Score: {int(keyword.intent_score)}/3")
            print(f"      Priority Score: {keyword.priority_score:.1f}/100")
            print(f"      Search Volume: {keyword.competition_metrics.search_volume or 'N/A'}")
            print(f"      Competition: {keyword.competition_metrics.competition_level}")
            print(f"      Business Value: {keyword.business_value}")
            print()
        
        # Step 5: Display top opportunities
        print("🚀 TOP OPPORTUNITIES:")
        for i, keyword in enumerate(scoring_result.top_opportunities[:5], 1):
            print(f"   {i}. {keyword.keyword_phrase}")
            print(f"      Opportunity Score: {keyword.competition_metrics.opportunity_score:.1f}/100")
            print(f"      Opportunity Type: {keyword.opportunity_type}")
            print(f"      Search Volume: {keyword.competition_metrics.search_volume or 'N/A'}")
            print()
        
        # Step 6: Display category performance
        print("📊 CATEGORY PERFORMANCE:")
        for stat in scoring_result.category_stats:
            print(f"   {stat.category_name}:")
            print(f"      Total Keywords: {stat.total_keywords}")
            print(f"      Avg Priority Score: {stat.avg_priority_score:.1f}")
            print(f"      Critical Count: {stat.critical_priority_count}")
            print(f"      High Priority Count: {stat.high_priority_count}")
            print()
        
        # Step 7: Test agent-based scoring (if available)
        print("🤖 Testing agent-based scoring...")
        try:
            agent_result = scoring_runner.run_intent_scoring_only(keyword_analysis)
            if agent_result.get('success'):
                print("✅ Agent-based intent scoring successful")
            else:
                print(f"⚠️ Agent-based scoring failed: {agent_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"⚠️ Agent-based scoring not available: {str(e)}")
        
        print("\n🎉 Scoring Agent test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing scoring agent: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_scoring_agent() 