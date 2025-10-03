import sys
import os
import pytest
from typing import List, Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_csv_products():
    """Sample CSV products for testing keyword categorization"""
    return [
        {
            "asin": "B08KT2Z93D",
            "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added",
            "brand": "BREWER",
            "category": "Food & Grocery"
        },
        {
            "asin": "B08KT2Z94E", 
            "title": "Organic Freeze Dried Strawberry Slices - No Sugar Added, Gluten Free Fruit Snack",
            "brand": "Organic Brand",
            "category": "Food & Grocery"
        },
        {
            "asin": "B08KT2Z95F",
            "title": "Premium Strawberry Slices - Freeze Dried Fruit Snack for Baking and Smoothies",
            "brand": "Premium Brand",
            "category": "Food & Grocery"
        },
        {
            "asin": "B08KT2Z96G",
            "title": "Freeze Dried Strawberry Chunks - Bulk Pack for Trail Mix and Snacking",
            "brand": "Bulk Brand",
            "category": "Food & Grocery"
        },
        {
            "asin": "B08KT2Z97H",
            "title": "Strawberry Fruit Crisps - Healthy Snack Alternative to Chips",
            "brand": "Healthy Brand",
            "category": "Food & Grocery"
        }
    ]


@pytest.fixture
def sample_revenue_csv():
    """Sample revenue CSV file path for testing"""
    return "backend/US_AMAZON_cerebro_B00O64QJOC_2025-08-21.csv"


@pytest.fixture
def sample_design_csv():
    """Sample design CSV file path for testing"""
    return "backend/design_products.csv"


@pytest.fixture
def sample_asins():
    """Sample ASINs for testing"""
    return [
        "B08KT2Z93D",
        "B08KT2Z94E", 
        "B08KT2Z95F",
        "B08KT2Z96G",
        "B08KT2Z97H"
    ]


@pytest.fixture
def sample_scraped_data():
    """Sample scraped product data for testing"""
    return {
        "B08KT2Z93D": {
            "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added",
            "brand": "BREWER",
            "bullets": [
                "🍓 PURE STRAWBERRY GOODNESS: Made from 100% real strawberries with no artificial flavors, colors, or preservatives",
                "🌱 ORGANIC & HEALTHY: Certified organic freeze dried strawberries with no sugar added, perfect for health-conscious consumers",
                "📦 BULK PACK VALUE: Pack of 4 individual 1.2 oz bags for maximum freshness and convenience",
                "🚀 VERSATILE USAGE: Perfect for baking, smoothies, cereals, yogurt, and on-the-go snacking",
                "✈️ TRAVEL READY: Lightweight and shelf-stable, ideal for hiking, camping, and travel adventures"
            ],
            "backend_keywords": ["freeze dried strawberries", "organic", "no sugar added", "bulk", "snack"]
        },
        "B08KT2Z94E": {
            "title": "Organic Freeze Dried Strawberry Slices - No Sugar Added, Gluten Free Fruit Snack",
            "brand": "Organic Brand",
            "bullets": [
                "Organic freeze dried strawberry slices with no added sugar",
                "Gluten free and perfect for healthy snacking",
                "Great for baking, smoothies, and trail mix"
            ],
            "backend_keywords": ["organic", "freeze dried", "strawberry", "slices"]
        }
    }


@pytest.fixture
def sample_search_results():
    """Sample Amazon search results for testing"""
    return [
        {
            "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added",
            "asin": "B08KT2Z93D",
            "price": "$12.99",
            "rating": "4.5",
            "reviews": "1,234"
        },
        {
            "title": "Organic Freeze Dried Strawberry Slices - No Sugar Added, Gluten Free Fruit Snack",
            "asin": "B08KT2Z94E",
            "price": "$9.99",
            "rating": "4.3",
            "reviews": "856"
        },
        {
            "title": "Premium Strawberry Slices - Freeze Dried Fruit Snack for Baking and Smoothies",
            "asin": "B08KT2Z95F",
            "price": "$11.50",
            "rating": "4.2",
            "reviews": "642"
        },
        {
            "title": "Freeze Dried Strawberry Chunks - Bulk Pack for Trail Mix and Snacking",
            "asin": "B08KT2Z96G",
            "price": "$15.99",
            "rating": "4.4",
            "reviews": "423"
        },
        {
            "title": "Strawberry Fruit Crisps - Healthy Snack Alternative to Chips",
            "asin": "B08KT2Z97H",
            "price": "$8.99",
            "rating": "4.1",
            "reviews": "789"
        }
    ]


@pytest.fixture
def sample_keywords_with_roots():
    """Sample keywords with root analysis for testing"""
    return {
        "freeze dried strawberry": {
            "roots": ["freeze", "dried", "strawberry"],
            "root_categories": {
                "freeze": "Relevant",
                "dried": "Relevant", 
                "strawberry": "Relevant"
            }
        },
        "freeze dried strawberry slices": {
            "roots": ["freeze", "dried", "strawberry", "slices"],
            "root_categories": {
                "freeze": "Relevant",
                "dried": "Relevant",
                "strawberry": "Relevant",
                "slices": "Design-Specific"
            }
        },
        "organic freeze dried": {
            "roots": ["organic", "freeze", "dried"],
            "root_categories": {
                "organic": "Relevant",
                "freeze": "Relevant",
                "dried": "Relevant"
            }
        },
        "strawberry banana mix": {
            "roots": ["strawberry", "banana", "mix"],
            "root_categories": {
                "strawberry": "Relevant",
                "banana": "Irrelevant",
                "mix": "Relevant"
            }
        }
    }
