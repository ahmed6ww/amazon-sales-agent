"""
Test Research + Keyword API Endpoint
Runs the Research agent, then feeds its scraped_product and base_relevancy_scores
into the Keyword agent for categorization.
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from typing import Dict, Any, Optional
import logging

from app.core.config import settings


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/test-research-keywords")
async def start_test_research_and_keywords(
    asin_or_url: str = Form(...),
    marketplace: str = Form("US"),
    main_keyword: Optional[str] = Form(None),
    revenue_csv: Optional[UploadFile] = File(None),
    design_csv: Optional[UploadFile] = File(None),
):
    """
    Test endpoint mirroring the analyze flow through Research, then Keyword Agent.

    - Accepts optional Helium10 CSV uploads (revenue/design) for Research context
    - Scrapes listing and runs ResearchRunner with structured outputs
    - Extracts only scraped_product and base_relevancy_scores
    - Runs KeywordRunner using ONLY those two inputs
    """

    try:
        # Validate OpenAI setup
        if not settings.openai_configured:
            raise HTTPException(status_code=503, detail="OpenAI not configured")
        if not settings.USE_AI_AGENTS:
            raise HTTPException(status_code=503, detail="AI agents are disabled")

        if not asin_or_url.strip():
            raise HTTPException(status_code=400, detail="asin_or_url is required")

        # Optional CSV validation
        if revenue_csv and not revenue_csv.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Revenue file must be a CSV")
        if design_csv and not design_csv.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Design file must be a CSV")

        # Parse CSV files if provided
        revenue_data: list = []
        design_data: list = []
        if revenue_csv:
            from app.services.file_processing.csv_processor import parse_csv_bytes

            revenue_bytes = await revenue_csv.read()
            revenue_res = parse_csv_bytes(revenue_csv.filename, revenue_bytes)
            if not revenue_res.get("success"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to parse revenue CSV: {revenue_res.get('error')}",
                )
            revenue_data = revenue_res["data"]
        if design_csv:
            from app.services.file_processing.csv_processor import parse_csv_bytes

            design_bytes = await design_csv.read()
            design_res = parse_csv_bytes(design_csv.filename, design_bytes)
            if not design_res.get("success"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to parse design CSV: {design_res.get('error')}",
                )
            design_data = design_res["data"]

        # Auto-pick main keyword if not provided
        if not main_keyword and revenue_data:
            phrases = [
                row.get("Keyword Phrase", "").strip().lower()
                for row in revenue_data[:10]
                if row.get("Keyword Phrase")
            ]
            main_keyword = phrases[0] if phrases else None

        # Scrape and run Research Agent similar to analyze flow
        logger.info(f"🔬 Test Research+Keywords: scraping and analyzing {asin_or_url}")

        from app.local_agents.research.helper_methods import scrape_amazon_listing

        scrape_result = scrape_amazon_listing(asin_or_url)
        if not scrape_result.get("success"):
            raise HTTPException(
                status_code=500, detail=f"Scraping failed: {scrape_result.get('error')}"
            )
        scraped_data = scrape_result.get("data", {})

        from app.local_agents.research.runner import ResearchRunner

        runner = ResearchRunner()

        import asyncio

        def run_research_agent():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return runner.run_research(
                    asin_or_url=asin_or_url,
                    marketplace=marketplace,
                    main_keyword=main_keyword,
                    revenue_csv=revenue_data,
                    design_csv=design_data,
                )
            finally:
                loop.close()

        loop = asyncio.get_event_loop()
        research_ai_result = await loop.run_in_executor(None, run_research_agent)

        # Extract only the required inputs for Keyword Agent
        scraped_product = (research_ai_result or {}).get("scraped_product") or {}
        base_relevancy_scores = (research_ai_result or {}).get(
            "base_relevancy_scores", {}
        )

        # Run Keyword Agent - only with the two required inputs
        from app.local_agents.keyword.runner import KeywordRunner

        kw_runner = KeywordRunner()

        def run_keyword_agent():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return kw_runner.run_keyword_categorization(
                    scraped_product=scraped_product,
                    base_relevancy_scores=base_relevancy_scores,
                    marketplace=marketplace,
                    asin_or_url=asin_or_url,
                )
            finally:
                loop.close()

        keyword_ai_result = await loop.run_in_executor(None, run_keyword_agent)

        response = {
            "success": True,
            "asin": scraped_data.get("asin", asin_or_url),
            "marketplace": marketplace,
            "ai_analysis_keywords": keyword_ai_result,
            "source": "test_research_keywords_endpoint",
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test research+keywords (POST) error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
