"""
SEO Optimization Runner

Orchestrates SEO analysis and optimization using deterministic analysis 
combined with AI-powered optimization suggestions.
"""

import logging
from typing import Dict, List, Any, Optional
from agents import Runner

from .agent import seo_optimization_agent
from .prompts import SEO_ANALYSIS_PROMPT_TEMPLATE
from .helper_methods import (
    calculate_keyword_coverage,
    calculate_keyword_coverage_from_analysis,
    analyze_root_coverage,
    analyze_content_piece,
    prepare_keyword_data_for_analysis,
    format_keywords_for_prompt,
    calculate_character_usage,
    extract_keywords_from_content
)
from .keyword_validator import SEOKeywordValidator, validate_seo_output_keywords
from .seo_keyword_filter import validate_and_correct_keywords_included
from .schemas import (
    SEOAnalysisResult, CurrentSEO, OptimizedSEO, SEOComparison,
    KeywordCoverage, RootCoverage, ContentAnalysis
)

logger = logging.getLogger(__name__)


class SEORunner:
    """
    Runner for SEO optimization analysis and suggestions.
    
    Combines deterministic analysis of current SEO state with 
    AI-powered optimization recommendations.
    """
    
    def run_seo_analysis(
        self,
        scraped_product: Dict[str, Any],
        keyword_items: List[Dict[str, Any]],
        broad_search_volume_by_root: Optional[Dict[str, int]] = None,
        competitor_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Run complete SEO analysis and optimization.
    
    Args:
            scraped_product: Product data from research agent
            keyword_items: Categorized and scored keywords from scoring agent
            broad_search_volume_by_root: Root volume data (optional)
            competitor_data: Competitor ASIN data for Task 6 analysis (optional)
        
    Returns:
            Complete SEO analysis result
    """
        try:
            logger.info("")
            logger.info("="*80)
            logger.info("🎨 [SEO OPTIMIZATION AGENT]")
            logger.info("="*80)
            logger.info("📋 What: Analyze current SEO and generate optimized content")
            logger.info("🎯 Why: Maximize keyword coverage and search volume potential")
            logger.info("💡 Output: Optimized title, bullets, backend keywords + comparison")
            logger.info("="*80)
            
            # Step 1: Extract current listing content
            current_content = self._extract_current_content(scraped_product)
            logger.info(f"")
            logger.info(f"📄 [STEP 1] Extracting current product listing")
            logger.info(f"   Title: {len(current_content.get('title', ''))} chars")
            logger.info(f"   Bullets: {len(current_content.get('bullets', []))} bullet points")
            logger.info(f"   Backend: {len(current_content.get('backend_keywords', []))} keywords")
            
            # Step 2: Initialize keyword validator to prevent hallucination
            # Use ALL keywords for optimization (all categories)
            relevant_keywords = keyword_items  # Use all keywords, not just "Relevant" category
            keyword_validator = SEOKeywordValidator(relevant_keywords)
            logger.info(f"")
            logger.info(f"🔒 [STEP 2] Keyword validator initialized")
            logger.info(f"   📋 What: Prevent AI from hallucinating non-existent keywords")
            logger.info(f"   🎯 Loaded: {len(relevant_keywords)} keywords (all categories)")
            logger.info(f"   💡 Validator will reject any keyword not in this list")
            
            # Step 3: Prepare keyword data for analysis
            keyword_data = prepare_keyword_data_for_analysis(keyword_items)
            logger.info(f"")
            logger.info(f"📊 [STEP 3] Organizing keywords for analysis")
            logger.info(f"   Total: {keyword_data['total_keywords']} keywords")
            logger.info(f"   Relevant: {len(keyword_data['relevant_keywords'])} keywords")
            logger.info(f"   Design-Specific: {len(keyword_data['design_keywords'])} keywords")
            logger.info(f"   High Intent (2-3): {len(keyword_data['high_intent_keywords'])} keywords")
            logger.info(f"   High Volume (>500): {len(keyword_data['high_volume_keywords'])} keywords")
            
            # Step 4: Perform deterministic current SEO analysis
            logger.info(f"")
            logger.info(f"🔍 [STEP 4] Analyzing current SEO performance")
            logger.info(f"   📋 What: Measure current keyword coverage and root distribution")
            logger.info(f"   💡 Uses: Relevant + Design-Specific keywords only")
            current_seo = self._analyze_current_seo(current_content, keyword_data, broad_search_volume_by_root)
            logger.info(f"")
            logger.info(f"✅ [CURRENT SEO RESULTS]")
            logger.info(f"   Keyword Coverage: {current_seo.keyword_coverage.coverage_percentage}%")
            logger.info(f"   Keywords Found: {current_seo.keyword_coverage.covered_keywords}/{current_seo.keyword_coverage.total_keywords}")
            logger.info(f"   Root Coverage: {current_seo.root_coverage.coverage_percentage}%")
            
            # Step 4: Task 6 - Analyze competitor titles for benefit-focused optimization
            competitor_analysis = None
            if competitor_data and len(competitor_data) > 0:
                try:
                    from .subagents.competitor_title_analysis_agent import apply_competitor_title_optimization_ai
                    competitor_analysis = apply_competitor_title_optimization_ai(
                        current_content=current_content,
                        competitor_data=competitor_data,
                        keyword_data=keyword_data,
                        product_context=scraped_product,
                        keyword_validator=keyword_validator
                    )
                    logger.info(f"🏆 Task 6: Analyzed {len(competitor_data)} competitors for benefit optimization")
                except Exception as e:
                    logger.warning(f"🟡 Task 6: Competitor analysis failed: {e}")
                    competitor_analysis = None
            else:
                logger.info("📝 Task 6: No competitor data provided, skipping competitor analysis")
            
            # Step 5: Pre-allocate keywords to prevent duplication
            # Allocate keywords for AI optimization
            # Get actual bullet count from scraped data for dynamic optimization
            actual_bullet_count = len(current_content.get("bullets", []))
            logger.info(f"📊 Detected {actual_bullet_count} bullet points in current listing")
            
            logger.info(f"📊 Allocating keywords for optimization...")
            title_keywords = keyword_validator.get_allocated_keywords_for_ai("title")
            bullet_keywords = keyword_validator.get_allocated_keywords_for_ai("bullets", actual_bullet_count)
            backend_keywords = keyword_validator.get_allocated_keywords_for_ai("backend")
            
            logger.info(f"   ✅ Allocated {len(title_keywords)} title, {len(bullet_keywords)} bullet, {len(backend_keywords)} backend keywords")
            
            # Step 6: Generate AI-powered optimization suggestions
            logger.info(f"🤖 Generating AI optimization suggestions...")
            optimized_seo = self._generate_ai_optimizations(
                current_content, keyword_data, scraped_product, competitor_analysis, keyword_validator,
                title_keywords, bullet_keywords, backend_keywords, actual_bullet_count
            )
            logger.info("🤖 AI optimization suggestions generated")
            
            # Step 5.5: Validate SEO output to prevent keyword hallucination
            validation_report = validate_seo_output_keywords(optimized_seo.model_dump(), keyword_validator)
            if not validation_report['overall_valid']:
                logger.error("❌ Keyword hallucination detected in SEO output - applying corrections")
                optimized_seo = self._correct_keyword_hallucination(optimized_seo, keyword_validator)
            else:
                logger.info("✅ SEO output validation passed - no keyword hallucination")
            
            # Step 5.6: Validate keywords_included fields to ensure only actual keywords are reported
            logger.info("🔍 Validating keywords_included fields...")
            optimized_seo_dict = optimized_seo.model_dump()
            validated_seo_dict, validation_stats = validate_and_correct_keywords_included(optimized_seo_dict, keyword_data)
            
            # Reconstruct the Pydantic model with validated data
            optimized_seo = OptimizedSEO(**validated_seo_dict)
            logger.info("✅ Keywords_included fields validated")
            
            # Step 5.7: Deduplicate keywords across title, bullets, backend
            optimized_seo = self._deduplicate_keywords_across_content(optimized_seo)
            
            # Step 5: Calculate comparison metrics
            comparison = self._calculate_comparison_metrics(current_seo, optimized_seo, keyword_data)
            logger.info("📈 Comparison metrics calculated")
            
            # Step 6: Assemble final result
            result = SEOAnalysisResult(
                current_seo=current_seo,
                optimized_seo=optimized_seo,
                comparison=comparison,
                product_context={
                    "title": scraped_product.get("title", ""),
                    "brand": current_content.get("brand", ""),
                    "category": "Unknown"  # Could be enhanced with category detection
                },
                analysis_metadata={
                    "total_keywords_analyzed": len(keyword_items),
                    "relevant_keywords_count": len(keyword_data["relevant_keywords"]),
                    "high_intent_keywords_count": len(keyword_data["high_intent_keywords"]),
                    "optimization_method": "ai" if self._should_use_ai_optimization() else "rule_based"
                }
            )
            
            logger.info("✅ SEO analysis complete")
            
            # Debug: Print stats and keywords to console
            # Debug output disabled
            # print("\n" + "="*80)
            # print("SEO ANALYSIS DEBUG INFO")
            # print("="*80)
            # 
            # # Print comparison stats
            # print(f"\nCOMPARISON STATS:")
            # print(f"  Coverage Improvement: {comparison.coverage_improvement.get('delta_pct_points', 0)}%")
            # print(f"  Before Coverage: {comparison.coverage_improvement.get('before_coverage_pct', 0)}%")
            # print(f"  After Coverage: {comparison.coverage_improvement.get('after_coverage_pct', 0)}%")
            # print(f"  Volume Increase: {comparison.volume_improvement.get('delta_volume', 0)}")
            # print(f"  Optimization Score: {comparison.summary_metrics.get('overall_improvement_score', 0)}/10")
            # 
            # # Print current title keywords
            # print(f"\nCURRENT TITLE KEYWORDS:")
            # current_title_keywords = getattr(current_seo.title_analysis, 'keywords_found', [])
            # print(f"  Found: {len(current_title_keywords)} keywords")
            # for i, kw in enumerate(current_title_keywords[:10], 1):
            #     print(f"    {i}. {kw}")
            # if len(current_title_keywords) > 10:
            #     print(f"    ... and {len(current_title_keywords) - 10} more")
            # 
            # # Print optimized title keywords
            # print(f"\nOPTIMIZED TITLE KEYWORDS:")
            # optimized_title_keywords = getattr(optimized_seo.optimized_title, 'keywords_included', [])
            # print(f"  Included: {len(optimized_title_keywords)} keywords")
            # for i, kw in enumerate(optimized_title_keywords[:10], 1):
            #     print(f"    {i}. {kw}")
            # if len(optimized_title_keywords) > 10:
            #     print(f"    ... and {len(optimized_title_keywords) - 10} more")
            # 
            # # Print bullet keywords
            # print(f"\nBULLET POINT KEYWORDS:")
            # for i, bullet in enumerate(optimized_seo.optimized_bullets, 1):
            #     bullet_keywords = getattr(bullet, 'keywords_included', [])
            #     print(f"  Bullet {i}: {len(bullet_keywords)} keywords")
            #     for j, kw in enumerate(bullet_keywords[:5], 1):
            #         print(f"    {j}. {kw}")
            #     if len(bullet_keywords) > 5:
            #         print(f"    ... and {len(bullet_keywords) - 5} more")
            # 
            # print("="*80)
            # print("END SEO ANALYSIS DEBUG INFO")
            # print("="*80 + "\n")
            
            return {
                "success": True,
                "analysis": result.model_dump(),
                "summary": {
                    "current_coverage": f"{current_seo.keyword_coverage.coverage_percentage}%",
                    "optimization_opportunities": len(current_seo.keyword_coverage.missing_high_intent),
                    "method": "ai" if self._should_use_ai_optimization() else "rule_based"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ SEO analysis failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"SEO analysis failed: {str(e)}"
            }
    
    def _extract_current_content(self, scraped_product: Dict[str, Any]) -> Dict[str, Any]:
        """Extract current listing content from scraped product data."""
        
        # Extract title
        title = scraped_product.get("title", "")
        
        # Extract bullets from elements
        bullets = []
        elements = scraped_product.get("elements", {})
        feature_bullets = elements.get("feature-bullets", {})
        if feature_bullets.get("present"):
            bullets = feature_bullets.get("bullets", [])
        
        # Extract backend keywords (if available - may not be in scraped data)
        backend_keywords = []
        
        # Extract brand if available
        brand = ""
        overview = elements.get("productOverview_feature_div", {})
        if overview.get("present"):
            kv_data = overview.get("kv", {})
            brand = kv_data.get("Brand", "")
        
        return {
            "title": title,
            "bullets": bullets,
            "backend_keywords": backend_keywords,
            "brand": brand
        }
    
    def _analyze_current_seo(
        self, 
        current_content: Dict[str, Any], 
        keyword_data: Dict[str, Any],
        root_volumes: Optional[Dict[str, int]] = None
    ) -> CurrentSEO:
        """Perform deterministic analysis of current SEO state."""
        
        # Get relevant keywords for analysis (include branded for detection in current content)
        all_relevant = (keyword_data["relevant_keywords"] + 
                       keyword_data["design_keywords"] + 
                       keyword_data.get("branded_keywords", []))
        keyword_phrases = [kw.get("phrase", "") for kw in all_relevant]
        
        logger.info(f"🔍 [CURRENT SEO] Searching for keywords in current content:")
        logger.info(f"   - Relevant: {len(keyword_data['relevant_keywords'])} keywords")
        logger.info(f"   - Design-Specific: {len(keyword_data['design_keywords'])} keywords")
        logger.info(f"   - Branded: {len(keyword_data.get('branded_keywords', []))} keywords (for detection only)")
        logger.info(f"   - Total: {len(all_relevant)} keywords to search")
        
        # Build keyword volumes map for Task 2 enhancement
        keyword_volumes = {}
        for kw in all_relevant:
            phrase = kw.get("phrase", "")
            volume = kw.get("search_volume", 0)
            if phrase and volume:
                keyword_volumes[phrase] = volume
        
        logger.info(f"📊 [TASK 2] Built keyword volumes map: {len(keyword_volumes)} keywords have volume data")
        
        # Analyze root coverage
        if root_volumes:
            root_data = analyze_root_coverage(current_content, root_volumes)
            root_coverage = RootCoverage(**root_data)
        else:
            # Use aggregated root volumes from keyword data
            root_coverage = RootCoverage(
                total_roots=len(keyword_data["root_volumes"]),
                covered_roots=0,
                coverage_percentage=0.0,
                missing_roots=list(keyword_data["root_volumes"].keys()),
                root_volumes=keyword_data["root_volumes"]
            )
    
    # ==================================================================================
        # ANALYZE CURRENT CONTENT WITH SMART DEDUPLICATION
    # ==================================================================================
        # PURPOSE: Find which keywords are in current title and bullets
        # DEDUPLICATION STRATEGY:
        #   1. Analyze title FIRST → finds keywords in title
        #   2. Analyze bullets → CAN include title keywords (for yellow highlighting)
        #   3. BUT prevent bullet-to-bullet duplication (same keyword in multiple bullets)
        # WHY: Frontend needs to see duplicates for yellow highlighting, but we prevent
        #      keywords appearing in multiple bullets
        # EXAMPLE: "freeze dried" in title + bullet 1 → Both shown (bullet gets yellow badge)
        #          "organic" in bullet 1 + bullet 2 → Only bullet 1 (prevent duplication)
        # ==================================================================================
        
        logger.info(f"")
        logger.info(f"🔍 [CURRENT CONTENT ANALYSIS]")
        logger.info(f"   📋 What: Extract keywords from title and bullets")
        logger.info(f"   💡 Strategy: Allow title-bullet duplicates (for highlighting)")
        logger.info(f"   🚫 Strategy: Prevent bullet-to-bullet duplicates")
        
        # Analyze title first (with volume calculation - Task 2)
        title_analysis_data = analyze_content_piece(current_content["title"], keyword_phrases, keyword_volumes)
        title_analysis = ContentAnalysis(**title_analysis_data)
        
        # Log volume
        title_volume = title_analysis_data.get("total_search_volume", 0)
        logger.info(f"   ✅ Title: {len(title_analysis_data.get('keywords_found', []))} keywords (volume: {title_volume:,})")
        
        # Track keywords already found in title
        found_in_title = set(kw.lower() for kw in title_analysis_data.get("keywords_found", []))
        
        # Analyze bullets with ALL keywords (for accurate detection)
        # Store both original and filtered results for different purposes
        bullets_analysis = []
        bullets_analysis_for_display = []  # For frontend display (shows all keywords)
        found_in_bullets_cumulative = set()  # Track across bullets only
        
        for i, bullet in enumerate(current_content["bullets"], 1):
            # Analyze each bullet with ALL keywords (for accurate detection) + volumes (Task 2)
            analysis_data = analyze_content_piece(bullet, keyword_phrases, keyword_volumes)
            analysis = ContentAnalysis(**analysis_data)
            
            # Store original analysis for frontend display (shows all keywords found)
            bullets_analysis_for_display.append(analysis)
            
            # Filter results to prevent double-counting in coverage calculations
            filtered_keywords = []
            filtered_volume = 0
            for kw in analysis.keywords_found:
                if kw.lower() not in found_in_bullets_cumulative:
                    filtered_keywords.append(kw)
                    found_in_bullets_cumulative.add(kw.lower())
                    # Add volume for this keyword
                    if kw in keyword_volumes:
                        filtered_volume += keyword_volumes[kw]
            
            # Create analysis with filtered keywords for coverage calculation
            filtered_analysis = ContentAnalysis(
                content=analysis.content,
                keywords_found=filtered_keywords,  # For coverage calculation
                keyword_count=len(filtered_keywords),
                character_count=analysis.character_count,
                keyword_density=analysis.keyword_density,
                opportunities=analysis.opportunities,
                total_search_volume=filtered_volume  # Task 2: Add filtered volume
            )
            bullets_analysis.append(filtered_analysis)
            
            # Track keywords found in this bullet for logging
            found_in_bullet = set(kw.lower() for kw in analysis.keywords_found)
            bullet_volume = analysis_data.get("total_search_volume", 0)
            duplicates_with_title = found_in_bullet & found_in_title
            if duplicates_with_title:
                logger.info(f"   ✅ Bullet {i}: {len(found_in_bullet)} keywords ({len(duplicates_with_title)} also in title), {len(filtered_keywords)} unique (volume: {bullet_volume:,})")
            else:
                logger.info(f"   ✅ Bullet {i}: {len(found_in_bullet)} keywords, {len(filtered_keywords)} unique (volume: {bullet_volume:,})")
        
        # Calculate keyword coverage using filtered bullet analysis (no duplicates)
        coverage_data = calculate_keyword_coverage_from_analysis(
            title_analysis, bullets_analysis, current_content["backend_keywords"], all_relevant
        )
        keyword_coverage = KeywordCoverage(**coverage_data)
        
        # Calculate character usage
        char_usage = calculate_character_usage(current_content)
        
        return CurrentSEO(
            title_analysis=title_analysis,
            bullets_analysis=bullets_analysis,
            bullets_analysis_for_display=bullets_analysis_for_display,
            backend_keywords=current_content["backend_keywords"],
            keyword_coverage=keyword_coverage,
            root_coverage=root_coverage,
            total_character_usage=char_usage
        )
    
    def _generate_ai_optimizations(
        self,
        current_content: Dict[str, Any],
        keyword_data: Dict[str, Any], 
        scraped_product: Dict[str, Any],
        competitor_analysis: Optional[Dict[str, Any]] = None,
        keyword_validator: Optional[SEOKeywordValidator] = None,
        title_keywords: Optional[List[Dict[str, Any]]] = None,
        bullet_keywords: Optional[List[Dict[str, Any]]] = None,
        backend_keywords: Optional[List[Dict[str, Any]]] = None,
        target_bullet_count: Optional[int] = None
    ) -> OptimizedSEO:
        """Generate AI-powered optimization suggestions with Task 7 Amazon compliance."""
        
        # Task 7: Use AI-powered Amazon Compliance Agent for guidelines compliance and 80-char optimization
        try:
            from app.local_agents.seo.subagents.amazon_compliance_agent import apply_amazon_compliance_ai
            
            # Extract product context for AI agent
            product_context = {
                "brand": current_content.get("brand", ""),  # Use already-extracted brand from current_content
                "category": scraped_product.get("category", ""),
                "title": current_content.get("title", "")
            }
            
            # Apply AI-powered Amazon compliance optimization (Task 7) with Task 6 competitor insights
            compliance_result = apply_amazon_compliance_ai(
                current_content=current_content,
                keyword_data=keyword_data,
                product_context=product_context,
                competitor_analysis=competitor_analysis,
                keyword_validator=keyword_validator,
                title_keywords=title_keywords,
                bullet_keywords=bullet_keywords,
                backend_keywords=backend_keywords,
                target_bullet_count=target_bullet_count
            )
            
            logger.info("[Task7-AI] Applied Amazon Guidelines Compliance with 80-character optimization")
            
            # Convert compliance result to OptimizedSEO format
            return self._convert_compliance_result_to_optimized_seo(compliance_result, keyword_data)
            
        except Exception as compliance_error:
            logger.warning(f"[Task7-AI] Amazon compliance agent failed, falling back to standard AI: {compliance_error}")
            
            # Fallback to original AI optimization if Task 7 agent fails
            # Extract brand name for prompt
            brand = current_content.get("brand", "")
            if not brand:
                # Try to extract brand from title (first word or before first delimiter)
                title = current_content.get("title", "")
                if title:
                    # Common brand extraction: first word before space, comma, or dash
                    brand = title.split()[0] if title.split() else ""
            
            prompt_data = {
                "brand": brand or "Brand Name Unknown",
                "current_title": current_content["title"],
                "current_bullets": "\n".join([f"• {bullet}" for bullet in current_content["bullets"]]),
                "backend_keywords": " ".join(current_content["backend_keywords"]) if current_content["backend_keywords"] else "None",
                "total_keywords": keyword_data["total_keywords"],
                "relevant_keywords": format_keywords_for_prompt(keyword_data["relevant_keywords"]),
                "design_keywords": format_keywords_for_prompt(keyword_data["design_keywords"]),
                "root_volumes": str(keyword_data["root_volumes"]),
                "high_intent_keywords": format_keywords_for_prompt(keyword_data["high_intent_keywords"]),
                "high_volume_keywords": format_keywords_for_prompt(keyword_data["high_volume_keywords"]),
                "product_context": str(scraped_product.get("elements", {}).get("productOverview_feature_div", {}))
            }
            
            # Enhanced prompt with Task 7 requirements
            enhanced_prompt = SEO_ANALYSIS_PROMPT_TEMPLATE.format(**prompt_data)
            enhanced_prompt += """
            ## REQUIREMENTS:
            - Follow Amazon Title Guidelines (https://sellercentral.amazon.com/help/hub/reference/external/GYTR6SYGFA5E3EQC?locale=en-US)
            - Follow Amazon Bullet Point Guidelines (https://sellercentral.amazon.com/help/hub/reference/external/GX5L8BF8GLMML6CX?locale=en-US)
            - OPTIMIZE FIRST 80 CHARACTERS: Must include main keyword root + design-specific keyword root + key benefit
            - No promotional language, proper capitalization, compliance with all Amazon guidelines
            """
            
            try:
                # Run standard AI agent with enhanced prompt
                result = Runner.run_sync(seo_optimization_agent, enhanced_prompt)
                ai_output = result.final_output
                return self._parse_ai_output_to_optimized_seo(ai_output, keyword_data)

            except Exception as e:
                logger.error(f"Both Task and fallback AI optimization failed: {e}")
                raise
    
    def _convert_compliance_result_to_optimized_seo(
        self, 
        compliance_result: Dict[str, Any], 
        keyword_data: Dict[str, Any]
    ) -> OptimizedSEO:
        """Convert compliance result to OptimizedSEO format with Task 2 volume calculation."""
        from .schemas import OptimizedContent
        from .helper_methods import extract_keywords_from_content
        
        # Build keyword volumes map and phrases list
        all_keywords = keyword_data.get("relevant_keywords", []) + keyword_data.get("design_keywords", [])
        keyword_volumes = {kw.get("phrase", ""): kw.get("search_volume", 0) for kw in all_keywords if kw.get("phrase")}
        keyword_phrases = list(keyword_volumes.keys())
        
        logger.info(f"📊 [TASK 2] Converting compliance result with volume calculation")
        
        # Extract optimized title with enhanced keyword detection
        title_data = compliance_result.get("optimized_title", {})
        title_content = title_data.get("content", "")
        
        # Use enhanced extraction to find ALL keywords in title (Task 2)
        title_keywords_found, title_volume = extract_keywords_from_content(
            title_content, keyword_phrases, keyword_volumes
        )
        
        logger.info(f"   ✅ Title: {len(title_keywords_found)} keywords found (volume: {title_volume:,})")
        
        optimized_title = OptimizedContent(
            content=title_content,
            keywords_included=title_keywords_found,  # Use enhanced detection
            improvements=[
                f"Amazon Guidelines Compliant",
                f"80-char optimized: {title_data.get('first_80_chars', '')[:50]}...",
                f"Main root included: {title_data.get('main_root_included', False)}",
                f"Design root included: {title_data.get('design_root_included', False)}"
            ],
            character_count=len(title_content),
            total_search_volume=title_volume  # Task 2: Add volume
        )
        
        # Extract optimized bullets with enhanced keyword detection
        bullets_data = compliance_result.get("optimized_bullets", [])
        optimized_bullets = []
        for idx, bullet in enumerate(bullets_data, 1):
            bullet_content = bullet.get("content", "")
            
            # Use enhanced extraction to find ALL keywords in bullet (Task 2)
            bullet_keywords_found, bullet_volume = extract_keywords_from_content(
                bullet_content, keyword_phrases, keyword_volumes
            )
            
            logger.info(f"   ✅ Bullet {idx}: {len(bullet_keywords_found)} keywords found (volume: {bullet_volume:,})")
            
            # Note: bullet-to-bullet deduplication and volume adjustment happens in seo_keyword_filter.py
            optimized_bullets.append(OptimizedContent(
                content=bullet_content,
                keywords_included=bullet_keywords_found,  # All keywords found
                keywords_duplicated_from_other_bullets=[],  # Will be set by validator
                unique_keywords_count=len(bullet_keywords_found),  # Will be adjusted by validator
                improvements=[
                    f"Benefit-focused: {bullet.get('primary_benefit', '')}",
                    f"Guideline compliant: {bullet.get('guideline_compliance', 'PASS')}"
                ],
                character_count=len(bullet_content),
                total_search_volume=bullet_volume  # Will be adjusted by validator
            ))
        
        # Generate backend keywords (enhanced with compliance awareness)
        relevant_keywords = keyword_data.get("relevant_keywords", [])
        design_keywords = keyword_data.get("design_keywords", [])
        all_keywords = relevant_keywords + design_keywords
        
        # Extract backend keywords not used in title/bullets
        title_content = title_data.get("content", "").lower()
        bullet_content = " ".join([b.get("content", "") for b in bullets_data]).lower()
        
        backend_keywords = []
        for kw in all_keywords[:15]:  # Top 15
            phrase = kw.get("phrase", "")
            if phrase.lower() not in title_content and phrase.lower() not in bullet_content:
                backend_keywords.append(phrase)
        
        # Build strategy explanation
        strategy = compliance_result.get("strategy", {})
        
        return OptimizedSEO(
            optimized_title=optimized_title,
            optimized_bullets=optimized_bullets,
            optimized_backend_keywords=backend_keywords,
            keyword_strategy={
                "amazon_compliance": "ENFORCED",
                "first_80_optimization": strategy.get("first_80_optimization", "Applied"),
                "keyword_integration": strategy.get("keyword_integration", "Optimized"),
                "guideline_compliance": "STRICT"
            },
            rationale=(
                f"Task 7 Amazon Guidelines Compliance Applied: "
                f"{strategy.get('compliance_approach', 'AI-powered optimization with strict guideline adherence')}. "
                f"First 80 characters optimized for mobile viewing with main and design-specific keyword roots. "
                f"All content verified for Amazon policy compliance."
            )
        )
    
    def _generate_rule_based_optimizations(
        self,
        current_content: Dict[str, Any],
        keyword_data: Dict[str, Any]
    ) -> OptimizedSEO:
        """Generate rule-based optimization suggestions that fulfill MVP requirements."""
        
        # Get keywords by category and intent
        relevant_keywords = keyword_data["relevant_keywords"]
        design_keywords = keyword_data["design_keywords"]
        high_intent_keywords = keyword_data["high_intent_keywords"]
        high_volume_keywords = keyword_data["high_volume_keywords"]
        
        # Combine relevant + design for optimization
        all_good_keywords = relevant_keywords + design_keywords
        
        # Sort by relevancy score (descending), then by search volume, then by intent score
        sorted_keywords = sorted(all_good_keywords, 
                               key=lambda x: (x.get("relevancy_score", 0), x.get("search_volume", 0), x.get("intent_score", 0)), 
                               reverse=True)
        
        # Get all unique roots from good keywords
        all_roots = set()
        root_to_best_keyword = {}
        for kw in sorted_keywords:
            root = kw.get("root", "")
            if root and root not in root_to_best_keyword:
                root_to_best_keyword[root] = kw.get("phrase", "")
                all_roots.add(root)
        
        # Select top keywords for title optimization
        # Prioritize: high intent + high volume + covers different roots
        title_keywords = []
        used_roots = set()
        
        # First, get highest relevancy keywords that cover different roots
        for kw in sorted_keywords[:15]:  # Look at top 15
            root = kw.get("root", "")
            phrase = kw.get("phrase", "")
            relevancy = kw.get("relevancy_score", 0)
            volume = kw.get("search_volume", 0)
            
            # Handle None values safely
            if relevancy is None:
                relevancy = 0
            if volume is None:
                volume = 0
            
            # Prioritize high relevancy (80+) and good volume (300+)
            if relevancy >= 80 and volume >= 300 and root not in used_roots and len(title_keywords) < 4:
                title_keywords.append(phrase)
                used_roots.add(root)
        
        # Fill remaining slots with high-relevancy terms
        for kw in sorted_keywords:
            phrase = kw.get("phrase", "")
            relevancy = kw.get("relevancy_score", 0)
            
            # Handle None values safely
            if relevancy is None:
                relevancy = 0
                
            if len(title_keywords) < 5 and phrase not in title_keywords and relevancy >= 70:
                title_keywords.append(phrase)
        
        # Create natural-sounding optimized title
        brand = current_content.get("brand", "BREWER")
        primary_keyword = title_keywords[0] if title_keywords else "freeze dried strawberries"
        
        # Build title with natural flow
        title_parts = []
        if brand:
            title_parts.append(brand)
        
        # Add pack info
        title_parts.append("Bulk")
        
        # Add primary keyword
        title_parts.append(primary_keyword.title())
        
        # Add key attributes
        title_parts.append("- Organic")
        title_parts.append("No Sugar Added")
        
        # Add secondary keyword if different
        if len(title_keywords) > 1:
            secondary = title_keywords[1]
            if "organic" not in secondary.lower():
                title_parts.append(f"Premium {secondary.title()}")
        
        # Add use cases
        title_parts.append("for Snacking, Baking & Travel")
        
        optimized_title_content = " ".join(title_parts)[:200]  # Amazon limit
        
        optimized_title = {
            "content": optimized_title_content,
            "keywords_included": title_keywords[:3],
            "improvements": [
                f"Covers {len(used_roots)} keyword roots",
                f"Uses {len([k for k in all_good_keywords if (k.get('relevancy_score') or 0) >= 80])} high-relevancy keywords",
                f"Prioritizes {sum((k.get('relevancy_score') or 0) for k in all_good_keywords[:3])//3} avg relevancy score",
                "Natural, readable format"
            ],
            "character_count": len(optimized_title_content)
        }
        
        # Create optimized bullets focusing on different keyword clusters
        optimized_bullets = []
        bullet_templates = [
            ("Flavor & Quality", "Enjoy the naturally sweet, tangy crunch of {} bursting with real fruit flavor."),
            ("Organic & Healthy", "Our {} are organic, no sugar added, and made from farm-fresh strawberries."),
            ("Versatile Use", "Perfect {} for baking, smoothies, cereals, and on-the-go snacking."),
            ("Travel Ready", "Lightweight and shelf-stable {} ideal for hiking, camping, and travel adventures."),
            ("Bulk Value", "Buy in bulk and enjoy premium quality {} whenever you need them.")
        ]
        
        for i, (focus, template) in enumerate(bullet_templates):
            if i < len(sorted_keywords):
                keyword = sorted_keywords[i].get("phrase", "")
                bullet_content = f"✅ {focus}: " + template.format(keyword)
                optimized_bullets.append({
                    "content": bullet_content,
                    "keywords_included": [keyword],
                    "improvements": [f"Focused on {focus.lower()}", "Clear value proposition"],
                    "character_count": len(bullet_content)
                })
        
        # Backend keywords: Use remaining good keywords not in title/bullets
        used_in_content = set(title_keywords)
        for bullet in optimized_bullets:
            used_in_content.update(bullet["keywords_included"])
        
        backend_keywords = []
        for kw in sorted_keywords:
            phrase = kw.get("phrase", "")
            if phrase not in used_in_content and len(backend_keywords) < 15:
                backend_keywords.append(phrase)
        
        # Task 11: Apply AI-powered variant optimization before generating variations
        try:
            from app.local_agents.scoring.subagents.keyword_variant_agent import apply_variant_optimization_ai
            # Use AI to remove redundant singular/plural variants from good keywords
            optimized_keywords = apply_variant_optimization_ai(all_good_keywords)
            logger.info(f"[Task11-AI] Applied AI variant optimization: {len(all_good_keywords)} -> {len(optimized_keywords)} keywords")
        except Exception as e:
            logger.warning(f"[Task11-AI] AI variant optimization failed, using original keywords: {e}")
            optimized_keywords = all_good_keywords
        
        # Add misspellings and variations (using optimized keyword list)
        variations = []
        for kw in optimized_keywords:
            phrase = kw.get("phrase", "")
            # Add common variations (punctuation, spacing only - no singular/plural thanks to AI)
            if "freeze dried" in phrase:
                variations.append(phrase.replace("freeze dried", "freeze-dried"))
                variations.append(phrase.replace("freeze dried", "freezedried"))
        
        # Remove duplicates and already used variations
        filtered_variations = []
        for variation in variations:
            if variation not in used_in_content and variation not in backend_keywords:
                filtered_variations.append(variation)
        
        backend_keywords.extend(filtered_variations[:5])
        
        from .schemas import OptimizedContent
        
        return OptimizedSEO(
            optimized_title=OptimizedContent(**optimized_title),
            optimized_bullets=[OptimizedContent(**bullet) for bullet in optimized_bullets],
            optimized_backend_keywords=backend_keywords,
            keyword_strategy={
                "primary_focus": f"Cover {len(all_roots)} keyword roots",
                "secondary_focus": f"Prioritize {len([k for k in all_good_keywords if (k.get('relevancy_score') or 0) >= 80])} high-relevancy keywords",
                "relevancy_strategy": f"Use {sum((k.get('relevancy_score') or 0) for k in all_good_keywords[:5])//5} avg relevancy score",
                "character_optimization": True,
                "root_coverage": f"{len(used_roots)}/{len(all_roots)} roots covered"
            },
            rationale=f"Enhanced optimization covering {len(all_roots)} keyword roots, prioritizing high-relevancy terms (80+ score), and using keywords sorted by relevancy score. Achieved natural readability while maximizing SEO potential."
        )
    
    def _parse_ai_output_to_optimized_seo(self, ai_output: Any, keyword_data: Dict[str, Any]) -> OptimizedSEO:
        """Parse AI output into OptimizedSEO structure."""
        from .schemas import OptimizedContent
        data = ai_output

        # If output is JSON string, parse it
        if isinstance(data, str):
            import json
            data = json.loads(data)

        # If output is a Pydantic model, convert to dict
        try:
            if hasattr(data, 'model_dump'):
                data = data.model_dump()
        except Exception:
            pass

        # If the agent returned a full SEOAnalysisResult, extract optimized_seo
        if isinstance(data, dict) and 'optimized_seo' in data:
            data = data['optimized_seo']

        # At this point, data should be the optimized_seo dict
        if not isinstance(data, dict):
            raise ValueError("AI output is not in expected optimized_seo dict format")

        # Build OptimizedSEO from dict tolerantly
        optimized_title = data.get('optimized_title') or {}
        optimized_bullets = data.get('optimized_bullets') or []
        optimized_backend_keywords = data.get('optimized_backend_keywords') or []
        keyword_strategy = data.get('keyword_strategy') or {}
        rationale = data.get('rationale') or ""

        # Normalize bullets and title into OptimizedContent
        def to_opt_content(obj: dict) -> OptimizedContent:
            return OptimizedContent(
                content=obj.get('content', ''),
                keywords_included=list(obj.get('keywords_included', [])),
                improvements=list(obj.get('improvements', [])),
                character_count=int(obj.get('character_count', len(obj.get('content', ''))))
            )

        title_content = to_opt_content(optimized_title)
        bullets_content = [to_opt_content(b) for b in optimized_bullets if isinstance(b, dict)]

        return OptimizedSEO(
            optimized_title=title_content,
            optimized_bullets=bullets_content,
            optimized_backend_keywords=list(optimized_backend_keywords),
            keyword_strategy=keyword_strategy,
            rationale=rationale
        )
    
    def _calculate_comparison_metrics(
        self, 
        current_seo: CurrentSEO, 
        optimized_seo: OptimizedSEO,
        keyword_data: Dict[str, Any]
    ) -> SEOComparison:
        """Calculate before/after comparison metrics from actual content."""

        # Build phrase lists and maps
        all_keywords = keyword_data.get("relevant_keywords", []) + keyword_data.get("design_keywords", [])
        phrases = [kw.get("phrase", "") for kw in all_keywords if kw.get("phrase")]
        phrase_to_volume = {kw.get("phrase", ""): (kw.get("search_volume") or 0) for kw in all_keywords}
        high_intent_phrases = [kw.get("phrase", "") for kw in keyword_data.get("high_intent_keywords", []) if kw.get("phrase")]

        # Debug logging
        logger.info(f"📊 [METRICS] Comparison data:")
        logger.info(f"   Total keywords for comparison: {len(phrases)}")
        logger.info(f"   High-intent keywords: {len(high_intent_phrases)}")

        # Current content strings
        current_title = current_seo.title_analysis.content
        current_bullets = [b.content for b in current_seo.bullets_analysis]
        current_backend = current_seo.backend_keywords
        current_text = " ".join([current_title] + current_bullets + [" ".join(current_backend)])

        # Optimized content strings
        opt_title = optimized_seo.optimized_title.content
        opt_bullets = [b.content for b in optimized_seo.optimized_bullets]
        opt_backend = optimized_seo.optimized_backend_keywords
        opt_text = " ".join([opt_title] + opt_bullets + [" ".join(opt_backend)])

        # Coverage details
        current_found, _ = extract_keywords_from_content(current_text, phrases)
        opt_found, _ = extract_keywords_from_content(opt_text, phrases)
        
        logger.info(f"   Current content keywords found: {len(current_found)}/{len(phrases)}")
        logger.info(f"   Optimized content keywords found: {len(opt_found)}/{len(phrases)}")

        total_kw = len(phrases)
        before_cov = len(set(current_found))
        after_cov = len(set(opt_found))
        before_pct = round((before_cov / total_kw * 100), 2) if total_kw else 0.0
        after_pct = round((after_cov / total_kw * 100), 2) if total_kw else 0.0
        new_added = [p for p in set(opt_found) if p not in set(current_found)]

        coverage_improvement = {
            "total_keywords": total_kw,
            "before_covered": before_cov,
            "after_covered": after_cov,
            "before_coverage_pct": before_pct,
            "after_coverage_pct": after_pct,
            "delta_pct_points": round(after_pct - before_pct, 2),
            "new_keywords_added": sorted(new_added)[:20]
        }

        # Intent coverage
        before_hi_intent = len([p for p in high_intent_phrases if p in set(current_found)])
        after_hi_intent = len([p for p in high_intent_phrases if p in set(opt_found)])
        intent_improvement = {
            "high_intent_total": len(high_intent_phrases),
            "before_covered": before_hi_intent,
            "after_covered": after_hi_intent,
            "delta": max(0, after_hi_intent - before_hi_intent)
        }

        # Volume capture (approximate)
        before_vol = sum(phrase_to_volume.get(p, 0) for p in set(current_found))
        after_vol = sum(phrase_to_volume.get(p, 0) for p in set(opt_found))
        volume_improvement = {
            "estimated_volume_before": before_vol,
            "estimated_volume_after": after_vol,
            "delta_volume": max(0, after_vol - before_vol)
        }

        # Character efficiency
        title_before = len(current_title or "")
        title_after = len(opt_title or "")
        backend_before = len(" ".join(current_backend) if current_backend else "")
        backend_after = len(" ".join(opt_backend) if opt_backend else "")
        char_efficiency = {
            "title_limit": 200,
            "title_before": title_before,
            "title_after": title_after,
            "title_utilization_before_pct": round((title_before / 200) * 100, 1) if 200 else 0,
            "title_utilization_after_pct": round((title_after / 200) * 100, 1) if 200 else 0,
            "backend_limit": 249,
            "backend_before": backend_before,
            "backend_after": backend_after,
        }

        # Summary metrics (simple heuristic)
        summary_metrics = {
            "overall_improvement_score": round(min(10.0, (after_pct - before_pct) / 10 + (after_hi_intent - before_hi_intent) / 2), 2),
            "priority_recommendations": max(1, min(5, len(new_added) // 4)),
        }

        return SEOComparison(
            coverage_improvement=coverage_improvement,
            intent_improvement=intent_improvement,
            volume_improvement=volume_improvement,
            character_efficiency=char_efficiency,
            summary_metrics=summary_metrics
        )
    
    def _should_use_ai_optimization(self) -> bool:
        """Always use AI optimization (no rule-based fallback)."""
        return True
    
    def _correct_keyword_hallucination(self, optimized_seo: OptimizedSEO, keyword_validator: SEOKeywordValidator) -> OptimizedSEO:
        """
        Correct keyword hallucination by replacing invalid keywords with valid research keywords.
        
        Args:
            optimized_seo: SEO output with potential hallucinated keywords
            keyword_validator: Validator instance with research keywords
            
        Returns:
            Corrected SEO output with only valid keywords
        """
        from .schemas import OptimizedContent
        
        logger.info("🔧 Correcting keyword hallucination in SEO output")
        
        # Get available valid keywords
        available_keywords = keyword_validator.get_available_keywords()
        
        # Correct title keywords
        title_keywords = optimized_seo.optimized_title.keywords_included
        valid_title_keywords, _ = keyword_validator.validate_keywords_against_research(title_keywords)
        
        # If title has invalid keywords, replace with top valid keywords
        if len(valid_title_keywords) < len(title_keywords):
            top_keywords = keyword_validator.get_top_keywords_by_relevancy(available_keywords, 5)
            corrected_title_keywords = keyword_validator.allocate_keywords_for_content_type(top_keywords, 'title')
            
            # Update title content to use corrected keywords
            corrected_title_content = self._rebuild_content_with_keywords(
                optimized_seo.optimized_title.content, 
                corrected_title_keywords
            )
            
            optimized_seo.optimized_title = OptimizedContent(
                content=corrected_title_content,
                keywords_included=corrected_title_keywords,
                improvements=optimized_seo.optimized_title.improvements + ["Keyword hallucination corrected"],
                character_count=len(corrected_title_content)
            )
        
        # Correct bullet keywords
        corrected_bullets = []
        for bullet in optimized_seo.optimized_bullets:
            bullet_keywords = bullet.keywords_included
            valid_bullet_keywords, _ = keyword_validator.validate_keywords_against_research(bullet_keywords)
            
            # If bullet has invalid keywords, replace with valid ones
            if len(valid_bullet_keywords) < len(bullet_keywords):
                top_keywords = keyword_validator.get_top_keywords_by_relevancy(available_keywords, 2)
                corrected_bullet_keywords = keyword_validator.allocate_keywords_for_content_type(top_keywords, 'bullets')
                
                # Update bullet content
                corrected_bullet_content = self._rebuild_content_with_keywords(
                    bullet.content, 
                    corrected_bullet_keywords
                )
                
                corrected_bullets.append(OptimizedContent(
                    content=corrected_bullet_content,
                    keywords_included=corrected_bullet_keywords,
                    improvements=bullet.improvements + ["Keyword hallucination corrected"],
                    character_count=len(corrected_bullet_content)
                ))
            else:
                corrected_bullets.append(bullet)
        
        optimized_seo.optimized_bullets = corrected_bullets
        
        # Correct backend keywords
        backend_keywords = optimized_seo.optimized_backend_keywords
        valid_backend_keywords, _ = keyword_validator.validate_keywords_against_research(backend_keywords)
        
        # If backend has invalid keywords, replace with valid ones
        if len(valid_backend_keywords) < len(backend_keywords):
            top_keywords = keyword_validator.get_top_keywords_by_relevancy(available_keywords, 15)
            corrected_backend_keywords = keyword_validator.allocate_keywords_for_content_type(top_keywords, 'backend')
            optimized_seo.optimized_backend_keywords = corrected_backend_keywords
        
        logger.info("✅ Keyword hallucination correction completed")
        
        return optimized_seo
    
    def _rebuild_content_with_keywords(self, content: str, keywords: List[str]) -> str:
        """
        Rebuild content using only valid keywords.
        This is a simple implementation - in practice, you might want more sophisticated content rebuilding.
        """
        if not keywords:
            return content
        
        # Simple approach: append keywords to content if they're not already present
        content_lower = content.lower()
        missing_keywords = [kw for kw in keywords if kw.lower() not in content_lower]
        
        if missing_keywords:
            # Add missing keywords to the end
            return content + " " + " ".join(missing_keywords)
        
        return content
    
    def _deduplicate_keywords_across_content(self, optimized_seo: OptimizedSEO) -> OptimizedSEO:
        """
        Remove duplicate keywords across title, bullets, and backend keywords.
        Priority: Title > Bullets > Backend (higher priority keeps the keyword)
        
        Args:
            optimized_seo: The optimized SEO content with potential duplicates
            
        Returns:
            OptimizedSEO with deduplicated keywords
        """
        from .schemas import OptimizedContent
        
        logger.info("🔄 [DEDUPLICATION] Removing duplicate keywords across all content")
        
        # Track used keywords (case-insensitive)
        used_keywords = set()
        
        # Step 1: Track title keywords (highest priority - keep all)
        title_keywords = optimized_seo.optimized_title.keywords_included
        used_keywords.update([kw.lower() for kw in title_keywords])
        logger.info(f"   📌 Title: {len(title_keywords)} keywords (all kept)")
        
        # Step 2: Deduplicate bullets (remove keywords already in title or previous bullets)
        total_removed_from_bullets = 0
        updated_bullets = []
        
        for i, bullet in enumerate(optimized_seo.optimized_bullets, 1):
            original_count = len(bullet.keywords_included)
            
            # Keep only keywords not already used
            unique_keywords = [
                kw for kw in bullet.keywords_included 
                if kw.lower() not in used_keywords
            ]
            
            removed_count = original_count - len(unique_keywords)
            total_removed_from_bullets += removed_count
            
            if removed_count > 0:
                logger.info(f"   🔹 Bullet {i}: Removed {removed_count} duplicates ({original_count} → {len(unique_keywords)})")
            
            # Create updated bullet with unique keywords only
            updated_bullets.append(OptimizedContent(
                content=bullet.content,
                keywords_included=unique_keywords,
                improvements=bullet.improvements,
                character_count=bullet.character_count
            ))
            
            # Add unique keywords to used set
            used_keywords.update([kw.lower() for kw in unique_keywords])
        
        optimized_seo.optimized_bullets = updated_bullets
        logger.info(f"   ✅ Bullets: Removed {total_removed_from_bullets} total duplicates")
        
        # Step 3: Deduplicate backend keywords (lowest priority)
        original_backend_count = len(optimized_seo.optimized_backend_keywords)
        
        unique_backend = [
            kw for kw in optimized_seo.optimized_backend_keywords
            if kw.lower() not in used_keywords
        ]
        
        removed_from_backend = original_backend_count - len(unique_backend)
        optimized_seo.optimized_backend_keywords = unique_backend
        
        logger.info(f"   🔹 Backend: Removed {removed_from_backend} duplicates ({original_backend_count} → {len(unique_backend)})")
        
        # Summary
        total_removed = total_removed_from_bullets + removed_from_backend
        logger.info(f"")
        logger.info(f"✅ [DEDUPLICATION COMPLETE]")
        logger.info(f"   Total Duplicates Removed: {total_removed}")
        logger.info(f"   Final Unique Keywords: {len(used_keywords)}")
        
        return optimized_seo
    
    def _generate_rule_based_optimizations(
        self,
        current_content: Dict[str, Any],
        keyword_data: Dict[str, Any]
    ) -> OptimizedSEO:
        """Generate rule-based optimization suggestions that fulfill MVP requirements."""
        
        # Get keywords by category and intent
        relevant_keywords = keyword_data["relevant_keywords"]
        design_keywords = keyword_data["design_keywords"]
        high_intent_keywords = keyword_data["high_intent_keywords"]
        high_volume_keywords = keyword_data["high_volume_keywords"]
        
        # Combine relevant + design for optimization
        all_good_keywords = relevant_keywords + design_keywords
        
        # Sort by relevancy score (descending), then by search volume, then by intent score
        sorted_keywords = sorted(all_good_keywords, 
                               key=lambda x: (x.get("relevancy_score", 0), x.get("search_volume", 0), x.get("intent_score", 0)), 
                               reverse=True)
        
        # Get all unique roots from good keywords
        all_roots = set()
        root_to_best_keyword = {}
        for kw in sorted_keywords:
            root = kw.get("root", "")
            if root and root not in root_to_best_keyword:
                root_to_best_keyword[root] = kw.get("phrase", "")
                all_roots.add(root)
        
        # Select top keywords for title optimization
        # Prioritize: high intent + high volume + covers different roots
        title_keywords = []
        used_roots = set()
        
        # First, get highest relevancy keywords that cover different roots
        for kw in sorted_keywords[:15]:  # Look at top 15
            root = kw.get("root", "")
            phrase = kw.get("phrase", "")
            relevancy = kw.get("relevancy_score", 0)
            volume = kw.get("search_volume", 0)
            
            # Handle None values safely
            if relevancy is None:
                relevancy = 0
            if volume is None:
                volume = 0
            
            # Prioritize high relevancy (80+) and good volume (300+)
            if relevancy >= 80 and volume >= 300 and root not in used_roots and len(title_keywords) < 4:
                title_keywords.append(phrase)
                used_roots.add(root)
        
        # Fill remaining slots with high-relevancy terms
        for kw in sorted_keywords:
            phrase = kw.get("phrase", "")
            relevancy = kw.get("relevancy_score", 0)
            
            # Handle None values safely
            if relevancy is None:
                relevancy = 0
                
            if len(title_keywords) < 5 and phrase not in title_keywords and relevancy >= 70:
                title_keywords.append(phrase)
        
        # Create natural-sounding optimized title
        brand = current_content.get("brand", "BREWER")
        primary_keyword = title_keywords[0] if title_keywords else "freeze dried strawberries"
        
        # Build title with natural flow
        title_parts = []
        if brand:
            title_parts.append(brand)
        
        # Add pack info
        title_parts.append("Bulk")
        
        # Add primary keyword
        title_parts.append(primary_keyword.title())
        
        # Add key attributes
        title_parts.append("- Organic")
        title_parts.append("No Sugar Added")
        
        # Add secondary keyword if different
        if len(title_keywords) > 1:
            secondary = title_keywords[1]
            if "organic" not in secondary.lower():
                title_parts.append(f"Premium {secondary.title()}")
        
        # Add use cases
        title_parts.append("for Snacking, Baking & Travel")
        
        optimized_title_content = " ".join(title_parts)[:200]  # Amazon limit
        
        optimized_title = {
            "content": optimized_title_content,
            "keywords_included": title_keywords[:3],
            "improvements": [
                f"Covers {len(used_roots)} keyword roots",
                f"Uses {len([k for k in all_good_keywords if (k.get('relevancy_score') or 0) >= 80])} high-relevancy keywords",
                f"Prioritizes {sum((k.get('relevancy_score') or 0) for k in all_good_keywords[:3])//3} avg relevancy score",
                "Natural, readable format"
            ],
            "character_count": len(optimized_title_content)
        }
        
        # Create optimized bullets focusing on different keyword clusters
        optimized_bullets = []
        bullet_templates = [
            ("Flavor & Quality", "Enjoy the naturally sweet, tangy crunch of {} bursting with real fruit flavor."),
            ("Organic & Healthy", "Our {} are organic, no sugar added, and made from farm-fresh strawberries."),
            ("Versatile Use", "Perfect {} for baking, smoothies, cereals, and on-the-go snacking."),
            ("Travel Ready", "Lightweight and shelf-stable {} ideal for hiking, camping, and travel adventures."),
            ("Bulk Value", "Buy in bulk and enjoy premium quality {} whenever you need them.")
        ]
        
        for i, (focus, template) in enumerate(bullet_templates):
            if i < len(sorted_keywords):
                keyword = sorted_keywords[i].get("phrase", "")
                bullet_content = f"✅ {focus}: " + template.format(keyword)
                optimized_bullets.append({
                    "content": bullet_content,
                    "keywords_included": [keyword],
                    "improvements": [f"Focused on {focus.lower()}", "Clear value proposition"],
                    "character_count": len(bullet_content)
                })
        
        # Backend keywords: Use remaining good keywords not in title/bullets
        used_in_content = set(title_keywords)
        for bullet in optimized_bullets:
            used_in_content.update(bullet["keywords_included"])
        
        backend_keywords = []
        for kw in sorted_keywords:
            phrase = kw.get("phrase", "")
            if phrase not in used_in_content and len(backend_keywords) < 15:
                backend_keywords.append(phrase)
        
        # Task 11: Apply AI-powered variant optimization before generating variations
        try:
            from app.local_agents.scoring.subagents.keyword_variant_agent import apply_variant_optimization_ai
            # Use AI to remove redundant singular/plural variants from good keywords
            optimized_keywords = apply_variant_optimization_ai(all_good_keywords)
            logger.info(f"[Task11-AI] Applied AI variant optimization: {len(all_good_keywords)} -> {len(optimized_keywords)} keywords")
        except Exception as e:
            logger.warning(f"[Task11-AI] AI variant optimization failed, using original keywords: {e}")
            optimized_keywords = all_good_keywords
        
        # Add misspellings and variations (using optimized keyword list)
        variations = []
        for kw in optimized_keywords:
            phrase = kw.get("phrase", "")
            # Add common variations (punctuation, spacing only - no singular/plural thanks to AI)
            if "freeze dried" in phrase:
                variations.append(phrase.replace("freeze dried", "freeze-dried"))
                variations.append(phrase.replace("freeze dried", "freezedried"))
        
        # Remove duplicates and already used variations
        filtered_variations = []
        for variation in variations:
            if variation not in used_in_content and variation not in backend_keywords:
                filtered_variations.append(variation)
        
        backend_keywords.extend(filtered_variations[:5])
        
        from .schemas import OptimizedContent
        
        return OptimizedSEO(
            optimized_title=OptimizedContent(**optimized_title),
            optimized_bullets=[OptimizedContent(**bullet) for bullet in optimized_bullets],
            optimized_backend_keywords=backend_keywords,
            keyword_strategy={
                "primary_focus": f"Cover {len(all_roots)} keyword roots",
                "secondary_focus": f"Prioritize {len([k for k in all_good_keywords if (k.get('relevancy_score') or 0) >= 80])} high-relevancy keywords",
                "relevancy_strategy": f"Use {sum((k.get('relevancy_score') or 0) for k in all_good_keywords[:5])//5} avg relevancy score",
                "character_optimization": True,
                "root_coverage": f"{len(used_roots)}/{len(all_roots)} roots covered"
            },
            rationale=f"Enhanced optimization covering {len(all_roots)} keyword roots, prioritizing high-relevancy terms (80+ score), and using keywords sorted by relevancy score. Achieved natural readability while maximizing SEO potential."
        )
    
    def _parse_ai_output_to_optimized_seo(self, ai_output: Any, keyword_data: Dict[str, Any]) -> OptimizedSEO:

        """Parse AI output into OptimizedSEO structure."""

        from .schemas import OptimizedContent

        data = ai_output



        # If output is JSON string, parse it

        if isinstance(data, str):

            import json

            data = json.loads(data)



        # If output is a Pydantic model, convert to dict

        try:

            if hasattr(data, 'model_dump'):

                data = data.model_dump()

        except Exception:

            pass



        # If the agent returned a full SEOAnalysisResult, extract optimized_seo

        if isinstance(data, dict) and 'optimized_seo' in data:

            data = data['optimized_seo']



        # At this point, data should be the optimized_seo dict

        if not isinstance(data, dict):

            raise ValueError("AI output is not in expected optimized_seo dict format")



        # Build OptimizedSEO from dict tolerantly

        optimized_title = data.get('optimized_title') or {}

        optimized_bullets = data.get('optimized_bullets') or []

        optimized_backend_keywords = data.get('optimized_backend_keywords') or []

        keyword_strategy = data.get('keyword_strategy') or {}

        rationale = data.get('rationale') or ""



        # Normalize bullets and title into OptimizedContent

        def to_opt_content(obj: dict) -> OptimizedContent:

            return OptimizedContent(

                content=obj.get('content', ''),

                keywords_included=list(obj.get('keywords_included', [])),

                improvements=list(obj.get('improvements', [])),

                character_count=int(obj.get('character_count', len(obj.get('content', ''))))

            )



        title_content = to_opt_content(optimized_title)

        bullets_content = [to_opt_content(b) for b in optimized_bullets if isinstance(b, dict)]



        return OptimizedSEO(

            optimized_title=title_content,

            optimized_bullets=bullets_content,

            optimized_backend_keywords=list(optimized_backend_keywords),

            keyword_strategy=keyword_strategy,

            rationale=rationale

        )
    
    
    
    def _calculate_comparison_metrics(

        self, 

        current_seo: CurrentSEO, 

        optimized_seo: OptimizedSEO,

        keyword_data: Dict[str, Any]

    ) -> SEOComparison:

        """Calculate before/after comparison metrics from actual content."""



        # Build phrase lists and maps

        all_keywords = keyword_data.get("relevant_keywords", []) + keyword_data.get("design_keywords", [])

        phrases = [kw.get("phrase", "") for kw in all_keywords if kw.get("phrase")]

        phrase_to_volume = {kw.get("phrase", ""): (kw.get("search_volume") or 0) for kw in all_keywords}
        high_intent_phrases = [kw.get("phrase", "") for kw in keyword_data.get("high_intent_keywords", []) if kw.get("phrase")]



        # Current content strings

        current_title = current_seo.title_analysis.content

        current_bullets = [b.content for b in current_seo.bullets_analysis]

        current_backend = current_seo.backend_keywords

        current_text = " ".join([current_title] + current_bullets + [" ".join(current_backend)])



        # Optimized content strings

        opt_title = optimized_seo.optimized_title.content

        opt_bullets = [b.content for b in optimized_seo.optimized_bullets]

        opt_backend = optimized_seo.optimized_backend_keywords

        opt_text = " ".join([opt_title] + opt_bullets + [" ".join(opt_backend)])



        # Coverage details

        current_found, _ = extract_keywords_from_content(current_text, phrases)

        opt_found, _ = extract_keywords_from_content(opt_text, phrases)



        total_kw = len(phrases)

        before_cov = len(set(current_found))

        after_cov = len(set(opt_found))

        before_pct = round((before_cov / total_kw * 100), 2) if total_kw else 0.0

        after_pct = round((after_cov / total_kw * 100), 2) if total_kw else 0.0

        new_added = [p for p in set(opt_found) if p not in set(current_found)]



        coverage_improvement = {

            "total_keywords": total_kw,

            "before_covered": before_cov,

            "after_covered": after_cov,

            "before_coverage_pct": before_pct,

            "after_coverage_pct": after_pct,

            "delta_pct_points": round(after_pct - before_pct, 2),

            "new_keywords_added": sorted(new_added)[:20]

        }



        # Intent coverage

        before_hi_intent = len([p for p in high_intent_phrases if p in set(current_found)])

        after_hi_intent = len([p for p in high_intent_phrases if p in set(opt_found)])

        intent_improvement = {

            "high_intent_total": len(high_intent_phrases),

            "before_covered": before_hi_intent,

            "after_covered": after_hi_intent,

            "delta": max(0, after_hi_intent - before_hi_intent)

        }



        # Volume capture (approximate)

        before_vol = sum(phrase_to_volume.get(p, 0) for p in set(current_found))

        after_vol = sum(phrase_to_volume.get(p, 0) for p in set(opt_found))

        volume_improvement = {

            "estimated_volume_before": before_vol,

            "estimated_volume_after": after_vol,

            "delta_volume": max(0, after_vol - before_vol)

        }



        # Character efficiency

        title_before = len(current_title or "")

        title_after = len(opt_title or "")

        backend_before = len(" ".join(current_backend) if current_backend else "")

        backend_after = len(" ".join(opt_backend) if opt_backend else "")

        char_efficiency = {

            "title_limit": 200,

            "title_before": title_before,

            "title_after": title_after,

            "title_utilization_before_pct": round((title_before / 200) * 100, 1) if 200 else 0,

            "title_utilization_after_pct": round((title_after / 200) * 100, 1) if 200 else 0,

            "backend_limit": 249,

            "backend_before": backend_before,

            "backend_after": backend_after,

        }



        # Summary metrics (simple heuristic)

        summary_metrics = {

            "overall_improvement_score": round(min(10.0, (after_pct - before_pct) / 10 + (after_hi_intent - before_hi_intent) / 2), 2),

            "priority_recommendations": max(1, min(5, len(new_added) // 4)),

        }



        return SEOComparison(

            coverage_improvement=coverage_improvement,

            intent_improvement=intent_improvement,

            volume_improvement=volume_improvement,

            character_efficiency=char_efficiency,

            summary_metrics=summary_metrics

        )
    
    
    
    def _should_use_ai_optimization(self) -> bool:

        """Always use AI optimization (no rule-based fallback)."""

        return True
    
    def _correct_keyword_hallucination(self, optimized_seo: OptimizedSEO, keyword_validator: SEOKeywordValidator) -> OptimizedSEO:
        """
        Correct keyword hallucination by replacing invalid keywords with valid research keywords.
        
        Args:
            optimized_seo: SEO output with potential hallucinated keywords
            keyword_validator: Validator instance with research keywords
            
        Returns:
            Corrected SEO output with only valid keywords
        """
        from .schemas import OptimizedContent
        
        logger.info("🔧 Correcting keyword hallucination in SEO output")
        
        # Get available valid keywords
        available_keywords = keyword_validator.get_available_keywords()
        
        # Correct title keywords
        title_keywords = optimized_seo.optimized_title.keywords_included
        valid_title_keywords, _ = keyword_validator.validate_keywords_against_research(title_keywords)
        
        # If title has invalid keywords, replace with top valid keywords
        if len(valid_title_keywords) < len(title_keywords):
            top_keywords = keyword_validator.get_top_keywords_by_relevancy(available_keywords, 5)
            corrected_title_keywords = keyword_validator.allocate_keywords_for_content_type(top_keywords, 'title')
            
            # Update title content to use corrected keywords
            corrected_title_content = self._rebuild_content_with_keywords(
                optimized_seo.optimized_title.content, 
                corrected_title_keywords
            )
            
            optimized_seo.optimized_title = OptimizedContent(
                content=corrected_title_content,
                keywords_included=corrected_title_keywords,
                improvements=optimized_seo.optimized_title.improvements + ["Keyword hallucination corrected"],
                character_count=len(corrected_title_content)
            )
        
        # Correct bullet keywords
        corrected_bullets = []
        for bullet in optimized_seo.optimized_bullets:
            bullet_keywords = bullet.keywords_included
            valid_bullet_keywords, _ = keyword_validator.validate_keywords_against_research(bullet_keywords)
            
            # If bullet has invalid keywords, replace with valid ones
            if len(valid_bullet_keywords) < len(bullet_keywords):
                top_keywords = keyword_validator.get_top_keywords_by_relevancy(available_keywords, 2)
                corrected_bullet_keywords = keyword_validator.allocate_keywords_for_content_type(top_keywords, 'bullets')
                
                # Update bullet content
                corrected_bullet_content = self._rebuild_content_with_keywords(
                    bullet.content, 
                    corrected_bullet_keywords
                )
                
                corrected_bullets.append(OptimizedContent(
                    content=corrected_bullet_content,
                    keywords_included=corrected_bullet_keywords,
                    improvements=bullet.improvements + ["Keyword hallucination corrected"],
                    character_count=len(corrected_bullet_content)
                ))
            else:
                corrected_bullets.append(bullet)
        
        optimized_seo.optimized_bullets = corrected_bullets
        
        # Correct backend keywords
        backend_keywords = optimized_seo.optimized_backend_keywords
        valid_backend_keywords, _ = keyword_validator.validate_keywords_against_research(backend_keywords)
        
        # If backend has invalid keywords, replace with valid ones
        if len(valid_backend_keywords) < len(backend_keywords):
            top_keywords = keyword_validator.get_top_keywords_by_relevancy(available_keywords, 15)
            corrected_backend_keywords = keyword_validator.allocate_keywords_for_content_type(top_keywords, 'backend')
            optimized_seo.optimized_backend_keywords = corrected_backend_keywords
        
        logger.info("✅ Keyword hallucination correction completed")
        
        return optimized_seo
    
    def _rebuild_content_with_keywords(self, content: str, keywords: List[str]) -> str:
        """
        Rebuild content using only valid keywords.
        This is a simple implementation - in practice, you might want more sophisticated content rebuilding.
        """
        if not keywords:
            return content
        
        # Simple approach: append keywords to content if they're not already present
        content_lower = content.lower()
        missing_keywords = [kw for kw in keywords if kw.lower() not in content_lower]
        
        if missing_keywords:
            # Add missing keywords to the end
            return content + " " + " ".join(missing_keywords)
        
        return content
    
    def _deduplicate_keywords_across_content(self, optimized_seo: OptimizedSEO) -> OptimizedSEO:
        """
        Remove duplicate keywords across title, bullets, and backend keywords.
        Priority: Title > Bullets > Backend (higher priority keeps the keyword)
        
        Args:
            optimized_seo: The optimized SEO content with potential duplicates
            
        Returns:
            OptimizedSEO with deduplicated keywords
        """
        from .schemas import OptimizedContent
        
        logger.info("🔄 [DEDUPLICATION] Removing duplicate keywords across all content")
        
        # Track used keywords (case-insensitive)
        used_keywords = set()
        
        # Step 1: Track title keywords (highest priority - keep all)
        title_keywords = optimized_seo.optimized_title.keywords_included
        used_keywords.update([kw.lower() for kw in title_keywords])
        logger.info(f"   📌 Title: {len(title_keywords)} keywords (all kept)")
        
        # Step 2: Deduplicate bullets (remove keywords already in title or previous bullets)
        total_removed_from_bullets = 0
        updated_bullets = []
        
        for i, bullet in enumerate(optimized_seo.optimized_bullets, 1):
            original_count = len(bullet.keywords_included)
            
            # Keep only keywords not already used
            unique_keywords = [
                kw for kw in bullet.keywords_included 
                if kw.lower() not in used_keywords
            ]
            
            removed_count = original_count - len(unique_keywords)
            total_removed_from_bullets += removed_count
            
            if removed_count > 0:
                logger.info(f"   🔹 Bullet {i}: Removed {removed_count} duplicates ({original_count} → {len(unique_keywords)})")
            
            # Create updated bullet with unique keywords only
            updated_bullets.append(OptimizedContent(
                content=bullet.content,
                keywords_included=unique_keywords,
                improvements=bullet.improvements,
                character_count=bullet.character_count
            ))
            
            # Add unique keywords to used set
            used_keywords.update([kw.lower() for kw in unique_keywords])
        
        optimized_seo.optimized_bullets = updated_bullets
        logger.info(f"   ✅ Bullets: Removed {total_removed_from_bullets} total duplicates")
        
        # Step 3: Deduplicate backend keywords (lowest priority)
        original_backend_count = len(optimized_seo.optimized_backend_keywords)
        
        unique_backend = [
            kw for kw in optimized_seo.optimized_backend_keywords
            if kw.lower() not in used_keywords
        ]
        
        removed_from_backend = original_backend_count - len(unique_backend)
        optimized_seo.optimized_backend_keywords = unique_backend
        
        logger.info(f"   🔹 Backend: Removed {removed_from_backend} duplicates ({original_backend_count} → {len(unique_backend)})")
        
        # Summary
        total_removed = total_removed_from_bullets + removed_from_backend
        logger.info(f"")
        logger.info(f"✅ [DEDUPLICATION COMPLETE]")
        logger.info(f"   Total Duplicates Removed: {total_removed}")
        logger.info(f"   Final Unique Keywords: {len(used_keywords)}")
        
        return optimized_seo
