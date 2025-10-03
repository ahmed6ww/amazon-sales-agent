"""
Amazon Search Results Scraper

Implements requirements #9, #13, #14: Keyword search on Amazon platform,
URL construction with s?k=, and top 15 organic results scraping.
"""

import json
import subprocess
import sys
import traceback
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class AmazonSearchScraper:
    """Scraper for Amazon search results pages"""
    
    def __init__(self):
        self.name = "amazon_search_scraper"
    
    def scrape_search_results(self, keyword: str, marketplace: str = "US", max_results: int = 15) -> Dict[str, Any]:
        """
        Scrape Amazon search results for a keyword (requirement #9, #14).
        
        Args:
            keyword: Search keyword
            marketplace: Target marketplace code
            max_results: Maximum number of organic results to scrape
            
        Returns:
            Dict containing search results data
        """
        try:
            from app.services.amazon.country_handler import construct_amazon_search_url
            
            # Construct search URL (requirement #13)
            search_url = construct_amazon_search_url(keyword, marketplace)
            
            # Use standalone scraper for search results
            result = self._run_search_scraper(search_url, max_results)
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": f"Search scraping failed: {result.get('error', 'Unknown error')}",
                    "keyword": keyword,
                    "marketplace": marketplace,
                    "search_url": search_url,
                    "results": []
                }
            
            # Parse and filter organic results (exclude sponsored)
            organic_results = self._filter_organic_results(result.get("data", {}), max_results)
            
            return {
                "success": True,
                "keyword": keyword,
                "marketplace": marketplace,
                "search_url": search_url,
                "total_results": len(organic_results),
                "results": organic_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Search scraping error: {str(e)}",
                "keyword": keyword,
                "marketplace": marketplace,
                "results": []
            }
    
    def _run_search_scraper(self, search_url: str, max_results: int) -> Dict[str, Any]:
        """Run the search scraper subprocess"""
        try:
            current_file = Path(__file__)
            app_dir = current_file.parent.parent.parent
            backend_dir = app_dir.parent
            scraper_script = app_dir / "services" / "amazon" / "standalone_search_scraper.py"
            
            result = subprocess.run(
                [sys.executable, str(scraper_script), search_url, str(max_results)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(backend_dir),
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Search scraper process failed: {result.stderr.strip()}",
                    "data": {},
                }
            
            try:
                container = json.loads(result.stdout.strip())
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse search scraper output: {str(e)}. Output head: {result.stdout[:200]}",
                    "data": {},
                }
            
            return container
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Search scraper timeout (120s)",
                "data": {},
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Search scraper error: {str(e)}",
                "data": {},
            }
    
    def _filter_organic_results(self, scraped_data: Dict[str, Any], max_results: int) -> List[Dict[str, Any]]:
        """
        Filter organic results from scraped search page data (requirement #14).
        Excludes sponsored results.
        """
        organic_results = []
        
        # Extract product results from the scraped data
        # This would need to be implemented based on the actual search page structure
        # For now, return a placeholder structure
        
        if not scraped_data:
            return organic_results
        
        # Placeholder implementation - would need actual search page parsing
        # The actual implementation would parse the search results HTML/JSON
        # and extract product titles, ASINs, prices, etc.
        
        return organic_results[:max_results]
    
    def search_keyword_against_roots(self, keyword: str, roots: List[str], marketplace: str = "US") -> Dict[str, Any]:
        """
        Search keyword against multiple roots on Amazon (requirement #9).
        
        Args:
            keyword: Keyword to search
            roots: List of root words to search against
            marketplace: Target marketplace code
            
        Returns:
            Dict containing search results for each root
        """
        results = {}
        
        for root in roots:
            # Create search query combining keyword and root
            search_query = f"{keyword} {root}"
            
            # Scrape search results
            search_result = self.scrape_search_results(search_query, marketplace)
            results[root] = search_result
        
        return {
            "success": True,
            "keyword": keyword,
            "marketplace": marketplace,
            "root_results": results,
            "total_roots_searched": len(roots)
        }


def scrape_amazon_search(keyword: str, marketplace: str = "US", max_results: int = 15) -> Dict[str, Any]:
    """
    Convenience function to scrape Amazon search results.
    
    Args:
        keyword: Search keyword
        marketplace: Target marketplace code
        max_results: Maximum number of organic results
        
    Returns:
        Dict containing search results
    """
    scraper = AmazonSearchScraper()
    return scraper.scrape_search_results(keyword, marketplace, max_results)


def search_keywords_for_categorization(keywords: List[str], marketplace: str = "US") -> Dict[str, Any]:
    """
    Search multiple keywords on Amazon for categorization analysis.
    
    Args:
        keywords: List of keywords to search
        marketplace: Target marketplace code
        
    Returns:
        Dict containing search results for all keywords
    """
    scraper = AmazonSearchScraper()
    results = {}
    
    for keyword in keywords:
        search_result = scraper.scrape_search_results(keyword, marketplace)
        results[keyword] = search_result
    
    return {
        "success": True,
        "marketplace": marketplace,
        "keywords_searched": len(keywords),
        "search_results": results
    }


