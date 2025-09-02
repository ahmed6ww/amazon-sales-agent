"""
Helper Methods for Research Agent

This module contains the core implementation functions for:
- Amazon product scraping
- Data extraction and processing
- CSV parsing
- Market position analysis
"""

import csv
import re
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())  # Load environment variables from .env file


def scrape_amazon_listing_with_mvp_scraper(asin_or_url: str) -> Dict[str, Any]:
    """
    Scrape an Amazon product listing using MVP scraper via subprocess isolation.
    This completely avoids any reactor conflicts with FastAPI/OpenAI agents.

    Args:
        asin_or_url: Either an ASIN (e.g., B08KT2Z93D) or full Amazon URL

    Returns:
        Dict containing MVP scraped data (title, images, A+ content, reviews, Q&A)
    """
    try:
        # Convert ASIN to full URL if needed
        if not asin_or_url.startswith("http"):
            url = f"https://www.amazon.com/dp/{asin_or_url}"
            asin = asin_or_url
        else:
            url = asin_or_url
            # Extract ASIN from URL
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
            asin = asin_match.group(1) if asin_match else ""

        # Use subprocess to run scraper in isolation
        import subprocess
        import json
        import sys
        from pathlib import Path
        
        # Get the path to the standalone MVP scraper
        current_file = Path(__file__)
        app_dir = current_file.parent.parent.parent
        backend_dir = app_dir.parent  # Go up one level from app to backend
        scraper_script = app_dir / "services" / "amazon" / "standalone_mvp_scraper.py"
        
        # Run the MVP scraper in a separate process
        result = subprocess.run(
            [sys.executable, str(scraper_script), url],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
            cwd=str(backend_dir)
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"MVP scraper process failed: {result.stderr}",
                "data": {},
                "url": url
            }
        
        # Parse JSON output (extract only the JSON part, ignore debug output)
        try:
            # Look for the JSON object in the output
            stdout_lines = result.stdout.strip().split('\n')
            json_line = None
            
            # Find the line that starts with '{' (the JSON output)
            for line in stdout_lines:
                line = line.strip()
                if line.startswith('{'):
                    json_line = line
                    break
            
            if json_line:
                subprocess_result = json.loads(json_line)
            else:
                # If no JSON found, try parsing the entire output
                subprocess_result = json.loads(result.stdout)
                
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse MVP scraper output: {str(e)}. Output: {result.stdout[:200]}",
                "data": {},
                "url": url
            }
        
        # Check if subprocess scraping was successful
        if not subprocess_result.get("success"):
            return {
                "success": False,
                "error": subprocess_result.get("error", "Unknown subprocess error"),
                "data": {},
                "url": url
            }

        scraped_data = subprocess_result.get("data", {})
        
        # Check if scraping was blocked or failed
        if "error" in scraped_data:
            return {
                "success": False,
                "error": f"Scraping blocked: {scraped_data.get('error')}",
                "blocked_reason": scraped_data.get("blocked_reason", "Unknown"),
                "data": {},
                "url": url
            }
        
        if not scraped_data or not scraped_data.get("asin"):
            return {
                "success": False,
                "error": "No valid product data extracted - Amazon may be blocking requests",
                "data": {},
                "url": url
            }

        # MVP scraper already returns clean data in the right format
        return {
            "success": True,
            "data": scraped_data,
            "url": url
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "MVP scraper process timed out (120 seconds)",
            "data": {},
            "url": url if 'url' in locals() else asin_or_url
        }
    except Exception as e:
        import traceback
        error_details = f"Error in MVP subprocess scraping: {str(e)}\nTraceback: {traceback.format_exc()}"
        return {
            "success": False,
            "error": error_details,
            "data": {},
            "url": url if 'url' in locals() else asin_or_url
        }


# Function removed - MVP scraper already returns properly structured data


def parse_helium10_csv(file_path: str) -> Dict[str, Any]:
    """
    Parse a Helium10 Cerebro CSV file to extract keyword data.

    Args:
        file_path: Path to the Helium10 CSV file

    Returns:
        Dict containing parsed keyword data with metrics
    """
    if not file_path or not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File not found: {file_path}",
            "data": []
        }

    try:
        keywords = []
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Clean up the row data
                cleaned_row = {}
                for key, value in row.items():
                    if key:  # Skip empty keys
                        # Normalize common column names
                        normalized_key = key.strip()
                        cleaned_row[normalized_key] = value.strip() if value else ""

                if cleaned_row:  # Only add non-empty rows
                    keywords.append(cleaned_row)

        return {
            "success": True,
            "data": keywords,
            "count": len(keywords)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }


def determine_market_position(attributes: Dict[str, Any], competitor_data: List[Dict] = None) -> Dict[str, Any]:
    """
    Determine if the product is budget, mid-range, or premium based on pricing and features.

    Args:
        attributes: Extracted product attributes
        competitor_data: Optional competitor pricing data for comparison

    Returns:
        Market position analysis
    """
    pricing = attributes.get("pricing", {})
    current_price = pricing.get("current_price", 0)

    # Basic price tier classification
    price_tier = pricing.get("price_tier", "unknown")

    # Enhanced classification based on features and brand
    brand = attributes.get("basic_info", {}).get("brand", "").lower()
    features = attributes.get("features", [])
    specs = attributes.get("specifications", {})

    # Premium indicators
    premium_keywords = ["premium", "luxury", "professional", "high-end", "stainless steel", "memory foam"]
    premium_score = sum(1 for keyword in premium_keywords if any(keyword in str(item).lower() for item in features + list(specs.values()) + [brand]))

    # Budget indicators
    budget_keywords = ["basic", "simple", "economy", "plastic", "lightweight"]
    budget_score = sum(1 for keyword in budget_keywords if any(keyword in str(item).lower() for item in features + list(specs.values()) + [brand]))

    # Final classification
    if current_price > 100 or premium_score > 2:
        final_tier = "premium"
    elif current_price < 25 or budget_score > 2:
        final_tier = "budget"
    else:
        final_tier = "mid-range"

    return {
        "price_tier": price_tier,
        "final_tier": final_tier,
        "price": current_price,
        "premium_score": premium_score,
        "budget_score": budget_score,
        "positioning_factors": {
            "price_based": price_tier,
            "feature_based": "premium" if premium_score > budget_score else "budget" if budget_score > 0 else "standard"
        }
    }
