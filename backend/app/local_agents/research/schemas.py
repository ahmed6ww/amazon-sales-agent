from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class ScrapeResult(BaseModel):
    success: bool
    data: Dict[str, Any]
    url: str
    error: Optional[str] = None


class CSVParseResult(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    count: Optional[int] = None
    error: Optional[str] = None


class ProductAttributes(BaseModel):
    # MVP Required Sources Only
    title: str
    images: Dict[str, Any]
    aplus_content: Dict[str, Any]
    reviews: Dict[str, Any]
    qa_section: Dict[str, Any]


class MarketPosition(BaseModel):
    price_tier: str
    final_tier: str
    price: float
    premium_score: int
    budget_score: int
    positioning_factors: Dict[str, str]
