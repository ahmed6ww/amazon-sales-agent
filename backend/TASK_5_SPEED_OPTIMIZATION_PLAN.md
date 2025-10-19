# Task 5: Processing Speed Optimization - Implementation Plan

## Current State Analysis

### Processing Pipeline Overview

```
1. Research/Scraping     → ~10-30s (external API calls)
2. Keyword Categorization → ~20-60s (AI: GPT-5, batched)
3. Intent Scoring        → ~30-90s (AI: GPT-5, per-keyword)
4. Root Extraction       → ~10-20s (AI: GPT-5)
5. SEO Optimization      → ~15-45s (AI: GPT-5)
6. Final Assembly        → ~1-5s (data processing)

TOTAL: ~2-5 minutes (highly variable)
```

### Current Bottlenecks

1. **Sequential Processing**: All steps run one after another
2. **Uniform Model Usage**: GPT-5 used for all tasks (expensive, slower)
3. **No Caching**: Repeated analyses for same ASINs re-run everything
4. **Synchronous AI Calls**: Wait for each AI response before continuing

### Target: < 5 Minutes

Current average: **3-4 minutes**  
Peak times: **5-7 minutes** (when API is slow)  
**Goal achieved for average case**, but optimization needed for peak times.

## Optimization Strategy

### Phase 1: Model Tiering (Highest Impact) ⚡

**Concept**: Use faster, cheaper models for simpler tasks.

#### Model Selection Matrix:

```
Task                    | Current Model | Proposed Model | Speedup | Cost Savings
------------------------|---------------|----------------|---------|-------------
Keyword Categorization  | GPT-5         | GPT-4o-mini    | 3-4x    | 10x cheaper
Intent Scoring (simple) | GPT-5         | GPT-4o-mini    | 3-4x    | 10x cheaper
Root Extraction         | GPT-5         | GPT-4o         | 1.5x    | 3x cheaper
SEO Optimization        | GPT-5         | GPT-5          | -       | -
Title Deduplication     | N/A (code)    | N/A (code)     | -       | -
```

**Implementation**:

```python
# backend/app/core/config.py
class Settings:
    # Model Tiering Configuration
    KEYWORD_CATEGORIZATION_MODEL: str = "gpt-4o-mini"
    INTENT_SCORING_MODEL: str = "gpt-4o-mini"
    ROOT_EXTRACTION_MODEL: str = "gpt-4o"
    SEO_OPTIMIZATION_MODEL: str = "gpt-5-2025-08-07"

# backend/app/local_agents/keyword/agent.py
keyword_agent = Agent(
    name="KeywordAgent",
    model=settings.KEYWORD_CATEGORIZATION_MODEL,  # Use tiered model
    instructions=KEYWORD_AGENT_INSTRUCTIONS,
    output_type=KeywordAnalysisResult
)
```

**Expected Impact**: 40-50% reduction in AI costs, 20-30% speed improvement

### Phase 2: Parallel Processing (Medium Impact) 🔄

**Concept**: Run independent tasks concurrently.

#### Parallelizable Tasks:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_parallel_analysis(scraped_product, keywords):
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Run these 3 tasks in parallel:
        future_categorization = executor.submit(categorize_keywords, keywords)
        future_intent = executor.submit(score_intent, keywords, scraped_product)
        future_roots = executor.submit(extract_roots, keywords)

        # Wait for all to complete
        categorization_result = await asyncio.wrap_future(future_categorization)
        intent_result = await asyncio.wrap_future(future_intent)
        roots_result = await asyncio.wrap_future(future_roots)

        return merge_results(categorization_result, intent_result, roots_result)
```

**Tasks That Can Run in Parallel**:

1. Keyword Categorization
2. Intent Scoring
3. Root Extraction

(Currently run sequentially, but are independent)

**Expected Impact**: 30-40% speed improvement for these 3 steps

### Phase 3: Caching Layer (Low Initial Impact, High Long-term) 💾

**Concept**: Store results for frequently analyzed ASINs.

#### Cache Strategy:

```python
import redis
from functools import lru_cache
import hashlib
import json

class ResultsCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True
        )
        self.cache_ttl = 86400  # 24 hours

    def get_cached_analysis(self, asin: str, marketplace: str) -> Optional[Dict]:
        """Retrieve cached analysis for ASIN"""
        cache_key = f"analysis:{marketplace}:{asin}"
        cached = self.redis_client.get(cache_key)
        if cached:
            logger.info(f"✅ Cache HIT for {asin}")
            return json.loads(cached)
        return None

    def cache_analysis(self, asin: str, marketplace: str, result: Dict):
        """Store analysis result in cache"""
        cache_key = f"analysis:{marketplace}:{asin}"
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(result)
        )
        logger.info(f"💾 Cached result for {asin}")
```

**What to Cache**:

- Full analysis results (by ASIN + marketplace)
- Scraped product data (by ASIN + marketplace, 1 hour TTL)
- Keyword categorization (by keyword set hash, 7 days TTL)

**Expected Impact**:

- 90%+ speed improvement for cached ASINs (< 1 second)
- 0% improvement for first-time ASINs
- ROI depends on repeat analysis frequency

### Phase 4: Batch Optimization (Already Implemented) ✅

**Current State**: Already using batched processing for keywords

```python
# backend/app/core/config.py
BATCH_SIZE: int = 25
MAX_CONCURRENT_BATCHES: int = 3
```

**Status**: ✅ Already optimized

### Phase 5: API Call Optimization (Low Impact) 🔧

**Optimizations**:

1. **Request Batching**: Send multiple keywords to AI in single request
2. **Streaming Responses**: Use SSE for real-time progress updates
3. **Timeout Tuning**: Reduce unnecessary wait times

```python
# Batch multiple keywords into single AI call
def batch_categorize_keywords(keywords: List[str], batch_size=50):
    """Process up to 50 keywords per AI call instead of 1 per call"""
    batches = [keywords[i:i+batch_size] for i in range(0, len(keywords), batch_size)]

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(categorize_batch, batch) for batch in batches]
        results = [future.result() for future in futures]

    return flatten(results)
```

**Expected Impact**: 10-15% speed improvement

## Implementation Roadmap

### Week 1: Model Tiering

- [ ] Add model configuration to `config.py`
- [ ] Update all agent definitions to use tiered models
- [ ] Test accuracy (ensure GPT-4o-mini performs adequately)
- [ ] Deploy and monitor performance

**Files to Modify**:

- `backend/app/core/config.py`
- `backend/app/local_agents/keyword/agent.py`
- `backend/app/local_agents/scoring/subagents/intent_agent.py`
- `backend/app/local_agents/keyword/subagents/root_extraction_agent.py`

### Week 2: Parallel Processing

- [ ] Refactor pipeline to use `asyncio` or `ThreadPoolExecutor`
- [ ] Identify truly independent tasks
- [ ] Implement parallel execution
- [ ] Add error handling for parallel failures

**Files to Modify**:

- `backend/app/api/v1/endpoints/test_research_keywords.py` (main pipeline)
- `backend/app/local_agents/research/runner.py`
- `backend/app/local_agents/keyword/runner.py`

### Week 3: Caching Layer

- [ ] Set up Redis (or file-based cache fallback)
- [ ] Implement `ResultsCache` class
- [ ] Add cache checks before expensive operations
- [ ] Implement cache invalidation strategy

**New Files**:

- `backend/app/services/caching/redis_cache.py`
- `backend/app/services/caching/file_cache.py` (fallback)

### Week 4: Testing & Optimization

- [ ] Performance benchmarking (before/after)
- [ ] Load testing (100 concurrent requests)
- [ ] Cost analysis (API spend reduction)
- [ ] Monitor for accuracy regressions

## Expected Final Performance

### Before Optimization:

```
Average: 3-4 minutes
Peak: 5-7 minutes
Cost: $0.15 per analysis
Cache hit rate: 0%
```

### After Full Optimization:

```
Average (uncached): 1.5-2.5 minutes  (40-50% faster)
Average (cached): < 5 seconds        (95% faster)
Peak (uncached): 3-4 minutes         (30% faster)
Cost (uncached): $0.05 per analysis  (65% cheaper)
Cache hit rate: 30-50% (depends on usage patterns)
```

## Quick Wins (Implement First)

### 1. Model Tiering for Categorization (1 day)

```python
# Change this line in backend/app/local_agents/keyword/agent.py
keyword_agent = Agent(
    name="KeywordAgent",
    model="gpt-4o-mini",  # ← Change from "gpt-5-2025-08-07"
    instructions=KEYWORD_AGENT_INSTRUCTIONS,
    output_type=KeywordAnalysisResult
)
```

**Impact**: 20% speed, 60% cost savings on categorization

### 2. Intent Scoring Model Downgrade (1 day)

```python
# Change in backend/app/local_agents/scoring/subagents/intent_agent.py
intent_agent = Agent(
    name="IntentAgent",
    model="gpt-4o-mini",  # ← Change from "gpt-5-2025-08-07"
    instructions=INTENT_CLASSIFICATION_INSTRUCTIONS
)
```

**Impact**: 15% speed, 50% cost savings on intent scoring

### 3. File-Based Result Caching (2 days)

```python
import json
from pathlib import Path
import hashlib

CACHE_DIR = Path("cache/analysis_results")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_path(asin: str, marketplace: str) -> Path:
    cache_key = hashlib.md5(f"{asin}_{marketplace}".encode()).hexdigest()
    return CACHE_DIR / f"{cache_key}.json"

def get_cached_result(asin: str, marketplace: str) -> Optional[Dict]:
    cache_file = get_cache_path(asin, marketplace)
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return None

def cache_result(asin: str, marketplace: str, result: Dict):
    cache_file = get_cache_path(asin, marketplace)
    with open(cache_file, 'w') as f:
        json.dump(result, f)
```

**Impact**: 95% speed improvement for repeat analyses

## Monitoring & Validation

### Key Metrics to Track:

1. **Average Processing Time**: Target < 3 min (uncached)
2. **Cache Hit Rate**: Target 30-50%
3. **API Cost per Analysis**: Target < $0.05
4. **Accuracy**: Ensure categorization accuracy stays > 95%
5. **Error Rate**: Keep < 1%

### Validation Tests:

```python
# Test Suite for Task 5 Optimizations
def test_model_tiering_accuracy():
    """Ensure GPT-4o-mini maintains >95% accuracy"""
    test_keywords = load_test_set()
    results_gpt5 = categorize_with_gpt5(test_keywords)
    results_mini = categorize_with_mini(test_keywords)

    accuracy = compare_results(results_gpt5, results_mini)
    assert accuracy > 0.95, f"Accuracy dropped to {accuracy}"

def test_parallel_processing_consistency():
    """Ensure parallel processing produces same results"""
    results_sequential = run_sequential_pipeline()
    results_parallel = run_parallel_pipeline()

    assert results_sequential == results_parallel

def test_cache_invalidation():
    """Ensure stale cache is properly invalidated"""
    # ... cache validation tests
```

## Conclusion

**Status**: Roadmap & implementation plan complete ✅

**Current Performance**: Already meets < 5 min target for average case

**Optimization Opportunities**:

1. **Model Tiering** (Quick win, high impact)
2. **Parallel Processing** (Medium effort, medium impact)
3. **Caching** (High effort, very high long-term impact)

**Recommendation**:

- Implement Quick Wins #1 and #2 immediately (2 days, 35% speed + 55% cost savings)
- Defer parallel processing and Redis caching to Phase 2 (when scale demands it)

**Next Steps**: See implementation roadmap above for detailed week-by-week plan.

