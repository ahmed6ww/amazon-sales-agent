"""
Keyword Root Extraction Service

This service extracts meaningful root words from keyword lists to:
1. Reduce the number of keywords processed by grouping similar terms
2. Optimize Amazon search calls by focusing on root terms
3. Manage contextual memory more efficiently
4. Enable better keyword categorization and analysis
"""

import re
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict, Counter
from dataclasses import dataclass


@dataclass
class KeywordRoot:
    """Represents a meaningful keyword root with its variants"""
    root: str
    variants: List[str]
    frequency: int
    is_meaningful: bool
    category: str  # product_type, attribute, brand, etc.


# Stopwords and meaningless terms to filter out
MEANINGLESS_WORDS = {
    # Articles, prepositions, conjunctions
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'between', 'among', 'through', 'against', 'during', 'without', 'within',
    
    # Common generic terms
    'item', 'items', 'product', 'products', 'thing', 'things', 'stuff', 'piece', 'pieces',
    'set', 'sets', 'pack', 'packs', 'lot', 'lots', 'bundle', 'bundles',
    
    # Size/quantity terms (often not meaningful alone)
    'small', 'medium', 'large', 'big', 'little', 'tiny', 'huge', 'mini', 'xl', 'xxl',
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
    
    # Generic descriptors
    'new', 'old', 'best', 'good', 'better', 'great', 'awesome', 'amazing', 'perfect',
    'premium', 'quality', 'high', 'low', 'top', 'bottom', 'left', 'right',
    
    # Common ecommerce terms
    'buy', 'purchase', 'order', 'shop', 'shopping', 'store', 'online', 'cheap', 'sale',
    'discount', 'deal', 'deals', 'price', 'cost', 'free', 'shipping', 'delivery'
}

# Brand names to identify and group separately
KNOWN_BRANDS = {
    'amazon', 'prime', 'basics', 'choice', 'recommended', 'brand',
    # Food brands
    'organic', 'natural', 'fresh', 'pure', 'simply', 'nature', 'whole', 'raw',
    # Electronics brands
    'apple', 'samsung', 'sony', 'bose', 'jbl', 'anker', 'beats', 'lg', 'panasonic',
    # Kitchen brands
    'cuisinart', 'kitchenaid', 'ninja', 'vitamix', 'breville', 'hamilton', 'oster',
    # Baby brands
    'graco', 'chicco', 'britax', 'evenflo', 'fisher', 'price', 'pampers', 'huggies',
    # Fitness brands
    'nike', 'adidas', 'under', 'armour', 'reebok', 'bowflex', 'nordictrack',
    # General brands
    'driscoll', 'dole', 'del', 'monte', 'kirkland', 'trader', 'joes'
}

# Product type indicators
PRODUCT_TYPE_INDICATORS = {
    # Food categories
    'food', 'snack', 'fruit', 'vegetable', 'drink', 'beverage', 'supplement', 'vitamin',
    # Electronics categories
    'electronics', 'headphones', 'earbuds', 'speaker', 'charger', 'cable', 'phone', 'tablet',
    'computer', 'laptop', 'monitor', 'keyboard', 'mouse', 'camera', 'tv', 'smart', 'device',
    # Kitchen categories
    'kitchen', 'appliance', 'blender', 'mixer', 'oven', 'cooker', 'maker', 'machine',
    # Baby categories
    'baby', 'infant', 'toddler', 'child', 'stroller', 'carrier', 'seat', 'monitor', 'bottle',
    # Fitness categories
    'fitness', 'exercise', 'workout', 'gym', 'equipment', 'mat', 'weight', 'dumbbell', 'bike',
    # General categories
    'toy', 'game', 'book', 'clothing', 'apparel', 'home', 'furniture', 'decor'
}


def extract_meaningful_roots(keyword_list: List[str]) -> Dict[str, KeywordRoot]:
    """
    Extract meaningful root words from a list of keywords and group similar terms.
    
    Args:
        keyword_list: List of keyword phrases to analyze
        
    Returns:
        Dictionary mapping root words to KeywordRoot objects with variants
    """
    # Step 1: Tokenize all keywords and collect word frequencies
    word_frequency = Counter()
    keyword_tokens = {}
    
    for keyword in keyword_list:
        if not keyword or not isinstance(keyword, str):
            continue
            
        # Clean and tokenize the keyword
        tokens = tokenize_keyword(keyword.lower().strip())
        keyword_tokens[keyword] = tokens
        
        # Count word frequencies
        for token in tokens:
            word_frequency[token] += 1
    
    # Step 2: Identify meaningful words (filter out stopwords and low-frequency terms)
    meaningful_words = set()
    for word, freq in word_frequency.items():
        if (word not in MEANINGLESS_WORDS and 
            len(word) > 2 and  # Ignore very short words
            freq >= 2 and  # Must appear at least twice
            not word.isdigit()):  # Ignore pure numbers
            meaningful_words.add(word)
    
    # Step 3: Group keywords by their meaningful root words
    root_groups = defaultdict(list)
    root_frequencies = defaultdict(int)
    
    for keyword, tokens in keyword_tokens.items():
        meaningful_tokens = [t for t in tokens if t in meaningful_words]
        
        if meaningful_tokens:
            # Use the most frequent meaningful word as the root
            # or the longest meaningful word if frequencies are equal
            root = max(meaningful_tokens, 
                      key=lambda x: (word_frequency[x], len(x)))
            root_groups[root].append(keyword)
            root_frequencies[root] += 1
    
    # Step 4: Create KeywordRoot objects with categorization
    keyword_roots = {}
    
    for root, variants in root_groups.items():
        category = categorize_root_word(root)
        is_meaningful = len(variants) >= 2 or word_frequency[root] >= 3
        
        keyword_roots[root] = KeywordRoot(
            root=root,
            variants=sorted(variants),
            frequency=root_frequencies[root],
            is_meaningful=is_meaningful,
            category=category
        )
    
    return keyword_roots


def tokenize_keyword(keyword: str) -> List[str]:
    """
    Tokenize a keyword phrase into individual words, handling common variations.
    
    Args:
        keyword: The keyword phrase to tokenize
        
    Returns:
        List of cleaned tokens
    """
    # Remove special characters and split on whitespace/punctuation
    # Keep hyphens in compound words but split on them for analysis
    keyword = re.sub(r'[^\w\s-]', ' ', keyword)
    tokens = re.findall(r'\b\w+\b', keyword.lower())
    
    # Handle common word variations (plural/singular, past tense, etc.)
    normalized_tokens = []
    for token in tokens:
        normalized = normalize_word(token)
        if normalized:
            normalized_tokens.append(normalized)
    
    return normalized_tokens


def normalize_word(word: str) -> str:
    """
    Normalize word variations to their root form.
    Enhanced for Task 11 to handle singular/plural variations better.
    
    Args:
        word: The word to normalize
        
    Returns:
        Normalized root form of the word
    """
    if len(word) <= 2:
        return word
    
    # Simple stemming rules for common cases
    # Handle plurals (Task 11: Enhanced plural handling)
    if word.endswith('ies') and len(word) > 4:
        return word[:-3] + 'y'
    elif word.endswith('es') and len(word) > 4:
        # Handle -es endings that need -es removed (boxes -> box, dishes -> dish)
        if word.endswith(('shes', 'ches', 'xes', 'zes', 'ses')):
            return word[:-2]
        # For words ending in -es but not special cases, just remove 's' (apples -> apple, not appl)
        else:
            return word[:-1]
    elif word.endswith('s') and len(word) > 3 and not word.endswith('ss'):
        return word[:-1]
    
    # Handle past tense
    elif word.endswith('ed') and len(word) > 4:
        return word[:-2]
    
    # Handle -ing forms (better logic)
    elif word.endswith('ing') and len(word) > 5:
        # For words ending in -ing, try to remove -ing and see if it makes sense
        base = word[:-3]
        # Handle doubled consonants (running -> run, not runn)
        if len(base) >= 2 and base[-1] == base[-2] and base[-1] in 'bcdfghjklmnpqrstvwxyz':
            base = base[:-1]
        return base
    
    return word


def are_singular_plural_variants(phrase1: str, phrase2: str) -> bool:
    """
    Check if two keyword phrases are singular/plural variants of each other.
    Task 11: Determine if keywords like "strawberry freeze dried" and "strawberries freeze dried" 
    are variants that should not be suggested as alternatives to each other.
    
    Args:
        phrase1: First keyword phrase
        phrase2: Second keyword phrase
        
    Returns:
        True if they are singular/plural variants, False otherwise
    """
    if not phrase1 or not phrase2:
        return False
    
    # Tokenize both phrases WITHOUT normalization to preserve original forms
    tokens1 = re.findall(r'\b\w+\b', phrase1.lower().strip())
    tokens2 = re.findall(r'\b\w+\b', phrase2.lower().strip())
    
    # Must have same number of tokens
    if len(tokens1) != len(tokens2):
        return False
    
    # Check each token pair
    differences = 0
    for t1, t2 in zip(tokens1, tokens2):
        if t1 == t2:
            continue
        
        # Check if they are singular/plural variants by normalizing
        normalized1 = normalize_word(t1)
        normalized2 = normalize_word(t2)
        
        if normalized1 == normalized2:
            differences += 1
            # Only allow one difference (one word being singular/plural)
            if differences > 1:
                return False
        else:
            # Not a singular/plural variant
            return False
    
    # Must have exactly one difference that is a singular/plural variant
    return differences == 1


def are_pronoun_variants(phrase1: str, phrase2: str) -> bool:
    """
    Check if two keyword phrases differ only by pronouns/articles.
    Task 11: Determine if keywords like "strawberry freeze dried" and "the strawberry freeze dried" 
    are variants that should not be suggested as alternatives to each other.
    
    Args:
        phrase1: First keyword phrase
        phrase2: Second keyword phrase
        
    Returns:
        True if they differ only by pronouns/articles, False otherwise
    """
    if not phrase1 or not phrase2:
        return False
    
    # Common articles and pronouns to ignore
    ARTICLES_PRONOUNS = {'a', 'an', 'the', 'this', 'that', 'these', 'those'}
    
    # Tokenize and filter out articles/pronouns (without normalization to preserve originals)
    tokens1 = [t for t in re.findall(r'\b\w+\b', phrase1.lower().strip()) if t not in ARTICLES_PRONOUNS]
    tokens2 = [t for t in re.findall(r'\b\w+\b', phrase2.lower().strip()) if t not in ARTICLES_PRONOUNS]
    
    # After removing articles/pronouns, check if they are the same or singular/plural variants
    if len(tokens1) != len(tokens2):
        return False
    
    for t1, t2 in zip(tokens1, tokens2):
        if t1 != t2:
            # Check if this difference is just singular/plural
            if normalize_word(t1) != normalize_word(t2):
                return False
    
    return True


def are_keyword_variants(phrase1: str, phrase2: str) -> bool:
    """
    Check if two keyword phrases are variants that should not be suggested as alternatives.
    Task 11: Master function that checks for singular/plural and pronoun variants.
    
    Args:
        phrase1: First keyword phrase
        phrase2: Second keyword phrase
        
    Returns:
        True if they are variants (should not suggest as alternatives), False otherwise
    """
    return are_singular_plural_variants(phrase1, phrase2) or are_pronoun_variants(phrase1, phrase2)


def select_best_keyword_variant(keywords_with_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Select the best variant from a list of keyword variants.
    Task 11: Pick the variant with highest search volume if it makes sense for sentence structure,
    otherwise pick the variant that makes more sense grammatically.
    
    Args:
        keywords_with_data: List of keyword dicts with phrase, search_volume, etc.
        
    Returns:
        The best keyword variant dict
    """
    if not keywords_with_data:
        return {}
    
    if len(keywords_with_data) == 1:
        return keywords_with_data[0]
    
    # Sort by search volume (descending)
    sorted_by_volume = sorted(keywords_with_data, 
                             key=lambda x: x.get('search_volume', 0), 
                             reverse=True)
    
    highest_volume = sorted_by_volume[0]
    
    # Simple heuristic: prefer singular forms for better sentence structure
    # unless plural has significantly higher volume
    for keyword in sorted_by_volume:
        phrase = keyword.get('phrase', '')
        volume = keyword.get('search_volume', 0)
        highest_volume_amount = highest_volume.get('search_volume', 0)
        
        # If this variant has good volume (within 20% of highest) and better structure
        if volume >= highest_volume_amount * 0.8:
            tokens = re.findall(r'\b\w+\b', phrase.lower())
            # Prefer phrases that don't end with 's' (usually better for titles)
            if tokens and not tokens[-1].endswith('s'):
                return keyword
    
    # Default: return highest volume variant
    return highest_volume


def categorize_root_word(root: str) -> str:
    """
    Categorize a root word into semantic categories.
    
    Args:
        root: The root word to categorize
        
    Returns:
        Category string (product_type, attribute, brand, etc.)
    """
    if root in KNOWN_BRANDS:
        return 'brand'
    elif root in PRODUCT_TYPE_INDICATORS:
        return 'product_type'
    elif root in ['organic', 'natural', 'fresh', 'raw', 'pure', 'wild', 'whole', 'premium', 'professional']:
        return 'attribute_quality'
    elif root in ['dried', 'freeze', 'frozen', 'dehydrated', 'powdered', 'sliced', 'wireless', 'bluetooth', 'smart', 'electric', 'manual', 'automatic', 'digital', 'analog']:
        return 'attribute_processing'
    elif root in ['bulk', 'pound', 'ounce', 'gram', 'piece', 'slice', 'pack', 'set', 'pair', 'single', 'double', 'triple']:
        return 'attribute_quantity'
    elif root in ['strawberry', 'apple', 'banana', 'berry', 'fruit', 'vegetable', 'meat', 'fish', 'dairy']:
        return 'product_ingredient'
    elif root in ['waterproof', 'portable', 'lightweight', 'heavy', 'duty', 'adjustable', 'foldable', 'compact', 'large', 'small', 'mini']:
        return 'attribute_feature'
    elif root in ['black', 'white', 'red', 'blue', 'green', 'silver', 'gold', 'pink', 'purple', 'orange']:
        return 'attribute_color'
    else:
        return 'other'


def group_keywords_by_roots(keyword_list: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Main function to group keywords by meaningful roots for efficient processing.
    
    Args:
        keyword_list: List of keyword phrases
        
    Returns:
        Dictionary with root analysis and grouped keywords
    """
    keyword_roots = extract_meaningful_roots(keyword_list)
    
    # Filter to only meaningful roots and sort by importance
    meaningful_roots = {
        root: root_obj for root, root_obj in keyword_roots.items()
        if root_obj.is_meaningful
    }
    
    # Sort roots by frequency and category importance
    category_priority = {
        'product_ingredient': 5,
        'product_type': 4,
        'attribute_processing': 3,
        'attribute_quality': 2,
        'attribute_quantity': 1,
        'brand': 1,
        'other': 0
    }
    
    sorted_roots = sorted(
        meaningful_roots.items(),
        key=lambda x: (category_priority.get(x[1].category, 0), x[1].frequency),
        reverse=True
    )
    
    # Compile results
    result = {
        'total_keywords': len(keyword_list),
        'total_roots': len(keyword_roots),
        'meaningful_roots': len(meaningful_roots),
        'roots': {},
        'summary': {
            'top_product_ingredients': [],
            'top_processing_methods': [],
            'top_brands': []
        }
    }
    
    # Add root information
    for root, root_obj in sorted_roots:
        result['roots'][root] = {
            'variants': root_obj.variants,
            'frequency': root_obj.frequency,
            'category': root_obj.category,
            'variant_count': len(root_obj.variants)
        }
        
        # Populate summary
        if root_obj.category == 'product_ingredient':
            result['summary']['top_product_ingredients'].append(root)
        elif root_obj.category in ['attribute_processing', 'attribute_quality']:
            result['summary']['top_processing_methods'].append(root)
        elif root_obj.category == 'brand':
            result['summary']['top_brands'].append(root)
    
    # Limit summary lists
    result['summary']['top_product_ingredients'] = result['summary']['top_product_ingredients'][:10]
    result['summary']['top_processing_methods'] = result['summary']['top_processing_methods'][:10]
    result['summary']['top_brands'] = result['summary']['top_brands'][:5]
    
    return result


def get_priority_roots_for_search(keyword_analysis: Dict[str, Any], max_roots: int = 20) -> List[str]:
    """
    Get the most important root words for Amazon search optimization.
    
    Args:
        keyword_analysis: Result from group_keywords_by_roots()
        max_roots: Maximum number of roots to return
        
    Returns:
        List of priority root words for searching
    """
    roots_data = keyword_analysis.get('roots', {})
    
    # Prioritize by category and frequency
    priority_categories = ['product_ingredient', 'product_type', 'attribute_processing']
    priority_roots = []
    
    for category in priority_categories:
        category_roots = [
            (root, data) for root, data in roots_data.items()
            if data['category'] == category
        ]
        # Sort by frequency within category
        category_roots.sort(key=lambda x: x[1]['frequency'], reverse=True)
        priority_roots.extend([root for root, _ in category_roots])
    
    # Add other meaningful roots if we haven't reached max_roots
    if len(priority_roots) < max_roots:
        other_roots = [
            (root, data) for root, data in roots_data.items()
            if data['category'] not in priority_categories
        ]
        other_roots.sort(key=lambda x: x[1]['frequency'], reverse=True)
        priority_roots.extend([root for root, _ in other_roots])
    
    return priority_roots[:max_roots] 