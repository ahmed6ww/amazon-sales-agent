from typing import Dict, List

from .schemas import KeywordCategory, KeywordData, KeywordAnalysisResult, CategoryStats


def categorize_keywords_from_csv(
	scraped_product: dict, base_relevancy_scores: Dict[str, int]
) -> KeywordAnalysisResult:
	"""Lightweight local categorizer as a fallback (heuristic only).
	The primary path should use the KeywordAgent via KeywordRunner.
	"""
	title = (
		((scraped_product or {}).get("elements", {}) or {})
		.get("productTitle", {})
		.get("text")
	)
	if isinstance(title, list):
		title = title[0] if title else ""
	title_l = (title or "").lower()

	items: List[KeywordData] = []
	for kw, score in (base_relevancy_scores or {}).items():
		k = (kw or "").strip()
		kl = k.lower()
		cat = KeywordCategory.RELEVANT
		reason = ""
		# Branded
		if any(x in kl for x in ["keekaroo", "skip hop", "frida", "munchkin", "hatch"]):
			cat = KeywordCategory.BRANDED
			reason = "Contains a brand name"
		# Spanish/other language (naive)
		elif any(ch for ch in kl if ord(ch) > 127) or any(w in kl for w in ["para", "cambiador", "pañal", "niño", "niña"]):
			cat = KeywordCategory.SPANISH
			reason = "Non-English or Spanish term"
		# Outlier (very broad)
		elif any(w in kl for w in ["baby products", "baby stuff", "baby items", "kids", "products"]):
			cat = KeywordCategory.OUTLIER
			reason = "Very broad, high-variety term"
		# Design-specific (contains qualifiers)
		elif any(w in kl for w in ["for dresser", "wipeable", "waterproof", "portable", "travel", "foam", "peanut", "contoured", "with straps"]):
			cat = KeywordCategory.DESIGN_SPECIFIC
			reason = "Specific feature/use-case/style"
		# Irrelevant (product mismatch)
		elif not kl or (title_l and not any(t in title_l for t in kl.split())):
			cat = KeywordCategory.IRRELEVANT
			reason = "Does not match core product"
		else:
			cat = KeywordCategory.RELEVANT
			reason = "Describes the core product"

		items.append(
			KeywordData(
				phrase=k,
				category=cat,
				reason=reason,
				relevancy_score=int(score) if isinstance(score, (int, float)) else 0,
			)
		)

	# Build stats
	by_cat: Dict[KeywordCategory, List[str]] = {c: [] for c in KeywordCategory}
	for it in items:
		if it.category not in by_cat:
			by_cat[it.category] = []
		if len(by_cat[it.category]) < 5:
			by_cat[it.category].append(it.phrase)

	stats = {
		c: CategoryStats(count=sum(1 for it in items if it.category == c), examples=by_cat.get(c, []))
		for c in KeywordCategory
	}

	return KeywordAnalysisResult(product_context={"title": title}, items=items, stats=stats)

