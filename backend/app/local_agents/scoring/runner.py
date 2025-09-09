from __future__ import annotations

from typing import Any, Dict, List
import logging


logger = logging.getLogger(__name__)


class ScoringRunner:
	"""Compute buyer intent (0..3) and sorted views for keywords.

	Inputs:
	  - scraped_product: dict (from research)
	  - keyword_items: list of dicts (KeywordAnalysisResult.items)

	Output:
	  - ScoringResult with intent_view (flat_sorted/by_intent/counts)
	"""

	def build_intent_view(
		self,
		scraped_product: Dict[str, Any],
		keyword_items: List[Dict[str, Any]],
		use_llm: bool = False,
	) -> Dict[str, Any]:
		# Deterministic local computation (scoring only, no sorting)
		# Import utilities at runtime to avoid package path issues in various runners
		import importlib
		intent_mod = importlib.import_module('app.services.keyword_processing.intent')
		classify_intent = getattr(intent_mod, 'classify_intent')
		extract_brand_tokens = getattr(intent_mod, 'extract_brand_tokens')

		brand_tokens = extract_brand_tokens(scraped_product)
		items_with_scores: List[Dict[str, Any]] = []
		for it in (keyword_items or []):
			phrase = (it or {}).get("phrase") or ""
			category = (it or {}).get("category")
			res = classify_intent(
				phrase=phrase,
				scraped_product=scraped_product or {},
				category=category,
				brand_tokens=brand_tokens,
			)
			items_with_scores.append({**it, "intent_score": res.intent_score})

		return {
			"product_context": {
				"title": (
					(((scraped_product or {}).get("elements", {}) or {}).get("productTitle", {}) or {}
				).get("text")
				)
			},
			"intent_scores": items_with_scores,
		}

	@staticmethod
	def append_intent_scores(
		items: List[Dict[str, Any]],
		scraped_product: Dict[str, Any],
		base_relevancy_scores: Dict[str, int] | None = None,
	) -> List[Dict[str, Any]]:
		"""Append intent_score using the LLM intent_scoring_agent, preserving order. No fallback.
		"""
		if not items:
			return items
		logger.info("[ScoringRunner] Calling IntentScoringSubagent for %d items", len(items))
		from agents import Runner as _Runner
		from app.local_agents.scoring.subagents.intent_agent import (
			intent_scoring_agent,
			USER_PROMPT_TEMPLATE,
		)
		import json as _json
		prompt = USER_PROMPT_TEMPLATE.format(
			scraped_product=_json.dumps(scraped_product or {}, separators=(",", ":")),
			base_relevancy_scores=_json.dumps(base_relevancy_scores or {}, separators=(",", ":")),
			items=_json.dumps(items or [], separators=(",", ":")),
		)
		# Try to attach optional metadata for better tracing; ignore if Runner doesn't support it
		try:
			result = _Runner.run_sync(
				intent_scoring_agent,
				prompt,
				metadata={
					"component": "ScoringRunner",
					"subagent": "IntentScoringSubagent",
					"items_count": len(items),
				},
			)
		except TypeError:
			# Older SDK signature
			result = _Runner.run_sync(intent_scoring_agent, prompt)
		output = getattr(result, "final_output", None)
		if isinstance(output, str):
			# Log a small preview to aid debugging/parsing issues
			logger.debug("[ScoringRunner] Intent raw output preview: %s", output[:500])
		# Expecting a list of objects matching input order
		scored = []
		if output is not None and hasattr(output, "model_dump"):
			try:
				scored = output.model_dump()  # type: ignore
			except Exception:
				scored = []
		elif isinstance(output, list):
			scored = output
		elif isinstance(output, str):
			# Try to parse a JSON array from text
			try:
				parsed = _json.loads(output)
				if isinstance(parsed, list):
					scored = parsed
			except Exception:
				pass
			if not scored:
				# Try to find the last JSON array in the text
				import re as _re
				matches = _re.findall(r"\[[\s\S]*\]", output.strip())
				for snippet in reversed(matches):
					try:
						candidate = _json.loads(snippet)
						if isinstance(candidate, list):
							scored = candidate
							break
					except Exception:
						continue
		# Map back by index to preserve order; write intent_score only
		for idx, it in enumerate(items):
			try:
				it["intent_score"] = int((scored[idx] or {}).get("intent_score", 0))
			except Exception:
				it["intent_score"] = 0
		logger.info("[ScoringRunner] Intent scores applied to %d items", len(items))
		return items

	@staticmethod
	def merge_metrics(
		items: List[Dict[str, Any]],
		revenue_csv: List[Dict[str, Any]] | None = None,
		design_csv: List[Dict[str, Any]] | None = None,
	) -> List[Dict[str, Any]]:
		"""Append metrics from CSVs onto items without removing existing values.

		Builds a base map from items using 'relevancy_score' (or 'base_relevancy_score' fallback)
		for compatibility with different upstream keyword agents.
		"""
		if not items:
			return items
		# Local import to keep module load light
		from app.local_agents.scoring.subagents import (
			collect_metrics_from_csv,
			merge_metrics_into_items,
		)

		base_map: Dict[str, int] = {}
		for it in items:
			phrase = str((it or {}).get("phrase") or "").strip()
			if not phrase:
				continue
			val = (
				it.get("relevancy_score")
				if isinstance(it.get("relevancy_score"), int)
				else it.get("base_relevancy_score")
			)
			try:
				base_map[phrase] = int(val) if val is not None else 0
			except Exception:
				base_map[phrase] = 0

		metrics_map = collect_metrics_from_csv(base_map, revenue_csv, design_csv)
		return merge_metrics_into_items(items, metrics_map)

	@staticmethod
	def score_and_enrich(
		items: List[Dict[str, Any]],
		scraped_product: Dict[str, Any],
		revenue_csv: List[Dict[str, Any]] | None = None,
		design_csv: List[Dict[str, Any]] | None = None,
		base_relevancy_scores: Dict[str, int] | None = None,
		include_broad_volume: bool = True,
	) -> List[Dict[str, Any]]:
		"""End-to-end convenience: append LLM intent scores, merge CSV metrics, and calculate broad volume."""
		# Step 1: Add intent scores
		ScoringRunner.append_intent_scores(items, scraped_product, base_relevancy_scores)
		
		# Step 2: Merge CSV metrics
		enriched_items = ScoringRunner.merge_metrics(items, revenue_csv, design_csv)
		
		# Step 3: Add broad volume calculation if requested
		if include_broad_volume:
			try:
				from app.local_agents.scoring.subagents.broad_volume_agent import calculate_broad_volume
				from app.services.keyword_processing.intent import extract_brand_tokens
				
				brand_tokens = extract_brand_tokens(scraped_product)
				broad_volume_result = calculate_broad_volume(
					enriched_items, 
					brand_tokens=brand_tokens, 
					use_llm=False  # Use deterministic for this helper method
				)
				enriched_items = broad_volume_result.get("items", enriched_items)
				
			except Exception as e:
				logger.warning(f"[ScoringRunner] Broad volume calculation failed in score_and_enrich: {e}")
		
		return enriched_items

	def run_full_scoring_analysis(
		self,
		keyword_analysis,
		product_attributes: Dict[str, Any],
		business_context: Dict[str, Any],
	) -> Dict[str, Any]:
		"""
		Complete scoring analysis workflow with intent scoring, metrics integration, and opportunity detection.
		
		This is the main method called by the analyze endpoint to run the full scoring pipeline.
		"""
		try:
			logger.info("[ScoringRunner] Starting full scoring analysis")
			
			# Extract data from keyword analysis
			if hasattr(keyword_analysis, 'items'):
				items = keyword_analysis.items
			elif hasattr(keyword_analysis, 'dict'):
				items = keyword_analysis.dict().get('items', [])
			else:
				items = keyword_analysis.get('items', [])
			
			# Convert items to dicts if they're objects
			items_list = []
			for item in items:
				if hasattr(item, 'dict'):
					items_list.append(item.dict())
				elif isinstance(item, dict):
					items_list.append(item)
				else:
					items_list.append({'phrase': str(item), 'category': 'Unknown', 'base_relevancy_score': 0})
			
			if not items_list:
				logger.warning("[ScoringRunner] No items found for scoring")
				return {
					"success": True,
					"intent_view": {
						"flat_sorted": [],
						"by_intent": {"3": [], "2": [], "1": [], "0": []},
						"counts": {"3": 0, "2": 0, "1": 0, "0": 0}
					},
					"total_keywords": 0,
					"message": "No keywords to score"
				}
			
			# Prepare scraped product context
			scraped_product = product_attributes.get('scraped_product', {})
			if not scraped_product and 'ai_analysis' in product_attributes:
				# Fallback: create minimal product context from available data
				scraped_product = {
					"elements": {
						"productTitle": {
							"text": product_attributes.get('product_title', '')
						}
					}
				}
			
			# Step 1: Add intent scores using LLM
			logger.info(f"[ScoringRunner] Adding intent scores to {len(items_list)} keywords")
			base_relevancy_scores = {}
			for item in items_list:
				phrase = item.get('phrase', '')
				score = item.get('base_relevancy_score', item.get('relevancy_score', 0))
				if phrase:
					base_relevancy_scores[phrase] = score
			
			enriched_items = self.append_intent_scores(
				items_list, 
				scraped_product, 
				base_relevancy_scores
			)
			
			# Step 2: Merge CSV metrics (revenue and design data would need to be passed)
			# Note: CSV data not available in current method signature, would need to be added
			logger.info("[ScoringRunner] CSV metrics integration skipped - no CSV data provided")
			
			# Step 3: Calculate broad volume by root words
			logger.info(f"[ScoringRunner] Calculating broad search volume for {len(enriched_items)} keywords")
			try:
				from app.local_agents.scoring.subagents.broad_volume_agent import calculate_broad_volume
				from app.services.keyword_processing.intent import extract_brand_tokens
				
				# Extract brand tokens for better root word identification
				brand_tokens = extract_brand_tokens(scraped_product)
				
				# Calculate broad volume (try LLM first, fallback to deterministic)
				broad_volume_result = calculate_broad_volume(
					enriched_items, 
					brand_tokens=brand_tokens, 
					use_llm=True
				)
				
				# Update items with root information
				enriched_items = broad_volume_result.get("items", enriched_items)
				broad_search_volume_by_root = broad_volume_result.get("broad_search_volume_by_root", {})
				
				logger.info(f"[ScoringRunner] Identified {len(broad_search_volume_by_root)} root words")
				
			except Exception as e:
				logger.warning(f"[ScoringRunner] Broad volume calculation failed: {e}")
				broad_search_volume_by_root = {}
			
			# Step 4: Sort and group by intent
			from app.services.keyword_processing.sort import sort_keywords_by_intent
			sorted_result = sort_keywords_by_intent(enriched_items, scraped_product)
			
			# Step 5: Calculate summary stats
			total_keywords = len(enriched_items)
			high_intent_count = len(sorted_result["by_intent"].get("3", [])) + len(sorted_result["by_intent"].get("2", []))
			
			logger.info(f"[ScoringRunner] Scoring complete: {total_keywords} keywords, {high_intent_count} high-intent")
			
			return {
				"success": True,
				"intent_view": sorted_result,
				"broad_search_volume_by_root": broad_search_volume_by_root,
				"total_keywords": total_keywords,
				"high_intent_keywords": high_intent_count,
				"summary": {
					"intent_3_count": sorted_result["counts"].get("3", 0),
					"intent_2_count": sorted_result["counts"].get("2", 0), 
					"intent_1_count": sorted_result["counts"].get("1", 0),
					"intent_0_count": sorted_result["counts"].get("0", 0),
					"total_root_words": len(broad_search_volume_by_root),
					"top_root_words": dict(sorted(broad_search_volume_by_root.items(), key=lambda x: x[1], reverse=True)[:10])
				}
			}
			
		except Exception as e:
			logger.error(f"[ScoringRunner] Full scoring analysis failed: {e}")
			return {
				"success": False,
				"error": str(e),
				"intent_view": {
					"flat_sorted": [],
					"by_intent": {"3": [], "2": [], "1": [], "0": []},
					"counts": {"3": 0, "2": 0, "1": 0, "0": 0}
				},
				"broad_search_volume_by_root": {},
				"total_keywords": 0
			}

