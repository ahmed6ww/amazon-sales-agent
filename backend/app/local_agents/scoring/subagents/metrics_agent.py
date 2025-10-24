from typing import Any, Dict, List, Optional, Tuple

from agents import Agent

# Minimal placeholder Agent so this module exports `metrics_agent` for package imports.
# Actual metrics logic is deterministic via the helper functions below.
METRICS_AGENT_INSTRUCTIONS = (
    "Attach Helium10-like metrics to keyword items deterministically. "
    "Use collect_metrics_from_csv() and merge_metrics_into_items() functions."
)

metrics_agent = Agent(
    name="MetricsSubagent",
    instructions=METRICS_AGENT_INSTRUCTIONS,
    model="gpt-5-nano-2025-08-07",
    output_type=None,
)


def collect_metrics_from_csv(
    base_relevancy_scores: Dict[str, int],
    revenue_csv: Optional[List[Dict[str, Any]]] = None,
    design_csv: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Deterministic metrics extraction for keywords present in base_relevancy_scores using uploaded CSV rows.

    Inputs:
      - base_relevancy_scores: { keyword -> score (0..10) }
      - revenue_csv: list of dict rows from the revenue CSV (optional)
      - design_csv: list of dict rows from the design CSV (optional)

        For each keyword, match by the "Keyword Phrase" column (case-insensitive, trimmed) in the provided CSV(s)
        and extract the following columns when present:
      - Title Density -> title_density (int)
      - Search Volume -> search_volume (int)
      - CPR -> cpr (int)
            - Competition data -> competition (dict) with these fields if available:
                        Competing Products, Ranking Competitors (count), Competitor Rank (avg), Competitor Performance Score

        Returns:
            { keyword: {
                    "title_density"?: int,
                    "search_volume"?: int,
                    "cpr"?: int,
                    "competition"?: {
                            "competing_products"?: int,
                            "ranking_competitors"?: int,
                            "competitor_rank_avg"?: float,
                            "competitor_performance_score"?: float
                    }
                }
            }
        Notes:
            - Missing metrics are omitted (keys not present) to avoid overwriting existing values during merges.
    """

    def _norm(s: Any) -> str:
        return str(s or "").strip().lower()

    def _to_int(v: Any) -> Optional[int]:
        try:
            if v is None or v == "":
                return None
            # Some CSVs have floats in strings like "1234.0"
            return int(float(str(v).replace(",", "").strip()))
        except Exception:
            return None

    def _to_float(v: Any) -> Optional[float]:
        try:
            if v is None or v == "":
                return None
            return float(str(v).replace(",", "").strip())
        except Exception:
            return None

    def _index_rows(rows: Optional[List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        idx: Dict[str, Dict[str, Any]] = {}
        if not rows:
            return idx
        for row in rows:
            key = _norm(row.get("Keyword Phrase"))
            if key and key not in idx:
                idx[key] = row
        return idx

    rev_idx = _index_rows(revenue_csv)
    des_idx = _index_rows(design_csv)

    def _pick_row(kw: str) -> Optional[Dict[str, Any]]:
        k = _norm(kw)
        r = rev_idx.get(k)
        d = des_idx.get(k)
        if r and d:
            # Prefer the one with higher Search Volume, else revenue
            r_sv = _to_int(r.get("Search Volume")) or -1
            d_sv = _to_int(d.get("Search Volume")) or -1
            return r if r_sv >= d_sv else d
        return r or d

    out: Dict[str, Dict[str, Any]] = {}
    for kw in (base_relevancy_scores or {}).keys():
        row = _pick_row(kw)
        if not row:
            # No metrics found; keep empty dict so callers can detect presence but nothing to merge.
            out[kw] = {}
            continue

        title_density = _to_int(row.get("Title Density"))
        search_volume = _to_int(row.get("Search Volume"))
        cpr = _to_int(row.get("CPR"))

        comp_products = _to_int(row.get("Competing Products"))
        ranking_competitors = _to_int(row.get("Ranking Competitors (count)"))
        competitor_rank_avg = _to_float(row.get("Competitor Rank (avg)"))
        comp_perf_score = _to_float(row.get("Competitor Performance Score"))

        m: Dict[str, Any] = {}
        if title_density is not None:
            m["title_density"] = title_density
        if search_volume is not None:
            m["search_volume"] = search_volume
        if cpr is not None:
            m["cpr"] = cpr

        comp: Dict[str, Any] = {}
        if comp_products is not None:
            comp["competing_products"] = comp_products
        if ranking_competitors is not None:
            comp["ranking_competitors"] = ranking_competitors
        if competitor_rank_avg is not None:
            comp["competitor_rank_avg"] = competitor_rank_avg
        if comp_perf_score is not None:
            comp["competitor_performance_score"] = comp_perf_score
        if comp:
            m["competition"] = comp

        out[kw] = m

    return out


def merge_metrics_into_items(
    items: List[Dict[str, Any]],
    metrics_map: Dict[str, Dict[str, Any]],
    *,
    case_insensitive: bool = True,
) -> List[Dict[str, Any]]:
    """
    Append metrics onto existing item dicts without removing values.

    - Only writes fields that exist in metrics_map (missing metrics are skipped).
    - Does not overwrite existing values with None (collect_metrics_from_csv already omits None keys).

    Returns the same list (mutated in place) for convenience.
    """

    if not items or not metrics_map:
        return items

    # Build a lookup map (optionally case-insensitive) from phrase -> metrics
    lookup: Dict[str, Dict[str, Any]] = (
        { (k.lower() if case_insensitive else k): v for k, v in metrics_map.items() }
    )

    for it in items:
        phrase = str((it or {}).get("phrase", ""))
        key = phrase.lower() if case_insensitive else phrase
        m = lookup.get(key)
        if not m:
            continue

        # Shallow fields
        for fld in ("title_density", "search_volume", "cpr"):
            if fld in m and m[fld] is not None:
                # Only set if not already present or value differs
                it[fld] = m[fld]

        # Nested competition
        comp = m.get("competition") or {}
        if comp:
            dest = it.get("competition") or {}
            for cf in (
                "competing_products",
                "ranking_competitors",
                "competitor_rank_avg",
                "competitor_performance_score",
            ):
                if cf in comp and comp[cf] is not None:
                    dest[cf] = comp[cf]
            if dest:
                it["competition"] = dest

    return items
