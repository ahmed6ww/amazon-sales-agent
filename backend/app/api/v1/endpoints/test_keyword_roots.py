"""
Test Keyword Root Extraction Endpoint

This endpoint allows testing the keyword root extraction functionality
to verify that the system properly groups keywords by meaningful roots
and reduces the total number of unique terms for analysis.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List, Dict, Any
import logging

from app.services.file_processing.csv_processor import parse_csv_bytes
from app.services.keyword_processing.root_extraction import (
    group_keywords_by_roots, 
    get_priority_roots_for_search
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/test-keyword-roots")
async def test_keyword_root_extraction(
    revenue_csv: Optional[UploadFile] = File(None),
    design_csv: Optional[UploadFile] = File(None),
):
    """
    Test the keyword root extraction system with uploaded CSV files.
    
    This endpoint demonstrates how the system:
    1. Extracts all keywords from CSV files
    2. Groups them by meaningful root words
    3. Reduces the total number of terms for analysis
    4. Prioritizes roots for Amazon search optimization
    """
    
    try:
        all_keywords = []
        csv_info = {}
        
        # Process revenue CSV if provided
        if revenue_csv and revenue_csv.filename:
            logger.info(f"Processing revenue CSV: {revenue_csv.filename}")
            revenue_data = await revenue_csv.read()
            revenue_result = parse_csv_bytes(revenue_csv.filename, revenue_data)
            
            if not revenue_result.get("success"):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to parse revenue CSV: {revenue_result.get('error')}"
                )
            
            revenue_rows = revenue_result["data"]
            revenue_keywords = []
            
            for row in revenue_rows:
                kw = row.get('Keyword Phrase', '')
                if kw and isinstance(kw, str):
                    keyword = kw.strip()
                    if keyword:
                        revenue_keywords.append(keyword)
                        all_keywords.append(keyword)
            
            csv_info['revenue'] = {
                'total_rows': len(revenue_rows),
                'keywords_extracted': len(revenue_keywords),
                'sample_keywords': revenue_keywords[:10]
            }
        
        # Process design CSV if provided
        if design_csv and design_csv.filename:
            logger.info(f"Processing design CSV: {design_csv.filename}")
            design_data = await design_csv.read()
            design_result = parse_csv_bytes(design_csv.filename, design_data)
            
            if not design_result.get("success"):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to parse design CSV: {design_result.get('error')}"
                )
            
            design_rows = design_result["data"]
            design_keywords = []
            
            for row in design_rows:
                kw = row.get('Keyword Phrase', '')
                if kw and isinstance(kw, str):
                    keyword = kw.strip()
                    if keyword:
                        design_keywords.append(keyword)
                        all_keywords.append(keyword)
            
            csv_info['design'] = {
                'total_rows': len(design_rows),
                'keywords_extracted': len(design_keywords),
                'sample_keywords': design_keywords[:10]
            }
        
        if not all_keywords:
            raise HTTPException(
                status_code=400, 
                detail="No keywords found in uploaded CSV files. Please ensure CSV files contain a 'Keyword Phrase' column."
            )
        
        # Remove duplicates while preserving order
        unique_keywords = list(dict.fromkeys(all_keywords))
        
        logger.info(f"Extracted {len(all_keywords)} total keywords, {len(unique_keywords)} unique")
        
        # Perform root-based analysis
        logger.info("Performing keyword root extraction analysis...")
        keyword_root_analysis = group_keywords_by_roots(unique_keywords)
        
        # Get priority roots for search optimization
        priority_roots = get_priority_roots_for_search(keyword_root_analysis, max_roots=25)
        
        # Calculate efficiency metrics
        original_keyword_count = len(unique_keywords)
        meaningful_roots_count = keyword_root_analysis['meaningful_roots']
        priority_roots_count = len(priority_roots)
        
        efficiency_improvement = {
            'original_keywords': original_keyword_count,
            'meaningful_roots': meaningful_roots_count,
            'priority_roots': priority_roots_count,
            'reduction_ratio': round((original_keyword_count - priority_roots_count) / original_keyword_count, 2) if original_keyword_count > 0 else 0,
            'efficiency_gain': f"{round((1 - priority_roots_count / original_keyword_count) * 100, 1)}%" if original_keyword_count > 0 else "0%"
        }
        
        # Prepare detailed root information for top roots
        detailed_roots = {}
        roots_data = keyword_root_analysis.get('roots', {})
        
        for root in priority_roots[:15]:  # Show details for top 15 roots
            if root in roots_data:
                root_info = roots_data[root]
                detailed_roots[root] = {
                    'category': root_info['category'],
                    'frequency': root_info['frequency'],
                    'variant_count': root_info['variant_count'],
                    'sample_variants': root_info['variants'][:5],  # Show first 5 variants
                    'all_variants': root_info['variants'] if len(root_info['variants']) <= 10 else None  # Full list if small
                }
        
        # Compile response
        response = {
            "success": True,
            "message": "Keyword root extraction analysis completed successfully",
            "csv_processing": csv_info,
            "analysis_summary": {
                "total_keywords_found": len(all_keywords),
                "unique_keywords": len(unique_keywords),
                "total_roots_identified": keyword_root_analysis['total_roots'],
                "meaningful_roots": keyword_root_analysis['meaningful_roots'],
                "priority_roots_selected": len(priority_roots)
            },
            "efficiency_metrics": efficiency_improvement,
            "keyword_categorization": keyword_root_analysis['summary'],
            "priority_roots": priority_roots,
            "detailed_root_analysis": detailed_roots,
            "recommendations": {
                "amazon_search_terms": priority_roots[:10],
                "optimization_potential": f"Reduced keyword analysis from {original_keyword_count} to {priority_roots_count} terms",
                "memory_efficiency": f"~{round((1 - priority_roots_count / original_keyword_count) * 100)}% reduction in contextual memory usage"
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in keyword root extraction test: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal error during keyword root extraction: {str(e)}"
        ) 