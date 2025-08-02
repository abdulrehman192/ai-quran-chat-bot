from langdetect import detect, DetectorFactory
from config.settings import Settings

# Set seed for consistent results
DetectorFactory.seed = 0

class LanguageDetector:
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect language of input text"""
        try:
            detected = detect(text)
            # Map detected languages to supported ones
            language_map = {
                'ur': 'ur',
                'ar': 'ar', 
                'en': 'en'
            }
            return language_map.get(detected, Settings.DEFAULT_LANGUAGE)
        except:
            return Settings.DEFAULT_LANGUAGE