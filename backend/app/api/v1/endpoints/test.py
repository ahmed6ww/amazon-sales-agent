"""
Test endpoints for the Amazon Sales Agent API.

These endpoints are for testing and development purposes only.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.local_agents.keyword import KeywordRunner
from app.local_agents.scoring import ScoringRunner

router = APIRouter()


class KeywordAgentTestRequest(BaseModel):
    csv_data: List[Dict[str, Any]]
    asin: Optional[str] = None


class ScoringAgentTestRequest(BaseModel):
    csv_data: List[Dict[str, Any]]
    asin: Optional[str] = None
    product_attributes: Optional[Dict[str, Any]] = None
    competitor_data: Optional[Dict[str, Any]] = None


@router.post("/test/keyword-agent")
async def test_keyword_agent(request: KeywordAgentTestRequest):
    """
    Test the keyword agent with provided CSV data.
    """
    try:
        # Initialize keyword runner
        keyword_runner = KeywordRunner()
        
        # Run direct processing (faster for testing)
        result = keyword_runner.run_direct_processing(request.csv_data)
        
        # Check if keyword analysis was successful
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=f"Keyword analysis failed: {result.get('error', 'Unknown error')}")
        
        # Extract the KeywordAnalysisResult object
        keyword_analysis = result["result"]
        
        # Convert result to dict for JSON response
        # Extract all keywords from categories
        all_keywords = []
        for category, keywords in keyword_analysis.keywords_by_category.items():
            for kw in keywords:
                all_keywords.append({
                    "keyword_phrase": kw.keyword_phrase,
                    "category": kw.category or (kw.final_category.value if kw.final_category else category.value),
                    "search_volume": getattr(kw, 'search_volume', None),
                    "relevancy_score": getattr(kw, 'relevancy_score', 0.0),
                    "title_density": getattr(kw, 'title_density', None),
                    "top_10_competitors": len([r for r in kw.competitor_rankings.values() if r <= 10]) if hasattr(kw, 'competitor_rankings') else 0,
                    "total_competitors": len([r for r in kw.competitor_rankings.values() if r > 0]) if hasattr(kw, 'competitor_rankings') else 0,
                    "root_word": getattr(kw, 'root_word', ''),
                    "root_volume": getattr(kw, 'root_volume', None)
                })
        
        response_data = {
            "success": True,
            "total_keywords": keyword_analysis.total_keywords,
            "processing_timestamp": getattr(keyword_analysis, 'processing_timestamp', ''),
            "keywords": all_keywords,
            "category_stats": [
                {
                    "category": category.value,
                    "count": stats.keyword_count,
                    "avg_search_volume": stats.total_search_volume / max(stats.keyword_count, 1),
                    "avg_relevancy": stats.avg_relevancy_score,
                    "total_volume": stats.total_search_volume
                }
                for category, stats in keyword_analysis.category_stats.items()
            ],
            "root_word_analysis": [
                {
                    "root_word": rwa.root_word,
                    "related_keywords": rwa.related_keywords,
                    "total_search_volume": rwa.total_search_volume,
                    "keyword_count": rwa.keyword_count
                }
                for rwa in keyword_analysis.root_word_analysis
            ],
            "summary": {
                "total_keywords": keyword_analysis.total_keywords,
                "processed_keywords": keyword_analysis.processed_keywords,
                "filtered_keywords": keyword_analysis.filtered_keywords,
                "processing_time": keyword_analysis.processing_time,
                "data_quality_score": keyword_analysis.data_quality_score
            }
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword agent test failed: {str(e)}")


@router.post("/test/scoring-agent")
async def test_scoring_agent(request: ScoringAgentTestRequest):
    """
    Test the scoring agent with provided CSV data.
    """
    try:
        # Step 1: Run keyword analysis first
        keyword_runner = KeywordRunner()
        keyword_result = keyword_runner.run_direct_processing(request.csv_data)
        
        # Check if keyword analysis was successful
        if not keyword_result.get("success", False):
            raise HTTPException(status_code=500, detail=f"Keyword analysis failed: {keyword_result.get('error', 'Unknown error')}")
        
        # Extract the KeywordAnalysisResult object
        keyword_analysis = keyword_result["result"]
        
        # Step 2: Run scoring analysis
        scoring_runner = ScoringRunner()
        scoring_result = scoring_runner.run_direct_processing(keyword_analysis)
        
        # Convert result to dict for JSON response
        response_data = {
            "success": True,
            "total_keywords_analyzed": scoring_result.total_keywords_analyzed,
            "processing_timestamp": scoring_result.processing_timestamp,
            
            # Priority distribution
            "priority_distribution": {
                "critical": len(scoring_result.critical_keywords),
                "high": len(scoring_result.high_priority_keywords),
                "medium": len(scoring_result.medium_priority_keywords),
                "low": len(scoring_result.low_priority_keywords),
                "filtered": len(scoring_result.filtered_keywords)
            },
            
            # Top keywords by priority
            "critical_keywords": [
                {
                    "keyword_phrase": kw.keyword_phrase,
                    "category": kw.category,
                    "intent_score": int(kw.intent_score),
                    "priority_score": kw.priority_score,
                    "search_volume": kw.competition_metrics.search_volume,
                    "relevancy_score": kw.relevancy_score,
                    "competition_level": kw.competition_metrics.competition_level,
                    "opportunity_score": kw.competition_metrics.opportunity_score,
                    "business_value": kw.business_value,
                    "opportunity_type": kw.opportunity_type,
                    "root_word": kw.root_word
                }
                for kw in scoring_result.critical_keywords
            ],
            
            "high_priority_keywords": [
                {
                    "keyword_phrase": kw.keyword_phrase,
                    "category": kw.category,
                    "intent_score": int(kw.intent_score),
                    "priority_score": kw.priority_score,
                    "search_volume": kw.competition_metrics.search_volume,
                    "relevancy_score": kw.relevancy_score,
                    "competition_level": kw.competition_metrics.competition_level,
                    "opportunity_score": kw.competition_metrics.opportunity_score,
                    "business_value": kw.business_value,
                    "opportunity_type": kw.opportunity_type,
                    "root_word": kw.root_word
                }
                for kw in scoring_result.high_priority_keywords
            ],
            
            # Top opportunities
            "top_opportunities": [
                {
                    "keyword_phrase": kw.keyword_phrase,
                    "category": kw.category,
                    "intent_score": int(kw.intent_score),
                    "priority_score": kw.priority_score,
                    "search_volume": kw.competition_metrics.search_volume,
                    "opportunity_score": kw.competition_metrics.opportunity_score,
                    "opportunity_type": kw.opportunity_type,
                    "competition_level": kw.competition_metrics.competition_level,
                    "business_value": kw.business_value
                }
                for kw in scoring_result.top_opportunities
            ],
            
            # Category performance
            "category_stats": [
                {
                    "category_name": stat.category_name,
                    "total_keywords": stat.total_keywords,
                    "avg_intent_score": stat.avg_intent_score,
                    "avg_priority_score": stat.avg_priority_score,
                    "total_search_volume": stat.total_search_volume,
                    "high_priority_count": stat.high_priority_count,
                    "critical_priority_count": stat.critical_priority_count
                }
                for stat in scoring_result.category_stats
            ],
            
            # Summary statistics
            "summary": scoring_result.summary,
            
            # Additional insights
            "insights": {
                "avg_priority_score": sum(kw.priority_score for kw in scoring_result.scored_keywords) / len(scoring_result.scored_keywords) if scoring_result.scored_keywords else 0,
                "high_value_keywords": len([kw for kw in scoring_result.scored_keywords if kw.priority_score > 70]),
                "quick_wins": len([kw for kw in scoring_result.scored_keywords if kw.competition_metrics.opportunity_score > 80 and kw.competition_metrics.competition_level == "low"]),
                "total_search_volume": sum(kw.competition_metrics.search_volume or 0 for kw in scoring_result.scored_keywords)
            }
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring agent test failed: {str(e)}")


@router.get("/test/status")
async def test_status():
    """
    Check the status of test endpoints.
    """
    return {
        "status": "healthy",
        "available_tests": [
            "keyword-agent",
            "scoring-agent"
        ],
        "message": "Test endpoints are ready"
    } 