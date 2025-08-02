from agents.base_worker import BaseWorker
from typing import Dict, Any

class GuidanceWorker(BaseWorker):
    """Worker for providing spiritual guidance with enhanced English support"""
    
    def can_handle(self, query: str, intent: str) -> bool:
        guidance_keywords = [
            "advice", "guidance", "help", "problem", "difficulty", "life", "issue",
            "struggling", "confused", "worried", "anxious", "sad", "depressed",
            "need help", "what should i do", "how to deal",
            "مشکل", "مدد", "رہنمائی", "مسئلہ", "پریشان",  # Urdu
            "مشكلة", "مساعدة", "إرشاد", "نصيحة", "قلق"   # Arabic
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in guidance_keywords) or intent == "guidance_request"
    
    async def process_request(self, query: str, language: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Identify the type of guidance needed
            guidance_type = self._identify_guidance_type(query)
            
            # Search for relevant content
            guidance_content = await self._get_guidance_content(query, guidance_type, language)
            
            # Format context for LLM
            if guidance_content['has_database_content']:
                context_text = self._format_guidance_context(guidance_content, language)
            else:
                context_text = self._create_general_guidance_context(guidance_type, language)
            
            # Generate guidance response
            response = await self.llm_client.generate_response(
                query, context_text, language, "guidance_request"
            )
            
            return self.format_response(
                content=response,
                sources=guidance_content['sources'],
                language=language,
                has_database_results=guidance_content['has_database_content']
            )
            
        except Exception as e:
            self.logger.error(f"Error in GuidanceWorker: {e}")
            return self.format_response(
                "Error processing guidance request", 
                language=language, 
                has_database_results=False
            )
    
    def _identify_guidance_type(self, query: str) -> str:
        """Identify the type of guidance needed"""
        query_lower = query.lower()
        
        guidance_types = {
            'anxiety': ['anxious', 'anxiety', 'worried', 'worry', 'stress', 'fear', 'پریشان', 'خوف', 'قلق'],
            'sadness': ['sad', 'sadness', 'depressed', 'depression', 'grief', 'غم', 'اداس', 'حزن'],
            'relationship': ['relationship', 'marriage', 'family', 'friend', 'spouse', 'رشتہ', 'شادی', 'خاندان'],
            'work': ['work', 'job', 'career', 'business', 'money', 'کام', 'نوکری', 'کاروبار'],
            'spiritual': ['spiritual', 'faith', 'prayer', 'islam', 'allah', 'روحانی', 'ایمان', 'نماز'],
            'decision': ['decision', 'choose', 'choice', 'confused', 'فیصلہ', 'انتخاب', 'الاختيار'],
            'health': ['health', 'sick', 'illness', 'disease', 'صحت', 'بیمار', 'مرض'],
            'forgiveness': ['forgive', 'forgiveness', 'guilt', 'sin', 'معاف', 'گناہ', 'توبہ']
        }
        
        for gtype, keywords in guidance_types.items():
            if any(keyword in query_lower for keyword in keywords):
                return gtype
        
        return 'general'
    
    async def _get_guidance_content(self, query: str, guidance_type: str, language: str) -> Dict[str, Any]:
        """Get relevant guidance content from database and other sources"""
        sources = []
        has_database_content = False
        
        try:
            # Map guidance types to search terms
            search_terms_map = {
                'anxiety': ['peace', 'trust', 'calm', 'سكينة', 'سلام', 'اطمئنان'],
                'sadness': ['comfort', 'hope', 'mercy', 'رحمة', 'صبر', 'أمل'],
                'spiritual': ['faith', 'prayer', 'remembrance', 'ذكر', 'ايمان', 'صلاة'],
                'forgiveness': ['forgiveness', 'repentance', 'mercy', 'غفران', 'توبة', 'رحمة'],
                'general': ['guidance', 'wisdom', 'help', 'هداية', 'حكمة', 'مساعدة']
            }
            
            search_terms = search_terms_map.get(guidance_type, search_terms_map['general'])
            
            # Search for relevant verses
            all_verses = []
            for term in search_terms:
                verses = self.db_queries.search_verses(term, language)
                all_verses.extend(verses)
            
            # Remove duplicates and limit results
            unique_verses = {v['ayatId']: v for v in all_verses}.values()
            relevant_verses = list(unique_verses)[:3]
            
            if relevant_verses:
                has_database_content = True
                sources.extend([
                    {
                        "type": "verse",
                        "surah": verse['name_en'],
                        "verse_number": verse['ayatNumber'],
                        "surah_id": verse['surahId']
                    }
                    for verse in relevant_verses
                ])
            
            # Also get some Allah's names for comfort
            relevant_names = self._get_relevant_allah_names(guidance_type)
            names_from_db = self.db_queries.get_allah_names()
            
            matching_names = [
                name for name in names_from_db 
                if any(rel_name.lower() in name['english'].lower() 
                      for rel_name in relevant_names)
            ][:2]
            
            if matching_names:
                has_database_content = True
                sources.extend([
                    {
                        "type": "allah_name",
                        "arabic": name['arabic'],
                        "english": name['english']
                    }
                    for name in matching_names
                ])
            
        except Exception as e:
            self.logger.error(f"Error getting guidance content: {e}")
        
        return {
            'has_database_content': has_database_content,
            'sources': sources,
            'guidance_type': guidance_type,
            'verses': relevant_verses if 'relevant_verses' in locals() else [],
            'names': matching_names if 'matching_names' in locals() else []
        }
    
    def _get_relevant_allah_names(self, guidance_type: str) -> list:
        """Get relevant Allah's names based on guidance type"""
        names_map = {
            'anxiety': ['Peaceful', 'Protector', 'Guardian', 'Helper'],
            'sadness': ['Merciful', 'Compassionate', 'Comforter', 'Healer'],
            'spiritual': ['Guide', 'Light', 'Truth', 'Wise'],
            'forgiveness': ['Forgiving', 'Merciful', 'Acceptor', 'Pardoner'],
            'general': ['Merciful', 'Wise', 'Helper', 'Guide']
        }
        
        return names_map.get(guidance_type, names_map['general'])
    
    def _create_general_guidance_context(self, guidance_type: str, language: str) -> str:
        """Create general guidance context when database results are limited"""
        context_map = {
            'en': {
                'anxiety': "Islamic guidance for anxiety: Trust in Allah's wisdom, remember that Allah does not burden a soul beyond its capacity, practice dhikr (remembrance of Allah), and seek comfort in prayer.",
                'sadness': "Islamic guidance for sadness: Remember that Allah is with those who are patient, seek comfort in prayer and Quran, and know that after hardship comes ease.",
                'spiritual': "Islamic spiritual guidance: Strengthen your relationship with Allah through regular prayer, Quran recitation, dhikr, and following the example of Prophet Muhammad (peace be upon him).",
                'forgiveness': "Islamic guidance on forgiveness: Allah is oft-forgiving and merciful. Sincere repentance (tawbah) includes acknowledging the mistake, feeling remorse, seeking Allah's forgiveness, and resolving not to repeat it.",
                'general': "Islamic guidance: Seek Allah's help through prayer and patience. Trust in Allah's wisdom and timing. Follow the teachings of the Quran and the example of Prophet Muhammad (peace be upon him)."
            },
            'ur': {
                'anxiety': "بے چینی کے لیے اسلامی رہنمائی: اللہ کی حکمت پر بھروسہ رکھیں، یاد رکھیں کہ اللہ کسی جان کو اس کی طاقت سے زیادہ تکلیف نہیں دیتا، ذکر اللہ کریں اور نماز میں سکون تلاش کریں۔",
                'sadness': "اداسی کے لیے اسلامی رہنمائی: یاد رکھیں کہ اللہ صبر کرنے والوں کے ساتھ ہے، نماز اور قرآن میں سکون تلاش کریں، اور یقین رکھیں کہ مشکل کے بعد آسانی آتی ہے۔",
                'general': "اسلامی رہنمائی: نماز اور صبر کے ذریعے اللہ سے مدد مانگیں۔ اللہ کی حکمت اور وقت پر بھروسہ رکھیں۔"
            }
        }
        
        lang_context = context_map.get(language, context_map['en'])
        return lang_context.get(guidance_type, lang_context['general'])
    
    def _format_guidance_context(self, guidance_content: Dict, language: str) -> str:
        """Format guidance content for LLM context"""
    def _format_guidance_context(self, guidance_content: Dict, language: str) -> str:
        """Format guidance content for LLM context"""
        context = f"Islamic guidance for {guidance_content['guidance_type']} concerns:\n\n"
        
        # Add verses if found
        if 'verses' in guidance_content and guidance_content['verses']:
            context += "Relevant Quranic verses:\n"
            for verse in guidance_content['verses']:
                context += f"- Surah {verse['name_en']}, Verse {verse['ayatNumber']}: {verse['arabicText']}\n"
                if language == 'ur' and verse.get('urduTranslation'):
                    context += f"  Translation: {verse['urduTranslation']}\n"
                context += "\n"
        
        # Add Allah's names if found
        if 'names' in guidance_content and guidance_content['names']:
            context += "Relevant names of Allah for comfort:\n"
            for name in guidance_content['names']:
                context += f"- {name['arabic']} ({name['english']}): {name['englishMeaning']}\n"
        
        return context
