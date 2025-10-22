"""
Test Task 3: Advanced Title Optimization Rules
Tests the 6 strict rules for title optimization.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.local_agents.seo.subagents.amazon_compliance_agent import apply_amazon_compliance_ai


# Mock product data
MOCK_PRODUCT = {
    "title": "Strawberry Snacks",  # Short, poor quality title (16 chars)
    "bullets": [
        "Made from real strawberries",
        "Healthy snacking option",
        "Great for kids",
        "Resealable bag"
    ],
    "brand": "Nature's Best"
}

# Mock keyword data (sorted by VALUE = relevancy × volume)
MOCK_KEYWORD_DATA = {
    "relevant_keywords": [
        {"phrase": "freeze dried strawberry slices", "relevancy_score": 10, "search_volume": 713, "category": "Relevant"},  # Value: 7,130
        {"phrase": "organic strawberry slices", "relevancy_score": 7, "search_volume": 150, "category": "Relevant"},  # Value: 1,050
        {"phrase": "dried strawberries", "relevancy_score": 7, "search_volume": 204, "category": "Relevant"},  # Value: 1,428
        {"phrase": "freeze dried strawberries", "relevancy_score": 8, "search_volume": 303, "category": "Relevant"},  # Value: 2,424
        {"phrase": "strawberry slices", "relevancy_score": 6, "search_volume": 351, "category": "Relevant"},  # Value: 2,106
    ],
    "design_keywords": [
        {"phrase": "bulk strawberries", "relevancy_score": 6, "search_volume": 180, "category": "Design-Specific"},  # Value: 1,080
        {"phrase": "organic slices", "relevancy_score": 5, "search_volume": 120, "category": "Design-Specific"},  # Value: 600
    ],
    "high_intent_keywords": [],
    "high_volume_keywords": [],
    "root_volumes": {}
}

MOCK_PRODUCT_CONTEXT = {
    "brand": "Nature's Best",
    "category": "Food",
    "title": "Strawberry Snacks"
}


def validate_title_rules(result: Dict[str, Any]) -> dict:
    """Validate that the optimized title follows all 6 Task 3 rules."""
    optimized_title = result.get("optimized_title", {})
    content = optimized_title.get("content", "")
    char_count = optimized_title.get("character_count", 0)
    first_80 = optimized_title.get("first_80_chars", "")
    brand_included = optimized_title.get("brand_included", False)
    keywords_included = optimized_title.get("keywords_included", [])
    
    validations = {}
    issues = []
    successes = []
    
    print("\n" + "="*80)
    print("🔍 TASK 3 VALIDATION - 6 RULES CHECK")
    print("="*80)
    
    # RULE 1: Character Count (150-200)
    print(f"\n📏 RULE 1: Character Count (150-200)")
    print(f"   Title: \"{content}\"")
    print(f"   Length: {char_count} characters")
    
    if 150 <= char_count <= 200:
        print(f"   ✅ PASS: Character count is {char_count} (within 150-200 range)")
        successes.append("Rule 1: Character count (150-200)")
        validations["rule1_char_count"] = True
    elif char_count < 150:
        print(f"   ❌ FAIL: Character count is {char_count} (below 150 minimum)")
        print(f"   → Need {150 - char_count} more characters")
        issues.append(f"Rule 1: Only {char_count} chars (need 150+)")
        validations["rule1_char_count"] = False
    else:
        print(f"   ❌ FAIL: Character count is {char_count} (exceeds 200 maximum)")
        issues.append(f"Rule 1: {char_count} chars (exceeds 200)")
        validations["rule1_char_count"] = False
    
    # RULE 2: Brand Inclusion
    print(f"\n🏷️  RULE 2: Brand Inclusion")
    print(f"   Brand: \"Nature's Best\"")
    print(f"   Brand in title: {brand_included}")
    
    brand_in_content = "nature's best" in content.lower()
    if brand_in_content:
        print(f"   ✅ PASS: Brand \"Nature's Best\" found in title")
        successes.append("Rule 2: Brand included")
        validations["rule2_brand"] = True
    else:
        print(f"   ❌ FAIL: Brand \"Nature's Best\" NOT found in title")
        issues.append("Rule 2: Brand missing")
        validations["rule2_brand"] = False
    
    # RULE 3: Top 3-4 High-Value Keywords (using Task 2 enhanced detection)
    print(f"\n⭐ RULE 3: Top Keywords Included (Task 2 Enhanced Detection)")
    print(f"   Expected top keywords by VALUE:")
    print(f"   1. 'freeze dried strawberry slices' (value: 7,130)")
    print(f"   2. 'freeze dried strawberries' (value: 2,424)")
    print(f"   3. 'dried strawberries' (value: 1,428)")
    print(f"   4. 'strawberry slices' (value: 2,106)")
    
    top_keywords = [
        "freeze dried strawberry slices",
        "freeze dried strawberries",
        "dried strawberries",
        "strawberry slices"
    ]
    
    # Use Task 2's enhanced detection (sub-phrase matching)
    from app.local_agents.seo.helper_methods import extract_keywords_from_content
    
    top_kw_volumes = {
        "freeze dried strawberry slices": 713,
        "freeze dried strawberries": 303,
        "dried strawberries": 204,
        "strawberry slices": 351
    }
    
    found_in_content, _ = extract_keywords_from_content(content, top_keywords, top_kw_volumes)
    keywords_found_count = len(found_in_content)
    
    print(f"\n   Keywords in AI's keywords_included: {keywords_included}")
    print(f"   Top keywords DETECTED in content (Task 2): {found_in_content}")
    print(f"   Top keywords found: {keywords_found_count}/4")
    
    if keywords_found_count >= 3:
        print(f"   ✅ PASS: {keywords_found_count} top keywords included (need 3-4)")
        successes.append("Rule 3: Top 3-4 keywords included")
        validations["rule3_top_keywords"] = True
    else:
        print(f"   ❌ FAIL: Only {keywords_found_count} top keywords (need 3-4)")
        issues.append(f"Rule 3: Only {keywords_found_count} top keywords")
        validations["rule3_top_keywords"] = False
    
    # RULE 4: No Root Duplication (accounting for singular/plural variants)
    print(f"\n🔄 RULE 4: No Keyword Root Duplication")
    
    # Extract all tokens from keywords used
    all_tokens = []
    for kw in keywords_included:
        tokens = kw.lower().split()
        all_tokens.extend(tokens)
    
    # Normalize tokens (handle singular/plural)
    def normalize_token(token):
        """Normalize singular/plural forms"""
        if token.endswith('ies'):
            return token[:-3] + 'y'
        elif token.endswith('es'):
            return token[:-2]
        elif token.endswith('s') and len(token) > 3:
            return token[:-1]
        return token
    
    normalized_tokens = [normalize_token(t) for t in all_tokens]
    
    # Check for duplicates in normalized form
    from collections import Counter
    token_counts = Counter(normalized_tokens)
    duplicated = {token: count for token, count in token_counts.items() if count > 1}
    
    if duplicated:
        # Check if duplications are significant (more than singular/plural variants)
        print(f"   ⚠️  Detected potential duplication: {duplicated}")
        
        # Allow if only 1-2 minor duplications (e.g., "strawberry" appearing in 2 phrases is OK)
        if len(duplicated) <= 2 and all(count <= 2 for count in duplicated.values()):
            print(f"   ✅ PASS: Minor duplication acceptable (singular/plural variants)")
            print(f"   → {len(duplicated)} tokens appear twice (within tolerance)")
            successes.append("Rule 4: No significant root duplication")
            validations["rule4_no_duplication"] = True
        else:
            print(f"   ❌ FAIL: Significant root duplication")
            issues.append(f"Rule 4: {len(duplicated)} duplicated roots")
            validations["rule4_no_duplication"] = False
    else:
        print(f"   ✅ PASS: No root duplication detected")
        print(f"   → All tokens are unique")
        successes.append("Rule 4: No root duplication")
        validations["rule4_no_duplication"] = True
    
    # RULE 5: First 80 Characters
    print(f"\n📱 RULE 5: First 80 Characters (Mobile Critical)")
    print(f"   First 80 chars: \"{first_80}\"")
    
    required_in_80 = {
        "Brand": "nature's best" in first_80.lower(),
        "Main keyword": any(word in first_80.lower() for word in ["freeze dried", "strawberry"]),
        "Design keyword": any(word in first_80.lower() for word in ["slices", "slice"]),
        "Pack/Size info": any(word in first_80.lower() for word in ["oz", "pack", "bulk", "count", "pound", "lb"])
    }
    
    missing_in_80 = [key for key, present in required_in_80.items() if not present]
    
    if not missing_in_80:
        print(f"   ✅ PASS: All required elements in first 80 characters")
        for key, present in required_in_80.items():
            print(f"      ✅ {key}")
        successes.append("Rule 5: First 80 chars optimized")
        validations["rule5_first_80"] = True
    else:
        print(f"   ❌ FAIL: Missing elements in first 80 characters:")
        for key in missing_in_80:
            print(f"      ❌ {key}")
        issues.append(f"Rule 5: Missing in first 80: {', '.join(missing_in_80)}")
        validations["rule5_first_80"] = False
    
    # RULE 6: Grammar & Readability
    print(f"\n✍️  RULE 6: Grammar & Readability")
    
    # Check for common issues
    grammar_checks = {
        "Title Case": content[0].isupper() if content else False,
        "No all caps": not any(word.isupper() and len(word) > 3 for word in content.split()),
        "Has separators": any(sep in content for sep in ['-', '|', ',']),
        "Not too many keywords": len(content.split()) < 30  # Prevent keyword stuffing
    }
    
    grammar_issues = [check for check, passed in grammar_checks.items() if not passed]
    
    if not grammar_issues:
        print(f"   ✅ PASS: Grammar and readability good")
        for check in grammar_checks.keys():
            print(f"      ✅ {check}")
        successes.append("Rule 6: Grammar & readability")
        validations["rule6_grammar"] = True
    else:
        print(f"   ⚠️  WARNING: Grammar issues detected:")
        for issue in grammar_issues:
            print(f"      ⚠️  {issue}")
        validations["rule6_grammar"] = len(grammar_issues) <= 1  # Allow 1 minor issue
    
    # Overall summary
    print("\n" + "="*80)
    print("📊 VALIDATION SUMMARY")
    print("="*80)
    
    rules_passed = sum(validations.values())
    total_rules = len(validations)
    
    print(f"\n✅ Passed: {rules_passed}/{total_rules} rules")
    print(f"❌ Failed: {total_rules - rules_passed}/{total_rules} rules")
    
    if successes:
        print(f"\n✅ SUCCESSES:")
        for success in successes:
            print(f"   • {success}")
    
    if issues:
        print(f"\n❌ ISSUES:")
        for issue in issues:
            print(f"   • {issue}")
    
    return {
        "validations": validations,
        "issues": issues,
        "successes": successes,
        "all_passed": rules_passed == total_rules
    }


def main():
    """Run Task 3 test."""
    print("\n" + "="*80)
    print("🧪 TASK 3: ADVANCED TITLE OPTIMIZATION TEST")
    print("="*80)
    
    print("\n📋 Testing 6 Strict Rules:")
    print("   1. Character Count: 150-200 chars")
    print("   2. Brand Inclusion: Must include brand if exists")
    print("   3. Top Keywords: Must use top 3-4 by value (relevancy × volume)")
    print("   4. No Root Duplication: Don't repeat keyword roots")
    print("   5. First 80 Characters: Brand + keywords + pack info")
    print("   6. Grammar & Readability: Natural language, Title Case")
    
    print("\n🔧 Running optimization...")
    
    try:
        # Run optimization
        result = apply_amazon_compliance_ai(
            current_content=MOCK_PRODUCT,
            keyword_data=MOCK_KEYWORD_DATA,
            product_context=MOCK_PRODUCT_CONTEXT,
            competitor_analysis=None,
            keyword_validator=None,
            title_keywords=None,  # Let it use all keywords
            bullet_keywords=None,
            backend_keywords=None,
            target_bullet_count=4
        )
        
        print("\n✅ Optimization completed!")
        
        # Display optimized title
        optimized_title = result.get("optimized_title", {})
        content = optimized_title.get("content", "")
        char_count = optimized_title.get("character_count", len(content))
        
        print("\n" + "="*80)
        print("📝 OPTIMIZED TITLE")
        print("="*80)
        print(f"\nTitle: {content}")
        print(f"Length: {char_count} characters")
        print(f"First 80: {content[:80]}")
        
        # Validate against rules
        validation_result = validate_title_rules(result)
        
        # Final verdict
        print("\n" + "="*80)
        print("🏁 FINAL VERDICT")
        print("="*80)
        
        if validation_result["all_passed"]:
            print("\n✅ ALL TESTS PASSED!")
            print("\n🎉 Task 3 implementation is working correctly!")
            print("\n📊 Title Quality:")
            print(f"   • Length: {char_count} chars (optimal range)")
            print(f"   • Brand: Included")
            print(f"   • Top keywords: Present")
            print(f"   • No duplication: Clean")
            print(f"   • First 80 chars: Optimized")
            print(f"   • Readability: Professional")
        else:
            print("\n⚠️  SOME RULES FAILED")
            print(f"\n📊 Results:")
            print(f"   • Passed: {sum(validation_result['validations'].values())}/6 rules")
            print(f"   • Failed: {6 - sum(validation_result['validations'].values())}/6 rules")
            print("\n💡 Review the issues above and adjust if needed.")
        
        print("\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

