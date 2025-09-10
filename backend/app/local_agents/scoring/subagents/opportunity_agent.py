from agents import Agent


OPPORTUNITY_INSTRUCTIONS = """
Role: Apply zero-title-density opportunity rules.
- If title_density == 0: ignore if irrelevant or derivative/misspelling; else mark as opportunity if volume is decent and root is distinct.
- If 0 < title_density <= low_threshold and volume is decent: mark as opportunity.
Return: original items with `opportunity_decision` and `opportunity_reason`.
"""


opportunity_agent = Agent(
    name="OpportunitySubagent",
    instructions=OPPORTUNITY_INSTRUCTIONS,
    model="gpt-5-2025-08-07",
)
