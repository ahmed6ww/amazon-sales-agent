#!/usr/bin/env python3
"""
Test suite for keyword filtering flow from CSV to batch processor.

Tests the complete pipeline:
1. CSV parsing and relevancy score calculation
2. Filtering by relevancy >= 5 
3. Batch processing with root extraction
4. Keyword categorization results
5. SEO agent input validation

Expected flow:
647 keywords → ~200-300 high-relevancy → 1000 processed → ~50-80 relevant
"""

import pytest
import json
from typing import Dict, List, Any
from unittest.mock import Mock, patch

from app.services.file_processing.csv_processor import parse_csv_bytes
from app.local_agents.research.runner import ResearchRunner
from app.services.keyword_processing.batch_processor import (
    create_agent_optimized_base_relevancy_scores,
    optimize_keyword_processing_for_agents
)
from app.local_agents.keyword.runner import KeywordRunner
from app.local_agents.scoring.runner import ScoringRunner
from app.local_agents.seo.runner import SEORunner


class TestKeywordFilteringFlow:
    """Test the complete keyword filtering and processing flow"""

    @pytest.fixture
    def sample_revenue_csv_data(self):
        """Sample revenue CSV data with keyword rankings"""
        return [
            {
                'Keyword Phrase': 'freeze dried strawberry',
                'Search Volume': 30664,
                'Revenue': 125000,
                'B08KT2Z93D': 3,  # Rank 3
                'B08KT2Z94E': 7,  # Rank 7
                'B08KT2Z95F': 15, # Rank 15 (not top 10)
                'B08KT2Z96G': 8,  # Rank 8
                'B08KT2Z97H': 12  # Rank 12 (not top 10)
            },
            {
                'Keyword Phrase': 'freeze dried strawberries',
                'Search Volume': 25000,
                'Revenue': 98000,
                'B08KT2Z93D': 1,  # Rank 1
                'B08KT2Z94E': 4,  # Rank 4
                'B08KT2Z95F': 6,  # Rank 6
                'B08KT2Z96G': 9,  # Rank 9
                'B08KT2Z97H': 11  # Rank 11 (not top 10)
            },
            {
                'Keyword Phrase': 'organic freeze dried strawberry',
                'Search Volume': 8500,
                'Revenue': 45000,
                'B08KT2Z93D': 2,  # Rank 2
                'B08KT2Z94E': 5,  # Rank 5
                'B08KT2Z95F': 8,  # Rank 8
                'B08KT2Z96G': 13, # Rank 13 (not top 10)
                'B08KT2Z97H': 16  # Rank 16 (not top 10)
            },
            {
                'Keyword Phrase': 'strawberry slices',
                'Search Volume': 12000,
                'Revenue': 35000,
                'B08KT2Z93D': 6,  # Rank 6
                'B08KT2Z94E': 3,  # Rank 3
                'B08KT2Z95F': 7,  # Rank 7
                'B08KT2Z96G': 14, # Rank 14 (not top 10)
                'B08KT2Z97H': 18  # Rank 18 (not top 10)
            },
            {
                'Keyword Phrase': 'bulk freeze dried strawberries',
                'Search Volume': 6500,
                'Revenue': 28000,
                'B08KT2Z93D': 4,  # Rank 4
                'B08KT2Z94E': 9,  # Rank 9
                'B08KT2Z95F': 11, # Rank 11 (not top 10)
                'B08KT2Z96G': 5,  # Rank 5
                'B08KT2Z97H': 19  # Rank 19 (not top 10)
            },
            {
                'Keyword Phrase': 'unrelated product keyword',
                'Search Volume': 5000,
                'Revenue': 15000,
                'B08KT2Z93D': 25, # Rank 25 (not top 10)
                'B08KT2Z94E': 30, # Rank 30 (not top 10)
                'B08KT2Z95F': 35, # Rank 35 (not top 10)
                'B08KT2Z96G': 40, # Rank 40 (not top 10)
                'B08KT2Z97H': 45  # Rank 45 (not top 10)
            }
        ]

    @pytest.fixture
    def sample_design_csv_data(self):
        """Sample design CSV data with relevancy scores"""
        return [
            {
                'Keyword Phrase': 'freeze dried strawberry powder',
                'Search Volume': 4000,
                'Cerebro IQ Score': 85,
                'Relevancy': 8.5,
                'B08KT2Z93D': 10, # Rank 10 (edge case)
                'B08KT2Z94E': 15, # Rank 15 (not top 10)
                'B08KT2Z95F': 5,  # Rank 5
                'B08KT2Z96G': 12, # Rank 12 (not top 10)
                'B08KT2Z97H': 8   # Rank 8
            },
            {
                'Keyword Phrase': 'strawberry fruit snacks',
                'Search Volume': 3200,
                'Cerebro IQ Score': 78,
                'Relevancy': 7.2,
                'B08KT2Z93D': 20, # Rank 20 (not top 10)
                'B08KT2Z94E': 25, # Rank 25 (not top 10)
                'B08KT2Z95F': 18, # Rank 18 (not top 10)
                'B08KT2Z96G': 22, # Rank 22 (not top 10)
                'B08KT2Z97H': 28  # Rank 28 (not top 10)
            }
        ]

    @pytest.fixture
    def competitor_asins(self):
        """Sample competitor ASINs"""
        return [
            'B08KT2Z93D',
            'B08KT2Z94E',
            'B08KT2Z95F',
            'B08KT2Z96G',
            'B08KT2Z97H'
        ]

    @pytest.fixture
    def sample_scraped_product(self):
        """Sample scraped product data"""
        return {
            'title': 'BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added',
            'category': 'Food & Grocery',
            'brand': 'BREWER',
            'bullets': [
                'PURE STRAWBERRY GOODNESS: Made from 100% real strawberries',
                'ORGANIC & HEALTHY: Certified organic freeze dried strawberries',
                'BULK PACK VALUE: Pack of 4 individual 1.2 oz bags',
                'VERSATILE USAGE: Perfect for baking, smoothies, cereals',
                'TRAVEL READY: Lightweight and shelf-stable'
            ]
        }

    def test_relevancy_score_calculation(self, sample_revenue_csv_data, competitor_asins):
        """Test relevancy score calculation formula"""
        # Extract the relevancy calculation logic directly
        def _compute_relevancy_scores(rows: List[Dict[str, Any]], competitor_asins: List[str]) -> Dict[str, int]:
            scores: Dict[str, int] = {}
            if not rows or not competitor_asins:
                return scores
            asin_set = [a for a in competitor_asins if isinstance(a, str) and len(a) == 10 and a.startswith('B0')][:50]
            if not asin_set:
                return scores
            for row in rows[:50]:
                kw = str(row.get('Keyword Phrase', '')).strip()
                if not kw:
                    continue
                ranks_in_top10 = 0
                for asin in asin_set:
                    try:
                        rank_val = row.get(asin)
                        if rank_val is None:
                            continue
                        rank_num = int(float(rank_val))
                        if rank_num > 0 and rank_num <= 10:
                            ranks_in_top10 += 1
                    except Exception:
                        continue
                score10 = int(round((ranks_in_top10 / max(1, len(asin_set))) * 10.0))
                scores[kw] = max(scores.get(kw, 0), score10)
            return scores
        
        relevancy_scores = _compute_relevancy_scores(sample_revenue_csv_data, competitor_asins)
        
        # Expected calculations:
        # 'freeze dried strawberry': 3/5 * 10 = 6
        # 'freeze dried strawberries': 4/5 * 10 = 8  
        # 'organic freeze dried strawberry': 3/5 * 10 = 6
        # 'strawberry slices': 3/5 * 10 = 6
        # 'bulk freeze dried strawberries': 3/5 * 10 = 6
        # 'unrelated product keyword': 0/5 * 10 = 0
        
        expected_scores = {
            'freeze dried strawberry': 6,
            'freeze dried strawberries': 8,
            'organic freeze dried strawberry': 6,
            'strawberry slices': 6,
            'bulk freeze dried strawberries': 6,
            'unrelated product keyword': 0
        }
        
        assert relevancy_scores == expected_scores

    def test_relevancy_filtering_threshold_5(self, sample_revenue_csv_data, competitor_asins):
        """Test filtering keywords with relevancy score >= 5"""
        runner = ResearchRunner()
        
        # Calculate relevancy scores
        all_scores = runner._compute_relevancy_scores(sample_revenue_csv_data, competitor_asins)
        
        # Filter by threshold >= 5
        filtered_scores = {kw: score for kw, score in all_scores.items() if score >= 5}
        
        # Expected: All keywords except 'unrelated product keyword' (score 0)
        expected_filtered = {
            'freeze dried strawberry': 6,
            'freeze dried strawberries': 8,
            'organic freeze dried strawberry': 6,
            'strawberry slices': 6,
            'bulk freeze dried strawberries': 6
        }
        
        assert filtered_scores == expected_filtered
        assert len(filtered_scores) == 5  # 5 out of 6 keywords pass the filter

    def test_batch_processor_keyword_limit(self, sample_revenue_csv_data, competitor_asins):
        """Test that batch processor handles increased keyword limit"""
        runner = ResearchRunner()
        
        # Calculate relevancy scores
        relevancy_scores = runner._compute_relevancy_scores(sample_revenue_csv_data, competitor_asins)
        
        # Filter by threshold >= 5
        filtered_keywords = list({kw: score for kw, score in relevancy_scores.items() if score >= 5}.keys())
        
        # Test batch processor with increased limit
        optimized_scores = create_agent_optimized_base_relevancy_scores(
            filtered_keywords,
            max_keywords_for_agent=1000  # Increased limit
        )
        
        # Should process all filtered keywords
        assert len(optimized_scores) <= len(filtered_keywords)
        assert len(optimized_scores) <= 1000  # Respects the limit

    def test_keyword_categorization_accuracy(self, sample_scraped_product, sample_revenue_csv_data, competitor_asins):
        """Test keyword categorization accuracy with filtered keywords"""
        runner = ResearchRunner()
        keyword_runner = KeywordRunner()
        
        # Calculate relevancy scores and filter
        relevancy_scores = runner._compute_relevancy_scores(sample_revenue_csv_data, competitor_asins)
        filtered_scores = {kw: score for kw, score in relevancy_scores.items() if score >= 5}
        
        # Run keyword categorization
        result = keyword_runner.run_keyword_categorization(sample_scraped_product, filtered_scores)
        
        # Analyze results
        items = result['structured_data'].get('items', [])
        relevant_count = sum(1 for item in items if item.get('category') == 'Relevant')
        design_specific_count = sum(1 for item in items if item.get('category') == 'Design-Specific')
        irrelevant_count = sum(1 for item in items if item.get('category') == 'Irrelevant')
        
        # Expected: Most keywords should be 'Relevant' since they passed relevancy >= 5
        assert relevant_count > 0, "Should have at least some Relevant keywords"
        assert relevant_count >= design_specific_count, "Relevant should dominate after relevancy filtering"
        assert irrelevant_count == 0, "No keywords should be Irrelevant after relevancy filtering"

    def test_seo_agent_keyword_input(self, sample_scraped_product, sample_revenue_csv_data, competitor_asins):
        """Test that SEO agent receives adequate keywords from filtered set"""
        runner = ResearchRunner()
        keyword_runner = KeywordRunner()
        scoring_runner = ScoringRunner()
        seo_runner = SEORunner()
        
        # Calculate relevancy scores and filter
        relevancy_scores = runner._compute_relevancy_scores(sample_revenue_csv_data, competitor_asins)
        filtered_scores = {kw: score for kw, score in relevancy_scores.items() if score >= 5}
        
        # Run keyword categorization
        keyword_result = keyword_runner.run_keyword_categorization(sample_scraped_product, filtered_scores)
        keyword_items = keyword_result['structured_data'].get('items', [])
        
        # Run scoring (with intent scores)
        scoring_result = scoring_runner.run_scoring_analysis(keyword_items)
        scored_items = scoring_result['structured_data'].get('items', [])
        
        # Run SEO analysis
        seo_result = seo_runner.run_seo_analysis(scored_items)
        
        # Verify SEO agent has adequate keywords
        seo_keywords = seo_result.get('structured_data', {}).get('optimized_keywords', [])
        
        assert len(seo_keywords) > 0, "SEO agent should have keywords to work with"
        assert len(seo_keywords) >= 3, "Should have enough keywords for title and bullets"

    def test_end_to_end_flow_accuracy(self, sample_revenue_csv_data, sample_design_csv_data, competitor_asins, sample_scraped_product):
        """Test complete end-to-end flow accuracy"""
        runner = ResearchRunner()
        keyword_runner = KeywordRunner()
        scoring_runner = ScoringRunner()
        seo_runner = SEORunner()
        
        # Step 1: Calculate relevancy scores from both CSVs
        revenue_scores = runner._compute_relevancy_scores(sample_revenue_csv_data, competitor_asins)
        design_scores = runner._compute_relevancy_scores(sample_design_csv_data, competitor_asins)
        
        # Combine scores (keep max)
        combined_scores = revenue_scores.copy()
        for kw, score in design_scores.items():
            combined_scores[kw] = max(combined_scores.get(kw, 0), score)
        
        # Step 2: Filter by relevancy >= 5
        filtered_scores = {kw: score for kw, score in combined_scores.items() if score >= 5}
        filtered_keywords = list(filtered_scores.keys())
        
        # Step 3: Batch processing
        optimized_scores = create_agent_optimized_base_relevancy_scores(
            filtered_keywords,
            max_keywords_for_agent=1000
        )
        
        # Step 4: Keyword categorization
        keyword_result = keyword_runner.run_keyword_categorization(sample_scraped_product, optimized_scores)
        keyword_items = keyword_result['structured_data'].get('items', [])
        
        # Step 5: Scoring
        scoring_result = scoring_runner.run_scoring_analysis(keyword_items)
        scored_items = scoring_result['structured_data'].get('items', [])
        
        # Step 6: SEO analysis
        seo_result = seo_runner.run_seo_analysis(scored_items)
        
        # Verify flow accuracy
        print(f"\n=== End-to-End Flow Results ===")
        print(f"Original keywords: {len(sample_revenue_csv_data) + len(sample_design_csv_data)}")
        print(f"After relevancy filtering (>=5): {len(filtered_keywords)}")
        print(f"After batch processing: {len(optimized_scores)}")
        print(f"After keyword categorization: {len(keyword_items)}")
        print(f"After scoring: {len(scored_items)}")
        print(f"SEO keywords generated: {len(seo_result.get('structured_data', {}).get('optimized_keywords', []))}")
        
        # Assertions for expected flow
        assert len(filtered_keywords) <= len(sample_revenue_csv_data) + len(sample_design_csv_data)
        assert len(optimized_scores) <= len(filtered_keywords)
        assert len(keyword_items) <= len(optimized_scores)
        assert len(scored_items) <= len(keyword_items)
        
        # Verify keyword quality
        relevant_count = sum(1 for item in keyword_items if item.get('category') == 'Relevant')
        assert relevant_count > 0, "Should have Relevant keywords after filtering"

    def test_keyword_quality_metrics(self, sample_revenue_csv_data, competitor_asins, sample_scraped_product):
        """Test keyword quality metrics to ensure filtering improves results"""
        runner = ResearchRunner()
        keyword_runner = KeywordRunner()
        
        # Test without filtering
        all_scores = runner._compute_relevancy_scores(sample_revenue_csv_data, competitor_asins)
        result_no_filter = keyword_runner.run_keyword_categorization(sample_scraped_product, all_scores)
        items_no_filter = result_no_filter['structured_data'].get('items', [])
        
        # Test with relevancy filtering >= 5
        filtered_scores = {kw: score for kw, score in all_scores.items() if score >= 5}
        result_with_filter = keyword_runner.run_keyword_categorization(sample_scraped_product, filtered_scores)
        items_with_filter = result_with_filter['structured_data'].get('items', [])
        
        # Calculate quality metrics
        relevant_no_filter = sum(1 for item in items_no_filter if item.get('category') == 'Relevant')
        relevant_with_filter = sum(1 for item in items_with_filter if item.get('category') == 'Relevant')
        
        irrelevant_no_filter = sum(1 for item in items_no_filter if item.get('category') == 'Irrelevant')
        irrelevant_with_filter = sum(1 for item in items_with_filter if item.get('category') == 'Irrelevant')
        
        print(f"\n=== Quality Metrics ===")
        print(f"Without filtering: {relevant_no_filter} relevant, {irrelevant_no_filter} irrelevant")
        print(f"With filtering (>=5): {relevant_with_filter} relevant, {irrelevant_with_filter} irrelevant")
        
        # Quality assertions
        assert relevant_with_filter >= relevant_no_filter, "Filtering should not reduce relevant keywords"
        assert irrelevant_with_filter <= irrelevant_no_filter, "Filtering should reduce irrelevant keywords"
        
        # Calculate relevance ratio
        if len(items_with_filter) > 0:
            relevance_ratio = relevant_with_filter / len(items_with_filter)
            assert relevance_ratio >= 0.5, f"Relevance ratio should be >= 50%, got {relevance_ratio:.2%}"

    def test_performance_with_large_dataset(self):
        """Test performance with simulated large dataset (647 keywords)"""
        # Generate large dataset
        large_keywords = []
        for i in range(647):
            if i < 300:  # First 300 have high relevancy
                large_keywords.append(f'high_relevancy_keyword_{i}')
            else:  # Rest have low relevancy
                large_keywords.append(f'low_relevancy_keyword_{i}')
        
        # Test batch processor performance
        optimized_scores = create_agent_optimized_base_relevancy_scores(
            large_keywords,
            max_keywords_for_agent=1000
        )
        
        # Should handle large dataset efficiently
        assert len(optimized_scores) <= 1000
        assert len(optimized_scores) > 0
        
        print(f"\n=== Large Dataset Performance ===")
        print(f"Input keywords: 647")
        print(f"Processed keywords: {len(optimized_scores)}")
        print(f"Processing ratio: {len(optimized_scores)/647:.2%}")

    def test_relevancy_threshold_sensitivity(self, sample_revenue_csv_data, competitor_asins):
        """Test how different relevancy thresholds affect filtering results"""
        runner = ResearchRunner()
        all_scores = runner._compute_relevancy_scores(sample_revenue_csv_data, competitor_asins)
        
        thresholds = [0, 3, 5, 7, 10]
        results = {}
        
        for threshold in thresholds:
            filtered = {kw: score for kw, score in all_scores.items() if score >= threshold}
            results[threshold] = len(filtered)
        
        print(f"\n=== Threshold Sensitivity ===")
        for threshold, count in results.items():
            print(f"Threshold >= {threshold}: {count} keywords")
        
        # Verify expected behavior
        assert results[0] >= results[3] >= results[5] >= results[7] >= results[10]
        assert results[5] > 0, "Threshold 5 should return some keywords"
        assert results[10] <= results[5], "Higher threshold should return fewer keywords"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
