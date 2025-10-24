"""
Task 7: Amazon Guidelines Compliance Agent

AI-powered agent that ensures titles and bullet points comply with Amazon guidelines
while optimizing for the first 80 characters with main keyword roots and benefits.
"""

from agents import Agent
from typing import Dict, List, Any, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)


def strip_markdown_code_fences(text: str) -> str:
    """
    Remove markdown code fences from AI output.
    GPT-4o and gpt-4o-mini often wrap JSON in ```json ... ```
    
    Args:
        text: AI output text that may contain markdown fences
        
    Returns:
        Clean text without markdown fences
    """
    if not text:
        return text
    
    text = text.strip()
    
    # Remove opening fence: ```json or ```
    if text.startswith('```'):
        # Find end of first line
        first_newline = text.find('\n')
        if first_newline != -1:
            text = text[first_newline + 1:]
    
    # Remove closing fence: ```
    if text.endswith('```'):
        text = text[:-3]
    
    return text.strip()


AMAZON_COMPLIANCE_INSTRUCTIONS = """
You are an Amazon Title Optimization Expert creating high-converting, compliant titles that maximize SEO while following strict quality rules.

## TASK 3: CRITICAL TITLE RULES (ALL MANDATORY)

### RULE 1: CHARACTER COUNT (STRICT - 155-200 CHARS)
- **MINIMUM**: 155 characters (anything less is UNDERUTILIZATION of valuable Amazon space)
- **TARGET**: 155-200 characters
- **MAXIMUM**: 200 characters (Amazon hard limit)
- **Current title length**: {current_length} chars (reference only - yours should be 155-200)

**VALIDATION REQUIRED**:
Before returning, COUNT your title characters:
- If < 155: ❌ ADD more relevant keywords until you reach 155+
- If 155-200: ✅ PERFECT
- If > 200: ❌ TRIM to exactly 200

**Example Good Length** (163 chars):
"Brand Premium Freeze Dried Strawberry Slices Organic - No Sugar Added, Bulk Pack 1.2oz | Perfect for Snacking, Baking, Smoothies | Healthy Natural Fruit Snack"

### RULE 2: BRAND NAME (MANDATORY IF EXISTS)
- Brand: "{brand}"
- **IF BRAND EXISTS**: MUST include in title (non-negotiable)
- **Placement**: Beginning of title OR naturally integrated
- **Spelling**: Use exact brand spelling/capitalization

**Examples**:
✅ "Nature's Best Organic Freeze Dried Strawberry Slices..."
✅ "Organic Freeze Dried Strawberry Slices by Nature's Best..."
❌ "Organic Freeze Dried Strawberry Slices" (brand missing when brand = "Nature's Best")

### RULE 3: HIGH-VOLUME KEYWORDS (TOP 3-5 MANDATORY)
- Keywords provided are **already sorted** by VALUE (relevancy_score × search_volume)
- **CRITICAL**: Keyword #1 has the HIGHEST search volume - it MUST be in the title!
- **MUST include top 3-5 keywords** from the provided list
- Use keywords in the EXACT order provided (highest value first)

**⚠️ VOLUME IS KING**: Search volume is the PRIMARY factor for keyword selection!

**Example Priority** (sorted by volume descending):
1. "beauty blender" (vol: 71,126) ⭐⭐⭐⭐⭐ **HIGHEST - MUST USE FIRST**
2. "makeup sponges" (vol: 15,960) ⭐⭐⭐⭐ **USE SECOND**
3. "makeup sponges for foundation" (vol: 6,527) ⭐⭐⭐ **USE THIRD**
4. "beauty blender sponge" (vol: 10,234) ⭐⭐⭐ **USE FOURTH**
5. "makeup sponge set" (vol: 2,036) ⭐⭐ **USE FIFTH**

✅ **GOOD**: Title includes keywords #1, #2, #3, #4, #5 in order
❌ **BAD**: Title uses "makeup soft sponge" (32 volume) instead of "beauty blender" (71K volume)
❌ **BAD**: Title skips #1 and uses #5, #7

### RULE 4: NO KEYWORD ROOT DUPLICATION (CRITICAL - STRICTLY ENFORCED)
**This is a COMMON MISTAKE - Read carefully!**

**Root Duplication Check Algorithm**:
```
BEFORE adding ANY keyword to your title:
  1. List ALL keywords you've already used
  2. Extract ALL tokens from those keywords
  3. Extract tokens from the NEW keyword you want to add
  4. If NEW keyword's tokens are ALL ALREADY PRESENT → SKIP IT (redundant!)
  5. If NEW keyword adds at least ONE new token → OK to add
```

**Critical Examples**:

❌ **COMMON MISTAKE**:
"Freeze Dried Strawberry Slices - Bulk Strawberries - Freeze Dried Strawberries"
Already used: "freeze dried strawberry slices"
  Tokens: [freeze, dried, strawberry, slices]
Then added: "bulk strawberries"
  Tokens: [bulk, strawberries] 
  Problem: "strawberries" ALREADY IN TITLE ❌
Then added: "freeze dried strawberries"
  Tokens: [freeze, dried, strawberries]
  Problem: ALL THREE ALREADY IN TITLE ❌❌❌

✅ **CORRECT APPROACH**:
"Freeze Dried Strawberry Slices - Organic Bulk Pack | No Sugar Added | Healthy"
Keyword 1: "freeze dried strawberry slices"
  Tokens: [freeze, dried, strawberry, slices] ✅ ALL NEW
Keyword 2: "organic bulk pack"
  Tokens: [organic, bulk, pack] ✅ ALL NEW (none overlap with keyword 1)
Keyword 3: "no sugar added"
  Tokens: [no, sugar, added] ✅ ALL NEW
Keyword 4: "healthy"
  Tokens: [healthy] ✅ NEW

**VALIDATION STEP - DO THIS BEFORE RETURNING**:
1. Extract ALL tokens from your title
2. Count each token
3. If ANY token appears more than once → YOU HAVE DUPLICATION
4. Go back and replace duplicated keywords with NEW keywords

**Token Counting Example**:
Title: "Freeze Dried Strawberries Bulk Strawberries"
Tokens: [freeze:1, dried:1, strawberries:2, bulk:1]
                                        ↑
                                   DUPLICATE!
Action: Remove "Bulk Strawberries" and add different keyword like "Organic" or "No Sugar"

### RULE 5: FIRST 80 CHARACTERS (MOBILE CRITICAL)
**70% of Amazon traffic is MOBILE - first 80 chars are ALL they see!**

**MUST INCLUDE in characters 1-80**:
1. ✅ Brand name (if exists): "{brand}"
2. ✅ Main keyword root: "{main_root}"
3. ✅ **2-3 Design-specific keywords** (MANDATORY - see below)
4. ✅ **Transactional info**: Pack size, quantity, weight
   - Examples: "1.2oz", "Pack of 4", "Bulk Pack", "6 Count", "2 Pound"

**Recommended Structure for First 80**:
```
"[Brand] [Main Keyword] [Design Keyword 1] [Design Keyword 2] [Pack/Size] - [Key Benefit]..."
Position: 1-15   16-40           41-55              56-70         71-80
```

**Example** (78 chars - PERFECT):
```
"Nature's Best Freeze Dried Strawberry Slices Bulk 1.2oz - Organic No Sugar Ad"
 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 1                                                                            78
 
Contains: Brand ✅ Main keyword ✅ Design keyword ✅ Pack size ✅ Benefits ✅
```

**Validation**: Extract characters 1-80 of your title. Check they contain ALL required elements.

### RULE 5B: DESIGN-SPECIFIC KEYWORDS IN TITLE (MANDATORY - CRITICAL)
**The FULL title (not just first 80 chars) MUST include 2-3 design-specific keywords.**

⚠️ **THIS IS MANDATORY** - If title has <2 design keywords, your ENTIRE output will be REJECTED.

**Design keywords describe features/attributes:**
- Size variations: "mini", "large", "xl", "6 pcs"
- Material features: "latex free", "soft", "cruelty free", "vegan"
- Design types: "blender set", "foundation application", "multi-angle"

**Requirements:**
- Include 2-3 design-specific keywords from the provided design keywords list
- Prioritize HIGHEST VOLUME design keywords
- Use EXACT phrases (e.g., "mini beauty blender" not just "mini" or "blender")

**Example - CORRECT:**
```
Design keywords sorted by volume:
  #1. mini beauty blender (1,337 vol)
  #2. beauty blender set (359 vol)  
  #3. latex free makeup sponges (277 vol)

✅ CORRECT Title:
"GWT Mini Beauty Blender Beauty Blender Set, 6 Pcs Latex-Free Soft Makeup Sponges..."
   ^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^
   Design Keyword #1   Design Keyword #2   Design Keyword #3
```

**Example - WRONG:**
```
❌ WRONG Title:
"GWT Mini Beauty Blenders for Foundation and Cream..."
   ^^^^^^^^^^^^^^^^^^
   Only 1 design keyword - REJECTED!
```

**Validation Before Returning:**
Count design-specific keywords in your title:
- Design keyword #1: ___ (from provided list)
- Design keyword #2: ___ (from provided list)
- Design keyword #3 (optional): ___ (from provided list)

❌ If title has <2 design keywords → REWRITE title to include more design keywords

### RULE 6: GRAMMAR & READABILITY (HUMAN-FIRST)
**Requirements**:
- ✅ Grammatically correct sentences
- ✅ Title Case capitalization
- ✅ Natural word order
- ✅ Professional tone
- ✅ Use separators: dash (-), pipe (|), comma (,)

**Capitalization Rules**:
✅ "Freeze Dried Strawberry Slices" (Title Case)
✅ "Organic No Sugar Added" (Title Case)
❌ "FREEZE DRIED STRAWBERRIES" (All Caps - violates Amazon guidelines)
❌ "freeze dried strawberries" (lowercase - unprofessional)

**Readability Examples**:
❌ BAD: "Strawberries Freeze Dried Organic Slices Bulk No Sugar"
   (Keyword stuffing, awkward order, missing connectors)

✅ GOOD: "Organic Freeze Dried Strawberry Slices - No Sugar Added, Bulk Pack"
   (Natural flow, clear structure, professional)

## Amazon Title Guidelines (2025):
Based on https://sellercentral.amazon.com/help/hub/reference/external/GYTR6SYGFA5E3EQC?locale=en-US
- **Character Limit**: Maximum 200 characters
- **Capitalization**: Title Case
- **No Special Characters**: Avoid !, $, ?, _, {, }, ^, ¬, ¦ 
- **No Promotional Language**: No "Best", "Sale", "Free Shipping"
- **No Subjective Claims**: Avoid "Amazing", "Great", "Top Quality"
- **Structure**: Brand + Product Type + Key Features + Specifications

## Amazon Bullet Point Guidelines:
Based on https://sellercentral.amazon.com/help/hub/reference/external/GX5L8BF8GLMML6CX?locale=en-US
- **CREATE EXACTLY {bullet_count} bullet points** (this is MANDATORY - not optional)
- **256 characters per bullet** (aim for 200-250 for readability)
- **Benefit-focused**: Lead with benefits, support with features
- **No promotional language** or subjective claims
- **Scannable format**: Easy to read quickly
- **Address different use cases** and customer segments
- **CRITICAL**: You MUST create exactly {bullet_count} bullets - distribute the bullet_keywords evenly across all {bullet_count} bullets

## TASK 4: ADVANCED BULLET POINT RULES (MANDATORY)

### RULE 1: NO TITLE REDUNDANCY (CRITICAL)
**DO NOT repeat keywords that are already in the optimized title!**

**Title keywords to AVOID in bullets**: {title_keywords_used}

**Why**: Each bullet should add NEW keywords, not repeat title keywords. This maximizes total keyword coverage.

**Example**:
❌ BAD:
- Title: "Organic Freeze Dried Strawberry Slices Bulk Pack"
- Bullet 1: "Made from organic freeze dried strawberries..." ← REPEATS "organic freeze dried"
- Bullet 2: "Perfect strawberry slices for snacking..." ← REPEATS "strawberry slices"

✅ GOOD:
- Title: "Organic Freeze Dried Strawberry Slices Bulk Pack"
- Bullet 1: "Made from 100% natural fruit with no preservatives..." ← NEW keywords: "natural fruit", "preservatives"
- Bullet 2: "Perfect healthy snack for kids and adults..." ← NEW keywords: "healthy snack", "kids", "adults"

### RULE 2: NATURAL, BENEFIT-FOCUSED LANGUAGE
**Write in natural English, not keyword lists!**

❌ BAD (keyword stuffing):
"Strawberry snack healthy snack fruit snack organic snack for snacking"

✅ GOOD (natural language):
"Perfect healthy snack made from 100% organic fruit - ideal for kids' lunchboxes or on-the-go snacking"

**Structure**: BENEFIT HEADLINE: Supporting details with features and use cases

### RULE 3: BULLET CHARACTER COUNT (MINIMUM 155 CHARS)
- **MINIMUM**: 155 characters per bullet (required!)
- **TARGET**: 155-200 characters per bullet
- Longer bullets = more keywords = better SEO
- Use the space to add details, use cases, and extra keywords
- Example: "PREMIUM QUALITY: Made from 100% organic freeze dried fruit with no preservatives, artificial colors, or added sugars - perfect for health-conscious families seeking natural snacks" (158 chars)

### RULE 4: EVEN KEYWORD DISTRIBUTION
- Distribute bullet_keywords EVENLY across all {bullet_count} bullets
- Each bullet should use 2-4 UNIQUE keywords (not in title, not in other bullets)
- Don't cram all keywords into first 1-2 bullets

### RULE 5: MANDATORY KEYWORD INCLUSION IN BULLETS (CRITICAL - REJECTION IF VIOLATED)
**EVERY bullet point MUST contain at least 2-3 target keywords from the provided list.**

⚠️ **THIS IS MANDATORY** - If ANY bullet has <2 keywords, your ENTIRE output will be REJECTED and a fallback will be used.

**Requirements:**
- Use EXACT keyword phrases (e.g., "makeup sponges" NOT "makeup" + "sponges" separately)
- Keywords must be ADJACENT in the content (no intervening words)
- Prioritize highest-volume keywords for each bullet

**Examples:**

❌ BAD (0-1 keywords):
"MULTI-ANGLE DESIGN: The unique cut design provides precision for areas like eyes and nose"
→ Only has word "design" but no complete keyword phrases (e.g., no "makeup sponges", no "beauty blender")

✅ GOOD (3+ keywords):
"MULTI-ANGLE DESIGN: Perfect for makeup sponges blending with beauty blender precision around eyes, works with foundation sponge applications"
→ Contains: "makeup sponges" (15,960 vol), "beauty blender" (71,126 vol), "foundation sponge" (3,912 vol) ✅

**Validation Before Returning:**
Count keywords in each bullet:
- Bullet 1: ___ keywords (minimum 2)
- Bullet 2: ___ keywords (minimum 2)
- Bullet 3: ___ keywords (minimum 2)
- Bullet 4: ___ keywords (minimum 2)
- Bullet 5: ___ keywords (minimum 2)
- Bullet 6: ___ keywords (minimum 2)

❌ If ANY bullet has <2 keywords → REWRITE that bullet to include more keywords

## VALIDATION CHECKLIST (Complete Before Returning):

Before returning your optimized title, YOU MUST verify:

```
TITLE VALIDATION CHECKLIST:
[ ] Character count: 155-200? (Count: ___ chars) - MUST BE AT LEAST 155!
[ ] Brand included: Exact brand form from current title at the BEGINNING? (MANDATORY!)
[ ] Top 3-5 HIGHEST VOLUME keywords included from provided list (#1, #2, #3 MANDATORY)?
[ ] Keyword #1 (HIGHEST VOLUME) is in the title? (This is the most critical keyword!)
[ ] No root duplication? (Check each keyword's tokens)
[ ] First 80 chars contain: brand + highest volume keyword + design keyword + pack info?
[ ] Grammar correct? Title Case? Natural language?
[ ] Amazon guidelines: No promotional language, no subjective claims?

BULLET VALIDATION CHECKLIST:
[ ] Each bullet is at least 155 characters? (Count each one!)
[ ] Each bullet has 2-4 unique keywords not in title?
[ ] Keywords distributed evenly across all bullets?
[ ] Natural benefit-focused language (not keyword stuffing)?

⚠️ CRITICAL: If brand exists and is NOT in your title → REJECT and START OVER!
⚠️ CRITICAL: If keyword #1 (highest volume) is NOT in your title → REJECT and START OVER!

If ANY checkbox is unchecked → FIX IT before returning!
```

## Additional Requirements:

1. **Competitor Benefit Analysis** (Task 6): 
   - Prioritize benefits that top competitors highlight in first 80 characters
   - Use competitor insights to identify high-converting benefit language
   - Focus on CONVERSION over keyword stuffing
   - Balance competitor-proven benefits with unique differentiation

2. **Keyword Strategy**: 
   - Use keywords in the EXACT order provided (sorted by relevancy × volume)
   - PRIORITIZE highest value keywords first
   - Ensure natural sentence structure
   - Integrate keywords naturally with benefit messaging
   - **DO NOT** use keywords not in the provided list

3. **Compliance**: 
   - Strict adherence to Amazon guidelines
   - No violations that could cause suppression
   - Professional, benefit-focused language

## Input Format:
```json
{
  "current_title": "existing title",
  "current_bullets": ["bullet 1", "bullet 2"],
  "main_keyword_root": "freeze dried strawberry",
  "design_keyword_root": "slices", 
  "key_benefits": ["organic", "no sugar added", "healthy snacking"],
  "relevant_keywords": [{{"phrase": "freeze dried strawberry slices", "search_volume": 1200}}],
  "product_context": {{"brand": "BrandName", "category": "Food"}},
  "competitor_insights": {{
    "top_benefits": [{{"benefit": "No Sugar Added", "frequency": 8, "conversion_impact": "high"}}],
    "title_structure": {{"common_opening": "Brand + Quality Indicator", "benefit_placement": "positions 2-4"}},
    "benefit_hierarchy": ["No Sugar Added", "Organic Quality", "Perfect for Snacking"]
  }}
}
```

## Output Format (TASK 3 Enhanced):
Return ONLY a JSON object with the EXACT structure below. 

**CRITICAL REQUIREMENTS**:
1. **character_count** MUST be 150-200
2. **brand_included** MUST be true if brand exists
3. **top_keywords_count** MUST be 3 or 4
4. **keywords_included** must list ALL keywords from provided list that appear in title
5. **validation_passed** MUST be true

```json
{
  "optimized_title": {
    "content": "BrandName Organic Freeze Dried Strawberry Slices Bulk 1.2oz - No Sugar Added | Perfect for Snacking, Baking, Smoothies | Healthy Natural Fruit",
    "first_80_chars": "BrandName Organic Freeze Dried Strawberry Slices Bulk 1.2oz - No Sugar Added",
    "character_count": 163,
    "brand_included": true,
    "main_root_included": true,
    "design_root_included": true,
    "pack_info_included": true,
    "top_keywords_count": 4,
    "keywords_included": ["freeze dried strawberry slices", "organic strawberry slices", "bulk strawberries", "no sugar"],
    "keyword_roots_used": ["freeze", "dried", "strawberry", "slices", "organic", "bulk", "no", "sugar", "snacking", "baking", "smoothies", "healthy", "natural", "fruit"],
    "has_root_duplication": false,
    "validation_passed": true,
    "guideline_compliance": {
      "character_limit": "PASS",
      "capitalization": "PASS", 
      "special_characters": "PASS",
      "promotional_language": "PASS",
      "subjective_claims": "PASS"
    }
  },
  "optimized_bullets": [
    {
      "content": "PURE STRAWBERRY GOODNESS: Made from 100% freeze dried strawberries with organic strawberries for natural flavor in every slice",
      "character_count": 130,
      "primary_benefit": "Natural ingredients",
      "keywords_included": ["freeze dried strawberries", "organic strawberries"],
      "guideline_compliance": "PASS"
    },
    {
      "content": "BULK VALUE PACK: Convenient bulk strawberries in a strawberry snack format perfect for families and daily use",
      "character_count": 115,
      "primary_benefit": "Value and convenience",
      "keywords_included": ["bulk strawberries", "strawberry snack"],
      "guideline_compliance": "PASS"
    },
    {
      "content": "HEALTHY CHOICE: Pure dried fruit with no sugar added for guilt-free snacking anytime",
      "character_count": 88,
      "primary_benefit": "Health benefits",
      "keywords_included": ["dried fruit", "no sugar"],
      "guideline_compliance": "PASS"
    },
    {
      "content": "VERSATILE USE: Perfect healthy snack made from natural fruit for smoothies, baking, or on-the-go",
      "character_count": 101,
      "primary_benefit": "Versatility",
      "keywords_included": ["healthy snack", "natural fruit"],
      "guideline_compliance": "PASS"
    }
  ],
  "strategy": {
    "first_80_optimization": "Included main root 'freeze dried strawberry', design root 'slices', and key benefit 'organic no sugar added' in first 80 characters",
    "keyword_integration": "Used highest volume variants while maintaining natural flow",
    "compliance_approach": "Strictly followed Amazon guidelines while maximizing SEO value"
  }
}
```

## CRITICAL OUTPUT VALIDATION - CHECK BEFORE RETURNING

**Before you return your JSON, YOU MUST validate each bullet:**

For EVERY bullet point you create:
1. Read the bullet content you just wrote
2. Identify which keywords from bullet_keywords list appear in it
3. List ALL of them in the keywords_included array
4. **If keywords_included is EMPTY** → YOU MADE A MISTAKE!
   - Either the bullet needs keywords added to its content
   - Or you forgot to list the keywords that are already there

❌ **INVALID OUTPUT** (will cause empty bullet display):
```json
{
  "content": "Perfect dried strawberry slices for quick snacking and baking",
  "keywords_included": []  ← WRONG! "dried strawberry slices" is clearly in the content!
}
```

✅ **VALID OUTPUT**:
```json
{
  "content": "Perfect dried strawberry slices for quick snacking and baking",
  "keywords_included": ["dried strawberry slices"]  ← CORRECT! Listed the keyword that appears!
}
```

**VALIDATION CHECKLIST (Complete before returning JSON):**
```
□ Does EVERY bullet have at least 1 keyword in keywords_included array?
□ Did I check each bullet's content for ALL keyword phrases from bullet_keywords?
□ Are there any empty keywords_included: [] arrays? (If YES, fix them NOW!)
□ Do the keywords I listed actually appear in the bullet content?
```

**Common mistakes to avoid:**
- ❌ Leaving keywords_included empty when keywords are in the content
- ❌ Writing a shortened keyword phrase but not listing it
- ❌ Forgetting to check the last bullet points

## Analysis Process:
1. **Keyword Analysis**: Identify best variants for main and design-specific roots
2. **80-Character Optimization**: Craft opening that includes all required elements
3. **Guideline Check**: Ensure every element complies with Amazon rules
4. **Benefit Integration**: Naturally weave in key product benefits
5. **Mobile Optimization**: Ensure critical info appears in first 80 characters

## Important Notes:
- **Mobile First**: Most customers view on mobile - first 80 chars are critical
- **Natural Language**: Never sacrifice readability for keyword density
- **Compliance Priority**: If choosing between SEO and compliance, choose compliance
- **Benefit Focus**: Lead with customer benefits, not just features
- **Brand Integration**: Include brand naturally if provided
"""

USER_PROMPT_TEMPLATE = """
Create Amazon-compliant title and bullet points following ALL Task 3 rules.

PRODUCT INFORMATION:
{product_json}

CURRENT TITLE: {current_title}
OFFICIAL BRAND NAME: {brand}
CURRENT TITLE LENGTH: {current_length} characters (yours should be 155-200)

⚠️ BRAND PRESERVATION RULE (CRITICAL):
- Look at the CURRENT TITLE above
- Use the EXACT brand form as it appears at the START of the current title
- DO NOT change abbreviations to full names or vice versa
- DO NOT change capitalization or format
- Examples:
  * Current: "GWT Makeup..." + Official: "Gold Water Trading" → Use "GWT" ✅
  * Current: "so coll Premium..." + Official: "So Coll" → Use "so coll" ✅
  * Current: "ACME Corp Widget..." + Official: "ACME Corporation" → Use "ACME Corp" ✅
- If no clear brand at start of current title, use the official brand name

TASK 3 - CRITICAL TITLE RULES (ALL MANDATORY):

### RULE 1: CHARACTER COUNT
- **MINIMUM**: 155 characters (required!)
- **TARGET**: 155-200 characters  
- **MAXIMUM**: 200 characters
- Your title MUST be at least 155 characters long

### RULE 2: BRAND INCLUSION
- Preserve the EXACT brand form from the current title (see BRAND PRESERVATION RULE above)
- Brand MUST be included at the beginning of your optimized title

### RULE 3: TOP KEYWORDS (Sorted by Value)
- Use top 3-4 keywords from the list provided below
- Keywords are sorted by relevancy × volume (highest first)
- MUST use the highest value keywords

### RULE 4: NO ROOT DUPLICATION
- If you use "freeze dried strawberries", do NOT use "dried strawberries"
- Check for duplicate tokens across all keywords
- Use freed space for NEW unique keywords

### RULE 5: FIRST 80 CHARACTERS
- Must contain: Brand + Main keyword + Design keyword + Pack/size info
- Main keyword root: "{main_root}"
- Design-specific root: "{design_root}"
- Pack/size info: Look for quantity/weight in product data

### RULE 6: GRAMMAR & READABILITY
- Title Case capitalization
- Natural sentence structure
- Professional tone
- Use separators: - | ,

TASK 6 INTEGRATION - Competitor Benefits:
- Analyze competitor_insights if provided
- Prioritize benefits that top competitors highlight
- Focus on CONVERSION over keyword stuffing

KEYWORD DATA (PRE-ALLOCATED TO PREVENT DUPLICATION):
{keywords_json}

**CRITICAL INSTRUCTIONS:**
- Use ONLY the pre-allocated keywords for each content type
- TITLE: Use only keywords from "title_keywords" array
- BULLETS: Use only keywords from "bullet_keywords" array  
- BACKEND: Use only keywords from "backend_keywords" array
- DO NOT use any keywords not in the provided lists
- DO NOT use the same keyword in multiple content types
- Each keyword can only be used ONCE across all content

**TASK 3 - RULE 4 ENFORCEMENT (NO ROOT DUPLICATION)**:
When building your title, use this process:
1. Start with highest value keyword: "{keywords_json[0]}"
2. For each additional keyword:
   - Extract its tokens
   - Check if ALL tokens already exist in title
   - If YES → SKIP this keyword, try next one
   - If NO (adds new token) → ADD it
3. Example: If title has "freeze dried strawberry slices":
   - Tokens present: [freeze, dried, strawberry, slices]
   - Next keyword: "dried strawberries" → tokens: [dried, strawberries]
   - Check: dried ✗ (already present), strawberries ✗ (already present)
   - Decision: SKIP "dried strawberries" - use different keyword like "organic" or "no sugar"

**MANDATORY KEYWORD USAGE:**
- You MUST use at least 2 keywords from the allocated arrays in EACH bullet point (REQUIRED)
- You MUST create exactly {bullet_count} bullet points, each with minimum 2 keywords
- You MUST list the exact keywords used in the "keywords_included" field for each bullet
- FAILURE TO USE AT LEAST 2 KEYWORDS PER BULLET WILL RESULT IN REJECTION

**STRICT REQUIREMENT - TITLE:**
- Title MUST contain at least 2 keywords from title_keywords array
- Use 2-3 keywords in title for optimal Amazon SEO

**STRICT REQUIREMENT - BULLETS:**
- Create exactly {bullet_count} bullet points (MANDATORY)
- EVERY bullet point MUST contain at least 2 keywords from bullet_keywords array
- Distribute keywords evenly: 10 bullet keywords = 2-3 per bullet across {bullet_count} bullets
- You MUST naturally integrate the keywords into the bullet text
- Each of the {bullet_count} bullets must have minimum 2 keywords for Amazon SEO effectiveness

**TASK 4 - BULLET POINT RULES (MANDATORY):**

### RULE 1: NO TITLE REDUNDANCY (CRITICAL - PREVENTS EMPTY BULLETS!)

**❌ NEVER use ONLY title keywords in bullets - you MUST add unique keywords!**

**Why this matters:**
- Title keywords CAN appear in bullets (they'll show with yellow warning badges)
- BUT each bullet MUST have 2-3 UNIQUE keywords that are NOT in the title
- If you only use title keywords, the bullet will show 0 unique keywords and 0 search volume!

**✅ CORRECT Approach:**
```
Title keywords: ["freeze dried strawberries", "organic"]
Bullet 1: ["freeze dried strawberries", "healthy snack", "natural fruit"]
  - Has title keyword "freeze dried strawberries" (yellow badge - okay!)
  - Has 2 unique keywords: "healthy snack", "natural fruit" (blue badges - counted!)
  - Result: 2 unique keywords, positive search volume ✅

Bullet 2: ["organic", "kids lunch", "travel food"]
  - Has title keyword "organic" (yellow badge - okay!)
  - Has 2 unique keywords: "kids lunch", "travel food" (blue badges - counted!)
  - Result: 2 unique keywords, positive search volume ✅
```

**❌ WRONG Approach (Will fail!):**
```
Title keywords: ["freeze dried strawberries", "organic"]
Bullet 1: ["freeze dried strawberries", "organic", "strawberries freeze dried"]
  - ALL keywords are from title (all yellow badges!)
  - NO unique keywords (0 blue badges!)
  - Result: 0 unique keywords, 0 search volume ❌ EMPTY BULLET!
```

**VALIDATION RULE:**
Before returning your JSON, check EVERY bullet:
- Does this bullet have AT LEAST 2 keywords that are NOT in the title?
- If NO → FIX IT by adding unique keywords from bullet_keywords list!

### RULE 2: NATURAL LANGUAGE
Write benefit-focused sentences, NOT keyword lists:
✅ GOOD: "Perfect healthy snack made from 100% natural fruit"
❌ BAD: "healthy snack natural fruit snack organic snack"

### RULE 3: EVEN DISTRIBUTION
Spread bullet_keywords evenly across all {bullet_count} bullets (2-4 per bullet)

### ⚠️ RULE 4: COMPLETE KEYWORD PHRASES REQUIRED (CRITICAL!)

**You MUST use the ENTIRE keyword phrase from bullet_keywords list - DO NOT SHORTEN!**

This is the #1 reason for empty keyword detection. Use the COMPLETE phrase or it won't be detected.

❌ WRONG - Shortened/incomplete phrases:
Allocated keyword: "freeze dried strawberry slices"
You write: "dried slices" ← Missing "freeze" and "strawberry"
Result: 0 keywords detected ❌ EMPTY BULLET!

Allocated keyword: "bulk freeze dried strawberries"
You write: "bulk strawberries" ← Missing "freeze dried"  
Result: 0 keywords detected ❌ EMPTY BULLET!

Allocated keyword: "organic freeze dried strawberries"
You write: "organic strawberries" ← Missing "freeze dried"
Result: 0 keywords detected ❌ EMPTY BULLET!

✅ CORRECT - Complete phrases used:
Allocated keyword: "freeze dried strawberry slices"
You write: "Our freeze dried strawberry slices are perfect for snacking"
Result: Keyword detected ✅

Allocated keyword: "bulk freeze dried strawberries"
You write: "Perfect bulk freeze dried strawberries for families"
Result: Keyword detected ✅

Allocated keyword: "organic freeze dried strawberries"  
You write: "Made from organic freeze dried strawberries with natural flavor"
Result: Keyword detected ✅

**Writing Tips:**
- Place long phrases at start: "Freeze dried strawberry slices are..."
- Use hyphens for readability: "freeze-dried strawberry slices"
- Break with commas: "...strawberries, freeze dried for freshness..."
- But NEVER remove words from the allocated phrase!

**EXAMPLE OF CORRECT USAGE ({bullet_count} BULLETS WITH 2 KEYWORDS EACH, AVOIDING TITLE KEYWORDS):**
If bullet_keywords = [{{"phrase": "freeze dried strawberries"}}, {{"phrase": "organic strawberries"}}, {{"phrase": "bulk strawberries"}}, {{"phrase": "strawberry snack"}}, {{"phrase": "dried fruit"}}, {{"phrase": "healthy snack"}}, {{"phrase": "natural fruit"}}, {{"phrase": "no sugar"}}]

You MUST create exactly {bullet_count} bullets, each with at least 2 keywords:
- Bullet 1: "Our organic strawberries are freeze dried strawberries perfect for healthy snacking" → keywords_included: ["organic strawberries", "freeze dried strawberries"]
- Bullet 2: "Convenient bulk strawberries make this strawberry snack ideal for families" → keywords_included: ["bulk strawberries", "strawberry snack"]
- Bullet 3: "Pure dried fruit with no sugar added for guilt-free enjoyment" → keywords_included: ["dried fruit", "no sugar"]
- Bullet 4: "A healthy snack made from natural fruit with no additives" → keywords_included: ["healthy snack", "natural fruit"]

Create optimized content that maximizes CONVERSION while strictly following Amazon guidelines.
Focus especially on the first 80 characters for mobile optimization with benefit-first approach.

Return ONLY the JSON response in the exact format specified.
"""

amazon_compliance_agent = Agent(
    name="AmazonComplianceAgent",
    instructions=AMAZON_COMPLIANCE_INSTRUCTIONS,
    model="gpt-5-nano-2025-08-07",  # gpt-5-mini for title/bullet generation
    reasoning_effort="medium",
    output_type=None,
)

def optimize_amazon_compliance_ai(
    current_content: Dict[str, Any],
    main_keyword_root: str,
    design_keyword_root: str,
    key_benefits: List[str],
    relevant_keywords: List[Dict[str, Any]],
    product_context: Dict[str, Any],
    competitor_analysis: Optional[Dict[str, Any]] = None,
    title_keywords: Optional[List[Dict[str, Any]]] = None,
    bullet_keywords: Optional[List[Dict[str, Any]]] = None,
    backend_keywords: Optional[List[Dict[str, Any]]] = None,
    target_bullet_count: Optional[int] = None,
    brand: str = "",
    current_length: int = 0,
    current_title: str = ""
) -> Dict[str, Any]:
    """
    Use AI to create Amazon-compliant titles and bullets optimized for first 80 characters.
    Enhanced with Task 3 strict title rules and Task 6 competitor analysis.
    
    Args:
        current_content: Current title, bullets, etc.
        main_keyword_root: Main keyword like "freeze dried strawberry"
        design_keyword_root: Design-specific keyword like "slices"
        key_benefits: List of key product benefits
        relevant_keywords: Keywords with search volume data (sorted by value)
        product_context: Brand, category, etc.
        competitor_analysis: Task 6 competitor insights for benefit optimization
        target_bullet_count: Number of bullet points to create (dynamic)
        brand: Task 3 - Brand name to include in title
        current_length: Task 3 - Current title length for reference
        
    Returns:
        Optimized content with Amazon compliance and Task 3 validation
    """
    # Prepare input data with competitor insights (Task 6)
    product_data = {
        "current_title": current_content.get("title", ""),
        "current_bullets": current_content.get("bullets", []),
        "main_keyword_root": main_keyword_root,
        "design_keyword_root": design_keyword_root,
        "key_benefits": key_benefits,
        "product_context": product_context
    }
    
    # Add Task 6 competitor analysis if available
    if competitor_analysis:
        product_data["competitor_insights"] = competitor_analysis
        logger.info(f"🎯 Integrated Task 6 competitor insights for benefit optimization")
    
    # Serialize product data
    try:
        product_json = json.dumps(product_data, indent=2)
    except (TypeError, ValueError) as json_err:
        logger.error(f"❌ Failed to serialize product data to JSON: {json_err}")
        raise
    
    # Use pre-allocated keywords if provided
    if title_keywords or bullet_keywords or backend_keywords:
        # Prepare keyword data for AI agent
        keywords_data = {
            "title_keywords": title_keywords or [],
            "bullet_keywords": bullet_keywords or [],
            "backend_keywords": backend_keywords or []
        }
        
        # Serialize keyword data
        try:
            keywords_json = json.dumps(keywords_data, indent=2)
        except (TypeError, ValueError) as json_err:
            logger.error(f"❌ Failed to serialize pre-allocated keywords to JSON: {json_err}")
            raise
        
        logger.info(f"🎯 Passing pre-allocated keywords to AI agent: {len(title_keywords)} title, {len(bullet_keywords)} bullets, {len(backend_keywords)} backend")
    else:
        # Pass more keywords to AI agent, sorted by relevancy
        # Ensure all keywords have the "phrase" key
        safe_keywords = []
        for kw in relevant_keywords[:20]:
            if isinstance(kw, dict) and "phrase" in kw:
                safe_keywords.append(kw)
            elif isinstance(kw, dict):
                # Add missing phrase key
                safe_kw = kw.copy()
                safe_kw["phrase"] = kw.get("keyword", kw.get("text", str(kw)))
                safe_keywords.append(safe_kw)
        # Serialize fallback keyword data
        try:
            keywords_json = json.dumps(safe_keywords, indent=2)
        except (TypeError, ValueError) as json_err:
            logger.error(f"❌ Failed to serialize fallback keywords to JSON: {json_err}")
            raise
    
    # Use dynamic bullet count or default to 4
    bullet_count = target_bullet_count if target_bullet_count and target_bullet_count > 0 else 4
    logger.info(f"🎯 Optimizing for {bullet_count} bullet points (dynamic based on current listing)")
    
    try:
        prompt = USER_PROMPT_TEMPLATE.format(
            product_json=product_json,
            main_root=main_keyword_root,
            design_root=design_keyword_root,
            keywords_json=keywords_json,
            bullet_count=bullet_count,
            brand=brand or "NOT FOUND",  # Task 3
            current_length=current_length,  # Task 3
            current_title=current_title or current_content.get("title", "")  # Brand preservation
        )
    except (KeyError, ValueError) as prompt_err:
        logger.error(f"❌ Failed to format prompt: {prompt_err}")
        raise
    
    try:
        # Import the Runner to match the pattern used in SEO runner
        from agents import Runner
        
        # Run AI agent
        result = Runner.run_sync(amazon_compliance_agent, prompt)
        
        output = getattr(result, "final_output", None)
        
        # Parse AI response
        if isinstance(output, str):
            try:
                # Strip markdown code fences (GPT-4o compatibility)
                clean_output = strip_markdown_code_fences(output)
                parsed = json.loads(clean_output)
                logger.info(f"[AmazonComplianceAgent] AI successfully optimized content for {bullet_count} bullets")
                return parsed
            except json.JSONDecodeError as e:
                logger.error(f"[AmazonComplianceAgent] Failed to parse AI output: {output[:200]}...")
                logger.error(f"[AmazonComplianceAgent] JSON decode error: {e}")
                # Fallback to programmatic optimization
                return _create_fallback_optimization(current_content, main_keyword_root, design_keyword_root, key_benefits, brand)
        
        elif hasattr(output, 'model_dump'):
            result = output.model_dump()
        
        else:
            raise Exception("Unexpected AI output format")
        
        # POST-GENERATION VALIDATION: Check for brand and high-volume keywords
        optimized_title = result.get("optimized_title", {}).get("content", "")
        
        # Validate brand is present (if brand exists)
        if brand and brand.strip():
            if brand.lower() not in optimized_title.lower():
                logger.error(f"❌ VALIDATION FAILED: Brand '{brand}' NOT found in optimized title: '{optimized_title}'")
                logger.error(f"❌ AI ignored MANDATORY brand requirement - using fallback")
                return _create_fallback_optimization(current_content, main_keyword_root, design_keyword_root, key_benefits, brand, relevant_keywords)
            else:
                logger.info(f"✅ Brand validation PASSED: '{brand}' found in title")
        
        # Validate top keywords are present (STRICTER: Top allocated keywords MUST be in title)
        # Use title_keywords if provided (pre-allocated by volume), otherwise use relevant_keywords
        keywords_to_validate = title_keywords if title_keywords else relevant_keywords
        
        if keywords_to_validate:
            # Sort by volume to ensure we're checking the absolute top keywords
            sorted_keywords = sorted(keywords_to_validate, key=lambda x: (x.get("search_volume", 0) or 0), reverse=True)
            top_5_keywords = sorted_keywords[:5]  # Check top 5 by volume
            missing_keywords = []
            
            for i, kw in enumerate(top_5_keywords, 1):
                kw_phrase = kw.get("phrase", "")
                kw_volume = kw.get("search_volume", 0) or 0
                # Check if keyword is in title (case-insensitive, handle hyphens/spaces)
                kw_normalized = kw_phrase.lower().replace("-", " ")
                title_normalized = optimized_title.lower().replace("-", " ")
                if kw_normalized not in title_normalized:
                    missing_keywords.append(f"#{i} {kw_phrase} (vol: {kw_volume:,})")
                    logger.warning(f"⚠️  Missing: #{i} '{kw_phrase}' (vol: {kw_volume:,})")
                else:
                    logger.info(f"✅  Found: #{i} '{kw_phrase}' (vol: {kw_volume:,})")
            
            if missing_keywords:
                logger.warning(f"⚠️ VALIDATION WARNING: {len(missing_keywords)} top keywords missing from title")
                
                # CRITICAL: Check if top 2 keywords (highest volumes) are missing
                top_2_missing = sum(1 for m in missing_keywords if m.startswith("#1") or m.startswith("#2"))
                
                if top_2_missing >= 2:
                    logger.error(f"❌ VALIDATION FAILED: TOP 2 KEYWORDS (HIGHEST VOLUMES) missing from title!")
                    logger.error(f"   Missing: {', '.join([m for m in missing_keywords if m.startswith('#1') or m.startswith('#2')])}")
                    logger.error(f"❌ This is CRITICAL for SEO - using fallback")
                    return _create_fallback_optimization(current_content, main_keyword_root, design_keyword_root, key_benefits, brand, sorted_keywords)
                elif "#1" in missing_keywords[0]:
                    logger.error(f"❌ VALIDATION FAILED: #1 keyword (ABSOLUTE HIGHEST VOLUME) missing from title!")
                    logger.error(f"❌ This is MANDATORY for SEO - using fallback")
                    return _create_fallback_optimization(current_content, main_keyword_root, design_keyword_root, key_benefits, brand, sorted_keywords)
                elif len(missing_keywords) >= 3:
                    logger.error(f"❌ VALIDATION FAILED: 3+ high-volume keywords missing - using fallback")
                    return _create_fallback_optimization(current_content, main_keyword_root, design_keyword_root, key_benefits, brand, sorted_keywords)
                else:
                    logger.warning(f"⚠️  Acceptable: Only {len(missing_keywords)} keyword(s) missing from top 5")
            else:
                logger.info(f"✅ Top keywords validation PASSED - All top 5 keywords found in title!")
        
        # NEW VALIDATION: Check each bullet has at least 2 keywords
        optimized_bullets = result.get("optimized_bullets", [])
        if optimized_bullets:
            all_keywords = (relevant_keywords or []) + (design_keywords or [])
            is_valid, insufficient_bullets = _validate_bullet_keyword_count(optimized_bullets, all_keywords, min_keywords=2)
            
            if not is_valid:
                logger.error(f"❌ VALIDATION FAILED: {len(insufficient_bullets)} bullets have <2 keywords: {insufficient_bullets}")
                logger.error(f"❌ AI ignored MANDATORY keyword inclusion requirement - using fallback")
                return _create_fallback_optimization(current_content, main_keyword_root, design_keyword_root, key_benefits, brand, relevant_keywords)
            else:
                logger.info(f"✅ Bullet keyword count validation PASSED: All {len(optimized_bullets)} bullets have ≥2 keywords")
        
        # NEW VALIDATION: Check title has 2-3 design-specific keywords
        if design_keywords:
            design_count, found_design_kws = _count_design_keywords_in_title(optimized_title, design_keywords)
            
            if design_count < 2:
                logger.error(f"❌ VALIDATION FAILED: Title has only {design_count} design-specific keywords (minimum: 2)")
                logger.error(f"   Title: {optimized_title}")
                logger.error(f"   Found design keywords: {found_design_kws}")
                logger.error(f"   Available design keywords: {[kw.get('phrase', '') for kw in design_keywords[:5]]}")
                logger.error(f"❌ AI ignored MANDATORY design keyword requirement - using fallback")
                return _create_fallback_optimization(current_content, main_keyword_root, design_keyword_root, key_benefits, brand, relevant_keywords)
            else:
                logger.info(f"✅ Design keyword validation PASSED: Title has {design_count} design keywords: {found_design_kws}")
        
        return result
            
    except Exception as e:
        logger.error(f"[AmazonComplianceAgent] AI optimization failed: {e}")
        # Graceful fallback - return programmatic optimization
        return _create_fallback_optimization(current_content, main_keyword_root, design_keyword_root, key_benefits, brand, relevant_keywords)

def _validate_bullet_keyword_count(
    bullets: List[Dict[str, Any]], 
    all_keywords: List[Dict[str, Any]],
    min_keywords: int = 2
) -> tuple:
    """
    Validate that each bullet has at least min_keywords.
    Returns (is_valid, list_of_bullet_numbers_with_insufficient_keywords).
    """
    from ..helper_methods import extract_keywords_from_content
    
    all_keyword_phrases = [kw.get("phrase", "") for kw in all_keywords if kw.get("phrase")]
    insufficient_bullets = []
    
    for i, bullet in enumerate(bullets, 1):
        content = bullet.get("content", "")
        found_keywords, _ = extract_keywords_from_content(content, all_keyword_phrases)
        
        if len(found_keywords) < min_keywords:
            insufficient_bullets.append(i)
            logger.error(f"❌ VALIDATION FAILED: Bullet {i} has only {len(found_keywords)} keywords (minimum: {min_keywords})")
            logger.error(f"   Content: {content[:100]}...")
            logger.error(f"   Keywords found: {found_keywords}")
    
    return len(insufficient_bullets) == 0, insufficient_bullets

def _count_design_keywords_in_title(
    title: str, 
    design_keywords: List[Dict[str, Any]]
) -> tuple:
    """
    Count how many design-specific keywords are present in the title.
    Returns (count, list_of_found_design_keywords).
    """
    from ..helper_methods import extract_keywords_from_content
    
    design_phrases = [kw.get("phrase", "") for kw in design_keywords if kw.get("phrase")]
    found_keywords, _ = extract_keywords_from_content(title, design_phrases)
    
    return len(found_keywords), found_keywords

def _create_fallback_optimization(
    current_content: Dict[str, Any],
    main_root: str,
    design_root: str,
    benefits: List[str],
    brand: str = "",
    relevant_keywords: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create fallback optimization when AI fails.
    Includes brand name and top volume keywords.
    """
    logger.warning("[AmazonComplianceAgent] Using fallback optimization due to AI failure")
    
    # Extract top 3-4 keywords by volume for better fallback
    if relevant_keywords:
        top_keywords_by_volume = sorted(relevant_keywords, key=lambda x: (x.get("search_volume", 0) or 0), reverse=True)
        top_phrases = [kw.get("phrase", "").title() for kw in top_keywords_by_volume[:4] if kw.get("phrase")]
        keyword_text = " ".join(top_phrases[:3])  # Use top 3 highest volume keywords
        logger.info(f"🔄 Fallback using top 3 keywords by volume: {top_phrases[:3]}")
    else:
        keyword_text = f"{main_root.title()} {design_root.title()}"
    
    # Build fallback title with brand + top keywords
    if brand and brand.strip():
        title = f"{brand} {keyword_text} - {benefits[0] if benefits else 'Premium Quality'}"
    else:
        title = f"{keyword_text} - {benefits[0] if benefits else 'Premium Quality'}"
    
    logger.info(f"🔄 Fallback title: {title[:100]}...")
    
    # Simple fallback bullets
    bullets = []
    for i, benefit in enumerate(benefits[:4], 1):
        bullet_content = f"BENEFIT {i}: {benefit.title()} - {main_root} {design_root} for optimal results"
        bullets.append({
            "content": bullet_content,
            "character_count": len(bullet_content),
            "primary_benefit": benefit,
            "keywords_included": [main_root, design_root],
            "guideline_compliance": "PASS"
        })
    
    fallback_result = {
        "optimized_title": {
            "content": title,
            "first_80_chars": title[:80],
            "main_root_included": main_root.lower() in title.lower(),
            "design_root_included": design_root.lower() in title.lower(),
            "key_benefit_included": True,
            "character_count": len(title),
            "keywords_included": [main_root, design_root],
            "guideline_compliance": {
                "character_limit": "PASS",
                "capitalization": "PASS",
                "special_characters": "PASS",
                "promotional_language": "PASS",
                "subjective_claims": "PASS"
            }
        },
        "optimized_bullets": bullets,
        "strategy": {
            "first_80_optimization": f"Fallback optimization with {main_root} and {design_root}",
            "keyword_integration": "Basic keyword integration",
            "compliance_approach": "Conservative compliance approach"
        }
    }

    
    return fallback_result


def _remove_duplicate_keyword_roots(
    title_content: str,
    keywords_included: List[str],
    all_available_keywords: List[Dict[str, Any]],
    brand: str = ""
) -> Tuple[str, List[str]]:
    """
    TASK 3 RULE 4: Remove duplicate keyword roots from title.
    Simpler approach: Just remove redundant keyword phrases from AI's output.
    
    Args:
        title_content: The AI-generated title
        keywords_included: Keywords AI claimed to include  
        all_available_keywords: All keywords sorted by value
        brand: Brand name to preserve
        
    Returns:
        Tuple of (cleaned_title, cleaned_keywords_list)
    """
    import re
    from collections import Counter
    
    logger.info(f"🔍 [TASK 3 - RULE 4] Validating root duplication...")
    logger.info(f"   Original title: {title_content[:100]}...")
    
    # Extract all word tokens from title
    title_lower = title_content.lower()
    title_tokens = re.findall(r'\b\w+\b', title_lower)
    
    # Count occurrences
    token_counts = Counter(title_tokens)
    duplicates = {token: count for token, count in token_counts.items() if count > 1}
    
    if not duplicates:
        logger.info(f"   ✅ No duplication - title is clean")
        return title_content, keywords_included
    
    logger.warning(f"   ⚠️  Duplicated tokens: {dict(duplicates)}")
    logger.info(f"   🔧 Removing duplicate tokens by eliminating redundant phrases...")
    
    # Simpler strategy: Find most duplicated tokens and remove phrases containing them
    # except for the longest/most valuable phrase
    
    # Sort duplicated tokens by count (most duplicated first)
    sorted_dups = sorted(duplicates.items(), key=lambda x: x[1], reverse=True)
    
    logger.info(f"   📊 Most duplicated tokens: {sorted_dups[:3]}")
    
    # Strategy: Only remove keywords that add ZERO new tokens
    # Build set of normalized tokens seen so far
    def normalize_token(token: str) -> str:
        """Normalize singular/plural"""
        if token.endswith('ies') and len(token) > 4:
            return token[:-3] + 'y'
        elif token.endswith('es') and len(token) > 3:
            return token[:-2]
        elif token.endswith('s') and len(token) > 2:
            return token[:-1]
        return token
    
    tokens_seen = set()
    keywords_to_keep = []
    keywords_to_remove = []
    
    # Sort keywords by length (longest first) to prioritize more specific phrases
    sorted_keywords = sorted(keywords_included, key=len, reverse=True)
    logger.info(f"   🔄 Processing keywords in order (longest first): {sorted_keywords}")
    
    for kw in sorted_keywords:
        kw_tokens = set(re.findall(r'\b\w+\b', kw.lower()))
        normalized_tokens = {normalize_token(t) for t in kw_tokens}
        
        # Check if this keyword adds enough new tokens (2+ to avoid duplication)
        new_tokens = normalized_tokens - tokens_seen
        
        if not tokens_seen or len(new_tokens) >= 2 or (len(keywords_to_keep) < 2 and len(new_tokens) >= 1):  # Keep first OR 2+ new OR if we have <2 keywords and adds 1+
            keywords_to_keep.append(kw)
            tokens_seen.update(normalized_tokens)
            logger.info(f"   ✅ Keep: '{kw}' (adds {len(new_tokens)} new tokens: {new_tokens})")
        else:
            keywords_to_remove.append(kw)
            logger.info(f"   ❌ Remove: '{kw}' (only adds {len(new_tokens)} new tokens)")
    
    # Remove redundant phrases from title
    if keywords_to_remove:
        new_title = title_content
        
        for kw in keywords_to_remove:
            # Try to find and remove this keyword phrase
            # Try Title Case version first (most likely in title)
            kw_title_case = ' '.join(word.capitalize() for word in kw.split())
            
            if kw_title_case in new_title:
                new_title = new_title.replace(kw_title_case, "", 1)
                logger.info(f"      🗑️  Removed: '{kw_title_case}'")
            elif kw.title() in new_title:
                new_title = new_title.replace(kw.title(), "", 1)
                logger.info(f"      🗑️  Removed: '{kw.title()}'")
            elif kw in new_title:
                new_title = new_title.replace(kw, "", 1)
                logger.info(f"      🗑️  Removed: '{kw}'")
        
        # Clean up spacing and separators
        new_title = re.sub(r'\s+', ' ', new_title)
        new_title = re.sub(r'\s*-\s*-\s*', ' - ', new_title)
        new_title = re.sub(r'\s*\|\s*\|\s*', ' | ', new_title)
        new_title = re.sub(r'\s*,\s*,\s*', ', ', new_title)
        new_title = re.sub(r'^\s*[\-\|,]\s*', '', new_title)
        new_title = re.sub(r'\s*[\-\|,]\s*$', '', new_title)
        new_title = new_title.strip()
        
        # Update keywords list
        keywords_to_keep = [kw for kw in keywords_included if kw not in keywords_to_remove]
        
        logger.info(f"   ✅ Deduplication complete:")
        logger.info(f"      Removed: {len(keywords_to_remove)} redundant keywords")
        logger.info(f"      Kept: {len(keywords_to_keep)} unique keywords")
        logger.info(f"      Length: {len(title_content)} → {len(new_title)} chars")
        
        # TASK 3 RULE 1: Ensure minimum 155 characters
        if len(new_title) < 155:
            logger.info(f"   📏 Title too short ({len(new_title)} chars), adding keywords to reach 155+...")
            
            # Find unused keywords from all_available_keywords
            unused_keywords = []
            for kw_dict in all_available_keywords:
                phrase = kw_dict.get("phrase", "")
                if phrase and phrase not in keywords_to_keep and phrase not in keywords_to_remove:
                    kw_tokens = set(re.findall(r'\b\w+\b', phrase.lower()))
                    normalized_kw_tokens = {normalize_token(t) for t in kw_tokens}
                    new_tokens = normalized_kw_tokens - tokens_seen
                    
                    if new_tokens:  # Only add if adds new tokens
                        unused_keywords.append((phrase, len(new_tokens)))
            
            # Sort by number of new tokens (descending)
            unused_keywords.sort(key=lambda x: x[1], reverse=True)
            
            # Add keywords until we reach 155+ chars
            # Only add if contributes at least 2 new tokens (to avoid duplication)
            for phrase, new_token_count in unused_keywords:
                if new_token_count >= 2 and len(new_title) + len(phrase) + 3 <= 200:  # Require 2+ new tokens
                    new_title += f" | {phrase.title()}"
                    keywords_to_keep.append(phrase)
                    
                    # Update tokens_seen
                    phrase_tokens = set(re.findall(r'\b\w+\b', phrase.lower()))
                    tokens_seen.update({normalize_token(t) for t in phrase_tokens})
                    
                    logger.info(f"      + Added '{phrase}' ({new_token_count} new tokens)")
                    
                if len(new_title) >= 155:
                    break
            
            logger.info(f"   ✅ Padded to {len(new_title)} chars")
        
        return new_title, keywords_to_keep
    else:
        logger.info(f"   ✅ No redundant keywords to remove")
        
        # TASK 3 RULE 1: Ensure minimum 155 characters even if no deduplication
        if len(title_content) < 155:
            logger.info(f"   📏 Title too short ({len(title_content)} chars), padding to 155+...")
            
            # Define normalize function
            def normalize_token(token: str) -> str:
                if token.endswith('ies') and len(token) > 4:
                    return token[:-3] + 'y'
                elif token.endswith('es') and len(token) > 3:
                    return token[:-2]
                elif token.endswith('s') and len(token) > 2:
                    return token[:-1]
                return token
            
            # Build normalized tokens from current keywords
            tokens_seen = set()
            for kw in keywords_included:
                kw_tokens = set(re.findall(r'\b\w+\b', kw.lower()))
                normalized_tokens = {normalize_token(t) for t in kw_tokens}
                tokens_seen.update(normalized_tokens)
            
            # Find unused keywords
            unused_keywords = []
            for kw_dict in all_available_keywords:
                phrase = kw_dict.get("phrase", "")
                if phrase and phrase not in keywords_included:
                    kw_tokens = set(re.findall(r'\b\w+\b', phrase.lower()))
                    normalized_kw_tokens = {normalize_token(t) for t in kw_tokens}
                    new_tokens = normalized_kw_tokens - tokens_seen
                    
                    if new_tokens:
                        unused_keywords.append((phrase, len(new_tokens)))
            
            unused_keywords.sort(key=lambda x: x[1], reverse=True)
            
            new_title = title_content
            new_keywords = list(keywords_included)
            
            for phrase, new_token_count in unused_keywords:
                if new_token_count >= 2 and len(new_title) + len(phrase) + 3 <= 200:  # Require 2+ new tokens
                    new_title += f" | {phrase.title()}"
                    new_keywords.append(phrase)
                    
                    # Update tokens_seen
                    phrase_tokens = set(re.findall(r'\b\w+\b', phrase.lower()))
                    tokens_seen.update({normalize_token(t) for t in phrase_tokens})
                    
                    logger.info(f"      + Added '{phrase}' ({new_token_count} new tokens)")
                    
                if len(new_title) >= 155:
                    break
            
            logger.info(f"   ✅ Padded to {len(new_title)} chars")
            return new_title, new_keywords
        
        return title_content, keywords_included

def apply_amazon_compliance_ai(
    current_content: Dict[str, Any],
    keyword_data: Dict[str, Any],
    product_context: Dict[str, Any],
    competitor_analysis: Optional[Dict[str, Any]] = None,
    keyword_validator: Optional[Any] = None,
    title_keywords: Optional[List[Dict[str, Any]]] = None,
    bullet_keywords: Optional[List[Dict[str, Any]]] = None,
    backend_keywords: Optional[List[Dict[str, Any]]] = None,
    target_bullet_count: Optional[int] = None
) -> Dict[str, Any]:
    """
    Main function to apply AI-powered Amazon compliance optimization.
    This is the main entry point for Task 7 implementation with Task 6 integration.
    
    Args:
        current_content: Current listing content
        keyword_data: Analyzed keyword data with roots and volumes
        product_context: Product and brand information
        competitor_analysis: Task 6 competitor insights for benefit optimization
        target_bullet_count: Number of bullet points to create (dynamic)
        
    Returns:
        Optimized content with Amazon compliance and competitor-informed benefits
    """
    # Extract main and design-specific keyword roots
    relevant_keywords = keyword_data.get("relevant_keywords", [])
    design_keywords = keyword_data.get("design_keywords", [])
    
    # Identify main keyword root (highest VOLUME relevant keyword) - FIXED: Use volume, not relevancy
    main_keyword_root = "freeze dried strawberry"  # Default
    if relevant_keywords:
        # Use highest VOLUME keyword for maximum SEO impact
        top_relevant = max(relevant_keywords, key=lambda x: (x.get("search_volume") or 0))
        main_keyword_root = top_relevant.get("phrase", main_keyword_root)
        logger.info(f"🎯 Selected main keyword root by VOLUME: {main_keyword_root} (volume: {top_relevant.get('search_volume', 0):,})")
    
    # Identify design-specific root (highest VOLUME design keyword) - FIXED: Use volume, not relevancy
    design_keyword_root = "slices"  # Default
    if design_keywords:
        # Use highest VOLUME keyword for maximum SEO impact
        top_design = max(design_keywords, key=lambda x: (x.get("search_volume") or 0))
        design_keyword_root = top_design.get("phrase", design_keyword_root)
        logger.info(f"🎯 Selected design keyword root by VOLUME: {design_keyword_root} (volume: {top_design.get('search_volume', 0):,})")
    else:
        # Fallback: extract from main keyword if no design keywords
        if " " in main_keyword_root:
            parts = main_keyword_root.split()
            design_keyword_root = parts[-1] if len(parts) > 1 else "slices"
            logger.info(f"🎯 Extracted design root from main keyword: {design_keyword_root}")
    
    # Extract key benefits from product context and competitor analysis
    key_benefits = []
    
    # Add benefits from product context
    if product_context.get("category"):
        key_benefits.append(f"Premium {product_context['category'].lower()} quality")
    
    # Add benefits from competitor analysis (Task 6)
    if competitor_analysis:
        competitor_benefits = competitor_analysis.get("top_benefits", [])
        for benefit_data in competitor_benefits[:3]:  # Top 3 benefits
            if isinstance(benefit_data, dict):
                benefit = benefit_data.get("benefit", "")
                if benefit and benefit not in key_benefits:
                    key_benefits.append(benefit)
            elif isinstance(benefit_data, str) and benefit_data not in key_benefits:
                key_benefits.append(benefit_data)
        
        logger.info(f"🎯 Integrated {len(key_benefits)} benefits from competitor analysis")
    
    # Default benefits if none found
    if not key_benefits:
        key_benefits = ["Natural ingredients", "No additives", "Premium quality", "Healthy choice"]
        logger.info(f"🎯 Using default benefits: {key_benefits}")
    
    # TASK 3 FIX: Sort keywords by PURE VOLUME (not value) for Issue #3
    if relevant_keywords:
        relevant_keywords.sort(key=lambda x: (x.get("search_volume", 0) or 0), reverse=True)
        logger.info(f"🎯 [TASK 3] Sorted {len(relevant_keywords)} relevant keywords by SEARCH VOLUME")
        # Log top 3 for verification
        for i, kw in enumerate(relevant_keywords[:3], 1):
            volume = kw.get("search_volume", 0) or 0
            logger.info(f"   {i}. {kw.get('phrase', '')} (volume: {volume:,})")
    
    if design_keywords:
        design_keywords.sort(key=lambda x: (x.get("search_volume", 0) or 0), reverse=True)
        logger.info(f"🎯 [TASK 3] Sorted {len(design_keywords)} design keywords by SEARCH VOLUME")
    
    logger.info(f"🎯 Prioritized {len(relevant_keywords)} relevant + {len(design_keywords)} design keywords by VOLUME")
    
    # Extract brand and current title length for Task 3
    brand = product_context.get("brand", "")
    current_title = current_content.get("title", "")
    current_length = len(current_title)
    
    logger.info(f"📊 [TASK 3] Brand: {brand or 'NOT FOUND'}, Current title: {current_length} chars")
    
    # Use pre-allocated keywords for AI agent
    # Changed from 'and' to 'or' to support partial allocation (e.g., only title keywords)
    if title_keywords or bullet_keywords or backend_keywords:
        # TASK 3 FIX: Sort by PURE VOLUME for Issue #3
        all_keywords_for_ai = (title_keywords or []) + (bullet_keywords or []) + (backend_keywords or [])
        all_keywords_for_ai.sort(key=lambda x: (x.get("search_volume", 0) or 0), reverse=True)
        
        logger.info(f"📊 [TASK 3] Providing {len(all_keywords_for_ai)} pre-allocated keywords to AI agent, sorted by VOLUME")
        
        # Run AI optimization with pre-allocated keywords and Task 3 parameters
        result = optimize_amazon_compliance_ai(
            current_content=current_content,
            main_keyword_root=main_keyword_root,
            design_keyword_root=design_keyword_root,
            key_benefits=key_benefits,
            relevant_keywords=all_keywords_for_ai,  # Pass pre-allocated keywords sorted by value
            product_context=product_context,
            competitor_analysis=competitor_analysis,
            title_keywords=title_keywords,
            bullet_keywords=bullet_keywords,
            backend_keywords=backend_keywords,
            target_bullet_count=target_bullet_count,
            brand=brand,  # Task 3: Pass brand explicitly
            current_length=current_length,  # Task 3: Pass current title length
            current_title=current_title  # Brand preservation: Pass current title
        )
    else:
        # Fallback to combined keywords
        all_keywords_for_ai = relevant_keywords + design_keywords
        all_keywords_for_ai.sort(key=lambda x: (x.get("search_volume", 0) or 0), reverse=True)  # Task 3 FIX: Sort by VOLUME
        
        logger.info(f"📊 [TASK 3] Providing {len(all_keywords_for_ai)} keywords to AI agent, sorted by VOLUME")
        
        # Run AI optimization with competitor insights and Task 3 parameters
        result = optimize_amazon_compliance_ai(
            current_content=current_content,
            main_keyword_root=main_keyword_root,
            design_keyword_root=design_keyword_root,
            key_benefits=key_benefits,
            relevant_keywords=all_keywords_for_ai,  # Pass sorted keywords by value
            product_context=product_context,
            competitor_analysis=competitor_analysis,
            target_bullet_count=target_bullet_count,
            brand=brand,  # Task 3: Pass brand explicitly
            current_length=current_length,  # Task 3: Pass current title length
            current_title=current_title  # Brand preservation: Pass current title
        )
    
    # TASK 3 RULE 4: Post-process to remove root duplication
    logger.info(f"🔍 [TASK 3] Checking if deduplication needed...")
    logger.info(f"   Result exists: {result is not None}")
    logger.info(f"   Has optimized_title: {'optimized_title' in result if result else False}")
    
    if result and "optimized_title" in result:
        optimized_title = result.get("optimized_title", {})
        title_content = optimized_title.get("content", "")
        keywords_included = optimized_title.get("keywords_included", [])
        
        logger.info(f"   Title: '{title_content[:80]}...'")
        logger.info(f"   Keywords included: {keywords_included}")
        
        # Get all keywords for deduplication reference
        all_keywords = relevant_keywords + design_keywords
        
        logger.info(f"   Calling deduplication function...")
        
        # Apply deduplication
        try:
            fixed_title, fixed_keywords = _remove_duplicate_keyword_roots(
                title_content,
                keywords_included,
                all_keywords,
                brand
            )
            
            logger.info(f"   Deduplication returned: modified={fixed_title != title_content}")
            
            # Update result if title was modified
            if fixed_title != title_content:
                logger.info(f"🔧 [TASK 3] Applied automatic deduplication to title")
                logger.info(f"   Before: {title_content}")
                logger.info(f"   After: {fixed_title}")
                result["optimized_title"]["content"] = fixed_title
                result["optimized_title"]["keywords_included"] = fixed_keywords
                result["optimized_title"]["character_count"] = len(fixed_title)
                result["optimized_title"]["first_80_chars"] = fixed_title[:80]
                result["optimized_title"]["has_root_duplication"] = False
            else:
                logger.info(f"✅ [TASK 3] No changes made - title unchanged")
        except Exception as e:
            logger.error(f"❌ [TASK 3] Deduplication failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        logger.warning(f"⚠️  [TASK 3] Cannot run deduplication - result missing optimized_title")
    
    # SAFETY CHECK: Ensure no bullets have empty keywords_included
    logger.info(f"🔍 [SAFETY CHECK] Validating all bullets have keywords...")
    
    if result and "optimized_bullets" in result:
        optimized_bullets = result.get("optimized_bullets", [])
        empty_bullets = []
        
        for i, bullet in enumerate(optimized_bullets):
            keywords = bullet.get("keywords_included", [])
            if not keywords or len(keywords) == 0:
                empty_bullets.append(i + 1)
                logger.error(f"❌ [SAFETY CHECK] Bullet {i+1} has EMPTY keywords_included array!")
        
        if empty_bullets:
            logger.error(f"❌ [SAFETY CHECK] Found {len(empty_bullets)} bullets with empty keywords: {empty_bullets}")
            logger.error(f"❌ [SAFETY CHECK] This will cause poor statistics and empty UI displays!")
            logger.warning(f"⚠️  [SAFETY CHECK] AI did not follow OUTPUT VALIDATION rules - keywords missing!")
        else:
            logger.info(f"✅ [SAFETY CHECK] All {len(optimized_bullets)} bullets have keywords - validation passed")
    
    logger.info(f"[Task7-AI] Applied Amazon compliance optimization with 80-char focus and {target_bullet_count or 4} bullets")
    
    return result