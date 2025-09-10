"""Helper methods for scoring package.

This module provides AI-based scoring functionality for the scoring agent.
Currently implements LLM-based intent scoring through the ScoringRunner.
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




