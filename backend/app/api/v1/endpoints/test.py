from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from app.local_agents.keyword.runner import KeywordRunner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class KeywordAgentTestRequest(BaseModel):
    csv_data: List[Dict[str, Any]]
    asin: Optional[str] = None
    product_attributes: Optional[Dict[str, Any]] = None


@router.post("/test/keyword-agent")
async def test_keyword_agent(request: KeywordAgentTestRequest):
    """
    Test endpoint for the Keyword Agent.
    Accepts CSV data and returns keyword analysis results.
    """
    try:
        logger.info(f"Testing Keyword Agent with {len(request.csv_data)} keywords")
        
        # Initialize the keyword runner
        runner = KeywordRunner()
        
        # Run direct processing (faster for testing)
        result = runner.run_direct_processing(request.csv_data)
        
        if not result["success"]:
            logger.error(f"Keyword Agent processing failed: {result['error']}")
            raise HTTPException(status_code=500, detail=f"Keyword processing failed: {result['error']}")
        
        # Convert the result to a JSON-serializable format
        analysis_result = result["result"]
        
        # Convert enum values to strings and format the response
        formatted_result = {
            "total_keywords": analysis_result.total_keywords,
            "processed_keywords": analysis_result.processed_keywords,
            "filtered_keywords": analysis_result.filtered_keywords,
            "processing_time": analysis_result.processing_time,
            "data_quality_score": analysis_result.data_quality_score,
            "warnings": analysis_result.warnings,
            "top_opportunities": analysis_result.top_opportunities,
            "coverage_gaps": analysis_result.coverage_gaps,
            "recommended_focus_areas": analysis_result.recommended_focus_areas,
            "category_stats": {
                category.value: {
                    "keyword_count": stats.keyword_count,
                    "total_search_volume": stats.total_search_volume,
                    "avg_relevancy_score": stats.avg_relevancy_score,
                    "avg_intent_score": stats.avg_intent_score,
                    "top_keywords": stats.top_keywords
                }
                for category, stats in analysis_result.category_stats.items()
            },
            "keywords_by_category": {
                category.value: [
                    {
                        "keyword_phrase": kw.keyword_phrase,
                        "category": kw.category,
                        "final_category": kw.final_category.value if kw.final_category else None,
                        "search_volume": kw.search_volume,
                        "relevancy_score": kw.relevancy_score,
                        "title_density": kw.title_density,
                        "cpr": kw.cpr,
                        "root_word": kw.root_word,
                        "broad_search_volume": kw.broad_search_volume,
                        "is_zero_title_density": kw.is_zero_title_density,
                        "is_derivative": kw.is_derivative,
                        "intent_score": kw.intent_score,
                        "cerebro_iq_score": kw.cerebro_iq_score,
                        "competing_products": kw.competing_products
                    }
                    for kw in keywords
                ]
                for category, keywords in analysis_result.keywords_by_category.items()
            },
            "root_word_analysis": [
                {
                    "root_word": rwa.root_word,
                    "related_keywords": rwa.related_keywords,
                    "total_search_volume": rwa.total_search_volume,
                    "avg_relevancy_score": rwa.avg_relevancy_score,
                    "keyword_count": rwa.keyword_count,
                    "best_keyword": rwa.best_keyword,
                    "categories_present": [cat.value for cat in rwa.categories_present]
                }
                for rwa in analysis_result.root_word_analysis
            ]
        }
        
        logger.info(f"Keyword Agent test completed successfully. Processed {analysis_result.processed_keywords} keywords in {analysis_result.processing_time:.3f}s")
        
        return {
            "success": True,
            "result": formatted_result,
            "processing_details": result["processing_details"]
        }
        
    except Exception as e:
        logger.exception(f"Unexpected error in keyword agent test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/test/status")
async def test_status():
    """
    Simple status endpoint to check if the test API is working.
    """
    return {
        "status": "ok",
        "message": "Test API is working",
        "available_tests": [
            "keyword-agent"
        ]
    } 