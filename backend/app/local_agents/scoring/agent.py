"""
Scoring Agent

Amazon keyword scoring agent for intent analysis and prioritization.
"""

from agents import Agent, ModelSettings
from .prompts import SCORING_AGENT_INSTRUCTIONS
# Create the scoring agent without tools (to avoid function object name errors)
scoring_agent = Agent(
    name="ScoringAgent",
    instructions=SCORING_AGENT_INSTRUCTIONS,
    model="gpt-4o",  # Using gpt-4o for better tool stability
    tools=[],  # No tools to avoid SDK conflicts
    model_settings=ModelSettings(
        temperature=0.1,  # Low temperature for consistent scoring
        max_tokens=4000
    )
) 