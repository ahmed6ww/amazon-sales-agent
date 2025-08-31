"""
Scoring Agent

Amazon keyword scoring agent for intent analysis and prioritization.
"""

from agents import Agent
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
    tools=[
        tool_calculate_intent_scores,
        tool_analyze_competition_metrics,
        tool_prioritize_keywords,
        tool_generate_final_rankings
    ]
) 