from agents import Agent, ModelSettings
from agents.agent_output import AgentOutputSchema

from .schemas import KeywordAnalysisResult
from .prompts import KEYWORD_AGENT_INSTRUCTIONS


# Define the Keyword Agent using the same agent SDK style as ResearchAgent
keyword_agent = Agent(
	name="KeywordAgent",
	instructions=KEYWORD_AGENT_INSTRUCTIONS,
	model="gpt-5-2025-08-07",  # gpt-5-mini - With batching (75 kw/batch), mini works great
	model_settings=ModelSettings(
		max_tokens=12000,  # Sufficient for 75 keywords per batch
		timeout=240.0,      # 4 minute timeout for large requests
	),
	output_type=AgentOutputSchema(KeywordAnalysisResult, strict_json_schema=False),
)

