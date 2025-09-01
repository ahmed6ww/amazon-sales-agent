"""
Scoring Agent

Amazon keyword scoring agent for intent analysis and prioritization.
"""

from agents import Agent, ModelSettings
from .prompts import SCORING_AGENT_INSTRUCTIONS
from .tools import (
    tool_calculate_intent_scores,
    tool_analyze_competition_metrics,
    tool_prioritize_keywords,
    tool_generate_final_rankings
)

# Create the scoring agent
scoring_agent = Agent(
    name="ScoringAgent",
    instructions=SCORING_AGENT_INSTRUCTIONS,
    model="gpt-4o",  # Using gpt-4o for better tool stability
    tools=[
        tool_calculate_intent_scores,
        tool_analyze_competition_metrics,
        tool_prioritize_keywords,
        tool_generate_final_rankings
    ],
    model_settings=ModelSettings(
        temperature=0.1,  # Low temperature for consistent scoring
        max_tokens=4000
    )
) 