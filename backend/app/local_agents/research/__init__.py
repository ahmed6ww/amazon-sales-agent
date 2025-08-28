"""
Research Agent Package

This package contains the Amazon product research agent with tools for:
- Scraping Amazon product listings
- Parsing Helium10 CSV files
- Determining market positioning
"""

from .agent import (
    research_agent
)
from .schemas import ScrapeResult, CSVParseResult, ProductAttributes, MarketPosition
from .tools import tool_scrape_amazon_listing, tool_parse_helium10_csv, tool_determine_market_position
from .prompts import RESEARCH_AGENT_INSTRUCTIONS
from .helper_methods import (
    scrape_amazon_listing_with_traditional_scraper,
    parse_helium10_csv,
    determine_market_position,
    extract_mvp_sources_from_traditional_data
)
from .runner import ResearchRunner

# Main scraping function
scrape_amazon_listing = scrape_amazon_listing_with_traditional_scraper

__all__ = [
    "research_agent",
    "ResearchRunner",
    "scrape_amazon_listing_with_traditional_scraper",
    "scrape_amazon_listing",  # Main function
    "parse_helium10_csv",
    "determine_market_position",
    "extract_mvp_sources_from_traditional_data",
    "ScrapeResult",
    "CSVParseResult",
    "ProductAttributes",
    "MarketPosition",
    "tool_scrape_amazon_listing",
    "tool_parse_helium10_csv",
    "tool_determine_market_position",
    "RESEARCH_AGENT_INSTRUCTIONS"
] 