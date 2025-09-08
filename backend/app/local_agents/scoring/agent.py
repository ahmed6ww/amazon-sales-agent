"""
Scoring Agent

Amazon keyword scoring agent for intent analysis and prioritization.
"""

from agents import Agent, ModelSettings
from .prompts import SCORING_AGENT_INSTRUCTIONS


# Create the scoring agent WITH tools for AI-only processing
scoring_agent = Agent(
    name="ScoringAgent",
    instructions=SCORING_AGENT_INSTRUCTIONS,
    model="gpt-5-2025-08-07",  # Using gpt-5-2025-08-07 for tool compatibility and stability
)