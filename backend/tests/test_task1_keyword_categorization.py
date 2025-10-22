"""
Test Task 1: Keyword Categorization Logic
Tests the enhanced categorization with product form detection and brand recognition.
"""

import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.local_agents.keyword.runner import KeywordRunner
from app.services.file_processing.csv_processor import parse_csv_bytes

# Mock scraped product data (Freeze Dried Strawberry Slices)
MOCK_PRODUCT_SLICES = {
    "title": "Organic Freeze Dried Strawberry Slices - 1.2oz Bulk Pack",
    "elements": {
        "productTitle": {
            "text": ["Organic Freeze Dried Strawberry Slices - 1.2oz Bulk Pack"],
            "present": True
        },
        "productOverview_feature_div": {
            "present": True,
            "kv": {
                "Brand": "Nature's Best",
                "Package Weight": "1.2 Ounces",
                "Item Form": "Slices"
            }
        },
        "feature-bullets": {
            "present": True,
            "bullets": [
                "Made from 100% organic strawberries",
                "Freeze dried to lock in flavor",
                "Perfect for snacking, baking, or cereal",
                "No sugar added, no preservatives",
                "Resealable bag for freshness"
            ]
        }
    }
}

# Test keywords that should be categorized differently
TEST_KEYWORDS = {
    # Should be RELEVANT (core product descriptors)
    "freeze dried strawberry slices": 8,
    "dried strawberry slices": 7,
    "organic strawberry slices": 7,
    "strawberry slices": 6,
    
    # Should be DESIGN-SPECIFIC (attributes of slices)
    "bulk strawberry slices": 6,
    "organic slices": 5,
    "large slices": 4,
    
    # Should be IRRELEVANT (different product forms)
    "freeze dried strawberry powder": 5,
    "strawberry powder": 4,
    "whole strawberries": 4,
    "strawberry juice": 3,
    "strawberry capsules": 2,
    
    # Should be IRRELEVANT (no contextual connection)
    "strawberry life": 3,
    "how to make strawberry": 2,
    "strawberry recipe": 2,
    
    # Should be BRANDED
    "anthony's freeze dried strawberries": 5,
    "so natural freeze dried fruit": 4,
    "trader joe's organic strawberries": 6,
    "nutristore strawberry slices": 5,
    "ruh roh freeze dried strawberry": 4,
    
    # Edge cases
    "dehydrated strawberry slices": 6,  # Similar to freeze dried - should be RELEVANT or DESIGN-SPECIFIC
    "freeze dried strawberries slices": 7,  # Plural variant - should be RELEVANT
}


def load_csv_keywords(csv_path: str, limit: int = 50) -> dict:
    """Load keywords from CSV file."""
    print(f"\n📂 Loading CSV: {csv_path}")
    
    with open(csv_path, 'rb') as f:
        content = f.read()
    
    result = parse_csv_bytes(os.path.basename(csv_path), content)
    
    if not result.get("success"):
        print(f"❌ Failed to parse CSV: {result.get('error')}")
        return {}
    
    data = result.get("data", [])
    print(f"✅ Loaded {len(data)} keywords from CSV")
    
    # Extract keywords and create mock relevancy scores
    keywords = {}
    for row in data[:limit]:
        phrase = row.get("Keyword Phrase", "").strip()
        if phrase:
            # Use Cerebro IQ Score as relevancy if available
            cerebro = row.get("Cerebro IQ Score", 5)
            try:
                # Convert to 0-10 scale if needed
                score = int(float(cerebro) / 100) if float(cerebro) > 10 else int(float(cerebro))
                score = max(1, min(10, score))  # Clamp to 1-10
            except:
                score = 5
            keywords[phrase] = score
    
    return keywords


def test_keyword_categorization(
    scraped_product: dict,
    base_relevancy_scores: dict,
    test_name: str
):
    """Test keyword categorization and analyze results."""
    print("\n" + "="*80)
    print(f"🧪 TEST: {test_name}")
    print("="*80)
    
    # Run categorization
    runner = KeywordRunner()
    result = runner.run_keyword_categorization(
        scraped_product=scraped_product,
        base_relevancy_scores=base_relevancy_scores,
        marketplace="US",
        asin_or_url="B0TEST12345"
    )
    
    # Analyze results
    structured_data = result.get("structured_data", {})
    items = structured_data.get("items", [])
    stats = structured_data.get("stats", {})
    
    print(f"\n📊 CATEGORIZATION RESULTS:")
    print(f"   Total Keywords: {len(items)}")
    for category, data in stats.items():
        count = data.get("count", 0) if isinstance(data, dict) else 0
        print(f"   - {category}: {count}")
    
    # Detailed analysis by category
    categories = {}
    for item in items:
        cat = item.get("category", "Unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "phrase": item.get("phrase", ""),
            "reason": item.get("reason", ""),
            "relevancy": item.get("relevancy_score", 0)
        })
    
    # Print detailed results
    print("\n" + "-"*80)
    for category in ["Relevant", "Design-Specific", "Irrelevant", "Branded", "Spanish", "Outlier"]:
        if category in categories:
            items_in_cat = categories[category]
            print(f"\n🏷️  {category.upper()} ({len(items_in_cat)} keywords):")
            for item in items_in_cat[:10]:  # Show first 10
                print(f"   • {item['phrase']}")
                print(f"     ↳ Reason: {item['reason'][:100]}...")
                print(f"     ↳ Relevancy: {item['relevancy']}/10")
            if len(items_in_cat) > 10:
                print(f"   ... and {len(items_in_cat) - 10} more")
    
    return categories


def validate_categorization(categories: dict, expected: dict):
    """Validate that categorization matches expectations."""
    print("\n" + "="*80)
    print("✅ VALIDATION RESULTS")
    print("="*80)
    
    issues = []
    successes = []
    
    for phrase, expected_cat in expected.items():
        found_cat = None
        for cat, items in categories.items():
            if any(item["phrase"].lower() == phrase.lower() for item in items):
                found_cat = cat
                break
        
        if found_cat:
            if found_cat == expected_cat:
                successes.append(f"✅ '{phrase}' → {found_cat} (correct)")
            else:
                issues.append(f"❌ '{phrase}' → Expected: {expected_cat}, Got: {found_cat}")
        else:
            issues.append(f"⚠️  '{phrase}' → Not found in results")
    
    # Print results
    print(f"\n📊 Summary: {len(successes)} correct, {len(issues)} issues")
    
    if successes:
        print("\n✅ CORRECT CATEGORIZATIONS:")
        for success in successes[:10]:
            print(f"   {success}")
        if len(successes) > 10:
            print(f"   ... and {len(successes) - 10} more")
    
    if issues:
        print("\n❌ ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
    
    return len(issues) == 0


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("🧪 TASK 1: KEYWORD CATEGORIZATION TEST SUITE")
    print("="*80)
    
    # Test 1: Manual test keywords with known expectations
    print("\n" + "="*80)
    print("TEST 1: MANUAL TEST KEYWORDS")
    print("="*80)
    
    categories_manual = test_keyword_categorization(
        scraped_product=MOCK_PRODUCT_SLICES,
        base_relevancy_scores=TEST_KEYWORDS,
        test_name="Manual Test Keywords with Expected Categories"
    )
    
    # Validate expectations
    expected_categories = {
        # Relevant
        "freeze dried strawberry slices": "Relevant",
        "dried strawberry slices": "Relevant",
        "organic strawberry slices": "Relevant",
        
        # Design-Specific
        "bulk strawberry slices": "Design-Specific",
        "organic slices": "Design-Specific",
        
        # Irrelevant (different forms)
        "freeze dried strawberry powder": "Irrelevant",
        "strawberry powder": "Irrelevant",
        "whole strawberries": "Irrelevant",
        "strawberry juice": "Irrelevant",
        
        # Irrelevant (no context)
        "strawberry life": "Irrelevant",
        "how to make strawberry": "Irrelevant",
        
        # Branded
        "anthony's freeze dried strawberries": "Branded",
        "so natural freeze dried fruit": "Branded",
        "trader joe's organic strawberries": "Branded",
        "nutristore strawberry slices": "Branded",
    }
    
    all_valid = validate_categorization(categories_manual, expected_categories)
    
    # Test 2: Real CSV data - Revenue
    print("\n" + "="*80)
    print("TEST 2: REAL CSV DATA - REVENUE KEYWORDS")
    print("="*80)
    
    csv_revenue_path = Path(__file__).parent / "csv" / "Freeze dried strawberry top revenue.csv"
    if csv_revenue_path.exists():
        revenue_keywords = load_csv_keywords(str(csv_revenue_path), limit=30)
        categories_revenue = test_keyword_categorization(
            scraped_product=MOCK_PRODUCT_SLICES,
            base_relevancy_scores=revenue_keywords,
            test_name="Real Revenue CSV Keywords"
        )
    else:
        print(f"⚠️  CSV not found: {csv_revenue_path}")
    
    # Test 3: Real CSV data - Design
    print("\n" + "="*80)
    print("TEST 3: REAL CSV DATA - DESIGN KEYWORDS")
    print("="*80)
    
    csv_design_path = Path(__file__).parent / "csv" / "freeze dried strawberry relevant designs.csv"
    if csv_design_path.exists():
        design_keywords = load_csv_keywords(str(csv_design_path), limit=30)
        categories_design = test_keyword_categorization(
            scraped_product=MOCK_PRODUCT_SLICES,
            base_relevancy_scores=design_keywords,
            test_name="Real Design CSV Keywords"
        )
    else:
        print(f"⚠️  CSV not found: {csv_design_path}")
    
    # Final summary
    print("\n" + "="*80)
    print("🏁 TEST SUITE COMPLETE")
    print("="*80)
    
    if all_valid:
        print("\n✅ ALL TESTS PASSED!")
        print("   Task 1 implementation is working correctly.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("   Review the issues above and adjust categorization logic.")
    
    print("\n💡 Next Steps:")
    print("   1. Review categorization results above")
    print("   2. Check if product form extraction worked")
    print("   3. Verify brand detection is accurate")
    print("   4. Look for any miscategorized keywords")
    print("\n")


if __name__ == "__main__":
    main()



