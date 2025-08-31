"""
Scoring Agent Helper Methods

Core business logic for intent scoring, competition analysis, and keyword prioritization.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from .schemas import (
    IntentScore, KeywordScore, CompetitionMetrics, ScoringResult,
    PriorityLevel, CategoryStats, ScoringConfig
)
from ..keyword.schemas import KeywordData, KeywordAnalysisResult


def calculate_intent_score(
    keyword_phrase: str,
    category: str,
    search_volume: Optional[int] = None,
    relevancy_score: float = 0.0,
    title_density: Optional[float] = None,
    product_attributes: Dict[str, Any] = None
) -> Tuple[IntentScore, str]:
    """
    Calculate intent score (0-3) based on MVP requirements.
    
    Returns:
        Tuple of (IntentScore, reasoning)
    """
    reasoning_parts = []
    
    # Start with category-based baseline
    if category.lower() in ['irrelevant', 'spanish', 'outlier']:
        return IntentScore.IRRELEVANT, f"Category '{category}' indicates no commercial relevance"
    
    if category.lower() == 'branded':
        return IntentScore.IRRELEVANT, "Branded keywords filtered unless analyzing brand strategy"
    
    # Analyze commercial intent signals
    commercial_signals = _analyze_commercial_intent(keyword_phrase)
    intent_signals = len(commercial_signals)
    
    # Factor in search volume and relevancy
    volume_factor = _calculate_volume_factor(search_volume)
    relevancy_factor = _calculate_relevancy_factor(relevancy_score)
    
    # Calculate base intent score
    base_score = 1  # Start with basic relevance for relevant categories
    
    # Add points for commercial signals
    if intent_signals >= 3:
        base_score = 3
        reasoning_parts.append(f"Strong commercial intent: {', '.join(commercial_signals)}")
    elif intent_signals >= 2:
        base_score = 2
        reasoning_parts.append(f"Good commercial intent: {', '.join(commercial_signals)}")
    elif intent_signals >= 1:
        base_score = 1
        reasoning_parts.append(f"Basic commercial intent: {', '.join(commercial_signals)}")
    
    # Adjust based on volume and relevancy
    if volume_factor > 0.8 and relevancy_factor > 0.7:
        base_score = min(3, base_score + 1)
        reasoning_parts.append("High volume and relevancy boost")
    elif volume_factor < 0.3 or relevancy_factor < 0.3:
        base_score = max(0, base_score - 1)
        reasoning_parts.append("Low volume or relevancy penalty")
    
    # Special handling for design-specific keywords
    if category.lower() == 'design-specific':
        if base_score >= 2:
            reasoning_parts.append("Design-specific with strong intent")
        else:
            base_score = max(1, base_score)
            reasoning_parts.append("Design-specific baseline intent")
    
    # Convert to IntentScore enum
    intent_score = IntentScore(max(0, min(3, base_score)))
    reasoning = "; ".join(reasoning_parts)
    
    return intent_score, reasoning


def _analyze_commercial_intent(keyword_phrase: str) -> List[str]:
    """Analyze keyword for commercial intent signals."""
    signals = []
    phrase_lower = keyword_phrase.lower()
    
    # Purchase intent signals
    purchase_terms = ['buy', 'purchase', 'order', 'shop', 'get', 'find']
    if any(term in phrase_lower for term in purchase_terms):
        signals.append("purchase_intent")
    
    # Quality/comparison signals
    quality_terms = ['best', 'top', 'review', 'compare', 'vs', 'good', 'quality']
    if any(term in phrase_lower for term in quality_terms):
        signals.append("quality_research")
    
    # Specific need signals
    need_terms = ['for', 'with', 'baby', 'newborn', 'toddler', 'infant']
    if any(term in phrase_lower for term in need_terms):
        signals.append("specific_need")
    
    # Feature/benefit signals
    feature_terms = ['waterproof', 'portable', 'easy', 'safe', 'soft', 'large', 'small']
    if any(term in phrase_lower for term in feature_terms):
        signals.append("feature_focused")
    
    # Urgency signals
    urgency_terms = ['now', 'today', 'quick', 'fast', 'immediate']
    if any(term in phrase_lower for term in urgency_terms):
        signals.append("urgency")
    
    return signals


def _calculate_volume_factor(search_volume: Optional[int]) -> float:
    """Calculate volume factor (0-1) for intent scoring."""
    if search_volume is None:
        return 0.5  # Neutral when unknown
    
    if search_volume >= 2000:
        return 1.0
    elif search_volume >= 1000:
        return 0.8
    elif search_volume >= 500:
        return 0.6
    elif search_volume >= 200:
        return 0.4
    elif search_volume >= 100:
        return 0.2
    else:
        return 0.1


def _calculate_relevancy_factor(relevancy_score: float) -> float:
    """Calculate relevancy factor (0-1) for intent scoring."""
    return min(1.0, relevancy_score / 100.0)


def analyze_competition_difficulty(
    keyword_data,  # KeywordData from keyword agent
    competitor_rankings: Dict[str, int] = None
) -> CompetitionMetrics:
    """
    Analyze competition difficulty and opportunity for a keyword.
    """
    # Calculate top 10 competitors from competitor rankings
    top_10_count = 0
    total_competitors = 0
    
    if hasattr(keyword_data, 'competitor_rankings') and keyword_data.competitor_rankings:
        for asin, rank in keyword_data.competitor_rankings.items():
            if rank > 0:  # Valid ranking
                total_competitors += 1
                if rank <= 10:
                    top_10_count += 1
    
    metrics = CompetitionMetrics(
        keyword_phrase=keyword_data.keyword_phrase,
        cpr_score=getattr(keyword_data, 'cpr', None),
        title_density=getattr(keyword_data, 'title_density', None),
        search_volume=getattr(keyword_data, 'search_volume', None),
        relevancy_score=getattr(keyword_data, 'relevancy_score', 0.0),
        top_10_competitors=top_10_count,
        total_competitors=total_competitors
    )
    
    # Calculate competition level
    difficulty_score = 0
    
    # CPR analysis
    if metrics.cpr_score:
        if metrics.cpr_score > 50:
            difficulty_score += 40
        elif metrics.cpr_score > 20:
            difficulty_score += 25
        else:
            difficulty_score += 10
    
    # Title density analysis
    if metrics.title_density:
        if metrics.title_density > 50:
            difficulty_score += 30
        elif metrics.title_density > 20:
            difficulty_score += 20
        else:
            difficulty_score += 5
    
    # Competitor ranking analysis
    if metrics.total_competitors > 0:
        competition_ratio = metrics.top_10_competitors / metrics.total_competitors
        if competition_ratio > 0.7:
            difficulty_score += 30
        elif competition_ratio > 0.4:
            difficulty_score += 20
        else:
            difficulty_score += 10
    
    metrics.difficulty_rating = min(100, difficulty_score)
    
    # Determine competition level
    if metrics.difficulty_rating > 70:
        metrics.competition_level = "high"
    elif metrics.difficulty_rating > 40:
        metrics.competition_level = "medium"
    else:
        metrics.competition_level = "low"
    
    # Calculate opportunity score (inverse of difficulty with volume boost)
    base_opportunity = 100 - metrics.difficulty_rating
    
    # Volume boost
    if metrics.search_volume:
        if metrics.search_volume > 1000:
            base_opportunity += 20
        elif metrics.search_volume > 500:
            base_opportunity += 10
        elif metrics.search_volume < 100:
            base_opportunity -= 20
    
    # Relevancy boost
    if metrics.relevancy_score > 60:
        base_opportunity += 15
    elif metrics.relevancy_score < 30:
        base_opportunity -= 15
    
    metrics.opportunity_score = max(0, min(100, base_opportunity))
    
    return metrics


def calculate_priority_score(
    intent_score: IntentScore,
    competition_metrics: CompetitionMetrics,
    config: ScoringConfig = None
) -> float:
    """
    Calculate final priority score using MVP formula.
    
    Priority Score = (Intent × 30) + (Relevancy × 25) + (Volume × 25) + (Opportunity × 20)
    """
    if config is None:
        config = ScoringConfig()
    
    # Normalize intent score to 0-100
    intent_normalized = (int(intent_score) / 3.0) * 100
    
    # Normalize volume score to 0-100
    volume_normalized = _calculate_volume_factor(competition_metrics.search_volume) * 100
    
    # Calculate weighted priority score
    priority_score = (
        intent_normalized * config.relevancy_weight +
        competition_metrics.relevancy_score * config.relevancy_weight +
        volume_normalized * config.volume_weight +
        competition_metrics.opportunity_score * config.opportunity_weight
    )
    
    return min(100, max(0, priority_score))


def determine_priority_level(priority_score: float, config: ScoringConfig = None) -> PriorityLevel:
    """Determine priority level based on score and thresholds."""
    if config is None:
        config = ScoringConfig()
    
    if priority_score >= config.critical_threshold:
        return PriorityLevel.CRITICAL
    elif priority_score >= config.high_threshold:
        return PriorityLevel.HIGH
    elif priority_score >= config.medium_threshold:
        return PriorityLevel.MEDIUM
    elif priority_score >= config.filter_threshold:
        return PriorityLevel.LOW
    else:
        return PriorityLevel.FILTERED


def rank_keywords_by_priority(
    keyword_analysis: KeywordAnalysisResult,
    config: ScoringConfig = None
) -> ScoringResult:
    """
    Rank all keywords by priority and create comprehensive scoring result.
    """
    if config is None:
        config = ScoringConfig()
    
    scored_keywords = []
    
    # Process each keyword from all categories
    all_keywords = []
    for category, keywords in keyword_analysis.keywords_by_category.items():
        all_keywords.extend(keywords)
    
    # Process each keyword
    for keyword_data in all_keywords:
        # Calculate intent score
        intent_score, intent_reasoning = calculate_intent_score(
            keyword_data.keyword_phrase,
            keyword_data.category or (keyword_data.final_category.value if keyword_data.final_category else "unknown"),
            keyword_data.search_volume,
            keyword_data.relevancy_score,
            keyword_data.title_density
        )
        
        # Analyze competition
        competition_metrics = analyze_competition_difficulty(keyword_data)
        
        # Calculate priority score
        priority_score = calculate_priority_score(intent_score, competition_metrics, config)
        
        # Determine priority level
        priority_level = determine_priority_level(priority_score, config)
        
        # Create keyword score object
        keyword_score = KeywordScore(
            keyword_phrase=keyword_data.keyword_phrase,
            category=keyword_data.category or (keyword_data.final_category.value if keyword_data.final_category else "unknown"),
            intent_score=intent_score,
            relevancy_score=getattr(keyword_data, 'relevancy_score', 0.0),
            competition_metrics=competition_metrics,
            priority_score=priority_score,
            priority_level=priority_level,
            business_value=_generate_business_value_explanation(intent_score, priority_level, competition_metrics),
            ranking_difficulty=competition_metrics.competition_level,
            opportunity_type=_determine_opportunity_type(competition_metrics),
            root_word=getattr(keyword_data, 'root_word', ''),
            root_volume=getattr(keyword_data, 'root_volume', None)
        )
        
        scored_keywords.append(keyword_score)
    
    # Sort by priority score
    scored_keywords.sort(key=lambda x: x.priority_score, reverse=True)
    
    # Create scoring result
    result = ScoringResult(
        total_keywords_analyzed=len(scored_keywords),
        processing_timestamp=datetime.now().isoformat(),
        scored_keywords=scored_keywords
    )
    
    # Categorize by priority level
    for keyword in scored_keywords:
        if keyword.priority_level == PriorityLevel.CRITICAL:
            result.critical_keywords.append(keyword)
        elif keyword.priority_level == PriorityLevel.HIGH:
            result.high_priority_keywords.append(keyword)
        elif keyword.priority_level == PriorityLevel.MEDIUM:
            result.medium_priority_keywords.append(keyword)
        elif keyword.priority_level == PriorityLevel.LOW:
            result.low_priority_keywords.append(keyword)
        else:
            result.filtered_keywords.append(keyword)
    
    # Generate category stats
    result.category_stats = _calculate_category_stats(scored_keywords)
    
    # Identify top opportunities
    result.top_opportunities = [
        kw for kw in scored_keywords 
        if kw.competition_metrics.opportunity_score > 70 and kw.priority_level in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]
    ][:10]  # Top 10 opportunities
    
    # Calculate summary stats
    result.summary = _calculate_summary_stats(result)
    
    return result


def _generate_business_value_explanation(
    intent_score: IntentScore,
    priority_level: PriorityLevel,
    competition_metrics: CompetitionMetrics
) -> str:
    """Generate business value explanation for a keyword."""
    explanations = []
    
    if intent_score == IntentScore.THREE_INTENTS:
        explanations.append("High commercial intent with strong buyer signals")
    elif intent_score == IntentScore.TWO_INTENTS:
        explanations.append("Good commercial intent with clear purchase indicators")
    elif intent_score == IntentScore.ONE_INTENT:
        explanations.append("Basic commercial relevance")
    else:
        explanations.append("Limited commercial value")
    
    if competition_metrics.opportunity_score > 70:
        explanations.append("excellent ranking opportunity")
    elif competition_metrics.opportunity_score > 50:
        explanations.append("good ranking potential")
    else:
        explanations.append("challenging competitive landscape")
    
    return "; ".join(explanations)


def _determine_opportunity_type(competition_metrics: CompetitionMetrics) -> str:
    """Determine the type of opportunity for a keyword."""
    if competition_metrics.title_density == 0 and competition_metrics.search_volume and competition_metrics.search_volume > 200:
        return "untapped_market"
    elif competition_metrics.competition_level == "low" and competition_metrics.search_volume and competition_metrics.search_volume > 500:
        return "low_hanging_fruit"
    elif competition_metrics.relevancy_score > 70 and competition_metrics.opportunity_score > 60:
        return "proven_demand"
    elif competition_metrics.search_volume and competition_metrics.search_volume > 1000:
        return "high_volume_competitive"
    else:
        return "standard_opportunity"


def _calculate_category_stats(scored_keywords: List[KeywordScore]) -> List[CategoryStats]:
    """Calculate statistics for each keyword category."""
    category_data = {}
    
    for keyword in scored_keywords:
        cat = keyword.category
        if cat not in category_data:
            category_data[cat] = {
                'keywords': [],
                'total_volume': 0,
                'high_priority': 0,
                'critical_priority': 0
            }
        
        category_data[cat]['keywords'].append(keyword)
        if keyword.competition_metrics.search_volume:
            category_data[cat]['total_volume'] += keyword.competition_metrics.search_volume
        
        if keyword.priority_level == PriorityLevel.HIGH:
            category_data[cat]['high_priority'] += 1
        elif keyword.priority_level == PriorityLevel.CRITICAL:
            category_data[cat]['critical_priority'] += 1
    
    stats = []
    for cat, data in category_data.items():
        keywords = data['keywords']
        stats.append(CategoryStats(
            category_name=cat,
            total_keywords=len(keywords),
            avg_intent_score=sum(int(kw.intent_score) for kw in keywords) / len(keywords),
            avg_priority_score=sum(kw.priority_score for kw in keywords) / len(keywords),
            total_search_volume=data['total_volume'],
            high_priority_count=data['high_priority'],
            critical_priority_count=data['critical_priority']
        ))
    
    return stats


def _calculate_summary_stats(result: ScoringResult) -> Dict[str, Any]:
    """Calculate summary statistics for the scoring result."""
    return {
        'total_keywords': result.total_keywords_analyzed,
        'critical_count': len(result.critical_keywords),
        'high_priority_count': len(result.high_priority_keywords),
        'medium_priority_count': len(result.medium_priority_keywords),
        'low_priority_count': len(result.low_priority_keywords),
        'filtered_count': len(result.filtered_keywords),
        'top_opportunities_count': len(result.top_opportunities),
        'avg_priority_score': sum(kw.priority_score for kw in result.scored_keywords) / len(result.scored_keywords) if result.scored_keywords else 0,
        'total_search_volume': sum(
            kw.competition_metrics.search_volume or 0 
            for kw in result.scored_keywords
        )
    }


def filter_by_thresholds(
    scoring_result: ScoringResult,
    config: ScoringConfig = None
) -> ScoringResult:
    """Apply additional filtering based on business thresholds."""
    if config is None:
        config = ScoringConfig()
    
    # Filter out keywords below minimum thresholds
    filtered_keywords = []
    for keyword in scoring_result.scored_keywords:
        # Apply volume threshold
        if keyword.competition_metrics.search_volume and keyword.competition_metrics.search_volume < config.min_search_volume:
            keyword.priority_level = PriorityLevel.FILTERED
        
        # Apply difficulty threshold
        if keyword.competition_metrics.difficulty_rating > config.max_difficulty_score:
            if keyword.priority_level not in [PriorityLevel.CRITICAL]:  # Keep critical keywords
                keyword.priority_level = PriorityLevel.FILTERED
        
        # Apply opportunity threshold
        if keyword.competition_metrics.opportunity_score < config.min_opportunity_score:
            if keyword.priority_level not in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]:
                keyword.priority_level = PriorityLevel.FILTERED
        
        filtered_keywords.append(keyword)
    
    # Rebuild result with filtered keywords
    scoring_result.scored_keywords = filtered_keywords
    
    # Recategorize by priority level
    scoring_result.critical_keywords = [kw for kw in filtered_keywords if kw.priority_level == PriorityLevel.CRITICAL]
    scoring_result.high_priority_keywords = [kw for kw in filtered_keywords if kw.priority_level == PriorityLevel.HIGH]
    scoring_result.medium_priority_keywords = [kw for kw in filtered_keywords if kw.priority_level == PriorityLevel.MEDIUM]
    scoring_result.low_priority_keywords = [kw for kw in filtered_keywords if kw.priority_level == PriorityLevel.LOW]
    scoring_result.filtered_keywords = [kw for kw in filtered_keywords if kw.priority_level == PriorityLevel.FILTERED]
    
    # Recalculate summary
    scoring_result.summary = _calculate_summary_stats(scoring_result)
    
    return scoring_result 