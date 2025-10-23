"""
Standalone Test for Issue #5: Design-Specific Keywords Not Required in Title

Issue: There was no explicit requirement to include 2-3 design-specific keywords
(from the highest volume root) in the optimized title.

Fix: Updated prompts to make design keyword inclusion MANDATORY in the title
with clear step-by-step instructions.

Location: backend/app/local_agents/seo/prompts.py
"""

import os


def test_title_optimization_section():
    """Test that Title Optimization section includes mandatory design keyword requirement"""
    print("\n" + "=" * 70)
    print("TEST 1: Title Optimization Section")
    print("=" * 70)
    
    prompts_file = os.path.join(os.path.dirname(__file__), 
                                "app", "local_agents", "seo", "prompts.py")
    
    with open(prompts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract Title Optimization section
    title_section_start = content.find("### Title Optimization:")
    title_section_end = content.find("### Bullet Point Optimization:")
    title_section = content[title_section_start:title_section_end]
    
    print("\n📋 Checking Title Optimization section for design keyword requirement...")
    
    # Check for mandatory requirement
    checks = [
        ("**MANDATORY: MUST include 2-3 Design-Specific keywords", 
         "Mandatory design keyword requirement"),
        ("highest volume root", 
         "Highest volume root specification"),
    ]
    
    all_passed = True
    for check_text, description in checks:
        if check_text in title_section:
            print(f"   ✅ {description} found")
        else:
            print(f"   ❌ {description} NOT found")
            all_passed = False
    
    assert all_passed, "Title Optimization section missing design keyword requirements"
    print("\n✅ PASS: Title section has mandatory design keyword requirement")


def test_design_keywords_section():
    """Test that Design-Specific Keywords section has clear instructions"""
    print("\n" + "=" * 70)
    print("TEST 2: Design-Specific Keywords Section")
    print("=" * 70)
    
    prompts_file = os.path.join(os.path.dirname(__file__), 
                                "app", "local_agents", "seo", "prompts.py")
    
    with open(prompts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract Design Keywords section
    design_section_start = content.find("**Design-Specific Keywords")
    design_section_end = content.find("**Root Volume Analysis:")
    design_section = content[design_section_start:design_section_end]
    
    print("\n📋 Checking Design-Specific Keywords section for guidance...")
    
    # Check for step-by-step instructions
    checks = [
        ("⚠️ **MANDATORY TITLE REQUIREMENT:**", 
         "Mandatory title requirement warning"),
        ("Step 1: Identify the design root with HIGHEST combined volume", 
         "Step 1: Identify highest volume root"),
        ("Step 2: Select 2-3 keywords from that specific root", 
         "Step 2: Select 2-3 keywords"),
        ("Step 3: MUST include these 2-3 keywords in the optimized title", 
         "Step 3: Must include in title"),
        ("Example:", 
         "Example provided"),
    ]
    
    all_passed = True
    for check_text, description in checks:
        if check_text in design_section:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} NOT found")
            all_passed = False
    
    assert all_passed, "Design Keywords section missing step-by-step instructions"
    print("\n✅ PASS: Design Keywords section has clear step-by-step guidance")


def test_critical_requirements_section():
    """Test that CRITICAL REQUIREMENTS section includes design keywords"""
    print("\n" + "=" * 70)
    print("TEST 3: CRITICAL REQUIREMENTS Section")
    print("=" * 70)
    
    prompts_file = os.path.join(os.path.dirname(__file__), 
                                "app", "local_agents", "seo", "prompts.py")
    
    with open(prompts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract CRITICAL REQUIREMENTS section
    critical_section_start = content.find("## CRITICAL REQUIREMENTS (ALL MANDATORY):")
    critical_section = content[critical_section_start:]
    
    print("\n📋 Checking CRITICAL REQUIREMENTS section...")
    
    # Check for design keyword requirement
    checks = [
        ("⚠️ **DESIGN KEYWORDS (MANDATORY)**", 
         "Design keywords mandatory marker"),
        ("Title MUST include 2-3 Design-Specific keywords from the HIGHEST volume root", 
         "Main requirement statement"),
        ("Find the design root with highest combined volume", 
         "Instruction: Find highest volume root"),
        ("Select 2-3 keywords from that specific root only", 
         "Instruction: Select from specific root"),
        ("All 2-3 MUST appear in the optimized title", 
         "Instruction: Must appear in title"),
    ]
    
    all_passed = True
    for check_text, description in checks:
        if check_text in critical_section:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} NOT found")
            all_passed = False
    
    assert all_passed, "CRITICAL REQUIREMENTS section missing design keyword requirements"
    print("\n✅ PASS: CRITICAL REQUIREMENTS has mandatory design keyword rule")


def test_multiple_enforcement_locations():
    """Test that design keyword requirement appears in multiple locations"""
    print("\n" + "=" * 70)
    print("TEST 4: Multiple Enforcement Locations")
    print("=" * 70)
    
    prompts_file = os.path.join(os.path.dirname(__file__), 
                                "app", "local_agents", "seo", "prompts.py")
    
    with open(prompts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n📋 Counting design keyword requirement mentions...")
    
    # Count different variations of the requirement
    patterns = [
        "MUST include 2-3 Design-Specific keywords",
        "MANDATORY TITLE REQUIREMENT",
        "DESIGN KEYWORDS (MANDATORY)",
    ]
    
    total_count = 0
    for pattern in patterns:
        count = content.count(pattern)
        total_count += count
        print(f"   📌 '{pattern}': {count} occurrence(s)")
    
    print(f"\n   Total enforcement points: {total_count}")
    
    assert total_count >= 3, "Design keyword requirement should appear in at least 3 locations"
    print("\n✅ PASS: Design keyword requirement enforced in multiple locations")


def test_before_after_comparison():
    """Show before/after state"""
    print("\n" + "=" * 70)
    print("TEST 5: Before/After Comparison")
    print("=" * 70)
    
    print("\n❌ BEFORE (Issue):")
    print("   Line 39 (old): '- Include 2-3 Design-Specific keywords from highest volume root'")
    print("   - Not marked as MANDATORY")
    print("   - No step-by-step instructions")
    print("   - Not emphasized in CRITICAL REQUIREMENTS")
    print("   Result: AI could ignore this requirement")
    
    print("\n✅ AFTER (Fixed):")
    print("   1. Title Optimization (Line 39):")
    print("      '- **MANDATORY: MUST include 2-3 Design-Specific keywords from highest volume root**'")
    print("   ")
    print("   2. Design Keywords Section (Lines 107-111):")
    print("      'ℹ️ **MANDATORY TITLE REQUIREMENT:**'")
    print("      '→ Step 1: Identify the design root with HIGHEST combined volume'")
    print("      '→ Step 2: Select 2-3 keywords from that specific root'")
    print("      '→ Step 3: MUST include these 2-3 keywords in the optimized title'")
    print("   ")
    print("   3. CRITICAL REQUIREMENTS (Lines 138-141):")
    print("      '3. ⚠️ **DESIGN KEYWORDS (MANDATORY)**: Title MUST include...'")
    print("      '   - Find the design root with highest combined volume'")
    print("      '   - Select 2-3 keywords from that specific root only'")
    print("      '   - All 2-3 MUST appear in the optimized title'")
    print("   ")
    print("   Result: AI cannot ignore - requirement appears 3 times with clear instructions")


def test_instruction_clarity():
    """Test that instructions are clear and actionable"""
    print("\n" + "=" * 70)
    print("TEST 6: Instruction Clarity")
    print("=" * 70)
    
    prompts_file = os.path.join(os.path.dirname(__file__), 
                                "app", "local_agents", "seo", "prompts.py")
    
    with open(prompts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n📋 Checking for actionable instructions...")
    
    # Check for clear, actionable verbs
    actionable_checks = [
        ("Identify the design root", "Action: Identify"),
        ("Select 2-3 keywords", "Action: Select"),
        ("MUST include", "Action: Include"),
        ("Find the design root", "Action: Find"),
        ("highest combined volume", "Metric: Volume-based"),
    ]
    
    all_passed = True
    for check_text, description in actionable_checks:
        if check_text in content:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} NOT found")
            all_passed = False
    
    assert all_passed, "Instructions not clear or actionable"
    print("\n✅ PASS: Instructions are clear and actionable")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("ISSUE #5: DESIGN-SPECIFIC KEYWORDS NOT REQUIRED - TEST SUITE")
    print("=" * 70)
    
    try:
        test_title_optimization_section()
        test_design_keywords_section()
        test_critical_requirements_section()
        test_multiple_enforcement_locations()
        test_before_after_comparison()
        test_instruction_clarity()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print("\nSummary:")
        print("✅ Title Optimization section has MANDATORY requirement")
        print("✅ Design Keywords section has step-by-step instructions")
        print("✅ CRITICAL REQUIREMENTS enforces design keyword inclusion")
        print("✅ Requirement appears in 3+ locations for strong enforcement")
        print("✅ Instructions are clear and actionable")
        
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


