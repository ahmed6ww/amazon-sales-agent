"""
Scoring Agent Tools

Tools for the scoring agent to interact with the OpenAI Agents SDK.
"""

import json
from typing import Dict, Any, List
from .helper_methods import (
    calculate_intent_score,
    analyze_competition_difficulty,
    rank_keywords_by_priority,
    filter_by_thresholds
)
from .schemas import ScoringConfig, IntentScore
from ..keyword.schemas import KeywordAnalysisResult, KeywordData


def tool_calculate_intent_scores(keywords_json: str, product_attributes_json: str = "{}") -> str:
    """
    Calculate intent scores (0-3) for keywords based on MVP requirements.
    
    Args:
        keywords_json: JSON string containing keyword data from keyword agent
        product_attributes_json: JSON string containing product attributes for context
        
    Returns:
        JSON string with intent scores and reasoning
    """
    try:
        keywords_data = json.loads(keywords_json)
        product_attributes = json.loads(product_attributes_json)
        
        intent_results = []
        
        # Process each keyword
        for keyword_info in keywords_data:
            if isinstance(keyword_info, dict):
                keyword_phrase = keyword_info.get('keyword_phrase', '')
                category = keyword_info.get('category', '')
                search_volume = keyword_info.get('search_volume')
                relevancy_score = keyword_info.get('relevancy_score', 0.0)
                title_density = keyword_info.get('title_density')
                
                # Calculate intent score
                intent_score, reasoning = calculate_intent_score(
                    keyword_phrase=keyword_phrase,
                    category=category,
                    search_volume=search_volume,
                    relevancy_score=relevancy_score,
                    title_density=title_density,
                    product_attributes=product_attributes
                )
                
                intent_results.append({
                    'keyword_phrase': keyword_phrase,
                    'category': category,
                    'intent_score': int(intent_score),
                    'intent_reasoning': reasoning,
                    'search_volume': search_volume,
                    'relevancy_score': relevancy_score,
                    'title_density': title_density
                })
        
        return json.dumps({
            'success': True,
            'total_keywords': len(intent_results),
            'intent_scores': intent_results,
            'score_distribution': _calculate_intent_distribution(intent_results),
            'summary': f"Calculated intent scores for {len(intent_results)} keywords"
        })
        
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': f"Failed to calculate intent scores: {str(e)}",
            'intent_scores': []
        })


def tool_analyze_competition_metrics(keywords_json: str, competitor_data_json: str = "{}") -> str:
    """
    Analyze competition metrics and difficulty for keywords.
    
    Args:
        keywords_json: JSON string containing keyword data
        competitor_data_json: JSON string containing competitor ranking data
        
    Returns:
        JSON string with competition analysis results
    """
    try:
        keywords_data = json.loads(keywords_json)
        competitor_data = json.loads(competitor_data_json)
        
        competition_results = []
        
        # Process each keyword
        for keyword_info in keywords_data:
            if isinstance(keyword_info, dict):
                # Create KeywordData object
                keyword_data = KeywordData(
                    keyword_phrase=keyword_info.get('keyword_phrase', ''),
                    category=keyword_info.get('category', ''),
                    search_volume=keyword_info.get('search_volume'),
                    relevancy_score=keyword_info.get('relevancy_score', 0.0),
                    title_density=keyword_info.get('title_density'),
                    top_10_competitors=keyword_info.get('top_10_competitors', 0),
                    total_competitors=keyword_info.get('total_competitors', 0),
                    root_word=keyword_info.get('root_word', ''),
                    root_volume=keyword_info.get('root_volume')
                )
                
                # Analyze competition
                competition_metrics = analyze_competition_difficulty(
                    keyword_data,
                    competitor_data.get(keyword_data.keyword_phrase, {})
                )
                
                competition_results.append({
                    'keyword_phrase': competition_metrics.keyword_phrase,
                    'competition_level': competition_metrics.competition_level,
                    'difficulty_rating': competition_metrics.difficulty_rating,
                    'opportunity_score': competition_metrics.opportunity_score,
                    'cpr_score': competition_metrics.cpr_score,
                    'title_density': competition_metrics.title_density,
                    'search_volume': competition_metrics.search_volume,
                    'relevancy_score': competition_metrics.relevancy_score,
                    'top_10_competitors': competition_metrics.top_10_competitors,
                    'total_competitors': competition_metrics.total_competitors
                })
        
        return json.dumps({
            'success': True,
            'total_keywords': len(competition_results),
            'competition_analysis': competition_results,
            'difficulty_distribution': _calculate_difficulty_distribution(competition_results),
            'opportunity_summary': _calculate_opportunity_summary(competition_results),
            'summary': f"Analyzed competition metrics for {len(competition_results)} keywords"
        })
        
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': f"Failed to analyze competition metrics: {str(e)}",
            'competition_analysis': []
        })


def tool_prioritize_keywords(keyword_analysis_json: str, config_json: str = "{}") -> str:
    """
    Prioritize keywords based on combined scoring methodology.
    
    Args:
        keyword_analysis_json: JSON string containing keyword analysis result
        config_json: JSON string containing scoring configuration
        
    Returns:
        JSON string with prioritized keywords and rankings
    """
    try:
        keyword_analysis_data = json.loads(keyword_analysis_json)
        config_data = json.loads(config_json)
        
        # Create ScoringConfig
        config = ScoringConfig(**config_data) if config_data else ScoringConfig()
        
        # Convert to KeywordAnalysisResult
        keywords = []
        for kw_data in keyword_analysis_data.get('keywords', []):
            keyword = KeywordData(**kw_data)
            keywords.append(keyword)
        
        keyword_analysis = KeywordAnalysisResult(
            keywords=keywords,
            total_keywords=len(keywords),
            processing_timestamp=keyword_analysis_data.get('processing_timestamp', ''),
            category_stats=keyword_analysis_data.get('category_stats', []),
            root_word_analysis=keyword_analysis_data.get('root_word_analysis', {}),
            summary=keyword_analysis_data.get('summary', {})
        )
        
        # Rank keywords by priority
        scoring_result = rank_keywords_by_priority(keyword_analysis, config)
        
        # Apply additional filtering
        scoring_result = filter_by_thresholds(scoring_result, config)
        
        return json.dumps({
            'success': True,
            'total_keywords_analyzed': scoring_result.total_keywords_analyzed,
            'priority_distribution': {
                'critical': len(scoring_result.critical_keywords),
                'high': len(scoring_result.high_priority_keywords),
                'medium': len(scoring_result.medium_priority_keywords),
                'low': len(scoring_result.low_priority_keywords),
                'filtered': len(scoring_result.filtered_keywords)
            },
            'top_critical_keywords': [
                {
                    'keyword_phrase': kw.keyword_phrase,
                    'priority_score': kw.priority_score,
                    'intent_score': int(kw.intent_score),
                    'business_value': kw.business_value,
                    'opportunity_score': kw.competition_metrics.opportunity_score
                }
                for kw in scoring_result.critical_keywords[:10]
            ],
            'top_opportunities': [
                {
                    'keyword_phrase': kw.keyword_phrase,
                    'priority_score': kw.priority_score,
                    'opportunity_score': kw.competition_metrics.opportunity_score,
                    'opportunity_type': kw.opportunity_type,
                    'search_volume': kw.competition_metrics.search_volume
                }
                for kw in scoring_result.top_opportunities[:10]
            ],
            'category_performance': [
                {
                    'category': stat.category_name,
                    'total_keywords': stat.total_keywords,
                    'avg_priority_score': stat.avg_priority_score,
                    'critical_count': stat.critical_priority_count,
                    'high_count': stat.high_priority_count
                }
                for stat in scoring_result.category_stats
            ],
            'summary': scoring_result.summary,
            'full_scoring_result': _serialize_scoring_result(scoring_result)
        })
        
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': f"Failed to prioritize keywords: {str(e)}",
            'priority_distribution': {}
        })


def tool_generate_final_rankings(scoring_result_json: str, business_context_json: str = "{}") -> str:
    """
    Generate final keyword rankings with business insights and recommendations.
    
    Args:
        scoring_result_json: JSON string containing scoring results
        business_context_json: JSON string containing business context and goals
        
    Returns:
        JSON string with final rankings and strategic recommendations
    """
    try:
        scoring_data = json.loads(scoring_result_json)
        business_context = json.loads(business_context_json)
        
        # Extract key insights
        critical_keywords = scoring_data.get('top_critical_keywords', [])
        opportunities = scoring_data.get('top_opportunities', [])
        category_performance = scoring_data.get('category_performance', [])
        
        # Generate strategic recommendations
        recommendations = _generate_strategic_recommendations(
            critical_keywords,
            opportunities,
            category_performance,
            business_context
        )
        
        # Create implementation roadmap
        roadmap = _create_implementation_roadmap(critical_keywords, opportunities)
        
        # Calculate ROI estimates
        roi_estimates = _calculate_roi_estimates(critical_keywords, opportunities)
        
        return json.dumps({
            'success': True,
            'final_rankings': {
                'must_target_keywords': critical_keywords[:15],  # Top 15 critical
                'quick_wins': [
                    opp for opp in opportunities 
                    if opp.get('opportunity_score', 0) > 80
                ][:10],  # Top 10 quick wins
                'long_term_opportunities': [
                    opp for opp in opportunities 
                    if opp.get('search_volume', 0) > 1000
                ][:10]  # High volume opportunities
            },
            'strategic_recommendations': recommendations,
            'implementation_roadmap': roadmap,
            'roi_estimates': roi_estimates,
            'resource_allocation': _suggest_resource_allocation(critical_keywords, opportunities),
            'success_metrics': _define_success_metrics(scoring_data),
            'risk_assessment': _assess_implementation_risks(critical_keywords, opportunities),
            'summary': f"Generated final rankings and strategic plan for keyword implementation"
        })
        
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': f"Failed to generate final rankings: {str(e)}",
            'final_rankings': {}
        })


# Helper functions for tool operations

def _calculate_intent_distribution(intent_results: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate distribution of intent scores."""
    distribution = {0: 0, 1: 0, 2: 0, 3: 0}
    for result in intent_results:
        score = result.get('intent_score', 0)
        distribution[score] = distribution.get(score, 0) + 1
    return distribution


def _calculate_difficulty_distribution(competition_results: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate distribution of competition difficulty levels."""
    distribution = {'low': 0, 'medium': 0, 'high': 0}
    for result in competition_results:
        level = result.get('competition_level', 'unknown')
        if level in distribution:
            distribution[level] += 1
    return distribution


def _calculate_opportunity_summary(competition_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate opportunity summary statistics."""
    if not competition_results:
        return {}
    
    opportunity_scores = [r.get('opportunity_score', 0) for r in competition_results]
    return {
        'avg_opportunity_score': sum(opportunity_scores) / len(opportunity_scores),
        'high_opportunity_count': len([s for s in opportunity_scores if s > 70]),
        'medium_opportunity_count': len([s for s in opportunity_scores if 40 <= s <= 70]),
        'low_opportunity_count': len([s for s in opportunity_scores if s < 40])
    }


def _serialize_scoring_result(scoring_result) -> Dict[str, Any]:
    """Serialize ScoringResult for JSON output."""
    return {
        'total_keywords_analyzed': scoring_result.total_keywords_analyzed,
        'processing_timestamp': scoring_result.processing_timestamp,
        'priority_counts': {
            'critical': len(scoring_result.critical_keywords),
            'high': len(scoring_result.high_priority_keywords),
            'medium': len(scoring_result.medium_priority_keywords),
            'low': len(scoring_result.low_priority_keywords),
            'filtered': len(scoring_result.filtered_keywords)
        },
        'summary': scoring_result.summary
    }


def _generate_strategic_recommendations(
    critical_keywords: List[Dict],
    opportunities: List[Dict],
    category_performance: List[Dict],
    business_context: Dict
) -> List[str]:
    """Generate strategic recommendations based on scoring results."""
    recommendations = []
    
    # Critical keyword recommendations
    if critical_keywords:
        recommendations.append(
            f"Immediately target {len(critical_keywords)} critical keywords with highest commercial intent"
        )
    
    # Opportunity recommendations
    high_opportunity_count = len([o for o in opportunities if o.get('opportunity_score', 0) > 80])
    if high_opportunity_count > 0:
        recommendations.append(
            f"Focus on {high_opportunity_count} high-opportunity keywords with low competition"
        )
    
    # Category-specific recommendations
    top_category = max(category_performance, key=lambda x: x.get('avg_priority_score', 0)) if category_performance else None
    if top_category:
        recommendations.append(
            f"Prioritize '{top_category['category']}' category keywords for maximum impact"
        )
    
    # Volume-based recommendations
    high_volume_opportunities = [o for o in opportunities if o.get('search_volume', 0) > 1000]
    if high_volume_opportunities:
        recommendations.append(
            f"Invest in {len(high_volume_opportunities)} high-volume keywords for long-term growth"
        )
    
    return recommendations


def _create_implementation_roadmap(critical_keywords: List[Dict], opportunities: List[Dict]) -> Dict[str, List[str]]:
    """Create implementation roadmap with phases."""
    return {
        'phase_1_immediate': [
            f"Target top {min(5, len(critical_keywords))} critical keywords",
            "Optimize title and bullets for highest intent keywords",
            "Update backend keywords with critical terms"
        ],
        'phase_2_short_term': [
            f"Expand to top {min(10, len(opportunities))} opportunity keywords",
            "Create A+ content targeting medium-priority keywords",
            "Monitor ranking improvements and adjust strategy"
        ],
        'phase_3_long_term': [
            "Scale to comprehensive keyword coverage",
            "Develop content strategy for all relevant categories",
            "Implement advanced SEO optimization techniques"
        ]
    }


def _calculate_roi_estimates(critical_keywords: List[Dict], opportunities: List[Dict]) -> Dict[str, str]:
    """Calculate ROI estimates for keyword targeting."""
    total_critical_volume = sum(kw.get('search_volume', 0) for kw in critical_keywords if kw.get('search_volume'))
    total_opportunity_volume = sum(opp.get('search_volume', 0) for opp in opportunities if opp.get('search_volume'))
    
    return {
        'critical_keywords_potential': f"{total_critical_volume:,} monthly searches from critical keywords",
        'opportunity_potential': f"{total_opportunity_volume:,} monthly searches from opportunities",
        'estimated_traffic_increase': "15-25% organic traffic increase within 3-6 months",
        'conversion_impact': "10-20% improvement in keyword-to-conversion rate"
    }


def _suggest_resource_allocation(critical_keywords: List[Dict], opportunities: List[Dict]) -> Dict[str, str]:
    """Suggest resource allocation for keyword implementation."""
    return {
        'content_optimization': "60% - Focus on critical keywords in titles, bullets, A+ content",
        'opportunity_targeting': "25% - Develop content for high-opportunity keywords",
        'monitoring_analysis': "10% - Track performance and adjust strategy",
        'competitive_research': "5% - Monitor competitor keyword strategies"
    }


def _define_success_metrics(scoring_data: Dict) -> List[str]:
    """Define success metrics for keyword implementation."""
    return [
        f"Rank in top 10 for {len(scoring_data.get('top_critical_keywords', []))} critical keywords",
        "Achieve 15%+ increase in organic click-through rate",
        "Improve conversion rate by 10%+ from targeted keywords",
        "Increase total keyword rankings by 25%+",
        "Maintain or improve average keyword position"
    ]


def _assess_implementation_risks(critical_keywords: List[Dict], opportunities: List[Dict]) -> List[str]:
    """Assess risks in keyword implementation strategy."""
    risks = []
    
    # Competition risks
    high_competition_count = len([kw for kw in critical_keywords if kw.get('difficulty_rating', 0) > 70])
    if high_competition_count > 0:
        risks.append(f"{high_competition_count} critical keywords have high competition difficulty")
    
    # Volume risks
    low_volume_count = len([kw for kw in critical_keywords if kw.get('search_volume', 0) < 200])
    if low_volume_count > 0:
        risks.append(f"{low_volume_count} critical keywords have relatively low search volume")
    
    # Opportunity risks
    if len(opportunities) < 5:
        risks.append("Limited high-opportunity keywords identified - may need broader research")
    
    return risks if risks else ["Low risk implementation strategy with good keyword balance"] 