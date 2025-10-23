"""
SEO Keyword Validator

Prevents keyword hallucination by ensuring only research-validated keywords are used
in SEO optimization. This class validates, tracks, and allocates keywords across
different content types (title, bullets, backend) while preventing duplication.
"""

import logging
from typing import Dict, List, Any, Set, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class SEOKeywordValidator:
    """
    Validates and manages keyword usage to prevent hallucination, duplication, and alteration.
    
    Key Features:
    1. Validates keywords against research data
    2. Tracks used keywords to prevent duplication
    3. Allocates keywords across content types
    4. Preserves exact keyword formatting
    5. Provides detailed logging for debugging
    """
    
    def __init__(self, research_keywords: List[Dict[str, Any]]):
        """
        Initialize validator with research keywords.
        
        Args:
            research_keywords: List of keyword dicts from research agent with phrase, relevancy_score, etc.
        """
        self.research_keywords = research_keywords
        self.used_keywords: Set[str] = set()
        self.keyword_phrases: Set[str] = set()
        self.keyword_data: Dict[str, Dict[str, Any]] = {}
        
        # Keyword allocation limits per content type (dynamic based on bullet count)
        self.keyword_allocation = {
            'title': 8,      # Max keywords for title (increased to ensure top-volume keywords are included)
            'bullets': 10,   # Max keywords for bullets (will be adjusted based on bullet count)
            'backend': 15    # Max keywords for backend
        }
        
        # Initialize keyword data
        self._initialize_keyword_data()
        
        logger.info(f"🔍 SEOKeywordValidator initialized with {len(self.research_keywords)} research keywords")
    
    def _initialize_keyword_data(self):
        """Initialize keyword phrases and data mapping."""
        for kw in self.research_keywords:
            phrase = kw.get("phrase", "").strip()
            if phrase:
                self.keyword_phrases.add(phrase.lower())
                self.keyword_data[phrase.lower()] = kw
        
        logger.info(f"📊 Initialized {len(self.keyword_phrases)} unique keyword phrases")
    
    def validate_keywords_against_research(self, keywords_to_validate: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validate keywords against research data.
        
        Args:
            keywords_to_validate: List of keyword phrases to validate
            
        Returns:
            Tuple of (valid_keywords, invalid_keywords)
        """
        valid_keywords = []
        invalid_keywords = []
        
        for keyword in keywords_to_validate:
            if not keyword or not isinstance(keyword, str):
                invalid_keywords.append(str(keyword))
                continue
                
            keyword_lower = keyword.strip().lower()
            
            if keyword_lower in self.keyword_phrases:
                # Find the original keyword with exact formatting
                original_keyword = self._get_original_keyword_format(keyword_lower)
                valid_keywords.append(original_keyword)
            else:
                invalid_keywords.append(keyword)
                logger.warning(f"🚫 Keyword hallucination detected: '{keyword}' not found in research data")
        
        if invalid_keywords:
            logger.warning(f"⚠️  Found {len(invalid_keywords)} invalid keywords: {invalid_keywords[:5]}")
        
        logger.info(f"✅ Validated {len(valid_keywords)}/{len(keywords_to_validate)} keywords against research data")
        
        return valid_keywords, invalid_keywords
    
    def _get_original_keyword_format(self, keyword_lower: str) -> str:
        """Get the original keyword format from research data."""
        for phrase in self.keyword_data.keys():
            if phrase.lower() == keyword_lower:
                # Return the original phrase from research data
                return self.keyword_data[phrase].get("phrase", phrase)
        return keyword_lower
    
    def get_top_keywords_by_relevancy(self, keywords: List[str], limit: int = 10) -> List[str]:
        """
        Get top keywords sorted by relevancy score.
        
        Args:
            keywords: List of valid keyword phrases
            limit: Maximum number of keywords to return
            
        Returns:
            List of top keywords sorted by relevancy score
        """
        # Get keyword data for sorting
        keyword_with_scores = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in self.keyword_data:
                kw_data = self.keyword_data[keyword_lower]
                keyword_with_scores.append({
                    'phrase': keyword,
                    'relevancy_score': kw_data.get('relevancy_score', 0) or 0,
                    'search_volume': kw_data.get('search_volume', 0) or 0,
                    'intent_score': kw_data.get('intent_score', 0) or 0
                })
        
        # Sort by SEARCH VOLUME first (descending), then by relevancy, then by intent score
        # Handle None values by treating them as 0
        sorted_keywords = sorted(keyword_with_scores, 
                               key=lambda x: (
                                   x['search_volume'] or 0,      # VOLUME FIRST for Issue #3
                                   x['relevancy_score'] or 0, 
                                   x['intent_score'] or 0
                               ), 
                               reverse=True)
        
        top_keywords = [kw['phrase'] for kw in sorted_keywords[:limit]]
        
        logger.info(f"📈 Selected top {len(top_keywords)} keywords by relevancy score")
        
        return top_keywords
    
    def get_top_keywords_by_volume_strict(self, keywords: List[str], limit: int = 10) -> List[str]:
        """
        Get top keywords by VOLUME ONLY (strict sorting, ignore relevancy/intent).
        This ensures highest-volume keywords are ALWAYS prioritized for title allocation.
        
        Args:
            keywords: List of keyword phrases
            limit: Number of top keywords to return
            
        Returns:
            Top keywords sorted by search volume only
        """
        keyword_with_volumes = []
        for kw in keywords:
            kw_data = self.get_keyword_data(kw)
            if kw_data:
                volume = kw_data.get('search_volume', 0) or 0
                keyword_with_volumes.append({
                    'phrase': kw,
                    'search_volume': volume
                })
        
        # Sort by VOLUME ONLY (no relevancy, no intent)
        sorted_keywords = sorted(
            keyword_with_volumes, 
            key=lambda x: x['search_volume'], 
            reverse=True
        )
        
        top_keywords = [kw['phrase'] for kw in sorted_keywords[:limit]]
        
        # Log top 3 for debugging
        if top_keywords:
            top_3_info = []
            for i, kw in enumerate(top_keywords[:3], 1):
                kw_data = self.get_keyword_data(kw)
                volume = kw_data.get('search_volume', 0) if kw_data else 0
                top_3_info.append(f"#{i} '{kw}' ({volume:,} vol)")
            logger.info(f"🔥 TOP KEYWORDS BY VOLUME: {', '.join(top_3_info)}")
        
        return top_keywords
    
    def allocate_keywords_for_content_type(self, keywords: List[str], content_type: str) -> List[str]:
        """
        Allocate keywords for specific content type, preventing duplication.
        
        Args:
            keywords: List of valid keywords
            content_type: 'title', 'bullets', or 'backend'
            
        Returns:
            List of allocated keywords for the content type
        """
        if content_type not in self.keyword_allocation:
            logger.error(f"❌ Unknown content type: {content_type}")
            return []
        
        # Filter out already used keywords
        available_keywords = [kw for kw in keywords if kw.lower() not in self.used_keywords]
        
        # Get allocation limit
        limit = self.keyword_allocation[content_type]
        
        # Allocate keywords
        allocated_keywords = available_keywords[:limit]
        
        # Track usage
        self.used_keywords.update([kw.lower() for kw in allocated_keywords])
        
        logger.info(f"🎯 Allocated {len(allocated_keywords)} keywords for {content_type} (limit: {limit})")
        
        return allocated_keywords
    
    def get_keyword_data(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Get full keyword data for a specific keyword."""
        keyword_lower = keyword.lower()
        return self.keyword_data.get(keyword_lower)
    
    def get_available_keywords(self) -> List[str]:
        """Get list of keywords not yet used."""
        available = []
        for phrase in self.keyword_data.keys():
            if phrase not in self.used_keywords:
                original_phrase = self.keyword_data[phrase].get("phrase", phrase)
                available.append(original_phrase)
        return available
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get summary of keyword usage."""
        return {
            'total_research_keywords': len(self.research_keywords),
            'unique_keyword_phrases': len(self.keyword_phrases),
            'used_keywords_count': len(self.used_keywords),
            'available_keywords_count': len(self.get_available_keywords()),
            'usage_percentage': round((len(self.used_keywords) / len(self.keyword_phrases)) * 100, 2) if self.keyword_phrases else 0,
            'used_keywords': list(self.used_keywords),
            'allocation_limits': self.keyword_allocation
        }
    
    def reset_usage_tracking(self):
        """Reset usage tracking (useful for testing)."""
        self.used_keywords.clear()
        logger.info("🔄 Reset keyword usage tracking")
    
    def validate_and_allocate_keywords(self, 
                                     keywords_to_use: List[str], 
                                     content_type: str,
                                     sort_by_relevancy: bool = True) -> List[str]:
        """
        Complete validation and allocation process.
        
        Args:
            keywords_to_use: Keywords to validate and allocate
            content_type: 'title', 'bullets', or 'backend'
            sort_by_relevancy: Whether to sort by relevancy score
            
        Returns:
            List of validated and allocated keywords
        """
        logger.info(f"🔍 Starting validation and allocation for {content_type}")
        
        # Step 1: Validate against research data
        valid_keywords, invalid_keywords = self.validate_keywords_against_research(keywords_to_use)
        
        if not valid_keywords:
            logger.warning(f"⚠️  No valid keywords found for {content_type}")
            return []
        
        # Step 2: Sort by relevancy if requested
        if sort_by_relevancy:
            valid_keywords = self.get_top_keywords_by_relevancy(valid_keywords)
        
        # Step 3: Allocate for content type
        allocated_keywords = self.allocate_keywords_for_content_type(valid_keywords, content_type)
        
        logger.info(f"✅ Successfully allocated {len(allocated_keywords)} keywords for {content_type}")
        
        return allocated_keywords
    
    def get_allocated_keywords_for_ai(self, content_type: str, bullet_count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get pre-allocated keywords for AI agents to prevent duplication.
        
        Args:
            content_type: 'title', 'bullets', or 'backend'
            bullet_count: Number of bullet points (for dynamic allocation)
            
        Returns:
            List of keyword dicts that AI agents should use
        """
        # Get available keywords (not yet used)
        available_keywords = self.get_available_keywords()
        
        # For TITLE: sort by VOLUME ONLY to ensure highest-volume keywords go to title
        # For other content types: use relevancy + volume + intent
        if content_type == 'title':
            top_keywords = self.get_top_keywords_by_volume_strict(available_keywords, 20)
            logger.info(f"🔥 Title allocation using STRICT VOLUME sorting (ensures top keywords in title)")
        else:
            # For bullets/backend: use relevancy + volume + intent
            top_keywords = self.get_top_keywords_by_relevancy(available_keywords, 20)
        
        # Dynamic allocation for bullets based on bullet count
        if content_type == 'bullets' and bullet_count:
            # Allocate 2-3 keywords per bullet point
            dynamic_limit = max(4, bullet_count * 2)  # Minimum 4, or 2 per bullet
            logger.info(f"🎯 Dynamic bullet allocation: {bullet_count} bullets → {dynamic_limit} keywords")
            
            # Temporarily adjust allocation limit
            original_limit = self.keyword_allocation['bullets']
            self.keyword_allocation['bullets'] = dynamic_limit
            
            # Allocate for the specific content type
            allocated_keywords = self.allocate_keywords_for_content_type(top_keywords, content_type)
            
            # Restore original limit
            self.keyword_allocation['bullets'] = original_limit
        else:
            # Allocate for the specific content type
            allocated_keywords = self.allocate_keywords_for_content_type(top_keywords, content_type)
        
        # Convert to keyword dicts with full data
        allocated_keyword_dicts = []
        for keyword in allocated_keywords:
            keyword_data = self.get_keyword_data(keyword)
            if keyword_data:
                allocated_keyword_dicts.append(keyword_data)
        
        logger.info(f"🎯 Allocated {len(allocated_keyword_dicts)} keywords for {content_type} AI agent")
        
        return allocated_keyword_dicts
    
    def get_allocation_summary(self) -> Dict[str, List[str]]:
        """
        Get summary of keyword allocation across all content types.
        
        Returns:
            Dict with allocated keywords by content type
        """
        return {
            'title_keywords': [kw for kw in self.used_keywords if kw in self._get_allocated_for_type('title')],
            'bullet_keywords': [kw for kw in self.used_keywords if kw in self._get_allocated_for_type('bullets')],
            'backend_keywords': [kw for kw in self.used_keywords if kw in self._get_allocated_for_type('backend')],
            'total_used': list(self.used_keywords),
            'available': self.get_available_keywords()
        }
    
    def _get_allocated_for_type(self, content_type: str) -> List[str]:
        """Helper method to get keywords allocated for specific content type."""
        # This is a simplified implementation - in practice, you'd track this more precisely
        available = self.get_available_keywords()
        allocated = self.allocate_keywords_for_content_type(available, content_type)
        return allocated


def create_keyword_validator_from_research_data(keyword_items: List[Dict[str, Any]]) -> SEOKeywordValidator:
    """
    Factory function to create validator from research keyword data.
    
    Args:
        keyword_items: List of keyword dicts from research agent
        
    Returns:
        SEOKeywordValidator instance
    """
    return SEOKeywordValidator(keyword_items)


def validate_seo_output_keywords(seo_output: Dict[str, Any], validator: SEOKeywordValidator) -> Dict[str, Any]:
    """
    Validate all keywords in SEO output against research data.
    
    Args:
        seo_output: SEO optimization output
        validator: SEOKeywordValidator instance
        
    Returns:
        Validation report
    """
    validation_report = {
        'title_validation': {'valid': True, 'invalid_keywords': []},
        'bullets_validation': {'valid': True, 'invalid_keywords': []},
        'backend_validation': {'valid': True, 'invalid_keywords': []},
        'overall_valid': True
    }
    
    # Validate title keywords
    if 'optimized_title' in seo_output:
        title_keywords = seo_output['optimized_title'].get('keywords_included', [])
        valid_title, invalid_title = validator.validate_keywords_against_research(title_keywords)
        validation_report['title_validation'] = {
            'valid': len(invalid_title) == 0,
            'invalid_keywords': invalid_title,
            'valid_keywords': valid_title
        }
    
    # Validate bullet keywords
    if 'optimized_bullets' in seo_output:
        all_bullet_keywords = []
        for bullet in seo_output['optimized_bullets']:
            all_bullet_keywords.extend(bullet.get('keywords_included', []))
        
        valid_bullets, invalid_bullets = validator.validate_keywords_against_research(all_bullet_keywords)
        validation_report['bullets_validation'] = {
            'valid': len(invalid_bullets) == 0,
            'invalid_keywords': invalid_bullets,
            'valid_keywords': valid_bullets
        }
    
    # Validate backend keywords
    if 'optimized_backend_keywords' in seo_output:
        backend_keywords = seo_output['optimized_backend_keywords']
        valid_backend, invalid_backend = validator.validate_keywords_against_research(backend_keywords)
        validation_report['backend_validation'] = {
            'valid': len(invalid_backend) == 0,
            'invalid_keywords': invalid_backend,
            'valid_keywords': valid_backend
        }
    
    # Overall validation
    validation_report['overall_valid'] = all([
        validation_report['title_validation']['valid'],
        validation_report['bullets_validation']['valid'],
        validation_report['backend_validation']['valid']
    ])
    
    if not validation_report['overall_valid']:
        logger.error("❌ SEO output contains invalid keywords (hallucination detected)")
    else:
        logger.info("✅ SEO output validation passed - no keyword hallucination")
    
    return validation_report
