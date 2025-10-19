from agents import Agent, ModelSettings
from agents.agent_output import AgentOutputSchema

from .schemas import KeywordAnalysisResult
from .prompts import KEYWORD_AGENT_INSTRUCTIONS


# Define the Keyword Agent using the same agent SDK style as ResearchAgent
keyword_agent = Agent(
	name="KeywordAgent",
	instructions=KEYWORD_AGENT_INSTRUCTIONS,
	model="gpt-4o-mini",  # TASK 5: Changed from gpt-5 for 3-4x speed improvement
	# model_settings=ModelSettings(max_tokens=3000),
	output_type=AgentOutputSchema(KeywordAnalysisResult, strict_json_schema=False),
)

