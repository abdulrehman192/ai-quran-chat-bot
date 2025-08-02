from typing import List, Dict, Tuple
from database.queries import QuranQueries
from config.english_handling import EnglishHandlingConfig
import logging

class EnhancedSearchUtility:
    """Utility for enhanced search with English support"""
    
    def __init__(self):
        self.db_queries = QuranQueries()
        self.config = EnglishHandlingConfig()
        self.logger = logging.getLogger(__name__)
    
    async def smart_search(self, query: str, language: str) -> Tuple[List[Dict], bool, str]:
        """
        Perform smart search that handles English queries intelligently
        Returns: (results, has_results, search_strategy_used)
        """
        results = []
        has_results = False
        strategy = "direct_search"
        
        try:
            # Strategy 1: Direct search
            results = self.db_queries.search_verses(query, language)
            if results:
                has_results = True
                return results, has_results, strategy
            
            # Strategy 2: For English queries, try concept mapping
            if language == "en":
                strategy = "concept_mapping"
                mapped_results = await self._search_by_concept_mapping(query)
                if mapped_results:
                    results.extend(mapped_results)
                    has_results = True
                    return results, has_results, strategy
            
            # Strategy 3: Topic-based search
            strategy = "topic_search"
            topic_results = self.db_queries.search_verses_by_topic(query, language)
            if topic_results:
                results.extend(topic_results)
                has_results = True
                return results, has_results, strategy
            
            # Strategy 4: Keyword extraction and search
            strategy = "keyword_extraction"
            keyword_results = await self._search_by_keywords(query, language)
            if keyword_results:
                results.extend(keyword_results)
                has_results = True
                return results, has_results, strategy
            
        except Exception as e:
            self.logger.error(f"Error in smart_search: {e}")
        
        return results, has_results, strategy
    
    async def _search_by_concept_mapping(self, english_query: str) -> List[Dict]:
        """Search using English to Arabic concept mapping"""
        results = []
        
        # Extract concepts from the query
        words = english_query.lower().split()
        
        for word in words:
            # Get Arabic terms for this English word
            arabic_terms = self.config.get_arabic_terms(word)
            
            for arabic_term in arabic_terms:
                # Search with Arabic term
                verses = self.db_queries.search_verses(arabic_term, "ar")
                results.extend(verses)
        
        # Remove duplicates
        unique_results = {r['ayatId']: r for r in results}.values()
        return list(unique_results)[:10]  # Limit results
    
    async def _search_by_keywords(self, query: str, language: str) -> List[Dict]:
        """Extract meaningful keywords and search"""
        # Simple keyword extraction
        import re
        
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'under', 'over',
            'what', 'where', 'when', 'why', 'how', 'which', 'who', 'whom',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
            'this', 'that', 'these', 'those', 'a', 'an', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'need', 'want', 'tell', 'show', 'give', 'find', 'help'
        }
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        results = []
        for keyword in keywords[:5]:  # Limit to 5 keywords
            verses = self.db_queries.search_verses(keyword, language)
            results.extend(verses)
        
        # Remove duplicates
        unique_results = {r['ayatId']: r for r in results}.values()
        return list(unique_results)[:8]
    
    def get_search_explanation(self, strategy: str, language: str) -> str:
        """Get explanation of search strategy used"""
        explanations = {
            'en': {
                'direct_search': "Found results using direct search in the database.",
                'concept_mapping': "Found results by mapping English concepts to Arabic terms.",
                'topic_search': "Found results using topic-based search.",
                'keyword_extraction': "Found results by extracting and searching key terms.",
                'no_results': "No specific results found in database. Providing general Islamic guidance."
            },
            'ur': {
                'direct_search': "ڈیٹابیس میں براہ راست تلاش سے نتائج ملے۔",
                'concept_mapping': "انگریزی تصورات کو عربی اصطلاحات سے ملا کر نتائج ملے۔",
                'topic_search': "موضوعی تلاش کے ذریعے نتائج ملے۔",
                'keyword_extraction': "اہم الفاظ نکال کر تلاش سے نتائج ملے۔",
                'no_results': "ڈیٹابیس میں مخصوص نتائج نہیں ملے۔ عمومی اسلامی رہنمائی فراہم کی جا رہی ہے۔"
            }
        }
        
        lang_explanations = explanations.get(language, explanations['en'])
        return lang_explanations.get(strategy, lang_explanations['no_results'])