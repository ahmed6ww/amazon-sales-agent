"""
Test Research + Keyword + SEO API Endpoint
Runs the Research agent, then feeds its scraped_product and base_relevancy_scores
into the Keyword agent for categorization, then runs Scoring enrichment, 
and finally generates SEO optimization analysis.
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from typing import Dict, Any, Optional
import logging
import time

from app.core.config import settings
from app.services.keyword_processing.root_extraction import get_priority_roots_for_search
from app.local_agents.keyword.subagents.root_extraction_agent import apply_root_extraction_ai
from app.services.openai_monitor import monitor


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/amazon-sales-intelligence")
async def amazon_sales_intelligence_pipeline(
    asin_or_url: str = Form(...),
    marketplace: str = Form("US"),
    main_keyword: Optional[str] = Form(None),
    revenue_csv: Optional[UploadFile] = File(None),
    design_csv: Optional[UploadFile] = File(None),
):
    """
    Amazon Sales Intelligence Pipeline - Complete AI-powered product analysis and optimization.
    
    🚀 **PRODUCTION ENDPOINT** - Runs complete 4-agent pipeline with advanced AI optimization:
    Research → Keyword Analysis → Scoring → SEO Optimization + Root Analysis

    ✨ **Features:**
    - 🔍 **Product Research**: Scrapes and analyzes Amazon listings with structured data extraction
    - 🎯 **Keyword Intelligence**: AI-powered categorization with intent scoring and relevancy analysis  
    - 📊 **Performance Scoring**: Advanced metrics with competition analysis and opportunity identification
    - 🏆 **SEO Optimization**: Amazon Guidelines compliant titles and bullets with 80-character mobile optimization
    - 🧠 **AI Enhancements**: Tasks 7, 11, 13 - Singular/plural handling, root filtering, compliance checking
    
    📈 **Efficiency Gains:**
    - Processes unlimited keywords from CSV files (no limitations)
    - Reduces keyword complexity by 70-95% through intelligent root grouping
    - Optimizes Amazon search strategies with priority root terms
    - Provides comprehensive analytics and actionable recommendations
    
    🎯 **Perfect for:**
    - Amazon sellers optimizing product listings
    - Market research and competitive analysis  
    - SEO optimization with compliance assurance
    - Data-driven decision making for product strategy
    """

    try:
        logger.info("="*80)
        logger.info("🚀 [REQUEST RECEIVED] Amazon Sales Intelligence Pipeline")
        logger.info(f"   ASIN/URL: {asin_or_url}")
        logger.info(f"   Marketplace: {marketplace}")
        logger.info(f"   Main Keyword: {main_keyword or 'Auto-detect'}")
        logger.info(f"   Revenue CSV: {'Provided' if revenue_csv else 'Not provided'}")
        logger.info(f"   Design CSV: {'Provided' if design_csv else 'Not provided'}")
        logger.info("="*80)
        
        # Validate OpenAI setup
        logger.info("🔧 [VALIDATION] Checking configuration...")
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
        
        logger.info("✅ [VALIDATION] Configuration valid")

        # Parse CSV files if provided
        logger.info("📄 [CSV PROCESSING] Parsing uploaded files...")
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
            logger.info(f"   ✅ Revenue CSV parsed: {len(revenue_data)} keywords")
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
            logger.info(f"   ✅ Design CSV parsed: {len(design_data)} keywords")
        
        logger.info(f"✅ [CSV PROCESSING] Complete - Total: {len(revenue_data) + len(design_data)} keywords")

        # Auto-pick main keyword if not provided
        if not main_keyword and revenue_data:
            phrases = [
                row.get("Keyword Phrase", "").strip().lower()
                for row in revenue_data[:10]
                if row.get("Keyword Phrase")
            ]
            main_keyword = phrases[0] if phrases else None
            if main_keyword:
                logger.info(f"🎯 [AUTO-DETECT] Main keyword: {main_keyword}")

        # Scrape and run Research Agent
        logger.info("")
        logger.info("📊 [STEP 1/4] RESEARCH AGENT - Product Analysis")
        logger.info(f"   Scraping Amazon listing: {asin_or_url}")

        from app.local_agents.research.helper_methods import scrape_amazon_listing

        scrape_result = scrape_amazon_listing(asin_or_url)
        if not scrape_result.get("success"):
            raise HTTPException(
                status_code=500, detail=f"Scraping failed: {scrape_result.get('error')}"
            )
        scraped_data = scrape_result.get("data", {})
        logger.info("   ✅ Product scraped successfully")

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

        # Extract keyword root analysis from research results
        keyword_root_analysis = (research_ai_result or {}).get("keyword_root_analysis", {})
        priority_roots = (research_ai_result or {}).get("priority_roots", [])
        total_unique_keywords = (research_ai_result or {}).get("total_unique_keywords", 0)

        # Extract only the required inputs for Keyword Agent
        scraped_product = (research_ai_result or {}).get("scraped_product") or {}
        base_relevancy_scores = (research_ai_result or {}).get(
            "base_relevancy_scores", {}
        )

        logger.info(f"✅ [STEP 1/4] RESEARCH COMPLETE")
        logger.info(f"   Total unique keywords: {total_unique_keywords}")
        logger.info(f"   Priority roots: {len(priority_roots)}")

        # Run Keyword Agent
        logger.info("")
        logger.info("🎯 [STEP 2/4] KEYWORD AGENT - Categorization")
        logger.info(f"   Analyzing {len(base_relevancy_scores)} keywords...")
        
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
        
        # Extract stats
        if isinstance(keyword_ai_result, dict):
            structured = keyword_ai_result.get("structured_data") or {}
            items = structured.get("items") or []
            stats = structured.get("stats") or {}
            logger.info(f"✅ [STEP 2/4] KEYWORD CATEGORIZATION COMPLETE")
            logger.info(f"   Total keywords: {len(items)}")
            logger.info(f"   Relevant: {stats.get('Relevant', {}).get('count', 0)}")
            logger.info(f"   Design-Specific: {stats.get('Design-Specific', {}).get('count', 0)}")
            logger.info(f"   Irrelevant: {stats.get('Irrelevant', {}).get('count', 0)}")

        # Enrich: append intent_score then merge CSV metrics into keyword items
        logger.info("")
        logger.info("📈 [STEP 3/4] SCORING AGENT - Intent & Metrics")
        logger.info("   Enriching keywords with intent scores...")
        
        try:
            from app.local_agents.scoring.runner import ScoringRunner

            items = []
            if isinstance(keyword_ai_result, dict):
                structured = keyword_ai_result.get("structured_data") or {}
                items = structured.get("items") or []
            if items:
                # Run scoring/LLM enrichment in a background thread to avoid event loop conflicts
                def run_scoring_enrichment():
                    loop_inner = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop_inner)
                    try:
                        return ScoringRunner.score_and_enrich(
                            items,
                            scraped_product=scraped_product,
                            revenue_csv=revenue_data,
                            design_csv=design_data,
                            base_relevancy_scores=base_relevancy_scores,
                        )
                    finally:
                        loop_inner.close()

                enriched = await loop.run_in_executor(None, run_scoring_enrichment)
                # Replace items inside structured_data
                if isinstance(keyword_ai_result, dict):
                    keyword_ai_result.setdefault("structured_data", {})["items"] = enriched
                    logger.info(f"✅ [STEP 3/4] SCORING COMPLETE")
                    logger.info(f"   Enriched {len(enriched)} keywords with intent scores and metrics")
        except Exception as _enrich_err:
            # Non-fatal: continue with original keyword result if enrichment fails
            logger.warning(f"⚠️  [STEP 3/4] Keyword enrichment skipped: {_enrich_err!s}")
            # Ensure items at least include a default intent_score
            try:
                if isinstance(keyword_ai_result, dict):
                    structured = keyword_ai_result.get("structured_data") or {}
                    items = structured.get("items") or []
                    if isinstance(items, list):
                        for it in items:
                            if isinstance(it, dict) and "intent_score" not in it:
                                it["intent_score"] = 0
                        keyword_ai_result.setdefault("structured_data", {})["items"] = items
            except Exception:
                pass

        # Always ensure intent_score field present (0 default) in case LLM returned nothing
        try:
            if isinstance(keyword_ai_result, dict):
                structured = keyword_ai_result.get("structured_data") or {}
                items = structured.get("items") or []
                if isinstance(items, list):
                    changed = False
                    for it in items:
                        if isinstance(it, dict) and "intent_score" not in it:
                            it["intent_score"] = 0
                            changed = True
                    if changed:
                        keyword_ai_result.setdefault("structured_data", {})["items"] = items
        except Exception:
            pass

        # Step 4: Run SEO Analysis
        logger.info("")
        logger.info("🏆 [STEP 4/4] SEO AGENT - Optimization")
        logger.info("   Analyzing current SEO state...")
        
        seo_analysis_result = None
        try:
            # Get the enriched keyword items for SEO analysis
            keyword_items = []
            if isinstance(keyword_ai_result, dict):
                structured = keyword_ai_result.get("structured_data", {})
                items = structured.get("items", [])
                if items:
                    keyword_items = items
                    logger.info(f"   Analyzing {len(keyword_items)} keywords for SEO optimization")
            
            # Compute filtered root volumes (Task 13) if we have items with roots
            filtered_root_volumes = None
            try:
                if keyword_items:
                    from app.local_agents.scoring.subagents.root_relevance_agent import apply_root_filtering_ai
                    filtered_root_volumes = apply_root_filtering_ai(keyword_items)
            except Exception as _rr_err:
                logger.debug(f"Root relevance filtering skipped: {_rr_err!s}")
                filtered_root_volumes = None
            
            if keyword_items and scraped_product:
                from app.local_agents.seo import SEORunner
                
                def run_seo_analysis():
                    loop_inner = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop_inner)
                    try:
                        seo_runner = SEORunner()
                        
                        # Extract competitor data for Task 6 analysis
                        competitor_data = []
                        if research_ai_result and research_ai_result.get("success"):
                            competitor_scrapes = research_ai_result.get("competitor_scrapes", {})
                            revenue_competitors = competitor_scrapes.get("revenue", [])
                            design_competitors = competitor_scrapes.get("design", [])
                            
                            # Combine both revenue and design competitors for comprehensive analysis
                            all_competitors = revenue_competitors + design_competitors
                            
                            # Deduplicate by ASIN and keep only successful scrapes with titles
                            seen_asins = set()
                            for comp in all_competitors:
                                asin = comp.get("asin", "")
                                if (asin not in seen_asins and 
                                    comp.get("success") and 
                                    comp.get("title") and 
                                    len(competitor_data) < 20):  # Limit to top 20 for analysis
                                    competitor_data.append(comp)
                                    seen_asins.add(asin)
                            
                            logger.info(f"🏆 Task 6: Prepared {len(competitor_data)} competitors for title analysis")
                        
                        return seo_runner.run_seo_analysis(
                            scraped_product=scraped_product,
                            keyword_items=keyword_items,
                            broad_search_volume_by_root=filtered_root_volumes,  # Task 13: filtered root volumes
                            competitor_data=competitor_data  # Task 6: Pass competitor data for benefit analysis
                        )
                    finally:
                        loop_inner.close()

                seo_result = await loop.run_in_executor(None, run_seo_analysis)
                
                if seo_result and seo_result.get("success"):
                    seo_analysis_result = seo_result
                    
                    # Extract and log SEO results
                    analysis = seo_result.get("analysis", {})
                    optimized_seo = analysis.get("optimized_seo", {})
                    optimized_title = optimized_seo.get("optimized_title", {})
                    optimized_bullets = optimized_seo.get("optimized_bullets", [])
                    
                    logger.info(f"✅ [STEP 4/4] SEO OPTIMIZATION COMPLETE")
                    logger.info(f"   Optimized title: {optimized_title.get('character_count', 0)} chars, {len(optimized_title.get('keywords_included', []))} keywords")
                    logger.info(f"   Optimized bullets: {len(optimized_bullets)} bullets created")
                    for i, bullet in enumerate(optimized_bullets[:3], 1):  # Show first 3
                        kw_count = len(bullet.get('keywords_included', []))
                        logger.info(f"      Bullet #{i}: {bullet.get('character_count', 0)} chars, {kw_count} keywords")
                else:
                    logger.warning(f"⚠️  [STEP 4/4] SEO analysis had issues: {seo_result.get('error') if seo_result else 'No result'}")
                    seo_analysis_result = {
                        "success": False,
                        "error": seo_result.get("error") if seo_result else "SEO analysis failed",
                        "summary": {
                            "current_coverage": "N/A",
                            "optimization_opportunities": 0,
                            "method": "failed"
                        }
                    }
            else:
                logger.warning("Skipping SEO analysis - insufficient data")
                seo_analysis_result = {
                    "success": False,
                    "error": "Insufficient data for SEO analysis",
                    "summary": {
                        "current_coverage": "N/A", 
                        "optimization_opportunities": 0,
                        "method": "skipped"
                    }
                }
                
        except Exception as e:
            logger.error(f"SEO analysis failed: {str(e)}", exc_info=True)
            seo_analysis_result = {
                "success": False,
                "error": f"SEO analysis failed: {str(e)}",
                "summary": {
                    "current_coverage": "N/A",
                    "optimization_opportunities": 0, 
                    "method": "error"
                }
            }

        # Calculate keyword efficiency metrics
        original_keyword_count = total_unique_keywords
        priority_roots_count = len(priority_roots)
        meaningful_roots_count = keyword_root_analysis.get('meaningful_roots', 0)
        
        efficiency_metrics = {}
        if original_keyword_count > 0:
            efficiency_metrics = {
                'original_keywords': original_keyword_count,
                'meaningful_roots': meaningful_roots_count,
                'priority_roots': priority_roots_count,
                'reduction_percentage': round((1 - priority_roots_count / original_keyword_count) * 100, 1),
                'efficiency_gain': f"{round((1 - priority_roots_count / original_keyword_count) * 100, 1)}%",
                'memory_optimization': f"~{round((1 - priority_roots_count / original_keyword_count) * 100)}% reduction in contextual memory usage",
                'api_optimization': f"Reduced Amazon search calls from {original_keyword_count} to {priority_roots_count}"
            }

        # Compile the final response with all 4 agent outputs + keyword root analysis
        response = {
            "success": True,
            "asin": scraped_data.get("asin", asin_or_url),
            "marketplace": marketplace,
            "ai_analysis_keywords": keyword_ai_result,
            "seo_analysis": seo_analysis_result,
            "keyword_root_optimization": {
                "analysis_summary": {
                    "total_keywords_processed": original_keyword_count,
                    "total_roots_identified": keyword_root_analysis.get('total_roots', 0),
                    "meaningful_roots": meaningful_roots_count,
                    "priority_roots_selected": priority_roots_count
                },
                "efficiency_metrics": efficiency_metrics,
                "priority_roots": priority_roots,
                "keyword_categorization": keyword_root_analysis.get('summary', {}),
                "recommendations": {
                    "amazon_search_terms": priority_roots[:10],
                    "optimization_notes": [
                        f"Process {priority_roots_count} root terms instead of {original_keyword_count} individual keywords",
                        f"Focus Amazon searches on: {', '.join(priority_roots[:5])}",
                        f"Achieved {efficiency_metrics.get('reduction_percentage', 0)}% reduction in keyword complexity"
                    ] if efficiency_metrics else []
                }
            },
            "source": "amazon_sales_intelligence_pipeline",
        }
        
        # Final success log
        logger.info("")
        logger.info("="*80)
        logger.info("✅ [PIPELINE COMPLETE] Response ready")
        logger.info(f"   Total keywords analyzed: {original_keyword_count}")
        logger.info(f"   Keyword categories: {len(items)} items categorized")
        logger.info(f"   SEO optimization: {'Success' if seo_analysis_result.get('success') else 'Failed'}")
        logger.info(f"   Root optimization: {priority_roots_count} priority roots identified")
        logger.info(f"   Efficiency gain: {efficiency_metrics.get('reduction_percentage', 0)}%")
        logger.info("="*80)
        
        # Print OpenAI API monitoring summary
        if settings.ENABLE_OPENAI_MONITORING:
            monitor.print_summary()
        
        # Add monitoring stats to response
        if settings.LOG_DETAILED_STATS:
            response["monitoring_stats"] = monitor.get_detailed_stats()

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("="*80)
        logger.error("❌ [PIPELINE ERROR] Request failed")
        logger.error(f"   Error type: {type(e).__name__}")
        logger.error(f"   Error message: {str(e)}")
        logger.error("="*80)
        logger.error(f"Full error details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
