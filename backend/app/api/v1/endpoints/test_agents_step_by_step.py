"""
Step-by-step agent testing endpoint
Allows testing each agent individually with sample data
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

class TestAgentRequest(BaseModel):
    agent_type: str  # "keyword", "scoring", "seo"
    test_data: Dict[str, Any]
    debug_mode: bool = True

@router.post("/test-agent-step")
async def test_agent_step(request: TestAgentRequest):
    """
    Test individual agents step by step with controlled data
    
    Usage:
    1. Test Keyword Agent with research output
    2. Test Scoring Agent with keyword output 
    3. Test SEO Agent with scoring output
    """
    
    try:
        if request.agent_type == "keyword":
            return await test_keyword_agent(request.test_data, request.debug_mode)
        elif request.agent_type == "scoring":
            return await test_scoring_agent(request.test_data, request.debug_mode)
        elif request.agent_type == "seo":
            return await test_seo_agent(request.test_data, request.debug_mode)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {request.agent_type}")
            
    except Exception as e:
        logger.error(f"Error testing {request.agent_type} agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def test_keyword_agent(test_data: Dict[str, Any], debug_mode: bool):
    """Test Keyword Agent with sample CSV data"""
    
    logger.info("🧪 Testing Keyword Agent...")
    
    try:
        from app.local_agents.keyword.runner import KeywordRunner
        
        # Create sample CSV data for testing
        sample_csv_data = test_data.get("csv_data", [
            {"Keyword": "philips tv", "Search Volume": "10000", "Competition": "0.5"},
            {"Keyword": "4k tv", "Search Volume": "50000", "Competition": "0.8"},
            {"Keyword": "smart tv", "Search Volume": "30000", "Competition": "0.7"},
            {"Keyword": "ambilight tv", "Search Volume": "5000", "Competition": "0.3"},
        ])
        
        keyword_runner = KeywordRunner()
        
        # Test the direct processing method first (no AI)
        logger.info("🔧 Testing direct keyword processing...")
        result = keyword_runner.run_direct_keyword_categorization(sample_csv_data)
        
        return {
            "success": True,
            "agent_type": "keyword",
            "method_used": "direct_processing",
            "input_keywords": len(sample_csv_data),
            "output_categories": len(result.keywords_by_category) if hasattr(result, 'keywords_by_category') else 0,
            "result": result.__dict__ if hasattr(result, '__dict__') else str(result),
            "debug_info": {
                "result_type": type(result).__name__,
                "result_attributes": dir(result) if hasattr(result, '__dict__') else []
            } if debug_mode else {}
        }
        
    except Exception as e:
        logger.error(f"Keyword Agent test failed: {e}")
        return {
            "success": False,
            "agent_type": "keyword", 
            "error": str(e),
            "debug_info": {
                "error_type": type(e).__name__
            } if debug_mode else {}
        }

async def test_scoring_agent(test_data: Dict[str, Any], debug_mode: bool):
    """Test Scoring Agent with sample keyword analysis result"""
    
    logger.info("🧪 Testing Scoring Agent...")
    
    try:
        from app.local_agents.scoring.runner import ScoringRunner
        from app.local_agents.keyword.schemas import KeywordAnalysisResult, KeywordCategory
        from pydantic import BaseModel
        
        # Create a sample KeywordAnalysisResult for testing
        class MockKeyword(BaseModel):
            keyword_phrase: str
            search_volume: int
            competition_score: float
            relevancy_score: float
            
        mock_keywords = [
            MockKeyword(keyword_phrase="philips tv", search_volume=10000, competition_score=0.5, relevancy_score=0.9),
            MockKeyword(keyword_phrase="4k tv", search_volume=50000, competition_score=0.8, relevancy_score=0.8),
        ]
        
        # Create a proper KeywordAnalysisResult
        keyword_analysis = KeywordAnalysisResult(
            total_keywords=2,
            keywords_by_category={
                KeywordCategory.PRIMARY: mock_keywords[:1],
                KeywordCategory.SECONDARY: mock_keywords[1:],
                KeywordCategory.LONG_TAIL: [],
                KeywordCategory.BRANDED: [],
                KeywordCategory.COMPETITOR: []
            },
            top_opportunities=["philips tv", "4k tv"],
            recommended_focus_areas=["primary keywords", "high volume terms"]
        )
        
        scoring_runner = ScoringRunner()
        
        # Test the direct processing method first
        logger.info("🔧 Testing direct scoring processing...")
        result = scoring_runner.run_direct_processing(keyword_analysis)
        
        return {
            "success": True,
            "agent_type": "scoring",
            "method_used": "direct_processing",
            "input_keywords": keyword_analysis.total_keywords,
            "result": result.__dict__ if hasattr(result, '__dict__') else str(result),
            "debug_info": {
                "result_type": type(result).__name__,
                "result_attributes": dir(result) if hasattr(result, '__dict__') else [],
                "input_type": type(keyword_analysis).__name__
            } if debug_mode else {}
        }
        
    except Exception as e:
        logger.error(f"Scoring Agent test failed: {e}")
        return {
            "success": False,
            "agent_type": "scoring",
            "error": str(e),
            "debug_info": {
                "error_type": type(e).__name__
            } if debug_mode else {}
        }

async def test_seo_agent(test_data: Dict[str, Any], debug_mode: bool):
    """Test SEO Agent with sample data"""
    
    logger.info("🧪 Testing SEO Agent...")
    
    try:
        from app.local_agents.seo.runner import SEORunner
        
        # Create sample data for SEO testing
        current_listing = test_data.get("current_listing", {
            "title": "PHILIPS 50 INCH AMBILIGHT PREMIUM GOOGLE TV",
            "bullets": ["4K UHD", "Smart TV", "Google TV"],
            "features": ["ambilight", "premium", "google tv"],
            "brand": "Philips",
            "category": "electronics"
        })
        
        safe_keywords = ["philips tv", "4k tv", "smart tv"]
        
        seo_runner = SEORunner()
        
        # Test the direct optimization method
        logger.info("🔧 Testing direct SEO optimization...")
        result = seo_runner.run_direct_optimization(
            current_listing=current_listing,
            critical_keywords=safe_keywords[:2],
            high_priority_keywords=safe_keywords[:1],
            medium_priority_keywords=safe_keywords[1:2],
            opportunity_keywords=safe_keywords,
            keyword_analysis={"total_keywords": len(safe_keywords)},
            scoring_analysis={
                "total_keywords_scored": len(safe_keywords),
                "keywords_processed": True
            },
            competitor_data={}
        )
        
        return {
            "success": True,
            "agent_type": "seo",
            "method_used": "direct_optimization",
            "input_keywords": len(safe_keywords),
            "result": result.__dict__ if hasattr(result, '__dict__') else str(result),
            "debug_info": {
                "result_type": type(result).__name__,
                "result_attributes": dir(result) if hasattr(result, '__dict__') else []
            } if debug_mode else {}
        }
        
    except Exception as e:
        logger.error(f"SEO Agent test failed: {e}")
        return {
            "success": False,
            "agent_type": "seo",
            "error": str(e),
            "debug_info": {
                "error_type": type(e).__name__
            } if debug_mode else {}
        }

@router.get("/sample-data/{agent_type}")
async def get_sample_data(agent_type: str):
    """Get sample test data for each agent type"""
    
    if agent_type == "keyword":
        return {
            "csv_data": [
                {"Keyword": "philips tv", "Search Volume": "10000", "Competition": "0.5"},
                {"Keyword": "4k tv", "Search Volume": "50000", "Competition": "0.8"},
                {"Keyword": "smart tv", "Search Volume": "30000", "Competition": "0.7"},
                {"Keyword": "ambilight tv", "Search Volume": "5000", "Competition": "0.3"},
                {"Keyword": "google tv", "Search Volume": "20000", "Competition": "0.6"}
            ]
        }
    elif agent_type == "scoring":
        return {
            "keyword_analysis": "Use output from keyword agent test"
        }
    elif agent_type == "seo":
        return {
            "current_listing": {
                "title": "PHILIPS 50 INCH AMBILIGHT PREMIUM GOOGLE TV",
                "bullets": ["4K UHD", "Smart TV", "Google TV"],
                "features": ["ambilight", "premium", "google tv"],
                "brand": "Philips",
                "category": "electronics"
            }
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid agent type") 