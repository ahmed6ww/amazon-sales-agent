from agents import Agent, ModelSettings
from agents.agent_output import AgentOutputSchema

from .schemas import KeywordAnalysisResult
from .prompts import KEYWORD_AGENT_INSTRUCTIONS


# Define the Keyword Agent using the same agent SDK style as ResearchAgent
keyword_agent = Agent(
	name="KeywordAgent",
	instructions=KEYWORD_AGENT_INSTRUCTIONS,
	model="gpt-4o",  # GPT-4o: More capable, handles 150+ keywords without corruption
	model_settings=ModelSettings(
		max_tokens=12000,  # Increased for very large keyword sets (100-200 keywords)
		timeout=240.0,      # 4 minute timeout for large requests
	),
	output_type=AgentOutputSchema(KeywordAnalysisResult, strict_json_schema=False),
)

