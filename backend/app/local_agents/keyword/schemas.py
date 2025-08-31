"""
Keyword Agent Schemas

Data structures for keyword processing, categorization, and analysis.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class KeywordCategory(str, Enum):
    """Keyword categories as defined in MVP"""
    RELEVANT = "relevant"
    DESIGN_SPECIFIC = "design_specific"
    IRRELEVANT = "irrelevant"
    BRANDED = "branded"
    SPANISH = "spanish"
    OUTLIER = "outlier"


class KeywordData(BaseModel):
    """Individual keyword data structure matching Helium10 CSV format"""
    keyword_phrase: str
    category: Optional[str] = None
    final_category: Optional[KeywordCategory] = None
    
    # Helium10 metrics
    search_volume: int = 0
    search_volume_trend: Optional[int] = None
    relevancy: int = 0
    title_density: int = 0
    cpr: int = 0  # Cerebro Product Rank
    cerebro_iq_score: int = 0
    
    # PPC data
    h10_ppc_sugg_bid: float = 0.0
    h10_ppc_sugg_min_bid: float = 0.0
    h10_ppc_sugg_max_bid: float = 0.0
    
    # Competition data
    competing_products: int = 0
    sponsored_asins: int = 0
    
    # Rankings for competitors (ASIN positions)
    competitor_rankings: Dict[str, int] = Field(default_factory=dict)
    
    # Calculated fields
    relevancy_score: float = 0.0
    intent_score: int = 0  # 0-3 scoring
    root_word: Optional[str] = None
    broad_search_volume: int = 0  # Aggregated by root word
    
    # Quality flags
    is_zero_title_density: bool = False
    is_derivative: bool = False
    has_own_root: bool = True


class RootWordAnalysis(BaseModel):
    """Analysis of keyword root words and their aggregated metrics"""
    root_word: str
    related_keywords: List[str]
    total_search_volume: int
    avg_relevancy_score: float
    keyword_count: int
    best_keyword: str  # Highest performing keyword for this root
    categories_present: List[KeywordCategory]


class CategoryStats(BaseModel):
    """Statistics for each keyword category"""
    category: KeywordCategory
    keyword_count: int
    total_search_volume: int
    avg_relevancy_score: float
    avg_intent_score: float
    top_keywords: List[str]  # Top 5 keywords by search volume


class KeywordAnalysisResult(BaseModel):
    """Complete keyword analysis results"""
    total_keywords: int
    processed_keywords: int
    filtered_keywords: int
    
    # Categorized keywords
    keywords_by_category: Dict[KeywordCategory, List[KeywordData]]
    category_stats: Dict[KeywordCategory, CategoryStats]
    
    # Root word analysis
    root_word_analysis: List[RootWordAnalysis]
    
    # Quality metrics
    zero_title_density_count: int
    derivative_keywords_count: int
    unique_root_words_count: int
    
    # Processing metadata
    processing_time: float
    data_quality_score: float  # 0-100 score
    warnings: List[str] = Field(default_factory=list)
    
    # Summary insights
    top_opportunities: List[str]  # Keywords with high potential
    coverage_gaps: List[str]  # Missing keyword areas
    recommended_focus_areas: List[str]


class CompetitorAnalysis(BaseModel):
    """Analysis of competitor keyword performance"""
    asin: str
    total_keywords_ranked: int
    avg_ranking_position: float
    top_10_rankings_count: int  # Keywords ranked in top 10
    keyword_coverage_score: float  # Percentage of relevant keywords they rank for
    strongest_categories: List[KeywordCategory]
    
    
class RelevancyCalculation(BaseModel):
    """Detailed relevancy calculation for a keyword"""
    keyword: str
    total_competitors: int
    competitors_ranked_top_10: int
    relevancy_percentage: float
    competitor_details: List[Dict[str, Any]]  # ASIN and ranking details
    is_relevant_by_formula: bool  # Based on countif logic 