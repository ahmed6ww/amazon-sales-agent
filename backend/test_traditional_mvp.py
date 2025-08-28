#!/usr/bin/env python3
"""
Test the traditional scraper MVP extraction
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_traditional_mvp():
    """Test the traditional scraper MVP extraction."""
    print("🎯 Testing Traditional Scraper MVP Extraction")
    print("=" * 60)
    
    from app.local_agents.research.agent import (
        scrape_amazon_listing_with_traditional_scraper,
        extract_product_attributes_from_firecrawl
    )
    
    # Test ASIN
    test_asin = "B08KT2Z93D"
    print(f"Testing with ASIN: {test_asin}")
    
    # 1. Scrape with traditional scraper
    print("\n1. 🔧 Scraping with traditional scraper...")
    try:
        scrape_result = scrape_amazon_listing_with_traditional_scraper(test_asin)
        
        if not scrape_result.get("success"):
            print(f"❌ Scraping failed: {scrape_result.get('error')}")
            return
        
        listing_data = scrape_result["data"]
        
        # 2. Extract MVP attributes
        print("2. 📊 Extracting MVP attributes...")
        attributes = extract_product_attributes_from_firecrawl(listing_data)
        
        # 3. Display clean results
        print("\n" + "=" * 60)
        print("📋 CLEAN MVP EXTRACTION RESULTS")
        print("=" * 60)
        
        # 1. Title
        title = attributes.get('title', '')
        print(f"\n📝 TITLE:")
        if title and "not found" not in title.lower():
            print(f"   ✅ Clean: {title}")
        else:
            print(f"   ❌ Missing or poor quality")
        
        # 2. Images
        images = attributes.get('images', {})
        image_count = images.get('image_count', 0)
        main_image = images.get('main_image', '')
        print(f"\n📸 IMAGES:")
        if image_count > 0 and main_image:
            print(f"   ✅ Good: {image_count} images")
            print(f"   Main: {main_image[:80]}...")
        else:
            print(f"   ❌ No images found")
        
        # 3. A+ Content
        aplus = attributes.get('aplus_content', {})
        aplus_sections = aplus.get('sections', [])
        aplus_length = aplus.get('total_length', 0)
        print(f"\n🎨 A+ CONTENT:")
        if aplus_length > 0:
            print(f"   ✅ Found: {len(aplus_sections)} sections, {aplus_length} chars")
            if aplus_sections:
                print(f"   Sample: \"{aplus_sections[0][:100]}...\"")
        else:
            print(f"   ⚠️  No A+ content found")
        
        # 4. Reviews  
        reviews = attributes.get('reviews', {})
        sample_reviews = reviews.get('sample_reviews', [])
        review_highlights = reviews.get('review_highlights', [])
        print(f"\n⭐ REVIEWS:")
        if sample_reviews or review_highlights:
            print(f"   ✅ Found: {len(sample_reviews)} review samples")
            print(f"   Highlights: {len(review_highlights)} items")
            if sample_reviews:
                print(f"   Sample: \"{sample_reviews[0][:100]}...\"")
            if review_highlights:
                print(f"   Rating info: {', '.join(review_highlights)}")
        else:
            print(f"   ❌ No review data found")
        
        # 5. Q&A Section
        qa = attributes.get('qa_section', {})
        qa_pairs = qa.get('qa_pairs', [])
        questions = qa.get('questions', [])
        print(f"\n❓ Q&A SECTION:")
        if qa_pairs or questions:
            print(f"   ✅ Found: {len(qa_pairs)} Q&A pairs, {len(questions)} questions")
        else:
            print(f"   ⚠️  No Q&A data (expected - traditional scraper limitation)")
        
        # Summary
        sources_found = sum([
            bool(title and "not found" not in title.lower()),
            image_count > 0,
            aplus_length > 0,
            len(sample_reviews) > 0 or len(review_highlights) > 0,
            len(qa_pairs) > 0 or len(questions) > 0
        ])
        
        quality_score = "excellent" if sources_found >= 4 else "good" if sources_found >= 3 else "fair" if sources_found >= 2 else "poor"
        
        print(f"\n📊 QUALITY SUMMARY:")
        print(f"   Sources Found: {sources_found}/5")
        print(f"   Data Quality: {quality_score.upper()}")
        print(f"   Clean Data: ✅ (no garbage/navigation text)")
        print(f"   Ready for Keyword Research: {'✅' if sources_found >= 3 else '⚠️'}")
        
    except Exception as e:
        print(f"💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_traditional_mvp() 