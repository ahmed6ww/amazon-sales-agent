from typing import Any, Dict, List, Optional
import logging

from agents import Runner

from .agent import keyword_agent
from .subagents.design_specific_classification_agent import enhance_keyword_categorization_with_design_logic

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
	) -> Dict[str, Any]:
		import json

		prompt = (
			"Categorize the provided keywords using only the given scraped_product (exact as provided) and base relevance map.\n\n"  # noqa: E501
			f"SCRAPED PRODUCT (exact):\n{json.dumps(scraped_product or {}, separators=(',', ':'))}\n\n"
			f"BASE RELEVANCY (0-10) — keyword->score:\n{json.dumps(base_relevancy_scores, separators=(',', ':'))}\n\n"
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

		# Apply refined design-specific classification logic
		enhanced_structured = structured
		if structured and structured.get("items"):
			try:
				logger.info("🔍 Applying refined design-specific classification logic")
				enhanced_items = enhance_keyword_categorization_with_design_logic(
					keyword_items=structured["items"],
					product_context=scraped_product or {}
				)
				enhanced_structured = structured.copy()
				enhanced_structured["items"] = enhanced_items
				logger.info("✅ Design-specific refinement completed")
			except Exception as e:
				logger.warning(f"⚠️ Design-specific refinement failed: {e}")
				enhanced_structured = structured

		return {
			"success": bool(enhanced_structured),
			"structured_data": enhanced_structured or {},
			"final_output": "Keyword categorization completed with design-specific refinement" if enhanced_structured else raw_output,
			"scraped_product": scraped_product or {},
			"keywords_count": len(base_relevancy_scores or {}),
		}

