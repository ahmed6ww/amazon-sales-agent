"""
Research Agent Module

This module provides comprehensive Amazon product research capabilities using
the OpenAI Agents SDK and Firecrawl for web scraping. It includes tools for:
- Scraping Amazon product listings with Firecrawl
- Parsing Helium10 CSV data
- Extracting product attributes from Firecrawl data
- Market positioning analysis
"""

from .agent import (
    research_agent,
    scrape_amazon_listing_with_firecrawl,
    parse_helium10_csv,
    extract_product_attributes_from_firecrawl,
    determine_market_position,
    extract_product_info_from_firecrawl
)

from .runner import ResearchRunner

# Backward compatibility aliases
scrape_amazon_listing = scrape_amazon_listing_with_firecrawl
extract_product_attributes = extract_product_attributes_from_firecrawl

__all__ = [
    "research_agent",
    "ResearchRunner", 
    "scrape_amazon_listing_with_firecrawl",
    "scrape_amazon_listing",  # Backward compatibility
    "parse_helium10_csv",
    "extract_product_attributes_from_firecrawl",
    "extract_product_attributes",  # Backward compatibility
    "determine_market_position",
    "extract_product_info_from_firecrawl"
] 