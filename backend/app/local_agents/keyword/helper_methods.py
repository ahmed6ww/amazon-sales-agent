"""
Keyword Agent Helper Methods

Core business logic for keyword processing, categorization, and analysis.
Implements the MVP requirements for keyword research.
"""

import re
import time
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter

from .schemas import (
    KeywordCategory, 
    KeywordData, 
    KeywordAnalysisResult, 
    RootWordAnalysis, 
    CategoryStats,
    CompetitorAnalysis,
    RelevancyCalculation
)


def categorize_keywords_from_csv(csv_data: List[Dict[str, Any]], product_attributes: Dict[str, Any] = None) -> KeywordAnalysisResult:
    """
    Main function to categorize keywords from Helium10 CSV data.
    Implements the full MVP keyword categorization logic.
    """
    start_time = time.time()
    
    # Parse CSV data into KeywordData objects
    keywords = []
    competitor_asins = set()
    
    for row in csv_data:
        keyword_data = _parse_csv_row_to_keyword_data(row)
        keywords.append(keyword_data)
        
        # Extract competitor ASINs from the row
        competitor_asins.update(_extract_competitor_asins_from_row(row))
    
    # Apply categorization logic
    categorized_keywords = {}
    for category in KeywordCategory:
        categorized_keywords[category] = []
    
    warnings = []
    
    for keyword in keywords:
        # Apply MVP categorization rules
        final_category = _determine_final_category(keyword, product_attributes)
        keyword.final_category = final_category
        
        # Calculate relevancy score using MVP formula
        keyword.relevancy_score = calculate_relevancy_score(keyword, list(competitor_asins))
        
        # Extract root word
        keyword.root_word = extract_root_word(keyword.keyword_phrase)
        
        # Check title density rules
        keyword.is_zero_title_density = keyword.title_density == 0
        keyword.is_derivative = _is_derivative_keyword(keyword.keyword_phrase)
        
        # Apply zero title density filtering rules from MVP
        if _should_filter_keyword(keyword):
            warnings.append(f"Filtered keyword: {keyword.keyword_phrase} (zero title density)")
            continue
            
        categorized_keywords[final_category].append(keyword)
    
    # Calculate root word analysis
    root_word_analysis = _calculate_root_word_analysis(keywords)
    
    # Update broad search volume for each keyword
    root_volumes = {rwa.root_word: rwa.total_search_volume for rwa in root_word_analysis}
    for keyword in keywords:
        if keyword.root_word in root_volumes:
            keyword.broad_search_volume = root_volumes[keyword.root_word]
    
    # Calculate category statistics
    category_stats = {}
    for category, category_keywords in categorized_keywords.items():
        if category_keywords:
            category_stats[category] = _calculate_category_stats(category, category_keywords)
    
    # Calculate quality metrics
    zero_density_count = sum(1 for kw in keywords if kw.is_zero_title_density)
    derivative_count = sum(1 for kw in keywords if kw.is_derivative)
    unique_roots = len(set(kw.root_word for kw in keywords if kw.root_word))
    
    processing_time = time.time() - start_time
    
    return KeywordAnalysisResult(
        total_keywords=len(csv_data),
        processed_keywords=len(keywords),
        filtered_keywords=len(csv_data) - sum(len(kws) for kws in categorized_keywords.values()),
        keywords_by_category=categorized_keywords,
        category_stats=category_stats,
        root_word_analysis=root_word_analysis,
        zero_title_density_count=zero_density_count,
        derivative_keywords_count=derivative_count,
        unique_root_words_count=unique_roots,
        processing_time=processing_time,
        data_quality_score=_calculate_data_quality_score(keywords),
        warnings=warnings,
        top_opportunities=_identify_top_opportunities(categorized_keywords),
        coverage_gaps=_identify_coverage_gaps(categorized_keywords),
        recommended_focus_areas=_get_recommended_focus_areas(category_stats)
    )


def calculate_relevancy_score(keyword: KeywordData, competitor_asins: List[str]) -> float:
    """
    Implement the MVP relevancy formula: =countif(range, filter)
    Count how many competitors are ranked in top 10 for this keyword.
    """
    if not keyword.competitor_rankings:
        return 0.0
    
    top_10_count = 0
    total_competitors = 0
    
    for asin, ranking in keyword.competitor_rankings.items():
        if asin in competitor_asins and ranking > 0:
            total_competitors += 1
            if ranking <= 10:  # Top 10 organic ranks
                top_10_count += 1
    
    if total_competitors == 0:
        return 0.0
    
    # Return percentage of competitors ranked in top 10
    return (top_10_count / total_competitors) * 100


def extract_root_word(keyword_phrase: str) -> str:
    """
    Extract the root word from a keyword phrase.
    Used for broad search volume calculation.
    """
    # Clean the keyword
    cleaned = keyword_phrase.lower().strip()
    
    # Remove common modifiers and get the main noun
    stop_words = {'for', 'with', 'and', 'or', 'the', 'a', 'an', 'baby', 'toddler', 'kids', 'children'}
    words = cleaned.split()
    
    # Filter out stop words and find the main product word
    main_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    if not main_words:
        return words[0] if words else keyword_phrase.lower()
    
    # Return the first significant word as root
    return main_words[0]


def analyze_title_density(keywords: List[KeywordData]) -> Dict[str, Any]:
    """
    Analyze title density patterns according to MVP rules.
    """
    zero_density_keywords = [kw for kw in keywords if kw.title_density == 0]
    high_density_keywords = [kw for kw in keywords if kw.title_density > 20]
    
    # Analyze zero density keywords per MVP rules
    zero_density_analysis = {
        'total_count': len(zero_density_keywords),
        'irrelevant_count': 0,
        'derivative_count': 0,
        'opportunity_count': 0
    }
    
    for kw in zero_density_keywords:
        if kw.final_category == KeywordCategory.IRRELEVANT:
            zero_density_analysis['irrelevant_count'] += 1
        elif kw.is_derivative:
            zero_density_analysis['derivative_count'] += 1
        elif kw.has_own_root and kw.search_volume > 1000:
            zero_density_analysis['opportunity_count'] += 1
    
    return {
        'zero_density_analysis': zero_density_analysis,
        'high_density_keywords': [kw.keyword_phrase for kw in high_density_keywords[:10]],
        'title_density_distribution': _get_title_density_distribution(keywords)
    }


def filter_zero_density_keywords(keywords: List[KeywordData]) -> List[KeywordData]:
    """
    Filter keywords based on MVP zero title density rules.
    """
    filtered = []
    
    for keyword in keywords:
        if not _should_filter_keyword(keyword):
            filtered.append(keyword)
    
    return filtered


def group_keywords_by_root(keywords: List[KeywordData]) -> Dict[str, List[KeywordData]]:
    """
    Group keywords by their root words for broad search volume calculation.
    """
    groups = defaultdict(list)
    
    for keyword in keywords:
        root = keyword.root_word or extract_root_word(keyword.keyword_phrase)
        groups[root].append(keyword)
    
    return dict(groups)


# Private helper functions

def _parse_csv_row_to_keyword_data(row: Dict[str, Any]) -> KeywordData:
    """Parse a CSV row into KeywordData object"""
    
    # Extract competitor rankings from ASIN columns
    competitor_rankings = {}
    asin_columns = [col for col in row.keys() if col.startswith('B0') and len(col) == 10]
    
    for asin_col in asin_columns:
        try:
            ranking = int(row.get(asin_col, 0))
            if ranking > 0:
                competitor_rankings[asin_col] = ranking
        except (ValueError, TypeError):
            continue
    
    return KeywordData(
        keyword_phrase=str(row.get('Keyword Phrase', '')),
        category=str(row.get('Category (R for relevant, D for design specific, I for irrelevant and B for branded, S for Spanish, O for Outlier)', '')),
        search_volume=int(row.get('Search Volume', 0)),
        search_volume_trend=_safe_int(row.get('Search Volume Trend')),
        relevancy=int(row.get('Relevancy', 0)),
        title_density=int(row.get('Title Density', 0)),
        cpr=int(row.get('CPR', 0)),
        cerebro_iq_score=int(row.get('Cerebro IQ Score', 0)),
        h10_ppc_sugg_bid=float(row.get('H10 PPC Sugg. Bid', 0)),
        h10_ppc_sugg_min_bid=float(row.get('H10 PPC Sugg. Min Bid', 0)),
        h10_ppc_sugg_max_bid=float(row.get('H10 PPC Sugg. Max Bid', 0)),
        competing_products=int(row.get('Competing Products', 0)),
        sponsored_asins=int(row.get('Sponsored ASINs', 0)),
        competitor_rankings=competitor_rankings
    )


def _extract_competitor_asins_from_row(row: Dict[str, Any]) -> List[str]:
    """Extract competitor ASINs from CSV row"""
    asin_columns = [col for col in row.keys() if col.startswith('B0') and len(col) == 10]
    return asin_columns


def _determine_final_category(keyword: KeywordData, product_attributes: Dict[str, Any] = None) -> KeywordCategory:
    """
    Determine final keyword category based on MVP rules.
    """
    # First check the original category from CSV
    original_category = keyword.category.upper() if keyword.category else ''
    
    # Map CSV categories to our enum
    category_mapping = {
        'R': KeywordCategory.RELEVANT,
        'D': KeywordCategory.DESIGN_SPECIFIC,
        'I': KeywordCategory.IRRELEVANT,
        'B': KeywordCategory.BRANDED,
        'S': KeywordCategory.SPANISH,
        'O': KeywordCategory.OUTLIER
    }
    
    # Handle combined categories like "I/D"
    if '/' in original_category:
        categories = original_category.split('/')
        # Prioritize based on MVP rules - Design-specific over Irrelevant
        if 'D' in categories:
            return KeywordCategory.DESIGN_SPECIFIC
        elif 'R' in categories:
            return KeywordCategory.RELEVANT
        elif 'I' in categories:
            return KeywordCategory.IRRELEVANT
    
    # Single category
    for key, category in category_mapping.items():
        if key in original_category:
            return category
    
    # Default classification based on keyword analysis
    return _classify_keyword_by_content(keyword.keyword_phrase, product_attributes)


def _classify_keyword_by_content(keyword_phrase: str, product_attributes: Dict[str, Any] = None) -> KeywordCategory:
    """
    Classify keyword based on content analysis when category is unclear.
    """
    keyword_lower = keyword_phrase.lower()
    
    # Brand detection
    known_brands = ['keekaroo', 'skip hop', 'bumbo', 'summer infant', 'munchkin']
    if any(brand in keyword_lower for brand in known_brands):
        return KeywordCategory.BRANDED
    
    # Spanish detection
    spanish_indicators = ['de', 'para', 'bebe', 'cambiador', 'pañales']
    if any(indicator in keyword_lower for indicator in spanish_indicators):
        return KeywordCategory.SPANISH
    
    # Design-specific indicators
    design_indicators = ['wipeable', 'waterproof', 'contoured', 'memory foam', 'organic cotton']
    if any(indicator in keyword_lower for indicator in design_indicators):
        return KeywordCategory.DESIGN_SPECIFIC
    
    # Default to relevant if it contains main product terms
    main_terms = ['changing pad', 'changing mat', 'diaper pad']
    if any(term in keyword_lower for term in main_terms):
        return KeywordCategory.RELEVANT
    
    return KeywordCategory.IRRELEVANT


def _should_filter_keyword(keyword: KeywordData) -> bool:
    """
    Apply MVP zero title density filtering rules.
    """
    if keyword.title_density > 0:
        return False
    
    # Filter if irrelevant
    if keyword.final_category == KeywordCategory.IRRELEVANT:
        return True
    
    # Filter if derivative/similar to main keyword
    if keyword.is_derivative:
        return True
    
    # Keep if it has its own root word and decent search volume (opportunity)
    if keyword.has_own_root and keyword.search_volume > 500:
        return False
    
    # Default filter for zero title density
    return True


def _is_derivative_keyword(keyword_phrase: str) -> bool:
    """
    Check if keyword is derivative/similar to main keywords.
    """
    main_keywords = ['changing pad', 'changing mat', 'diaper pad']
    keyword_lower = keyword_phrase.lower()
    
    # Check for plural/singular variations
    for main_kw in main_keywords:
        if main_kw in keyword_lower or main_kw.replace(' ', '') in keyword_lower.replace(' ', ''):
            # Check if it's just a plural/singular variation
            words_diff = set(keyword_lower.split()) - set(main_kw.split())
            if len(words_diff) <= 1:  # Only one word difference
                return True
    
    return False


def _calculate_root_word_analysis(keywords: List[KeywordData]) -> List[RootWordAnalysis]:
    """
    Calculate broad search volume analysis by root words.
    """
    root_groups = defaultdict(list)
    
    for keyword in keywords:
        root = keyword.root_word or extract_root_word(keyword.keyword_phrase)
        root_groups[root].append(keyword)
    
    analysis = []
    for root_word, root_keywords in root_groups.items():
        if len(root_keywords) < 2:  # Skip single keyword roots
            continue
            
        total_volume = sum(kw.search_volume for kw in root_keywords)
        avg_relevancy = sum(kw.relevancy_score for kw in root_keywords) / len(root_keywords)
        best_keyword = max(root_keywords, key=lambda x: x.search_volume).keyword_phrase
        categories = list(set(kw.final_category for kw in root_keywords if kw.final_category))
        
        analysis.append(RootWordAnalysis(
            root_word=root_word,
            related_keywords=[kw.keyword_phrase for kw in root_keywords],
            total_search_volume=total_volume,
            avg_relevancy_score=avg_relevancy,
            keyword_count=len(root_keywords),
            best_keyword=best_keyword,
            categories_present=categories
        ))
    
    # Sort by total search volume
    return sorted(analysis, key=lambda x: x.total_search_volume, reverse=True)


def _calculate_category_stats(category: KeywordCategory, keywords: List[KeywordData]) -> CategoryStats:
    """
    Calculate statistics for a keyword category.
    """
    if not keywords:
        return CategoryStats(
            category=category,
            keyword_count=0,
            total_search_volume=0,
            avg_relevancy_score=0.0,
            avg_intent_score=0.0,
            top_keywords=[]
        )
    
    total_volume = sum(kw.search_volume for kw in keywords)
    avg_relevancy = sum(kw.relevancy_score for kw in keywords) / len(keywords)
    avg_intent = sum(kw.intent_score for kw in keywords) / len(keywords)
    
    # Get top 5 keywords by search volume
    top_keywords = sorted(keywords, key=lambda x: x.search_volume, reverse=True)[:5]
    
    return CategoryStats(
        category=category,
        keyword_count=len(keywords),
        total_search_volume=total_volume,
        avg_relevancy_score=avg_relevancy,
        avg_intent_score=avg_intent,
        top_keywords=[kw.keyword_phrase for kw in top_keywords]
    )


def _calculate_data_quality_score(keywords: List[KeywordData]) -> float:
    """
    Calculate overall data quality score (0-100).
    """
    if not keywords:
        return 0.0
    
    # Factors for quality score
    has_search_volume = sum(1 for kw in keywords if kw.search_volume > 0) / len(keywords)
    has_relevancy_data = sum(1 for kw in keywords if kw.relevancy > 0) / len(keywords)
    has_competition_data = sum(1 for kw in keywords if kw.competing_products > 0) / len(keywords)
    has_ranking_data = sum(1 for kw in keywords if kw.competitor_rankings) / len(keywords)
    
    quality_score = (has_search_volume * 0.3 + 
                    has_relevancy_data * 0.3 + 
                    has_competition_data * 0.2 + 
                    has_ranking_data * 0.2) * 100
    
    return round(quality_score, 2)


def _identify_top_opportunities(categorized_keywords: Dict[KeywordCategory, List[KeywordData]]) -> List[str]:
    """
    Identify top keyword opportunities based on MVP criteria.
    """
    opportunities = []
    
    # High search volume, low competition relevant keywords
    relevant_keywords = categorized_keywords.get(KeywordCategory.RELEVANT, [])
    for kw in relevant_keywords:
        if kw.search_volume > 5000 and kw.competing_products < 1000:
            opportunities.append(kw.keyword_phrase)
    
    # Zero title density opportunities
    for category_keywords in categorized_keywords.values():
        for kw in category_keywords:
            if kw.is_zero_title_density and kw.has_own_root and kw.search_volume > 1000:
                opportunities.append(f"{kw.keyword_phrase} (zero title density opportunity)")
    
    return opportunities[:10]  # Top 10 opportunities


def _identify_coverage_gaps(categorized_keywords: Dict[KeywordCategory, List[KeywordData]]) -> List[str]:
    """
    Identify keyword coverage gaps.
    """
    gaps = []
    
    # Analyze root word coverage
    all_keywords = []
    for keywords in categorized_keywords.values():
        all_keywords.extend(keywords)
    
    root_groups = group_keywords_by_root(all_keywords)
    
    # Find root words with high volume but low keyword count
    for root, keywords in root_groups.items():
        total_volume = sum(kw.search_volume for kw in keywords)
        if total_volume > 10000 and len(keywords) < 3:
            gaps.append(f"Limited coverage for '{root}' root word")
    
    return gaps


def _get_recommended_focus_areas(category_stats: Dict[KeywordCategory, CategoryStats]) -> List[str]:
    """
    Get recommended focus areas based on category analysis.
    """
    recommendations = []
    
    relevant_stats = category_stats.get(KeywordCategory.RELEVANT)
    if relevant_stats and relevant_stats.keyword_count > 0:
        recommendations.append(f"Focus on {relevant_stats.keyword_count} relevant keywords")
    
    design_stats = category_stats.get(KeywordCategory.DESIGN_SPECIFIC)
    if design_stats and design_stats.total_search_volume > 50000:
        recommendations.append("High opportunity in design-specific keywords")
    
    return recommendations


def _get_title_density_distribution(keywords: List[KeywordData]) -> Dict[str, int]:
    """
    Get distribution of title density values.
    """
    density_ranges = {
        '0': 0,
        '1-5': 0,
        '6-15': 0,
        '16-30': 0,
        '30+': 0
    }
    
    for kw in keywords:
        density = kw.title_density
        if density == 0:
            density_ranges['0'] += 1
        elif density <= 5:
            density_ranges['1-5'] += 1
        elif density <= 15:
            density_ranges['6-15'] += 1
        elif density <= 30:
            density_ranges['16-30'] += 1
        else:
            density_ranges['30+'] += 1
    
    return density_ranges


def _safe_int(value: Any) -> Optional[int]:
    """Safely convert value to int, return None if not possible"""
    if value is None or value == '' or value == '-':
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _safe_float(value: Any) -> float:
    """Safely convert value to float, return 0.0 if conversion fails."""
    if value is None or value == '' or value == '-':
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0 