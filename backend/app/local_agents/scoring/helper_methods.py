"""Helper methods for scoring package.

This module defines the names exported by app.local_agents.scoring.__init__ so imports succeed.
Only calculate_intent_score is wired to the LLM-based scorer; the rest are safe pass-throughs
that can be implemented later.
"""

from typing import Any, Dict, List, Optional


def calculate_intent_score(
	items: List[Dict[str, Any]],
	scraped_product: Dict[str, Any],
	base_relevancy_scores: Optional[Dict[str, int]] = None,
) -> List[Dict[str, Any]]:
	"""Append LLM-based intent_score to items using ScoringRunner. Mutates and returns items.

	This strictly uses the intent_scoring_agent (no deterministic fallback).
	"""
	if not items:
		return items
	# Local import to avoid circular imports
	from app.local_agents.scoring.runner import ScoringRunner

	return ScoringRunner.append_intent_scores(
		items, scraped_product, base_relevancy_scores
	)


def analyze_competition_difficulty(
	items: List[Dict[str, Any]],
	*args: Any,
	**kwargs: Any,
) -> Dict[str, Any]:
	"""Placeholder: returns an empty analysis dict. Implement later."""
	return {}


def calculate_priority_score(
	items: List[Dict[str, Any]],
	*args: Any,
	**kwargs: Any,
) -> Dict[str, Any]:
	"""Placeholder: returns an empty priority dict. Implement later."""
	return {}


def rank_keywords_by_priority(
	items: List[Dict[str, Any]],
	*args: Any,
	**kwargs: Any,
) -> List[Dict[str, Any]]:
	"""Placeholder: returns items unchanged. Implement later."""
	return items


def filter_by_thresholds(
	items: List[Dict[str, Any]],
	*args: Any,
	**kwargs: Any,
) -> List[Dict[str, Any]]:
	"""Placeholder: returns items unchanged. Implement later."""
	return items

