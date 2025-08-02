from config.settings import Settings
import re

class InputValidator:
    @staticmethod
    def validate_query(query: str) -> tuple[bool, str]:
        """Validate user input query"""
        if not query or not query.strip():
            return False, "Query cannot be empty"
        
        if len(query) > Settings.MAX_QUERY_LENGTH:
            return False, f"Query too long. Maximum {Settings.MAX_QUERY_LENGTH} characters allowed"
        
        # Check for restricted content (basic check)
        query_lower = query.lower()
        for restricted in Settings.RESTRICTED_TOPICS:
            if any(word in query_lower for word in restricted.split()):
                return False, "Please focus on spiritual guidance and Quranic teachings"
        
        return True, "Valid"
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Basic input sanitization"""
        # Remove potentially harmful characters
        cleaned = re.sub(r'[<>\"\'%;()&+]', '', text)
        return cleaned.strip()