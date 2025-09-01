from agents import Agent, ModelSettings
from dotenv import load_dotenv, find_dotenv

from .schemas import ScrapeResult, CSVParseResult, ProductAttributes, MarketPosition
# Function tools no longer used - using Pythonic approach
# from .tools import tool_scrape_amazon_listing, tool_parse_helium10_csv, tool_determine_market_position
from .prompts import RESEARCH_AGENT_INSTRUCTIONS
from .helper_methods import (
    scrape_amazon_listing_with_mvp_scraper,

    parse_helium10_csv,
    determine_market_position
)

load_dotenv(find_dotenv())  # Load environment variables from .env file


# Implementation functions have been moved to helper_methods.py

# Create the Research Agent with MVP-focused instructions
research_agent = Agent(
    name="ResearchAgent",
    instructions=RESEARCH_AGENT_INSTRUCTIONS,
    tools=[
            # No tools needed - using Pythonic approach
    ],
    model_settings=ModelSettings(
        temperature=0.1,
        max_tokens=4000
    )
) 