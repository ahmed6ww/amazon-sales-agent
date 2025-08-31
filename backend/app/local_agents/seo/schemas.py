"""
SEO Agent Schemas

Data models for Amazon SEO optimization including title, bullets, backend keywords,
gap analysis, and performance scoring.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


class SEOSection(str, Enum):
    """Amazon listing sections for SEO optimization"""
    TITLE = "title"
    BULLET_POINTS = "bullet_points"
    BACKEND_KEYWORDS = "backend_keywords"
    DESCRIPTION = "description"
    A_PLUS_CONTENT = "a_plus_content"


class OptimizationPriority(str, Enum):
    """Priority levels for SEO optimizations"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TitleOptimization(BaseModel):
    """Title optimization results and recommendations"""
    current_title: str = Field(description="Current product title")
    recommended_title: str = Field(description="Optimized title recommendation")
    keywords_added: List[str] = Field(description="High-priority keywords integrated")
    keywords_removed: List[str] = Field(default_factory=list, description="Low-value keywords removed")
    character_count: int = Field(description="Character count of optimized title")
    character_limit: int = Field(default=200, description="Amazon character limit for marketplace")
    improvement_score: float = Field(description="Percentage improvement score")
    keyword_density: Dict[str, float] = Field(description="Keyword density analysis")
    readability_score: float = Field(description="Title readability score (0-100)")
    compliance_check: Dict[str, bool] = Field(description="Amazon compliance validation")


class BulletPointOptimization(BaseModel):
    """Bullet points optimization results"""
    current_bullets: List[str] = Field(default_factory=list, description="Current bullet points")
    recommended_bullets: List[str] = Field(description="Optimized bullet point recommendations")
    keywords_coverage: int = Field(description="Number of high-priority keywords covered")
    feature_coverage: Dict[str, int] = Field(description="Product features coverage analysis")
    character_efficiency: float = Field(description="Character usage efficiency score")
    bullet_scores: List[float] = Field(description="Individual bullet point quality scores")
    call_to_action_strength: float = Field(description="CTA effectiveness score")


class BackendKeywordOptimization(BaseModel):
    """Backend keywords optimization results"""
    current_keywords: List[str] = Field(default_factory=list, description="Current backend keywords")
    recommended_keywords: List[str] = Field(description="Optimized backend keyword list")
    character_count: int = Field(description="Total character count")
    character_limit: int = Field(default=250, description="Amazon backend keyword limit")
    keyword_efficiency: float = Field(description="Keyword efficiency score")
    search_volume_coverage: int = Field(description="Total search volume covered")
    opportunity_keywords: List[str] = Field(description="High-opportunity keywords included")
    avoided_duplicates: List[str] = Field(description="Duplicates from title/bullets avoided")
    coverage_improvement: str = Field(description="Coverage improvement percentage")


class ContentGap(BaseModel):
    """Content gap identification and recommendations"""
    section: SEOSection = Field(description="Listing section with content gap")
    missing_keywords: List[str] = Field(description="High-value keywords not covered")
    missing_features: List[str] = Field(description="Product features not mentioned")
    competitor_advantages: List[str] = Field(description="Advantages competitors have")
    recommended_content: str = Field(description="Specific content recommendation")
    priority: OptimizationPriority = Field(description="Gap priority level")
    estimated_impact: float = Field(description="Estimated impact score (0-100)")


class CompetitiveAdvantage(BaseModel):
    """Competitive positioning and advantages"""
    advantage_type: str = Field(description="Type of competitive advantage")
    description: str = Field(description="Detailed advantage description")
    supporting_keywords: List[str] = Field(description="Keywords that support this advantage")
    implementation_section: SEOSection = Field(description="Where to implement in listing")
    strength_score: float = Field(description="Advantage strength score (0-100)")
    market_differentiation: str = Field(description="How this differentiates from competitors")


class SEOScore(BaseModel):
    """SEO performance scoring and metrics"""
    overall_score: float = Field(description="Overall SEO score (0-100)")
    title_score: float = Field(description="Title optimization score")
    bullets_score: float = Field(description="Bullet points score")
    backend_score: float = Field(description="Backend keywords score")
    keyword_coverage_score: float = Field(description="Keyword coverage score")
    competitive_score: float = Field(description="Competitive positioning score")
    improvement_potential: float = Field(description="Potential improvement percentage")
    benchmark_comparison: Dict[str, float] = Field(description="Comparison to category benchmarks")


class SEOOptimization(BaseModel):
    """Complete SEO optimization package"""
    title_optimization: TitleOptimization
    bullet_optimization: BulletPointOptimization
    backend_optimization: BackendKeywordOptimization
    content_gaps: List[ContentGap]
    competitive_advantages: List[CompetitiveAdvantage]
    seo_score: SEOScore
    quick_wins: List[str] = Field(description="Immediate actionable improvements")
    long_term_strategy: List[str] = Field(description="Long-term SEO strategy recommendations")


class SEOAnalysisResult(BaseModel):
    """Complete SEO analysis results"""
    product_info: Dict[str, Any] = Field(description="Product information from research")
    keyword_insights: Dict[str, Any] = Field(description="Keyword analysis insights")
    scoring_insights: Dict[str, Any] = Field(description="Scoring analysis insights")
    seo_optimization: SEOOptimization
    implementation_priority: List[str] = Field(description="Prioritized implementation steps")
    performance_predictions: Dict[str, float] = Field(description="Predicted performance improvements")
    processing_time: float = Field(description="Analysis processing time in seconds")
    confidence_level: float = Field(description="Confidence in recommendations (0-100)")
    next_review_date: str = Field(description="Recommended next review date")


class SEOConfig(BaseModel):
    """Configuration for SEO analysis"""
    marketplace: str = Field(default="US", description="Amazon marketplace")
    character_limits: Dict[str, int] = Field(
        default_factory=lambda: {
            "title": 200,
            "backend_keywords": 250,
            "bullet_points": 1000
        },
        description="Character limits by marketplace"
    )
    optimization_focus: List[str] = Field(
        default_factory=lambda: ["conversion", "visibility", "competition"],
        description="Primary optimization focus areas"
    )
    include_competitor_analysis: bool = Field(default=True, description="Include competitor analysis")
    keyword_density_targets: Dict[str, float] = Field(
        default_factory=lambda: {
            "primary": 0.03,
            "secondary": 0.02,
            "supporting": 0.01
        },
        description="Target keyword density ranges"
    ) 