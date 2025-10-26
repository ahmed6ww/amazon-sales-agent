from enum import Enum
from typing import Dict, List, Union

from pydantic import BaseModel, Field, ConfigDict, field_validator


class KeywordCategory(str, Enum):
	RELEVANT = "Relevant"
	DESIGN_SPECIFIC = "Design-Specific"
	IRRELEVANT = "Irrelevant"
	BRANDED = "Branded"
	SPANISH = "Spanish"
	OUTLIER = "Outlier"


class KeywordData(BaseModel):
	model_config = ConfigDict(extra="allow")  # Changed from "forbid" to "allow" to accept base_relevancy_score
	phrase: str = Field(..., description="The keyword phrase")
	category: KeywordCategory = Field(..., description="Full category name (e.g., 'Relevant', 'Design-Specific')")
	reason: str = Field(default="", description="Optional rationale (omit to save tokens)")
	relevancy_score: int = Field(
		None, ge=0, le=10, description="Relevancy score (0-10) from research CSVs"
	)
	# Accept both field names - AI might return either
	base_relevancy_score: int = Field(
		None, ge=0, le=10, description="Alternative field name for relevancy score"
	)

	@field_validator('relevancy_score', 'base_relevancy_score', mode='before')
	@classmethod
	def sanitize_score(cls, v: Union[int, str, None]) -> Union[int, None]:
		"""Sanitize malformed relevancy scores from AI (e.g., ': 10' → 10)"""
		if v is None:
			return None
		if isinstance(v, int):
			return v
		if isinstance(v, str):
			# Fix malformed scores like ": 10" or ":10"
			v = v.strip().lstrip(':').strip()
			try:
				return int(v)
			except (ValueError, AttributeError):
				return None
		return None


class CategoryStats(BaseModel):
	count: int = Field(..., description="Number of keywords in this category")
	examples: List[str] = Field(default_factory=list, description="Up to a few example phrases")


class KeywordAnalysisResult(BaseModel):
	model_config = ConfigDict(extra="forbid")
	product_context: Dict = Field(..., description="Slimmed details from scraped_product")
	items: List[KeywordData] = Field(..., description="Per-keyword categorization list")
	stats: Dict[KeywordCategory, CategoryStats] = Field(default_factory=dict, description="Summary stats by category")

