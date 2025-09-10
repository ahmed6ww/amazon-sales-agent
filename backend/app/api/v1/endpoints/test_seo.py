"""
Test SEO Optimization Endpoint

Test endpoint for SEO analysis and optimization functionality.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from app.local_agents.seo import SEORunner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class SEOTestRequest(BaseModel):
    """Request model for SEO testing."""
    scraped_product: Dict[str, Any]
    keyword_items: List[Dict[str, Any]]
    broad_search_volume_by_root: Optional[Dict[str, int]] = None


@router.post("/test-seo")
async def test_seo_optimization(request: SEOTestRequest):
    """
    Test the SEO optimization agent with provided data.
    
    This endpoint allows testing the SEO agent independently with custom data.
    """
    
    try:
        logger.info("🧪 Testing SEO optimization agent")
        
        # Initialize SEO runner
        seo_runner = SEORunner()
        
        # Run SEO analysis
        result = seo_runner.run_seo_analysis(
            scraped_product=request.scraped_product,
            keyword_items=request.keyword_items,
            broad_search_volume_by_root=request.broad_search_volume_by_root
        )
        
        logger.info(f"✅ SEO test completed: {result.get('success', False)}")
        
        return {
            "success": True,
            "test_result": result,
            "input_summary": {
                "keywords_count": len(request.keyword_items),
                "has_scraped_data": bool(request.scraped_product),
                "has_root_volumes": bool(request.broad_search_volume_by_root)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ SEO test failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"SEO test failed: {str(e)}"
        )


@router.post("/test-seo-with-sample-data")
async def test_seo_with_sample_data():
    """
    Test SEO optimization with sample data for demo purposes.
    """
    
    # Sample scraped product data
    sample_scraped_product = {
        "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added, Dry Strawberry Gluten Free Fruit Snack for Baking, Smoothies, Cereals & Travel",
        "elements": {
            "feature-bullets": {
                "present": True,
                "bullets": [
                    "Delicious Flavor in Every Bite: Savor the naturally sweet, tangy crunch of freeze dried strawberry slices bursting with real fruit flavor.",
                    "Ideal Travel Companion: Lightweight, mess-free, and shelf-stable, our freeze dried strawberries bulk are perfect for hiking or camping.",
                    "From Farm to Your Table: Our organic dried strawberries, delivered sun-ripened, farm-fresh, are made from real strawberries.",
                    "Shelf Life: Our freeze-dried strawberries are at peak flavor for up to 24 months.",
                    "Bulk Packed for Convenience: Buy in bulk and enjoy premium quality freeze dried strawberries whenever you need them."
                ]
            },
            "productOverview_feature_div": {
                "present": True,
                "kv": {
                    "Brand": "Brewer Outdoor Solutions",
                    "Item Weight": "4.8 Ounces",
                    "Size": "4 Pack"
                }
            }
        }
    }
    
    # Sample keyword items
    sample_keyword_items = [
        {
            "phrase": "freeze dried strawberries",
            "category": "Relevant",
            "intent_score": 3,
            "search_volume": 470,
            "title_density": 4,
            "cpr": 8,
            "root": "strawberrie",
            "relevancy_score": 4
        },
        {
            "phrase": "freeze dried strawberries bulk",
            "category": "Design-Specific",
            "intent_score": 3,
            "search_volume": 909,
            "title_density": 0,
            "cpr": 12,
            "root": "strawberrie",
            "relevancy_score": 3
        },
        {
            "phrase": "organic freeze dried strawberries",
            "category": "Design-Specific",
            "intent_score": 3,
            "search_volume": 242,
            "title_density": 0,
            "cpr": 8,
            "root": "strawberrie",
            "relevancy_score": 3
        },
        {
            "phrase": "dried strawberries",
            "category": "Relevant",
            "intent_score": 2,
            "search_volume": 8603,
            "title_density": 21,
            "cpr": 41,
            "root": "strawberrie",
            "relevancy_score": 5
        },
        {
            "phrase": "strawberry chips",
            "category": "Design-Specific",
            "intent_score": 2,
            "search_volume": 371,
            "title_density": 1,
            "cpr": 8,
            "root": "strawberry",
            "relevancy_score": 4
        }
    ]
    
    # Sample root volumes
    sample_root_volumes = {
        "strawberrie": 12000,
        "strawberry": 8500,
        "freeze": 3500
    }
    
    try:
        logger.info("🧪 Testing SEO optimization with sample data")
        
        # Initialize SEO runner
        seo_runner = SEORunner()
        
        # Run SEO analysis
        result = seo_runner.run_seo_analysis(
            scraped_product=sample_scraped_product,
            keyword_items=sample_keyword_items,
            broad_search_volume_by_root=sample_root_volumes
        )
        
        logger.info(f"✅ SEO sample test completed: {result.get('success', False)}")
        
        return {
            "success": True,
            "test_result": result,
            "sample_data_summary": {
                "keywords_tested": len(sample_keyword_items),
                "product_title": sample_scraped_product["title"][:100] + "...",
                "bullets_count": len(sample_scraped_product["elements"]["feature-bullets"]["bullets"]),
                "root_volumes_count": len(sample_root_volumes)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ SEO sample test failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"SEO sample test failed: {str(e)}"
        ) 