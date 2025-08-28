from agents import Agent
from typing import Dict, Any, List, Optional
import csv
import re
import os
from pathlib import Path
from app.services.amazon.scrapper import scrape_url

def scrape_amazon_listing(asin_or_url: str) -> Dict[str, Any]:
    """
    Scrape an Amazon product listing to extract all product attributes.
    
    Args:
        asin_or_url: Either an ASIN (e.g., B08KT2Z93D) or full Amazon URL
        
    Returns:
        Dictionary containing scraped product data including title, price, rating, 
        images, specifications, product information sections, etc.
    """
    # Convert ASIN to full URL if needed
    if not asin_or_url.startswith("http"):
        url = f"https://www.amazon.com/dp/{asin_or_url}"
    else:
        url = asin_or_url
    
    # Use existing scraper
    listing_data = scrape_url(url)
    
    return {
        "success": True,
        "data": listing_data,
        "url": url
    }

def parse_helium10_csv(file_path: str) -> Dict[str, Any]:
    """
    Parse a Helium10 Cerebro CSV file to extract keyword data.
    
    Args:
        file_path: Path to the Helium10 CSV file
        
    Returns:
        Dictionary containing parsed keyword data with metrics
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

def extract_product_attributes(listing_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and categorize key product attributes from scraped listing data.
    
    Args:
        listing_data: Raw scraped data from Amazon listing
        
    Returns:
        Structured product attributes for competitor filtering and analysis
    """
    attributes = {
        "basic_info": {},
        "features": [],
        "specifications": {},
        "category_info": {},
        "pricing": {},
        "content_sources": {}
    }
    
    # Basic product information
    attributes["basic_info"] = {
        "asin": listing_data.get("asin", ""),
        "title": listing_data.get("product_title", ""),
        "brand": listing_data.get("brand", ""),
        "manufacturer": listing_data.get("manufacturer", ""),
        "categories": listing_data.get("categories", [])
    }
    
    # Pricing information for budget/premium classification
    price_str = listing_data.get("price", "0")
    original_price_str = listing_data.get("original_price", "0")
    
    try:
        current_price = float(re.sub(r'[^\d.]', '', price_str)) if price_str != "Price not found" else 0
        original_price = float(re.sub(r'[^\d.]', '', original_price_str)) if original_price_str not in ["No original price", "Price not found"] else current_price
    except:
        current_price = 0
        original_price = 0
    
    attributes["pricing"] = {
        "current_price": current_price,
        "original_price": original_price,
        "price_tier": "budget" if current_price < 25 else "premium" if current_price > 100 else "mid-range"
    }
    
    # Extract features from structured sections
    product_sections = listing_data.get("product_information_sections", {})
    
    # From "About this item" section
    about_section = product_sections.get("About this item", {})
    if about_section and about_section.get("type") == "list":
        attributes["features"] = about_section.get("content", [])
    
    # Specifications
    attributes["specifications"] = listing_data.get("specifications", {})
    
    # Category classification
    categories = listing_data.get("categories", [])
    attributes["category_info"] = {
        "main_category": categories[0] if categories else "",
        "sub_categories": categories[1:] if len(categories) > 1 else [],
        "best_sellers_rank": listing_data.get("best_sellers_rank", {})
    }
    
    # Content sources for attribute extraction
    attributes["content_sources"] = {
        "title": listing_data.get("product_title", ""),
        "images_count": len(listing_data.get("all_images", [])),
        "has_aplus_content": bool(product_sections.get("From the brand/manufacturer")),
        "review_count": listing_data.get("review_count", "0"),
        "rating": listing_data.get("rating", "0"),
        "has_qa_section": False,  # Would need additional scraping
        "product_sections": list(product_sections.keys())
    }
    
    return attributes

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

# Create the Research Agent with proper instructions
research_agent = Agent(
    name="ResearchAgent",
    instructions="""
    You are an Amazon product research specialist focused on comprehensive product analysis for keyword research.
    
    Your primary responsibilities:
    1. Process Amazon product URLs or ASINs to extract complete product information
    2. Parse Helium10 Cerebro CSV files containing competitor keyword data
    3. Extract and categorize product attributes from listings (title, images, A+ content, reviews, Q&A)
    4. Determine market positioning (budget vs premium) based on pricing and features
    5. Prepare structured data for downstream keyword analysis
    
    When processing products:
    - Always validate URLs and convert ASINs to full Amazon URLs
    - Extract comprehensive product attributes including pricing, features, specifications
    - Identify content sources (title, images, A+ content, review data)
    - Classify market position to help with competitor filtering
    - Parse competitor data from Helium10 CSV files accurately
    
    Provide clear, structured output that can be used by keyword processing agents.
    """,
    tools=[
        scrape_amazon_listing,
        parse_helium10_csv, 
        extract_product_attributes,
        determine_market_position
    ]
) 