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
        
        # Use AI agent processing directly
        logger.info("Using AI keyword agent processing for testing")
        return self._try_agent_keyword_analysis(csv_data, product_attributes, "direct_processing_disabled_for_testing")
    
    def _try_agent_keyword_analysis(
        self, 
        csv_data: List[Dict[str, Any]], 
        product_attributes: Optional[Dict[str, Any]],
        direct_error: str
    ) -> Dict[str, Any]:
        """
        Fallback to agent approach if direct processing fails.
        """
        # Construct the analysis prompt
        prompt = f"""
        Please conduct a comprehensive keyword analysis on this Helium10 data:
        
        Data contains {len(csv_data)} keywords from competitor analysis.
        Product attributes: {product_attributes or "Not provided"}
        
        Tasks to complete:
        1. Categorize all keywords using tool_categorize_keywords
        2. Calculate relevancy scores using tool_calculate_relevancy_scores
        3. Extract root words and group keywords using tool_extract_root_words
        4. Analyze title density patterns using tool_analyze_title_density
        
        Please provide structured analysis that includes:
        - Complete keyword categorization (Relevant, Design-Specific, Irrelevant, Branded)
        - Relevancy scores using MVP formula (competitors in top 10)
        - Root word analysis with broad search volume calculations
        - Title density analysis with filtering recommendations
        - Top opportunities and coverage gaps
        - Data quality assessment and warnings
        
        Follow MVP requirements exactly for categorization and scoring.
        """
        
        try:
            # Prepare data for the agent
            csv_data_json = json.dumps(csv_data)
            product_attributes_json = json.dumps(product_attributes or {})
            
            # Run the agent with the data
            result = Runner.run_sync(
                keyword_agent, 
                prompt
            )
            
            return {
                "success": True,
                "final_output": result.final_output,
                "processing_details": {
                    "total_keywords": len(csv_data),
                    "agent_used": "KeywordAgent",
                    "analysis_type": "full_keyword_analysis"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_output": None
            }
    
    def run_categorization_only(self, csv_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run only keyword categorization without full analysis.
        Useful for quick categorization tasks.
        """
        
        prompt = f"""
        Categorize these {len(csv_data)} keywords from Helium10 data according to MVP rules:
        
        Use tool_categorize_keywords to process the data and provide:
        1. Keywords categorized into: Relevant, Design-Specific, Irrelevant, Branded
        2. Category statistics and distribution
        3. Basic quality assessment
        4. Filtering recommendations
        
        Focus on accurate categorization following MVP requirements exactly.
        """
        
        try:
            csv_data_json = json.dumps(csv_data)
            
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
            # Extract competitor ASINs from the data
            competitor_asins = set()
            for row in csv_data:
                asin_columns = [col for col in row.keys() if col.startswith('B0') and len(col) == 10]
                competitor_asins.update(asin_columns)
            
            keywords_json = json.dumps(csv_data)
            competitor_asins_json = json.dumps(list(competitor_asins))
            
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
            keywords_json = json.dumps(csv_data)
            
            result = Runner.run_sync(
                keyword_agent, 
                prompt,
                context_variables={"keywords_data": keywords_json}
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
            keywords_json = json.dumps(csv_data)
            
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