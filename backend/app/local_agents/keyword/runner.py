from typing import Any, Dict, List, Optional
import logging

from agents import Runner

from .agent import keyword_agent

logger = logging.getLogger(__name__)


class KeywordRunner:
	"""
	Minimal runner for the KeywordAgent. It only consumes:
	- scraped_product: dict from ResearchRunner output (scraped product elements)
	- base_relevancy_scores: {keyword -> 0..10}
	and returns the agent's structured categorization.
	"""

	def run_keyword_categorization(
		self,
		scraped_product: Dict[str, Any],
		base_relevancy_scores: Dict[str, int],
		marketplace: Optional[str] = None,
		asin_or_url: Optional[str] = None,
		csv_products: Optional[List[Dict[str, Any]]] = None,
	) -> Dict[str, Any]:
		import json

		# Filter out keywords with relevancy score 0 (requirement #2)
		filtered_relevancy_scores = {
			keyword: score for keyword, score in base_relevancy_scores.items()
			if score > 0
		}
		
		logger.info(f"Filtered {len(base_relevancy_scores) - len(filtered_relevancy_scores)} keywords with relevancy score 0")
		logger.info(f"Processing {len(filtered_relevancy_scores)} keywords with relevancy score 1-10")

		# Apply search-based categorization if CSV products are provided (requirements #20-24)
		if csv_products and marketplace:
			logger.info(f"Applying search-based categorization with {len(csv_products)} CSV products")
			from app.services.amazon.keyword_categorizer import categorize_keywords_with_amazon_search
			
			# Extract keywords for search-based categorization
			keywords_to_categorize = list(filtered_relevancy_scores.keys())
			
			# Categorize keywords using Amazon search analysis
			search_categorization = categorize_keywords_with_amazon_search(
				keywords_to_categorize, 
				csv_products, 
				marketplace
			)
			
			# Update relevancy scores with search-based categories
			for keyword, result in search_categorization.get("categorization_results", {}).items():
				if keyword in filtered_relevancy_scores:
					# Override category based on search results
					search_category = result.get("category", "Relevant")
					# Apply classification rules (requirements #22-24)
					filtered_relevancy_scores[keyword] = {
						"score": filtered_relevancy_scores[keyword],
						"search_category": search_category,
						"search_confidence": result.get("confidence", 0.0),
						"search_reason": result.get("reason", "")
					}
			
			logger.info(f"Search-based categorization completed for {len(keywords_to_categorize)} keywords")

		prompt = (
			"Categorize the provided keywords using only the given scraped_product (exact as provided) and base relevance map.\n\n"  # noqa: E501
			f"SCRAPED PRODUCT (exact):\n{json.dumps(scraped_product or {}, separators=(',', ':'))}\n\n"
			f"BASE RELEVANCY (1-10) — keyword->score (filtered to exclude score 0):\n{json.dumps(filtered_relevancy_scores, separators=(',', ':'))}\n\n"
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
				# attempt to parse as full JSON first
				structured = json.loads(raw_output)
			except Exception:
				# fallback: try to find last JSON object
				import re
				matches = re.findall(r"\{[\s\S]*\}", raw_output.strip())
				for snippet in reversed(matches):
					try:
						candidate = json.loads(snippet)
						if isinstance(candidate, dict):
							structured = candidate
							break
					except Exception:
						continue
		
		# Validate and fix malformed JSON structure
		if structured and isinstance(structured, dict):
			# Check if items array contains malformed data
			items = structured.get("items", [])
			if isinstance(items, list):
				# Filter out any non-dict items (like strings that got mixed in)
				valid_items = []
				for item in items:
					if isinstance(item, dict):
						valid_items.append(item)
					else:
						logger.warning(f"Removing invalid item from items array: {item}")
				structured["items"] = valid_items
			
			# Ensure stats is a proper dict, not mixed into items
			if "stats" not in structured and items:
				# Try to extract stats from the end of items if it got mixed in
				last_item = items[-1] if items else None
				if isinstance(last_item, str) and "stats" in last_item:
					try:
						# Try to parse the stats part
						stats_match = re.search(r'"stats":\s*(\{.*\})', last_item)
						if stats_match:
							stats_json = stats_match.group(1)
							structured["stats"] = json.loads(stats_json)
							# Remove the malformed last item
							structured["items"] = items[:-1]
							logger.info("✅ Extracted stats from malformed items array")
					except Exception as e:
						logger.warning(f"Failed to extract stats from malformed JSON: {e}")
			
			# Ensure required fields exist
			if "product_context" not in structured:
				structured["product_context"] = {}
			if "items" not in structured:
				structured["items"] = []
			if "stats" not in structured:
				structured["stats"] = {}

		return {
			"success": bool(structured),
			"structured_data": structured or {},
			"final_output": "Keyword categorization completed" if structured else raw_output,
			"scraped_product": scraped_product or {},
			"keywords_count": len(base_relevancy_scores or {}),
		}

