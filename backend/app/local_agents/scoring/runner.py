from __future__ import annotations

from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


def strip_markdown_code_fences(text: str) -> str:
	"""
	Remove markdown code fences and extract pure JSON from AI output.
	GPT-4o and gpt-4o-mini often wrap JSON in ```json ... ``` or add extra text.
	
	Handles:
	- Markdown code fences: ```json ... ```
	- Extra text before JSON: "Here's the result: {...}"
	- Extra text after JSON: "{...} Hope this helps!"
	
	Args:
		text: AI output text that may contain markdown fences or extra commentary
		
	Returns:
		Clean JSON text without markdown fences or extra text
	"""
	if not text:
		return text
	
	text = text.strip()
	
	# Step 1: Remove markdown code fences
	if text.startswith('```'):
		# Find end of first line (remove ```json or ``` line)
		first_newline = text.find('\n')
		if first_newline != -1:
			text = text[first_newline + 1:]
	
	if text.endswith('```'):
		text = text[:-3]
	
	text = text.strip()
	
	# Step 2: Extract JSON if there's extra text before/after
	# Look for JSON array [...] or object {...}
	import re
	
	# Try to find complete JSON structure
	# This regex finds the outermost JSON array or object
	json_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', text)
	if json_match:
		extracted = json_match.group(1).strip()
		# Only return extracted JSON if it's substantial (not just empty brackets)
		if len(extracted) > 2:
			return extracted
	
	# If no JSON pattern found, return cleaned text as-is
	return text


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
		use_llm: bool = True,
	) -> Dict[str, Any]:
		# AI-only analysis - no deterministic fallback allowed
		if not use_llm:
			raise ValueError("AI-only mode: deterministic intent classification not allowed")
		
		# Use LLM-based intent scoring through ScoringRunner
		logger.info("[ScoringRunner] Using AI-based intent scoring for build_intent_view")
		enriched_items = self.append_intent_scores(keyword_items, scraped_product)

		return {
			"product_context": {
				"title": (
					(((scraped_product or {}).get("elements", {}) or {}).get("productTitle", {}) or {}
				).get("text")
				)
			},
			"intent_scores": enriched_items,
		}

	@staticmethod
	def append_intent_scores(
		items: List[Dict[str, Any]],
		scraped_product: Dict[str, Any],
		base_relevancy_scores: Dict[str, int] | None = None,
	) -> List[Dict[str, Any]]:
		"""
		Add intent scores (0-3) to keywords using AI agent with BATCHING.
		Prevents timeout for large keyword sets (200+).
		"""
		if not items:
			return items
		
		# ========================================================================
		# BATCHING: Process in chunks to prevent timeout/token limits
		# ========================================================================
		BATCH_SIZE = 75  # Same as keyword categorization
		total_items = len(items)
		all_results = []
		
		logger.info(f"[ScoringRunner] Processing {total_items} items in batches of {BATCH_SIZE}")
		
		num_batches = (total_items + BATCH_SIZE - 1) // BATCH_SIZE
		
		from agents import Runner as _Runner
		from app.local_agents.scoring.subagents.intent_agent import (
			intent_scoring_agent,
			USER_PROMPT_TEMPLATE,
		)
		import json as _json
		import time
		
		for batch_idx in range(num_batches):
			start_idx = batch_idx * BATCH_SIZE
			end_idx = min(start_idx + BATCH_SIZE, total_items)
			batch_items = items[start_idx:end_idx]
			batch_label = f"Batch {batch_idx + 1}/{num_batches}"
			
			logger.info(f"[ScoringRunner] 🔄 {batch_label}: Processing {len(batch_items)} items")
			
			try:
				# Simple rate limiting
				time.sleep(1)
				
				# Run AI intent scoring for this batch
				prompt = USER_PROMPT_TEMPLATE.format(
					scraped_product=_json.dumps(scraped_product or {}, separators=(",", ":")),
					base_relevancy_scores=_json.dumps(base_relevancy_scores or {}, separators=(",", ":")),
					items=_json.dumps(batch_items or [], separators=(",", ":")),
				)
				
				result = _Runner.run_sync(intent_scoring_agent, prompt)
				scored = []
				
				# Parse result
				if result and hasattr(result, 'final_output'):
					output = result.final_output
					if output:
						try:
							clean_output = strip_markdown_code_fences(output)
							parsed_result = _json.loads(clean_output)
							if isinstance(parsed_result, list):
								scored = parsed_result
							elif isinstance(parsed_result, dict) and "items" in parsed_result:
								scored = parsed_result["items"]
						except _json.JSONDecodeError as e:
							logger.warning(f"[ScoringRunner] {batch_label} JSON parse failed: {e}")
				elif result and hasattr(result, 'content'):
					try:
						clean_content = strip_markdown_code_fences(result.content)
						parsed_result = _json.loads(clean_content)
						if isinstance(parsed_result, list):
							scored = parsed_result
						elif isinstance(parsed_result, dict) and "items" in parsed_result:
							scored = parsed_result["items"]
					except _json.JSONDecodeError as e:
						logger.warning(f"[ScoringRunner] {batch_label} JSON parse failed: {e}")
				
				# If parsing succeeded, use scored items
				if scored:
					# Ensure all items have required fields
					for item in scored:
						if "intent_score" not in item or item.get("intent_score") is None:
							item["intent_score"] = 1
						if "relevancy_score" not in item or item.get("relevancy_score") is None:
							if base_relevancy_scores:
								phrase = item.get("phrase", "").lower().strip()
								item["relevancy_score"] = base_relevancy_scores.get(phrase, 5)
							else:
								item["relevancy_score"] = 5
					
					all_results.extend(scored)
					logger.info(f"[ScoringRunner] ✅ {batch_label} complete ({len(scored)} items)")
				else:
					# Fallback: Use original items with default scores
					raise ValueError("Parsing failed")
					
			except Exception as e:
				logger.error(f"[ScoringRunner] ❌ {batch_label} failed: {e}")
				# Fallback: Add default scores to failed batch items
				for item in batch_items:
					item["intent_score"] = 1  # Default moderate intent
					if base_relevancy_scores:
						phrase = item.get("phrase", "").lower().strip()
						item["relevancy_score"] = base_relevancy_scores.get(phrase, 5)
					else:
						item["relevancy_score"] = 5
				all_results.extend(batch_items)
				logger.warning(f"[ScoringRunner] ⚠️  {batch_label} used fallback scores")
		
		logger.info(f"[ScoringRunner] ✅ All batches complete: {len(all_results)}/{total_items} items processed")
		
		return all_results
	
	
	@staticmethod
	def _parse_intent_output(output: Any, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		"""Parse intent scoring output from LLM."""
		scored = []
		
		if output is not None and hasattr(output, "model_dump"):
			try:
				scored = output.model_dump()
			except Exception:
				scored = []
		elif isinstance(output, list):
			scored = output
		elif isinstance(output, str):
			# Try to parse a JSON array from text
			try:
				import json as _json
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
		
		# Ensure we have the right number of results
		if not isinstance(scored, list) or len(scored) != len(items):
			logger.warning("[ScoringRunner] Intent output length mismatch: expected %d, got %d", 
						  len(items), len(scored) if isinstance(scored, list) else 0)
			# Create default scores
			scored = [{"intent_score": 0} for _ in items]
		
		return scored

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
		# Optional pre-pass: DISABLED - variant optimization was too aggressive (77 -> 4)
		# Keeping all keywords for better SEO coverage and bullet point creation
		# try:
		# 	from app.local_agents.scoring.subagents.keyword_variant_agent import apply_variant_optimization_ai
		# 	_before = len(items)
		# 	items = apply_variant_optimization_ai(items)
		# 	logger.info(f"[ScoringRunner] Variant optimization reduced keywords {_before} -> {len(items)}")
		# except Exception as e:
		# 	logger.debug(f"[ScoringRunner] Variant optimization skipped: {e}")
		logger.info(f"[ScoringRunner] Processing all {len(items)} keywords (variant optimization disabled)")
		# Step 1: Add intent scores and apply alignment
		aligned_items = ScoringRunner.append_intent_scores(items, scraped_product, base_relevancy_scores)
		
		# Step 2: Merge CSV metrics (using aligned items)
		enriched_items = ScoringRunner.merge_metrics(aligned_items, revenue_csv, design_csv)
		
		# Step 3: Add broad volume calculation if requested
		if include_broad_volume:
			try:
				from app.local_agents.scoring.subagents.broad_volume_agent import calculate_broad_volume
				from app.services.keyword_processing.intent import extract_brand_tokens
				
				brand_tokens = extract_brand_tokens(scraped_product)
				broad_volume_result = calculate_broad_volume(
					enriched_items, 
					brand_tokens=brand_tokens, 
					use_llm=True  # Use AI analysis only - no deterministic fallback
				)
				enriched_items = broad_volume_result.get("items", enriched_items)
				# Note: filtered root volumes will be computed where they are consumed (API/SEO stage)
			except Exception as e:
				logger.warning(f"[ScoringRunner] Broad volume calculation failed in score_and_enrich: {e}")
		
		# Step 4: Opportunity detection (AI rules) - DISABLED
		# REASON: Redundant with existing metrics (title_density already in data)
		# - Spanish keywords already filtered by category
		# - Title density metric already shows competitor usage
		# - Relevancy scoring already ranks quality
		# - SEO agent makes final inclusion decisions
		# BENEFIT: Saves 5+ API calls per run, faster processing
		# To re-enable: Uncomment this block and fix output format ("Yes" -> "Opportunity")
		logger.info("[OpportunityAgent] ⏭️  Skipped (disabled - title_density metric used instead)")
		
		# try:
		# 	from agents import Runner as _Runner
		# 	from app.local_agents.scoring.subagents.opportunity_agent import opportunity_agent
		# 	import json as _json
		# 	import time
		# 	
		# 	# BATCHING: Process in chunks to prevent token limits
		# 	BATCH_SIZE = 100  # Opportunity detection is lightweight
		# 	total_items = len(enriched_items)
		# 	num_batches = (total_items + BATCH_SIZE - 1) // BATCH_SIZE
		# 	
		# 	if total_items > BATCH_SIZE:
		# 		logger.info(f"[OpportunityAgent] 📦 Processing {total_items} items in {num_batches} batch(es) (size: {BATCH_SIZE})")
		# 	
		# 	all_updates = []
		# 	
		# 	for batch_idx in range(num_batches):
		# 		start_idx = batch_idx * BATCH_SIZE
		# 		end_idx = min(start_idx + BATCH_SIZE, total_items)
		# 		batch_items = enriched_items[start_idx:end_idx]
		# 		batch_label = f"Batch {batch_idx + 1}/{num_batches}"
		# 		
		# 		if total_items > BATCH_SIZE:
		# 			logger.info(f"[OpportunityAgent] 🔄 {batch_label}: Processing {len(batch_items)} items")
		# 		
		# 		try:
		# 			# Rate limiting between batches
		# 			if batch_idx > 0:
		# 				time.sleep(1)
		# 			
		# 			opp_prompt = _json.dumps({"items": batch_items}, separators=(",", ":"))
		# 			opp_res = _Runner.run_sync(opportunity_agent, opp_prompt)
		# 			opp_out = getattr(opp_res, "final_output", None)
		# 			
		# 			batch_updates = None
		# 			if isinstance(opp_out, str):
		# 				try:
		# 					parsed = _json.loads(opp_out.strip())
		# 					batch_updates = parsed.get("items", parsed if isinstance(parsed, list) else None)
		# 				except Exception:
		# 					batch_updates = None
		# 			elif hasattr(opp_out, "model_dump"):
		# 				try:
		# 					parsed = opp_out.model_dump()
		# 					batch_updates = parsed.get("items", parsed if isinstance(parsed, list) else None)
		# 				except Exception:
		# 					batch_updates = None
		# 			
		# 			if isinstance(batch_updates, list):
		# 				all_updates.extend(batch_updates)
		# 				if total_items > BATCH_SIZE:
		# 					logger.info(f"[OpportunityAgent] ✅ {batch_label} complete ({len(batch_updates)} items)")
		# 			else:
		# 				# No updates for this batch - items will use defaults
		# 				if total_items > BATCH_SIZE:
		# 					logger.warning(f"[OpportunityAgent] ⚠️  {batch_label} returned no updates")
		# 		
		# 		except Exception as e:
		# 			logger.error(f"[OpportunityAgent] ❌ {batch_label} failed: {e}")
		# 			# Continue with other batches
		# 	
		# 	# Apply updates by phrase match if available
		# 	if all_updates:
		# 		by_phrase = {str((u or {}).get("phrase", "")).strip().lower(): u for u in all_updates}
		# 		for it in enriched_items:
		# 			p = str(it.get("phrase", "")).strip().lower()
		# 			upd = by_phrase.get(p)
		# 			if isinstance(upd, dict):
		# 				for k in ("opportunity_decision", "opportunity_reason"):
		# 					if k in upd:
		# 						it[k] = upd[k]
		# 		logger.info(f"[OpportunityAgent] ✅ All batches complete: Annotations applied to {len(by_phrase)} items")
		# 	else:
		# 		logger.warning("[OpportunityAgent] No updates received from any batch")
		# except Exception as e:
		# 	logger.debug(f"[ScoringRunner] Opportunity subagent skipped: {e}")
		
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
				# Data preparation: create minimal product context from available data
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
			
			# Step 4: Apply score alignment to fix inconsistencies
			logger.info(f"[ScoringRunner] Applying relevancy-intent score alignment to {len(enriched_items)} keywords")
			aligned_items = ScoringRunner.align_relevancy_and_intent_scores(enriched_items)
			
			# Step 5: Sort and group by intent (using aligned scores)
			from app.services.keyword_processing.sort import sort_keywords_by_intent
			sorted_result = sort_keywords_by_intent(aligned_items, scraped_product)
			
			# Step 6: Calculate summary stats
			total_keywords = len(aligned_items)
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

	@staticmethod
	def align_relevancy_and_intent_scores(keyword_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		"""
		Align relevancy and intent scores to fix inconsistencies.
		
		Addresses cases where:
		- High relevancy (8-10) but intent 0 (market validates relevance)
		- High intent (2-3) but low relevancy (0-3) (semantic vs market mismatch)
		- Category overrides that should affect both scores
		
		Args:
			keyword_items: List of keyword dictionaries with relevancy_score, intent_score, category
			
		Returns:
			List of keyword dictionaries with aligned scores
		"""
		if not keyword_items:
			return keyword_items
			
		aligned_items = []
		alignment_count = 0
		
		for keyword in keyword_items:
			# Get current scores
			original_relevancy = keyword.get('relevancy_score', 0)
			original_intent = keyword.get('intent_score', 0)
			category = keyword.get('category', '')
			phrase = keyword.get('phrase', '')
			
			# Create working copy
			aligned_keyword = keyword.copy()
			
			# Rule 1: Category-based alignment
			# If category is Irrelevant/Branded/Spanish → Force both scores low
			if category in ['Irrelevant', 'Branded', 'Spanish']:
				if original_relevancy > 2 or original_intent > 0:
					aligned_keyword['relevancy_score'] = min(2, original_relevancy)  # Cap at 2/10
					aligned_keyword['intent_score'] = 0  # Force to 0
					aligned_keyword['_alignment_applied'] = f"Category {category}: relevancy {original_relevancy}→{aligned_keyword['relevancy_score']}, intent {original_intent}→0"
					alignment_count += 1
					
			# Rule 2: High relevancy but zero intent
			# If relevancy is very high (8-10) but intent is 0 → Boost intent
			elif original_relevancy >= 8 and original_intent == 0:
				aligned_keyword['intent_score'] = 1  # Boost to minimum viable intent
				aligned_keyword['_alignment_applied'] = f"High market performance: intent {original_intent}→1 (relevancy {original_relevancy})"
				alignment_count += 1
				
			# Rule 3: High intent but very low relevancy  
			# If intent is high (2-3) but relevancy is very low (0-2) → Boost relevancy
			elif original_intent >= 2 and original_relevancy <= 2:
				aligned_keyword['relevancy_score'] = 4  # Boost to moderate relevancy
				aligned_keyword['_alignment_applied'] = f"High semantic relevance: relevancy {original_relevancy}→4 (intent {original_intent})"
				alignment_count += 1
				
			# Rule 4: Moderate misalignment
			# If relevancy is high (6-7) but intent is 0 → Small intent boost
			elif original_relevancy >= 6 and original_intent == 0:
				aligned_keyword['intent_score'] = 1  # Small boost
				aligned_keyword['_alignment_applied'] = f"Moderate market performance: intent {original_intent}→1 (relevancy {original_relevancy})"
				alignment_count += 1
				
			aligned_items.append(aligned_keyword)
		
		if alignment_count > 0:
			logger.info(f"[ScoringRunner] Applied score alignment to {alignment_count}/{len(keyword_items)} keywords")
			
		return aligned_items



		# Step 3: Add broad volume calculation if requested

		if include_broad_volume:

			try:

				from app.local_agents.scoring.subagents.broad_volume_agent import calculate_broad_volume

				from app.services.keyword_processing.intent import extract_brand_tokens

				

				brand_tokens = extract_brand_tokens(scraped_product)

				broad_volume_result = calculate_broad_volume(

					enriched_items, 

					brand_tokens=brand_tokens, 

					use_llm=True  # Use AI analysis only - no deterministic fallback

				)

				enriched_items = broad_volume_result.get("items", enriched_items)

				# Note: filtered root volumes will be computed where they are consumed (API/SEO stage)

			except Exception as e:

				logger.warning(f"[ScoringRunner] Broad volume calculation failed in score_and_enrich: {e}")

		

		# Step 4: Opportunity detection (AI rules) after metrics and (optionally) root assignment

		try:

			from agents import Runner as _Runner

			from app.local_agents.scoring.subagents.opportunity_agent import opportunity_agent

			import json as _json

			opp_prompt = _json.dumps({"items": enriched_items}, separators=(",", ":"))

			opp_res = _Runner.run_sync(opportunity_agent, opp_prompt)

			opp_out = getattr(opp_res, "final_output", None)

			updates = None

			if isinstance(opp_out, str):

				try:

					parsed = _json.loads(opp_out.strip())

					updates = parsed.get("items", parsed if isinstance(parsed, list) else None)

				except Exception:

					updates = None

			elif hasattr(opp_out, "model_dump"):

				try:

					parsed = opp_out.model_dump()

					updates = parsed.get("items", parsed if isinstance(parsed, list) else None)

				except Exception:

					updates = None

			# Apply updates by phrase match if available

			if isinstance(updates, list):

				by_phrase = {str((u or {}).get("phrase", "")).strip().lower(): u for u in updates}

				for it in enriched_items:

					p = str(it.get("phrase", "")).strip().lower()

					upd = by_phrase.get(p)

					if isinstance(upd, dict):

						for k in ("opportunity_decision", "opportunity_reason"):

							if k in upd:

								it[k] = upd[k]

				logger.info("[ScoringRunner] Opportunity annotations applied to items")

		except Exception as e:

			logger.debug(f"[ScoringRunner] Opportunity subagent skipped: {e}")

		

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

				# Data preparation: create minimal product context from available data

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




