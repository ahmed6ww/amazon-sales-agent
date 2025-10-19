"""
Test Requirements 19-24: Keyword Classification Rules and Process Repetition

Requirements:
19. If keyword shows one design across results but not matching CSV (irrelevant)
20. Based on instructions in points 15-19 assign category to root word
21. Repeat process for all available roots
22. If keyword has irrelevant root then keyword is irrelevant (override rule)
23. If keyword has no irrelevant root and has design-specific root then design-specific
24. If keyword has no irrelevant/design-specific roots and has relevant root then relevant
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List
from app.services.amazon.keyword_categorizer import AmazonKeywordCategorizer
from app.local_agents.keyword.runner import KeywordRunner
from app.services.keyword_processing.root_extraction import extract_meaningful_roots


class TestRequirements19To24:
    """Test requirements 19-24: Keyword classification rules and process repetition"""
    
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
                "title": "Premium Strawberry Slices - Freeze Dried Fruit Snack for Baking and Smoothies",
                "brand": "Premium Brand"
            },
            {
                "asin": "B08KT2Z96G",
                "title": "Freeze Dried Strawberry Chunks - Bulk Pack for Trail Mix and Snacking",
                "brand": "Bulk Brand"
            },
            {
                "asin": "B08KT2Z97H",
                "title": "Strawberry Fruit Crisps - Healthy Snack Alternative to Chips",
                "brand": "Healthy Brand"
            }
        ]
    
    @pytest.fixture
    def sample_keywords_with_roots(self):
        """Sample keywords with their root words"""
        return {
            "freeze dried strawberry slices": ["freeze", "dried", "strawberry", "slices"],
            "organic strawberry pieces": ["organic", "strawberry", "pieces"],
            "bulk freeze dried fruit": ["bulk", "freeze", "dried", "fruit"],
            "strawberry powder": ["strawberry", "powder"],
            "banana chips": ["banana", "chips"],
            "apple slices": ["apple", "slices"]
        }
    
    def test_requirement_19_consistent_design_irrelevant(self, sample_csv_products):
        """Test requirement 19: Consistent design but not matching CSV = irrelevant"""
        # Mock search results with consistent but non-matching design
        consistent_results = [
            {
                "title": "BrandX Freeze Dried Strawberry Slices - Pack of 6",
                "asin": "B99X1",
                "price": "$10.99"
            },
            {
                "title": "BrandY Freeze Dried Strawberry Slices - Pack of 8", 
                "asin": "B99X2",
                "price": "$12.99"
            },
            {
                "title": "BrandZ Freeze Dried Strawberry Slices - Pack of 10",
                "asin": "B99X3",
                "price": "$14.99"
            },
            {
                "title": "BrandA Freeze Dried Strawberry Slices - Pack of 12",
                "asin": "B99X4",
                "price": "$16.99"
            },
            {
                "title": "BrandB Freeze Dried Strawberry Slices - Pack of 4",
                "asin": "B99X5",
                "price": "$8.99"
            }
        ]
        
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            mock_search.return_value = {
                "success": True,
                "results": consistent_results
            }
            
            result = categorizer.categorize_keyword("freeze dried strawberry slices")
            
            # Should be categorized as irrelevant due to consistent but different design
            assert result["category"] == "Irrelevant", f"Expected Irrelevant, got {result['category']}"
            assert "consistent but different" in result["reason"].lower() or "different product design" in result["reason"].lower()
            assert result["confidence"] >= 0.6, f"Expected confidence >= 0.6, got {result['confidence']}"
            
            # Should have 0 matches with CSV products
            match_ratio = result["analysis_details"]["match_ratio"]
            assert match_ratio == 0.0, f"Expected 0.0 match ratio, got {match_ratio}"
        
        print(f"✅ Requirement 19: Successfully detected consistent design as irrelevant with {result['confidence']:.2f} confidence")
    
    def test_requirement_20_root_word_categorization(self, sample_csv_products, sample_keywords_with_roots):
        """Test requirement 20: Assign category to root word based on search results"""
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        # Mock search results for different root words
        root_search_results = {
            "strawberry": [
                {"title": "BREWER Bulk Freeze Dried Strawberries Slices", "asin": "B08KT2Z93D"},
                {"title": "Organic Freeze Dried Strawberry Pieces", "asin": "B08KT2Z94E"},
                {"title": "Different Brand Strawberry Product", "asin": "B99"}
            ],
            "freeze": [
                {"title": "BREWER Bulk Freeze Dried Strawberries Slices", "asin": "B08KT2Z93D"},
                {"title": "Organic Freeze Dried Strawberry Pieces", "asin": "B08KT2Z94E"}
            ],
            "banana": [
                {"title": "Banana Chips - Freeze Dried", "asin": "B99"},
                {"title": "Banana Slices - Dehydrated", "asin": "B99"}
            ]
        }
        
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            def mock_search_side_effect(keyword, marketplace, max_results):
                # Return results based on root word
                for root, results in root_search_results.items():
                    if root in keyword:
                        return {"success": True, "results": results}
                return {"success": True, "results": []}
            
            mock_search.side_effect = mock_search_side_effect
            
            # Test root word categorization
            root_categories = {}
            for root in ["strawberry", "freeze", "banana"]:
                result = categorizer.categorize_keyword(root)
                root_categories[root] = result["category"]
            
            # Verify root categories
            assert root_categories["strawberry"] in ["Relevant", "Design-Specific"], f"Strawberry root should be Relevant/Design-Specific, got {root_categories['strawberry']}"
            assert root_categories["freeze"] in ["Relevant", "Design-Specific"], f"Freeze root should be Relevant/Design-Specific, got {root_categories['freeze']}"
            assert root_categories["banana"] == "Irrelevant", f"Banana root should be Irrelevant, got {root_categories['banana']}"
        
        print(f"✅ Requirement 20: Successfully categorized root words: {root_categories}")
    
    def test_requirement_21_process_repetition(self, sample_csv_products, sample_keywords_with_roots):
        """Test requirement 21: Repeat process for all available roots"""
        # Extract roots from keywords
        all_keywords = list(sample_keywords_with_roots.keys())
        roots = extract_meaningful_roots(all_keywords)
        
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        # Mock search results for all roots
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            mock_search.return_value = {
                "success": True,
                "results": [
                    {"title": "BREWER Bulk Freeze Dried Strawberries Slices", "asin": "B08KT2Z93D"},
                    {"title": "Organic Freeze Dried Strawberry Pieces", "asin": "B08KT2Z94E"}
                ]
            }
            
            # Process all roots
            root_results = {}
            for root_name in roots.keys():
                result = categorizer.categorize_keyword(root_name)
                root_results[root_name] = result["category"]
            
            # Verify all roots were processed
            assert len(root_results) == len(roots), f"Expected {len(roots)} roots processed, got {len(root_results)}"
            
            # Verify each root has a category
            for root_name, category in root_results.items():
                assert category in ["Relevant", "Design-Specific", "Irrelevant", "Outlier"], f"Invalid category for root {root_name}: {category}"
        
        print(f"✅ Requirement 21: Successfully processed {len(root_results)} roots: {root_results}")
    
    def test_requirement_22_irrelevant_root_override(self, sample_csv_products):
        """Test requirement 22: Irrelevant root overrides other categories"""
        # Mock keyword with mixed roots (relevant + irrelevant)
        keyword = "strawberry banana chips"
        roots = ["strawberry", "banana", "chips"]
        
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        # Mock search results - strawberry relevant, banana irrelevant
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            def mock_search_side_effect(keyword, marketplace, max_results):
                if "strawberry" in keyword:
                    return {
                        "success": True,
                        "results": [
                            {"title": "BREWER Bulk Freeze Dried Strawberries Slices", "asin": "B08KT2Z93D"}
                        ]
                    }
                elif "banana" in keyword:
                    return {
                        "success": True,
                        "results": [
                            {"title": "Banana Chips - Different Brand", "asin": "B99"}
                        ]
                    }
                return {"success": True, "results": []}
            
            mock_search.side_effect = mock_search_side_effect
            
            # Test individual root categorization
            strawberry_result = categorizer.categorize_keyword("strawberry")
            banana_result = categorizer.categorize_keyword("banana")
            
            # Strawberry should be relevant, banana should be irrelevant
            assert strawberry_result["category"] in ["Relevant", "Design-Specific"], f"Strawberry should be relevant, got {strawberry_result['category']}"
            assert banana_result["category"] == "Irrelevant", f"Banana should be irrelevant, got {banana_result['category']}"
            
            # Test keyword with mixed roots - should be irrelevant due to override rule
            # Use batch processing with root rules to apply requirement 22
            batch_result = categorizer.categorize_keywords_batch([keyword], apply_root_rules=True)
            mixed_result = batch_result["categorization_results"][keyword]
            assert mixed_result["category"] == "Irrelevant", f"Keyword with irrelevant root should be Irrelevant, got {mixed_result['category']}"
        
        print(f"✅ Requirement 22: Successfully applied irrelevant root override rule")
    
    def test_requirement_23_design_specific_priority(self, sample_csv_products):
        """Test requirement 23: Design-specific root takes priority over relevant"""
        # Mock keyword with design-specific and relevant roots
        keyword = "freeze dried strawberry slices"
        roots = ["freeze", "dried", "strawberry", "slices"]
        
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        # Mock search results - slices should be design-specific, others relevant
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            def mock_search_side_effect(keyword, marketplace, max_results):
                if "slices" in keyword:
                    return {
                        "success": True,
                        "results": [
                            {"title": "BREWER Bulk Freeze Dried Strawberries Slices", "asin": "B08KT2Z93D"},
                            {"title": "Organic Freeze Dried Strawberry Slices", "asin": "B08KT2Z94E"},
                            {"title": "Premium Freeze Dried Strawberry Slices", "asin": "B08KT2Z95F"},
                            {"title": "Freeze Dried Strawberry Chunks - Bulk Pack for Trail Mix and Snacking", "asin": "B08KT2Z96G"}
                        ]
                    }
                else:
                    return {
                        "success": True,
                        "results": [
                            {"title": "BREWER Bulk Freeze Dried Strawberries Slices", "asin": "B08KT2Z93D"}
                        ]
                    }
            
            mock_search.side_effect = mock_search_side_effect
            
            # Test individual root categorization
            slices_result = categorizer.categorize_keyword("slices")
            strawberry_result = categorizer.categorize_keyword("strawberry")
            
            # Slices should be design-specific, strawberry should be relevant
            assert slices_result["category"] == "Design-Specific", f"Slices should be design-specific, got {slices_result['category']}"
            assert strawberry_result["category"] in ["Relevant", "Design-Specific"], f"Strawberry should be relevant, got {strawberry_result['category']}"
            
            # Test keyword with design-specific root - should be design-specific due to priority rule
            # Use batch processing with root rules to apply requirement 23
            batch_result = categorizer.categorize_keywords_batch([keyword], apply_root_rules=True)
            keyword_result = batch_result["categorization_results"][keyword]
            assert keyword_result["category"] == "Design-Specific", f"Keyword with design-specific root should be Design-Specific, got {keyword_result['category']}"
        
        print(f"✅ Requirement 23: Successfully applied design-specific priority rule")
    
    def test_requirement_24_relevant_fallback(self, sample_csv_products):
        """Test requirement 24: Relevant root as fallback when no irrelevant/design-specific"""
        # Mock keyword with only relevant roots
        keyword = "freeze dried strawberry"
        roots = ["freeze", "dried", "strawberry"]
        
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        # Mock search results - all roots should be relevant
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            mock_search.return_value = {
                "success": True,
                "results": [
                    {"title": "BREWER Bulk Freeze Dried Strawberries Slices", "asin": "B08KT2Z93D"},
                    {"title": "Organic Freeze Dried Strawberry Pieces", "asin": "B08KT2Z94E"}
                ]
            }
            
            # Test individual root categorization
            for root in roots:
                result = categorizer.categorize_keyword(root)
                assert result["category"] in ["Relevant", "Design-Specific"], f"Root {root} should be relevant, got {result['category']}"
            
            # Test keyword with only relevant roots - should be relevant
            relevant_result = categorizer.categorize_keyword(keyword)
            assert relevant_result["category"] == "Relevant", f"Keyword with only relevant roots should be Relevant, got {relevant_result['category']}"
        
        print(f"✅ Requirement 24: Successfully applied relevant fallback rule")
    
    def test_classification_rules_integration(self, sample_csv_products):
        """Test integration of all classification rules (requirements 22-24)"""
        test_cases = [
            {
                "keyword": "strawberry banana chips",
                "expected_category": "Irrelevant",
                "reason": "Contains irrelevant root (banana)"
            },
            {
                "keyword": "freeze dried strawberry slices", 
                "expected_category": "Design-Specific",
                "reason": "Contains design-specific root (slices)"
            },
            {
                "keyword": "freeze dried strawberry",
                "expected_category": "Relevant", 
                "reason": "Only relevant roots"
            }
        ]
        
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        # Mock search results
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            def mock_search_side_effect(keyword, marketplace, max_results):
                if "banana" in keyword:
                    return {
                        "success": True,
                        "results": [{"title": "Banana Chips - Different Brand", "asin": "B99"}]
                    }
                elif "slices" in keyword:
                    return {
                        "success": True,
                        "results": [
                            {"title": "BREWER Bulk Freeze Dried Strawberries Slices", "asin": "B08KT2Z93D"},
                            {"title": "Organic Freeze Dried Strawberry Slices", "asin": "B08KT2Z94E"},
                            {"title": "Premium Freeze Dried Strawberry Slices", "asin": "B08KT2Z95F"},
                            {"title": "Freeze Dried Strawberry Chunks - Bulk Pack for Trail Mix and Snacking", "asin": "B08KT2Z96G"}
                        ]
                    }
                else:
                    return {
                        "success": True,
                        "results": [
                            {"title": "BREWER Bulk Freeze Dried Strawberries Slices", "asin": "B08KT2Z93D"}
                        ]
                    }
            
            mock_search.side_effect = mock_search_side_effect
            
            # Test each case using batch processing with root rules
            keywords = [case["keyword"] for case in test_cases]
            batch_result = categorizer.categorize_keywords_batch(keywords, apply_root_rules=True)
            
            for case in test_cases:
                result = batch_result["categorization_results"][case["keyword"]]
                assert result["category"] == case["expected_category"], f"Keyword '{case['keyword']}' expected {case['expected_category']}, got {result['category']}. Reason: {case['reason']}"
        
        print(f"✅ Classification Rules Integration: Successfully tested {len(test_cases)} classification rule scenarios")
    
    def test_keyword_runner_integration(self, sample_csv_products):
        """Test integration with KeywordRunner for search-based categorization"""
        # Mock scraped product
        scraped_product = {
            "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4",
            "elements": {
                "productTitle": {
                    "text": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4"
                }
            }
        }
        
        # Mock base relevancy scores
        base_relevancy_scores = {
            "freeze dried strawberry": 8,
            "organic freeze dried": 7,
            "strawberry slices": 6,
            "banana chips": 5
        }
        
        runner = KeywordRunner()
        
        # Mock the search-based categorization
        with patch('app.services.amazon.keyword_categorizer.categorize_keywords_with_amazon_search') as mock_categorize:
            mock_categorize.return_value = {
                "success": True,
                "categorization_results": {
                    "freeze dried strawberry": {"category": "Relevant", "confidence": 0.8, "reason": "Matches product"},
                    "organic freeze dried": {"category": "Relevant", "confidence": 0.7, "reason": "Matches product"},
                    "strawberry slices": {"category": "Design-Specific", "confidence": 0.9, "reason": "Product variation"},
                    "banana chips": {"category": "Irrelevant", "confidence": 0.8, "reason": "Different product"}
                }
            }
            
            # Test keyword categorization with CSV products
            result = runner.run_keyword_categorization(
                scraped_product=scraped_product,
                base_relevancy_scores=base_relevancy_scores,
                marketplace="US",
                csv_products=sample_csv_products
            )
            
            # Verify search-based categorization was called
            mock_categorize.assert_called_once()
            
            # Verify result structure
            assert "success" in result
            assert "structured_data" in result
            
            print(f"✅ KeywordRunner Integration: Successfully integrated search-based categorization")
    
    def test_complete_workflow(self, sample_csv_products):
        """Test complete workflow from CSV processing to final categorization"""
        # This test simulates the complete workflow
        keywords = [
            "freeze dried strawberry slices",  # Should be design-specific
            "organic freeze dried fruit",      # Should be relevant
            "banana chips",                    # Should be irrelevant
            "strawberry banana mix"            # Should be irrelevant (banana override)
        ]
        
        categorizer = AmazonKeywordCategorizer(sample_csv_products, "US")
        
        # Mock comprehensive search results
        with patch.object(categorizer.search_scraper, 'scrape_search_results') as mock_search:
            def mock_search_side_effect(keyword, marketplace, max_results):
                if "slices" in keyword:
                    return {
                        "success": True,
                        "results": [
                            {"title": "BREWER Bulk Freeze Dried Strawberries Slices", "asin": "B08KT2Z93D"},
                            {"title": "Organic Freeze Dried Strawberry Slices", "asin": "B08KT2Z94E"},
                            {"title": "Premium Freeze Dried Strawberry Slices", "asin": "B08KT2Z95F"},
                            {"title": "Freeze Dried Strawberry Chunks - Bulk Pack for Trail Mix and Snacking", "asin": "B08KT2Z96G"}
                        ]
                    }
                elif "banana" in keyword:
                    return {
                        "success": True,
                        "results": [{"title": "Banana Chips - Different Brand", "asin": "B99"}]
                    }
                else:
                    return {
                        "success": True,
                        "results": [
                            {"title": "BREWER Bulk Freeze Dried Strawberries Slices", "asin": "B08KT2Z93D"}
                        ]
                    }
            
            mock_search.side_effect = mock_search_side_effect
            
            # Process all keywords
            results = categorizer.categorize_keywords_batch(keywords, apply_root_rules=True)
            
            # Verify batch processing
            assert results["success"]
            assert results["total_keywords"] == len(keywords)
            
            # Verify categories
            categories = [results["categorization_results"][kw]["category"] for kw in keywords]
            expected_categories = ["Design-Specific", "Relevant", "Irrelevant", "Irrelevant"]
            
            for i, (actual, expected) in enumerate(zip(categories, expected_categories)):
                assert actual == expected, f"Keyword {i} ({keywords[i]}) expected {expected}, got {actual}"
            
            # Verify category summary
            category_summary = results["category_summary"]
            assert category_summary["Design-Specific"] == 1
            assert category_summary["Relevant"] == 1
            assert category_summary["Irrelevant"] == 2
        
        print(f"✅ Complete Workflow: Successfully processed {len(keywords)} keywords through complete categorization workflow")
