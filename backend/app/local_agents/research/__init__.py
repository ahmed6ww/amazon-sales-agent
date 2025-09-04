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
from .schemas import ScrapeResult, ProductAttributes
# Function tools no longer used - using Pythonic approach
# from .tools import tool_scrape_amazon_listing, tool_parse_helium10_csv, tool_determine_market_position
from .prompts import RESEARCH_AGENT_INSTRUCTIONS
from .helper_methods import (
    scrape_amazon_listing,
)
from .runner import ResearchRunner

# Main scraping function
scrape_amazon_listing = scrape_amazon_listing

__all__ = [
    "research_agent",
    "ResearchRunner",
    "scrape_amazon_listing",
    "ScrapeResult",
    "ProductAttributes",
    # Function tools no longer used - using Pythonic approach
    "RESEARCH_AGENT_INSTRUCTIONS"
] 