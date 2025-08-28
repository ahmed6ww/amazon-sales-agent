#!/usr/bin/env python3
"""
Test for the MVP source extraction from traditional scraper data.
"""

import os
import sys
import json
from pathlib import Path
import unittest

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "app"))

from app.local_agents.research.agent import extract_mvp_sources_from_traditional_data

class TestMvpExtraction(unittest.TestCase):
    """Test suite for extract_mvp_sources_from_traditional_data."""

    def test_successful_extraction(self):
        """Test that all 5 MVP sources are extracted correctly from a live scrape."""
        print("🧪 Testing successful MVP extraction from live data...")
        
        from app.local_agents.research.agent import scrape_amazon_listing_with_traditional_scraper
        
        asin = "B08KT2Z93D"
        url = f"https://www.amazon.com/dp/{asin}"

        # 1. Perform live scrape
        scrape_result = scrape_amazon_listing_with_traditional_scraper(asin)
        self.assertTrue(scrape_result["success"], f"Scraping failed: {scrape_result.get('error')}")
        
        extracted_data = scrape_result["data"]
        self.assertIsNotNone(extracted_data, "Scraped data should not be None")

    # 3. Check top-level keys
        self.assertIn("asin", extracted_data)
        self.assertIn("title", extracted_data)
        self.assertIn("images", extracted_data)
        self.assertIn("aplus_content", extracted_data)
        self.assertIn("reviews", extracted_data)
        self.assertIn("qa_section", extracted_data)
        
        # 4. Title validation (check that it's not empty)
        self.assertTrue(extracted_data["title"])

        # 5. Images validation
        images = extracted_data["images"]
        self.assertTrue(images["main_image"])
        self.assertTrue(images["image_count"] > 0)

        # 6. A+ Content validation (may not always be present, so check structure)
        aplus = extracted_data["aplus_content"]
        self.assertIn("sections", aplus)
        self.assertIn("total_length", aplus)

        # 7. Reviews validation
        reviews = extracted_data["reviews"]
        self.assertIn("sample_reviews", reviews)
        self.assertIn("review_highlights", reviews)

        # 8. Q&A validation (should be empty structure as per function logic)
        qa = extracted_data["qa_section"]
        self.assertListEqual(qa["qa_pairs"], [])
        self.assertListEqual(qa["questions"], [])
        
        # 9. Display the extracted MVP data for visibility
        print("\n📦 Extracted MVP data (from extract_mvp_sources_from_traditional_data):")
        try:
            print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"[display error] {e}")
        
        print("   ✅ All MVP sources extracted and validated successfully!")

    def test_missing_data_handling(self):
        """Test that the function handles missing data gracefully."""
        print("\n🧪 Testing graceful handling of missing data...")
        
        empty_data = {}
        asin = "B08KT2Z93D"
        url = f"https://www.amazon.com/dp/{asin}"
        
        extracted_data = extract_mvp_sources_from_traditional_data(
            empty_data, asin, url
        )

        self.assertEqual(extracted_data["title"], "")
        self.assertEqual(extracted_data["images"]["image_count"], 0)
        self.assertEqual(extracted_data["aplus_content"]["total_length"], 0)
        self.assertEqual(len(extracted_data["reviews"]["sample_reviews"]), 0)
        
        # Display the (empty) extracted structure as well
        print("\n📦 Extracted MVP data for missing input:")
        try:
            print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"[display error] {e}")
        
        print("   ✅ Function handles missing data without errors.")

if __name__ == "__main__":
    unittest.main()
