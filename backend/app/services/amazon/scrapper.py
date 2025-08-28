import scrapy
from scrapy.crawler import CrawlerProcess
import sys
import re
import json
import textwrap # Imported for better text formatting in the output


# --- Moved Pipeline to Top Level ---
# The DataCollectorPipeline class is now defined at the module's top level,
# making it visible to the Scrapy CrawlerProcess.
class DataCollectorPipeline:
    def __init__(self, stats):
        self.stats = stats
        self.data = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def close_spider(self, spider):
        # When the spider closes, copy its data to our reference.
        # This is the primary mechanism for getting data out of the spider.
        spider.crawler.stats.set_value("scraped_data", spider.scraped_data)


class AmazonProductSpider(scrapy.Spider):
    """
    A Scrapy spider to comprehensively scrape Amazon product pages.
    """

    name = "amazon_product_spider"

    # This dictionary will hold all the scraped data.
    scraped_data = {}

    def __init__(self, url=None, *args, **kwargs):
        super(AmazonProductSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        else:
            raise ValueError("A start URL must be provided.")

    def parse(self, response):
        """Main parse method to delegate parsing to the correct function."""
        is_amazon_product = "amazon." in response.url and (
            "/dp/" in response.url or "/gp/product/" in response.url
        )

        if is_amazon_product:
            self.parse_amazon_product(response)
        else:
            self.parse_general_page(response)

    # --- Helper methods for extracting and cleaning data ---

    def _get_first(self, response_or_selector, selectors):
        """Get the first non-empty result from a list of CSS selectors."""
        for selector in selectors:
            result = response_or_selector.css(selector).get()
            if result:
                return result.strip()
        return None

    def _get_all(self, response_or_selector, selectors):
        """Get all non-empty results from a list of CSS selectors."""
        for selector in selectors:
            results = response_or_selector.css(selector).getall()
            if results:
                cleaned_results = [r.strip() for r in results if r.strip()]
                if cleaned_results:
                    return cleaned_results
        return []

    def _clean_price(self, price):
        """Remove currency symbols and extra whitespace from price."""
        if not price:
            return None
        return re.sub(r"[^\d.]", "", price)

    # --- Main parsing functions for different page types ---

    def parse_general_page(self, response):
        """Fallback parser for non-Amazon pages."""
        self.scraped_data["title"] = response.css("title::text").get("").strip()
        self.scraped_data["headings"] = self._get_all(
            response, ["h1::text", "h2::text", "h3::text"]
        )
        self.scraped_data["description"] = self._get_first(
            response, ['meta[name="description"]::attr(content)']
        )
        self.scraped_data["text_content"] = self._get_all(response, ["p::text"])
        self.scraped_data["links"] = response.css("a::attr(href)").getall()

    def parse_amazon_product(self, response):
        """Comprehensive parser for an Amazon product page."""

        # Extract ASIN from URL
        asin_match = re.search(r"/dp/([A-Z0-9]{10})", response.url)
        self.scraped_data["asin"] = (
            asin_match.group(1) if asin_match else "ASIN not found"
        )

        self.scraped_data["product_title"] = (
            self._get_first(response, ["#productTitle::text"]) or "Title not found"
        )

        # Enhanced price extraction
        price_str = self._get_first(
            response,
            [
                ".a-price .a-offscreen::text",
                ".priceToPay .a-offscreen::text",
                "#corePrice_feature_div span.a-offscreen::text",
            ],
        )
        self.scraped_data["price"] = self._clean_price(price_str) or "Price not found"

        # Better original price extraction
        original_price_str = self._get_first(
            response,
            [
                ".a-price[data-a-strike=true] .a-offscreen::text",
                ".a-text-strike .a-offscreen::text",
                ".basisPrice .a-offscreen::text",
            ],
        )
        self.scraped_data["original_price"] = (
            self._clean_price(original_price_str) or "No original price"
        )

        # Enhanced rating extraction with multiple fallbacks
        rating_str = self._get_first(
            response,
            [
                "#acrPopover::attr(title)",
                '[data-hook="rating-out-of-text"]::text',
                "#acrPopover .a-icon-alt::text",
                'span[aria-label*="stars"]::attr(aria-label)',
            ],
        )
        if rating_str:
            # Extract numeric rating from text like "4.7 out of 5 stars"
            rating_match = re.search(r"(\d+\.?\d*)\s*out of", rating_str)
            self.scraped_data["rating"] = (
                rating_match.group(1) if rating_match else rating_str
            )
        else:
            self.scraped_data["rating"] = "Rating not found"

        # Add review count extraction
        review_count_str = self._get_first(
            response,
            [
                "#acrCustomerReviewText::text",
                '[data-hook="total-review-count"]::text',
                'span[aria-label*="ratings"]::attr(aria-label)',
            ],
        )
        if review_count_str:
            # Extract number from text like "1,234 ratings"
            review_match = re.search(r"([\d,]+)", review_count_str.replace(",", ""))
            self.scraped_data["review_count"] = (
                review_match.group(1) if review_match else review_count_str
            )
        else:
            self.scraped_data["review_count"] = "Review count not found"

        self.scraped_data["availability"] = (
            self._get_first(
                response,
                ["#availability .a-color-success::text", "#availability span::text"],
            )
            or "Availability not found"
        )

        self.scraped_data["brand"] = (
            self._get_first(
                response, ["tr.po-brand .a-span9 span::text", "#bylineInfo::text"]
            )
            or "Brand not found"
        )

        # Extract product details/specifications table
        specs = {}
        spec_rows = response.css(
            "#productDetails_techSpec_section_1 tr, #productDetails_detailBullets_sections1 tr"
        )
        for row in spec_rows:
            key = self._get_first(row, ["th::text"])
            value = self._get_first(row, ["td::text"])
            if key and value:
                specs[key.strip()] = value.strip()
        self.scraped_data["specifications"] = specs or {
            "specs": "Specifications not found"
        }

        # Attempt to extract manufacturer from specifications or detail bullets
        manufacturer = None
        for key, value in specs.items():
            normalized_key = re.sub(r"\W+", "", key).lower()
            if normalized_key.startswith("manufacturer"):
                manufacturer = value.strip()
                break
        if not manufacturer:
            detail_items = response.css("#detailBullets_feature_div li")
            for li in detail_items:
                label = li.css("span.a-text-bold::text").get()
                if label and "Manufacturer" in label:
                    value_parts = li.css("span:not(.a-text-bold)::text").getall()
                    value_text = " ".join([v.strip() for v in value_parts if v.strip()])
                    if value_text:
                        manufacturer = re.sub(r"\s+", " ", value_text)
                        break
        if manufacturer:
            self.scraped_data["manufacturer"] = manufacturer

        # Extract Best Sellers Rank (from Product details bullets)
        best_sellers_rank = {}
        try:
            bsr_li = None
            for li in response.css("#detailBullets_feature_div li"):
                label = li.css("span.a-text-bold::text").get()
                if label and "Best Sellers Rank" in label:
                    bsr_li = li
                    break

            if bsr_li:
                # Combined text content within the list item
                all_text_parts = [
                    t.strip()
                    for t in bsr_li.css("span.a-list-item ::text").getall()
                    if t.strip()
                ]
                combined_text = re.sub(r"\s+", " ", " ".join(all_text_parts))

                # Overall rank like "#2 in Beauty & Personal Care"
                overall_match = re.search(r"#(\d+)\s+in\s+([^#(]+)", combined_text)
                if overall_match:
                    overall_rank_num = int(overall_match.group(1))
                    overall_category = overall_match.group(2).strip()
                else:
                    overall_rank_num = None
                    overall_category = None

                # Top 100 link for overall category (if present)
                top_100_href = bsr_li.css(
                    'a[href*="/gp/bestsellers/"]::attr(href)'
                ).get()
                top_100_url = response.urljoin(top_100_href) if top_100_href else None

                # Sub ranks under the nested list
                sub_ranks = []
                for sub in bsr_li.css("ul.zg_hrsr li, ul.a-nostyle li"):
                    sub_text = " ".join(
                        [t.strip() for t in sub.css("*::text").getall() if t.strip()]
                    )
                    sub_text = re.sub(r"\s+", " ", sub_text)
                    if not sub_text:
                        continue
                    sub_match = re.search(r"#(\d+)\s+in\s+(.+)", sub_text)
                    sub_rank_num = int(sub_match.group(1)) if sub_match else None
                    sub_category = sub_match.group(2).strip() if sub_match else sub_text
                    sub_href = sub.css("a::attr(href)").get()
                    sub_url = response.urljoin(sub_href) if sub_href else None
                    sub_ranks.append(
                        {
                            "text": sub_text,
                            "rank": sub_rank_num,
                            "category": sub_category,
                            "url": sub_url,
                        }
                    )

                best_sellers_rank = {
                    "overall": {
                        "text": (
                            f"#{overall_rank_num} in {overall_category}"
                            if overall_rank_num and overall_category
                            else None
                        ),
                        "rank": overall_rank_num,
                        "category": overall_category,
                        "top_100_url": top_100_url,
                    },
                    "sub": sub_ranks,
                }

            # Fallback: sometimes appears in specs table value
            if not best_sellers_rank:
                for key, value in specs.items():
                    if "best sellers rank" in key.lower():
                        value_clean = re.sub(r"\s+", " ", value)
                        segments = re.findall(r"#\d+\s+in\s+[^#;]+", value_clean)
                        best_sellers_rank = {
                            "overall": {
                                "text": segments[0] if segments else value_clean,
                                "rank": None,
                                "category": None,
                                "top_100_url": None,
                            },
                            "sub": [
                                {"text": s, "rank": None, "category": None, "url": None}
                                for s in segments[1:]
                            ],
                        }
                        break

            if best_sellers_rank:
                self.scraped_data["best_sellers_rank"] = best_sellers_rank
        except Exception:
            # Do not fail the whole scrape if BSR parsing is brittle
            pass

        # Enhanced image extraction using multiple methods
        main_image = None
        all_images = []

        # Method 1: Extract from data-a-dynamic-image attribute
        image_data_str = response.css(
            "#imgTagWrapperId img::attr(data-a-dynamic-image)"
        ).get()
        if image_data_str:
            try:
                image_data = json.loads(image_data_str)
                all_images = list(image_data.keys())
                main_image = all_images[0] if all_images else None
            except json.JSONDecodeError:
                pass

        # Method 2: Extract from script tags containing colorImages JSON (from report)
        if not all_images:
            script_texts = response.css("script::text").getall()
            for script in script_texts:
                # Look for colorImages pattern from the report
                color_images_match = re.search(
                    r"colorImages['\"]:\s*.*?['\"]initial['\"]\s*:\s*(\[.+?\])", script
                )
                if color_images_match:
                    try:
                        images_json = json.loads(color_images_match.group(1))
                        for img in images_json:
                            if "hiRes" in img and img["hiRes"]:
                                all_images.append(img["hiRes"])
                            elif "large" in img and img["large"]:
                                all_images.append(img["large"])
                        if all_images:
                            main_image = all_images[0]
                            break
                    except (json.JSONDecodeError, KeyError):
                        continue

        # Method 3: Fallback to basic selectors
        if not main_image:
            main_image = self._get_first(
                response, ["#landingImage::attr(src)", "#imgBlkFront::attr(src)"]
            )

        if not all_images:
            all_images = self._get_all(
                response, ["#altImages img::attr(src)", ".s-image::attr(src)"]
            )

        self.scraped_data["main_image"] = main_image or "Image not found"
        self.scraped_data["all_images"] = all_images or []

        # Enhanced seller extraction
        self.scraped_data["seller"] = (
            self._get_first(
                response,
                [
                    "#sellerProfileContainer a::text",
                    "a#sellerName::text",
                    "#sellerProfileTriggerId::text",
                    "#merchant-info a::text",
                    "#shipsFromSoldBy_feature_div a::text",
                ],
            )
            or "Seller not found"
        )
        self.scraped_data["categories"] = self._get_all(
            response, ["#wayfinding-breadcrumbs_feature_div a::text"]
        ) or ["Categories not found"]

        # Fallback: If seller not found, use manufacturer value
        if (
            not self.scraped_data.get("seller")
            or self.scraped_data.get("seller") == "Seller not found"
        ) and self.scraped_data.get("manufacturer"):
            self.scraped_data["seller"] = self.scraped_data["manufacturer"]

        # --- Extracting structured product information ---
        self.scraped_data["product_information_sections"] = (
            self.extract_product_information(response)
        )
        
        # --- NEW: Extract AI-generated customer summary ---
        ai_summary_text = self._get_first(
            response,
            [
                # This selector is specific to the "Customers say" section
                'div#product-summary[data-hook="cr-insights-widget-summary"] p.a-spacing-small span::text',
            ],
        )
        self.scraped_data["ai_summary"] = ai_summary_text or "AI summary not found"


    def extract_product_information(self, response):
        """
        Extracts key sections like 'About this item', 'Product Description', etc.
        into a structured dictionary.
        """
        sections = {}

        # 1. About this item / Key Features (enhanced extraction)
        about_content = self._get_all(
            response,
            [
                "#feature-bullets ul li span::text",
                "#feature-bullets .a-list-item::text",
                "#feature-bullets li::text",
            ],
        )
        # Clean up the content - remove empty items and unwanted text
        if about_content:
            cleaned_content = []
            for item in about_content:
                item = item.strip()
                # Skip items that are just "See more product details" or similar
                if item and len(item) > 10 and not item.startswith("See more"):
                    cleaned_content.append(item)
            if cleaned_content:
                sections["About this item"] = {
                    "type": "list",
                    "content": cleaned_content,
                }

        # 2. From the brand / manufacturer (A+ Content)
        brand_content_parts = []
        brand_headers = response.css("#aplus h2::text, #aplus h3::text").getall()
        brand_paras = response.css("#aplus p::text").getall()
        if brand_headers or brand_paras:
            if brand_headers:
                brand_content_parts.extend([h.strip() for h in brand_headers])
            if brand_paras:
                brand_content_parts.extend([p.strip() for p in brand_paras])
            sections["From the brand/manufacturer"] = {
                "type": "paragraphs",
                "content": [part for part in brand_content_parts if part],
            }

        # 3. Product Description
        description_header = (
            self._get_first(response, ["#productDescription h2::text"])
            or "Product Description"
        )
        description_content = self._get_all(
            response,
            ["#productDescription p span::text", "#productDescription p::text"],
        )
        if description_content:
            sections[description_header] = {
                "type": "paragraphs",
                "content": description_content,
            }

        # 4. Product details
        details_header = (
            self._get_first(response, ["#productDetails h2::text"]) or "Product details"
        )
        details_content = self._get_all(
            response,
            [
                "#productDetails .a-list-item::text",
                "#detailBullets_feature_div .a-list-item::text",
            ],
        )
        if details_content:
            cleaned_details = []
            for item in details_content:
                text = re.sub(r"\s+", " ", item).strip()
                # Skip empty/parentheses-only fragments and BSR-related fragments
                if not text or text in {"(", ")"}:
                    continue
                if "Best Sellers Rank" in text:
                    continue
                if re.search(r"^#\d+\s+in\b", text):
                    continue
                cleaned_details.append(text)
            if cleaned_details:
                sections[details_header] = {
                    "type": "list",
                    "content": cleaned_details,
                }

        # 5. Important information
        important_info_header = (
            self._get_first(response, ["#important-information h2::text"])
            or "Important information"
        )
        important_info_content = {}
        for section in response.css("#important-information .a-section"):
            sub_heading = self._get_first(section, ["h4::text"])
            text = " ".join(self._get_all(section, ["p::text"]))
            if sub_heading and text:
                important_info_content[sub_heading] = text
        if important_info_content:
            sections[important_info_header] = {
                "type": "sub-sections",
                "content": important_info_content,
            }

        return sections


def scrape_url(url: str):
    """
    Run a one-off scrape and return the collected data.
    """
    process = CrawlerProcess(
        settings={
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "ROBOTSTXT_OBEY": False,
            "LOG_LEVEL": "ERROR",  # Reduce noise so the heading is the first output
            "DOWNLOAD_DELAY": 0.75,
            "COOKIES_ENABLED": True,
            "RETRY_ENABLED": True,
            "RETRY_TIMES": 2,
            "DOWNLOAD_TIMEOUT": 30,
            "REFERER_ENABLED": True,
            "DEFAULT_REQUEST_HEADERS": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
            },
            "AUTOTHROTTLE_ENABLED": True,
            "AUTOTHROTTLE_START_DELAY": 0.5,
            "AUTOTHROTTLE_MAX_DELAY": 10.0,
            "ITEM_PIPELINES": {
                __name__ + ".DataCollectorPipeline": 300,
            },
        }
    )

    crawler = process.create_crawler(AmazonProductSpider)
    process.crawl(crawler, url=url)
    process.start()

    # Retrieve the data from the stats after the crawl is finished
    return crawler.stats.get_value("scraped_data", {})


def display_results(result):
    """Formats and prints the scraped data to the console with beautiful formatting."""
    if not result:
        print("\n❌ No data was scraped or an error occurred.")
        return

    # For product pages, start directly with the main heading
    if "product_title" in result and result["product_title"] != "Title not found":
        print("🛍️  AMAZON PRODUCT DETAILS  🛍️")

        # Product Title - make it stand out
        title = result.get("product_title", "Not found")
        asin = result.get("asin", "Not found")
        print(f"\n📝 PRODUCT TITLE:")
        print(f"   {title}")
        print(f"   🔖 ASIN: {asin}")

        # Key product info in a nice table format
        print(f"\n💼 ESSENTIAL DETAILS:")
        price = result.get("price", "Not found")
        original_price = result.get("original_price", "No original price")

        if price != "Not found":
            if original_price != "No original price":
                print(f"   💰 Current Price:    ${price}")
                print(f"   💸 Original Price:   ${original_price}")
                try:
                    savings = float(original_price) - float(price)
                    print(f"   💸 You Save:         ${savings:.2f}")
                except (ValueError, TypeError):
                    pass
            else:
                print(f"   💰 Price:            ${price}")
        else:
            print(f"   💰 Price:            Not available")

        rating = result.get("rating", "Not available")
        review_count = result.get("review_count", "Not available")
        print(f"   ⭐ Rating:           {rating}")
        if review_count != "Not available":
            print(f"   📊 Review Count:     {review_count} reviews")
        print(f"   📦 Availability:     {result.get('availability', 'Not available')}")
        print(f"   🏷️  Brand:            {result.get('brand', 'Not available')}")
        print(f"   🏪 Seller:           {result.get('seller', 'Not available')}")

        # Categories
        categories = result.get("categories", [])
        if categories and categories != ["Categories not found"]:
            print(f"   🗂️  Categories:       {' > '.join(categories)}")

        # Images section - show URLs
        print(f"\n🖼️  IMAGES:")
        main_image = result.get("main_image")
        print(f"   📸 Main Image:       {main_image or 'Not found'}")
        all_images = result.get("all_images", [])
        if all_images:
            print("   🖼️  Gallery URLs:")
            for idx, url in enumerate(all_images, 1):
                print(f"      {idx:02d}. {url}")
        else:
            print("   🖼️  Gallery URLs:    None")

        # Specifications in a clean format
        specs = result.get("specifications", {})
        if specs and "specs" not in specs:
            print(f"\n⚙️  SPECIFICATIONS:")
            for key, value in specs.items():
                display_value = str(value)
                print(f"   - {key}: {display_value}")

        # --- NEW: AI-Generated Summary display ---
        ai_summary = result.get("ai_summary")
        if ai_summary and ai_summary != "AI summary not found":
            print(f"\n🤖 CUSTOMER REVIEWS SUMMARY:")
            # Use textwrap to format the paragraph nicely in the console
            wrapped_summary = textwrap.fill(ai_summary, width=80, initial_indent="   ", subsequent_indent="   ")
            print(wrapped_summary)

        # Structured Information with better formatting
        sections = result.get("product_information_sections", {})
        if sections:
            print(f"\n📄 DETAILED PRODUCT INFORMATION:")
            for section_title, data in sections.items():
                print(f"\n{section_title.upper()}:")
                content = data.get("content")
                if not content:
                    continue
                if data["type"] == "list":
                    for item in content:
                        print(f" - {item}")
                elif data["type"] == "paragraphs":
                    for para in content:
                        print(f" {para}")
                elif data["type"] == "sub-sections":
                    for sub_head, text in content.items():
                        print(f" - {sub_head}: {text}")

        # Best Sellers Rank display (structured)
        bsr = result.get("best_sellers_rank")
        if bsr:
            print(f"\n🏆 BEST SELLERS RANK:")
            overall = bsr.get("overall", {})
            overall_text = overall.get("text")
            if overall_text:
                print(f"   • Overall: {overall_text}")
            sub = bsr.get("sub", [])
            for item in sub:
                print(f"   • {item.get('text')}")

    else:
        # General page formatting
        print("📄  WEBPAGE SUMMARY  📄")

        title = result.get("title", "Not found")
        print(f"\n📝 PAGE TITLE:")
        print(f"   {title}")

        headings = result.get("headings", [])
        print(f"\n📑 CONTENT OVERVIEW:")
        print(f"   🔤 Headings found:    {len(headings)}")

        if headings:
            print(f"   📋 All headings ({len(headings)} total):")
            for heading in headings:
                print(f"      • {heading}")

        description = result.get("description")
        if description:
            print(f"\n📄 DESCRIPTION:")
            print(f"   {description}")