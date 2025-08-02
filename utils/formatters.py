from typing import Dict, Any, List
import json

class ResponseFormatter:
    """Format responses for different output types"""
    
    @staticmethod
    def format_for_cli(response: Dict[str, Any]) -> str:
        """Format response for command line interface"""
        formatted = f"🤖 {response['content']}\n"
        
        sources = response.get('sources', [])
        if sources:
            formatted += "\n📚 References:\n"
            for i, source in enumerate(sources, 1):
                if source['type'] == 'verse':
                    formatted += f"  • Surah {source['surah']}, Verse {source['verse_number']}\n"
                elif source['type'] == 'allah_name':
                    formatted += f"  • {source['arabic']} ({source['english']})\n"
        
        return formatted
    
    @staticmethod
    def format_for_api(response: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for API endpoints"""
        return {
            "status": "success" if not response.get('error') else "error",
            "content": response['content'],
            "language": response.get('language', 'en'),
            "sources": response.get('sources', []),
            "metadata": {
                "worker": response.get('worker'),
                "timestamp": response.get('timestamp')
            }
        }
    
    @staticmethod
    def format_for_web(response: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for web interface"""
        return {
            "message": response['content'],
            "language": response.get('language', 'en'),
            "references": ResponseFormatter._format_sources_for_web(response.get('sources', [])),
            "worker_used": response.get('worker', 'Unknown')
        }
    
    @staticmethod
    def _format_sources_for_web(sources: List[Dict]) -> List[Dict]:
        """Format sources for web display"""
        formatted_sources = []
        for source in sources:
            if source['type'] == 'verse':
                formatted_sources.append({
                    "type": "Quranic Verse",
                    "reference": f"Surah {source['surah']}, Verse {source['verse_number']}",
                    "icon": "📖"
                })
            elif source['type'] == 'allah_name':
                formatted_sources.append({
                    "type": "Allah's Name",
                    "reference": f"{source['arabic']} ({source['english']})",
                    "icon": "✨"
                })
            elif source['type'] == 'dua':
                formatted_sources.append({
                    "type": "Dua",
                    "reference": f"From Surah {source['surah']}, Verse {source['verse']}",
                    "icon": "🤲"
                })
        return formatted_sources