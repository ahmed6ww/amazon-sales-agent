#!/usr/bin/env python3
"""
Test script for the Firecrawl-based Research Agent

This script tests the Research Agent with Firecrawl integration to ensure
all tools are working correctly and the agent provides proper analysis.
"""

import os
import sys
import asyncio
from pathlib import Path
import json
import time

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.local_agents.research import ResearchRunner

def test_firecrawl_scraping():
    """Test the Firecrawl scraping functionality directly."""
    print("🔥 Testing Firecrawl Scraping - Direct Function")
    print("=" * 60)
    
    if not os.getenv("FIRECRAWL_API_KEY"):
        print("⚠️  FIRECRAWL_API_KEY not set - skipping Firecrawl tests")
        return {"success": False, "error": "No FIRECRAWL_API_KEY"}
    
    from app.local_agents.research.agent import scrape_amazon_listing_with_firecrawl
    
    test_asin = "B08KT2Z93D"
    print(f"Testing Firecrawl scraping with ASIN: {test_asin}")
    print("This may take 10-30 seconds...")
    
    start_time = time.time()
    result = scrape_amazon_listing_with_firecrawl(test_asin)
    end_time = time.time()
    
    print(f"⏱️  Scraping took {end_time - start_time:.2f} seconds")
    
    if result["success"]:
        print("✅ Firecrawl scraping successful!")
        listing_data = result["data"]
        
        print("\n📊 EXTRACTED DATA:")
        print("-" * 40)
        print(f"Product: {listing_data.get('product_title', 'N/A')[:80]}...")
        print(f"Price: {listing_data.get('price', 'N/A')}")
        print(f"Rating: {listing_data.get('rating', 'N/A')}")
        print(f"Brand: {listing_data.get('brand', 'N/A')}")
        print(f"Review Count: {listing_data.get('review_count', 'N/A')}")
        print(f"Features Count: {len(listing_data.get('product_information_sections', {}).get('About this item', {}).get('content', []))}")
        
        # Check content quality
        content_length = listing_data.get('content_length', {})
        print(f"Content Quality: Markdown {content_length.get('markdown', 0)} chars, HTML {content_length.get('html', 0)} chars")
        
        # Show raw Firecrawl info
        raw_info = result.get("raw_firecrawl_data", {})
        print(f"Raw Firecrawl: Markdown {raw_info.get('markdown_length', 0)} chars, HTML {raw_info.get('html_length', 0)} chars")
    else:
        print("❌ Firecrawl scraping failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    return result

def test_firecrawl_extraction_pipeline():
    """Test the complete extraction pipeline with Firecrawl data."""
    print("\n\n🔧 Testing Firecrawl Extraction Pipeline")
    print("=" * 60)
    
    if not os.getenv("FIRECRAWL_API_KEY"):
        print("⚠️  FIRECRAWL_API_KEY not set - skipping pipeline tests")
        return {"success": False, "error": "No FIRECRAWL_API_KEY"}
    
    from app.local_agents.research.agent import (
        scrape_amazon_listing_with_firecrawl,
        extract_product_attributes_from_firecrawl,
        determine_market_position
    )
    
    test_asin = "B08KT2Z93D"
    
    print(f"1. Scraping with Firecrawl: {test_asin}")
    scrape_result = scrape_amazon_listing_with_firecrawl(test_asin)
    
    if not scrape_result["success"]:
        print(f"   ❌ Scraping failed: {scrape_result.get('error')}")
        return scrape_result
    
    print("   ✅ Scraping successful")
    listing_data = scrape_result["data"]
    
    print("\n2. Extracting product attributes")
    attributes = extract_product_attributes_from_firecrawl(listing_data)
    
    print("   ✅ Attribute extraction successful")
    print(f"   Brand: {attributes['basic_info']['brand']}")
    print(f"   Price Tier: {attributes['pricing']['price_tier']}")
    print(f"   Current Price: ${attributes['pricing']['current_price']}")
    print(f"   Features Count: {len(attributes['features'])}")
    print(f"   Content Quality: {attributes['content_sources']['content_quality']}")
    print(f"   Firecrawl Content Size: {attributes['content_sources']['firecrawl_content_size']} chars")
    
    print("\n3. Determining market position")
    position = determine_market_position(attributes)
    
    print("   ✅ Market positioning successful")
    print(f"   Final Tier: {position['final_tier']}")
    print(f"   Price: ${position['price']}")
    print(f"   Premium Score: {position['premium_score']}")
    print(f"   Budget Score: {position['budget_score']}")
    print(f"   Price-based: {position['positioning_factors']['price_based']}")
    print(f"   Feature-based: {position['positioning_factors']['feature_based']}")
    
    return {
        "success": True,
        "scrape_result": scrape_result,
        "attributes": attributes,
        "position": position
    }

def test_firecrawl_agent_tools():
    """Test the agent tool functions directly."""
    print("\n\n🤖 Testing Firecrawl Agent Tools")
    print("=" * 60)
    
    if not os.getenv("FIRECRAWL_API_KEY"):
        print("⚠️  FIRECRAWL_API_KEY not set - skipping agent tool tests")
        return {"success": False, "error": "No FIRECRAWL_API_KEY"}
    
    # Import the underlying functions directly instead of the decorated tools
    from app.local_agents.research.agent import (
        scrape_amazon_listing_with_firecrawl,
        extract_product_attributes_from_firecrawl,
        determine_market_position
    )
    
    test_asin = "B08KT2Z93D"
    
    print(f"1. Testing scrape_amazon_listing_with_firecrawl with: {test_asin}")
    scrape_result = scrape_amazon_listing_with_firecrawl(test_asin)
    
    if scrape_result.get("success"):
        print("   ✅ Agent scraping function successful")
        listing_data = scrape_result["data"]
        print(f"   Product: {listing_data.get('product_title', 'N/A')[:60]}...")
        
        print("\n2. Testing extract_product_attributes_from_firecrawl")
        attributes = extract_product_attributes_from_firecrawl(listing_data)
        
        print("   ✅ Agent attribute extraction successful")
        print(f"   Brand: {attributes['basic_info']['brand']}")
        print(f"   Price Tier: {attributes['pricing']['price_tier']}")
        
        print("\n3. Testing determine_market_position")
        position = determine_market_position(attributes)
        
        print("   ✅ Agent market positioning successful")
        print(f"   Final Tier: {position['final_tier']}")
        print(f"   Price: ${position['price']}")
        
        return {"success": True, "data": scrape_result}
    else:
        print(f"   ❌ Agent scraping function failed: {scrape_result.get('error')}")
        return {"success": False, "error": scrape_result.get('error')}

def test_firecrawl_agent_integration():
    """Test the full agent integration with Firecrawl."""
    print("\n\n🎯 Testing Firecrawl Agent Integration")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set - skipping agent integration tests")
        return {"success": False, "error": "No OPENAI_API_KEY"}
    
    if not os.getenv("FIRECRAWL_API_KEY"):
        print("⚠️  FIRECRAWL_API_KEY not set - skipping agent integration tests")
        return {"success": False, "error": "No FIRECRAWL_API_KEY"}
    
    runner = ResearchRunner()
    test_asin = "B08KT2Z93D"
    print(f"Testing agent with ASIN: {test_asin}")
    print("This may take 30-60 seconds for full analysis...")
    
    start_time = time.time()
    result = runner.run_listing_analysis_only(test_asin)
    end_time = time.time()
    
    print(f"⏱️  Agent analysis took {end_time - start_time:.2f} seconds")
    
    if result["success"]:
        print("✅ Firecrawl agent analysis completed successfully!")
        print("\n📋 AGENT RESULTS:")
        print("-" * 50)
        output = result["final_output"]
        # Truncate very long output
        if len(output) > 2000:
            print(f"{output[:2000]}...")
            print(f"\n[Output truncated - full length: {len(output)} characters]")
        else:
            print(output)
    else:
        print("❌ Firecrawl agent analysis failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    return result

def test_different_products():
    """Test with different types of products to validate robustness."""
    print("\n\n🛍️  Testing Different Product Types")
    print("=" * 60)
    
    if not os.getenv("FIRECRAWL_API_KEY"):
        print("⚠️  FIRECRAWL_API_KEY not set - skipping product variety tests")
        return {"success": False, "error": "No FIRECRAWL_API_KEY"}
    
    from app.local_agents.research.agent import scrape_amazon_listing_with_firecrawl
    
    # Different product types for testing
    test_products = [
        {"asin": "B08KT2Z93D", "type": "Body Lotion (Budget)"},
        {"asin": "B08N5WRWNW", "type": "Echo Dot (Electronics)"},
        {"asin": "B08LR9RYYR", "type": "Coffee Mug (Home)"}
    ]
    
    results = []
    for product in test_products:
        print(f"\nTesting {product['type']} - ASIN: {product['asin']}")
        
        result = scrape_amazon_listing_with_firecrawl(product['asin'])
        if result["success"]:
            data = result["data"]
            print(f"   ✅ Success: {data.get('product_title', 'N/A')[:50]}...")
            print(f"   Price: {data.get('price', 'N/A')}, Brand: {data.get('brand', 'N/A')}")
            results.append({"asin": product['asin'], "success": True})
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
            results.append({"asin": product['asin'], "success": False, "error": result.get('error')})
        
        # Small delay between requests
        time.sleep(2)
    
    successful = sum(1 for r in results if r.get("success"))
    print(f"\n📊 Results: {successful}/{len(test_products)} products successfully scraped")
    
    return {"success": successful > 0, "results": results}

def main():
    print("🚀 FIRECRAWL RESEARCH AGENT TEST SUITE")
    print("=" * 80)
    
    # Check environment variables
    if not os.getenv("FIRECRAWL_API_KEY"):
        print("⚠️  WARNING: FIRECRAWL_API_KEY environment variable not set")
        print("   Firecrawl tests will be skipped")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY environment variable not set")
        print("   Agent integration tests will be skipped")
    
    print()
    
    try:
        # Run tests in order
        test_firecrawl_scraping()
        test_firecrawl_extraction_pipeline()
        test_firecrawl_agent_tools()
        
        if os.getenv("OPENAI_API_KEY"):
            test_firecrawl_agent_integration()
        else:
            print("\n⏭️  Skipping agent integration tests (no OpenAI API key)")
        
        # Uncomment to test different products (takes longer)
        # test_different_products()
        
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 Firecrawl test suite completed!")

if __name__ == "__main__":
    main() 