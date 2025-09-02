from agents import function_tool
import json
from .schemas import ScrapeResult, CSVParseResult, ProductAttributes, MarketPosition
from .helper_methods import scrape_amazon_listing_with_mvp_scraper, parse_helium10_csv, determine_market_position


@function_tool
def tool_scrape_amazon_listing(asin_or_url: str) -> str:
    """
    Scrape an Amazon product listing to extract clean MVP required sources: title, images, A+ content, reviews, Q&A section.

    Args:
        asin_or_url: Either an ASIN (e.g., B08KT2Z93D) or full Amazon URL

    Returns:
        JSON string containing clean MVP product data
    """
    result = scrape_amazon_listing_with_mvp_scraper(asin_or_url)
    return json.dumps(result, indent=2)


@function_tool
def tool_parse_helium10_csv(file_path: str) -> str:
    """
    Parse a Helium10 Cerebro CSV file to extract keyword data with metrics.

    Args:
        file_path: Path to the Helium10 CSV file

    Returns:
        JSON string containing parsed keyword data
    """
    result = parse_helium10_csv(file_path)
    return json.dumps(result, indent=2)


@function_tool
def tool_determine_market_position(attributes_json: str) -> str:
    """
    Determine market positioning (budget/mid-range/premium) based on pricing and features.

    Args:
        attributes_json: JSON string of extracted product attributes

    Returns:
        JSON string containing market position analysis
    """
    try:
        attributes = json.loads(attributes_json) if attributes_json else {}
        result = determine_market_position(attributes)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON input: {str(e)}"})
