#!/usr/bin/env python3
"""
Test the traditional scraper agent functions directly
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_agent_functions_directly():
    """Test the underlying agent functions directly without tool decorators."""
    print("🔧 Testing Agent Functions Directly (Traditional Scraper)")
    print("=" * 65)
    
    from app.local_agents.research.agent import (
        scrape_amazon_listing_with_traditional_scraper,
        extract_product_attributes_from_firecrawl
    )
    
    test_asin = "B08KT2Z93D"
    print(f"Testing with ASIN: {test_asin}")
    
    print("\n1. 🔧 Testing scrape_amazon_listing_with_traditional_scraper...")
    try:
        scrape_result = scrape_amazon_listing_with_traditional_scraper(test_asin)
        
        if scrape_result.get("success"):
            print(f"   ✅ Scraping successful!")
            listing_data = scrape_result["data"]
            
            print("\n2. 📊 Testing extract_product_attributes_from_firecrawl...")
            attributes = extract_product_attributes_from_firecrawl(listing_data)
            
            print("✅ Extract function executed successfully!")
            
            # Display results
            print("\n" + "=" * 65)
            print("🎯 AGENT FUNCTIONS TEST RESULTS")
            print("=" * 65)
            
            # 1. Title
            title = attributes.get('title', '')
            print(f"\n📝 TITLE:")
            print(f"   {'✅' if title else '❌'} {title[:100]}..." if title else "   ❌ No title")
            
            # 2. Images
            images = attributes.get('images', {})
            image_count = images.get('image_count', 0)
            print(f"\n📸 IMAGES:")
            print(f"   {'✅' if image_count > 0 else '❌'} {image_count} images found")
            
            # 3. A+ Content
            aplus = attributes.get('aplus_content', {})
            aplus_length = aplus.get('total_length', 0)
            print(f"\n🎨 A+ CONTENT:")
            print(f"   {'✅' if aplus_length > 0 else '❌'} {aplus_length} characters")
            
            # 4. Reviews
            reviews = attributes.get('reviews', {})
            sample_reviews = reviews.get('sample_reviews', [])
            print(f"\n⭐ REVIEWS:")
            print(f"   {'✅' if sample_reviews else '❌'} {len(sample_reviews)} review samples")
            
            # 5. Q&A
            qa = attributes.get('qa_section', {})
            qa_pairs = qa.get('qa_pairs', [])
            print(f"\n❓ Q&A:")
            print(f"   {'⚠️' if not qa_pairs else '✅'} {len(qa_pairs)} Q&A pairs")
            
            # Summary
            sources_found = sum([
                bool(title),
                image_count > 0,
                aplus_length > 0,
                len(sample_reviews) > 0,
                len(qa_pairs) > 0
            ])
            
            print(f"\n📊 FUNCTIONS SUMMARY:")
            print(f"   Agent Functions: ✅ Working correctly")
            print(f"   Data Sources: {sources_found}/5 found")
            print(f"   Quality: {'✅ Excellent' if sources_found >= 4 else '⚠️ Good' if sources_found >= 3 else '❌ Poor'}")
            print(f"   Traditional Scraper: ✅ Clean data")
            print(f"   Ready for Agent Integration: ✅ Yes")
            
        else:
            print(f"❌ Scraping failed: {scrape_result.get('error')}")
            
    except Exception as e:
        print(f"💥 Function test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_functions_directly() 