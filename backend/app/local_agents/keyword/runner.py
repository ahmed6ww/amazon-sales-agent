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
		"""
		Run AI-powered keyword categorization.
		
		PURPOSE: Categorize keywords into: Relevant, Design-Specific, Irrelevant, Branded, Spanish, Outlier
		INPUT: Keywords with relevancy scores (0-10) from research agent
		OUTPUT: Categorized keywords with assigned categories and reasons
		"""
		logger.info("")
		logger.info("="*80)
		logger.info("🤖 [KEYWORD CATEGORIZATION AGENT]")
		logger.info("="*80)
		logger.info("📋 What: AI categorizes keywords into 6 categories")
		logger.info("🎯 Why: Separate relevant keywords from irrelevant/branded/outliers")
		logger.info("💡 Categories: Relevant, Design-Specific, Irrelevant, Branded, Spanish, Outlier")
		logger.info("="*80)
		
		# Filter out zero relevancy scores
		filtered_relevancy_scores = {
			keyword: score for keyword, score in base_relevancy_scores.items()
			if score > 0
		}
		logger.info(f"")
		logger.info(f"🔍 [PRE-FILTER] Removing keywords with 0 relevancy score")
		logger.info(f"   📊 Input: {len(base_relevancy_scores)} keywords")
		logger.info(f"   🎯 Output: {len(filtered_relevancy_scores)} keywords (score 1-10)")
		logger.info(f"   🗑️  Filtered: {len(base_relevancy_scores) - len(filtered_relevancy_scores)} keywords (score 0)")

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

		# Post-process: Normalize field names (base_relevancy_score -> relevancy_score)
		if structured and "items" in structured:
			logger.info(f"")
			logger.info(f"🔧 [POST-PROCESSING] Normalizing AI output field names")
			logger.info(f"   📋 What: Ensure 'relevancy_score' field is present")
			logger.info(f"   💡 Why: AI may return 'base_relevancy_score' instead")
			logger.info(f"   🎯 Processing: {len(structured['items'])} keywords")
			for item in structured["items"]:
				# Handle both field name scenarios
				if "base_relevancy_score" in item and "relevancy_score" not in item:
					# AI returned base_relevancy_score, rename to relevancy_score
					item["relevancy_score"] = item.pop("base_relevancy_score")
					logger.debug(f"[KeywordRunner] Renamed base_relevancy_score -> relevancy_score for '{item.get('phrase', 'unknown')}'")
				elif "relevancy_score" in item and "base_relevancy_score" in item:
					# Both fields exist, keep relevancy_score and remove base_relevancy_score
					item.pop("base_relevancy_score", None)
					logger.debug(f"[KeywordRunner] Removed duplicate base_relevancy_score for '{item.get('phrase', 'unknown')}'")
				elif "relevancy_score" not in item and "base_relevancy_score" not in item:
					# Neither field exists, this shouldn't happen
					logger.error(f"[KeywordRunner] No relevancy score found for '{item.get('phrase', 'unknown')}'")
				
				# Ensure relevancy_score is always present
				if "relevancy_score" not in item:
					logger.error(f"[KeywordRunner] ❌ relevancy_score still missing for '{item.get('phrase', 'unknown')}' after processing!")
					# Try to get from base_relevancy_score as last resort
					if "base_relevancy_score" in item:
						item["relevancy_score"] = item.pop("base_relevancy_score")
						logger.warning(f"[KeywordRunner] Emergency fix: copied base_relevancy_score to relevancy_score for '{item.get('phrase', 'unknown')}'")
				
				# Log the final relevancy_score
				if "relevancy_score" in item:
					logger.debug(f"[KeywordRunner] ✅ '{item.get('phrase', 'unknown')}': relevancy_score={item['relevancy_score']}/10")
				else:
					logger.error(f"[KeywordRunner] ❌ relevancy_score MISSING for '{item.get('phrase', 'unknown')}'")

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