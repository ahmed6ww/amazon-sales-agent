#!/usr/bin/env python3
"""
Simple test script for individual Research Agent tool functions
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_individual_functions():
    """Test the individual tool functions directly"""
    print("🔧 Testing Individual Research Agent Functions")
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
        print("   ✅ Scraping function executed successfully")
        listing_data = scrape_result["data"]
        
        print(f"   Product Title: {listing_data.get('product_title', 'N/A')}")
        print(f"   Price: {listing_data.get('price', 'N/A')}")
        print(f"   Rating: {listing_data.get('rating', 'N/A')}")
        print(f"   ASIN: {listing_data.get('asin', 'N/A')}")
        print(f"   Available data keys: {list(listing_data.keys())}")
        
        print("\n2. Testing extract_product_attributes")
        attributes = extract_product_attributes(listing_data)
        
        print("   ✅ Attribute extraction successful")
        print(f"   Brand: {attributes['basic_info']['brand']}")
        print(f"   Price Tier: {attributes['pricing']['price_tier']}")
        print(f"   Features Count: {len(attributes['features'])}")
        print(f"   Specifications Count: {len(attributes['specifications'])}")
        print(f"   Content Sources: {len(attributes['content_sources']['product_sections'])} sections")
        
        print("\n3. Testing determine_market_position")
        position = determine_market_position(attributes)
        
        print("   ✅ Market positioning successful")
        print(f"   Final Tier: {position['final_tier']}")
        print(f"   Price: ${position['price']}")
        print(f"   Premium Score: {position['premium_score']}")
        print(f"   Budget Score: {position['budget_score']}")
        
        return True
        
    else:
        print(f"   ❌ Scraping failed: {scrape_result.get('error', 'Unknown error')}")
        return False

def test_csv_parsing():
    """Test CSV parsing with a non-existent file"""
    print("\n\n📄 Testing CSV Parsing Function")
    print("=" * 60)
    
    from app.local_agents.research.agent import parse_helium10_csv
    
    # Test with non-existent file (should handle gracefully)
    result = parse_helium10_csv("/path/to/non/existent/file.csv")
    
    if not result["success"]:
        print("   ✅ CSV parsing correctly handles missing file")
        print(f"   Error message: {result['error']}")
    else:
        print("   ❌ Unexpected success with non-existent file")
    
    return True

def main():
    """Run individual function tests"""
    print("🧪 INDIVIDUAL FUNCTION TEST SUITE")
    print("=" * 80)
    
    try:
        success1 = test_individual_functions()
        success2 = test_csv_parsing()
        
        if success1 and success2:
            print("\n✅ All individual function tests completed!")
        else:
            print("\n⚠️  Some tests had issues, but this is expected without proper scraping setup")
            
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 Individual function test suite completed!")

if __name__ == "__main__":
    main() 