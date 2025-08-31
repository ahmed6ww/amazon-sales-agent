"""
Keyword Agent Tools

Tools for the keyword agent to interface with OpenAI Agents SDK.
"""

import json
from typing import Dict, List, Any

from .helper_methods import (
    categorize_keywords_from_csv,
    calculate_relevancy_score,
    extract_root_word,
    analyze_title_density,
    group_keywords_by_root
)
from .schemas import KeywordData


def tool_categorize_keywords(csv_data_json: str, product_attributes_json: str = "{}") -> str:
    """
    Tool to categorize keywords from Helium10 CSV data.
    
    Args:
        csv_data_json: JSON string containing list of CSV row dictionaries
        product_attributes_json: JSON string containing product attributes (optional)
    
    Returns:
        JSON string with categorization results
    """
    try:
        csv_data = json.loads(csv_data_json)
        product_attributes = json.loads(product_attributes_json)
        
        result = categorize_keywords_from_csv(csv_data, product_attributes)
        
        # Convert result to JSON-serializable format
        result_dict = {
            "total_keywords": result.total_keywords,
            "processed_keywords": result.processed_keywords,
            "filtered_keywords": result.filtered_keywords,
            "processing_time": result.processing_time,
            "data_quality_score": result.data_quality_score,
            "warnings": result.warnings,
            "top_opportunities": result.top_opportunities,
            "coverage_gaps": result.coverage_gaps,
            "recommended_focus_areas": result.recommended_focus_areas,
            "category_stats": {
                category.value: {
                    "keyword_count": stats.keyword_count,
                    "total_search_volume": stats.total_search_volume,
                    "avg_relevancy_score": stats.avg_relevancy_score,
                    "avg_intent_score": stats.avg_intent_score,
                    "top_keywords": stats.top_keywords
                }
                for category, stats in result.category_stats.items()
            },
            "keywords_by_category": {
                category.value: [
                    {
                        "keyword_phrase": kw.keyword_phrase,
                        "category": kw.category,
                        "final_category": kw.final_category.value if kw.final_category else None,
                        "search_volume": kw.search_volume,
                        "relevancy_score": kw.relevancy_score,
                        "title_density": kw.title_density,
                        "cpr": kw.cpr,
                        "root_word": kw.root_word,
                        "broad_search_volume": kw.broad_search_volume,
                        "is_zero_title_density": kw.is_zero_title_density,
                        "is_derivative": kw.is_derivative
                    }
                    for kw in keywords
                ]
                for category, keywords in result.keywords_by_category.items()
            },
            "root_word_analysis": [
                {
                    "root_word": rwa.root_word,
                    "related_keywords": rwa.related_keywords,
                    "total_search_volume": rwa.total_search_volume,
                    "avg_relevancy_score": rwa.avg_relevancy_score,
                    "keyword_count": rwa.keyword_count,
                    "best_keyword": rwa.best_keyword,
                    "categories_present": [cat.value for cat in rwa.categories_present]
                }
                for rwa in result.root_word_analysis
            ]
        }
        
        return json.dumps(result_dict, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to categorize keywords: {str(e)}"})


def tool_calculate_relevancy_scores(keywords_json: str, competitor_asins_json: str) -> str:
    """
    Tool to calculate relevancy scores for keywords using MVP formula.
    
    Args:
        keywords_json: JSON string containing keyword data
        competitor_asins_json: JSON string containing list of competitor ASINs
    
    Returns:
        JSON string with relevancy calculations
    """
    try:
        keywords_data = json.loads(keywords_json)
        competitor_asins = json.loads(competitor_asins_json)
        
        results = []
        
        for kw_data in keywords_data:
            # Create KeywordData object
            keyword = KeywordData(**kw_data)
            
            # Calculate relevancy score
            relevancy_score = calculate_relevancy_score(keyword, competitor_asins)
            
            # Count competitors in top 10
            top_10_count = 0
            total_competitors = 0
            
            for asin, ranking in keyword.competitor_rankings.items():
                if asin in competitor_asins and ranking > 0:
                    total_competitors += 1
                    if ranking <= 10:
                        top_10_count += 1
            
            results.append({
                "keyword": keyword.keyword_phrase,
                "relevancy_score": relevancy_score,
                "total_competitors": total_competitors,
                "competitors_in_top_10": top_10_count,
                "interpretation": _get_relevancy_interpretation(relevancy_score)
            })
        
        return json.dumps({
            "relevancy_calculations": results,
            "summary": {
                "total_keywords": len(results),
                "high_relevancy_count": len([r for r in results if r["relevancy_score"] > 60]),
                "medium_relevancy_count": len([r for r in results if 30 <= r["relevancy_score"] <= 60]),
                "low_relevancy_count": len([r for r in results if r["relevancy_score"] < 30])
            }
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to calculate relevancy scores: {str(e)}"})


def tool_extract_root_words(keywords_json: str) -> str:
    """
    Tool to extract root words and group keywords for broad search volume analysis.
    
    Args:
        keywords_json: JSON string containing keyword phrases and data
    
    Returns:
        JSON string with root word analysis
    """
    try:
        keywords_data = json.loads(keywords_json)
        
        # Extract root words and group
        root_groups = {}
        
        for kw_data in keywords_data:
            keyword_phrase = kw_data.get("keyword_phrase", "")
            search_volume = kw_data.get("search_volume", 0)
            
            root_word = extract_root_word(keyword_phrase)
            
            if root_word not in root_groups:
                root_groups[root_word] = {
                    "root_word": root_word,
                    "keywords": [],
                    "total_search_volume": 0,
                    "keyword_count": 0
                }
            
            root_groups[root_word]["keywords"].append(keyword_phrase)
            root_groups[root_word]["total_search_volume"] += search_volume
            root_groups[root_word]["keyword_count"] += 1
        
        # Sort by total search volume
        sorted_roots = sorted(root_groups.values(), key=lambda x: x["total_search_volume"], reverse=True)
        
        return json.dumps({
            "root_word_groups": sorted_roots,
            "summary": {
                "total_root_words": len(root_groups),
                "total_keywords_processed": len(keywords_data),
                "top_root_word": sorted_roots[0]["root_word"] if sorted_roots else None,
                "highest_volume": sorted_roots[0]["total_search_volume"] if sorted_roots else 0
            }
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to extract root words: {str(e)}"})


def tool_analyze_title_density(keywords_json: str) -> str:
    """
    Tool to analyze title density patterns according to MVP rules.
    
    Args:
        keywords_json: JSON string containing keyword data with title density
    
    Returns:
        JSON string with title density analysis
    """
    try:
        keywords_data = json.loads(keywords_json)
        
        # Convert to KeywordData objects
        keywords = []
        for kw_data in keywords_data:
            keyword = KeywordData(**kw_data)
            keywords.append(keyword)
        
        # Perform title density analysis
        analysis = analyze_title_density(keywords)
        
        # Additional analysis for MVP requirements
        zero_density_keywords = [kw for kw in keywords if kw.title_density == 0]
        
        zero_density_details = []
        for kw in zero_density_keywords:
            root_word = extract_root_word(kw.keyword_phrase)
            
            zero_density_details.append({
                "keyword": kw.keyword_phrase,
                "search_volume": kw.search_volume,
                "category": kw.category,
                "root_word": root_word,
                "recommendation": _get_zero_density_recommendation(kw, root_word),
                "reasoning": _get_zero_density_reasoning(kw, root_word)
            })
        
        result = {
            "title_density_analysis": analysis,
            "zero_density_details": zero_density_details,
            "filtering_recommendations": {
                "keep_count": len([d for d in zero_density_details if d["recommendation"] == "keep"]),
                "filter_count": len([d for d in zero_density_details if d["recommendation"] == "filter"]),
                "opportunity_count": len([d for d in zero_density_details if "opportunity" in d["recommendation"]])
            }
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to analyze title density: {str(e)}"})


# Helper functions

def _get_relevancy_interpretation(relevancy_score: float) -> str:
    """Get interpretation of relevancy score"""
    if relevancy_score > 60:
        return "High relevancy - Many competitors rank well, keyword generates sales"
    elif relevancy_score >= 30:
        return "Medium relevancy - Some competition, potential opportunity"
    else:
        return "Low relevancy - Few competitors, either low demand or opportunity"


def _get_zero_density_recommendation(keyword: KeywordData, root_word: str) -> str:
    """Get recommendation for zero title density keyword"""
    # Check if irrelevant
    if keyword.final_category and keyword.final_category.value == "irrelevant":
        return "filter"
    
    # Check if derivative
    main_keywords = ['changing', 'pad', 'mat']
    if root_word in main_keywords and keyword.search_volume < 1000:
        return "filter"
    
    # Check for opportunity
    if keyword.search_volume > 1000 and root_word not in main_keywords:
        return "keep - opportunity"
    
    return "filter"


def _get_zero_density_reasoning(keyword: KeywordData, root_word: str) -> str:
    """Get reasoning for zero title density recommendation"""
    if keyword.final_category and keyword.final_category.value == "irrelevant":
        return "Irrelevant keyword - no one uses it in titles because it's not related to the product"
    
    main_keywords = ['changing', 'pad', 'mat']
    if root_word in main_keywords and keyword.search_volume < 1000:
        return "Derivative of main keyword with low search volume"
    
    if keyword.search_volume > 1000 and root_word not in main_keywords:
        return "Has own root word with decent search volume - potential opportunity"
    
    return "Low search volume and not clearly relevant" 