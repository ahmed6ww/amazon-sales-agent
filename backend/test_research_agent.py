#!/usr/bin/env python3
"""
Test script for the Research Agent

This script tests the Research Agent with a real Amazon product to ensure
all tools are working correctly and the agent provides proper analysis.
"""

import os
import sys
import asyncio
from pathlib import Path
import json
import subprocess

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.local_agents.research import ResearchRunner

def run_fresh(cmd: list[str]) -> str:
    """Run a python snippet in a fresh subprocess and return stdout."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent)
    result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return result.stdout

def test_basic_listing_analysis():
    print("🧪 Testing Research Agent - Basic Listing Analysis")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⏭️  Skipping basic listing analysis (no OPENAI_API_KEY)")
        return {"success": False, "error": "No OPENAI_API_KEY"}
    
    runner = ResearchRunner()
    test_asin = "B08KT2Z93D"
    print(f"Analyzing product: {test_asin}")
    print("Running analysis...")
    result = runner.run_listing_analysis_only(test_asin)
    
    if result["success"]:
        print("✅ Analysis completed successfully!")
        print("\n📊 RESULTS:")
        print("-" * 40)
        print(result["final_output"])
    else:
        print("❌ Analysis failed!")
        print(f"Error: {result['error']}")
    
    return result

def test_full_research_workflow():
    print("\n\n🔬 Testing Research Agent - Full Workflow")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⏭️  Skipping full workflow (no OPENAI_API_KEY)")
        return {"success": False, "error": "No OPENAI_API_KEY"}
    
    runner = ResearchRunner()
    test_url = "https://www.amazon.com/dp/B08KT2Z93D"
    print(f"Running full research workflow for: {test_url}")
    result = runner.run_research(
        asin_or_url=test_url,
        marketplace="US",
        main_keyword="wireless charging pad"
    )
    
    if result["success"]:
        print("✅ Full research completed successfully!")
        print("\n📋 COMPREHENSIVE RESULTS:")
        print("-" * 50)
        print(result["final_output"])
    else:
        print("❌ Full research failed!")
        print(f"Error: {result['error']}")
    
    return result

def test_tool_functions_directly():
    print("\n\n🔧 Testing Individual Tool Functions")
    print("=" * 60)
    
    from app.local_agents.research.agent import (
        scrape_amazon_listing,
        extract_product_attributes,
        determine_market_position
    )
    
    test_asin = "B08KT2Z93D"
    
    print(f"1. Testing scrape_amazon_listing with ASIN: {test_asin}")
    scrape_result = scrape_amazon_listing(test_asin)
    
    if scrape_result["success"]:
        print("   ✅ Scraping successful")
        listing_data = scrape_result["data"]
        
        print(f"   Product: {listing_data.get('product_title', 'N/A')}")
        print(f"   Price: ${listing_data.get('price', 'N/A')}")
        print(f"   Rating: {listing_data.get('rating', 'N/A')}")
        
        print("\n2. Testing extract_product_attributes")
        attributes = extract_product_attributes(listing_data)
        
        print("   ✅ Attribute extraction successful")
        print(f"   Brand: {attributes['basic_info']['brand']}")
        print(f"   Price Tier: {attributes['pricing']['price_tier']}")
        print(f"   Features Count: {len(attributes['features'])}")
        print(f"   Content Sources: {len(attributes['content_sources']['product_sections'])} sections")
        
        print("\n3. Testing determine_market_position")
        position = determine_market_position(attributes)
        
        print("   ✅ Market positioning successful")
        print(f"   Final Tier: {position['final_tier']}")
        print(f"   Price: ${position['price']}")
        print(f"   Premium Score: {position['premium_score']}")
        print(f"   Budget Score: {position['budget_score']}")
        
        # Compare against agent tool in a fresh process (avoid reactor restart)
        print("\n🔁 Comparing with agent tool (fresh process)")
        code = (
            "import sys, json; sys.path.insert(0,'app'); "
            "from app.local_agents.research.agent import tool_scrape_amazon_listing; "
            "print(tool_scrape_amazon_listing('" + test_asin + "'))"
        )
        out = run_fresh(["python", "-c", code])
        try:
            agent_tool_json = json.loads(out.strip().splitlines()[-1])
        except Exception:
            agent_tool_json = {"success": False, "error": out}
        
        if agent_tool_json.get("success"):
            agent_title = agent_tool_json["data"].get("product_title")
            print(f"   Agent tool title: {agent_title}")
        else:
            print("   Agent tool scrape failed in fresh process")
            print(agent_tool_json.get("error", "unknown error"))
    else:
        print(f"   ❌ Scraping failed: {scrape_result.get('error', 'Unknown error')}")

def main():
    print("🚀 RESEARCH AGENT TEST SUITE")
    print("=" * 80)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY environment variable not set")
        print("   Agent functionality will be limited without API access")
        print()
    
    try:
        test_tool_functions_directly()
        
        if os.getenv("OPENAI_API_KEY"):
            test_basic_listing_analysis()
            test_full_research_workflow()
        else:
            print("\n⏭️  Skipping agent tests (no OpenAI API key)")
            
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 Test suite completed!")

if __name__ == "__main__":
    main() 