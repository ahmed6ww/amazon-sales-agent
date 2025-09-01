"""
Pythonic Research Runner - Pre-fetch data approach
Following OpenAI best practices for deterministic flows
"""

from agents import Agent, Runner, ModelSettings
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PythonicResearchRunner:
    """
    Research runner that follows OpenAI best practices:
    1. Pre-fetch data using pure Python functions
    2. Pass structured data directly to agents for analysis
    3. Use deterministic flows rather than tool-based approaches
    """
    
    def __init__(self):
        # Create a simple research agent WITHOUT function tools
        self.research_agent = Agent(
            name="ResearchAnalyst",
            instructions="""
You are a professional product research analyst. You will be provided with pre-fetched Amazon product data in JSON format.

Your task is to analyze the provided data and extract the 5 MVP required sources:

1. TITLE - Product title and quality assessment
2. IMAGES - Image URLs, count, and quality
3. A+ CONTENT - Enhanced brand content sections and marketing material
4. REVIEWS - Customer review samples and sentiment highlights  
5. Q&A SECTION - Question and answer pairs

For each source, provide:
- **Extracted**: Yes/No
- **Content**: The actual data found
- **Quality**: Assessment (Excellent/Good/Fair/Poor)
- **Notes**: Any observations about completeness or issues

Format your response with clear headings and bullet points for easy reading.
Focus on data quality, completeness, and usefulness for keyword research purposes.
            """,
            model="gpt-4o",
            model_settings=ModelSettings(
                temperature=0.1,
                max_tokens=4000
            )
        )
    
    async def run_research_analysis(self, asin_or_url: str) -> Dict[str, Any]:
        """
        Main research method using pure Pythonic approach:
        1. Pre-fetch data using independent Python functions
        2. Pass structured data to agent for analysis
        3. Return comprehensive results
        """
        try:
            # Step 1: Pre-fetch data using pure Python (no tools)
            logger.info(f"Pre-fetching data for: {asin_or_url}")
            scraped_data = await self._fetch_amazon_data(asin_or_url)
            
            if not scraped_data.get("success"):
                return {
                    "success": False,
                    "error": f"Data fetching failed: {scraped_data.get('error')}",
                    "analysis": None
                }
            
            # Step 2: Structure the data for agent analysis
            structured_data = self._structure_data_for_analysis(scraped_data["data"])
            
            # Step 3: Create analysis prompt with pre-fetched data
            analysis_prompt = self._create_analysis_prompt(asin_or_url, structured_data)
            
            # Step 4: Pass data directly to agent (no tool calls needed)
            logger.info("Running agent analysis on pre-fetched data")
            result = await Runner.run(self.research_agent, analysis_prompt)
            
            return {
                "success": True,
                "analysis": result.final_output,
                "raw_data": scraped_data["data"],
                "structured_data": structured_data,
                "agent_used": "ResearchAnalyst"
            }
            
        except Exception as e:
            logger.error(f"Research analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    async def analyze_prefetched_data(self, raw_data: Dict[str, Any], source_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze pre-fetched data without invoking any scraper.
        """
        try:
            structured_data = self._structure_data_for_analysis(raw_data or {})
            analysis_prompt = self._create_analysis_prompt(source_url or "", structured_data)
            logger.info("Running agent analysis on pre-fetched data (external)")
            result = await Runner.run(self.research_agent, analysis_prompt)
            return {
                "success": True,
                "analysis": result.final_output,
                "raw_data": raw_data,
                "structured_data": structured_data,
                "agent_used": "ResearchAnalyst"
            }
        except Exception as e:
            logger.error(f"Prefetched data analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    async def _fetch_amazon_data(self, asin_or_url: str) -> Dict[str, Any]:
        """
        Pure Python data fetching - no agent tools involved
        Uses our proven subprocess approach
        """
        try:
                           # Import here to avoid circular imports
               from .helper_methods import scrape_amazon_listing_with_mvp_scraper
               
               # Use our working MVP subprocess scraper
               return scrape_amazon_listing_with_mvp_scraper(asin_or_url)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Scraping failed: {str(e)}",
                "data": {}
            }
    
    def _structure_data_for_analysis(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure raw scraped data for agent analysis
        Convert MVP data into a clear format for the agent
        """
        structured = {
            "product_info": {
                "asin": raw_data.get("asin", "Not found"),
                "title": raw_data.get("title", raw_data.get("product_title", "Not found")),
                "url": raw_data.get("url", "Not provided")
            },
            "images": {
                "main_image": raw_data.get("images", {}).get("main_image", "Not found"),
                "all_images": raw_data.get("images", {}).get("all_images", []),
                "image_count": raw_data.get("images", {}).get("image_count", 0)
            },
            "aplus_content": raw_data.get("aplus_content", []),
            "reviews": {
                "sample_reviews": raw_data.get("reviews", {}).get("sample_reviews", []),
                "review_highlights": raw_data.get("reviews", {}).get("review_highlights", [])
            },
            "qa_section": {
                "qa_pairs": raw_data.get("qa_section", {}).get("qa_pairs", []),
                "questions": raw_data.get("qa_section", {}).get("questions", [])
            }
        }
        
        return structured
    
    def _create_analysis_prompt(self, asin_or_url: str, structured_data: Dict[str, Any]) -> str:
        """
        Create a comprehensive analysis prompt with pre-fetched data
        """
        import json
        
        prompt = f"""
Analyze this Amazon product data for MVP source extraction:

PRODUCT URL: {asin_or_url}

PRE-FETCHED DATA:
{json.dumps(structured_data, indent=2)}

Please provide a comprehensive analysis of the 5 MVP required sources based on this data.
Assess data quality, completeness, and usefulness for keyword research.
        """
        
        return prompt
    
    def run_research_analysis_sync(self, asin_or_url: str) -> Dict[str, Any]:
        """
        Synchronous version for easier integration
        """
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.run_research_analysis(asin_or_url))
        except RuntimeError:
            # No event loop running
            return asyncio.run(self.run_research_analysis(asin_or_url))
    
    def analyze_prefetched_data_sync(self, raw_data: Dict[str, Any], source_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Synchronous wrapper for analyzing pre-fetched data
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.analyze_prefetched_data(raw_data, source_url))
        except RuntimeError:
            return asyncio.run(self.analyze_prefetched_data(raw_data, source_url))


# Convenience function for direct usage
async def analyze_amazon_product(asin_or_url: str) -> Dict[str, Any]:
    """
    Convenience function for direct product analysis
    """
    runner = PythonicResearchRunner()
    return await runner.run_research_analysis(asin_or_url)


def analyze_amazon_product_sync(asin_or_url: str) -> Dict[str, Any]:
    """
    Synchronous convenience function for direct product analysis
    """
    runner = PythonicResearchRunner()
    return runner.run_research_analysis_sync(asin_or_url) 