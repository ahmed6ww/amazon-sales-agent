"""
Test Requirements 7-12: ASIN Search, Title Scraping, Keyword Search, 
Country Code Handling, URL Construction

Requirements:
7. Search ASINs on Amazon individually
8. Scrape title of first organic search result
9. Search keyword against every root on Amazon platform
10. Amazon URLs are different for different countries
11. Pick up country code from customer URL input
12. Use portion of URL only till country code
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List
from app.local_agents.research.helper_methods import scrape_amazon_listing, scrape_competitors
from app.services.amazon.country_handler import (
    extract_country_code_from_url, get_amazon_domain_for_marketplace,
    construct_amazon_url, construct_amazon_search_url, extract_base_url_from_input,
    get_marketplace_from_url, validate_marketplace, get_supported_marketplaces
)
from app.services.amazon.search_scraper import AmazonSearchScraper


class TestRequirements7To12:
    """Test requirements 7-12: Amazon search and country handling"""
    
    @pytest.fixture
    def sample_asins(self):
        """Sample ASINs for testing"""
        return ["B08KT2Z93D", "B08KT2Z94E", "B08KT2Z95F"]
    
    @pytest.fixture
    def sample_scraped_data(self):
        """Sample scraped Amazon data"""
        return {
            "success": True,
            "data": {
                "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4",
                "url": "https://www.amazon.com/dp/B08KT2Z93D",
                "elements": {
                    "productTitle": {
                        "text": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4"
                    }
                }
            }
        }
    
    @patch('app.local_agents.research.helper_methods.subprocess.run')
    def test_requirement_7_asin_search(self, mock_subprocess, sample_asins, sample_scraped_data):
        """Test requirement 7: Search ASINs on Amazon individually"""
        # Mock subprocess response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"success": true, "data": {"title": "Test Product"}}'
        mock_subprocess.return_value = mock_result
        
        # Test ASIN search
        asin = sample_asins[0]
        result = scrape_amazon_listing(asin, marketplace="US")
        
        # Verify subprocess was called with correct URL
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert asin in ' '.join(call_args), f"ASIN {asin} not found in subprocess call"
        
        # Verify URL construction
        expected_url = f"https://www.amazon.com/dp/{asin}"
        assert expected_url in ' '.join(call_args), f"Expected URL {expected_url} not found in call"
        
        print(f"✅ Requirement 7: Successfully searched ASIN {asin} on Amazon")
    
    @patch('app.local_agents.research.helper_methods.subprocess.run')
    def test_requirement_8_title_scraping(self, mock_subprocess, sample_scraped_data):
        """Test requirement 8: Scrape title of first organic search result"""
        # Mock subprocess response with title data
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"success": true, "data": {"title": "Test Product Title", "elements": {"productTitle": {"text": "Test Product Title"}}}}'
        mock_subprocess.return_value = mock_result
        
        # Test title scraping
        result = scrape_amazon_listing("B08KT2Z93D", marketplace="US")
        
        # Verify title was extracted
        assert result["success"], f"Scraping failed: {result.get('error')}"
        assert "title" in result["data"], "Title not found in scraped data"
        
        title = result["data"]["title"]
        assert title == "Test Product Title", f"Expected 'Test Product Title', got '{title}'"
        
        print(f"✅ Requirement 8: Successfully scraped title: {title}")
    
    @patch('app.services.amazon.search_scraper.AmazonSearchScraper.scrape_search_results')
    def test_requirement_9_keyword_search(self, mock_search, sample_asins):
        """Test requirement 9: Search keyword against every root on Amazon platform"""
        # Mock search results
        mock_search.return_value = {
            "success": True,
            "keyword": "freeze dried strawberry",
            "marketplace": "US",
            "search_url": "https://www.amazon.com/s?k=freeze+dried+strawberry",
            "total_results": 15,
            "results": [
                {"title": "Freeze Dried Strawberry Product 1", "asin": "B08KT2Z93D"},
                {"title": "Freeze Dried Strawberry Product 2", "asin": "B08KT2Z94E"}
            ]
        }
        
        # Test keyword search
        scraper = AmazonSearchScraper()
        roots = ["strawberry", "freeze", "dried"]
        
        result = scraper.search_keyword_against_roots("freeze dried strawberry", roots, "US")
        
        # Verify search was performed for each root
        assert result["success"], f"Keyword search failed: {result.get('error')}"
        assert result["total_roots_searched"] == len(roots), f"Expected {len(roots)} roots searched, got {result['total_roots_searched']}"
        
        # Verify each root was searched
        for root in roots:
            assert root in result["root_results"], f"Root '{root}' not found in search results"
            root_result = result["root_results"][root]
            assert root_result["success"], f"Search failed for root '{root}'"
        
        print(f"✅ Requirement 9: Successfully searched keyword against {len(roots)} roots")
    
    def test_requirement_10_country_urls(self):
        """Test requirement 10: Amazon URLs are different for different countries"""
        # Test different country domains
        test_cases = [
            ("US", "amazon.com"),
            ("UK", "amazon.co.uk"),
            ("DE", "amazon.de"),
            ("FR", "amazon.fr"),
            ("CA", "amazon.ca"),
            ("AE", "amazon.ae"),
            ("IN", "amazon.in"),
            ("IT", "amazon.it"),
            ("ES", "amazon.es"),
            ("NL", "amazon.nl"),
            ("JP", "amazon.jp")
        ]
        
        for marketplace, expected_domain in test_cases:
            domain = get_amazon_domain_for_marketplace(marketplace)
            assert domain == expected_domain, f"Expected {expected_domain} for {marketplace}, got {domain}"
        
        # Test unsupported marketplace (should default to .com)
        default_domain = get_amazon_domain_for_marketplace("UNKNOWN")
        assert default_domain == "amazon.com", f"Expected amazon.com for unknown marketplace, got {default_domain}"
        
        print(f"✅ Requirement 10: Successfully handled {len(test_cases)} country domains")
    
    def test_requirement_11_country_code_extraction(self):
        """Test requirement 11: Pick up country code from customer URL input"""
        test_cases = [
            ("https://www.amazon.com/dp/B08KT2Z93D", "US"),
            ("https://www.amazon.co.uk/dp/B08KT2Z93D", "UK"),
            ("https://www.amazon.de/dp/B08KT2Z93D", "DE"),
            ("https://www.amazon.fr/dp/B08KT2Z93D", "FR"),
            ("https://www.amazon.ca/dp/B08KT2Z93D", "CA"),
            ("https://www.amazon.ae/dp/B08KT2Z93D", "AE"),
            ("https://www.amazon.in/dp/B08KT2Z93D", "IN"),
            ("https://www.amazon.it/dp/B08KT2Z93D", "IT"),
            ("https://www.amazon.es/dp/B08KT2Z93D", "ES"),
            ("https://www.amazon.nl/dp/B08KT2Z93D", "NL"),
            ("https://www.amazon.jp/dp/B08KT2Z93D", "JP")
        ]
        
        for url, expected_country in test_cases:
            country = extract_country_code_from_url(url)
            assert country == expected_country, f"Expected {expected_country} for {url}, got {country}"
        
        # Test invalid URL
        invalid_country = extract_country_code_from_url("https://www.google.com")
        assert invalid_country is None, f"Expected None for invalid URL, got {invalid_country}"
        
        print(f"✅ Requirement 11: Successfully extracted country codes from {len(test_cases)} URLs")
    
    def test_requirement_12_base_url_extraction(self):
        """Test requirement 12: Use portion of URL only till country code"""
        test_cases = [
            ("https://www.amazon.com/dp/B08KT2Z93D/ref=sr_1_1?crid=329728", "https://www.amazon.com"),
            ("https://www.amazon.co.uk/dp/B08KT2Z93D/ref=sr_1_1?crid=329728", "https://www.amazon.co.uk"),
            ("https://www.amazon.de/dp/B08KT2Z93D/ref=sr_1_1?crid=329728", "https://www.amazon.de"),
            ("https://www.amazon.fr/dp/B08KT2Z93D/ref=sr_1_1?crid=329728", "https://www.amazon.fr"),
            ("https://www.amazon.ca/dp/B08KT2Z93D/ref=sr_1_1?crid=329728", "https://www.amazon.ca")
        ]
        
        for input_url, expected_base in test_cases:
            base_url = extract_base_url_from_input(input_url)
            assert base_url == expected_base, f"Expected {expected_base} for {input_url}, got {base_url}"
        
        # Test URL without www
        base_url = extract_base_url_from_input("https://amazon.com/dp/B08KT2Z93D")
        assert base_url == "https://www.amazon.com", f"Expected https://www.amazon.com, got {base_url}"
        
        print(f"✅ Requirement 12: Successfully extracted base URLs from {len(test_cases)} URLs")
    
    def test_url_construction(self):
        """Test URL construction with country codes"""
        # Test product URL construction
        asin = "B08KT2Z93D"
        test_cases = [
            ("US", f"https://www.amazon.com/dp/{asin}"),
            ("UK", f"https://www.amazon.co.uk/dp/{asin}"),
            ("DE", f"https://www.amazon.de/dp/{asin}")
        ]
        
        for marketplace, expected_url in test_cases:
            url = construct_amazon_url(asin, marketplace)
            assert url == expected_url, f"Expected {expected_url} for {marketplace}, got {url}"
        
        # Test search URL construction
        keyword = "stress ball"
        search_test_cases = [
            ("US", "https://www.amazon.com/s?k=stress+ball"),
            ("UK", "https://www.amazon.co.uk/s?k=stress+ball"),
            ("DE", "https://www.amazon.de/s?k=stress+ball")
        ]
        
        for marketplace, expected_url in search_test_cases:
            url = construct_amazon_search_url(keyword, marketplace)
            assert url == expected_url, f"Expected {expected_url} for {marketplace}, got {url}"
        
        print(f"✅ URL Construction: Successfully constructed {len(test_cases)} product URLs and {len(search_test_cases)} search URLs")
    
    def test_marketplace_validation(self):
        """Test marketplace validation and supported marketplaces"""
        # Test valid marketplaces
        valid_marketplaces = ["US", "UK", "DE", "FR", "CA", "AE", "IN", "IT", "ES", "NL", "JP"]
        for marketplace in valid_marketplaces:
            assert validate_marketplace(marketplace), f"Marketplace {marketplace} should be valid"
        
        # Test invalid marketplaces
        invalid_marketplaces = ["XX", "UNKNOWN", "", "123"]
        for marketplace in invalid_marketplaces:
            assert not validate_marketplace(marketplace), f"Marketplace {marketplace} should be invalid"
        
        # Test case insensitive validation
        assert validate_marketplace("us"), "Lowercase marketplace should be valid"
        assert validate_marketplace("Uk"), "Mixed case marketplace should be valid"
        
        # Test supported marketplaces list
        supported = get_supported_marketplaces()
        assert len(supported) > 10, f"Expected more than 10 supported marketplaces, got {len(supported)}"
        assert "US" in supported, "US marketplace should be supported"
        assert "UK" in supported, "UK marketplace should be supported"
        
        print(f"✅ Marketplace Validation: Successfully validated {len(valid_marketplaces)} marketplaces")
    
    def test_marketplace_from_url(self):
        """Test extracting marketplace from URL"""
        test_cases = [
            ("https://www.amazon.com/dp/B08KT2Z93D", "US"),
            ("https://www.amazon.co.uk/dp/B08KT2Z93D", "UK"),
            ("https://www.amazon.de/dp/B08KT2Z93D", "DE"),
            ("https://www.amazon.fr/dp/B08KT2Z93D", "FR"),
            ("https://www.amazon.ca/dp/B08KT2Z93D", "CA")
        ]
        
        for url, expected_marketplace in test_cases:
            marketplace = get_marketplace_from_url(url)
            assert marketplace == expected_marketplace, f"Expected {expected_marketplace} for {url}, got {marketplace}"
        
        # Test invalid URL (should default to US)
        default_marketplace = get_marketplace_from_url("https://www.google.com")
        assert default_marketplace == "US", f"Expected US for invalid URL, got {default_marketplace}"
        
        print(f"✅ Marketplace from URL: Successfully extracted marketplace from {len(test_cases)} URLs")


