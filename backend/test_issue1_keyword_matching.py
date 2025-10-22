"""
Test Issue #1: False Keyword Matching (Word-Boundary Fix)

Tests the fix for substring matching issue where keywords were incorrectly
matched when words appeared separated in the content.

Example Problem:
- Keyword: "make up sponges foundation"
- Content: "make up blending sponges for foundation"
- Before Fix: MATCHED (incorrect - substring match)
- After Fix: NOT MATCHED (correct - word-boundary match)
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.local_agents.seo.helper_methods import extract_keywords_from_content


def test_exact_phrase_match():
    """Test that exact phrase matches work correctly"""
    print("\n" + "="*80)
    print("TEST 1: Exact Phrase Matching")
    print("="*80)
    
    content = "GWT Makeup Sponge Set, 6 Pcs Latex-Free Beauty Blender Sponges for Foundation"
    keywords = [
        "makeup sponge",
        "latex-free",
        "beauty blender",
        "sponges for foundation",
    ]
    
    found, total_volume = extract_keywords_from_content(content, keywords)
    
    print(f"Content: {content}")
    print(f"Keywords to find: {keywords}")
    print(f"Found: {found}")
    
    # All should be found (exact matches)
    assert "makeup sponge" in found, "❌ Failed: 'makeup sponge' should match"
    assert "latex-free" in found, "❌ Failed: 'latex-free' should match"
    assert "beauty blender" in found, "❌ Failed: 'beauty blender' should match"
    assert "sponges for foundation" in found, "❌ Failed: 'sponges for foundation' should match"
    
    print("✅ PASSED: All exact phrases matched correctly")
    return True


def test_false_substring_rejection():
    """Test that false substring matches are rejected"""
    print("\n" + "="*80)
    print("TEST 2: False Substring Rejection (Issue #1 - Core Test)")
    print("="*80)
    
    content = "GWT Makeup Sponge Set, 6 Pcs Beauty Blender Sponges for Foundation, Liquid & Cream"
    keywords = [
        "make up sponges foundation",  # Words separated by "blender" and "for"
        "makeup sponge foundation",    # Words separated
        "beauty sponges liquid",       # Words separated by "for foundation,"
    ]
    
    found, total_volume = extract_keywords_from_content(content, keywords)
    
    print(f"Content: {content}")
    print(f"Keywords to test (should NOT match): {keywords}")
    print(f"Found: {found}")
    
    # None should be found (false substring matches)
    assert "make up sponges foundation" not in found, "❌ Failed: False match detected for 'make up sponges foundation'"
    assert "makeup sponge foundation" not in found, "❌ Failed: False match detected for 'makeup sponge foundation'"
    assert "beauty sponges liquid" not in found, "❌ Failed: False match detected for 'beauty sponges liquid'"
    
    print("✅ PASSED: All false substring matches correctly rejected")
    return True


def test_word_boundary_cases():
    """Test various word boundary edge cases"""
    print("\n" + "="*80)
    print("TEST 3: Word Boundary Edge Cases")
    print("="*80)
    
    test_cases = [
        {
            "content": "makeup sponges for foundation",
            "keyword": "makeup sponge",
            "should_match": False,  # "sponge" vs "sponges" - different word
            "reason": "Singular vs plural without plural handling in METHOD 1"
        },
        {
            "content": "the makeup sponge is great",
            "keyword": "makeup sponge",
            "should_match": True,
            "reason": "Exact phrase with word boundaries"
        },
        {
            "content": "buy makeup-sponge set",
            "keyword": "makeup sponge",
            "should_match": False,  # Hyphen vs space
            "reason": "Hyphen vs space - different"
        },
        {
            "content": "best makeup sponge",
            "keyword": "makeup",
            "should_match": True,
            "reason": "Single word match"
        },
        {
            "content": "makeups sponge",
            "keyword": "makeup",
            "should_match": False,  # "makeups" contains "makeup" but different word
            "reason": "Word boundary prevents partial word match"
        },
    ]
    
    all_passed = True
    for i, test in enumerate(test_cases, 1):
        content = test["content"]
        keyword = test["keyword"]
        should_match = test["should_match"]
        reason = test["reason"]
        
        found, _ = extract_keywords_from_content(content, [keyword])
        matched = keyword in found
        
        print(f"\n  Test {i}:")
        print(f"    Content: '{content}'")
        print(f"    Keyword: '{keyword}'")
        print(f"    Expected: {'MATCH' if should_match else 'NO MATCH'}")
        print(f"    Result: {'MATCH' if matched else 'NO MATCH'}")
        print(f"    Reason: {reason}")
        
        if matched == should_match:
            print(f"    ✅ PASSED")
        else:
            print(f"    ❌ FAILED")
            all_passed = False
    
    assert all_passed, "❌ Some word boundary tests failed"
    print("\n✅ PASSED: All word boundary edge cases handled correctly")
    return True


def test_real_world_example():
    """Test with real-world Amazon listing content"""
    print("\n" + "="*80)
    print("TEST 4: Real-World Amazon Listing Example")
    print("="*80)
    
    # Real content from makeup sponge listing
    content = """
    GWT Makeup Sponge Set, 6 Pcs Latex-Free Beauty Blender Sponges for Foundation, 
    Liquid & Cream, Ultra-Soft Wonder Sponges, Multi-Angle Blending, 
    Ideal Stocking Stuffers for Women
    """
    
    # Keywords that SHOULD match
    should_match = [
        "makeup sponge",
        "latex-free",
        "beauty blender",
        "sponges for foundation",
        "ultra-soft",
        "multi-angle",
    ]
    
    # Keywords that should NOT match (false substrings)
    should_not_match = [
        "make up sponges foundation",  # Words separated
        "latex free beauty",            # Words separated by "blender"
        "soft wonder sponges",          # Words separated by punctuation
        "blending ideal",               # Words separated
    ]
    
    found, _ = extract_keywords_from_content(content, should_match + should_not_match)
    
    print("Content (excerpt):")
    print(f"  {content[:100]}...")
    
    print("\nKeywords that SHOULD match:")
    for kw in should_match:
        matched = kw in found
        status = "✅" if matched else "❌"
        print(f"  {status} '{kw}': {'FOUND' if matched else 'NOT FOUND'}")
        assert matched, f"❌ Failed: '{kw}' should have matched"
    
    print("\nKeywords that should NOT match:")
    for kw in should_not_match:
        matched = kw in found
        status = "✅" if not matched else "❌"
        print(f"  {status} '{kw}': {'NOT FOUND' if not matched else 'INCORRECTLY FOUND'}")
        assert not matched, f"❌ Failed: '{kw}' should NOT have matched (false substring)"
    
    print("\n✅ PASSED: Real-world example works correctly")
    return True


def run_all_tests():
    """Run all tests for Issue #1"""
    print("\n" + "="*80)
    print("TESTING ISSUE #1: FALSE KEYWORD MATCHING FIX")
    print("="*80)
    print("\nFix: Changed from substring matching to word-boundary regex matching")
    print("File: backend/app/local_agents/seo/helper_methods.py (Line 60)")
    
    try:
        test_exact_phrase_match()
        test_false_substring_rejection()
        test_word_boundary_cases()
        test_real_world_example()
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED FOR ISSUE #1!")
        print("="*80)
        print("\n✅ Word-boundary matching is working correctly")
        print("✅ False substring matches are properly rejected")
        print("✅ Issue #1 is FIXED and VERIFIED")
        
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
    success = run_all_tests()
    sys.exit(0 if success else 1)


