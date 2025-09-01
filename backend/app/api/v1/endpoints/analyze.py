"""
Main Analysis Endpoint

Production endpoint for the complete agentic workflow:
Research Agent → Keyword Agent → Scoring Agent → SEO Agent
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import uuid
from datetime import datetime

from app.local_agents.research import ResearchRunner
from app.local_agents.keyword import KeywordRunner
from app.local_agents.scoring import ScoringRunner
from app.local_agents.seo import SEORunner
from app.services.file_processing.csv_processor import parse_csv_bytes
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for analysis results (in production, use Redis/Database)
analysis_results = {}

class AnalysisRequest(BaseModel):
    asin_or_url: str
    marketplace: str = "US"
    main_keyword: Optional[str] = None


class AnalysisStatus(BaseModel):
    analysis_id: str
    status: str  # "pending", "processing", "completed", "failed"
    current_step: str
    progress: int  # 0-100
    message: str
    started_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    results: Optional[Dict[str, Any]] = None


@router.post("/analyze")
async def start_analysis(
    background_tasks: BackgroundTasks,
    asin_or_url: str = Form(...),
    marketplace: str = Form("US"),
    main_keyword: Optional[str] = Form(None),
    revenue_csv: UploadFile = File(...),
    design_csv: UploadFile = File(...)
):
    """
    Start the complete agentic analysis workflow.
    
    This endpoint orchestrates all agents in sequence:
    1. Research Agent: Analyze product listing and CSVs
    2. Keyword Agent: Categorize and analyze keywords
    3. Scoring Agent: Score and prioritize keywords
    4. SEO Agent: Generate optimization recommendations
    """
    
    # Generate unique analysis ID
    analysis_id = str(uuid.uuid4())
    
    # Validate files
    if not revenue_csv.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Revenue file must be a CSV")
    if not design_csv.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Design file must be a CSV")
    
    # Initialize analysis status
    analysis_results[analysis_id] = AnalysisStatus(
        analysis_id=analysis_id,
        status="pending",
        current_step="initializing",
        progress=0,
        message="Analysis queued for processing",
        started_at=datetime.now().isoformat()
    )
    
    # Start background processing
    background_tasks.add_task(
        run_complete_analysis,
        analysis_id,
        asin_or_url,
        marketplace,
        main_keyword,
        await revenue_csv.read(),
        revenue_csv.filename,
        await design_csv.read(),
        design_csv.filename
    )
    
    return {
        "success": True,
        "analysis_id": analysis_id,
        "message": "Analysis started successfully",
        "status_url": f"/api/v1/analyze/{analysis_id}/status",
        "results_url": f"/api/v1/analyze/{analysis_id}/results"
    }


@router.get("/analyze/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """Get the current status of an analysis."""
    
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_results[analysis_id]


@router.get("/analyze/{analysis_id}/results")
async def get_analysis_results(analysis_id: str):
    """Get the complete results of an analysis."""
    
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    status = analysis_results[analysis_id]
    
    if status.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Analysis not completed. Current status: {status.status}"
        )
    
    # Return just the results object, not the entire status
    if hasattr(status, 'results') and status.results:
        return {"success": True, "results": status.results}
    else:
        raise HTTPException(status_code=404, detail="Results not found")


async def run_complete_analysis(
    analysis_id: str,
    asin_or_url: str,
    marketplace: str,
    main_keyword: Optional[str],
    revenue_csv_data: bytes,
    revenue_filename: str,
    design_csv_data: bytes,
    design_filename: str
):
    """
    Run the complete analysis workflow with all agents.
    """
    
    try:
        # Update status
        analysis_results[analysis_id].status = "processing"
        analysis_results[analysis_id].current_step = "parsing_data"
        analysis_results[analysis_id].progress = 5
        analysis_results[analysis_id].message = "Parsing uploaded CSV files"
        
        # Step 1: Parse CSV files
        revenue_csv_result = parse_csv_bytes(revenue_filename, revenue_csv_data)
        design_csv_result = parse_csv_bytes(design_filename, design_csv_data)
        
        if not revenue_csv_result.get("success"):
            raise Exception(f"Failed to parse revenue CSV: {revenue_csv_result.get('error')}")
        
        if not design_csv_result.get("success"):
            raise Exception(f"Failed to parse design CSV: {design_csv_result.get('error')}")
        
        revenue_data = revenue_csv_result["data"]
        design_data = design_csv_result["data"]
        
        # Update status
        analysis_results[analysis_id].current_step = "research_analysis"
        analysis_results[analysis_id].progress = 15
        analysis_results[analysis_id].message = f"Running research analysis on {asin_or_url}"
        
        # Step 2: Research Agent - Analyze product listing
        research_runner = ResearchRunner()
        
        # Extract main keyword if not provided
        if not main_keyword and revenue_data:
            keyword_phrases = [row.get('Keyword Phrase', '').lower().strip() for row in revenue_data[:10] if row.get('Keyword Phrase')]
            main_keyword = keyword_phrases[0] if keyword_phrases else None
        
        # Use AI Research Agent with Pythonic approach if OpenAI is configured
        if settings.openai_configured and settings.USE_AI_AGENTS:
            logger.info(f"Using Pythonic AI Research Agent for {asin_or_url}")
            try:
                # Import the new Pythonic runner
                from app.local_agents.research.pythonic_runner import PythonicResearchRunner
                
                pythonic_runner = PythonicResearchRunner()
                research_ai_result = pythonic_runner.run_research_analysis_sync(asin_or_url)
                
                if research_ai_result.get("success"):
                    research_result = {
                        "success": True,
                        "asin": asin_or_url,
                        "marketplace": marketplace,
                        "main_keyword": main_keyword,
                        "revenue_competitors": len(revenue_data),
                        "design_competitors": len(design_data),
                        "ai_analysis": research_ai_result.get("analysis", "Analysis completed"),
                        "raw_data": research_ai_result.get("raw_data", {}),
                        "structured_data": research_ai_result.get("structured_data", {}),
                        "agent_used": research_ai_result.get("agent_used", "Pythonic Research Agent"),
                        "source": "pythonic_ai_agent"
                    }
                else:
                    raise Exception(f"Pythonic Research failed: {research_ai_result.get('error')}")
            except Exception as e:
                logger.warning(f"Pythonic Research Agent failed: {e}, falling back to inference")
                research_result = _create_fallback_research_result(asin_or_url, marketplace, main_keyword, revenue_data, design_data)
        else:
            logger.info("OpenAI not configured or AI agents disabled, using inference-based research")
            research_result = _create_fallback_research_result(asin_or_url, marketplace, main_keyword, revenue_data, design_data)
        
        # Update status
        analysis_results[analysis_id].current_step = "keyword_analysis"
        analysis_results[analysis_id].progress = 35
        analysis_results[analysis_id].message = f"Analyzing {len(revenue_data)} revenue keywords"
        
        # Step 3: Keyword Agent - Process revenue competitors
        keyword_runner = KeywordRunner()
        
        # Combine both CSV datasets for comprehensive analysis
        combined_data = revenue_data + design_data
        
        # Use AI Keyword Agent if configured, otherwise use direct processing
        if settings.openai_configured and settings.USE_AI_AGENTS:
            logger.info(f"Using AI Keyword Agent for {len(combined_data)} keywords")
            try:
                keyword_result = keyword_runner.run_full_keyword_analysis(combined_data)
                if not keyword_result.get("success"):
                    raise Exception(f"AI Keyword analysis failed: {keyword_result.get('error')}")
            except Exception as e:
                logger.warning(f"AI Keyword Agent failed: {e}, falling back to direct processing")
                keyword_result = keyword_runner.run_direct_processing(combined_data)
        else:
            logger.info("Using direct keyword processing")
            keyword_result = keyword_runner.run_direct_processing(combined_data)
        
        if not keyword_result.get("success"):
            raise Exception(f"Keyword analysis failed: {keyword_result.get('error')}")
        
        keyword_analysis = keyword_result["result"]
        
        # Update status
        analysis_results[analysis_id].current_step = "scoring_analysis"
        analysis_results[analysis_id].progress = 60
        analysis_results[analysis_id].message = f"Scoring and prioritizing {keyword_analysis.total_keywords} keywords"
        
        # Step 4: Scoring Agent - Score and prioritize keywords
        scoring_runner = ScoringRunner()
        
        # Use AI Scoring Agent if configured, otherwise use direct processing
        if settings.openai_configured and settings.USE_AI_AGENTS:
            logger.info(f"Using AI Scoring Agent for {keyword_analysis.total_keywords} keywords")
            try:
                scoring_result = scoring_runner.run_full_scoring_analysis(keyword_analysis)
                if not scoring_result:
                    raise Exception("AI Scoring analysis returned empty result")
            except Exception as e:
                logger.warning(f"AI Scoring Agent failed: {e}, falling back to direct processing")
                scoring_result = scoring_runner.run_direct_processing(keyword_analysis)
        else:
            logger.info("Using direct scoring processing")
            scoring_result = scoring_runner.run_direct_processing(keyword_analysis)
        
        # Update status
        analysis_results[analysis_id].current_step = "seo_optimization"
        analysis_results[analysis_id].progress = 80
        analysis_results[analysis_id].message = "Generating SEO optimization recommendations"
        
        # Step 5: SEO Agent - Generate comprehensive recommendations
        seo_runner = SEORunner()
        
        # Prepare SEO optimization data
        current_listing = {
            "title": research_result.get("product_attributes", {}).get("title", main_keyword.title() if main_keyword else "Premium Product Title"),
            "bullets": [],
            "features": ["high-quality", "durable", "versatile"],
            "brand": research_result.get("product_attributes", {}).get("brand", "Premium Brand"),
            "category": research_result.get("product_attributes", {}).get("category", "general")
        }
        
        # Use AI SEO Agent if configured, otherwise use direct optimization
        if settings.openai_configured and settings.USE_AI_AGENTS:
            logger.info("Using AI SEO Agent for optimization recommendations")
            try:
                seo_analysis = seo_runner.run_full_seo_optimization(
                    product_info=current_listing,
                    keyword_analysis=keyword_analysis.__dict__,
                    scoring_analysis=scoring_result.__dict__
                )
                if not seo_analysis:
                    raise Exception("AI SEO analysis returned empty result")
            except Exception as e:
                logger.warning(f"AI SEO Agent failed: {e}, falling back to direct optimization")
                seo_analysis = seo_runner.run_direct_optimization(
                    current_listing=current_listing,
                    critical_keywords=[kw.keyword_phrase for kw in scoring_result.critical_keywords[:5]],
                    high_priority_keywords=[kw.keyword_phrase for kw in scoring_result.high_priority_keywords[:8]],
                    medium_priority_keywords=[kw.keyword_phrase for kw in scoring_result.medium_priority_keywords[:10]],
                    opportunity_keywords=[kw.keyword_phrase for kw in scoring_result.top_opportunities[:10]],
                    keyword_analysis={"total_keywords": keyword_analysis.total_keywords},
                    scoring_analysis={
                        "critical_keywords": [kw.keyword_phrase for kw in scoring_result.critical_keywords],
                        "high_priority_keywords": [kw.keyword_phrase for kw in scoring_result.high_priority_keywords],
                        "opportunity_keywords": [kw.keyword_phrase for kw in scoring_result.top_opportunities]
                    },
                    competitor_data={}
                )
        else:
            logger.info("Using direct SEO optimization")
            seo_analysis = seo_runner.run_direct_optimization(
                current_listing=current_listing,
                critical_keywords=[kw.keyword_phrase for kw in scoring_result.critical_keywords[:5]],
                high_priority_keywords=[kw.keyword_phrase for kw in scoring_result.high_priority_keywords[:8]],
                medium_priority_keywords=[kw.keyword_phrase for kw in scoring_result.medium_priority_keywords[:10]],
                opportunity_keywords=[kw.keyword_phrase for kw in scoring_result.top_opportunities[:10]],
                keyword_analysis={"total_keywords": keyword_analysis.total_keywords},
                scoring_analysis={
                    "critical_keywords": [kw.keyword_phrase for kw in scoring_result.critical_keywords],
                    "high_priority_keywords": [kw.keyword_phrase for kw in scoring_result.high_priority_keywords],
                    "opportunity_keywords": [kw.keyword_phrase for kw in scoring_result.top_opportunities]
                },
                competitor_data={}
            )
        
        # Convert SEO analysis to response format
        seo_recommendations = {
            "title_optimization": {
                "current_title": seo_analysis.title_optimization.current_title,
                "recommended_title": seo_analysis.title_optimization.recommended_title,
                "keywords_added": seo_analysis.title_optimization.keywords_added,
                "improvement_score": seo_analysis.title_optimization.improvement_score
            },
            "bullet_points": {
                "recommended_bullets": seo_analysis.bullet_optimization.recommended_bullets,
                "keywords_coverage": seo_analysis.bullet_optimization.keywords_coverage
            },
            "backend_keywords": {
                "recommended_keywords": seo_analysis.backend_optimization.recommended_keywords,
                "character_count": seo_analysis.backend_optimization.character_count,
                "coverage_improvement": seo_analysis.backend_optimization.coverage_improvement
            },
            "content_gaps": [gap.recommended_content for gap in seo_analysis.content_gaps[:5]],
            "competitive_advantages": [adv.description for adv in seo_analysis.competitive_advantages[:3]]
        }
        
        # Update status
        analysis_results[analysis_id].current_step = "finalizing"
        analysis_results[analysis_id].progress = 95
        analysis_results[analysis_id].message = "Finalizing results"
        
        # Compile final results
        final_results = {
            "analysis_id": analysis_id,
            "input": {
                "asin_or_url": asin_or_url,
                "marketplace": marketplace,
                "main_keyword": main_keyword,
                "revenue_keywords_count": len(revenue_data),
                "design_keywords_count": len(design_data)
            },
            "research_analysis": research_result,
            "keyword_analysis": {
                "total_keywords": keyword_analysis.total_keywords,
                "processed_keywords": keyword_analysis.processed_keywords,
                "categories_found": len(keyword_analysis.category_stats),
                "processing_time": keyword_analysis.processing_time,
                "data_quality_score": keyword_analysis.data_quality_score
            },
            "scoring_analysis": {
                "total_analyzed": scoring_result.total_keywords_analyzed,
                "priority_distribution": {
                    "critical": len(scoring_result.critical_keywords),
                    "high": len(scoring_result.high_priority_keywords),
                    "medium": len(scoring_result.medium_priority_keywords),
                    "low": len(scoring_result.low_priority_keywords),
                    "filtered": len(scoring_result.filtered_keywords)
                },
                "top_critical_keywords": [
                    {
                        "keyword": kw.keyword_phrase,
                        "intent_score": int(kw.intent_score),
                        "priority_score": kw.priority_score,
                        "search_volume": kw.competition_metrics.search_volume,
                        "opportunity_score": kw.competition_metrics.opportunity_score
                    }
                    for kw in scoring_result.critical_keywords[:10]
                ],
                "top_opportunities": [
                    {
                        "keyword": kw.keyword_phrase,
                        "opportunity_score": kw.competition_metrics.opportunity_score,
                        "opportunity_type": kw.opportunity_type,
                        "search_volume": kw.competition_metrics.search_volume
                    }
                    for kw in scoring_result.top_opportunities[:10]
                ]
            },
            "seo_recommendations": seo_recommendations,
            "summary": {
                "total_processing_time": "2.5 minutes",  # Would be calculated
                "confidence_score": 85,  # Would be calculated
                "actionable_keywords": len(scoring_result.critical_keywords) + len(scoring_result.high_priority_keywords),
                "quick_wins": len([kw for kw in scoring_result.top_opportunities if kw.competition_metrics.opportunity_score > 80])
            }
        }
        
        # Complete successfully
        analysis_results[analysis_id].status = "completed"
        analysis_results[analysis_id].current_step = "completed"
        analysis_results[analysis_id].progress = 100
        analysis_results[analysis_id].message = "Analysis completed successfully"
        analysis_results[analysis_id].completed_at = datetime.now().isoformat()
        
        # Store results (in production, save to database)
        analysis_results[analysis_id].results = final_results
        
    except Exception as e:
        # Handle errors
        analysis_results[analysis_id].status = "failed"
        analysis_results[analysis_id].error = str(e)
        analysis_results[analysis_id].message = f"Analysis failed: {str(e)}"
        analysis_results[analysis_id].completed_at = datetime.now().isoformat()


def generate_seo_recommendations(scoring_result, product_attributes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate SEO optimization recommendations based on scoring results.
    This is a placeholder - will be replaced with proper SEO Agent.
    """
    
    critical_keywords = [kw.keyword_phrase for kw in scoring_result.critical_keywords[:5]]
    high_priority_keywords = [kw.keyword_phrase for kw in scoring_result.high_priority_keywords[:10]]
    
    return {
        "title_optimization": {
            "current_title": product_attributes.get("title", "Current Product Title"),
            "recommended_title": f"Optimized Title with {', '.join(critical_keywords[:3])}",
            "keywords_added": critical_keywords[:3],
            "improvement_score": 85
        },
        "bullet_points": {
            "recommended_bullets": [
                f"Premium quality featuring {critical_keywords[0] if critical_keywords else 'key features'}",
                f"Perfect for {critical_keywords[1] if len(critical_keywords) > 1 else 'your needs'}",
                f"Includes {critical_keywords[2] if len(critical_keywords) > 2 else 'essential features'}",
                f"Compatible with {high_priority_keywords[0] if high_priority_keywords else 'various uses'}",
                f"Easy to use {high_priority_keywords[1] if len(high_priority_keywords) > 1 else 'design'}"
            ],
            "keywords_coverage": len(critical_keywords) + len(high_priority_keywords[:5])
        },
        "backend_keywords": {
            "recommended_keywords": high_priority_keywords[:20],
            "character_count": sum(len(kw) + 1 for kw in high_priority_keywords[:20]),
            "coverage_improvement": "45%"
        },
        "content_gaps": [
            f"Add content about {kw.keyword_phrase}" 
            for kw in scoring_result.top_opportunities[:5]
        ],
        "competitive_advantages": [
            "Focus on high-opportunity keywords with low competition",
            "Target design-specific features for differentiation",
            "Leverage untapped market opportunities"
        ]
    }


@router.delete("/analyze/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete an analysis and its results."""
    
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    del analysis_results[analysis_id]
    
    return {"success": True, "message": "Analysis deleted successfully"}


@router.get("/analyze")
async def list_analyses():
    """List all analyses (for admin/debugging)."""
    
    return {
        "analyses": [
            {
                "analysis_id": aid,
                "status": status.status,
                "current_step": status.current_step,
                "progress": status.progress,
                "started_at": status.started_at,
                "completed_at": status.completed_at
            }
            for aid, status in analysis_results.items()
        ]
    }


@router.get("/analyze/status")
async def get_system_status():
    """Get system status and configuration for debugging."""
    
    return {
        "ai_configuration": {
            "openai_configured": settings.openai_configured,
            "openai_api_key_present": bool(settings.OPENAI_API_KEY),
            "openai_api_key_length": len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0,
            "use_ai_agents": settings.USE_AI_AGENTS,
            "fallback_to_direct": settings.FALLBACK_TO_DIRECT,
            "openai_model": settings.OPENAI_MODEL,
            "openai_temperature": settings.OPENAI_TEMPERATURE
        },
        "agent_status": {
            "research_agent": "AI enabled" if settings.openai_configured and settings.USE_AI_AGENTS else "Direct processing only",
            "keyword_agent": "AI enabled" if settings.openai_configured and settings.USE_AI_AGENTS else "Direct processing only", 
            "scoring_agent": "AI enabled" if settings.openai_configured and settings.USE_AI_AGENTS else "Direct processing only",
            "seo_agent": "AI enabled" if settings.openai_configured and settings.USE_AI_AGENTS else "Direct processing only"
        },
        "current_analyses": len(analysis_results),
        "cors_origins": settings.get_cors_origins()
    }


def _create_fallback_research_result(asin_or_url: str, marketplace: str, main_keyword: str, revenue_data: list, design_data: list) -> dict:
    """Create fallback research result when AI agent is not available"""
    
    # Infer product category from keywords dynamically
    inferred_category = "general"
    if revenue_data:
        # Analyze keywords to determine product category
        all_keywords = " ".join([row.get('Keyword Phrase', '').lower() for row in revenue_data[:20]])
        
        # Category inference logic based on keyword patterns
        if any(word in all_keywords for word in ['baby', 'infant', 'toddler', 'newborn', 'nursery']):
            inferred_category = "baby_products"
        elif any(word in all_keywords for word in ['kitchen', 'cooking', 'food', 'recipe', 'utensil']):
            inferred_category = "kitchen_dining"
        elif any(word in all_keywords for word in ['home', 'house', 'decor', 'furniture', 'living']):
            inferred_category = "home_garden"
        elif any(word in all_keywords for word in ['beauty', 'skincare', 'makeup', 'cosmetic', 'hair']):
            inferred_category = "beauty_personal_care"
        elif any(word in all_keywords for word in ['electronic', 'tech', 'device', 'gadget', 'computer']):
            inferred_category = "electronics"
        elif any(word in all_keywords for word in ['clothing', 'shirt', 'dress', 'pants', 'fashion']):
            inferred_category = "clothing_shoes_jewelry"
        elif any(word in all_keywords for word in ['sport', 'fitness', 'exercise', 'workout', 'athletic']):
            inferred_category = "sports_outdoors"
        elif any(word in all_keywords for word in ['book', 'read', 'novel', 'author', 'literature']):
            inferred_category = "books"
        elif any(word in all_keywords for word in ['toy', 'game', 'play', 'children', 'kids']):
            inferred_category = "toys_games"
        elif any(word in all_keywords for word in ['health', 'supplement', 'vitamin', 'wellness', 'medical']):
            inferred_category = "health_household"
    
    # Create product title based on main keyword
    if main_keyword:
        inferred_title = f"{main_keyword.title()} - High Quality Amazon Product"
    else:
        inferred_title = "Premium Amazon Product - High Quality"
    
    # Try to infer brand from ASIN pattern or use generic
    inferred_brand = "Premium Brand"
    if asin_or_url.startswith('B0'):
        inferred_brand = "Amazon Brand"
    
    return {
        "success": True,
        "asin": asin_or_url,
        "marketplace": marketplace,
        "main_keyword": main_keyword,
        "revenue_competitors": len(revenue_data),
        "design_competitors": len(design_data),
        "product_attributes": {
            "category": inferred_category,
            "brand": inferred_brand,
            "title": inferred_title,
        },
        "source": "inference_fallback"
    } 