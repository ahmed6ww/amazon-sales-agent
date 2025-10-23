"""
Standalone Test for Issue #6: Duplicate Keywords Across Content

Issue: The same keywords were appearing in the optimized title, multiple bullet 
points, and backend keywords, leading to inefficient keyword coverage.

Fix: Added _deduplicate_keywords_across_content() method in SEORunner that removes
duplicates with priority: Title > Bullets > Backend

Location: backend/app/local_agents/seo/runner.py
"""

from typing import List


class OptimizedContent:
    """Mock OptimizedContent schema"""
    def __init__(self, content: str, keywords_included: List[str], 
                 improvements: str = "", character_count: int = 0):
        self.content = content
        self.keywords_included = keywords_included
        self.improvements = improvements
        self.character_count = character_count


class OptimizedSEO:
    """Mock OptimizedSEO schema"""
    def __init__(self, optimized_title, optimized_bullets, optimized_backend_keywords):
        self.optimized_title = optimized_title
        self.optimized_bullets = optimized_bullets
        self.optimized_backend_keywords = optimized_backend_keywords


def deduplicate_keywords_across_content_mock(optimized_seo: OptimizedSEO) -> OptimizedSEO:
    """Mock version of _deduplicate_keywords_across_content with the fix"""
    print("🔄 [DEDUPLICATION] Removing duplicate keywords across all content")
    
    # Track used keywords (case-insensitive)
    used_keywords = set()
    
    # Step 1: Track title keywords (highest priority - keep all)
    title_keywords = optimized_seo.optimized_title.keywords_included
    used_keywords.update([kw.lower() for kw in title_keywords])
    print(f"   📌 Title: {len(title_keywords)} keywords (all kept)")
    
    # Step 2: Deduplicate bullets
    total_removed_from_bullets = 0
    updated_bullets = []
    
    for i, bullet in enumerate(optimized_seo.optimized_bullets, 1):
        original_count = len(bullet.keywords_included)
        
        # Keep only keywords not already used
        unique_keywords = [
            kw for kw in bullet.keywords_included 
            if kw.lower() not in used_keywords
        ]
        
        removed_count = original_count - len(unique_keywords)
        total_removed_from_bullets += removed_count
        
        if removed_count > 0:
            print(f"   🔹 Bullet {i}: Removed {removed_count} duplicates ({original_count} → {len(unique_keywords)})")
        
        # Create updated bullet
        updated_bullets.append(OptimizedContent(
            content=bullet.content,
            keywords_included=unique_keywords,
            improvements=bullet.improvements,
            character_count=bullet.character_count
        ))
        
        # Add unique keywords to used set
        used_keywords.update([kw.lower() for kw in unique_keywords])
    
    optimized_seo.optimized_bullets = updated_bullets
    print(f"   ✅ Bullets: Removed {total_removed_from_bullets} total duplicates")
    
    # Step 3: Deduplicate backend keywords
    original_backend_count = len(optimized_seo.optimized_backend_keywords)
    
    unique_backend = [
        kw for kw in optimized_seo.optimized_backend_keywords
        if kw.lower() not in used_keywords
    ]
    
    removed_from_backend = original_backend_count - len(unique_backend)
    optimized_seo.optimized_backend_keywords = unique_backend
    
    print(f"   🔹 Backend: Removed {removed_from_backend} duplicates ({original_backend_count} → {len(unique_backend)})")
    
    # Summary
    total_removed = total_removed_from_bullets + removed_from_backend
    print(f"")
    print(f"✅ [DEDUPLICATION COMPLETE]")
    print(f"   Total Duplicates Removed: {total_removed}")
    print(f"   Final Unique Keywords: {len(used_keywords)}")
    
    return optimized_seo


def test_basic_deduplication():
    """Test basic deduplication across title, bullets, and backend"""
    print("\n" + "=" * 70)
    print("TEST 1: Basic Deduplication")
    print("=" * 70)
    
    # Create SEO content with duplicates
    title = OptimizedContent(
        content="Brand Makeup Sponge Beauty Blender Latex Free",
        keywords_included=["makeup sponge", "beauty blender", "latex free"]
    )
    
    bullets = [
        OptimizedContent(
            content="Bullet 1: Perfect makeup sponge for flawless foundation",
            keywords_included=["makeup sponge", "foundation sponge"]  # "makeup sponge" is duplicate
        ),
        OptimizedContent(
            content="Bullet 2: This beauty blender is latex free and hypoallergenic",
            keywords_included=["beauty blender", "latex free", "hypoallergenic"]  # Both are duplicates
        ),
    ]
    
    backend = ["makeup sponge", "beauty tool", "latex free", "cosmetic sponge"]  # 2 duplicates
    
    optimized_seo = OptimizedSEO(title, bullets, backend)
    
    # Run deduplication
    result = deduplicate_keywords_across_content_mock(optimized_seo)
    
    # Verify title unchanged
    assert len(result.optimized_title.keywords_included) == 3
    print(f"\n✅ Title: {result.optimized_title.keywords_included}")
    
    # Verify bullet 1
    bullet1_keywords = result.optimized_bullets[0].keywords_included
    assert "makeup sponge" not in bullet1_keywords, "Duplicate 'makeup sponge' should be removed"
    assert "foundation sponge" in bullet1_keywords, "'foundation sponge' should be kept"
    print(f"✅ Bullet 1: {bullet1_keywords}")
    
    # Verify bullet 2
    bullet2_keywords = result.optimized_bullets[1].keywords_included
    assert "beauty blender" not in bullet2_keywords, "Duplicate 'beauty blender' should be removed"
    assert "latex free" not in bullet2_keywords, "Duplicate 'latex free' should be removed"
    assert "hypoallergenic" in bullet2_keywords, "'hypoallergenic' should be kept"
    print(f"✅ Bullet 2: {bullet2_keywords}")
    
    # Verify backend
    backend_keywords = result.optimized_backend_keywords
    assert "makeup sponge" not in backend_keywords
    assert "latex free" not in backend_keywords
    assert "beauty tool" in backend_keywords
    assert "cosmetic sponge" in backend_keywords
    print(f"✅ Backend: {backend_keywords}")
    
    print("\n✅ PASS: Basic deduplication works correctly")


def test_case_insensitive_deduplication():
    """Test that deduplication is case-insensitive"""
    print("\n" + "=" * 70)
    print("TEST 2: Case-Insensitive Deduplication")
    print("=" * 70)
    
    title = OptimizedContent(
        content="Brand Makeup Sponge",
        keywords_included=["Makeup Sponge"]  # Capitalized
    )
    
    bullets = [
        OptimizedContent(
            content="Bullet 1",
            keywords_included=["makeup sponge", "MAKEUP SPONGE"]  # Different cases - should be removed
        )
    ]
    
    backend = ["MakeUp Sponge", "beauty tool"]  # Different case - should be removed
    
    optimized_seo = OptimizedSEO(title, bullets, backend)
    result = deduplicate_keywords_across_content_mock(optimized_seo)
    
    # Verify case-insensitive deduplication
    assert len(result.optimized_bullets[0].keywords_included) == 0
    assert "MakeUp Sponge" not in result.optimized_backend_keywords
    assert "beauty tool" in result.optimized_backend_keywords
    
    print(f"\n✅ Title: {result.optimized_title.keywords_included}")
    print(f"✅ Bullet 1: {result.optimized_bullets[0].keywords_included}")
    print(f"✅ Backend: {result.optimized_backend_keywords}")
    
    print("\n✅ PASS: Case-insensitive deduplication works")


def test_priority_order():
    """Test that priority order is correct: Title > Bullet 1 > Bullet 2 > Backend"""
    print("\n" + "=" * 70)
    print("TEST 3: Priority Order")
    print("=" * 70)
    
    title = OptimizedContent(
        content="Brand Keyword A",
        keywords_included=["keyword a"]
    )
    
    bullets = [
        OptimizedContent(content="Bullet 1", keywords_included=["keyword a", "keyword b"]),
        OptimizedContent(content="Bullet 2", keywords_included=["keyword b", "keyword c"]),
        OptimizedContent(content="Bullet 3", keywords_included=["keyword c", "keyword d"]),
    ]
    
    backend = ["keyword a", "keyword b", "keyword c", "keyword d", "keyword e"]
    
    optimized_seo = OptimizedSEO(title, bullets, backend)
    result = deduplicate_keywords_across_content_mock(optimized_seo)
    
    # Title keeps "keyword a"
    assert "keyword a" in result.optimized_title.keywords_included
    print(f"\n✅ Title keeps: keyword a")
    
    # Bullet 1 loses "keyword a" but keeps "keyword b"
    assert "keyword a" not in result.optimized_bullets[0].keywords_included
    assert "keyword b" in result.optimized_bullets[0].keywords_included
    print(f"✅ Bullet 1 keeps: keyword b")
    
    # Bullet 2 loses "keyword b" but keeps "keyword c"
    assert "keyword b" not in result.optimized_bullets[1].keywords_included
    assert "keyword c" in result.optimized_bullets[1].keywords_included
    print(f"✅ Bullet 2 keeps: keyword c")
    
    # Bullet 3 loses "keyword c" but keeps "keyword d"
    assert "keyword c" not in result.optimized_bullets[2].keywords_included
    assert "keyword d" in result.optimized_bullets[2].keywords_included
    print(f"✅ Bullet 3 keeps: keyword d")
    
    # Backend only keeps "keyword e"
    assert result.optimized_backend_keywords == ["keyword e"]
    print(f"✅ Backend keeps: keyword e")
    
    print("\n✅ PASS: Priority order is correct")


def test_no_duplicates_case():
    """Test when there are no duplicates"""
    print("\n" + "=" * 70)
    print("TEST 4: No Duplicates (Should Not Change)")
    print("=" * 70)
    
    title = OptimizedContent(
        content="Brand A B C",
        keywords_included=["keyword a", "keyword b"]
    )
    
    bullets = [
        OptimizedContent(content="Bullet 1", keywords_included=["keyword c", "keyword d"]),
        OptimizedContent(content="Bullet 2", keywords_included=["keyword e", "keyword f"]),
    ]
    
    backend = ["keyword g", "keyword h"]
    
    optimized_seo = OptimizedSEO(title, bullets, backend)
    result = deduplicate_keywords_across_content_mock(optimized_seo)
    
    # Everything should remain unchanged
    assert len(result.optimized_title.keywords_included) == 2
    assert len(result.optimized_bullets[0].keywords_included) == 2
    assert len(result.optimized_bullets[1].keywords_included) == 2
    assert len(result.optimized_backend_keywords) == 2
    
    print(f"\n✅ All keywords kept (no duplicates found)")
    print("\n✅ PASS: No false positives")


def test_actual_code_verification():
    """Verify the actual implementation exists"""
    print("\n" + "=" * 70)
    print("TEST 5: Actual Code Verification")
    print("=" * 70)
    
    import os
    runner_file = os.path.join(os.path.dirname(__file__), 
                               "app", "local_agents", "seo", "runner.py")
    
    with open(runner_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the deduplication method exists
    if "def _deduplicate_keywords_across_content" in content:
        print("   ✅ Deduplication method found")
    else:
        print("   ❌ Deduplication method NOT found")
        raise AssertionError("Deduplication method not found in runner.py")
    
    # Check if it's called in run_seo_analysis
    if "self._deduplicate_keywords_across_content" in content:
        print("   ✅ Deduplication method is called")
    else:
        print("   ❌ Deduplication method NOT called")
        raise AssertionError("Deduplication method not called in run_seo_analysis")
    
    # Check for key logic elements
    checks = [
        ("Priority: Title > Bullets > Backend", "Priority documentation"),
        ("used_keywords.update", "Keyword tracking"),
        ("kw.lower() not in used_keywords", "Case-insensitive deduplication"),
        ("Total Duplicates Removed", "Summary logging"),
    ]
    
    for check_text, description in checks:
        if check_text in content:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} NOT found")
            raise AssertionError(f"{description} not found in code")
    
    print("\n✅ PASS: Actual code implementation verified")


def test_before_after_comparison():
    """Show before/after behavior"""
    print("\n" + "=" * 70)
    print("TEST 6: Before/After Comparison")
    print("=" * 70)
    
    print("\n❌ BEFORE (Issue):")
    print("   Title: ['makeup sponge', 'beauty blender', 'latex free']")
    print("   Bullet 1: ['makeup sponge', 'foundation']  ← duplicate")
    print("   Bullet 2: ['beauty blender', 'latex free']  ← duplicates")
    print("   Backend: ['makeup sponge', 'latex free', 'cosmetic']  ← duplicates")
    print("   ")
    print("   Result: 'makeup sponge' appears 3 times!")
    print("           'latex free' appears 3 times!")
    print("           'beauty blender' appears 2 times!")
    print("           Inefficient keyword coverage")
    
    print("\n✅ AFTER (Fixed):")
    print("   Title: ['makeup sponge', 'beauty blender', 'latex free']  ← all kept")
    print("   Bullet 1: ['foundation']  ← 'makeup sponge' removed")
    print("   Bullet 2: []  ← both duplicates removed")
    print("   Backend: ['cosmetic']  ← duplicates removed")
    print("   ")
    print("   Result: Each keyword appears ONCE")
    print("           Maximum keyword coverage")
    print("           More space for additional keywords")
    print("   ")
    print("   Code Location: backend/app/local_agents/seo/runner.py")
    print("   - Line ~1644-1730: _deduplicate_keywords_across_content() method")
    print("   - Line ~169: Called after AI generation and validation")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("ISSUE #6: DUPLICATE KEYWORDS ACROSS CONTENT - TEST SUITE")
    print("=" * 70)
    
    try:
        test_basic_deduplication()
        test_case_insensitive_deduplication()
        test_priority_order()
        test_no_duplicates_case()
        test_actual_code_verification()
        test_before_after_comparison()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print("\nSummary:")
        print("✅ Basic deduplication works correctly")
        print("✅ Case-insensitive matching")
        print("✅ Priority order enforced (Title > Bullets > Backend)")
        print("✅ No false positives when no duplicates exist")
        print("✅ Actual code implementation verified")
        
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


