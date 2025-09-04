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
    3. Scoring Agent: Score and prioritize keywords (COMMENTED OUT)
    4. SEO Agent: Generate optimization recommendations (COMMENTED OUT)
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
    Run the complete analysis workflow with Research + Keyword agents only.
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
        
        # 🚀 Production-Ready MVP Scraper → Research Agent Pipeline
        if settings.openai_configured and settings.USE_AI_AGENTS:
            logger.info(f"🚀 Using Production MVP Scraper → Research Agent Pipeline for {asin_or_url}")
            try:
                # Step 1: Get clean MVP data using our production scraper
                from app.local_agents.research.helper_methods import scrape_amazon_listing
                
                logger.info(f"📊 Step 1: Scraping MVP data...")
                scrape_result = scrape_amazon_listing(asin_or_url)
                
                if not scrape_result.get("success"):
                    raise Exception(f"MVP scraping failed: {scrape_result.get('error')}")
                
                scraped_data = scrape_result.get("data", {})
                logger.info(f"✅ MVP data extracted: {scraped_data.get('title', 'No title')[:50]}...")
                
                # Step 2: Pass clean data to Research Agent
                logger.info(f"🤖 Step 2: Running Research Agent analysis...")
                research_runner = ResearchRunner()
                
                # Handle asyncio properly for FastAPI context (use module-level asyncio import)
                
                def run_agent_analysis():
                    """Run agent analysis in a separate thread with its own event loop"""
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return research_runner.run_research(
                            asin_or_url=asin_or_url,
                            marketplace=marketplace,
                            main_keyword=main_keyword
                        )
                    finally:
                        loop.close()
                
                # Run in thread pool to avoid event loop conflicts
                loop = asyncio.get_event_loop()
                research_ai_result = await loop.run_in_executor(
                    None, run_agent_analysis
                )
                
                if research_ai_result.get("success"):
                    logger.info(f"✅ Research Agent analysis completed successfully")
                    
                    # Extract MVP data summary for response
                    mvp_summary = {
                        "title_extracted": bool(scraped_data.get("title", "").strip()),
                        "images_count": scraped_data.get("images", {}).get("image_count", 0),
                        "aplus_sections": len(scraped_data.get("aplus_content", {}).get("sections", [])),
                        "reviews_count": len(scraped_data.get("reviews", {}).get("sample_reviews", [])),
                        "qa_questions": len(scraped_data.get("qa_section", {}).get("questions", []))
                    }
                    
                    research_result = {
                        "success": True,
                        "asin": scraped_data.get("asin", asin_or_url),
                        "marketplace": marketplace,
                        "main_keyword": main_keyword,
                        "revenue_competitors": len(revenue_data),
                        "design_competitors": len(design_data),
                        "ai_analysis": research_ai_result.get("analysis", "Analysis completed"),
                        "mvp_data_summary": mvp_summary,
                        "product_title": scraped_data.get("title", "Title not found"),
                        "agent_used": research_ai_result.get("agent_used", "ResearchAnalyst"),
                        "source": "production_mvp_pipeline",
                        "data_quality_score": sum([
                            1 if mvp_summary["title_extracted"] else 0,
                            1 if mvp_summary["images_count"] > 0 else 0,
                            1 if mvp_summary["aplus_sections"] > 0 else 0,
                            1 if mvp_summary["reviews_count"] > 0 else 0,
                            1 if mvp_summary["qa_questions"] > 0 else 0
                        ])
                    }
                    
                else:
                    raise Exception(f"Research Agent analysis failed: {research_ai_result.get('error')}")
                    
            except Exception as e:
                logger.warning(f"🔧 Production pipeline failed: {e}, falling back to inference")
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
        
        # Force AI Keyword Agent processing only (no direct fallback)
        keyword_processing_method = "ai_keyword"
        logger.info(f"Using AI Keyword Agent for {len(combined_data)} keywords")
        try:
            def run_keyword_analysis():
                """Run keyword analysis in a separate thread with its own event loop"""
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return keyword_runner.run_full_keyword_analysis(combined_data)
                finally:
                    loop.close()

            # Run in thread pool to avoid event loop conflicts
            loop = asyncio.get_event_loop()
            keyword_result = await loop.run_in_executor(None, run_keyword_analysis)

            if not keyword_result.get("success"):
                raise Exception(f"AI Keyword analysis failed: {keyword_result.get('error')}")
            if "result" not in keyword_result or not keyword_result.get("result"):
                raise Exception("AI Keyword analysis did not return structured result")
        except Exception as e:
            # Hard error if AI fails
            raise Exception(f"Keyword analysis failed (AI-only mode): {e}")
        
        if not keyword_result.get("success"):
            raise Exception(f"Keyword analysis failed: {keyword_result.get('error')}")
        
        keyword_analysis = keyword_result["result"]
        
        # Update status
        analysis_results[analysis_id].current_step = "scoring_analysis"
        analysis_results[analysis_id].progress = 60
        analysis_results[analysis_id].message = f"Scoring and prioritizing {keyword_analysis.total_keywords} keywords"
        
        # Step 4: Scoring Agent - Score and prioritize keywords
        scoring_runner = ScoringRunner()
        
        # Force AI Scoring Agent (no direct fallback)
        scoring_processing_method = "ai_scoring"
        logger.info(f"Using AI Scoring Agent for {keyword_analysis.total_keywords} keywords")
        try:
            def run_scoring_analysis():
                """Run scoring analysis in a separate thread with its own event loop"""
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return scoring_runner.run_full_scoring_analysis(
                        keyword_analysis=keyword_analysis,
                        product_attributes={
                            "product_title": research_result.get("product_title", ""),
                            "asin": research_result.get("asin", ""),
                            "marketplace": research_result.get("marketplace", marketplace),
                            "ai_analysis": research_result.get("ai_analysis", ""),
                            "data_quality_score": research_result.get("data_quality_score", 0),
                            **research_result.get("product_attributes", {})
                        },
                        business_context={
                            "main_keyword": main_keyword,
                            "revenue_competitors": research_result.get("revenue_competitors", 0),
                            "design_competitors": research_result.get("design_competitors", 0),
                            "source": research_result.get("source", "unknown")
                        }
                    )
                finally:
                    loop.close()

            # Run in thread pool to avoid event loop conflicts
            loop = asyncio.get_event_loop()
            scoring_result = await loop.run_in_executor(None, run_scoring_analysis)
            if not scoring_result:
                raise Exception("AI Scoring analysis returned empty result")
        except Exception as e:
            raise Exception(f"Scoring analysis failed (AI-only mode): {e}")
        
        # Update status
        analysis_results[analysis_id].current_step = "seo_optimization"
        analysis_results[analysis_id].progress = 80
        analysis_results[analysis_id].message = f"Generating SEO optimization recommendations"
        
        # Step 5: SEO Agent - Generate optimization recommendations
        seo_runner = SEORunner()
        
        # Use AI SEO Agent with proper asyncio handling
        seo_processing_method = "direct_processing"
        if settings.openai_configured and settings.USE_AI_AGENTS:
            logger.info("Using AI SEO Agent for optimization recommendations")
            try:
                def run_seo_analysis():
                    """Run SEO analysis in a separate thread with its own event loop"""
                    # Create a new event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return seo_runner.run_full_seo_optimization(
                            product_info={
                                "title": research_result.get("product_title", ""),
                                "asin": research_result.get("asin", ""),
                                "marketplace": research_result.get("marketplace", marketplace),
                                "ai_analysis": research_result.get("ai_analysis", ""),
                                "main_keyword": main_keyword,
                                **research_result
                            },
                            keyword_analysis=keyword_analysis.dict() if hasattr(keyword_analysis, 'dict') else {},
                            scoring_analysis=scoring_result.dict() if hasattr(scoring_result, 'dict') else {},
                            competitor_data={
                                "revenue_competitors": research_result.get("revenue_competitors", 0),
                                "design_competitors": research_result.get("design_competitors", 0),
                                "total_keywords_analyzed": keyword_analysis.total_keywords
                            }
                        )
                    finally:
                        loop.close()
                
                # Run in thread pool to avoid event loop conflicts
                loop = asyncio.get_event_loop()
                seo_result = await loop.run_in_executor(None, run_seo_analysis)
                
                if not seo_result:
                    raise Exception("AI SEO analysis returned empty result")
                seo_processing_method = "ai_seo"
            except Exception as e:
                logger.warning(f"AI SEO Agent failed: {e}, falling back to direct processing")
                seo_result = seo_runner.run_direct_optimization(
                    current_listing=research_result,
                    critical_keywords=[getattr(kw, 'keyword_phrase', str(kw)) for kw in getattr(scoring_result, 'critical_keywords', [])],
                    high_priority_keywords=[getattr(kw, 'keyword_phrase', str(kw)) for kw in getattr(scoring_result, 'high_priority_keywords', [])],
                    medium_priority_keywords=[getattr(kw, 'keyword_phrase', str(kw)) for kw in getattr(scoring_result, 'medium_priority_keywords', [])],
                    opportunity_keywords=[getattr(kw, 'keyword_phrase', str(kw)) for kw in getattr(scoring_result, 'high_priority_keywords', [])],
                    keyword_analysis={},
                    scoring_analysis={},
                    competitor_data={}
                )
                seo_processing_method = "direct_processing"
        else:
            logger.info("Using direct SEO processing")
            seo_result = seo_runner.run_direct_optimization(
                current_listing=research_result,
                critical_keywords=[getattr(kw, 'keyword_phrase', str(kw)) for kw in getattr(scoring_result, 'critical_keywords', [])],
                high_priority_keywords=[getattr(kw, 'keyword_phrase', str(kw)) for kw in getattr(scoring_result, 'high_priority_keywords', [])],
                medium_priority_keywords=[getattr(kw, 'keyword_phrase', str(kw)) for kw in getattr(scoring_result, 'medium_priority_keywords', [])],
                opportunity_keywords=[getattr(kw, 'keyword_phrase', str(kw)) for kw in getattr(scoring_result, 'high_priority_keywords', [])],
                keyword_analysis={},
                scoring_analysis={},
                competitor_data={}
            )
            seo_processing_method = "direct_processing"
        
        logger.info("✅ Complete pipeline analysis finished - Research + Keyword + Scoring + SEO")
        
        # Update status to complete with all results
        analysis_results[analysis_id].status = "completed"
        analysis_results[analysis_id].current_step = "pipeline_complete"
        analysis_results[analysis_id].progress = 100
        analysis_results[analysis_id].message = f"Complete AI pipeline analysis finished successfully"
        analysis_results[analysis_id].completed_at = datetime.now().isoformat()
        analysis_results[analysis_id].results = {
            "analysis_id": analysis_id,
            "research_analysis": research_result,
            "keyword_analysis": {
                "total_keywords": keyword_analysis.total_keywords,
                "keywords_by_category": {k.value: len(v) for k, v in keyword_analysis.keywords_by_category.items()},
                "top_opportunities": keyword_analysis.top_opportunities[:10],
                "recommended_focus_areas": keyword_analysis.recommended_focus_areas,
                "processing_method": keyword_processing_method
            },
            "scoring_analysis": {
                "total_analyzed": getattr(scoring_result, 'total_keywords_analyzed', 0),
                "priority_distribution": {
                    "critical": len(getattr(scoring_result, 'critical_keywords', [])),
                    "high": len(getattr(scoring_result, 'high_priority_keywords', [])),
                    "medium": len(getattr(scoring_result, 'medium_priority_keywords', [])),
                    "low": len(getattr(scoring_result, 'low_priority_keywords', [])),
                    "filtered": len(getattr(scoring_result, 'filtered_keywords', []))
                },
                "top_critical_keywords": [
                    {
                        "keyword": getattr(kw, 'keyword_phrase', str(kw)),
                        "intent_score": getattr(kw, 'intent_score', 0),
                        "priority_score": getattr(kw, 'priority_score', 0),
                        "search_volume": getattr(getattr(kw, 'competition_metrics', None), 'search_volume', 0),
                        "opportunity_score": getattr(getattr(kw, 'competition_metrics', None), 'opportunity_score', 0)
                    }
                    for kw in getattr(scoring_result, 'critical_keywords', [])[:10]
                ],
                "processing_method": scoring_processing_method
            },
            "seo_analysis": (
                {
                    # AI path returns SEOAnalysisResult with seo_optimization
                    "optimizations_generated": len(getattr(seo_result.seo_optimization, 'quick_wins', [])) + len(getattr(seo_result.seo_optimization, 'long_term_strategy', [])),
                    "title_optimization": getattr(seo_result.seo_optimization.title_optimization, 'recommended_title', 'No optimization available'),
                    "bullet_optimizations": len(getattr(seo_result.seo_optimization, 'bullet_optimization', [])) if isinstance(getattr(seo_result.seo_optimization, 'bullet_optimization', None), list) else len(getattr(getattr(seo_result.seo_optimization, 'bullet_optimization', None), 'recommended_bullets', []) if hasattr(getattr(seo_result.seo_optimization, 'bullet_optimization', None), 'recommended_bullets') else []),
                    "backend_keywords": getattr(getattr(seo_result.seo_optimization, 'backend_optimization', None), 'recommended_keywords', []),
                    "content_gaps": len(getattr(seo_result.seo_optimization, 'content_gaps', [])),
                    "competitive_advantages": len(getattr(seo_result.seo_optimization, 'competitive_advantages', [])),
                    "seo_score": getattr(getattr(seo_result.seo_optimization, 'seo_score', None), 'overall_score', 0),
                    "processing_method": seo_processing_method
                }
                if hasattr(seo_result, 'seo_optimization') else
                {
                    # Direct path returns SEOOptimization directly
                    "optimizations_generated": len(getattr(seo_result, 'quick_wins', [])) + len(getattr(seo_result, 'long_term_strategy', [])),
                    "title_optimization": getattr(getattr(seo_result, 'title_optimization', None), 'recommended_title', 'No optimization available'),
                    "bullet_optimizations": len(getattr(getattr(seo_result, 'bullet_optimization', None), 'recommended_bullets', []) if hasattr(seo_result, 'bullet_optimization') else []),
                    "backend_keywords": getattr(getattr(seo_result, 'backend_optimization', None), 'recommended_keywords', []) if hasattr(seo_result, 'backend_optimization') else [],
                    "content_gaps": len(getattr(seo_result, 'content_gaps', [])),
                    "competitive_advantages": len(getattr(seo_result, 'competitive_advantages', [])),
                    "seo_score": getattr(getattr(seo_result, 'seo_score', None), 'overall_score', 0),
                    "processing_method": seo_processing_method
                }
            ),
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_status": "complete"
        }
        
    except Exception as e:
        # Handle errors
        analysis_results[analysis_id].status = "failed"
        analysis_results[analysis_id].error = str(e)
        analysis_results[analysis_id].message = f"Analysis failed: {str(e)}"
        analysis_results[analysis_id].completed_at = datetime.now().isoformat()


@router.delete("/analyze/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete an analysis and its results."""
    
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    del analysis_results[analysis_id]
    return {"success": True, "message": "Analysis deleted successfully"}


def _create_fallback_research_result(asin_or_url: str, marketplace: str, main_keyword: str, revenue_data: List[Dict], design_data: List[Dict]) -> Dict[str, Any]:
    """
    Create a fallback research result when AI agents are not available.
    This uses inference to provide basic analysis.
    """
    
    # Extract all keywords for analysis
    all_keywords = []
    for row in revenue_data + design_data:
        keyword = row.get('Keyword Phrase', '').lower().strip()
        if keyword:
            all_keywords.append(keyword)
    
    # Infer product category from keywords
    inferred_category = "general"
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
    
    # Infer product title from main keyword
    if main_keyword:
        inferred_title = main_keyword.title() + " - Premium Quality Product"
    else:
        inferred_title = "Premium Product"
    
    # Infer brand
    brand_keywords = [kw for kw in all_keywords if len(kw.split()) == 1 and kw.isalpha() and len(kw) > 3]
    if brand_keywords:
        inferred_brand = brand_keywords[0].title()
    else:
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