from agents.base_worker import BaseWorker
from typing import Dict, Any

class NamesWorker(BaseWorker):
    """Worker for Allah's names (Asma ul Husna)"""
    
    def can_handle(self, query: str, intent: str) -> bool:
        names_keywords = [
            "allah", "names", "asma", "husna", "attributes",
            "اللہ", "نام", "اسماء", "حسنیٰ",  # Urdu
            "الله", "أسماء", "الحسنى"    # Arabic
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in names_keywords) or intent == "names_request"
    
    async def process_request(self, query: str, language: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Extract search term if any
            search_term = self._extract_name_search_term(query)
            
            # Get Allah's names
            names = self.db_queries.get_allah_names(search_term)
            
            # Format context for LLM
            context_text = self._format_names_context(names, language)
            
            # Generate response
            response = await self.llm_client.generate_response(query, context_text, language)
            
            return self.format_response(
                content=response,
                sources=self._format_names_sources(names),
                language=language
            )
            
        except Exception as e:
            self.logger.error(f"Error in NamesWorker: {e}")
            return self.format_response("Error processing names request", language=language)
    
    def _extract_name_search_term(self, query: str) -> str:
        """Extract specific name being searched"""
        # Simple extraction - enhance as needed
        words = query.split()
        for word in words:
            if len(word) > 3 and word.lower() not in ['allah', 'name', 'names', 'asma']:
                return word
        return None
    
    def _format_names_context(self, names: list, language: str) -> str:
        """Format names for LLM context"""
        context = "Allah's Beautiful Names (Asma ul Husna):\n\n"
        for name in names:
            context += f"Arabic: {name['arabic']}\n"
            context += f"English: {name['english']}\n"
            if language == 'ur':
                context += f"Urdu Meaning: {name['urduMeaning']}\n"
            else:
                context += f"English Meaning: {name['englishMeaning']}\n"
            context += f"Explanation: {name['englishExplanation']}\n\n"
        return context
    
    def _format_names_sources(self, names: list) -> list:
        """Format names sources"""
        return [
            {
                "type": "allah_name",
                "arabic": name['arabic'],
                "english": name['english']
            }
            for name in names
        ]