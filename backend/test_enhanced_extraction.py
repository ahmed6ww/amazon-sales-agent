#!/usr/bin/env python3
"""
Test script for MVP Product Attribute Extraction
Tests ONLY the 5 required sources: title, images, A+ content, reviews, Q&A section.
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.local_agents.research.agent import (
    scrape_amazon_listing_with_firecrawl,
    extract_product_attributes_from_firecrawl
)

def test_mvp_extraction():
    """Test the MVP extraction functionality."""
    print("🎯 Testing MVP Product Attribute Extraction")
    print("=" * 60)
    print("Only extracting: title, images, A+ content, reviews, Q&A section")
    
    if not os.getenv("FIRECRAWL_API_KEY"):
        print("⚠️  FIRECRAWL_API_KEY not set - creating mock test")
        test_with_mock_data()
        return
    
    # Test with real ASIN
    test_asin = "B08KT2Z93D"
    print(f"\nTesting with ASIN: {test_asin}")
    
    # 1. Scrape the listing
    print("\n1. 🔥 Scraping with Firecrawl...")
    scrape_result = scrape_amazon_listing_with_firecrawl(test_asin)
    
    if not scrape_result.get("success"):
        print(f"❌ Scraping failed: {scrape_result.get('error')}")
        return
    
    listing_data = scrape_result["data"]
    
    # 2. Extract MVP attributes
    print("2. 📊 Extracting MVP attributes...")
    attributes = extract_product_attributes_from_firecrawl(listing_data)
    
    # 3. Display results
    print("\n" + "=" * 60)
    print("📋 MVP EXTRACTION RESULTS")
    print("=" * 60)
    
    # 1. Title
    title = attributes.get('title', '')
    print(f"\n📝 TITLE:")
    print(f"   {'✓' if title else '✗'} {title[:80]}..." if title else "   ✗ No title found")
    
    # 2. Images
    images = attributes.get('images', {})
    image_count = images.get('image_count', 0)
    main_image = images.get('main_image', '')
    print(f"\n📸 IMAGES:")
    print(f"   {'✓' if image_count > 0 else '✗'} {image_count} images found")
    if main_image:
        print(f"   Main: {main_image[:60]}...")
    
    # 3. A+ Content
    aplus = attributes.get('aplus_content', {})
    aplus_sections = aplus.get('sections', [])
    aplus_length = aplus.get('total_length', 0)
    print(f"\n🎨 A+ CONTENT:")
    print(f"   {'✓' if aplus_length > 0 else '✗'} {len(aplus_sections)} sections, {aplus_length} chars")
    if aplus_sections:
        print(f"   Sample: \"{aplus_sections[0][:80]}...\"")
    
    # 4. Reviews
    reviews = attributes.get('reviews', {})
    sample_reviews = reviews.get('sample_reviews', [])
    review_highlights = reviews.get('review_highlights', [])
    print(f"\n⭐ REVIEWS:")
    print(f"   {'✓' if sample_reviews else '✗'} {len(sample_reviews)} sample reviews")
    print(f"   {'✓' if review_highlights else '✗'} {len(review_highlights)} highlights")
    if sample_reviews:
        print(f"   Sample: \"{sample_reviews[0][:80]}...\"")
    
    # 5. Q&A Section
    qa = attributes.get('qa_section', {})
    qa_pairs = qa.get('qa_pairs', [])
    questions = qa.get('questions', [])
    print(f"\n❓ Q&A SECTION:")
    print(f"   {'✓' if qa_pairs or questions else '✗'} {len(qa_pairs)} Q&A pairs, {len(questions)} questions")
    if qa_pairs:
        pair = qa_pairs[0]
        print(f"   Q: {pair.get('question', '')[:60]}...")
        print(f"   A: {pair.get('answer', '')[:60]}...")
    
    # Summary
    sources_found = sum([
        bool(title),
        image_count > 0,
        aplus_length > 0,
        len(sample_reviews) > 0,
        len(qa_pairs) > 0 or len(questions) > 0
    ])
    
    print(f"\n📊 SUMMARY:")
    print(f"   MVP Sources Found: {sources_found}/5")
    print(f"   Status: {'✅ Complete' if sources_found == 5 else '⚠️ Partial' if sources_found > 2 else '❌ Insufficient'}")

def test_with_mock_data():
    """Test with mock data when API key is not available."""
    print("🧪 Testing with mock data (no API key)")
    
    # Create simplified mock data
    mock_listing_data = {
        "asin": "B08KT2Z93D",
        "title": "eos Shea Better Body Lotion Vanilla Cashmere, 24-Hour Moisture",
        "images": {
            "main_image": "https://example.com/main-image.jpg",
            "all_images": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
            "image_count": 2
        },
        "aplus_content": {
            "sections": ["Premium skincare for daily use with natural ingredients"],
            "content_blocks": [],
            "total_length": 150
        },
        "reviews": {
            "sample_reviews": ["Great product, very moisturizing", "Love the vanilla scent"],
            "review_highlights": ["quality", "moisturizing"]
        },
        "qa_section": {
            "qa_pairs": [{"question": "Is this product vegan?", "answer": "Yes, it is vegan"}],
            "questions": []
        }
    }
    
    # Test extraction
    attributes = extract_product_attributes_from_firecrawl(mock_listing_data)
    
    print(f"\n✅ Mock test completed!")
    print(f"   Title: {'✓' if attributes['title'] else '✗'}")
    print(f"   Images: {'✓' if attributes['images']['image_count'] > 0 else '✗'}")
    print(f"   A+ Content: {'✓' if attributes['aplus_content']['total_length'] > 0 else '✗'}")
    print(f"   Reviews: {'✓' if attributes['reviews']['sample_reviews'] else '✗'}")
    print(f"   Q&A: {'✓' if attributes['qa_section']['qa_pairs'] else '✗'}")

if __name__ == "__main__":
    test_mvp_extraction() 