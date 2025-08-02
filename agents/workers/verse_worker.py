from agents.base_worker import BaseWorker
from typing import Dict, Any

class VerseWorker(BaseWorker):
    """Worker for handling Quranic verse searches with English support"""
    
    def can_handle(self, query: str, intent: str) -> bool:
        verse_keywords = [
            "verse", "ayah", "surah", "chapter", "quran", "quranic",
            "آیت", "سورہ", "قرآن",  # Urdu
            "آية", "سورة", "قرآن"   # Arabic
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in verse_keywords) or intent == "verse_search"
    
    async def process_request(self, query: str, language: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Use enhanced search with fallback
            verses, has_database_results = await self.search_with_fallback(query, language)
            
            # Format context for LLM
            if has_database_results:
                context_text = self._format_verses_context(verses, language)
            else:
                context_text = ""
            
            # Generate response using LLM with appropriate template
            response = await self.llm_client.generate_response(
                query, context_text, language, "verse_search"
            )
            
            return self.format_response(
                content=response,
                sources=self._format_verse_sources(verses),
                language=language,
                has_database_results=has_database_results
            )
            
        except Exception as e:
            self.logger.error(f"Error in VerseWorker: {e}")
            return self.format_response(
                "Error processing verse request", 
                language=language, 
                has_database_results=False
            )
    
    def _format_verses_context(self, verses: list, language: str) -> str:
        """Format verses for LLM context with language consideration"""
        if not verses:
            return ""
        
        context = "Relevant Quranic verses found:\n\n"
        for i, verse in enumerate(verses[:5], 1):  # Limit to 5 verses
            context += f"{i}. Surah {verse['name_en']} ({verse['surahId']}), Verse {verse['ayatNumber']}:\n"
            context += f"Arabic: {verse['arabicText']}\n"
            
            # Add translation based on language preference
            if language == 'ur' and verse.get('urduTranslation'):
                context += f"Urdu Translation: {verse['urduTranslation']}\n"
            elif language == 'en':
                if verse.get('urduTranslation'):
                    context += f"Translation (via Urdu): {verse['urduTranslation']}\n"
                context += "Note: Please provide English interpretation based on the Arabic text.\n"
            
            context += "\n"
        
        return context
    
    def _format_verse_sources(self, verses: list) -> list:
        """Format verse sources for response"""
        return [
            {
                "type": "verse",
                "surah": verse['name_en'],
                "verse_number": verse['ayatNumber'],
                "surah_id": verse['surahId'],
                "arabic_text": verse.get('arabicText', ''),
                "translation": verse.get('urduTranslation', '')
            }
            for verse in verses[:5]
        ]