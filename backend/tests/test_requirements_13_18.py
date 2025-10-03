"""
Test Requirements 13-18: URL Construction, Search Results Scraping, 
Keyword Categorization Logic

Requirements:
13. With taken URL, add keyword in following manner (s?k=)
14. Scrape and analyze product title of top 15 organic results (exclude sponsored)
15. Check if keyword shows exactly similar design/product (design-specific)
16. Check if keyword shows different designs of same product (relevant)
17. Check if keyword shows product not matching CSV products (irrelevant)
18. Check if keyword shows mix of matching/non-matching products (outlier)
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List
from app.services.amazon.search_scraper import AmazonSearchScraper, scrape_amazon_search
from app.services.amazon.keyword_categorizer import AmazonKeywordCategorizer, categorize_keywords_with_amazon_search


class TestRequirements13To18:
    """Test requirements 13-18: Search URL construction and keyword categorization"""
    
    @pytest.fixture
    def sample_csv_products(self):
        """Sample CSV products for testing"""
        return [
            {
                "asin": "B08KT2Z93D",
                "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4",
                "brand": "BREWER"
            },
            {
                "asin": "B08KT2Z94E", 
                "title": "Organic Freeze Dried Strawberry Pieces - 2 Pack",
                "brand": "OrganicBrand"
            },
            {
                "asin": "B08KT2Z95F",
                "title": "Premium Strawberry Slices - Freeze Dried",
                "brand": "PremiumBrand"
            }
        ]
    
    @pytest.fixture
    def sample_search_results(self):
        """Sample Amazon search results"""
        return [
            {
                "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4",
                "asin": "B08KT2Z93D",
                "price": "$12.99",
                "rating": "4.5",
                "is_organic": True
            },
            {
                "title": "Organic Freeze Dried Strawberry Pieces - 2 Pack", 
                "asin": "B08KT2Z94E",
                "price": "$9.99",
                "rating": "4.3",
                "is_organic": True
            },
            {
                "title": "Premium Strawberry Slices - Freeze Dried",
                "asin": "B08KT2Z95F", 
                "price": "$15.99",
                "rating": "4.7",
                "is_organic": False
            },
            {
                "title": "Different Brand Strawberry Snacks",
                "asin": "B08KT2Z96G",
                "price": "$8.99", 
                "rating": "4.1",
                "is_organic": False
            },
            {
                "title": "Banana Chips - Freeze Dried",
                "asin": "B08KT2Z97H",
                "price": "$7.99",
                "rating": "4.0",
                "is_organic": False
            }
        ]
    
    def test_requirement_13_search_url_construction(self):
        """Test requirement 13: Construct search URLs with s?k= format"""
        from app.services.amazon.country_handler import construct_amazon_search_url
        
        test_cases = [
            ("stress ball", "US", "https://www.amazon.com/s?k=stress+ball"),
            ("freeze dried strawberry", "UK", "https://www.amazon.co.uk/s?k=freeze+dried+strawberry"),
            ("organic fruit snack", "DE", "https://www.amazon.de/s?k=organic+fruit+snack"),
            ("wireless mouse", "FR", "https://www.amazon.fr/s?k=wireless+mouse"),
            ("baby changing pad", "CA", "https://www.amazon.ca/s?k=baby+changing+pad")
        ]
        
        for keyword, marketplace, expected_url in test_cases:
            url = construct_amazon_search_url(keyword, marketplace)
            assert url == expected_url, f"Expected {expected_url} for '{keyword}' in {marketplace}, got {url}"
        
        # Test URL encoding
        special_char_url = construct_amazon_search_url("stress ball & toy", "US")
        assert "stress+ball+%26+toy" in special_char_url, f"Special characters not properly encoded: {special_char_url}"
        
        print(f"✅ Requirement 13: Successfully constructed {len(test_cases)} search URLs with s?k= format")
    
    @patch('app.services.amazon.search_scraper.AmazonSearchScraper._run_search_scraper')
    def test_requirement_14_organic_results_scraping(self, mock_scraper, sample_search_results):
        """Test requirement 14: Scrape top 15 organic results (exclude sponsored)"""
        # Mock scraper response
        mock_scraper.return_value = {
            "success": True,
            "data": {
                "organic_results": sample_search_results,
                "total_organic_found": len(sample_search_results)
            }
        }
        
        # Test search scraper
        scraper = AmazonSearchScraper()
        result = scraper.scrape_search_results("freeze dried strawberry", "US", max_results=15)
        
        # Verify search was successful
        assert result["success"], f"Search failed: {result.get('error')}"
        assert result["keyword"] == "freeze dried strawberry"
        assert result["marketplace"] == "US"
        
        # Verify organic results
        results = result["results"]
        assert len(results) <= 15, f"Expected max 15 results, got {len(results)}"
        
        # Verify no sponsored results (all should have is_organic or not be marked as sponsored)
        for result_item in results:
            assert "sponsored" not in result_item.get("title", "").lower(), f"Found sponsored result: {result_item}"
        
        print(f"✅ Requirement 14: Successfully scraped {len(results)} organic results (max 15)")
    
    def test_requirement_15_design_specific_detection(self, sample_csv_products, sample_search_results):
        """Test requirement 15: Design-specific keyword detection"""
        # Mock search results with mostly matching products (design-specific)
        # Use 4 matching + 1 non-matching to get 4/5 = 80% match ratio
        # Add one more CSV product to get 4 matches
        extended_csv_products = sample_csv_products + [
            {
                "asin": "B08KT2Z96G",
                "title": "Freeze Dried Strawberry Chunks - Bulk Pack for Trail Mix and Snacking",
                "brand": "Bulk Brand",
                "category": "Food & Grocery"
            }
        ]
        
        design_specific_results = extended_csv_products + [
            {
                "title": "Completely Different Product - Banana Chips",
                "asin": "B99X2",
                "price": "$8.99",
                "rating": "4.0"
            }
        ]  # 4 out of 5 match
        
        categorizer = AmazonKeywordCategorizer(extended_csv_products, "US")
        
        # Mock the search method
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            mock_search.return_value = {
                "success": True,
                "results": design_specific_results
            }
            
            result = categorizer.categorize_keyword("freeze dried strawberry slices")
            
            # Should be categorized as design-specific
            assert result["category"] == "Design-Specific", f"Expected Design-Specific, got {result['category']}"
            assert "exactly similar" in result["reason"].lower() or "similar products" in result["reason"].lower()
            assert result["confidence"] >= 0.7, f"Expected confidence >= 0.7, got {result['confidence']}"
            
            # Should have high match ratio
            match_ratio = result["analysis_details"]["match_ratio"]
            assert match_ratio >= 0.6, f"Expected match ratio >= 0.6, got {match_ratio}"
        
        print(f"✅ Requirement 15: Successfully detected design-specific keyword with {result['confidence']:.2f} confidence")
    
    def test_requirement_16_relevant_detection(self, sample_csv_products, sample_search_results):
        """Test requirement 16: Relevant keyword detection"""
        # Mock search results with some matching products (relevant)
        # Use 3 matching + 2 non-matching to get 3/5 = 60% match ratio
        relevant_results = sample_search_results[:3] + [
            {
                "title": "Different Brand Freeze Dried Fruit Mix",
                "asin": "B99X1",
                "price": "$10.99",
                "rating": "4.2"
            },
            {
                "title": "Premium Dried Fruit Snacks",
                "asin": "B99X2", 
                "price": "$8.99",
                "rating": "4.0"
            }
        ]  # 3 out of 5 match
        
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            mock_search.return_value = {
                "success": True,
                "results": relevant_results
            }
            
            result = categorizer.categorize_keyword("freeze dried fruit")
            
            # Should be categorized as relevant
            assert result["category"] == "Relevant", f"Expected Relevant, got {result['category']}"
            assert "similar product variations" in result["reason"].lower() or "variations" in result["reason"].lower()
            assert result["confidence"] >= 0.6, f"Expected confidence >= 0.6, got {result['confidence']}"
            
            # Should have moderate match ratio
            match_ratio = result["analysis_details"]["match_ratio"]
            assert 0.4 <= match_ratio <= 0.8, f"Expected match ratio 0.4-0.8, got {match_ratio}"
        
        print(f"✅ Requirement 16: Successfully detected relevant keyword with {result['confidence']:.2f} confidence")
    
    def test_requirement_17_irrelevant_detection(self, sample_csv_products, sample_search_results):
        """Test requirement 17: Irrelevant keyword detection"""
        # Mock search results with mostly non-matching products (irrelevant)
        irrelevant_results = [
            {
                "title": "Banana Chips - Freeze Dried",
                "asin": "B08KT2Z97H",
                "price": "$7.99",
                "rating": "4.0"
            },
            {
                "title": "Apple Slices - Dehydrated", 
                "asin": "B08KT2Z98I",
                "price": "$6.99",
                "rating": "3.8"
            },
            {
                "title": "Orange Pieces - Dried",
                "asin": "B08KT2Z99J",
                "price": "$5.99",
                "rating": "3.9"
            }
        ]
        
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            mock_search.return_value = {
                "success": True,
                "results": irrelevant_results
            }
            
            result = categorizer.categorize_keyword("banana chips")
            
            # Should be categorized as irrelevant
            assert result["category"] == "Irrelevant", f"Expected Irrelevant, got {result['category']}"
            assert "different products" in result["reason"].lower() or "not matching" in result["reason"].lower()
            assert result["confidence"] >= 0.6, f"Expected confidence >= 0.6, got {result['confidence']}"
            
            # Should have low match ratio
            match_ratio = result["analysis_details"]["match_ratio"]
            assert match_ratio < 0.3, f"Expected match ratio < 0.3, got {match_ratio}"
        
        print(f"✅ Requirement 17: Successfully detected irrelevant keyword with {result['confidence']:.2f} confidence")
    
    def test_requirement_18_outlier_detection(self, sample_csv_products, sample_search_results):
        """Test requirement 18: Outlier keyword detection"""
        # Mock search results with mixed matching/non-matching products (outlier)
        outlier_results = sample_search_results[:2] + [
            {
                "title": "Different Brand Strawberry Snacks",
                "asin": "B08KT2Z96G",
                "price": "$8.99",
                "rating": "4.1"
            },
            {
                "title": "Banana Chips - Freeze Dried",
                "asin": "B08KT2Z97H", 
                "price": "$7.99",
                "rating": "4.0"
            }
        ]  # 2 out of 4 match
        
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            mock_search.return_value = {
                "success": True,
                "results": outlier_results
            }
            
            result = categorizer.categorize_keyword("fruit snacks")
            
            # Should be categorized as outlier
            assert result["category"] == "Outlier", f"Expected Outlier, got {result['category']}"
            assert "mixed product variety" in result["reason"].lower() or "mixed" in result["reason"].lower()
            assert result["confidence"] >= 0.6, f"Expected confidence >= 0.6, got {result['confidence']}"
            
            # Should have moderate match ratio
            match_ratio = result["analysis_details"]["match_ratio"]
            assert 0.2 <= match_ratio <= 0.6, f"Expected match ratio 0.2-0.6, got {match_ratio}"
        
        print(f"✅ Requirement 18: Successfully detected outlier keyword with {result['confidence']:.2f} confidence")
    
    def test_keyword_categorization_integration(self, sample_csv_products):
        """Test integration of keyword categorization requirements"""
        keywords = [
            "freeze dried strawberry slices",  # Should be design-specific
            "freeze dried fruit",              # Should be relevant  
            "banana chips",                    # Should be irrelevant
            "fruit snacks"                     # Should be outlier
        ]
        
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        # Mock search results for each keyword
        mock_results = {
            "freeze dried strawberry slices": sample_csv_products[:4],  # 4/4 match
            "freeze dried fruit": sample_csv_products[:3] + [{"title": "Different Brand Freeze Dried Fruit", "asin": "B99X1"}],  # 3/4 match
            "banana chips": [{"title": "Banana Chips", "asin": "B99"}], # 0/1 match
            "fruit snacks": sample_csv_products[:2] + [{"title": "Other", "asin": "B99"}, {"title": "Different Product", "asin": "B99X2"}]  # 2/4 match
        }
        
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            def mock_search_side_effect(keyword, marketplace, max_results):
                return {
                    "success": True,
                    "results": mock_results.get(keyword, [])
                }
            
            mock_search.side_effect = mock_search_side_effect
            
            result = categorizer.categorize_keywords_batch(keywords)
            
            # Verify batch processing
            assert result["success"], f"Batch categorization failed: {result.get('error')}"
            assert result["total_keywords"] == len(keywords)
            assert len(result["categorization_results"]) == len(keywords)
            
            # Verify categories
            categories = [result["categorization_results"][kw]["category"] for kw in keywords]
            expected_categories = ["Design-Specific", "Relevant", "Irrelevant", "Outlier"]
            
            for i, (actual, expected) in enumerate(zip(categories, expected_categories)):
                assert actual == expected, f"Keyword {i} ({keywords[i]}) expected {expected}, got {actual}"
            
            # Verify category summary
            category_summary = result["category_summary"]
            assert "Design-Specific" in category_summary
            assert "Relevant" in category_summary
            assert "Irrelevant" in category_summary
            assert "Outlier" in category_summary
        
        print(f"✅ Integration Test: Successfully categorized {len(keywords)} keywords with correct categories")
    
    def test_product_matching_logic(self, sample_csv_products):
        """Test product matching logic for categorization"""
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        # Test ASIN matching
        matching_result = {
            "title": "Different Title",
            "asin": "B08KT2Z93D"  # Matches CSV ASIN
        }
        assert categorizer._is_product_match(matching_result), "ASIN match should return True"
        
        # Test title similarity
        similar_result = {
            "title": "BREWER Bulk Freeze Dried Strawberries Slices - Different Pack",
            "asin": "B99"  # Different ASIN
        }
        assert categorizer._is_product_match(similar_result), "Title similarity should return True"
        
        # Test non-matching
        non_matching_result = {
            "title": "Completely Different Product",
            "asin": "B99"
        }
        assert not categorizer._is_product_match(non_matching_result), "Non-matching product should return False"
        
        print(f"✅ Product Matching: Successfully tested ASIN, title similarity, and non-matching logic")


