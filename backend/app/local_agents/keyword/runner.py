"""
Keyword Agent Runner

Runner class for the Keyword Agent that handles session management 
and provides a clean interface for running keyword analysis tasks.
"""

from agents import Runner
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

from .agent import keyword_agent
from .helper_methods import categorize_keywords_from_csv
from .schemas import (
    KeywordAnalysisResult,
    KeywordCategory,
    KeywordData,
    RootWordAnalysis,
    CategoryStats,
)


class KeywordRunner:
    """
    Runner class for the Keyword Agent that handles keyword categorization,
    relevancy scoring, and root word analysis.
    """
    
    def __init__(self):
        pass
    
    def run_full_keyword_analysis(
        self, 
        csv_data: List[Dict[str, Any]], 
        product_attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute complete keyword analysis including categorization, relevancy scoring,
        and root word analysis.
        
        Args:
            csv_data: Parsed Helium10 CSV data as list of dictionaries
            product_attributes: Optional product attributes for better categorization
            
        Returns:
            Complete keyword analysis results
        """
        
        # First try direct processing to avoid asyncio conflicts
        # Comment out direct processing to test AI processing
        # try:
        #     logger.info("Attempting direct keyword processing to avoid asyncio conflicts")
        #     return self.run_direct_processing(csv_data)
        # except Exception as direct_error:
        #     logger.warning(f"Direct processing failed: {direct_error}, trying agent approach")
        #     return self._try_agent_keyword_analysis(csv_data, product_attributes, str(direct_error))
        
        # Use AI agent processing directly (limit input size for context efficiency)
        logger.info("Using AI keyword agent processing for testing")
        selected_keywords = self._select_keywords_for_ai(csv_data, limit=20)
        if len(csv_data) != len(selected_keywords):
            logger.info(f"Limiting AI keyword analysis to {len(selected_keywords)} of {len(csv_data)} keywords to stay within context limits")
        return self._try_agent_keyword_analysis(selected_keywords, product_attributes, "direct_processing_disabled_for_testing")
    
    def _try_agent_keyword_analysis(
        self, 
        csv_data: List[Dict[str, Any]], 
        product_attributes: Optional[Dict[str, Any]],
        direct_error: str
    ) -> Dict[str, Any]:
        """
        Fallback to agent approach if direct processing fails.
        """
        try:
            # Minify and slim payload to avoid tool/input formatting errors
            slimmed_rows = self._slim_csv_rows_for_ai(csv_data)
            csv_data_json = json.dumps(slimmed_rows, separators=(",", ":"))
            product_attributes_json = json.dumps(product_attributes or {}, separators=(",", ":"))

            # Use a compact prompt that directly instructs tool usage
            prompt = (
                "Perform keyword analysis. "
                "Call tool_categorize_keywords with the EXACT arguments below and return ONLY the tool's JSON.\n"
                f"csv_data_json: {csv_data_json}\n"
                f"product_attributes_json: {product_attributes_json}"
            )

            # Run the agent with the data embedded in the prompt
            result = Runner.run_sync(
                keyword_agent,
                prompt
            )

            # Capture last AI output for surfacing later
            self.last_ai_output = getattr(result, "final_output", None)

            # Attempt to parse structured JSON or model from the agent/tool output
            parsed_model: Optional[KeywordAnalysisResult] = None
            raw_output = getattr(result, "final_output", None)

            # Case 1: The SDK already returned a KeywordAnalysisResult model
            if raw_output is not None and isinstance(raw_output, KeywordAnalysisResult):
                parsed_model = raw_output

            # Case 2: A dict-like payload
            if parsed_model is None and isinstance(raw_output, dict):
                try:
                    parsed_model = self._parse_keyword_agent_json_to_model(raw_output)
                except Exception:
                    parsed_model = None

            # Case 3: A Pydantic-like object with model_dump()/dict()
            if parsed_model is None and raw_output is not None:
                try:
                    if hasattr(raw_output, "model_dump"):
                        data_obj = raw_output.model_dump()
                    elif hasattr(raw_output, "dict"):
                        data_obj = raw_output.dict()
                    else:
                        data_obj = None
                    if isinstance(data_obj, dict):
                        parsed_model = self._parse_keyword_agent_json_to_model(data_obj)
                except Exception:
                    parsed_model = None

            # Case 4: A string that may contain JSON (with or without fences)
            if parsed_model is None and isinstance(raw_output, str):
                data = self._extract_json_from_text(raw_output)
                if data is not None:
                    try:
                        parsed_model = self._parse_keyword_agent_json_to_model(data)
                    except Exception:
                        parsed_model = None

            if not parsed_model:
                raise ValueError("AI output parsing failed or returned empty result")

            return {
                "success": True,
                "final_output": result.final_output,
                "result": parsed_model,
                "processing_details": {
                    "total_keywords": len(csv_data),
                    "agent_used": "KeywordAgent",
                    "analysis_type": "full_keyword_analysis",
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_output": None,
            }
    
    def run_categorization_only(self, csv_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run only keyword categorization without full analysis.
        Useful for quick categorization tasks.
        """
        
        selected_keywords = self._select_keywords_for_ai(csv_data, limit=20)
        prompt = (
            f"Categorize these {len(selected_keywords)} keywords (limited to 10). "
            "Call tool_categorize_keywords with the exact JSON args below and return ONLY the tool JSON.\n"
            f"csv_data_json: {json.dumps(self._slim_csv_rows_for_ai(selected_keywords), separators=(',', ':'))}\n"
            "product_attributes_json: {}"
        )
        
        try:
            csv_data_json = json.dumps(selected_keywords)
            
            result = Runner.run_sync(
                keyword_agent, 
                prompt
            )
            
            return {
                "success": True,
                "final_output": result.final_output,
                "processing_details": {
                    "total_keywords": len(csv_data),
                    "analysis_type": "categorization_only"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_output": None
            }
    
    def run_relevancy_analysis(self, csv_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run relevancy scoring analysis using MVP formula.
        """
        
        prompt = f"""
        Calculate relevancy scores for these {len(csv_data)} keywords using the MVP formula:
        
        Use tool_calculate_relevancy_scores to:
        1. Count competitors ranked in top 10 for each keyword
        2. Calculate relevancy percentage using =countif(range, filter) logic
        3. Provide business interpretation for each score
        4. Summarize high/medium/low relevancy distribution
        
        Focus on accurate implementation of the MVP relevancy formula.
        """
        
        try:
            # Extract competitor ASINs from the limited data
            selected_keywords = self._select_keywords_for_ai(csv_data, limit=20)
            competitor_asins = set()
            for row in selected_keywords:
                asin_columns = [col for col in row.keys() if col.startswith('B0') and len(col) == 10]
                competitor_asins.update(asin_columns)

            prompt = (
                f"Calculate relevancy scores for these {len(selected_keywords)} keywords using MVP formula. "
                "Call tool_calculate_relevancy_scores with the exact JSON args below and return ONLY tool JSON.\n"
                f"keywords_json: {json.dumps(self._slim_csv_rows_for_ai(selected_keywords), separators=(',', ':'))}\n"
                f"competitor_asins_json: {json.dumps(list(competitor_asins), separators=(',', ':'))}"
            )

            result = Runner.run_sync(
                keyword_agent,
                prompt
            )
            
            return {
                "success": True,
                "final_output": result.final_output,
                "processing_details": {
                    "total_keywords": len(csv_data),
                    "competitor_asins_found": len(competitor_asins),
                    "analysis_type": "relevancy_analysis"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_output": None
            }
    
    def run_root_word_analysis(self, csv_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run root word extraction and broad search volume analysis.
        """
        
        prompt = f"""
        Extract root words and analyze broad search volume for these {len(csv_data)} keywords:
        
        Use tool_extract_root_words to:
        1. Extract root words from each keyword phrase
        2. Group keywords by root word
        3. Calculate total search volume for each root group
        4. Identify top root word opportunities
        5. Find coverage gaps in root word categories
        
        Provide insights for broad search volume strategy.
        """
        
        try:
            selected_keywords = self._select_keywords_for_ai(csv_data, limit=20)
            keywords_json = json.dumps(selected_keywords, separators=(",", ":"))

            prompt = (
                f"Extract root words and analyze broad search volume for these {len(selected_keywords)} keywords (limited to 10). "
                "Call tool_extract_root_words with the exact JSON arg below and return ONLY tool JSON.\n"
                f"keywords_json: {keywords_json}"
            )

            result = Runner.run_sync(
                keyword_agent, 
                prompt
            )
            
            return {
                "success": True,
                "final_output": result.final_output,
                "processing_details": {
                    "total_keywords": len(csv_data),
                    "analysis_type": "root_word_analysis"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_output": None
            }
    
    def run_title_density_analysis(self, csv_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run title density analysis with MVP filtering rules.
        """
        
        prompt = f"""
        Analyze title density patterns for these {len(csv_data)} keywords according to MVP rules:
        
        Use tool_analyze_title_density to:
        1. Identify zero title density keywords
        2. Determine which are irrelevant vs opportunities
        3. Apply MVP filtering rules
        4. Recommend which keywords to keep vs filter
        5. Identify opportunity keywords with zero density but high volume
        
        Follow MVP zero title density rules exactly.
        """
        
        try:
            selected_keywords = self._select_keywords_for_ai(csv_data, limit=20)
            keywords_json = json.dumps(selected_keywords, separators=(",", ":"))

            prompt = (
                f"Analyze title density patterns for these {len(selected_keywords)} keywords (limited to 10). "
                "Call tool_analyze_title_density with the exact JSON arg below and return ONLY tool JSON.\n"
                f"keywords_json: {keywords_json}"
            )

            result = Runner.run_sync(
                keyword_agent, 
                prompt
            )
            
            return {
                "success": True,
                "final_output": result.final_output,
                "processing_details": {
                    "total_keywords": len(csv_data),
                    "analysis_type": "title_density_analysis"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_output": None
            }
    
    def run_direct_processing(self, csv_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run direct keyword processing without using the agent.
        Useful for programmatic processing or when agent is not needed.
        """
        
        try:
            # Use helper methods directly
            result = categorize_keywords_from_csv(csv_data)
            
            return {
                "success": True,
                "result": result,
                "processing_details": {
                    "total_keywords": len(csv_data),
                    "processing_method": "direct_helper_methods"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": None
            } 

    # --- Internal helpers ---
    def _parse_keyword_agent_json_to_model(self, data: Dict[str, Any]) -> Optional[KeywordAnalysisResult]:
        """Parse the Keyword Agent tool JSON into KeywordAnalysisResult model."""
        try:
            # Map keywords_by_category
            keywords_by_category: Dict[KeywordCategory, List[KeywordData]] = {}
            raw_kw_by_cat = data.get("keywords_by_category", {}) or {}
            for cat_str, kw_list in raw_kw_by_cat.items():
                try:
                    cat_enum = KeywordCategory(cat_str)
                except Exception:
                    # Fallback mapping from display value
                    cat_enum = KeywordCategory(cat_str.lower()) if isinstance(cat_str, str) else KeywordCategory.RELEVANT
                model_list: List[KeywordData] = []
                for kw in kw_list or []:
                    final_cat = kw.get("final_category")
                    try:
                        final_cat_enum = KeywordCategory(final_cat) if final_cat else None
                    except Exception:
                        final_cat_enum = None
                    model_list.append(
                        KeywordData(
                            keyword_phrase=kw.get("keyword_phrase", ""),
                            category=kw.get("category"),
                            final_category=final_cat_enum,
                            search_volume=int(kw.get("search_volume", 0) or 0),
                            relevancy=int(kw.get("relevancy_score", 0) or 0),
                            title_density=int(kw.get("title_density", 0) or 0),
                            cpr=int(kw.get("cpr", 0) or 0),
                            cerebro_iq_score=int(kw.get("cerebro_iq_score", 0) or 0),
                            broad_search_volume=int(kw.get("broad_search_volume", 0) or 0),
                            root_word=kw.get("root_word"),
                            is_zero_title_density=bool(kw.get("is_zero_title_density", False)),
                            is_derivative=bool(kw.get("is_derivative", False)),
                        )
                    )
                keywords_by_category[cat_enum] = model_list

            # Map category_stats
            category_stats: Dict[KeywordCategory, CategoryStats] = {}
            raw_stats = data.get("category_stats", {}) or {}
            for cat_str, stat in raw_stats.items():
                try:
                    cat_enum = KeywordCategory(cat_str)
                except Exception:
                    cat_enum = KeywordCategory(cat_str.lower()) if isinstance(cat_str, str) else KeywordCategory.RELEVANT
                category_stats[cat_enum] = CategoryStats(
                    category=cat_enum,
                    keyword_count=int(stat.get("keyword_count", 0) or 0),
                    total_search_volume=int(stat.get("total_search_volume", 0) or 0),
                    avg_relevancy_score=float(stat.get("avg_relevancy_score", 0.0) or 0.0),
                    avg_intent_score=float(stat.get("avg_intent_score", 0.0) or 0.0),
                    top_keywords=list(stat.get("top_keywords", []) or []),
                )

            # Map root word analysis
            root_word_analysis: List[RootWordAnalysis] = []
            for rwa in data.get("root_word_analysis", []) or []:
                cats = []
                for c in rwa.get("categories_present", []) or []:
                    try:
                        cats.append(KeywordCategory(c))
                    except Exception:
                        continue
                root_word_analysis.append(
                    RootWordAnalysis(
                        root_word=rwa.get("root_word", ""),
                        related_keywords=list(rwa.get("related_keywords", []) or []),
                        total_search_volume=int(rwa.get("total_search_volume", 0) or 0),
                        avg_relevancy_score=float(rwa.get("avg_relevancy_score", 0.0) or 0.0),
                        keyword_count=int(rwa.get("keyword_count", 0) or 0),
                        best_keyword=rwa.get("best_keyword", ""),
                        categories_present=cats,
                    )
                )

            return KeywordAnalysisResult(
                total_keywords=int(data.get("total_keywords", 0) or 0),
                processed_keywords=int(data.get("processed_keywords", 0) or 0),
                filtered_keywords=int(data.get("filtered_keywords", 0) or 0),
                keywords_by_category=keywords_by_category,
                category_stats=category_stats,
                root_word_analysis=root_word_analysis,
                zero_title_density_count=int(data.get("zero_title_density_count", 0) or 0),
                derivative_keywords_count=int(data.get("derivative_keywords_count", 0) or 0),
                unique_root_words_count=int(data.get("unique_root_words_count", 0) or 0),
                processing_time=float(data.get("processing_time", 0.0) or 0.0),
                data_quality_score=float(data.get("data_quality_score", 0.0) or 0.0),
                warnings=list(data.get("warnings", []) or []),
                top_opportunities=list(data.get("top_opportunities", []) or []),
                coverage_gaps=list(data.get("coverage_gaps", []) or []),
                recommended_focus_areas=list(data.get("recommended_focus_areas", []) or []),
            )
        except Exception:
            return None

    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Best-effort extraction of a JSON object from arbitrary text."""
        # 1) Direct parse
        try:
            return json.loads(text)
        except Exception:
            pass

        # 2) Code fence extraction
        if "```" in text:
            try:
                start = text.find("```json")
                if start == -1:
                    start = text.find("```")
                if start != -1:
                    start = text.find("\n", start)
                    end = text.find("```", start + 1)
                    if start != -1 and end != -1:
                        fenced = text[start + 1:end]
                        return json.loads(fenced)
            except Exception:
                pass

        # 3) Brace matching to extract the first top-level JSON object
        first_brace = text.find("{")
        if first_brace != -1:
            depth = 0
            for i in range(first_brace, len(text)):
                ch = text[i]
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = text[first_brace:i + 1]
                        try:
                            return json.loads(candidate)
                        except Exception:
                            break
        return None

    def _slim_csv_rows_for_ai(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Reduce each CSV row to essential fields to minimize tokens for AI calls."""
        whitelist = {
            'Keyword Phrase',
            'Category (R for relevant, D for design specific, I for irrelevant and B for branded, S for Spanish, O for Outlier)',
            'Search Volume',
            'Search Volume Trend',
            'Relevancy',
            'Title Density',
            'CPR',
            'Cerebro IQ Score',
            'H10 PPC Sugg. Bid',
            'H10 PPC Sugg. Min Bid',
            'H10 PPC Sugg. Max Bid',
            'Competing Products',
            'Sponsored ASINs',
        }
        slimmed: List[Dict[str, Any]] = []
        for row in rows:
            slim = {}
            for k, v in row.items():
                if k in whitelist:
                    slim[k] = v
            # Drop ASIN ranking columns (B0...)
            slimmed.append(slim)
        return slimmed

    def _select_keywords_for_ai(self, csv_data: List[Dict[str, Any]], limit: int = 100) -> List[Dict[str, Any]]:
        """Select up to 'limit' keywords for AI processing to avoid context overflow.
        Prefer higher search volume when available.
        """
        try:
            # Sort by Search Volume (desc) then Relevancy (desc) if present
            def to_int(value: Any) -> int:
                try:
                    return int(float(value))
                except Exception:
                    return 0

            sorted_keywords = sorted(
                csv_data,
                key=lambda row: (
                    to_int(row.get('Search Volume', 0)),
                    to_int(row.get('Relevancy', 0)),
                ),
                reverse=True,
            )
            return sorted_keywords[:limit]
        except Exception:
            # Fallback to first N if sorting fails
            return csv_data[:limit]