from __future__ import annotations

from typing import Any, Dict, List
import logging
import json

from agents import Runner
from app.local_agents.keyword.agent import keyword_agent

logger = logging.getLogger(__name__)


class KeywordRunner:
	"""Run keyword categorization agent on scraped product + base relevancy scores.

	Inputs:
	  - scraped_product: dict (from research)
	  - base_relevancy_scores: {keyword -> 0..10}

	Output:
	  - KeywordAnalysisResult with items (phrase, category, relevancy_score)
	"""

	def run_keyword_categorization(
		self,
		scraped_product: Dict[str, Any],
		base_relevancy_scores: Dict[str, int],
		marketplace: str = "US",
		asin_or_url: str = "",
		csv_products: List[Dict[str, Any]] = None,
	) -> Dict[str, Any]:
		"""Run keyword categorization agent."""
		# Filter out zero relevancy scores
		filtered_relevancy_scores = {
			keyword: score for keyword, score in base_relevancy_scores.items()
			if score > 0
		}
		logger.info(f"Filtered {len(base_relevancy_scores) - len(filtered_relevancy_scores)} keywords with relevancy score 0")
		logger.info(f"Processing {len(filtered_relevancy_scores)} keywords with relevancy score 1-10")

		prompt = (
			f"SCRAPED PRODUCT (exact):\n{json.dumps(scraped_product or {}, separators=(',', ':'))}\n\n"
			f"BASE RELEVANCY (1-10) — keyword->score (filtered to exclude score 0):\n{json.dumps(filtered_relevancy_scores, separators=(',', ':'))}\n\n"
			f"MARKETPLACE: {marketplace}\n\n"
			f"ASIN/URL: {asin_or_url}\n\n"
			"Return a KeywordAnalysisResult."
		)

		result = Runner.run_sync(keyword_agent, prompt)
		raw_output = getattr(result, "final_output", None)

		# If SDK returned a Pydantic model
		structured: Dict[str, Any] = {}
		if raw_output is not None and hasattr(raw_output, "model_dump"):
			try:
				structured = raw_output.model_dump()
			except Exception:
				structured = {}

		if not structured and isinstance(raw_output, dict):
			structured = raw_output

		# Best-effort JSON extraction if narrative string
		if not structured and isinstance(raw_output, str):
			try:
				# Try direct JSON parsing
				structured = json.loads(raw_output.strip())
			except Exception:
				# Try to find JSON in the text
				import re
				matches = re.findall(r"\{[\s\S]*\}", raw_output.strip())
				for match in reversed(matches):
					try:
						candidate = json.loads(match)
						if isinstance(candidate, dict) and "items" in candidate:
							structured = candidate
							break
					except Exception:
						continue

		# Ensure we have the expected structure
		if not structured or "items" not in structured:
			logger.warning("Keyword agent output not in expected format, creating fallback")
			structured = {
				"items": [
					{
						"phrase": keyword,
						"category": "Relevant",
						"relevancy_score": score
					}
					for keyword, score in filtered_relevancy_scores.items()
				],
				"stats": {
					"Relevant": {"count": len(filtered_relevancy_scores)},
					"Design-Specific": {"count": 0},
					"Irrelevant": {"count": 0}
				}
			}

		# Ensure relevancy scores are integers
		for item in structured.get("items", []):
			if "relevancy_score" in item:
				try:
					item["relevancy_score"] = int(item["relevancy_score"])
				except Exception:
					item["relevancy_score"] = 5  # Default fallback

		return {
			"structured_data": structured,
			"source": "keyword_agent",
			"total_keywords": len(filtered_relevancy_scores)
		}