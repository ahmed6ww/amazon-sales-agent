"""
SEO Agent Runner

Manages the execution and orchestration of SEO optimization analysis.
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .agent import seo_agent
from .helper_methods import (
    optimize_product_title,
    generate_bullet_points,
    create_backend_keywords,
    analyze_content_gaps,
    identify_competitive_advantages,
    calculate_seo_score
)
from .schemas import (
    SEOOptimization,
    SEOAnalysisResult,
    TitleOptimization,
    BulletPointOptimization,
    BackendKeywordOptimization,
    ContentGap,
    CompetitiveAdvantage,
    SEOScore,
    SEOConfig
)


class SEORunner:
    """
    SEO Agent runner for managing Amazon listing optimization workflow.
    """
    
    def __init__(self, config: Optional[SEOConfig] = None):
        """
        Initialize SEO runner with configuration.
        
        Args:
            config: SEO optimization configuration
        """
        self.config = config or SEOConfig()
        self.agent = seo_agent
    
    def run_full_seo_optimization(
        self,
        product_info: Dict[str, Any],
        keyword_analysis: Dict[str, Any],
        scoring_analysis: Dict[str, Any],
        competitor_data: Optional[Dict[str, Any]] = None
    ) -> SEOAnalysisResult:
        """
        Run complete SEO optimization workflow using the agent.
        
        Args:
            product_info: Product information from research agent
            keyword_analysis: Keyword analysis results
            scoring_analysis: Scoring analysis with prioritized keywords
            competitor_data: Optional competitor analysis data
        
        Returns:
            SEOAnalysisResult: Complete SEO optimization analysis
        """
        
        start_time = time.time()
        
        try:
            # Extract data for optimization
            current_listing = {
                "title": product_info.get("title", ""),
                "bullets": product_info.get("bullets", []),
                "features": product_info.get("features", []),
                "brand": product_info.get("brand", ""),
                "category": product_info.get("category", "")
            }
            
            # Extract keywords from scoring analysis
            critical_keywords = self._extract_keywords_by_priority(scoring_analysis, "critical")
            high_priority_keywords = self._extract_keywords_by_priority(scoring_analysis, "high")
            medium_priority_keywords = self._extract_keywords_by_priority(scoring_analysis, "medium")
            opportunity_keywords = self._extract_opportunity_keywords(scoring_analysis)
            
            # Run SEO optimization workflow
            seo_optimization = self.run_direct_optimization(
                current_listing=current_listing,
                critical_keywords=critical_keywords,
                high_priority_keywords=high_priority_keywords,
                medium_priority_keywords=medium_priority_keywords,
                opportunity_keywords=opportunity_keywords,
                keyword_analysis=keyword_analysis,
                scoring_analysis=scoring_analysis,
                competitor_data=competitor_data or {}
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Generate implementation priority
            implementation_priority = self._generate_implementation_priority(seo_optimization)
            
            # Predict performance improvements
            performance_predictions = self._predict_performance_improvements(seo_optimization)
            
            # Calculate confidence level
            confidence_level = self._calculate_confidence_level(seo_optimization)
            
            # Set next review date
            next_review_date = (datetime.now() + timedelta(days=30)).isoformat()
            
            return SEOAnalysisResult(
                product_info=product_info,
                keyword_insights=keyword_analysis,
                scoring_insights=scoring_analysis,
                seo_optimization=seo_optimization,
                implementation_priority=implementation_priority,
                performance_predictions=performance_predictions,
                processing_time=round(processing_time, 2),
                confidence_level=confidence_level,
                next_review_date=next_review_date
            )
            
        except Exception as e:
            print(f"Error in SEO optimization: {str(e)}")
            raise e
    
    def run_direct_optimization(
        self,
        current_listing: Dict[str, Any],
        critical_keywords: List[str],
        high_priority_keywords: List[str],
        medium_priority_keywords: List[str],
        opportunity_keywords: List[str],
        keyword_analysis: Dict[str, Any],
        scoring_analysis: Dict[str, Any],
        competitor_data: Dict[str, Any]
    ) -> SEOOptimization:
        """
        Run direct SEO optimization without agent orchestration.
        
        Args:
            current_listing: Current listing content
            critical_keywords: Critical priority keywords
            high_priority_keywords: High priority keywords
            medium_priority_keywords: Medium priority keywords
            opportunity_keywords: Opportunity keywords
            keyword_analysis: Keyword analysis data
            scoring_analysis: Scoring analysis data
            competitor_data: Competitor analysis data
        
        Returns:
            SEOOptimization: Complete optimization package
        """
        
        # Normalize listing fields to strings/lists of strings
        def _to_text(value: Any) -> str:
            if isinstance(value, str):
                return value
            if isinstance(value, dict):
                for key in ("text", "value", "content", "title", "name"):
                    v = value.get(key)
                    if isinstance(v, str):
                        return v
                # Fallback to string representation
                return str(value)
            return str(value) if value is not None else ""

        def _to_text_list(values: Any) -> List[str]:
            if isinstance(values, list):
                return [_to_text(v) for v in values]
            return []

        current_listing = {
            "title": _to_text(current_listing.get("title", "")),
            "bullets": _to_text_list(current_listing.get("bullets", [])),
            "features": _to_text_list(current_listing.get("features", [])),
            "brand": _to_text(current_listing.get("brand", "")),
            "category": _to_text(current_listing.get("category", "")),
        }

        # 1. Title Optimization
        title_optimization = optimize_product_title(
            current_title=current_listing.get("title", ""),
            critical_keywords=critical_keywords,
            high_priority_keywords=high_priority_keywords,
            product_info=current_listing,
            character_limit=self.config.character_limits["title"]
        )
        
        # 2. Bullet Points Optimization
        bullet_optimization = generate_bullet_points(
            current_bullets=current_listing.get("bullets", []),
            critical_keywords=critical_keywords,
            high_priority_keywords=high_priority_keywords,
            product_info=current_listing,
            customer_insights={}
        )
        
        # 3. Backend Keywords Optimization
        backend_optimization = create_backend_keywords(
            title=title_optimization.recommended_title,
            bullets=bullet_optimization.recommended_bullets,
            critical_keywords=critical_keywords,
            high_priority_keywords=high_priority_keywords,
            medium_priority_keywords=medium_priority_keywords,
            opportunity_keywords=opportunity_keywords,
            character_limit=self.config.character_limits["backend_keywords"]
        )
        
        # 4. Content Gap Analysis
        content_gaps = analyze_content_gaps(
            current_listing=current_listing,
            keyword_analysis=keyword_analysis,
            scoring_analysis=scoring_analysis,
            competitor_data=competitor_data
        )
        
        # 5. Competitive Advantages
        competitive_advantages = identify_competitive_advantages(
            product_info=current_listing,
            keyword_analysis=keyword_analysis,
            competitor_data=competitor_data
        )
        
        # 6. SEO Score Calculation
        seo_score = calculate_seo_score(
            title_optimization=title_optimization,
            bullet_optimization=bullet_optimization,
            backend_optimization=backend_optimization,
            content_gaps=content_gaps,
            competitive_advantages=competitive_advantages
        )
        
        # 7. Generate Quick Wins and Strategy
        quick_wins = self._generate_quick_wins(
            title_optimization, bullet_optimization, backend_optimization, content_gaps
        )
        
        long_term_strategy = self._generate_long_term_strategy(
            seo_score, competitive_advantages, content_gaps
        )
        
        return SEOOptimization(
            title_optimization=title_optimization,
            bullet_optimization=bullet_optimization,
            backend_optimization=backend_optimization,
            content_gaps=content_gaps,
            competitive_advantages=competitive_advantages,
            seo_score=seo_score,
            quick_wins=quick_wins,
            long_term_strategy=long_term_strategy
        )
    
    def _extract_keywords_by_priority(self, scoring_analysis: Dict[str, Any], priority: str) -> List[str]:
        """Extract keywords by priority level from scoring analysis."""
        keywords: List[str] = []
        
        data = scoring_analysis.get(f"{priority}_keywords", [])
        if isinstance(data, list):
            for kw in data:
                # Pydantic object
                if hasattr(kw, 'keyword_phrase'):
                    value = getattr(kw, 'keyword_phrase')
                # Dict from .dict()
                elif isinstance(kw, dict):
                    value = kw.get("keyword_phrase") or kw.get("keyword") or kw.get("keyword_phrase", "")
                else:
                    value = kw
                # Coerce to string
                if value is None:
                    continue
                keywords.append(str(value))
        
        return keywords[:10]
    
    def _extract_opportunity_keywords(self, scoring_analysis: Dict[str, Any]) -> List[str]:
        """Extract opportunity keywords from scoring analysis."""
        keywords: List[str] = []
        
        opportunities = scoring_analysis.get("top_opportunities", [])
        if isinstance(opportunities, list):
            for opp in opportunities:
                if hasattr(opp, 'keyword_phrase'):
                    value = getattr(opp, 'keyword_phrase')
                elif isinstance(opp, dict):
                    value = opp.get("keyword_phrase") or opp.get("keyword") or opp.get("keyword_phrase", "")
                else:
                    value = opp
                if value is None:
                    continue
                keywords.append(str(value))
        
        return keywords[:15]
    
    def _generate_quick_wins(
        self,
        title_opt: TitleOptimization,
        bullet_opt: BulletPointOptimization,
        backend_opt: BackendKeywordOptimization,
        content_gaps: List[ContentGap]
    ) -> List[str]:
        """Generate list of quick win recommendations."""
        quick_wins = []
        
        # Title quick wins
        if title_opt.improvement_score > 20:
            quick_wins.append(f"Update title to include {len(title_opt.keywords_added)} critical keywords")
        
        # Backend keywords quick wins
        if len(backend_opt.opportunity_keywords) > 0:
            quick_wins.append(f"Add {len(backend_opt.opportunity_keywords)} high-opportunity backend keywords")
        
        # Content gap quick wins
        critical_gaps = [gap for gap in content_gaps if gap.priority == "critical"]
        if critical_gaps:
            quick_wins.append(f"Address {len(critical_gaps)} critical content gaps")
        
        # Bullet points quick wins
        if bullet_opt.keywords_coverage < 5:
            quick_wins.append("Increase keyword coverage in bullet points")
        
        return quick_wins
    
    def _generate_long_term_strategy(
        self,
        seo_score: SEOScore,
        competitive_advantages: List[CompetitiveAdvantage],
        content_gaps: List[ContentGap]
    ) -> List[str]:
        """Generate long-term SEO strategy recommendations."""
        strategy = []
        
        # Performance improvement strategy
        if seo_score.overall_score < 80:
            strategy.append("Focus on improving overall SEO score through systematic optimization")
        
        # Competitive positioning strategy
        if len(competitive_advantages) > 0:
            strategy.append("Leverage unique competitive advantages in all listing content")
        
        # Content development strategy
        high_impact_gaps = [gap for gap in content_gaps if gap.estimated_impact > 70]
        if high_impact_gaps:
            strategy.append("Develop comprehensive content strategy addressing high-impact gaps")
        
        # Keyword expansion strategy
        strategy.append("Implement quarterly keyword analysis to capture emerging search trends")
        
        # Performance monitoring strategy
        strategy.append("Monitor listing performance and adjust optimization based on conversion data")
        
        return strategy
    
    def _generate_implementation_priority(self, seo_optimization: SEOOptimization) -> List[str]:
        """Generate prioritized implementation steps."""
        priority_steps = []
        
        # Critical priority items
        if seo_optimization.title_optimization.improvement_score > 30:
            priority_steps.append("1. CRITICAL: Implement optimized title")
        
        critical_gaps = [gap for gap in seo_optimization.content_gaps if gap.priority == "critical"]
        if critical_gaps:
            priority_steps.append("2. CRITICAL: Address critical content gaps")
        
        # High priority items
        if len(seo_optimization.backend_optimization.opportunity_keywords) > 5:
            priority_steps.append("3. HIGH: Update backend keywords")
        
        if seo_optimization.bullet_optimization.keywords_coverage < 8:
            priority_steps.append("4. HIGH: Optimize bullet points")
        
        # Medium priority items
        if len(seo_optimization.competitive_advantages) > 0:
            priority_steps.append("5. MEDIUM: Highlight competitive advantages")
        
        return priority_steps
    
    def _predict_performance_improvements(self, seo_optimization: SEOOptimization) -> Dict[str, float]:
        """Predict performance improvements from optimization."""
        predictions = {}
        
        # Search visibility improvement
        title_score = seo_optimization.title_optimization.improvement_score
        keyword_coverage = seo_optimization.bullet_optimization.keywords_coverage
        predictions["search_visibility"] = min(50, (title_score + keyword_coverage * 3) / 2)
        
        # Conversion rate improvement
        bullet_score = seo_optimization.bullet_optimization.call_to_action_strength
        advantage_count = len(seo_optimization.competitive_advantages)
        predictions["conversion_rate"] = min(25, bullet_score / 4 + advantage_count * 3)
        
        # Click-through rate improvement
        overall_seo_score = seo_optimization.seo_score.overall_score
        predictions["click_through_rate"] = min(30, overall_seo_score / 3)
        
        # Overall traffic improvement
        predictions["organic_traffic"] = (
            predictions["search_visibility"] * 0.4 +
            predictions["click_through_rate"] * 0.6
        )
        
        return predictions
    
    def _calculate_confidence_level(self, seo_optimization: SEOOptimization) -> float:
        """Calculate confidence level in optimization recommendations."""
        confidence_factors = []
        
        # Data quality factors
        keyword_coverage = seo_optimization.bullet_optimization.keywords_coverage
        confidence_factors.append(min(100, keyword_coverage * 10))
        
        # Optimization completeness
        overall_score = seo_optimization.seo_score.overall_score
        confidence_factors.append(overall_score)
        
        # Competitive analysis depth
        advantage_count = len(seo_optimization.competitive_advantages)
        confidence_factors.append(min(100, advantage_count * 25))
        
        # Title optimization quality
        title_compliance = sum(seo_optimization.title_optimization.compliance_check.values())
        confidence_factors.append(title_compliance / len(seo_optimization.title_optimization.compliance_check) * 100)
        
        return round(sum(confidence_factors) / len(confidence_factors), 1) 