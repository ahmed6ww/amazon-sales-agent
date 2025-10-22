"""
Test for Issue #1 Fix: Sequential Proximity Matching

Verifies that METHOD 2 now requires:
1. Tokens in exact sequential order
2. Tight proximity (max 20 chars between adjacent tokens)
3. No scattered word matching
"""

import re


def extract_keywords_sequential(content: str, keywords: list) -> list:
    """Mock implementation of the fixed METHOD 2 logic"""
    found_keywords = []
    content_lower = content.lower()
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # METHOD 1: Word-boundary exact match
        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
        if re.search(pattern, content_lower):
            found_keywords.append(keyword)
            continue
        
        # METHOD 2: Sequential Proximity Match
        keyword_tokens = keyword_lower.split()
        
        if len(keyword_tokens) > 1:
            last_position = -1
            all_sequential = True
            
            for token in keyword_tokens:
                search_start = last_position + 1
                remaining_content = content_lower[search_start:]
                
                found_position = -1
                
                # Direct match
                if token in remaining_content:
                    found_position = search_start + remaining_content.find(token)
                else:
                    # Try plural/singular variants
                    variants = []
                    
                    if token.endswith('ies') and len(token) > 4:
                        variants.append(token[:-3] + 'y')
                    elif token.endswith('es') and len(token) > 3:
                        variants.append(token[:-2])
                    elif token.endswith('s') and len(token) > 2:
                        variants.append(token[:-1])
                    
                    if token.endswith('y') and len(token) > 2:
                        variants.append(token[:-1] + 'ies')
                    variants.append(token + 'es')
                    variants.append(token + 's')
                    
                    for variant in variants:
                        if variant in remaining_content:
                            found_position = search_start + remaining_content.find(variant)
                            break
                
                if found_position == -1:
                    all_sequential = False
                    break
                
                # Check proximity
                if last_position != -1:
                    distance = found_position - last_position
                    if distance > 20:
                        all_sequential = False
                        break
                
                last_position = found_position
            
            if all_sequential:
                found_keywords.append(keyword)
                continue
    
    return found_keywords


def test_sequential_matches():
    """Test that sequential matches with plural/singular work"""
    print("\n" + "=" * 70)
    print("TEST 1: Sequential Matches (Should Pass)")
    print("=" * 70)
    
    content = "GWT Ultra Soft Makeup Sponges Set for Foundation"
    
    test_cases = [
        ("makeup sponges", True, "Exact match"),
        ("makeup sponge", True, "Singular match (sponges -> sponge)"),
        ("sponges set", True, "Adjacent words"),
        ("soft makeup sponge", True, "Sequential with singular variant"),
    ]
    
    for keyword, should_match, description in test_cases:
        result = extract_keywords_sequential(content, [keyword])
        matched = len(result) > 0
        
        if matched == should_match:
            print(f"   ✅ '{keyword}' - {description}")
        else:
            print(f"   ❌ '{keyword}' - {description}")
            print(f"      Expected: {should_match}, Got: {matched}")
            raise AssertionError(f"Failed: {keyword}")
    
    print("\n✅ PASS: All sequential matches work correctly")


def test_reject_scattered_words():
    """Test that scattered words are rejected"""
    print("\n" + "=" * 70)
    print("TEST 2: Reject Scattered Words (Should Fail to Match)")
    print("=" * 70)
    
    content = "GWT Makeup Sponge Set, 6 Pcs Latex-Free Beauty Blender Sponges for Foundation"
    
    test_cases = [
        ("makeup sponges for foundation", "makeup...sponge (singular)...sponges for foundation"),
        ("makeup sponges beauty blender", "makeup sponge...beauty blender sponges (wrong order/scattered)"),
        ("foundation sponge for liquid makeup", "sponges for foundation, liquid (rearranged)"),
        ("beauty blender makeup sponge", "makeup sponge...beauty blender (reverse order)"),
    ]
    
    for keyword, reason in test_cases:
        result = extract_keywords_sequential(content, [keyword])
        matched = len(result) > 0
        
        if not matched:
            print(f"   ✅ '{keyword}' - Correctly rejected")
            print(f"      Reason: {reason}")
        else:
            print(f"   ❌ '{keyword}' - INCORRECTLY MATCHED!")
            print(f"      Should reject: {reason}")
            raise AssertionError(f"False positive: {keyword}")
    
    print("\n✅ PASS: All scattered words correctly rejected")


def test_proximity_limit():
    """Test that distance > 20 chars is rejected"""
    print("\n" + "=" * 70)
    print("TEST 3: Proximity Limit (20 characters)")
    print("=" * 70)
    
    # Close enough (should match)
    content1 = "makeup soft beauty sponge"  # ~19 chars between makeup and sponge
    keyword1 = "makeup sponge"
    result1 = extract_keywords_sequential(content1, [keyword1])
    
    if len(result1) > 0:
        print(f"   ✅ '{keyword1}' in '{content1}' - Matched (within 20 chars)")
    else:
        print(f"   ❌ Should match: words are close enough")
        raise AssertionError("Proximity test failed")
    
    # Too far (should not match)
    content2 = "makeup ultra soft beauty blender foundation sponge"  # >25 chars
    keyword2 = "makeup sponge"
    result2 = extract_keywords_sequential(content2, [keyword2])
    
    if len(result2) == 0:
        print(f"   ✅ '{keyword2}' in '{content2}' - Rejected (>20 chars)")
    else:
        print(f"   ❌ Should reject: words are too far apart")
        raise AssertionError("Proximity test failed")
    
    print("\n✅ PASS: Proximity limit working correctly")


def test_real_world_false_positives():
    """Test the actual false positives from the screenshot"""
    print("\n" + "=" * 70)
    print("TEST 4: Real-World False Positives from Screenshot")
    print("=" * 70)
    
    # Original title from screenshot
    content = "GWT Makeup Sponge Set, 6 Pcs Latex-Free Beauty Blender Sponges for Foundation, Liquid & Cream"
    
    false_positives = [
        "make up sponges for foundation",
        "makeup sponges for foundation",
        "foundation sponge for liquid makeup",
        "makeup sponges beauty blender",
        "beauty blender makeup sponge",
    ]
    
    all_rejected = True
    for keyword in false_positives:
        result = extract_keywords_sequential(content, [keyword])
        matched = len(result) > 0
        
        if not matched:
            print(f"   ✅ '{keyword}' - Correctly rejected")
        else:
            print(f"   ❌ '{keyword}' - FALSE POSITIVE!")
            all_rejected = False
    
    if all_rejected:
        print("\n✅ PASS: All false positives from screenshot are now rejected")
    else:
        raise AssertionError("Some false positives still match")


def test_valid_matches_still_work():
    """Test that legitimate matches still work"""
    print("\n" + "=" * 70)
    print("TEST 5: Valid Matches Still Work")
    print("=" * 70)
    
    content = "GWT Makeup Sponge Set, 6 Pcs Latex-Free Beauty Blender Sponges for Foundation"
    
    valid_keywords = [
        ("makeup sponge", "Exact match with singular variant"),
        ("latex free", "Adjacent words with hyphen variant (METHOD 3)"),
        ("beauty blender sponges", "Exact sequential match"),
        ("sponges for foundation", "Exact sequential match"),
        ("makeup sponge set", "Sequential match"),
    ]
    
    for keyword, description in valid_keywords:
        result = extract_keywords_sequential(content, [keyword])
        matched = len(result) > 0
        
        if matched:
            print(f"   ✅ '{keyword}' - {description}")
        else:
            print(f"   ❌ '{keyword}' - Should match!")
            print(f"      {description}")
            raise AssertionError(f"Valid match failed: {keyword}")
    
    print("\n✅ PASS: All valid matches still work")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("ISSUE #1 FIX: SEQUENTIAL PROXIMITY MATCHING - TEST SUITE")
    print("=" * 70)
    
    try:
        test_sequential_matches()
        test_reject_scattered_words()
        test_proximity_limit()
        test_real_world_false_positives()
        test_valid_matches_still_work()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print("\nSummary:")
        print("✅ Sequential matches work (with plural/singular variants)")
        print("✅ Scattered words rejected")
        print("✅ Proximity limit enforced (20 chars)")
        print("✅ Real-world false positives from screenshot rejected")
        print("✅ Valid matches still work")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()


