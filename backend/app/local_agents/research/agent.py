from agents import Agent, ModelSettings
from dotenv import load_dotenv, find_dotenv

from agents.agent_output import AgentOutputSchema
from .schemas import ResearchOutput
from .prompts import RESEARCH_AGENT_INSTRUCTIONS


load_dotenv(find_dotenv())  # Load environment variables from .env file


research_agent = Agent(
    name="ResearchAgent",
    instructions=RESEARCH_AGENT_INSTRUCTIONS,
    model="gpt-5-2025-08-07",
    # model_settings=ModelSettings(
    #     max_tokens=4000,
    # ),
    # Enforce structured output; keep schema non-strict to allow additive fields
    output_type=AgentOutputSchema(ResearchOutput, strict_json_schema=False),
)