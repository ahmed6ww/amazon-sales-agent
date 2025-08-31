"""
Test SEO Agent

Test script to validate SEO Agent functionality with sample data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.local_agents.seo import SEORunner
from app.local_agents.keyword import KeywordRunner
from app.local_agents.scoring import ScoringRunner
from app.services.file_processing.csv_processor import parse_csv_generic

def test_seo_agent():
    """Test the SEO Agent with sample keyword and scoring data."""
    
    print("🔍 Testing SEO Agent...")
    print("=" * 50)
    
    try:
        # Load sample CSV data
        csv_file = "US_AMAZON_cerebro_B00O64QJOC_2025-08-21.csv"
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return False
        
        # Parse CSV data
        csv_result = parse_csv_generic(csv_file)
        if not csv_result.get("success"):
            print(f"❌ Failed to parse CSV: {csv_result.get('error')}")
            return False
        
        csv_data = csv_result["data"][:50]  # Use first 50 rows for testing
        print(f"📊 Loaded {len(csv_data)} keywords from CSV")
        
        # Step 1: Run keyword analysis
        print("\n1. Running Keyword Analysis...")
        keyword_runner = KeywordRunner()
        keyword_result = keyword_runner.run_direct_processing(csv_data)
        
        if not keyword_result.get("success"):
            print(f"❌ Keyword analysis failed: {keyword_result.get('error')}")
            return False
        
        keyword_analysis = keyword_result["result"]
        print(f"✅ Analyzed {keyword_analysis.total_keywords} keywords")
        
        # Step 2: Run scoring analysis
        print("\n2. Running Scoring Analysis...")
        scoring_runner = ScoringRunner()
        scoring_result = scoring_runner.run_direct_processing(keyword_analysis)
        print(f"✅ Scored keywords with {len(scoring_result.critical_keywords)} critical keywords")
        
        # Step 3: Run SEO optimization
        print("\n3. Running SEO Optimization...")
        seo_runner = SEORunner()
        
        # Prepare test data
        current_listing = {
            "title": "Baby Changing Pad - Waterproof Portable Diaper Changing Mat",
            "bullets": [
                "Waterproof and easy to clean surface",
                "Portable design for travel convenience",
                "Safe and comfortable for baby"
            ],
            "features": ["waterproof", "portable", "safe", "comfortable"],
            "brand": "BabyBrand",
            "category": "baby_products"
        }
        
        # Extract keywords from scoring results
        critical_keywords = [kw.keyword_phrase for kw in scoring_result.critical_keywords[:5]]
        high_priority_keywords = [kw.keyword_phrase for kw in scoring_result.high_priority_keywords[:8]]
        medium_priority_keywords = [kw.keyword_phrase for kw in scoring_result.medium_priority_keywords[:10]]
        opportunity_keywords = [kw.keyword_phrase for kw in scoring_result.top_opportunities[:10]]
        
        print(f"   Critical keywords: {critical_keywords[:3]}...")
        print(f"   High priority keywords: {high_priority_keywords[:3]}...")
        print(f"   Opportunity keywords: {opportunity_keywords[:3]}...")
        
        # Run SEO optimization
        seo_optimization = seo_runner.run_direct_optimization(
            current_listing=current_listing,
            critical_keywords=critical_keywords,
            high_priority_keywords=high_priority_keywords,
            medium_priority_keywords=medium_priority_keywords,
            opportunity_keywords=opportunity_keywords,
            keyword_analysis={"total_keywords": keyword_analysis.total_keywords},
            scoring_analysis={
                "critical_keywords": critical_keywords,
                "high_priority_keywords": high_priority_keywords,
                "opportunity_keywords": opportunity_keywords
            },
            competitor_data={}
        )
        
        # Display results
        print("\n🎯 SEO OPTIMIZATION RESULTS")
        print("=" * 50)
        
        # Title optimization
        print(f"\n📋 TITLE OPTIMIZATION:")
        print(f"   Current: {seo_optimization.title_optimization.current_title}")
        print(f"   Optimized: {seo_optimization.title_optimization.recommended_title}")
        print(f"   Improvement: {seo_optimization.title_optimization.improvement_score}%")
        print(f"   Keywords added: {seo_optimization.title_optimization.keywords_added}")
        
        # Bullet points
        print(f"\n• BULLET POINTS:")
        for i, bullet in enumerate(seo_optimization.bullet_optimization.recommended_bullets, 1):
            print(f"   {i}. {bullet}")
        print(f"   Keywords coverage: {seo_optimization.bullet_optimization.keywords_coverage}")
        
        # Backend keywords
        print(f"\n🔍 BACKEND KEYWORDS:")
        backend_keywords = seo_optimization.backend_optimization.recommended_keywords
        print(f"   Keywords ({len(backend_keywords)}): {', '.join(backend_keywords[:10])}...")
        print(f"   Character usage: {seo_optimization.backend_optimization.character_count}/250")
        print(f"   Coverage improvement: {seo_optimization.backend_optimization.coverage_improvement}")
        
        # Content gaps
        print(f"\n📊 CONTENT GAPS ({len(seo_optimization.content_gaps)}):")
        for gap in seo_optimization.content_gaps[:3]:
            print(f"   • {gap.section.value}: {gap.recommended_content[:100]}...")
        
        # Competitive advantages
        print(f"\n🚀 COMPETITIVE ADVANTAGES ({len(seo_optimization.competitive_advantages)}):")
        for advantage in seo_optimization.competitive_advantages[:3]:
            print(f"   • {advantage.advantage_type}: {advantage.description[:100]}...")
        
        # SEO Score
        print(f"\n📈 SEO PERFORMANCE SCORE:")
        print(f"   Overall Score: {seo_optimization.seo_score.overall_score}/100")
        print(f"   Title Score: {seo_optimization.seo_score.title_score}/100")
        print(f"   Bullets Score: {seo_optimization.seo_score.bullets_score}/100")
        print(f"   Backend Score: {seo_optimization.seo_score.backend_score}/100")
        print(f"   Improvement Potential: {seo_optimization.seo_score.improvement_potential}%")
        
        # Quick wins
        print(f"\n⚡ QUICK WINS ({len(seo_optimization.quick_wins)}):")
        for win in seo_optimization.quick_wins:
            print(f"   • {win}")
        
        # Long-term strategy
        print(f"\n📅 LONG-TERM STRATEGY ({len(seo_optimization.long_term_strategy)}):")
        for strategy in seo_optimization.long_term_strategy:
            print(f"   • {strategy}")
        
        print(f"\n✅ SEO Agent test completed successfully!")
        print(f"🎉 All optimization components working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ SEO Agent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_seo_agent() 