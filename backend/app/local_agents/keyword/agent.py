from agents import Agent, ModelSettings
from agents.agent_output import AgentOutputSchema

from .schemas import KeywordAnalysisResult
from .prompts import KEYWORD_AGENT_INSTRUCTIONS


# Define the Keyword Agent using the same agent SDK style as ResearchAgent
keyword_agent = Agent(
	name="KeywordAgent",
	instructions=KEYWORD_AGENT_INSTRUCTIONS,
	model="gpt-4o-mini",  # GPT-4o-mini: More stable, reliable for large keyword sets
	model_settings=ModelSettings(
		max_tokens=8000,  # Increased for large keyword sets (80-100+ keywords)
		timeout=180.0,     # 3 minute timeout for large requests
	),
	output_type=AgentOutputSchema(KeywordAnalysisResult, strict_json_schema=False),
)

