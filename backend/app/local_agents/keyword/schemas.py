from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class KeywordCategory(str, Enum):
	RELEVANT = "Relevant"
	DESIGN_SPECIFIC = "Design-Specific"
	IRRELEVANT = "Irrelevant"
	BRANDED = "Branded"
	SPANISH = "Spanish"
	OUTLIER = "Outlier"


class KeywordData(BaseModel):
	model_config = ConfigDict(extra="forbid")
	phrase: str = Field(..., description="The keyword phrase")
	category: KeywordCategory = Field(..., description="Full category name (e.g., 'Relevant', 'Design-Specific')")
	reason: Optional[str] = Field(None, description="Short rationale for the category")
	base_relevancy_score: Optional[int] = Field(
		None, ge=0, le=10, description="Optional base relevancy score (0-10) from research CSVs"
	)


class CategoryStats(BaseModel):
	model_config = ConfigDict(extra="forbid")
	count: int = Field(..., description="Number of keywords in this category")


class KeywordAnalysisResult(BaseModel):
	model_config = ConfigDict(extra="forbid")
	product_context: Dict = Field(default_factory=dict, description="Slimmed details from scraped_product")
	items: List[KeywordData] = Field(default_factory=list, description="Per-keyword categorization list")
	stats: Dict[KeywordCategory, CategoryStats] = Field(default_factory=dict, description="Counts and examples by category")

