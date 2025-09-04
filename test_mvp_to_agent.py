#!/usr/bin/env python3
"""
Test MVP Scraper Data → Research Agent Integration
Following OpenAI Agents SDK best practices for deterministic flows
"""

import sys
from pathlib import Path
# Ensure backend package is on the path for imports
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

import asyncio
import json
from app.local_agents.research.runner import ResearchRunner  # type: ignore
from app.local_agents.research.helper_methods import scrape_amazon_listing  # type: ignore

async def test_mvp_data_to_agent():
    """
    Test the complete flow:
    1. Scrape product data using MVP scraper
    2. Pass clean data to research agent
    3. Get AI analysis without tool conflicts
    """
    
    # Test URL - Samsung TV we were working with
    test_url = "https://www.amazon.ae/Samsung-PurColor-Upscaling-Q-Symphony-UA65DU7000UXZN/dp/B0D1R8JNF6"
    
    print("🔄 Step 1: Scraping product data with MVP scraper...")
    
    # Get clean MVP data using our working scraper
    scrape_result = scrape_amazon_listing(test_url)
    
    if not scrape_result.get("success"):
        print(f"❌ Scraping failed: {scrape_result.get('error')}")
        return
    
    scraped_data = scrape_result.get("data", {})
    print(f"✅ Successfully scraped: {scraped_data.get('title', 'No title')[:50]}...")
    print(f"📊 Data includes:")
    print(f"   - Images: {scraped_data.get('images', {}).get('image_count', 0)}")
    print(f"   - A+ Content: {len(scraped_data.get('aplus_content', {}).get('sections', []))}")
    print(f"   - Reviews: {len(scraped_data.get('reviews', {}).get('sample_reviews', []))}")
    print(f"   - Q&A: {len(scraped_data.get('qa_section', {}).get('questions', []))}")
    
    print("\n🤖 Step 2: Passing data to Research Agent...")
    
    # Initialize the Research Runner
    runner = ResearchRunner()
    
    # Pass the pre-fetched data directly to the agent (no scraping inside agent)
    analysis_result = runner.run_research(
        asin_or_url=test_url
    )
    
    if analysis_result.get("success"):
        print("✅ Research Agent Analysis Complete!")
        print("\n📝 AI Analysis:")
        print("=" * 60)
        print(analysis_result.get("analysis", "No analysis"))
        print("=" * 60)
        
        print(f"\n📊 Agent used: {analysis_result.get('agent_used')}")
        print(f"🔧 Data structure keys: {list(analysis_result.get('structured_data', {}).keys())}")
        
    else:
        print(f"❌ Agent analysis failed: {analysis_result.get('error')}")

def test_mvp_data_to_agent_sync():
    """Synchronous wrapper for easier testing"""
    return asyncio.run(test_mvp_data_to_agent())

if __name__ == "__main__":
    print("🚀 Testing MVP Scraper → Research Agent Integration")
    print("Following OpenAI Agents SDK best practices\n")
    
    test_mvp_data_to_agent_sync()
    
    print("\n✨ Test complete!")