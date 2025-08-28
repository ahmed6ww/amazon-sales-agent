from typing import Dict, Any
from agents import Agent, Runner, ModelSettings
from .agent import tool_scrape_amazon_listing

# Minimal agent: call the scrape tool once and stop
mini_research_agent = Agent(
    name="MiniResearchAgent",
    instructions=(
        "Scrape exactly one Amazon ASIN or URL and return the raw JSON string from the tool."
    ),
    tools=[tool_scrape_amazon_listing],
    model_settings=ModelSettings(tool_choice="tool_scrape_amazon_listing"),
    tool_use_behavior="stop_on_first_tool",
)

class MiniResearchRunner:
    """Runner for a single-scrape flow to avoid reactor restarts."""

    def run(self, asin_or_url: str) -> Dict[str, Any]:
        prompt = f"Scrape: {asin_or_url}"
        result = Runner.run_sync(mini_research_agent, prompt)
        return {
            "success": True,
            "final_output": result.final_output,
        } 