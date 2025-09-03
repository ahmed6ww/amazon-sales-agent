from agents import Agent, ModelSettings
from agents.tool import function_tool
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

# Define Research tools for AI-only path
@function_tool
def tool_extract_product_attributes(scraped_json: str) -> str:
    import json
    data = json.loads(scraped_json)
    # Return as-is for now; real extraction is already done by scraper
    return json.dumps({"extracted": True, "sources": list(data.keys())})

@function_tool
def tool_parse_csv(csv_json: str) -> str:
    import json
    rows = json.loads(csv_json)
    return json.dumps({"rows": len(rows)})

load_dotenv(find_dotenv())  # Load environment variables from .env file


# Implementation functions have been moved to helper_methods.py

# Create the Research Agent with MVP-focused instructions
research_agent = Agent(
    name="ResearchAgent",
    instructions=RESEARCH_AGENT_INSTRUCTIONS,
    model="gpt-5-2025-08-07",  # Tool-compatible
    tools=[
        tool_extract_product_attributes,
        tool_parse_csv,
    ],
    model_settings=ModelSettings(
        max_tokens=4000,
        tool_choice="required",
    )
) 