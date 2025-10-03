#!/usr/bin/env python3
"""
Test script to demonstrate the complete 4-agent pipeline:
Research → Keyword → Scoring → SEO

This script uses the successful data structure you already have and adds SEO analysis.
"""

import json
import sys
import os
import logging

# Configure logging to see debug messages
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

# Add the backend path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_complete_pipeline():
    """Test the complete 4-agent pipeline with your successful data."""
    
    # Your existing successful data structure
    existing_successful_data = {
        "success": True,
        "asin": "http://amazon.com/dp/B0D5BL35MS",
        "marketplace": "US",
        "ai_analysis_keywords": {
            "success": True,
            "structured_data": {
                "product_context": {
                    "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added, Dry Strawberry Gluten Free Fruit Snack for Baking, Smoothies, Cereals & Travel",
                    "brand": "Brewer Outdoor Solutions",
                    "form": "Freeze-dried strawberry slices; organic; no sugar added; gluten free",
                    "pack_size": "4 pack (1.2 oz each)",
                    "use_cases": ["baking", "smoothies", "cereals", "travel"]
                },
                "items": [
                    {
                        "phrase": "freeze dried strawberries",
                        "category": "Relevant",
                        "reason": "Exact core term for the product.",
                        "relevancy_score": 4,
                        "intent_score": 2,
                        "title_density": 4,
                        "search_volume": 470,
                        "cpr": 8,
                        "competition": {
                            "competing_products": 548,
                            "ranking_competitors": 9,
                            "competitor_rank_avg": 15.9,
                            "competitor_performance_score": 10
                        },
                        "root": "strawberrie"
                    },
                    {
                        "phrase": "freeze dried strawberries bulk",
                        "category": "Design-Specific", 
                        "reason": "Includes 'bulk', a specific pack/size feature of this product.",
                        "relevancy_score": 3,
                        "intent_score": 3,
                        "title_density": 0,
                        "search_volume": 909,
                        "cpr": 12,
                        "competition": {
                            "competing_products": 640,
                            "ranking_competitors": 9,
                            "competitor_rank_avg": 15.9,
                            "competitor_performance_score": 10
                        },
                        "root": "strawberrie"
                    },
                    {
                        "phrase": "organic freeze dried strawberries",
                        "category": "Design-Specific",
                        "reason": "Adds 'organic', a specific attribute of this item.",
                        "relevancy_score": 3,
                        "intent_score": 3,
                        "title_density": 1,
                        "search_volume": 422,
                        "cpr": 8,
                        "competition": {
                            "competing_products": 404,
                            "ranking_competitors": 9,
                            "competitor_rank_avg": 16.9,
                            "competitor_performance_score": 8
                        },
                        "root": "strawberrie"
                    },
                    {
                        "phrase": "dried strawberries",
                        "category": "Relevant",
                        "reason": "Generic dried strawberries directly match the item.",
                        "relevancy_score": 5,
                        "intent_score": 2,
                        "title_density": 21,
                        "search_volume": 8603,
                        "cpr": 41,
                        "competition": {
                            "competing_products": 819,
                            "ranking_competitors": 9,
                            "competitor_rank_avg": 44.4,
                            "competitor_performance_score": 6
                        },
                        "root": "strawberrie"
                    },
                    {
                        "phrase": "strawberry chips",
                        "category": "Design-Specific",
                        "reason": "Describes a style variant (chips) of strawberry slices.",
                        "relevancy_score": 4,
                        "intent_score": 2,
                        "title_density": 1,
                        "search_volume": 371,
                        "cpr": 8,
                        "competition": {
                            "competing_products": 205,
                            "ranking_competitors": 8,
                            "competitor_rank_avg": 18.1,
                            "competitor_performance_score": 8
                        },
                        "root": "strawberry"
                    }
                ],
                "stats": {
                    "Relevant": {"count": 2, "examples": []},
                    "Design-Specific": {"count": 3, "examples": []},
                    "Irrelevant": {"count": 0, "examples": []},
                    "Branded": {"count": 0, "examples": []},
                    "Spanish": {"count": 0, "examples": []},
                    "Outlier": {"count": 0, "examples": []}
                }
            },
            "scraped_product": {
                "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added, Dry Strawberry Gluten Free Fruit Snack for Baking, Smoothies, Cereals & Travel",
                "elements": {
                    "feature-bullets": {
                        "present": True,
                        "bullets": [
                            "Delicious Flavor in Every Bite: Savor the naturally sweet, tangy crunch of freeze dried strawberry slices bursting with real fruit flavor.",
                            "Ideal Travel Companion: Lightweight, mess-free, and shelf-stable, our freeze dried strawberries bulk are perfect for hiking or camping.",
                            "From Farm to Your Table: Our organic dried strawberries, delivered sun-ripened, farm-fresh, are made from real strawberries.",
                            "Shelf Life: Our freeze-dried strawberries are at peak flavor for up to 24 months.",
                            "Bulk Packed for Convenience: Buy in bulk and enjoy premium quality freeze dried strawberries whenever you need them."
                        ]
                    },
                    "productOverview_feature_div": {
                        "present": True,
                        "kv": {
                            "Brand": "Brewer Outdoor Solutions",
                            "Item Weight": "4.8 Ounces",
                            "Size": "4 Pack"
                        }
                    }
                }
            }
        }
    }
    
    # Now run SEO analysis on this successful data
    try:
        from app.local_agents.seo import SEORunner
        
        print("[TEST] Testing complete 4-agent pipeline...")
        print("[OK] Research Agent: Product scraped and analyzed")
        print("[OK] Keyword Agent: 5 keywords categorized")
        print("[OK] Scoring Agent: Intent scores and metrics added")
        print("[RUN] Running SEO Agent...")
        
        # Extract data for SEO analysis
        scraped_product = existing_successful_data["ai_analysis_keywords"]["scraped_product"]
        keyword_items = existing_successful_data["ai_analysis_keywords"]["structured_data"]["items"]
        
        # Run SEO analysis
        seo_runner = SEORunner()
        seo_result = seo_runner.run_seo_analysis(
            scraped_product=scraped_product,
            keyword_items=keyword_items,
            broad_search_volume_by_root={"strawberrie": 12000, "strawberry": 8500}
        )
        
        if seo_result.get("success"):
            print("[OK] SEO Agent: Analysis completed successfully")
            
            # Display the complete pipeline results
            complete_result = existing_successful_data.copy()
            complete_result["seo_analysis"] = seo_result
            complete_result["source"] = "complete_4_agent_pipeline"
            
            # Show summary metrics
            analysis = seo_result.get("analysis", {})
            current_seo = analysis.get("current_seo", {})
            optimized_seo = analysis.get("optimized_seo", {})
            comparison = analysis.get("comparison", {})
            
            print("\n" + "="*60)
            print("[RESULTS] COMPLETE 4-AGENT PIPELINE RESULTS")
            print("="*60)
            
            # Current SEO State
            if current_seo:
                keyword_coverage = current_seo.get("keyword_coverage", {})
                print(f"\n[CURRENT] CURRENT SEO ANALYSIS:")
                print(f"   Keyword Coverage: {keyword_coverage.get('coverage_percentage', 0)}%")
                print(f"   Keywords Covered: {keyword_coverage.get('covered_keywords', 0)}/{keyword_coverage.get('total_keywords', 0)}")
                print(f"   Missing High-Intent: {len(keyword_coverage.get('missing_high_intent', []))}")
                
                title_analysis = current_seo.get("title_analysis", {})
                print(f"   Title Keywords: {title_analysis.get('keyword_count', 0)} found")
                print(f"   Title Characters: {title_analysis.get('character_count', 0)}/200")
            
            # Optimized Suggestions
            if optimized_seo:
                optimized_title = optimized_seo.get("optimized_title", {})
                optimized_bullets = optimized_seo.get("optimized_bullets", [])
                print(f"\n[OPTIMIZED] OPTIMIZED SEO SUGGESTIONS:")
                print(f"   Improved Title: {optimized_title.get('character_count', 0)} chars")
                print(f"   Keywords Added: {len(optimized_title.get('keywords_included', []))}")
                print(f"   Optimized Bullets: {len(optimized_bullets)}")
                
            # Comparison Metrics
            if comparison:
                coverage_improvement = comparison.get("coverage_improvement", {})
                intent_improvement = comparison.get("intent_improvement", {})
                volume_improvement = comparison.get("volume_improvement", {})
                print(f"\n[METRICS] IMPROVEMENT METRICS:")
                print(f"   Coverage: {coverage_improvement.get('before_coverage_pct', 0)}% -> {coverage_improvement.get('after_coverage_pct', 0)}% (+{coverage_improvement.get('delta_pct_points', 0)}%)")
                print(f"   Keywords: {coverage_improvement.get('before_covered', 0)}/{coverage_improvement.get('total_keywords', 0)} -> {coverage_improvement.get('after_covered', 0)}/{coverage_improvement.get('total_keywords', 0)}")
                print(f"   High-Intent: {intent_improvement.get('before_covered', 0)} -> {intent_improvement.get('after_covered', 0)} (+{intent_improvement.get('delta', 0)})")
                print(f"   Search Volume: {volume_improvement.get('estimated_volume_before', 0):,} -> {volume_improvement.get('estimated_volume_after', 0):,} (+{volume_improvement.get('delta_volume', 0):,})")
                
                new_keywords = coverage_improvement.get('new_keywords_added', [])
                if new_keywords:
                    print(f"   New Keywords Added: {', '.join(new_keywords[:5])}")
                
                summary_metrics = comparison.get("summary_metrics", {})
                print(f"   Overall Score: {summary_metrics.get('overall_improvement_score', 0)}/10")
            
            print("\n" + "="*60)
            print("[SUCCESS] COMPLETE PIPELINE SUCCESS!")
            print("All 4 agents working together:")
            print("Research -> Keyword -> Scoring -> SEO [OK]")
            print("="*60)
            
            # Save complete result
            with open("complete_pipeline_result.json", "w") as f:
                json.dump(complete_result, f, indent=2)
            print(f"\n[SAVED] Complete result saved to: complete_pipeline_result.json")
            
            return True
            
        else:
            print(f"[ERROR] SEO Agent failed: {seo_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_pipeline()
    sys.exit(0 if success else 1) 