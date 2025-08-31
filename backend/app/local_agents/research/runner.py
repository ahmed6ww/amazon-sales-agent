from agents import Runner
from typing import Dict, Any, Optional
from .agent import research_agent

class ResearchRunner:
    """
    Runner class for the Research Agent that handles session management 
    and provides a clean interface for running research tasks.
    """
    
    def __init__(self):
        pass
    
    def run_research(
        self, 
        asin_or_url: str, 
        marketplace: str = "US",
        h10_revenue_csv: Optional[str] = None,
        h10_design_csv: Optional[str] = None,
        main_keyword: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete research analysis for an Amazon product.
        
        Args:
            asin_or_url: Amazon ASIN or full product URL
            marketplace: Target marketplace (US, UK, DE, etc.)
            h10_revenue_csv: Path to Helium10 revenue competitors CSV
            h10_design_csv: Path to Helium10 design competitors CSV  
            main_keyword: Optional main keyword for the product
            
        Returns:
            Comprehensive research results including listing data, competitor data,
            and product attributes analysis
        """
        
        # Construct the research prompt
        prompt = f"""
        Please conduct a comprehensive research analysis for this Amazon product:
        
        Product: {asin_or_url}
        Marketplace: {marketplace}
        Main Keyword: {main_keyword or "Not specified"}
        
        Tasks to complete:
        1. Scrape the Amazon listing to get complete product information
        2. Extract and categorize all product attributes (pricing, features, specifications)
        3. Determine market positioning (budget/premium classification)
        4. Parse Helium10 competitor data if provided:
           - Revenue competitors CSV: {h10_revenue_csv or "Not provided"}
           - Design competitors CSV: {h10_design_csv or "Not provided"}
        
        Please provide structured output that includes:
        - Complete listing data
        - Extracted product attributes
        - Market positioning analysis  
        - Competitor keyword data (if CSV files provided)
        - Any insights about content sources for attribute extraction
        """
        
        try:
            # Run the agent
            result = Runner.run_sync(research_agent, prompt)
            
            return {
                "success": True,
                "final_output": result.final_output
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_output": None
            }
    
    def run_listing_analysis_only(self, asin_or_url: str) -> Dict[str, Any]:
        """
        Run MVP product attribute extraction from Amazon listing.
        Extracts only the 5 required sources: title, images, A+ content, reviews, Q&A section.
        """
        
        prompt = f"""
        Extract the 5 MVP required sources from this Amazon product listing: {asin_or_url}
        
        Required sources to extract:
        1. TITLE - Product title text
        2. IMAGES - Product image URLs and count
        3. A+ CONTENT - Enhanced brand content sections
        4. REVIEWS - Customer review samples and highlights
        5. Q&A SECTION - Question and answer pairs
        
        Workflow:
        1. Scrape the listing with tool_scrape_amazon_listing
        2. Extract clean attributes with tool_extract_product_attributes
        3. Report extraction quality for each of the 5 sources
        
        Provide a summary of what was successfully extracted and the quality of each source.
        """
        
        try:
            result = Runner.run_sync(research_agent, prompt)
            
            return {
                "success": True,
                "final_output": result.final_output
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_output": None
            }
    
    def run_csv_analysis_only(self, csv_file_path: str, csv_type: str = "revenue") -> Dict[str, Any]:
        """
        Run just the CSV parsing without listing analysis.
        Useful for processing Helium10 data independently.
        """
        
        prompt = f"""
        Please parse this Helium10 CSV file: {csv_file_path}
        
        CSV Type: {csv_type} competitors
        
        Task:
        - Parse the CSV and extract all keyword data with metrics
        - Provide summary statistics about the data
        - Identify any data quality issues
        """
        
        try:
            result = Runner.run_sync(research_agent, prompt)
            
            return {
                "success": True,
                "final_output": result.final_output
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_output": None
            } 