"""
Amazon Keyword Categorizer

Implements requirements #15-24: Keyword categorization based on Amazon search results.
- Design-specific: Shows exactly similar design/product
- Relevant: Shows different designs of same product  
- Irrelevant: Shows products not matching CSV products
- Outlier: Shows mix of matching and non-matching products
"""

import logging
from typing import Dict, Any, List, Optional, Set
from app.services.amazon.search_scraper import AmazonSearchScraper
from app.services.amazon.country_handler import get_marketplace_from_url

logger = logging.getLogger(__name__)


class AmazonKeywordCategorizer:
    """Categorizes keywords based on Amazon search results analysis"""
    
    def __init__(self, csv_products: List[Dict[str, Any]], marketplace: str = "US"):
        """
        Initialize categorizer with CSV product data.
        
        Args:
            csv_products: List of products from CSV files (with ASINs, titles, etc.)
            marketplace: Target marketplace code
        """
        self.csv_products = csv_products
        self.marketplace = marketplace
        self.search_scraper = AmazonSearchScraper()
        
        # Extract ASINs and titles from CSV products for comparison
        self.csv_asins = self._extract_csv_asins()
        self.csv_titles = self._extract_csv_titles()
        self.csv_brands = self._extract_csv_brands()
        
        logger.info(f"Initialized categorizer with {len(self.csv_products)} CSV products")
        logger.info(f"CSV ASINs: {len(self.csv_asins)}, Titles: {len(self.csv_titles)}")
    
    def _extract_csv_asins(self) -> Set[str]:
        """Extract ASINs from CSV products"""
        asins = set()
        for product in self.csv_products:
            # Look for ASIN in various possible fields
            for field in ['asin', 'ASIN', 'product_asin', 'amazon_asin']:
                if field in product and product[field]:
                    asins.add(str(product[field]).strip())
        return asins
    
    def _extract_csv_titles(self) -> List[str]:
        """Extract titles from CSV products"""
        titles = []
        for product in self.csv_products:
            # Look for title in various possible fields
            for field in ['title', 'Title', 'product_title', 'name', 'product_name']:
                if field in product and product[field]:
                    titles.append(str(product[field]).strip().lower())
        return titles
    
    def _extract_csv_brands(self) -> Set[str]:
        """Extract brands from CSV products"""
        brands = set()
        for product in self.csv_products:
            # Look for brand in various possible fields
            for field in ['brand', 'Brand', 'manufacturer', 'company']:
                if field in product and product[field]:
                    brands.add(str(product[field]).strip().lower())
        return brands
    
    def categorize_keyword(self, keyword: str) -> Dict[str, Any]:
        """
        Categorize a single keyword based on Amazon search results (requirements #15-19).
        
        Args:
            keyword: Keyword to categorize
            
        Returns:
            Dict containing categorization result
        """
        try:
            # Search keyword on Amazon
            search_result = self.search_scraper.scrape_search_results(keyword, self.marketplace, max_results=15)
            
            if not search_result.get("success"):
                return {
                    "keyword": keyword,
                    "category": "Irrelevant",
                    "reason": f"Search failed: {search_result.get('error')}",
                    "confidence": 0.0,
                    "search_results_count": 0
                }
            
            organic_results = search_result.get("results", [])
            
            if not organic_results:
                return {
                    "keyword": keyword,
                    "category": "Irrelevant", 
                    "reason": "No organic search results found",
                    "confidence": 0.0,
                    "search_results_count": 0
                }
            
            # Analyze search results against CSV products
            analysis = self._analyze_search_results(keyword, organic_results)
            
            return {
                "keyword": keyword,
                "category": analysis["category"],
                "reason": analysis["reason"],
                "confidence": analysis["confidence"],
                "search_results_count": len(organic_results),
                "matching_products": analysis["matching_products"],
                "non_matching_products": analysis["non_matching_products"],
                "analysis_details": analysis["details"]
            }
            
        except Exception as e:
            logger.error(f"Error categorizing keyword '{keyword}': {e}")
            return {
                "keyword": keyword,
                "category": "Irrelevant",
                "reason": f"Categorization error: {str(e)}",
                "confidence": 0.0,
                "search_results_count": 0
            }
    
    def _analyze_search_results(self, keyword: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze search results to determine keyword category (requirements #15-19).
        
        Args:
            keyword: The keyword being analyzed
            search_results: List of organic search results
            
        Returns:
            Dict containing analysis results
        """
        matching_products = []
        non_matching_products = []
        
        # Analyze each search result
        for result in search_results:
            is_match = self._is_product_match(result)
            
            if is_match:
                matching_products.append(result)
            else:
                non_matching_products.append(result)
        
        # Determine category based on matching analysis
        category, reason, confidence = self._determine_category(
            keyword, matching_products, non_matching_products
        )
        
        return {
            "category": category,
            "reason": reason,
            "confidence": confidence,
            "matching_products": matching_products,
            "non_matching_products": non_matching_products,
            "details": {
                "total_results": len(search_results),
                "matching_count": len(matching_products),
                "non_matching_count": len(non_matching_products),
                "match_ratio": len(matching_products) / len(search_results) if search_results else 0
            }
        }
    
    def _is_product_match(self, search_result: Dict[str, Any]) -> bool:
        """
        Check if a search result matches any CSV product (requirements #15-19).
        
        Args:
            search_result: Single search result from Amazon
            
        Returns:
            True if matches CSV product, False otherwise
        """
        # Check ASIN match (exact match)
        result_asin = search_result.get("asin", "").strip()
        if result_asin and result_asin in self.csv_asins:
            return True
        
        # Check title similarity
        result_title = search_result.get("title", "").strip().lower()
        if result_title:
            for csv_title in self.csv_titles:
                if self._titles_similar(result_title, csv_title):
                    return True
        
        # Check brand match
        result_brand = self._extract_brand_from_title(result_title)
        if result_brand and result_brand in self.csv_brands:
            return True
        
        return False
    
    def _titles_similar(self, title1: str, title2: str, threshold: float = 0.7) -> bool:
        """
        Check if two titles are similar enough to be considered the same product.
        
        Args:
            title1: First title
            title2: Second title
            threshold: Similarity threshold (0-1)
            
        Returns:
            True if titles are similar enough
        """
        # Simple word overlap similarity
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union) if union else 0
        return similarity >= threshold
    
    def _extract_brand_from_title(self, title: str) -> Optional[str]:
        """Extract brand name from product title"""
        # Simple brand extraction - first word or two words
        words = title.split()
        if words:
            # Check if first word is a brand
            if len(words[0]) > 2:
                return words[0]
            # Check first two words
            if len(words) > 1 and len(words[0] + words[1]) > 3:
                return f"{words[0]} {words[1]}"
        return None
    
    def _determine_category(self, keyword: str, matching_products: List[Dict], non_matching_products: List[Dict]) -> tuple:
        """
        Determine keyword category based on matching analysis (requirements #15-19).
        
        Args:
            keyword: The keyword being analyzed
            matching_products: Products that match CSV data
            non_matching_products: Products that don't match CSV data
            
        Returns:
            Tuple of (category, reason, confidence)
        """
        total_results = len(matching_products) + len(non_matching_products)
        
        if total_results == 0:
            return "Irrelevant", "No search results found", 0.0
        
        match_ratio = len(matching_products) / total_results
        
        # Requirement #15: Design-specific - shows exactly similar design/product (>= 80%)
        if match_ratio >= 0.8 and len(matching_products) >= 3:
            return "Design-Specific", f"Shows exactly similar products ({len(matching_products)}/{total_results} match)", 0.9
        
        # Requirement #18: Outlier - shows mix of matching and non-matching products (20-50%)
        if 0.2 <= match_ratio <= 0.5 and len(matching_products) >= 1:
            return "Outlier", f"Shows mixed product variety ({len(matching_products)}/{total_results} match)", 0.7
        
        # Requirement #16: Relevant - shows different designs of same product (50-80%)
        if 0.5 < match_ratio < 0.8 and len(matching_products) >= 2:
            return "Relevant", f"Shows similar product variations ({len(matching_products)}/{total_results} match)", 0.8
        
        # Requirement #19: Irrelevant - shows one design across results but not matching CSV
        if len(matching_products) == 0 and total_results >= 5:
            return "Irrelevant", "Shows consistent but different product design", 0.7
        
        # Requirement #17: Irrelevant - shows products not matching CSV products
        if match_ratio < 0.2:
            return "Irrelevant", f"Shows different products ({len(matching_products)}/{total_results} match)", 0.8
        
        # Default fallback
        return "Relevant", f"General product relevance ({len(matching_products)}/{total_results} match)", 0.5
    
    def categorize_keywords_batch(self, keywords: List[str], apply_root_rules: bool = False) -> Dict[str, Any]:
        """
        Categorize multiple keywords in batch with optional root-level classification rules.
        
        Args:
            keywords: List of keywords to categorize
            apply_root_rules: Whether to apply root-level classification rules (requirements #22-24)
            
        Returns:
            Dict containing categorization results for all keywords
        """
        results = {}
        
        # First, categorize each keyword individually
        for keyword in keywords:
            logger.info(f"Categorizing keyword: {keyword}")
            result = self.categorize_keyword(keyword)
            results[keyword] = result
        
        # Apply root-level classification rules only if requested (requirements #22-24)
        if apply_root_rules:
            results = self._apply_root_classification_rules(keywords, results)
        
        # Summary statistics
        categories = [result["category"] for result in results.values()]
        category_counts = {}
        for category in categories:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "success": True,
            "total_keywords": len(keywords),
            "categorization_results": results,
            "category_summary": category_counts,
            "marketplace": self.marketplace
        }
    
    def _apply_root_classification_rules(self, keywords: List[str], results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply root-level classification rules (requirements #22-24).
        
        Args:
            keywords: List of keywords
            results: Initial categorization results
            
        Returns:
            Updated results with root-level rules applied
        """
        from app.services.keyword_processing.root_extraction import extract_meaningful_roots
        
        # Extract roots for all keywords
        roots = extract_meaningful_roots(keywords)
        
        # Categorize each root
        root_categories = {}
        for root_name in roots.keys():
            root_result = self.categorize_keyword(root_name)
            root_categories[root_name] = root_result["category"]
        
        # Apply classification rules to each keyword
        for keyword in keywords:
            keyword_roots = []
            for root_name in roots.keys():
                if root_name in keyword.lower():
                    keyword_roots.append((root_name, root_categories[root_name]))
            
            if keyword_roots:
                # Requirement #22: If keyword has irrelevant root then keyword is irrelevant (override rule)
                irrelevant_roots = [root for root, category in keyword_roots if category == "Irrelevant"]
                if irrelevant_roots:
                    results[keyword]["category"] = "Irrelevant"
                    results[keyword]["reason"] = f"Contains irrelevant root(s): {', '.join(irrelevant_roots)}"
                    results[keyword]["confidence"] = 0.9
                    continue
                
                # Requirement #23: If keyword has no irrelevant root and has design-specific root then design-specific
                design_specific_roots = [root for root, category in keyword_roots if category == "Design-Specific"]
                if design_specific_roots:
                    results[keyword]["category"] = "Design-Specific"
                    results[keyword]["reason"] = f"Contains design-specific root(s): {', '.join(design_specific_roots)}"
                    results[keyword]["confidence"] = 0.9
                    continue
                
                # Requirement #24: If keyword has no irrelevant/design-specific roots and has relevant root then relevant
                relevant_roots = [root for root, category in keyword_roots if category == "Relevant"]
                if relevant_roots:
                    results[keyword]["category"] = "Relevant"
                    results[keyword]["reason"] = f"Contains relevant root(s): {', '.join(relevant_roots)}"
                    results[keyword]["confidence"] = 0.8
                    continue
        
        return results


def categorize_keywords_with_amazon_search(
    keywords: List[str], 
    csv_products: List[Dict[str, Any]], 
    marketplace: str = "US",
    apply_root_rules: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to categorize keywords using Amazon search analysis.
    
    Args:
        keywords: List of keywords to categorize
        csv_products: List of products from CSV files
        marketplace: Target marketplace code
        apply_root_rules: Whether to apply root-level classification rules
        
    Returns:
        Dict containing categorization results
    """
    categorizer = AmazonKeywordCategorizer(csv_products, marketplace)
    return categorizer.categorize_keywords_batch(keywords, apply_root_rules=apply_root_rules)
