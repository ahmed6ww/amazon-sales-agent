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
	) -> List[Dict[str, Any]]:
		"""End-to-end convenience: append LLM intent scores, then merge CSV metrics."""
		ScoringRunner.append_intent_scores(items, scraped_product, base_relevancy_scores)
		return ScoringRunner.merge_metrics(items, revenue_csv, design_csv)

