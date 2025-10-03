from typing import Dict, List

from .schemas import KeywordCategory, KeywordData, KeywordAnalysisResult, CategoryStats


def categorize_keywords_from_csv(
	scraped_product: dict, base_relevancy_scores: Dict[str, int]
) -> KeywordAnalysisResult:
	"""AI-powered categorizer as a fallback when main agent fails.
	Uses a lightweight AI agent to categorize keywords dynamically.
	"""
	import json
	from .agent import keyword_agent
	from .runner import Runner
	from .prompts import FALLBACK_CATEGORIZATION_PROMPT
	
	# Use the centralized prompt template
	prompt = FALLBACK_CATEGORIZATION_PROMPT.format(
		scraped_product=json.dumps(scraped_product or {}, separators=(',', ':')),
		base_relevancy_scores=json.dumps(base_relevancy_scores, separators=(',', ':'))
	)
	
	try:
		# Use AI agent for categorization
		result = Runner.run_sync(keyword_agent, prompt)
		raw_output = getattr(result, "final_output", None)
		
		# If SDK returned a Pydantic model
		if hasattr(result, "items") and hasattr(result, "stats"):
			return result
		
		# If we got raw text, try to parse it
		if raw_output:
			try:
				parsed = json.loads(raw_output)
				if "items" in parsed and "stats" in parsed:
					return KeywordAnalysisResult(**parsed)
			except json.JSONDecodeError:
				pass
		
		# If AI fails, return empty result
		stats = {
			c: CategoryStats(count=0, examples=[])
			for c in KeywordCategory
		}
		return KeywordAnalysisResult(product_context={}, items=[], stats=stats)
		
	except Exception as e:
		# If AI agent fails completely, return empty result
		stats = {
			c: CategoryStats(count=0, examples=[])
			for c in KeywordCategory
		}
		return KeywordAnalysisResult(product_context={}, items=[], stats=stats)

