#!/usr/bin/env python3
"""
Test the integrated MVP agent workflow
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_mvp_agent_integration():
    """Test the MVP agent integration with mock data."""
    print("🤖 Testing MVP Agent Integration")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set - skipping agent integration")
        test_direct_functions()
        return
    
    from app.local_agents.research import ResearchRunner
    
    runner = ResearchRunner()
    test_asin = "B08KT2Z93D"
    
    print(f"Testing agent with ASIN: {test_asin}")
    print("Agent will extract 5 MVP sources...")
    
    try:
        result = runner.run_listing_analysis_only(test_asin)
        
        if result["success"]:
            print("✅ Agent analysis completed successfully!")
            print("\n📋 AGENT OUTPUT:")
            print("-" * 50)
            output = result["final_output"]
            # Show first 1000 chars to avoid overwhelming output
            if len(output) > 1000:
                print(f"{output[:1000]}...")
                print(f"\n[Output truncated - full length: {len(output)} characters]")
            else:
                print(output)
        else:
            print("❌ Agent analysis failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"💥 Agent test failed with error: {e}")

def test_direct_functions():
    """Test the MVP functions directly without agent."""
    print("🧪 Testing MVP functions directly (no OpenAI API key)")
    
    from app.local_agents.research.agent import (
        extract_product_info_from_firecrawl,
        extract_product_attributes_from_firecrawl
    )
    
    # Mock firecrawl data
    mock_firecrawl_data = {
        "markdown": """
        # eos Shea Better Body Lotion Vanilla Cashmere
        
        ## About this item
        • 24-hour moisturizing body lotion
        • Natural shea butter formula
        • Lightweight and non-greasy
        
        ## From the brand
        Premium skincare with natural ingredients for daily use.
        
        ## Customer reviews
        Great product, very moisturizing. Love the vanilla scent.
        
        ## Questions and answers
        Q: Is this product vegan?
        A: Yes, this product is vegan and cruelty-free.
        """,
        "html": """
        <img src="https://example.com/main-product.jpg" alt="Product image">
        <img src="https://example.com/gallery1.jpg" alt="Gallery image 1">
        """
    }
    
    # Test extraction
    print("\n1. Testing extract_product_info_from_firecrawl...")
    listing_data = extract_product_info_from_firecrawl(mock_firecrawl_data, "B08KT2Z93D", "https://amazon.com/dp/B08KT2Z93D")
    
    print(f"   Title: {'✓' if listing_data['title'] else '✗'}")
    print(f"   Images: {'✓' if listing_data['images']['image_count'] > 0 else '✗'} ({listing_data['images']['image_count']} found)")
    print(f"   A+ Content: {'✓' if listing_data['aplus_content']['total_length'] > 0 else '✗'} ({listing_data['aplus_content']['total_length']} chars)")
    print(f"   Reviews: {'✓' if listing_data['reviews']['sample_reviews'] else '✗'} ({len(listing_data['reviews']['sample_reviews'])} samples)")
    print(f"   Q&A: {'✓' if listing_data['qa_section']['qa_pairs'] else '✗'} ({len(listing_data['qa_section']['qa_pairs'])} pairs)")
    
    print("\n2. Testing extract_product_attributes_from_firecrawl...")
    attributes = extract_product_attributes_from_firecrawl(listing_data)
    
    print("   MVP Attributes extracted:")
    print(f"   - Title: {attributes['title'][:50]}..." if attributes['title'] else "   - Title: ✗")
    print(f"   - Images: {attributes['images']['image_count']} images")
    print(f"   - A+ Content: {len(attributes['aplus_content']['sections'])} sections")
    print(f"   - Reviews: {len(attributes['reviews']['sample_reviews'])} samples")
    print(f"   - Q&A: {len(attributes['qa_section']['qa_pairs'])} pairs")
    
    print("\n✅ Direct function test completed!")

if __name__ == "__main__":
    test_mvp_agent_integration() 