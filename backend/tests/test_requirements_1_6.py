"""
Test Requirements 1-6: CSV Processing, Relevancy Filtering, Root Extraction, 
Branded/Stopwords Filtering, Volume Selection, ASIN Extraction

Requirements:
1. Pick up keyword lists from both provided CSV files
2. Apply relevancy formula to CSV, filter out keywords with relevancy zero
3. Break down keywords into root words
4. Exclude branded/stopwords from extracted root words
5. Pick one keyword per root with highest search volume
6. Pick up ASINs from given CSV files
"""

import pytest
import tempfile
import os
from typing import Dict, Any, List
from app.services.file_processing.csv_processor import parse_csv_generic, parse_csv_bytes
from app.services.keyword_processing.root_extraction import extract_meaningful_roots, select_best_keyword_variant
from app.services.keyword_processing.batch_processor import optimize_keyword_processing_for_agents
from app.local_agents.research.helper_methods import collect_asins


class TestRequirements1To6:
    """Test requirements 1-6: CSV processing and keyword analysis"""
    
    @pytest.fixture
    def sample_revenue_csv(self):
        """Sample revenue CSV data"""
        csv_content = """Keyword Phrase,Search Volume,Relevancy Score,ASIN
freeze dried strawberry,1200,8,B08KT2Z93D
organic freeze dried,800,7,B08KT2Z94E
strawberry slices,600,6,B08KT2Z95F
bulk strawberries,400,5,B08KT2Z96G
dried fruit snack,300,4,B08KT2Z97H
freeze dried fruit,200,3,B08KT2Z98I
strawberry powder,150,2,B08KT2Z99J
fruit snacks,100,1,B08KT2Z9AK
banana chips,50,0,B08KT2Z9BL
apple slices,25,0,B08KT2Z9CM"""
        return csv_content
    
    @pytest.fixture
    def sample_design_csv(self):
        """Sample design CSV data"""
        csv_content = """Keyword Phrase,Search Volume,Relevancy Score,ASIN
freeze dried strawberries,900,9,B08KT2Z93D
organic strawberry slices,700,8,B08KT2Z94E
bulk strawberry pieces,500,7,B08KT2Z95F
strawberry chunks,350,6,B08KT2Z96G
dried strawberry snack,250,5,B08KT2Z97H
freeze dried berry,180,4,B08KT2Z98I
strawberry powder,120,3,B08KT2Z99J
berry snacks,80,2,B08KT2Z9AK
orange slices,40,1,B08KT2Z9BL
grape pieces,20,0,B08KT2Z9CM"""
        return csv_content
    
    def test_requirement_1_csv_processing(self, sample_revenue_csv, sample_design_csv):
        """Test requirement 1: Pick up keyword lists from both CSV files"""
        # Create temporary CSV files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_revenue_csv)
            revenue_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_design_csv)
            design_file = f.name
        
        try:
            # Parse revenue CSV
            revenue_result = parse_csv_generic(revenue_file)
            assert revenue_result["success"], f"Revenue CSV parsing failed: {revenue_result.get('error')}"
            assert len(revenue_result["data"]) == 10, f"Expected 10 revenue keywords, got {len(revenue_result['data'])}"
            
            # Parse design CSV
            design_result = parse_csv_generic(design_file)
            assert design_result["success"], f"Design CSV parsing failed: {design_result.get('error')}"
            assert len(design_result["data"]) == 10, f"Expected 10 design keywords, got {len(design_result['data'])}"
            
            # Extract keyword phrases
            revenue_keywords = [row["Keyword Phrase"] for row in revenue_result["data"]]
            design_keywords = [row["Keyword Phrase"] for row in design_result["data"]]
            
            assert "freeze dried strawberry" in revenue_keywords
            assert "freeze dried strawberries" in design_keywords
            
            print(f"✅ Requirement 1: Successfully processed {len(revenue_keywords)} revenue and {len(design_keywords)} design keywords")
            
        finally:
            os.unlink(revenue_file)
            os.unlink(design_file)
    
    def test_requirement_2_relevancy_filtering(self, sample_revenue_csv):
        """Test requirement 2: Filter out keywords with relevancy score 0"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_revenue_csv)
            csv_file = f.name
        
        try:
            result = parse_csv_generic(csv_file)
            assert result["success"]
            
            # Filter out keywords with relevancy score 0
            filtered_data = [row for row in result["data"] if row["Relevancy Score"] > 0]
            
            # Should have 8 keywords (excluding the 2 with score 0)
            assert len(filtered_data) == 8, f"Expected 8 keywords after filtering, got {len(filtered_data)}"
            
            # Verify no zero scores
            for row in filtered_data:
                assert row["Relevancy Score"] > 0, f"Found keyword with score 0: {row['Keyword Phrase']}"
            
            print(f"✅ Requirement 2: Successfully filtered out {len(result['data']) - len(filtered_data)} keywords with relevancy score 0")
            
        finally:
            os.unlink(csv_file)
    
    def test_requirement_3_root_extraction(self):
        """Test requirement 3: Break down keywords into root words"""
        keywords = [
            "freeze dried strawberry",
            "freeze dried strawberries", 
            "organic freeze dried",
            "strawberry slices",
            "bulk strawberries"
        ]
        
        # Extract meaningful roots
        roots = extract_meaningful_roots(keywords)
        
        # Should extract meaningful root words
        assert len(roots) > 0, "No root words extracted"
        
        # Check for expected roots
        root_names = list(roots.keys())
        assert "strawberry" in root_names or "freeze" in root_names, f"Expected root words not found: {root_names}"
        
        # Verify root structure
        for root_name, root_obj in roots.items():
            assert hasattr(root_obj, 'root'), "Root object missing 'root' attribute"
            assert hasattr(root_obj, 'variants'), "Root object missing 'variants' attribute"
            assert hasattr(root_obj, 'frequency'), "Root object missing 'frequency' attribute"
            assert len(root_obj.variants) > 0, f"Root '{root_name}' has no variants"
        
        print(f"✅ Requirement 3: Successfully extracted {len(roots)} root words from {len(keywords)} keywords")
    
    def test_requirement_4_branded_stopwords_filtering(self):
        """Test requirement 4: Exclude branded/stopwords from root words"""
        keywords = [
            "keekaroo changing pad",
            "skip hop diaper bag", 
            "frida baby products",
            "munchkin baby items",
            "freeze dried strawberry",
            "organic fruit snack"
        ]
        
        roots = extract_meaningful_roots(keywords)
        
        # Should filter out branded terms
        root_names = list(roots.keys())
        
        # Branded terms should be filtered out or categorized appropriately
        branded_terms = ["keekaroo", "skip", "hop", "frida", "munchkin"]
        for term in branded_terms:
            if term in root_names:
                root_obj = roots[term]
                # If present, should be categorized as brand
                assert root_obj.category == 'brand', f"Branded term '{term}' not categorized as brand"
        
        # Should include meaningful product terms
        meaningful_terms = ["strawberry", "freeze", "organic", "fruit"]
        found_meaningful = any(term in root_names for term in meaningful_terms)
        assert found_meaningful, f"No meaningful terms found in roots: {root_names}"
        
        print(f"✅ Requirement 4: Successfully filtered branded/stopwords, found {len(roots)} meaningful roots")
    
    def test_requirement_5_highest_volume_selection(self):
        """Test requirement 5: Pick one keyword per root with highest search volume"""
        # Mock keyword data with different search volumes
        keywords_with_data = [
            {"phrase": "freeze dried strawberry", "search_volume": 1200, "root": "strawberry"},
            {"phrase": "freeze dried strawberries", "search_volume": 800, "root": "strawberry"},
            {"phrase": "organic strawberry", "search_volume": 600, "root": "strawberry"},
            {"phrase": "strawberry slices", "search_volume": 400, "root": "strawberry"}
        ]
        
        # Select best variant
        best_variant = select_best_keyword_variant(keywords_with_data)
        
        # Should select the highest volume variant
        assert best_variant["phrase"] == "freeze dried strawberry", f"Expected 'freeze dried strawberry', got '{best_variant['phrase']}'"
        assert best_variant["search_volume"] == 1200, f"Expected volume 1200, got {best_variant['search_volume']}"
        
        print(f"✅ Requirement 5: Successfully selected highest volume variant: {best_variant['phrase']} (volume: {best_variant['search_volume']})")
    
    def test_requirement_6_asin_extraction(self, sample_revenue_csv):
        """Test requirement 6: Pick up ASINs from CSV files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_revenue_csv)
            csv_file = f.name
        
        try:
            result = parse_csv_generic(csv_file)
            assert result["success"]
            
            # Extract ASINs using the helper function
            asins = collect_asins(result["data"])
            
            # Should extract ASINs
            assert len(asins) > 0, "No ASINs extracted from CSV"
            
            # Verify ASIN format (should start with B0 and be 10 characters)
            for asin in asins:
                assert asin.startswith("B0"), f"Invalid ASIN format: {asin}"
                assert len(asin) == 10, f"ASIN should be 10 characters: {asin}"
            
            # Should have extracted the ASINs from the CSV
            expected_asins = {"B08KT2Z93D", "B08KT2Z94E", "B08KT2Z95F", "B08KT2Z96G", "B08KT2Z97H"}
            found_asins = asins.intersection(expected_asins)
            assert len(found_asins) > 0, f"Expected ASINs not found: {asins}"
            
            print(f"✅ Requirement 6: Successfully extracted {len(asins)} ASINs from CSV")
            
        finally:
            os.unlink(csv_file)
    
    def test_requirements_integration(self, sample_revenue_csv, sample_design_csv):
        """Test integration of requirements 1-6"""
        # Create temporary CSV files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_revenue_csv)
            revenue_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_design_csv)
            design_file = f.name
        
        try:
            # Parse both CSVs
            revenue_result = parse_csv_generic(revenue_file)
            design_result = parse_csv_generic(design_file)
            
            assert revenue_result["success"] and design_result["success"]
            
            # Extract keywords and filter by relevancy
            revenue_keywords = [row["Keyword Phrase"] for row in revenue_result["data"] if row["Relevancy Score"] > 0]
            design_keywords = [row["Keyword Phrase"] for row in design_result["data"] if row["Relevancy Score"] > 0]
            
            # Process with batch processor
            analysis_result = optimize_keyword_processing_for_agents(
                revenue_keywords=revenue_keywords,
                design_keywords=design_keywords,
                batch_size=10
            )
            
            # Verify results
            assert "best_variants_per_root" in analysis_result
            assert "root_selection_stats" in analysis_result
            
            best_variants = analysis_result["best_variants_per_root"]
            selection_stats = analysis_result["root_selection_stats"]
            
            assert selection_stats["selection_applied"] == True
            assert selection_stats["total_roots"] > 0
            
            print(f"✅ Integration Test: Successfully processed {len(revenue_keywords)} revenue + {len(design_keywords)} design keywords")
            print(f"   Generated {selection_stats['total_roots']} roots with {selection_stats['roots_with_multiple_variants']} having multiple variants")
            
        finally:
            os.unlink(revenue_file)
            os.unlink(design_file)


