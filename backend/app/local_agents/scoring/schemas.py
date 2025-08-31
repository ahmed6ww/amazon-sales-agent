"""
Scoring Agent Schemas

Data models for intent scoring, competition analysis, and keyword prioritization.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class IntentScore(int, Enum):
    """Intent scoring scale as per MVP requirements"""
    IRRELEVANT = 0  # Irrelevant intent
    ONE_INTENT = 1  # One relevant intent
    TWO_INTENTS = 2  # Two relevant intents
    THREE_INTENTS = 3  # Three relevant intents


class PriorityLevel(str, Enum):
    """Keyword priority levels for final ranking"""
    CRITICAL = "critical"      # Must-have keywords (intent 3, high volume)
    HIGH = "high"             # Important keywords (intent 2-3, good metrics)
    MEDIUM = "medium"         # Decent keywords (intent 1-2, moderate metrics)
    LOW = "low"              # Optional keywords (intent 1, low competition)
    FILTERED = "filtered"     # Below threshold keywords


class CompetitionMetrics(BaseModel):
    """Competition analysis metrics for a keyword"""
    keyword_phrase: str
    cpr_score: Optional[float] = Field(None, description="Cerebro Product Rank")
    title_density: Optional[float] = Field(None, description="Title density percentage")
    search_volume: Optional[int] = Field(None, description="Monthly search volume")
    relevancy_score: float = Field(0.0, description="Relevancy percentage from keyword agent")
    
    # Competition difficulty metrics
    competition_level: str = Field("unknown", description="Low/Medium/High competition")
    opportunity_score: float = Field(0.0, description="Opportunity rating 0-100")
    difficulty_rating: float = Field(0.0, description="Difficulty to rank 0-100")
    
    # Ranking data
    avg_competitor_rank: Optional[float] = Field(None, description="Average competitor ranking")
    top_10_competitors: int = Field(0, description="Number of competitors in top 10")
    total_competitors: int = Field(0, description="Total competitors tracked")


class KeywordScore(BaseModel):
    """Complete scoring data for a single keyword"""
    keyword_phrase: str
    category: str = Field(..., description="Keyword category from keyword agent")
    
    # Core scoring components
    intent_score: IntentScore = Field(..., description="Intent score 0-3")
    relevancy_score: float = Field(0.0, description="Relevancy percentage")
    competition_metrics: CompetitionMetrics
    
    # Calculated scores
    priority_score: float = Field(0.0, description="Final priority score 0-100")
    priority_level: PriorityLevel = Field(PriorityLevel.LOW, description="Priority classification")
    
    # Business insights
    business_value: str = Field("", description="Business value explanation")
    ranking_difficulty: str = Field("", description="Difficulty assessment")
    opportunity_type: str = Field("", description="Type of opportunity")
    
    # Root word analysis
    root_word: str = Field("", description="Extracted root word")
    root_volume: Optional[int] = Field(None, description="Total root word search volume")


class CategoryStats(BaseModel):
    """Statistics for a keyword category"""
    category_name: str
    total_keywords: int
    avg_intent_score: float
    avg_priority_score: float
    total_search_volume: int
    high_priority_count: int
    critical_priority_count: int


class ScoringResult(BaseModel):
    """Complete scoring analysis result"""
    # Input summary
    total_keywords_analyzed: int
    processing_timestamp: str
    
    # Scored keywords
    scored_keywords: List[KeywordScore] = Field(default_factory=list)
    
    # Priority rankings
    critical_keywords: List[KeywordScore] = Field(default_factory=list)
    high_priority_keywords: List[KeywordScore] = Field(default_factory=list)
    medium_priority_keywords: List[KeywordScore] = Field(default_factory=list)
    low_priority_keywords: List[KeywordScore] = Field(default_factory=list)
    filtered_keywords: List[KeywordScore] = Field(default_factory=list)
    
    # Category analysis
    category_stats: List[CategoryStats] = Field(default_factory=list)
    
    # Root word insights
    root_word_priorities: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Business insights
    top_opportunities: List[KeywordScore] = Field(default_factory=list)
    coverage_gaps: List[str] = Field(default_factory=list)
    competitive_advantages: List[str] = Field(default_factory=list)
    
    # Quality metrics
    data_quality_score: float = Field(0.0, description="Data completeness score 0-100")
    confidence_level: str = Field("medium", description="Analysis confidence level")
    warnings: List[str] = Field(default_factory=list)
    
    # Summary stats
    summary: Dict[str, Any] = Field(default_factory=dict)


class ScoringConfig(BaseModel):
    """Configuration for scoring thresholds and weights"""
    # Intent scoring weights
    relevancy_weight: float = Field(0.3, description="Weight for relevancy score")
    volume_weight: float = Field(0.25, description="Weight for search volume")
    competition_weight: float = Field(0.25, description="Weight for competition metrics")
    opportunity_weight: float = Field(0.2, description="Weight for opportunity score")
    
    # Priority thresholds
    critical_threshold: float = Field(80.0, description="Minimum score for critical priority")
    high_threshold: float = Field(60.0, description="Minimum score for high priority")
    medium_threshold: float = Field(40.0, description="Minimum score for medium priority")
    filter_threshold: float = Field(20.0, description="Minimum score to avoid filtering")
    
    # Volume thresholds
    min_search_volume: int = Field(100, description="Minimum monthly search volume")
    high_volume_threshold: int = Field(1000, description="High volume threshold")
    
    # Competition thresholds
    max_difficulty_score: float = Field(80.0, description="Maximum acceptable difficulty")
    min_opportunity_score: float = Field(30.0, description="Minimum opportunity score") 