"""
SEO Optimization Agent

Amazon SEO analysis and optimization agent for listing improvement.
"""

from agents import Agent, ModelSettings
from agents.agent_output import AgentOutputSchema
from .schemas import SEOAnalysisResult
from .prompts import SEO_OPTIMIZATION_INSTRUCTIONS


# Create the SEO optimization agent with structured output
seo_optimization_agent = Agent(
    name="SEOOptimizationAgent",
    instructions=SEO_OPTIMIZATION_INSTRUCTIONS,
    model="gpt-5-2025-08-07",
    model_settings=ModelSettings(
        max_tokens=4000,  # Need higher token count for comprehensive SEO analysis
    ),
    # Enforce structured output for consistent SEO analysis results
    output_type=AgentOutputSchema(SEOAnalysisResult, strict_json_schema=False),
) 