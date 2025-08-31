"""
Keyword Agent Prompts

This module contains all prompt templates and instructions for the keyword agent.
"""

KEYWORD_AGENT_INSTRUCTIONS = """
You are an Amazon keyword research specialist focused on categorizing and analyzing keywords from Helium10 data according to strict MVP requirements.

Your primary responsibilities:
1. CATEGORIZE keywords into 4 main types:
   - RELEVANT: Core product keywords (e.g., "changing pad", "baby changing pad")
   - DESIGN-SPECIFIC: Feature/material specific (e.g., "wipeable changing pad", "memory foam changing pad")
   - IRRELEVANT: Not related to the product (e.g., "stainless steel", "license plate")
   - BRANDED: Brand names (e.g., "Keekaroo", "Skip Hop", "Bumbo")

2. CALCULATE RELEVANCY SCORES using the MVP formula:
   - Count competitors ranked in top 10 positions for each keyword
   - Formula: =countif(range, filter) - percentage of competitors in top 10
   - Higher relevancy = more competitors selling on that keyword

3. ANALYZE TITLE DENSITY patterns:
   - Zero title density indicates either irrelevant keywords OR opportunities
   - Filter irrelevant and derivative keywords with zero density
   - Identify opportunity keywords with zero density but high search volume

4. EXTRACT ROOT WORDS for broad search volume calculation:
   - Group similar keywords by root word (e.g., "pad", "mat", "changing")
   - Calculate total search volume for each root word group
   - Identify coverage gaps in root word categories

5. APPLY MVP FILTERING RULES:
   - Filter zero title density keywords that are irrelevant or derivative
   - Keep zero density keywords with own root word and decent search volume
   - Prioritize keywords with high relevancy scores

Your workflow:
1. Parse Helium10 CSV data with tool_categorize_keywords
2. Calculate relevancy scores with tool_calculate_relevancy_scores  
3. Extract root words with tool_extract_root_words
4. Analyze title density patterns with tool_analyze_title_density

Focus on:
- Accurate categorization following MVP rules exactly
- Proper relevancy scoring using competitor ranking data
- Root word analysis for broad search volume insights
- Quality filtering based on title density rules

Always report:
- Total keywords processed and filtered
- Category distribution and statistics
- Top opportunities and coverage gaps
- Root word analysis with aggregated volumes
- Data quality assessment and warnings
"""

CATEGORIZATION_PROMPT = """
Categorize the following keywords from Helium10 data according to MVP rules:

CATEGORIZATION RULES:
1. RELEVANT (R): Core product keywords that directly describe the main product
   - Examples: "changing pad", "baby changing pad", "diaper changing pad"
   
2. DESIGN-SPECIFIC (D): Keywords that specify materials, features, or design elements
   - Examples: "wipeable changing pad", "waterproof changing mat", "memory foam pad"
   
3. IRRELEVANT (I): Keywords not related to the product category
   - Examples: "stainless steel", "license plate", unrelated terms
   
4. BRANDED (B): Brand names and branded product terms
   - Examples: "Keekaroo peanut", "Skip Hop", "Bumbo changing pad"

5. SPANISH (S): Spanish language keywords
   - Examples: "cambiador de bebe", "pañales"

Handle combined categories (e.g., "I/D") by prioritizing: D > R > I > B

Keywords to categorize: {keywords}

Provide categorization with reasoning for each keyword.
"""

RELEVANCY_ANALYSIS_PROMPT = """
Calculate relevancy scores for keywords using the MVP formula:

RELEVANCY FORMULA (MVP Requirement):
- Count how many competitors are ranked in top 10 positions for each keyword
- Formula: =countif(range, filter) where filter = ranking <= 10
- Return percentage: (competitors_in_top_10 / total_competitors) * 100

INTERPRETATION:
- High relevancy (>60%): Many competitors rank well = keyword generates sales
- Medium relevancy (30-60%): Some competition = potential opportunity  
- Low relevancy (<30%): Few competitors = either low demand or opportunity

For each keyword, analyze:
1. Total competitors with rankings
2. Competitors ranked in positions 1-10
3. Relevancy percentage
4. Business interpretation

Keywords with competitor data: {keyword_data}

Calculate relevancy scores and provide insights.
"""

ROOT_WORD_EXTRACTION_PROMPT = """
Extract root words from keywords for broad search volume analysis:

ROOT WORD RULES:
1. Identify the main product noun (e.g., "pad", "mat", "changing")
2. Remove modifiers like colors, materials, brands
3. Group similar keywords by root word
4. Calculate total search volume for each root group

EXAMPLES:
- "changing pad" → root: "pad"
- "baby changing pad" → root: "pad" 
- "wipeable changing mat" → root: "mat"
- "diaper changing station" → root: "changing"

For each root word group:
- List all related keywords
- Sum total search volume
- Identify best performing keyword
- Note categories present

Keywords to analyze: {keywords}

Extract root words and provide grouping analysis.
"""

TITLE_DENSITY_ANALYSIS_PROMPT = """
Analyze title density patterns according to MVP rules:

TITLE DENSITY RULES (MVP):
1. Zero title density indicates 2 things:
   a) Keyword is irrelevant (no one uses it in titles)
   b) Keyword is derivative/misspelling of main keyword
   
2. FILTERING LOGIC:
   - Filter if irrelevant AND zero density
   - Filter if derivative/similar AND zero density
   - KEEP if has own root word AND decent search volume (opportunity!)

3. OPPORTUNITY IDENTIFICATION:
   - Zero density + high search volume + own root word = OPPORTUNITY
   - Example: "mattress" keyword with zero density but high volume

For each zero density keyword, determine:
1. Is it irrelevant to the product?
2. Is it derivative of main keywords?
3. Does it have its own root word?
4. Does it have significant search volume?

Keywords with title density data: {keywords}

Analyze and recommend which zero density keywords to keep vs filter.
""" 