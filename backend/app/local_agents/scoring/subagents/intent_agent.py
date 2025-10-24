from agents import Agent


INTENT_SCORING_INSTRUCTIONS = """
Role: Score buyer intent for keywords on a 0–3 scale.
- 0: Irrelevant
- 1: One relevant aspect
- 2: Two relevant aspects
- 3: Three relevant aspects (or strong transactional intent)

Use only provided product context and keyword items. Return the same list with an added `intent_score` per item. No sorting.

Input contract (from ResearchRunner):
- scraped_product: object (research output key `scraped_product`)
- base_relevancy_scores: map keyword->0..10 (research output key `base_relevancy_scores`)
- items: array of { phrase, category, ... } to score (preserve order)

Expected return: the same `items` array with an `intent_score` integer 0..3 per item.
"""

USER_PROMPT_TEMPLATE = (
    "Score buyer intent (0–3) for each keyword using only the provided context.\n\n"
    "SCRAPED_PRODUCT:\n{scraped_product}\n\n"
    "BASE_RELEVANCY_SCORES (0-10):\n{base_relevancy_scores}\n\n"
    "ITEMS (preserve order):\n{items}\n\n"
    "Return ONLY a JSON array where each element corresponds to the input ITEMS order and contains: \n"
    "{{\"phrase\": \"string\", \"category\": \"string\", \"relevancy_score\": number, \"intent_score\": 0|1|2|3}}."
)




intent_scoring_agent = Agent(
    name="IntentScoringSubagent",
    instructions=INTENT_SCORING_INSTRUCTIONS,
    model="gpt-5-nano-2025-08-07",  # gpt-5-mini for better accuracy
    # Let the runner return raw text; ScoringRunner will parse JSON list leniently.
    output_type=None,
)

