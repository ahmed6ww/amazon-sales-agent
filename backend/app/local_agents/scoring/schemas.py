from typing import Any, Dict, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

class IntentScore(BaseModel):
	model_config = ConfigDict(extra="forbid")
	phrase: str
	category: str
	base_relevancy_score: int = Field(0, ge=0, le=10)
	intent_score: int = Field(0, ge=0, le=3)


class KeywordScore(BaseModel):
	model_config = ConfigDict(extra="forbid")
	keyword: str
	score: float = Field(0.0, ge=0.0, le=10.0)
	priority: str = Field("medium", description="Priority level: low, medium, high")


class CompetitionMetrics(BaseModel):
	model_config = ConfigDict(extra="forbid")
	competition_level: str = Field("low", description="Competition level: low, medium, high")
	estimated_sales: int = Field(0, ge=0)
	estimated_revenue: float = Field(0.0, ge=0.0)


class PriorityLevel(Enum):
	LOW = "low"
	MEDIUM = "medium"
	HIGH = "high"


class IntentView(BaseModel):
	model_config = ConfigDict(extra="forbid")
	flat_sorted: List[Dict[str, Any]]
	by_intent: Dict[str, List[Dict[str, Any]]]
	counts: Dict[str, int]

class ScoringResult(BaseModel):
	model_config = ConfigDict(extra="forbid")
	product_context: Dict[str, Any] = Field(default_factory=dict)
	intent_view: IntentView
