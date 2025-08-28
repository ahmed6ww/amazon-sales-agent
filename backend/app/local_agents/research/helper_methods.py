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


def scrape_amazon_listing_with_traditional_scraper(asin_or_url: str) -> Dict[str, Any]:
    """
    Scrape an Amazon product listing using traditional scraper to extract clean MVP data.

    Args:
        asin_or_url: Either an ASIN (e.g., B08KT2Z93D) or full Amazon URL

    Returns:
        Dict containing clean scraped product data with MVP sources
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

        # Use traditional scraper for clean data
        from app.services.amazon.scrapper import scrape_url
        scraped_data = scrape_url(url)

        if not scraped_data:
            return {
                "success": False,
                "error": "Traditional scraper returned no data",
                "data": {},
                "url": url
            }

        # Extract only MVP required sources from clean scraped data
        mvp_data = extract_mvp_sources_from_traditional_data(scraped_data, asin, url)

        return {
            "success": True,
            "data": mvp_data,
            "url": url
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error scraping with traditional scraper: {str(e)}",
            "data": {},
            "url": url if 'url' in locals() else asin_or_url
        }


def extract_mvp_sources_from_traditional_data(scraped_data: Dict[str, Any], asin: str, url: str) -> Dict[str, Any]:
    """
    Extract the 5 MVP required sources from clean traditional scraper data.

    Args:
        scraped_data: Clean data from traditional Amazon scraper
        asin: Product ASIN
        url: Product URL

    Returns:
        Dict with only the 5 MVP sources: title, images, aplus_content, reviews, qa_section
    """

    # ===== 1. TITLE EXTRACTION =====
    title = scraped_data.get("product_title", "")

    # ===== 2. IMAGES EXTRACTION =====
    main_image = scraped_data.get("main_image", "")
    all_images = scraped_data.get("all_images", [])

    images = {
        "main_image": main_image,
        "all_images": all_images,
        "image_count": len(all_images)
    }

    # ===== 3. A+ CONTENT EXTRACTION =====
    product_sections = scraped_data.get("product_information_sections", {})

    # Normalize keys for case-insensitive lookup
    def _find_section_key(target: str) -> Optional[str]:
        t = target.strip().lower()
        for k in product_sections.keys():
            if k.strip().lower() == t:
                return k
        return None

    # Extract A+ content blocks
    content_blocks: List[Dict[str, Any]] = []

    # 3a. From the brand/manufacturer (paragraphs)
    brand_key = _find_section_key("From the brand/manufacturer")
    brand_section = product_sections.get(brand_key, {}) if brand_key else {}
    if brand_section and brand_section.get("type") == "paragraphs":
        content = brand_section.get("content", [])
        if content:
            content_blocks.append({
                "heading": brand_key,
                "paragraphs": content
            })

    # 3b. Product Description (paragraphs)
    desc_key = _find_section_key("Product Description") or _find_section_key("Product Description".title())
    desc_section = product_sections.get(desc_key, {}) if desc_key else {}
    if desc_section and desc_section.get("type") == "paragraphs":
        content = desc_section.get("content", [])
        if content:
            content_blocks.append({
                "heading": desc_key,
                "paragraphs": content
            })

    # 3c. ABOUT THIS ITEM (list)
    about_key = _find_section_key("About this item")
    about_section = product_sections.get(about_key, {}) if about_key else {}
    if about_section and about_section.get("type") == "list":
        about_items = about_section.get("content", [])
        if about_items:
            content_blocks.append({
                "heading": about_key,
                "items": about_items
            })

    # 3d. IMPORTANT INFORMATION (sub-sections)
    important_key = _find_section_key("Important information")
    important_section = product_sections.get(important_key, {}) if important_key else {}
    if important_section and important_section.get("type") == "sub-sections":
        important_content: Dict[str, str] = important_section.get("content", {}) or {}
        if important_content:
            content_blocks.append({
                "heading": important_key,
                "items": [f"{k}: {v}" for k, v in important_content.items()]
            })

    # Calculate total length from the structured blocks
    total_length = 0
    for block in content_blocks:
        if "paragraphs" in block:
            total_length += sum(len(p) for p in block["paragraphs"])
        if "items" in block:
            total_length += sum(len(i) for i in block["items"])

    # Finalize A+ content payload
    aplus_content = {
        "sections": content_blocks,
        "total_length": total_length
    }

    # ===== 4. REVIEWS EXTRACTION =====
    # The traditional scraper has AI summary, use that as review content
    ai_summary = scraped_data.get("ai_summary", "")

    # Create sample reviews from AI summary
    sample_reviews = []
    if ai_summary and ai_summary != "AI summary not found":
        # Split AI summary into review-like segments
        sentences = ai_summary.split('. ')
        sample_reviews = [f"{sentence.strip()}." for sentence in sentences if len(sentence.strip()) > 20][:5]

    # Extract review highlights from rating and review count
    review_highlights = []
    rating = scraped_data.get("rating", "")
    review_count = scraped_data.get("review_count", "")

    if rating != "Rating not found":
        review_highlights.append(f"rating {rating}")
    if review_count != "Review count not found":
        review_highlights.append(f"{review_count} reviews")

    reviews = {
        "sample_reviews": sample_reviews,
        "review_highlights": review_highlights
    }

    # ===== 5. Q&A SECTION EXTRACTION =====
    # Traditional scraper doesn't extract Q&A, so we'll create empty structure
    qa_section = {
        "qa_pairs": [],
        "questions": []
    }

    # Return only the 5 MVP sources
    return {
        "asin": asin,
        "title": title,
        "images": images,
        "aplus_content": aplus_content,
        "reviews": reviews,
        "qa_section": qa_section
    }


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
