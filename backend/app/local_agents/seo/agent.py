"""
SEO Optimization Agent

Amazon SEO analysis and optimization agent for listing improvement.
"""

from agents import Agent, ModelSettings
from agents.agent_output import AgentOutputSchema
from openai.types.shared.reasoning import Reasoning
from .schemas import SEOAnalysisResult
from .prompts import SEO_OPTIMIZATION_INSTRUCTIONS


# Create the SEO optimization agent with structured output
seo_optimization_agent = Agent(
    name="SEOOptimizationAgent",
    instructions=SEO_OPTIMIZATION_INSTRUCTIONS,
    model="gpt-5-mini-2025-08-07",  # gpt-5-mini for SEO optimization
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="minimal"),
    ),
    # Enforce structured output for consistent SEO analysis results
    output_type=AgentOutputSchema(SEOAnalysisResult, strict_json_schema=False),
) 