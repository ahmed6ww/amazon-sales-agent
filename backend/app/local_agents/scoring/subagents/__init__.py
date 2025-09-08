"""Subagents for the Scoring Agent.

Modules:
- intent_agent: computes buyer intent (0..3) per keyword.
- broad_volume_agent: computes broad search volume sums by root term.
- metrics_agent: attaches Helium 10 (or similar) metrics to items.
- opportunity_agent: flags opportunity/ignore based on title density rules.

All subagents expose minimal, stable method signatures and return
no-op results by default. Implementations can be filled in iteratively.
"""

__all__ = [
    "intent_scoring_agent",
    "broad_volume_agent",
    "metrics_agent",
    "opportunity_agent",
    "collect_metrics_from_csv",
    "merge_metrics_into_items",
]


from .intent_agent import intent_scoring_agent
from .broad_volume_agent import broad_volume_agent
from .metrics_agent import metrics_agent, collect_metrics_from_csv, merge_metrics_into_items
from .opportunity_agent import opportunity_agent
