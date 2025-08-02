from agents.base_worker import BaseWorker
from typing import Dict, Any

class DuaWorker(BaseWorker):
    """Worker for handling dua requests with enhanced language support"""
    
    def can_handle(self, query: str, intent: str) -> bool:
        dua_keywords = [
            "dua", "prayer", "pray", "supplication", "supplicate",
            "دعا", "نماز", "التماس", "منت",  # Urdu
            "دعاء", "صلاة", "ابتهال", "تضرع"   # Arabic
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in dua_keywords) or intent == "dua_request"
    
    async def process_request(self, query: str, language: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Identify what type of dua is needed
            dua_category = self._identify_dua_category(query)
            
            # Search for relevant duas
            dua_content = await self._get_dua_content(dua_category, language)
            
            # Format context for LLM
            if dua_content['has_database_content']:
                context_text = self._format_duas_context(dua_content, language)
            else:
                context_text = self._create_general_dua_context(dua_category, language)
            
            # Generate response
            response = await self.llm_client.generate_response(
                query, context_text, language, "dua_request"
            )
            
            return self.format_response(
                content=response,
                sources=dua_content['sources'],
                language=language,
                has_database_results=dua_content['has_database_content']
            )
            
        except Exception as e:
            self.logger.error(f"Error in DuaWorker: {e}")
            return self.format_response(
                "Error processing dua request", 
                language=language, 
                has_database_results=False
            )
    
    def _identify_dua_category(self, query: str) -> str:
        """Identify what type of dua is being requested"""
        query_lower = query.lower()
        
        categories = {
            'success': ['success', 'achievement', 'victory', 'کامیابی', 'نجاح'],
            'protection': ['protection', 'safety', 'security', 'حفاظت', 'امان', 'حماية'],
            'health': ['health', 'healing', 'cure', 'صحت', 'شفا', 'صحة'],
            'forgiveness': ['forgiveness', 'repentance', 'sins', 'معافی', 'توبہ', 'مغفرة'],
            'guidance': ['guidance', 'direction', 'help', 'رہنمائی', 'مدد', 'هداية'],
            'gratitude': ['thanks', 'gratitude', 'blessing', 'شکر', 'نعمت', 'شكر'],
            'travel': ['travel', 'journey', 'trip', 'سفر', 'سفر'],
            'knowledge': ['knowledge', 'wisdom', 'learning', 'علم', 'حکمت', 'علم'],
            'family': ['family', 'parents', 'children', 'خاندان', 'والدین', 'أسرة'],
            'general': ['general', 'daily', 'routine', 'عام', 'روزانہ']
        }
        
        for category, keywords in categories.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return 'general'
    
    async def _get_dua_content(self, category: str, language: str) -> Dict[str, Any]:
        """Get duas from database and create fallback content"""
        sources = []
        has_database_content = False
        
        try:
            # Search in dua table
            duas = self.db_queries.search_duas(category)
            
            if not duas:
                # Try searching in general duas
                duas = self.db_queries.search_duas()
            
            if duas:
                has_database_content = True
                sources.extend([
                    {
                        "type": "dua",
                        "surah": dua.get('surah', 'Unknown'),
                        "verse": dua.get('aya_number', 'Unknown'),
                        "text": dua.get('aya', '')
                    }
                    for dua in duas[:3]  # Limit to 3 duas
                ])
            
            # Also get some relevant Quranic verses that are commonly used as duas
            dua_verses = await self._search_dua_verses(category, language)
            if dua_verses:
                has_database_content = True
                sources.extend([
                    {
                        "type": "verse_dua",
                        "surah": verse['name_en'],
                        "verse_number": verse['ayatNumber'],
                        "surah_id": verse['surahId']
                    }
                    for verse in dua_verses[:2]
                ])
        
        except Exception as e:
            self.logger.error(f"Error getting dua content: {e}")
        
        return {
            'has_database_content': has_database_content,
            'sources': sources,
            'category': category,
            'duas': duas if 'duas' in locals() else [],
            'verses': dua_verses if 'dua_verses' in locals() else []
        }
    
    async def _search_dua_verses(self, category: str, language: str) -> list:
        """Search for Quranic verses commonly used as duas"""
        # Map categories to Arabic search terms for verses commonly used as duas
        dua_terms = {
            'success': ['نجح', 'فلح', 'وفق'],
            'protection': ['احفظ', 'احم', 'اعوذ'],
            'health': ['شفا', 'عافية', 'صحة'],
            'forgiveness': ['اغفر', 'تب علي'],
            'guidance': ['اهد', 'أرشد'],
            'knowledge': ['علم', 'زد علما'],
            'general': ['رب', 'اللهم']
        }
        
        search_terms = dua_terms.get(category, dua_terms['general'])
        all_verses = []
        
        for term in search_terms:
            verses = self.db_queries.search_verses(term, 'ar')  # Search in Arabic
            all_verses.extend(verses)
        
        # Remove duplicates
        unique_verses = {v['ayatId']: v for v in all_verses}.values()
        return list(unique_verses)[:2]
    
    def _create_general_dua_context(self, category: str, language: str) -> str:
        """Create general dua context when database results are limited"""
        context_templates = {
            'en': {
                'success': "General duas for success include asking Allah for guidance, blessing in your efforts, and success in both this world and the hereafter. Common supplications include 'Rabbana atina fi'd-dunya hasanatan wa fi'l-akhirati hasanatan wa qina 'adhab an-nar' (Our Lord, give us good in this world and good in the hereafter, and save us from the punishment of the Fire).",
                'protection': "Protection duas include seeking refuge in Allah from all harm. The most common is 'A'udhu billahi min ash-shaytani'r-rajim' (I seek refuge in Allah from Satan the accursed) and morning/evening supplications for daily protection.",
                'health': "Health-related duas include asking Allah for healing and well-being. A common supplication is 'Allahumma 'afini fi badani, Allahumma 'afini fi sam'i, Allahumma 'afini fi basari' (O Allah, grant me health in my body, hearing, and sight).",
                'general': "Islamic duas are supplications to Allah. They can be made in any language, but many prophetic duas are preserved in Arabic. The key is sincerity, humility, and trust in Allah's wisdom."
            },
            'ur': {
                'success': "کامیابی کے لیے دعائیں: اللہ سے رہنمائی، اپنی کوششوں میں برکت، اور دنیا و آخرت میں کامیابی مانگیں۔",
                'protection': "حفاظت کی دعائیں: تمام نقصانات سے اللہ کی پناہ مانگیں۔ صبح و شام کی دعائیں پڑھیں۔",
                'health': "صحت کی دعائیں: اللہ سے شفا اور عافیت مانگیں۔ جسم، کان اور آنکھوں کی صحت کے لیے دعا کریں۔",
                'general': "اسلامی دعائیں اللہ سے التجا ہیں۔ یہ کسی بھی زبان میں کی جا سکتی ہیں، لیکن اصل بات خلوص اور اللہ پر بھروسہ ہے۔"
            }
        }
        
        lang_templates = context_templates.get(language, context_templates['en'])
        return lang_templates.get(category, lang_templates['general'])
    
    def _format_duas_context(self, dua_content: Dict, language: str) -> str:
        """Format duas for LLM context"""
        context = f"Relevant duas for {dua_content['category']}:\n\n"
        
        # Add duas from database
        if 'duas' in dua_content and dua_content['duas']:
            context += "Duas from the database:\n"
            for i, dua in enumerate(dua_content['duas'], 1):
                context += f"{i}. From Surah {dua.get('surah', 'Unknown')}, Verse {dua.get('aya_number', 'Unknown')}:\n"
                context += f"   {dua.get('aya', '')}\n\n"
        
        # Add Quranic verses used as duas
        if 'verses' in dua_content and dua_content['verses']:
            context += "Quranic verses commonly used as duas:\n"
            for verse in dua_content['verses']:
                context += f"- Surah {verse['name_en']}, Verse {verse['ayatNumber']}: {verse['arabicText']}\n"
                if language == 'ur' and verse.get('urduTranslation'):
                    context += f"  {verse['urduTranslation']}\n"
                context += "\n"
        
        return context