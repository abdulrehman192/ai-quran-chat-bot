from agents.base_worker import BaseWorker
from typing import Dict, Any
import random

class LearningWorker(BaseWorker):
    """Worker for educational content about Quran and Islamic teachings"""
    
    def can_handle(self, query: str, intent: str) -> bool:
        learning_keywords = [
            "learn", "teach", "explain", "what is", "how to", "meaning", "definition",
            "tell me about", "education", "study", "understand", "knowledge",
            "سیکھنا", "پڑھانا", "سمجھانا", "کیا ہے", "معنی",  # Urdu
            "تعلم", "علم", "شرح", "ما هو", "معنى"  # Arabic
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in learning_keywords) or intent == "learning_request"
    
    async def process_request(self, query: str, language: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Determine what the user wants to learn about
            learning_topic = self._identify_learning_topic(query)
            
            # Get relevant educational content from database
            educational_content = await self._get_educational_content(learning_topic, language)
            
            # If no specific database content, use LLM's knowledge
            if not educational_content['database_sources']:
                context_text = self._create_general_islamic_context(learning_topic, language)
            else:
                context_text = self._format_educational_context(educational_content, language)
            
            # Generate educational response
            response = await self.llm_client.generate_response(query, context_text, language)
            
            return self.format_response(
                content=response,
                sources=educational_content['sources'],
                language=language
            )
            
        except Exception as e:
            self.logger.error(f"Error in LearningWorker: {e}")
            return self.format_response("Error processing learning request", language=language)
    
    def _identify_learning_topic(self, query: str) -> str:
        """Identify what the user wants to learn about"""
        query_lower = query.lower()
        
        # Map common learning topics
        topic_keywords = {
            'prayer': ['prayer', 'salah', 'namaz', 'نماز', 'صلاة'],
            'hajj': ['hajj', 'pilgrimage', 'حج'],
            'fasting': ['fast', 'fasting', 'ramadan', 'روزہ', 'صوم'],
            'zakat': ['zakat', 'charity', 'زکات'],
            'quran': ['quran', 'quranic', 'قرآن'],
            'prophet': ['prophet', 'muhammad', 'نبی', 'رسول', 'النبي'],
            'islamic_law': ['law', 'sharia', 'halal', 'haram', 'حلال', 'حرام', 'شریعہ'],
            'faith': ['faith', 'belief', 'iman', 'ایمان', 'إيمان'],
            'history': ['history', 'islamic history', 'تاریخ', 'تاريخ']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return topic
        
        return 'general'
    
    async def _get_educational_content(self, topic: str, language: str) -> Dict[str, Any]:
        """Get educational content from database based on topic"""
        sources = []
        database_sources = False
        
        try:
            if topic == 'prayer':
                # Get prayer-related duas
                duas = self.db_queries.search_duas('prayer')
                if duas:
                    database_sources = True
                    sources.extend([{
                        "type": "dua",
                        "surah": dua['surah'],
                        "verse": dua['aya_number']
                    } for dua in duas[:3]])
            
            elif topic in ['quran', 'general']:
                # Get some verses for general learning
                sample_verses = self.db_queries.get_sample_verses(3)  # Will implement this
                if sample_verses:
                    database_sources = True
                    sources.extend([{
                        "type": "verse",
                        "surah": verse['name_en'],
                        "verse_number": verse['ayatNumber'],
                        "surah_id": verse['surahId']
                    } for verse in sample_verses])
            
            elif topic == 'faith':
                # Get Allah's names for faith-related learning
                names = self.db_queries.get_allah_names()[:5]
                if names:
                    database_sources = True
                    sources.extend([{
                        "type": "allah_name",
                        "arabic": name['arabic'],
                        "english": name['english']
                    } for name in names])
            
        except Exception as e:
            self.logger.error(f"Error getting educational content: {e}")
        
        return {
            'database_sources': database_sources,
            'sources': sources,
            'topic': topic
        }
    
    def _create_general_islamic_context(self, topic: str, language: str) -> str:
        """Create general Islamic context when no database content is available"""
        context_templates = {
            'en': {
                'prayer': "Islamic prayer (Salah) is one of the Five Pillars of Islam. It involves specific movements, recitations, and is performed five times daily facing the Qibla (direction of Kaaba).",
                'hajj': "Hajj is the annual pilgrimage to Mecca, one of the Five Pillars of Islam. It must be performed at least once by every able-bodied Muslim who can afford it.",
                'fasting': "Fasting (Sawm) during Ramadan is one of the Five Pillars of Islam. Muslims abstain from food, drink, and other physical desires from dawn to sunset.",
                'zakat': "Zakat is the obligatory charitable giving in Islam, one of the Five Pillars. It purifies wealth and helps support the needy in the community.",
                'general': "Islam is a comprehensive way of life based on the Quran and the teachings of Prophet Muhammad (peace be upon him)."
            },
            'ur': {
                'prayer': "نماز اسلام کے پانچ بنیادی ارکان میں سے ایک ہے۔ یہ دن میں پانچ بار قبلہ کی سمت ادا کی جاتی ہے۔",
                'hajj': "حج اسلام کا بنیادی رکن ہے جو ہر صاحب استطاعت مسلمان پر زندگی میں ایک بار فرض ہے۔",
                'fasting': "رمضان کے روزے اسلام کے پانچ بنیادی ارکان میں سے ایک ہیں۔",
                'general': "اسلام قرآن اور حضرت محمد صلی اللہ علیہ وسلم کی تعلیمات پر مبنی مکمل طریقہ زندگی ہے۔"
            }
        }
        
        templates = context_templates.get(language, context_templates['en'])
        return templates.get(topic, templates['general'])
    
    def _format_educational_context(self, educational_content: Dict, language: str) -> str:
        """Format educational content for LLM context"""
        context = f"Educational content about {educational_content['topic']}:\n\n"
        
        for source in educational_content['sources']:
            if source['type'] == 'verse':
                context += f"Reference: Surah {source['surah']}, Verse {source['verse_number']}\n"
            elif source['type'] == 'dua':
                context += f"Prayer from: Surah {source['surah']}, Verse {source['verse']}\n"
            elif source['type'] == 'allah_name':
                context += f"Allah's Name: {source['arabic']} ({source['english']})\n"
        
        return context