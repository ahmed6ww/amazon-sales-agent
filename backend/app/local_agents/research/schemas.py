from pydantic import BaseModel
from typing import Dict, Any, Optional


class ScrapeResult(BaseModel):
    success: bool
    data: Dict[str, Any]
    url: str
    error: Optional[str] = None


class ProductAttributes(BaseModel):
    # MVP Required Sources Only
    title: str
    images: Dict[str, Any]
    aplus_content: Dict[str, Any]
    reviews: Dict[str, Any]
    qa_section: Dict[str, Any]
