"""
Keyword Agent Package

This package contains the Amazon keyword processing agent with tools for:
- Keyword categorization (Relevant, Design-Specific, Irrelevant, Branded)
- Relevancy scoring using competitor ranking data
- Root word extraction and grouping
- Intent scoring and prioritization
"""

from .agent import keyword_agent
from .schemas import (
    KeywordCategory,
    KeywordData,
    KeywordAnalysisResult,
    RootWordAnalysis,
    CategoryStats
)
from .tools import (
    tool_categorize_keywords,
    tool_calculate_relevancy_scores,
    tool_extract_root_words,
    tool_analyze_title_density
)
from .prompts import KEYWORD_AGENT_INSTRUCTIONS
from .helper_methods import (
    categorize_keywords_from_csv,
    calculate_relevancy_score,
    extract_root_word,
    analyze_title_density,
    filter_zero_density_keywords,
    group_keywords_by_root
)
from .runner import KeywordRunner

__all__ = [
    "keyword_agent",
    "KeywordRunner",
    "categorize_keywords_from_csv",
    "calculate_relevancy_score",
    "extract_root_word",
    "analyze_title_density",
    "filter_zero_density_keywords",
    "group_keywords_by_root",
    "KeywordCategory",
    "KeywordData",
    "KeywordAnalysisResult",
    "RootWordAnalysis",
    "CategoryStats",
    "tool_categorize_keywords",
    "tool_calculate_relevancy_scores",
    "tool_extract_root_words",
    "tool_analyze_title_density",
    "KEYWORD_AGENT_INSTRUCTIONS"
] 