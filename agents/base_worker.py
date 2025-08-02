from abc import ABC, abstractmethod
from typing import Dict, Any
from llm.gemini_client import GeminiClient
from database.queries import QuranQueries
import logging

class BaseWorker(ABC):
    """Base class for all worker agents with enhanced English support"""
    
    def __init__(self):
        self.llm_client = GeminiClient()
        self.db_queries = QuranQueries()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def process_request(self, query: str, language: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the user request and return response"""
        pass
    
    @abstractmethod
    def can_handle(self, query: str, intent: str) -> bool:
        """Check if this worker can handle the given query"""
        pass
    
    def format_response(self, content: str, sources: list = None, language: str = "en", 
                       has_database_results: bool = True) -> Dict[str, Any]:
        """Format the response in a standard structure"""
        return {
            "content": content,
            "sources": sources or [],
            "language": language,
            "worker": self.__class__.__name__,
            "has_database_results": has_database_results,
            "disclaimer": self._get_disclaimer(language, has_database_results)
        }
    
    def _get_disclaimer(self, language: str, has_database_results: bool) -> str:
        """Get appropriate disclaimer based on whether database results were found"""
        if has_database_results:
            return ""
        
        disclaimers = {
            "en": "Note: No specific verses were found in the database for your query. This guidance is based on general Islamic principles. For specific Quranic references, please consult Islamic scholars or authentic Quranic resources.",
            
            "ur": "نوٹ: آپ کے سوال کے لیے ڈیٹابیس میں کوئی مخصوص آیات نہیں ملیں۔ یہ رہنمائی عمومی اسلامی اصولوں پر مبنی ہے۔ مخصوص قرآنی حوالوں کے لیے براہ کرم علماء کرام یا مستند قرآنی وسائل سے رجوع کریں۔",
            
            "ar": "ملاحظة: لم يتم العثور على آيات محددة في قاعدة البيانات لاستعلامك. هذا التوجيه يعتمد على المبادئ الإسلامية العامة. للحصول على مراجع قرآنية محددة، يرجى استشارة العلماء أو المصادر القرآنية الموثقة."
        }
        
        return disclaimers.get(language, disclaimers["en"])
    
    async def search_with_fallback(self, query: str, language: str) -> tuple[list, bool]:
        """Search database with fallback strategies for English queries"""
        results = []
        has_results = False
        
        try:
            # Try direct search first
            results = self.db_queries.search_verses(query, language)
            
            if results:
                has_results = True
            elif language == "en":
                # For English queries, try searching with common Islamic terms
                english_to_arabic_terms = {
                    'patience': 'صبر',
                    'forgiveness': 'غفر',
                    'mercy': 'رحم',
                    'guidance': 'هدى',
                    'peace': 'سلام',
                    'knowledge': 'علم',
                    'prayer': 'صلاة',
                    'charity': 'زكاة',
                    'faith': 'ايمان',
                    'hope': 'رجاء',
                    'love': 'حب',
                    'trust': 'توكل',
                    'worship': 'عبادة',
                    'gratitude': 'شكر',
                    'repentance': 'توبة'
                }
                
                query_words = query.lower().split()
                for word in query_words:
                    if word in english_to_arabic_terms:
                        arabic_results = self.db_queries.search_verses(
                            english_to_arabic_terms[word], "ar"
                        )
                        results.extend(arabic_results)
                        if arabic_results:
                            has_results = True
                
                # Also try topic-based search
                if not has_results:
                    topic_results = self.db_queries.search_verses_by_topic(query, language)
                    if topic_results:
                        results = topic_results
                        has_results = True
        
        except Exception as e:
            self.logger.error(f"Error in search_with_fallback: {e}")
        
        return results, has_results