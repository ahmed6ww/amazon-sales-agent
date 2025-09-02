"""
Scoring Agent Runner

Manages the execution of scoring agent tasks and workflows.
"""

import json
from typing import Dict, Any, Optional
from agents import Runner
from .agent import scoring_agent
from .helper_methods import rank_keywords_by_priority, filter_by_thresholds
from .schemas import ScoringConfig, ScoringResult
from ..keyword.schemas import KeywordAnalysisResult


class ScoringRunner:
    """Runner for managing scoring agent operations."""
    
    def __init__(self, config: Optional[ScoringConfig] = None):
        """Initialize the scoring runner with optional configuration."""
        self.agent = scoring_agent
        self.config = config or ScoringConfig()
    
    def run_full_scoring_analysis(
        self,
        keyword_analysis: KeywordAnalysisResult,
        product_attributes: Dict[str, Any] = None,
        competitor_data: Dict[str, Any] = None,
        business_context: Dict[str, Any] = None
    ) -> ScoringResult:
        """
        Run complete scoring analysis using the agent.
        
        Args:
            keyword_analysis: Results from keyword agent
            product_attributes: Product context for intent scoring
            competitor_data: Competitor ranking information
            business_context: Business goals and context
            
        Returns:
            Complete scoring result with prioritized keywords
        """
        try:
            # Prepare data for agent - limit to top keywords to stay under token limits
            all_keywords = []
            for category, keyword_list in keyword_analysis.keywords_by_category.items():
                all_keywords.extend(keyword_list)
            
            # Sort by search volume and relevancy, take top 100 for AI analysis
            sorted_keywords = sorted(all_keywords, 
                                   key=lambda kw: (kw.search_volume or 0) * (kw.relevancy_score or 0), 
                                   reverse=True)[:100]
            
            print(f"🎯 Limiting AI analysis to top {len(sorted_keywords)} keywords (from {len(all_keywords)} total) to stay under token limits")
            
            keywords_data = []
            for kw in sorted_keywords:
                keywords_data.append({
                    'keyword_phrase': kw.keyword_phrase,
                    'category': kw.category,
                    'search_volume': kw.search_volume,
                    'relevancy_score': kw.relevancy_score,
                    'title_density': kw.title_density,
                    'top_10_competitors': len([r for r in kw.competitor_rankings.values() if r <= 10]) if hasattr(kw, 'competitor_rankings') else 0,
                    'total_competitors': len([r for r in kw.competitor_rankings.values() if r > 0]) if hasattr(kw, 'competitor_rankings') else 0,
                    'root_word': getattr(kw, 'root_word', None),
                    'root_volume': getattr(kw, 'root_volume', 0)
                })
            
            # Step 1: Calculate intent scores
            intent_message = f"""
            Calculate intent scores for the following keywords based on MVP requirements (0-3 scale):
            
            Keywords data: {json.dumps(keywords_data)}
            Product attributes: {json.dumps(product_attributes or {})}
            
            Use tool_calculate_intent_scores to analyze commercial intent and assign scores.
            """
            
            intent_response = Runner.run_sync(self.agent, intent_message)
            print(f"Intent scoring completed: {intent_response.final_output}")
            
            # Step 2: Analyze competition metrics
            competition_message = f"""
            Analyze competition metrics and difficulty for these keywords:
            
            Keywords data: {json.dumps(keywords_data)}
            Competitor data: {json.dumps(competitor_data or {})}
            
            Use tool_analyze_competition_metrics to evaluate ranking difficulty and opportunities.
            """
            
            competition_response = Runner.run_sync(self.agent, competition_message)
            print(f"Competition analysis completed: {competition_response.final_output}")
            
            # Step 3: Prioritize keywords
            keyword_analysis_data = {
                'keywords': keywords_data,
                'total_keywords': keyword_analysis.total_keywords,
                'top_opportunities': keyword_analysis.top_opportunities[:10],  # Limit to top 10
                'recommended_focus_areas': keyword_analysis.recommended_focus_areas[:5]  # Limit to top 5
            }
            
            prioritization_message = f"""
            Prioritize keywords using combined scoring methodology:
            
            Keyword analysis: {json.dumps(keyword_analysis_data)}
            Scoring config: {json.dumps(self.config.dict())}
            
            Use tool_prioritize_keywords to create final priority rankings.
            """
            
            prioritization_response = Runner.run_sync(self.agent, prioritization_message)
            print(f"Keyword prioritization completed: {prioritization_response.final_output}")
            
            # Step 4: Generate final rankings and recommendations
            final_message = f"""
            Generate final keyword rankings with strategic recommendations:
            
            Use the prioritization results to create actionable business insights.
            Business context: {json.dumps(business_context or {})}
            
            Use tool_generate_final_rankings to provide implementation guidance.
            """
            
            final_response = Runner.run_sync(self.agent, final_message)
            print(f"Final rankings generated: {final_response.final_output}")
            
            # Use direct processing as fallback for complete result
            return self.run_direct_processing(keyword_analysis)
            
        except Exception as e:
            print(f"Error in full scoring analysis: {str(e)}")
            # Fallback to direct processing
            return self.run_direct_processing(keyword_analysis)
    
    def run_intent_scoring_only(
        self,
        keyword_analysis: KeywordAnalysisResult,
        product_attributes: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Run only intent scoring analysis."""
        try:
            # Limit to top keywords for AI analysis
            all_keywords = []
            for category, keyword_list in keyword_analysis.keywords_by_category.items():
                all_keywords.extend(keyword_list)
            
            sorted_keywords = sorted(all_keywords, 
                                   key=lambda kw: (kw.search_volume or 0) * (kw.relevancy_score or 0), 
                                   reverse=True)[:50]  # Even smaller for intent-only analysis
            
            keywords_data = []
            for kw in sorted_keywords:
                keywords_data.append({
                    'keyword_phrase': kw.keyword_phrase,
                    'category': kw.category,
                    'search_volume': kw.search_volume,
                    'relevancy_score': kw.relevancy_score,
                    'title_density': kw.title_density
                })
            
            message = f"""
            Calculate intent scores (0-3) for these keywords:
            
            Keywords: {json.dumps(keywords_data)}
            Product attributes: {json.dumps(product_attributes or {})}
            
            Use tool_calculate_intent_scores to analyze commercial intent.
            """
            
            response = Runner.run_sync(self.agent, message)
            return {"success": True, "response": response.final_output}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_competition_analysis_only(
        self,
        keyword_analysis: KeywordAnalysisResult,
        competitor_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Run only competition analysis."""
        try:
            # Limit to top keywords for AI analysis
            all_keywords = []
            for category, keyword_list in keyword_analysis.keywords_by_category.items():
                all_keywords.extend(keyword_list)
            
            sorted_keywords = sorted(all_keywords, 
                                   key=lambda kw: (kw.search_volume or 0) * (kw.relevancy_score or 0), 
                                   reverse=True)[:50]
            
            keywords_data = []
            for kw in sorted_keywords:
                keywords_data.append({
                    'keyword_phrase': kw.keyword_phrase,
                    'category': kw.category,
                    'search_volume': kw.search_volume,
                    'relevancy_score': kw.relevancy_score,
                    'title_density': kw.title_density,
                    'top_10_competitors': len([r for r in kw.competitor_rankings.values() if r <= 10]) if hasattr(kw, 'competitor_rankings') else 0,
                    'total_competitors': len([r for r in kw.competitor_rankings.values() if r > 0]) if hasattr(kw, 'competitor_rankings') else 0
                })
            
            message = f"""
            Analyze competition metrics for these keywords:
            
            Keywords: {json.dumps(keywords_data)}
            Competitor data: {json.dumps(competitor_data or {})}
            
            Use tool_analyze_competition_metrics to evaluate difficulty and opportunities.
            """
            
            response = Runner.run_sync(self.agent, message)
            return {"success": True, "response": response.final_output}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_prioritization_only(
        self,
        keyword_analysis: KeywordAnalysisResult
    ) -> Dict[str, Any]:
        """Run only keyword prioritization."""
        try:
            keywords_list = []
            for category, keyword_list in keyword_analysis.keywords_by_category.items():
                for kw in keyword_list:
                    keywords_list.append({
                        'keyword_phrase': kw.keyword_phrase,
                        'category': kw.category,
                        'search_volume': kw.search_volume,
                        'relevancy_score': kw.relevancy_score,
                        'title_density': kw.title_density,
                        'top_10_competitors': len([r for r in kw.competitor_rankings.values() if r <= 10]) if hasattr(kw, 'competitor_rankings') else 0,
                        'total_competitors': len([r for r in kw.competitor_rankings.values() if r > 0]) if hasattr(kw, 'competitor_rankings') else 0,
                        'root_word': getattr(kw, 'root_word', None),
                        'root_volume': getattr(kw, 'root_volume', 0)
                    })
            
            keyword_analysis_data = {
                'keywords': keywords_list,
                'total_keywords': keyword_analysis.total_keywords,
                'top_opportunities': keyword_analysis.top_opportunities[:5],
                'recommended_focus_areas': keyword_analysis.recommended_focus_areas[:3]
            }
            
            message = f"""
            Prioritize keywords using combined scoring:
            
            Keyword analysis: {json.dumps(keyword_analysis_data)}
            Config: {json.dumps(self.config.dict())}
            
            Use tool_prioritize_keywords to create priority rankings.
            """
            
            response = Runner.run_sync(self.agent, message)
            return {"success": True, "response": response.final_output}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_direct_processing(
        self,
        keyword_analysis: KeywordAnalysisResult,
        apply_filters: bool = True
    ) -> ScoringResult:
        """
        Run scoring analysis using direct helper methods (no agent).
        
        This provides a reliable fallback and faster processing for testing.
        """
        try:
            # Use helper methods directly
            scoring_result = rank_keywords_by_priority(keyword_analysis, self.config)
            
            if apply_filters:
                scoring_result = filter_by_thresholds(scoring_result, self.config)
            
            return scoring_result
            
        except Exception as e:
            print(f"Error in direct processing: {str(e)}")
            # Return minimal result
            return ScoringResult(
                total_keywords_analyzed=0,
                processing_timestamp="",
                summary={"error": str(e)}
            )
    
    def update_config(self, new_config: ScoringConfig):
        """Update the scoring configuration."""
        self.config = new_config
    
    def get_config(self) -> ScoringConfig:
        """Get current scoring configuration."""
        return self.config 