"""
Keyword Agent

OpenAI Agents SDK implementation for keyword categorization and analysis.
"""

from agents import Agent, ModelSettings
from agents.agent_output import AgentOutputSchema
from dotenv import load_dotenv, find_dotenv

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

load_dotenv(find_dotenv())  # Load environment variables from .env file


# Create the Keyword Agent with MVP-focused instructions
keyword_agent = Agent(
    name="KeywordAgent",
    instructions=KEYWORD_AGENT_INSTRUCTIONS,
    model="gpt-4o",  # Using gpt-4o for better tool stability
    tools=[
        tool_categorize_keywords,
        tool_calculate_relevancy_scores,
        tool_extract_root_words,
        tool_analyze_title_density
    ],
    model_settings=ModelSettings(
        temperature=0.1,  # Low temperature for consistent categorization
        max_tokens=4000,
        tool_choice="required",
    ),
    output_type=AgentOutputSchema(KeywordAnalysisResult, strict_json_schema=False)
) 