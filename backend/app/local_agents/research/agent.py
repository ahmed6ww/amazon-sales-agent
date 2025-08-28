from agents import Agent, function_tool, ModelSettings
from typing import Dict, Any, List, Optional
import csv
import re
import os
from pathlib import Path
from pydantic import BaseModel
from app.services.amazon.firecrawl_client import FirecrawlClient
import json
import subprocess
import sys

class ScrapeResult(BaseModel):
    success: bool
    data: Dict[str, Any]
    url: str
    error: Optional[str] = None

class CSVParseResult(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    count: Optional[int] = None
    error: Optional[str] = None

class ProductAttributes(BaseModel):
    # MVP Required Sources Only
    title: str
    images: Dict[str, Any]
    aplus_content: Dict[str, Any]
    reviews: Dict[str, Any]
    qa_section: Dict[str, Any]

class MarketPosition(BaseModel):
    price_tier: str
    final_tier: str
    price: float
    premium_score: int
    budget_score: int
    positioning_factors: Dict[str, str]

# -----------------------------
# Implementation functions (for tests and internal calls)
# -----------------------------

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
    
    # Extract A+ content from "From the brand/manufacturer" section
    aplus_sections = []
    aplus_content_blocks = []
    
    # Look for brand content
    brand_section = product_sections.get("From the brand/manufacturer", {})
    if brand_section and brand_section.get("type") == "paragraphs":
        content = brand_section.get("content", [])
        aplus_sections.extend(content[:5])  # Limit to 5 sections
    
    # Look for product description as A+ content
    desc_section = product_sections.get("Product Description", {})
    if desc_section and desc_section.get("type") == "paragraphs":
        content = desc_section.get("content", [])
        aplus_sections.extend(content[:3])  # Add up to 3 more
    
    aplus_content = {
        "sections": aplus_sections[:10],  # Max 10 sections
        "content_blocks": aplus_content_blocks,
        "total_length": sum(len(section) for section in aplus_sections[:10])
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

def extract_product_info_from_firecrawl(firecrawl_data: Dict[str, Any], asin: str, url: str) -> Dict[str, Any]:
    """
    Extract ONLY the MVP required sources: title, images, A+ content, reviews, Q&A section.
    Includes content truncation to avoid context window issues.
    """
    # Handle both dict and object formats
    if hasattr(firecrawl_data, 'metadata'):
        metadata = firecrawl_data.metadata if hasattr(firecrawl_data.metadata, '__dict__') else firecrawl_data.metadata or {}
        markdown = getattr(firecrawl_data, 'markdown', '') or ''
        html = getattr(firecrawl_data, 'html', '') or ''
    else:
        metadata = firecrawl_data.get("metadata", {}) or {}
        markdown = firecrawl_data.get("markdown", "") or ""
        html = firecrawl_data.get("html", "") or ""
    
    # TRUNCATE CONTENT TO AVOID CONTEXT WINDOW ISSUES
    # Keep only the most relevant parts for MVP extraction
    MAX_MARKDOWN_LENGTH = 50000  # ~50KB limit
    MAX_HTML_LENGTH = 30000      # ~30KB limit
    
    if len(markdown) > MAX_MARKDOWN_LENGTH:
        # Keep beginning (product info) and middle section (reviews/Q&A)
        markdown = markdown[:MAX_MARKDOWN_LENGTH//2] + "\n...[TRUNCATED]...\n" + markdown[-MAX_MARKDOWN_LENGTH//2:]
    
    if len(html) > MAX_HTML_LENGTH:
        html = html[:MAX_HTML_LENGTH] + "...[TRUNCATED]..."
    
    # ===== 1. TITLE EXTRACTION =====
    product_title = ""
    if isinstance(metadata, dict):
        product_title = metadata.get("title", "")
    elif hasattr(metadata, 'title'):
        product_title = metadata.title or ""
    
    if not product_title or "Amazon" in product_title:
        title_patterns = [
            r'# (.+?)(?:\n|$)',  # Markdown header
            r'<title>(.+?)</title>',  # HTML title
            r'productTitle["\']?>([^<\n]+)',  # Amazon product title ID
        ]
        for pattern in title_patterns:
            title_match = re.search(pattern, markdown + html, re.IGNORECASE)
            if title_match:
                product_title = title_match.group(1).strip()
                break
    
    # ===== 2. IMAGES EXTRACTION =====
    image_patterns = [
        r'!\[([^\]]*)\]\(([^)]+)\)',  # Markdown images
        r'<img[^>]+src=["\']([^"\']+)["\']',  # HTML img tags
        r'https://[^"\s]+\.(?:jpg|jpeg|png|webp|gif)',  # Direct image URLs
    ]
    
    found_images = set()
    for pattern in image_patterns:
        matches = re.findall(pattern, markdown + html, re.IGNORECASE)
        if isinstance(matches[0], tuple) if matches else False:
            found_images.update([match[1] if len(match) > 1 else match[0] for match in matches])
        else:
            found_images.update(matches)
    
    # Filter out small/irrelevant images
    relevant_images = []
    for img_url in found_images:
        if any(indicator in img_url.lower() for indicator in ['product', 'large', 'zoom', 'main']):
            relevant_images.insert(0, img_url)  # Priority images first
        elif not any(skip in img_url.lower() for skip in ['icon', 'logo', 'button', 'star', 'pixel']):
            relevant_images.append(img_url)
    
    images = {
        "main_image": relevant_images[0] if relevant_images else "",
        "all_images": list(relevant_images),
        "image_count": len(relevant_images)
    }
    
    # ===== 3. A+ CONTENT EXTRACTION =====
    aplus_patterns = [
        r'(?:A\+|Enhanced|Brand Store|From the Brand)[:\s]*(.+?)(?:\n\n|\n#{1,3}|$)',
        r'<div[^>]*(?:aplus|brand|enhanced)[^>]*>(.+?)</div>',
        r'## (?:From the brand|Brand story|About)(.+?)(?:\n\n|\n#{1,2}|$)',
    ]
    
    aplus_sections = []
    for pattern in aplus_patterns:
        matches = re.findall(pattern, markdown + html, re.DOTALL | re.IGNORECASE)
        for match in matches:
            cleaned_content = re.sub(r'<[^>]+>', ' ', match).strip()
            if 50 < len(cleaned_content) < 1000:  # Limit section size
                aplus_sections.append(cleaned_content[:500])  # Truncate to 500 chars
    
    # Extract content blocks
    content_blocks = []
    content_block_matches = re.findall(r'(?:###?\s+(.+?)\n(.+?)(?=\n###?|\n\n|$))', markdown, re.DOTALL)
    for header, content in content_block_matches:
        if 100 < len(content.strip()) < 1000:
            content_blocks.append({
                "header": header.strip()[:100],  # Limit header length
                "content": content.strip()[:300]  # Limit content length
            })
        if len(content_blocks) >= 5:  # Limit number of blocks
            break
    
    aplus_content = {
        "sections": aplus_sections[:10],  # Limit to 10 sections max
        "content_blocks": content_blocks[:5],  # Limit to 5 blocks max
        "total_length": sum(len(section) for section in aplus_sections[:10])
    }
    
    # ===== 4. REVIEWS EXTRACTION =====
    review_patterns = [
        r'(?:Review|Customer)[:\s]*(.{50,200})',
        r'★{1,5}\s*(.{30,150})',
        r'Verified Purchase[:\s]*(.{40,200})',
        r'(?:Helpful|Good|Great|Bad|Poor)[:\s]*(.{40,180})',
    ]
    
    found_reviews = []
    for pattern in review_patterns:
        matches = re.findall(pattern, markdown, re.IGNORECASE)
        for match in matches:
            cleaned_review = re.sub(r'[^\w\s.,!?-]', ' ', match).strip()
            if 20 < len(cleaned_review) < 200:
                found_reviews.append(cleaned_review[:150])  # Limit review length
            if len(found_reviews) >= 15:  # Limit number of reviews processed
                break
    
    # Extract review highlights
    review_highlights = []
    # Limit review text to avoid processing too much content
    review_text = ' '.join(found_reviews[:10])  # Only use first 10 reviews
    if review_text:
        attribute_patterns = [
            r'\b(quality|sturdy|durable|cheap|expensive)\b',
            r'\b(easy|difficult|hard) to (.{5,20})\b',
            r'\b(love|hate|like|dislike) (.{5,30})\b',
            r'\b(works|doesnt work|broken|perfect)\b',
        ]
        
        for pattern in attribute_patterns:
            matches = re.findall(pattern, review_text, re.IGNORECASE)
            review_highlights.extend([' '.join(match) if isinstance(match, tuple) else match for match in matches])
            if len(review_highlights) >= 20:  # Limit highlights
                break
    
    reviews = {
        "sample_reviews": list(set(found_reviews))[:5],  # Limit to 5 unique reviews
        "review_highlights": review_highlights[:15]  # Limit highlights
    }
    
    # ===== 5. Q&A SECTION EXTRACTION =====
    qa_patterns = [
        r'(?:Question|Q)[:\s]*(.{10,150})\s*(?:Answer|A)[:\s]*(.{10,200})',
        r'Q:\s*(.+?)\s*A:\s*(.+?)(?=\n|Q:|$)',
        r'(?:Ask|Question)[:\s]*(.{20,150})',
    ]
    
    qa_pairs = []
    questions = []
    
    for pattern in qa_patterns:
        matches = re.findall(pattern, markdown, re.DOTALL | re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple) and len(match) == 2:
                qa_pairs.append({
                    "question": match[0].strip()[:100],  # Shorter questions
                    "answer": match[1].strip()[:150]     # Shorter answers
                })
                if len(qa_pairs) >= 5:  # Limit to 5 Q&A pairs
                    break
            else:
                question = match if isinstance(match, str) else match[0]
                questions.append(question.strip()[:100])  # Shorter questions
                if len(questions) >= 10:  # Limit to 10 standalone questions
                    break
    
    qa_section = {
        "qa_pairs": qa_pairs[:5],      # Limit pairs
        "questions": questions[:10]    # Limit questions
    }
    
    # ===== RETURN ONLY MVP REQUIRED DATA =====
    return {
        "asin": asin,
        "title": product_title,
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

def extract_product_attributes_from_firecrawl(listing_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract ONLY the MVP required sources: title, images, A+ content, reviews, Q&A section.
    
    Args:
        listing_data: Simplified data with only MVP sources
        
    Returns:
        Clean product attributes with only essential data
    """
    return {
        "title": listing_data.get("title", ""),
        "images": listing_data.get("images", {}),
        "aplus_content": listing_data.get("aplus_content", {}),
        "reviews": listing_data.get("reviews", {}),
        "qa_section": listing_data.get("qa_section", {})
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

# -----------------------------
# Decorated tool wrappers for the Agent (string-in / string-out)
# -----------------------------

@function_tool
def tool_scrape_amazon_listing(asin_or_url: str) -> str:
    """
    Scrape an Amazon product listing to extract clean MVP required sources: title, images, A+ content, reviews, Q&A section.
    
    Args:
        asin_or_url: Either an ASIN (e.g., B08KT2Z93D) or full Amazon URL
        
    Returns:
        JSON string containing clean MVP product data
    """
    result = scrape_amazon_listing_with_traditional_scraper(asin_or_url)
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
def tool_extract_product_attributes(listing_data_json: str) -> str:
    """
    Extract MVP product attributes: title, images, A+ content, reviews, Q&A section.
    
    Args:
        listing_data_json: JSON string of scraped listing data
        
    Returns:
        JSON string containing clean MVP attributes
    """
    try:
        listing_data = json.loads(listing_data_json) if listing_data_json else {}
        result = extract_product_attributes_from_firecrawl(listing_data)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON input: {str(e)}"})

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

# Create the Research Agent with MVP-focused instructions
research_agent = Agent(
    name="ResearchAgent",
    instructions="""
    You are an Amazon product research specialist focused on extracting the 5 MVP required sources for keyword research.
    
    Your primary responsibility:
    Extract ONLY these 5 product attribute sources from Amazon listings:
    1. TITLE - Product title text
    2. IMAGES - Product image URLs and descriptions
    3. A+ CONTENT - Enhanced brand content sections
    4. REVIEWS - Customer review samples and highlights  
    5. Q&A SECTION - Question and answer pairs
    
    Secondary responsibilities:
    - Parse Helium10 Cerebro CSV files for competitor keyword data
    - Determine market positioning (budget vs premium) when needed
    
    Your streamlined workflow:
    1. Scrape Amazon listing with tool_scrape_amazon_listing (extracts MVP sources only)
    2. Extract clean attributes with tool_extract_product_attributes (returns only the 5 sources)
    3. If market positioning needed, use tool_determine_market_position
    4. If CSV files provided, parse with tool_parse_helium10_csv
    
    Focus on:
    - Clean, structured extraction of the 5 MVP sources
    - Quality assessment of each source (title length, image count, A+ content size, review samples, Q&A pairs)
    - Actionable insights for keyword research
    
    Always report which of the 5 sources were successfully extracted and their quality.
    """,
    tools=[
        tool_scrape_amazon_listing,
        tool_parse_helium10_csv, 
        tool_extract_product_attributes,
        tool_determine_market_position
    ],
    model_settings=ModelSettings(
        temperature=0.1,
        max_tokens=4000
    )
) 