"""
Test Research API Endpoint
Dynamic testing of the Pythonic research agent with any Amazon URL
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/test-research")
async def test_research_agent(
    url: str = Query(..., description="Amazon product URL to analyze"),
    include_raw_data: bool = Query(False, description="Include raw scraped data in response"),
    include_structured_data: bool = Query(True, description="Include structured data in response")
) -> Dict[str, Any]:
    """
    Test endpoint for the Pythonic Research Agent
    
    **Usage Examples:**
    - `/api/v1/test-research?url=https://www.amazon.ae/Apple-MYQY3ZE-A-EarPods-USB-C/dp/B0DD413Q9J`
    - `/api/v1/test-research?url=https://www.amazon.com/dp/B08KT2Z93D&include_raw_data=true`
    
    **Returns:**
    - Full research analysis
    - Data quality assessment  
    - MVP source extraction results
    - Optional raw/structured data
    """
    
    try:
        # Validate URL
        if not url.strip():
            raise HTTPException(status_code=400, detail="URL parameter is required")
        
        if "amazon." not in url.lower():
            raise HTTPException(status_code=400, detail="Please provide a valid Amazon product URL")
        
        # Check if OpenAI is configured
        if not settings.openai_configured:
            raise HTTPException(
                status_code=503, 
                detail="OpenAI is not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        if not settings.USE_AI_AGENTS:
            raise HTTPException(
                status_code=503,
                detail="AI agents are disabled. Please set USE_AI_AGENTS=true environment variable."
            )
        
        logger.info(f"Testing research agent with URL: {url}")
        
        # Import and use the Pythonic research runner
        from app.local_agents.research.pythonic_runner import PythonicResearchRunner
        
        runner = PythonicResearchRunner()
        # Use the async method directly since FastAPI is async
        result = await runner.run_research_analysis(url)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Research analysis failed: {result.get('error', 'Unknown error')}"
            )
        
        # Prepare the response
        response = {
            "success": True,
            "url": url,
            "agent_used": result.get("agent_used", "ResearchAnalyst"),
            "analysis": result.get("analysis", ""),
            "metadata": {
                "analysis_length": len(result.get("analysis", "")),
                "has_raw_data": bool(result.get("raw_data")),
                "has_structured_data": bool(result.get("structured_data")),
                "data_source": "real_data" if result.get("raw_data") else "no_data"
            }
        }
        
        # Add optional data based on query parameters
        if include_raw_data and result.get("raw_data"):
            response["raw_data"] = result["raw_data"]
        
        if include_structured_data and result.get("structured_data"):
            response["structured_data"] = result["structured_data"]
        
        # Add analysis summary
        analysis_text = result.get("analysis", "")
        response["analysis_summary"] = {
            "title_extracted": "TITLE" in analysis_text and "Yes" in analysis_text,
            "images_extracted": "IMAGES" in analysis_text and "Yes" in analysis_text,
            "aplus_extracted": "A+ CONTENT" in analysis_text and "Yes" in analysis_text,
            "reviews_extracted": "REVIEWS" in analysis_text and "Yes" in analysis_text,
            "qa_extracted": "Q&A SECTION" in analysis_text and "Yes" in analysis_text,
            "overall_quality": _assess_overall_quality(analysis_text)
        }
        
        logger.info(f"Research test completed successfully for {url}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test research endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/test-research/status")
async def test_research_status() -> Dict[str, Any]:
    """
    Check the status of research agent configuration
    """
    return {
        "openai_configured": settings.openai_configured,
        "use_ai_agents": settings.USE_AI_AGENTS,
        "openai_model": getattr(settings, 'OPENAI_MODEL', 'gpt-4'),
        "ready_for_research": settings.openai_configured and settings.USE_AI_AGENTS,
        "pythonic_runner_available": True
    }


@router.get("/test-research/examples")
async def test_research_examples() -> Dict[str, Any]:
    """
    Get example URLs for testing the research agent
    """
    return {
        "example_urls": [
            "https://www.amazon.ae/Apple-MYQY3ZE-A-EarPods-USB-C/dp/B0DD413Q9J",
            "https://www.amazon.ae/PNY-GeForce-RTXTM-Triple-Graphics/dp/B0DYPFGL88/",
            "https://www.amazon.com/dp/B08KT2Z93D",
            "https://www.amazon.com/Apple-AirPods-Pro-2nd-Generation/dp/B0BDHWDR12"
        ],
        "usage_instructions": [
            "Copy any example URL",
            "Use: /api/v1/test-research?url=YOUR_URL",
            "Add &include_raw_data=true for raw scraped data",
            "Add &include_structured_data=true for structured data (default)",
            "Check OpenAI dashboard for traces after each test"
        ],
        "expected_results": {
            "mvp_sources": ["TITLE", "IMAGES", "A+ CONTENT", "REVIEWS", "Q&A SECTION"],
            "data_quality_assessment": ["Excellent", "Good", "Fair", "Poor"],
            "trace_generation": "Clean OpenAI traces without function tool complexity"
        }
    }


def _assess_overall_quality(analysis_text: str) -> str:
    """Assess the overall quality based on analysis text"""
    if not analysis_text:
        return "Poor"
    
    quality_indicators = analysis_text.count("Excellent") + analysis_text.count("Good")
    poor_indicators = analysis_text.count("Poor") + analysis_text.count("Fair")
    
    if quality_indicators > poor_indicators:
        return "Good"
    elif quality_indicators == poor_indicators:
        return "Fair"
    else:
        return "Poor" 