"""
SEO Optimization Agent Schemas

Data models for SEO analysis and optimization results.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class KeywordCoverage(BaseModel):
    """Analysis of keyword coverage in current content."""
    total_keywords: int = Field(..., description="Total number of relevant keywords")
    covered_keywords: int = Field(..., description="Keywords found in current content") 
    coverage_percentage: float = Field(..., description="Percentage of keywords covered")
    missing_high_intent: List[str] = Field(default_factory=list, description="High-intent keywords not covered")
    missing_high_volume: List[str] = Field(default_factory=list, description="High-volume keywords not covered")


class RootCoverage(BaseModel):
    """Analysis of root keyword coverage."""
    total_roots: int = Field(..., description="Total number of root keywords")
    covered_roots: int = Field(..., description="Root keywords covered in content")
    coverage_percentage: float = Field(..., description="Percentage of roots covered")
    missing_roots: List[str] = Field(default_factory=list, description="Root keywords not covered")
    root_volumes: Dict[str, int] = Field(default_factory=dict, description="Volume by root keyword")


class ContentAnalysis(BaseModel):
    """Analysis of specific content piece (title, bullet, etc.)."""
    content: str = Field(..., description="The content being analyzed")
    keywords_found: List[str] = Field(default_factory=list, description="Keywords found in this content")
    keyword_count: int = Field(..., description="Number of keywords found")
    character_count: int = Field(..., description="Character count")
    keyword_density: float = Field(..., description="Keyword density percentage")
    opportunities: List[str] = Field(default_factory=list, description="Missing keyword opportunities")


class CurrentSEO(BaseModel):
    """Analysis of current SEO state."""
    title_analysis: ContentAnalysis = Field(..., description="Current title analysis")
    bullets_analysis: List[ContentAnalysis] = Field(default_factory=list, description="Analysis of each bullet point")
    backend_keywords: List[str] = Field(default_factory=list, description="Current backend keywords")
    keyword_coverage: KeywordCoverage = Field(..., description="Overall keyword coverage analysis")
    root_coverage: RootCoverage = Field(..., description="Root keyword coverage analysis")
    total_character_usage: Dict[str, int] = Field(default_factory=dict, description="Character usage by content type")


class OptimizedContent(BaseModel):
    """Optimized content suggestion."""
    content: str = Field(..., description="Optimized content")
    keywords_included: List[str] = Field(default_factory=list, description="Keywords included in optimization")
    improvements: List[str] = Field(default_factory=list, description="List of improvements made")
    character_count: int = Field(..., description="Character count of optimized content")


class OptimizedSEO(BaseModel):
    """Optimized SEO suggestions."""
    optimized_title: OptimizedContent = Field(..., description="Optimized title suggestion")
    optimized_bullets: List[OptimizedContent] = Field(default_factory=list, description="Optimized bullet points")
    optimized_backend_keywords: List[str] = Field(default_factory=list, description="Optimized backend keywords")
    keyword_strategy: Dict[str, Any] = Field(default_factory=dict, description="Overall keyword strategy")
    rationale: str = Field(..., description="Explanation of optimization strategy")


class SEOComparison(BaseModel):
    """Comparison metrics between current and optimized SEO."""
    coverage_improvement: Dict[str, float] = Field(default_factory=dict, description="Coverage improvement metrics")
    intent_improvement: Dict[str, int] = Field(default_factory=dict, description="Intent score improvements")
    volume_improvement: Dict[str, int] = Field(default_factory=dict, description="Search volume improvements")
    character_efficiency: Dict[str, float] = Field(default_factory=dict, description="Character usage efficiency")
    summary_metrics: Dict[str, Any] = Field(default_factory=dict, description="High-level summary metrics")


class SEOAnalysisResult(BaseModel):
    """Complete SEO analysis and optimization result."""
    current_seo: CurrentSEO = Field(..., description="Analysis of current SEO state")
    optimized_seo: OptimizedSEO = Field(..., description="Optimized SEO suggestions")
    comparison: SEOComparison = Field(..., description="Comparison metrics")
    product_context: Dict[str, Any] = Field(default_factory=dict, description="Product context used for optimization")
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict, description="Analysis metadata and settings") 