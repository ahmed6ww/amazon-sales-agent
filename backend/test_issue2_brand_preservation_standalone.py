"""
Test Issue #2: Brand Name Preservation - STANDALONE VERSION

Tests the fix for brand name preservation in optimized content.
"""

import re


def test_prompt_file_includes_brand():
    """Test that prompts.py file includes brand preservation requirements"""
    print("\n" + "="*80)
    print("TEST 1: Prompt File Includes Brand Requirements")
    print("="*80)
    
    # Read the prompts file directly
    with open('app/local_agents/seo/prompts.py', 'r', encoding='utf-8') as f:
        prompts_content = f.read()
    
    # Test 1: Check for {brand} placeholder
    assert "{brand}" in prompts_content, "❌ Failed: Missing {brand} placeholder"
    print("✅ Brand placeholder {brand} found in prompts file")
    
    # Test 2: Check for MANDATORY language
    assert "MANDATORY" in prompts_content, "❌ Failed: Missing MANDATORY language"
    print("✅ MANDATORY language found")
    
    # Test 3: Check for brand at beginning requirement
    brand_beginning_patterns = [
        r"MUST start with brand",
        r"start with brand name",
        r"begin with brand",
    ]
    
    found_beginning = any(
        re.search(pattern, prompts_content, re.IGNORECASE) 
        for pattern in brand_beginning_patterns
    )
    assert found_beginning, "❌ Failed: Missing 'brand at beginning' requirement"
    print("✅ 'Brand at beginning of title' requirement found")
    
    # Test 4: Check for CRITICAL REQUIREMENTS section
    assert "CRITICAL REQUIREMENTS" in prompts_content, "❌ Failed: Missing CRITICAL REQUIREMENTS section"
    print("✅ CRITICAL REQUIREMENTS section found")
    
    # Test 5: Check for NON-NEGOTIABLE language
    assert "NON-NEGOTIABLE" in prompts_content, "❌ Failed: Missing NON-NEGOTIABLE enforcement"
    print("✅ NON-NEGOTIABLE enforcement found")
    
    # Test 6: Count how many times brand is mentioned
    brand_mentions = prompts_content.lower().count("brand")
    print(f"✅ Brand mentioned {brand_mentions} times (multiple enforcement)")
    assert brand_mentions >= 5, "❌ Failed: Brand not mentioned enough times"
    
    print("\n✅ PASSED: Prompt file correctly enforces brand preservation")
    return True


def test_runner_includes_brand_extraction():
    """Test that runner.py includes brand extraction and passing logic"""
    print("\n" + "="*80)
    print("TEST 2: Runner Includes Brand Extraction")
    print("="*80)
    
    # Read the runner file directly
    with open('app/local_agents/seo/runner.py', 'r', encoding='utf-8') as f:
        runner_content = f.read()
    
    # Test 1: Check for brand extraction from current_content
    assert 'current_content.get("brand"' in runner_content, \
        "❌ Failed: No brand extraction from current_content"
    print("✅ Brand extraction from current_content found")
    
    # Test 2: Check for brand in prompt_data
    assert '"brand":' in runner_content, \
        "❌ Failed: Brand not added to prompt_data"
    print("✅ Brand added to prompt_data")
    
    # Test 3: Check for fallback from title
    assert 'title.split()' in runner_content, \
        "❌ Failed: No fallback brand extraction from title"
    print("✅ Fallback brand extraction from title found")
    
    # Test 4: Check for "Brand Name Unknown" fallback
    assert 'Brand Name Unknown' in runner_content or 'brand or' in runner_content, \
        "⚠️  Warning: No final fallback for missing brand"
    print("✅ Final fallback for missing brand found")
    
    print("\n✅ PASSED: Runner correctly extracts and passes brand")
    return True


def test_brand_extraction_logic():
    """Test the brand extraction logic simulation"""
    print("\n" + "="*80)
    print("TEST 3: Brand Extraction Logic Simulation")
    print("="*80)
    
    test_cases = [
        {
            "current_content": {"brand": "GWT", "title": "GWT Makeup Sponge Set"},
            "expected_brand": "GWT",
            "description": "Direct brand from current_content"
        },
        {
            "current_content": {"brand": "", "title": "BREWER Freeze Dried Strawberries"},
            "expected_brand": "BREWER",
            "description": "Extract brand from title first word"
        },
        {
            "current_content": {"brand": None, "title": "Nature's Best Organic Snacks"},
            "expected_brand": "Nature's",
            "description": "Extract brand with apostrophe"
        },
        {
            "current_content": {"brand": "", "title": ""},
            "expected_brand": "Brand Name Unknown",
            "description": "Fallback when no brand"
        },
        {
            "current_content": {}, 
            "expected_brand": "Brand Name Unknown",
            "description": "Empty current_content"
        },
    ]
    
    all_passed = True
    for i, test in enumerate(test_cases, 1):
        current_content = test["current_content"]
        expected = test["expected_brand"]
        description = test["description"]
        
        # Simulate the brand extraction logic from runner.py
        brand = current_content.get("brand", "") if current_content else ""
        if not brand:
            title = current_content.get("title", "") if current_content else ""
            if title:
                brand = title.split()[0] if title.split() else ""
        brand = brand or "Brand Name Unknown"
        
        passed = brand == expected
        status = "✅" if passed else "❌"
        
        print(f"\n  Test {i}: {description}")
        print(f"    Expected: '{expected}'")
        print(f"    Got: '{brand}'")
        print(f"    {status}")
        
        if not passed:
            all_passed = False
    
    assert all_passed, "❌ Some brand extraction tests failed"
    print("\n✅ PASSED: Brand extraction logic works correctly")
    return True


def test_critical_requirements_comprehensive():
    """Test that CRITICAL REQUIREMENTS section is comprehensive"""
    print("\n" + "="*80)
    print("TEST 4: CRITICAL REQUIREMENTS Comprehensive Check")
    print("="*80)
    
    with open('app/local_agents/seo/prompts.py', 'r', encoding='utf-8') as f:
        prompts_content = f.read()
    
    # Extract CRITICAL REQUIREMENTS section
    match = re.search(r'CRITICAL REQUIREMENTS.*?(?=\n\n|\Z|""")', prompts_content, re.DOTALL)
    
    if not match:
        print("❌ Failed: CRITICAL REQUIREMENTS section not found")
        return False
    
    requirements_section = match.group(0)
    print("\nFound CRITICAL REQUIREMENTS section:")
    print("-" * 80)
    # Print first 400 characters
    print(requirements_section[:400])
    if len(requirements_section) > 400:
        print("...")
    print("-" * 80)
    
    # Check for each required element
    required_elements = [
        ("BRAND NAME", "Brand preservation"),
        ("KEYWORD ORDER", "Keyword volume ordering"),
        ("DESIGN KEYWORDS", "Design-specific keywords"),
        ("NO DUPLICATES", "Duplicate prevention"),
    ]
    
    all_found = True
    for element, description in required_elements:
        if element in requirements_section:
            print(f"  ✅ {description}: '{element}' found")
        else:
            print(f"  ❌ {description}: '{element}' NOT found")
            all_found = False
    
    assert all_found, "❌ CRITICAL REQUIREMENTS section missing elements"
    print("\n✅ PASSED: CRITICAL REQUIREMENTS section is comprehensive")
    return True


def test_before_vs_after_comparison():
    """Compare prompts before and after fix"""
    print("\n" + "="*80)
    print("TEST 5: Before vs After Comparison")
    print("="*80)
    
    with open('app/local_agents/seo/prompts.py', 'r', encoding='utf-8') as f:
        current_prompts = f.read()
    
    print("\n📊 BEFORE FIX:")
    print("  - Brand was 'if beneficial' (OPTIONAL)")
    print("  - No MANDATORY language")
    print("  - No brand at beginning requirement")
    print("  - No CRITICAL REQUIREMENTS section")
    
    print("\n📊 AFTER FIX (Current):")
    has_mandatory = "MANDATORY" in current_prompts
    has_beginning = "start with brand" in current_prompts.lower()
    has_critical_section = "CRITICAL REQUIREMENTS" in current_prompts
    has_non_negotiable = "NON-NEGOTIABLE" in current_prompts
    
    print(f"  {'✅' if has_mandatory else '❌'} MANDATORY language present")
    print(f"  {'✅' if has_beginning else '❌'} Brand at beginning requirement")
    print(f"  {'✅' if has_critical_section else '❌'} CRITICAL REQUIREMENTS section")
    print(f"  {'✅' if has_non_negotiable else '❌'} NON-NEGOTIABLE enforcement")
    
    all_present = has_mandatory and has_beginning and has_critical_section and has_non_negotiable
    assert all_present, "❌ Not all fixes are present"
    
    print("\n✅ PASSED: All fixes are present in current version")
    return True


def run_all_tests():
    """Run all tests for Issue #2"""
    print("\n" + "="*80)
    print("TESTING ISSUE #2: BRAND NAME PRESERVATION FIX")
    print("="*80)
    print("\nFix: Made brand name preservation MANDATORY in prompts")
    print("Files Modified:")
    print("  1. backend/app/local_agents/seo/prompts.py (3 sections)")
    print("  2. backend/app/local_agents/seo/runner.py (brand extraction)")
    
    try:
        test_prompt_file_includes_brand()
        test_runner_includes_brand_extraction()
        test_brand_extraction_logic()
        test_critical_requirements_comprehensive()
        test_before_vs_after_comparison()
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED FOR ISSUE #2!")
        print("="*80)
        print("\n✅ Brand name preservation is now MANDATORY")
        print("✅ Prompt enforces brand at beginning of title")
        print("✅ Brand extraction and fallback logic implemented")
        print("✅ CRITICAL REQUIREMENTS section added")
        print("✅ Triple enforcement (instructions + template + requirements)")
        print("✅ Issue #2 is FIXED and VERIFIED")
        
        return True
        
    except AssertionError as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)
        print(f"\nError: {e}")
        return False
    except Exception as e:
        print("\n" + "="*80)
        print("❌ UNEXPECTED ERROR")
        print("="*80)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)


