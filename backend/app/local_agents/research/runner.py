from agents import Runner
from typing import Dict, Any, Optional
from .agent import research_agent
from .helper_methods import scrape_amazon_listing


class ResearchRunner:
    """
    Minimal runner: scrape via helper, then analyze with the agent once.
    """

    def run_research(
        self,
        asin_or_url: str,
        marketplace: str = "US",
        main_keyword: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Scrape the Amazon listing and analyze the 5 MVP sources using the agent.

        Args:
            asin_or_url: Amazon ASIN or full product URL
            marketplace: Target marketplace code
            main_keyword: Optional main keyword context

        Returns:
            Dict with success flag, analysis text, and raw scraped data
        """

        # 1) Fetch scraped data via helper
        scraped_result = scrape_amazon_listing(asin_or_url)
        if not scraped_result.get("success"):
            return {
                "success": False,
                "error": f"Scraping failed: {scraped_result.get('error', 'Unknown error')}",
                "scraped_data": scraped_result,
            }

        scraped_data = scraped_result.get("data", {})

        # 2) Build a single analysis prompt using pre-fetched data
        prompt = (
            "Analyze this pre-fetched Amazon product data for the 5 MVP required sources:\n\n"
            f"PRODUCT INFO:\n- URL/ASIN: {asin_or_url}\n- Marketplace: {marketplace}\n- Main Keyword: {main_keyword or 'Not specified'}\n\n"
            f"SCRAPED DATA:\n{scraped_data}\n\n"
            "Required sources to analyze:\n"
            "1. TITLE - Product title text and quality assessment\n"
            "2. IMAGES - Image URLs, count, and quality\n"
            "3. A+ CONTENT - Enhanced brand content sections and marketing material\n"
            "4. REVIEWS - Customer review samples and sentiment highlights\n"
            "5. Q&A SECTION - Question and answer pairs\n\n"
            "For each source, provide:\n"
            "- Extracted: Yes/No\n"
            "- Content: The actual data found\n"
            "- Quality: Assessment (Excellent/Good/Fair/Poor/Missing)\n"
            "- Notes: Any observations about completeness or issues\n"
        )

        # 3) Single agent call
        try:
            result = Runner.run_sync(research_agent, prompt)
            return {
                "success": True,
                "final_output": result.final_output,
                "scraped_data": scraped_data,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_output": None,
                "scraped_data": scraped_data,
            }