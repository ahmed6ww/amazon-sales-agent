from enum import Enum
from typing import Dict, List

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
	reason: str = Field(..., description="Short rationale for the category")
	base_relevancy_score: int = Field(
		..., ge=0, le=10, description="Base relevancy score (0-10) from research CSVs"
	)


class CategoryStats(BaseModel):
	model_config = ConfigDict(extra="forbid")
	count: int = Field(..., description="Number of keywords in this category")


class KeywordAnalysisResult(BaseModel):
	model_config = ConfigDict(extra="forbid")
	product_context: Dict = Field(..., description="Slimmed details from scraped_product")
	items: List[KeywordData] = Field(..., description="Per-keyword categorization list")
	stats: Dict[KeywordCategory, CategoryStats] = Field(..., description="Counts and examples by category")

