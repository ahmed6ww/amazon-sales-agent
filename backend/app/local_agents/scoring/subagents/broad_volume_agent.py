from agents import Agent


BROAD_VOLUME_INSTRUCTIONS = """
Role: Compute broad search volume per root word.
- Identify a simple root token for each keyword (e.g., main noun excluding stopwords/brands).
- Sum search_volume across all keywords sharing that root.
Return: the original list with `root` field per item and a separate map `broad_search_volume_by_root`.
No sorting; no external data.
"""


broad_volume_agent = Agent(
    name="BroadVolumeSubagent",
    instructions=BROAD_VOLUME_INSTRUCTIONS,
    model="gpt-5-2025-08-07",
)
