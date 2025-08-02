import asyncio
from typing import Dict, Any, List
from agents.workers.verse_worker import VerseWorker
from agents.workers.dua_worker import DuaWorker
from agents.workers.names_worker import NamesWorker
from agents.workers.guidance_worker import GuidanceWorker
from agents.workers.learning_worker import LearningWorker  # Add this import
from utils.language_detector import LanguageDetector
from utils.validators import InputValidator
from llm.gemini_client import GeminiClient
import logging

class QuranChatbotOrchestrator:
    """Main orchestrator that routes requests to appropriate workers"""
    
    def __init__(self):
        self.workers = [
            VerseWorker(),
            DuaWorker(),
            NamesWorker(),
            GuidanceWorker(),
            LearningWorker()  # Add learning worker
        ]
        self.fallback_llm = GeminiClient()
        self.logger = logging.getLogger(__name__)
    
    async def process_query(self, user_query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main entry point for processing user queries with enhanced English support"""
        try:
            # Validate input
            is_valid, validation_message = InputValidator.validate_query(user_query)
            if not is_valid:
                return self._create_error_response(validation_message)
            
            # Sanitize input
            clean_query = InputValidator.sanitize_input(user_query)
            
            # Detect language
            language = LanguageDetector.detect_language(clean_query)
            
            # Determine intent and route to appropriate worker
            intent = await self._determine_intent(clean_query, language)
            
            # Find appropriate worker
            selected_worker = self._select_worker(clean_query, intent)
            
            if selected_worker:
                self.logger.info(f"Routing to {selected_worker.__class__.__name__}")
                response = await selected_worker.process_request(
                    clean_query, 
                    language, 
                    user_context or {}
                )
            else:
                # Enhanced fallback response
                self.logger.info("Using enhanced fallback response")
                response = await self._generate_enhanced_fallback_response(clean_query, language)
            
            # Add metadata
            response.update({
                "query": clean_query,
                "intent": intent,
                "timestamp": asyncio.get_event_loop().time(),
                "language_detected": language
            })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in orchestrator: {e}")
            return self._create_error_response(
                self._get_error_message(user_context.get('language', 'en') if user_context else 'en')
            )
    
    async def _determine_intent(self, query: str, language: str) -> str:
        """Enhanced intent determination"""
        query_lower = query.lower()
        
        # Enhanced intent patterns
        intent_patterns = {
            'verse_search': [
                'verse', 'ayah', 'surah', 'chapter', 'quran', 'quranic',
                'آیت', 'سورہ', 'قرآن',  # Urdu
                'آية', 'سورة', 'قرآن'   # Arabic
            ],
            'dua_request': [
                'dua', 'prayer', 'pray', 'supplication', 'supplicate',
                'دعا', 'نماز', 'التماس',  # Urdu
                'دعاء', 'صلاة', 'ابتهال'   # Arabic
            ],
            'names_request': [
                'allah', 'names', 'asma', 'husna', 'attributes',
                'اللہ', 'نام', 'اسماء', 'حسنیٰ',  # Urdu
                'الله', 'أسماء', 'الحسنى'    # Arabic
            ],
            'guidance_request': [
                'advice', 'guidance', 'help', 'problem', 'difficulty',
                'struggling', 'confused', 'worried', 'what should i do',
                'مشکل', 'مدد', 'رہنمائی', 'مسئلہ',  # Urdu
                'مشكلة', 'مساعدة', 'إرشاد', 'نصيحة'   # Arabic
            ],
            'learning_request': [
                'learn', 'teach', 'explain', 'what is', 'how to', 'meaning',
                'tell me about', 'education', 'study', 'understand',
                'سیکھنا', 'پڑھانا', 'سمجھانا', 'کیا ہے',  # Urdu
                'تعلم', 'علم', 'شرح', 'ما هو'    # Arabic
            ]
        }
        
        # Check each intent pattern
        for intent, patterns in intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent
        
        return 'general_query'
    
    def _select_worker(self, query: str, intent: str):
        """Enhanced worker selection"""
        for worker in self.workers:
            if worker.can_handle(query, intent):
                return worker
        return None
    
    async def _generate_enhanced_fallback_response(self, query: str, language: str) -> Dict[str, Any]:
        """Enhanced fallback response with better context"""
        try:
            context = self._create_fallback_context(language)
            
            response = await self.fallback_llm.generate_response(
                query, context, language, "fallback"
            )
            
            return {
                "content": response,
                "sources": [],
                "language": language,
                "worker": "EnhancedFallbackResponse",
                "has_database_results": False,
                "disclaimer": self._get_fallback_disclaimer(language)
            }
        except Exception as e:
            self.logger.error(f"Enhanced fallback response error: {e}")
            return self._create_error_response(self._get_error_message(language))
    
    def _create_fallback_context(self, language: str) -> str:
        """Create enhanced context for fallback responses"""
        contexts = {
            'en': """You are responding to a general Islamic question. Since no specific database content was found, provide helpful guidance based on authentic Islamic knowledge. Remember to:
                     1. Be respectful and compassionate
                     2. Provide practical Islamic guidance when possible
                     3. Mention that for specific Quranic verses or hadith references, consulting Islamic scholars is recommended
                     4. Focus on universal Islamic principles
                     5. Encourage seeking knowledge from qualified sources""",
            
            'ur': """آپ ایک عمومی اسلامی سوال کا جواب دے رہے ہیں۔ چونکہ ڈیٹابیس میں کوئی مخصوص مواد نہیں ملا، لہذا مستند اسلامی علم کی بنیاد پر مفید رہنمائی فراہم کریں۔""",
            
            'ar': """أنت تجيب على سؤال إسلامي عام. نظرًا لعدم العثور على محتوى محدد في قاعدة البيانات، قدم إرشادات مفيدة بناءً على المعرفة الإسلامية الموثقة."""
        }
        
        return contexts.get(language, contexts['en'])
    
    def _get_fallback_disclaimer(self, language: str) -> str:
        """Get disclaimer for fallback responses"""
        disclaimers = {
            'en': "This response is based on general Islamic knowledge. For specific Quranic references or detailed religious guidance, please consult qualified Islamic scholars.",
            'ur': "یہ جواب عمومی اسلامی علم پر مبنی ہے۔ مخصوص قرآنی حوالوں یا تفصیلی مذہبی رہنمائی کے لیے براہ کرم اہل علماء سے رجوع کریں۔",
            'ar': "هذه الإجابة مبنية على المعرفة الإسلامية العامة. للحصول على مراجع قرآنية محددة أو إرشادات دينية مفصلة، يرجى استشارة العلماء المؤهلين."
        }
        
        return disclaimers.get(language, disclaimers['en'])
    
    def _get_error_message(self, language: str) -> str:
        """Get appropriate error message"""
        messages = {
            'en': "I apologize, but I'm having trouble processing your request. Please try again.",
            'ur': "معذرت، آپ کی درخواست پر عمل کرنے میں مسئلہ ہو رہا ہے۔ براہ کرم دوبارہ کوشش کریں۔",
            'ar': "أعتذر، لكنني أواجه مشكلة في معالجة طلبك. يرجى المحاولة مرة أخرى."
        }
        
        return messages.get(language, messages['en'])
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "content": message,
            "sources": [],
            "language": "en",
            "worker": "ErrorHandler",
            "error": True,
            "has_database_results": False
        }