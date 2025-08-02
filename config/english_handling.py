"""
Configuration for handling English queries when database has Arabic/Urdu content
"""

class EnglishHandlingConfig:
    """Configuration for English query processing"""
    
    # Mapping of English concepts to Arabic search terms
    ENGLISH_TO_ARABIC_MAPPING = {
        # Emotions and States
        'patience': ['صبر', 'صابر', 'اصبر'],
        'mercy': ['رحم', 'رحيم', 'رحمن', 'رحمة'],
        'forgiveness': ['غفر', 'غفور', 'تواب', 'غفران'],
        'guidance': ['هدى', 'هداية', 'مهتد', 'هادي'],
        'peace': ['سلام', 'سكينة', 'أمن', 'سالم'],
        'hope': ['رجاء', 'أمل', 'طمع'],
        'fear': ['خوف', 'خشية', 'رهبة'],
        'love': ['حب', 'محبة', 'ود'],
        'gratitude': ['شكر', 'حمد', 'شاكر'],
        'trust': ['توكل', 'ثقة', 'متوكل'],
        
        # Actions and Practices
        'prayer': ['صلاة', 'صلى', 'مصلي', 'ذكر'],
        'charity': ['زكاة', 'صدقة', 'انفاق', 'خير'],
        'fasting': ['صوم', 'صيام', 'صائم'],
        'pilgrimage': ['حج', 'عمرة', 'حاج'],
        'worship': ['عبادة', 'عبد', 'تعبد'],
        'repentance': ['توبة', 'تاب', 'تائب'],
        'remembrance': ['ذكر', 'ذاكر', 'تذكر'],
        
        # Concepts and Values
        'justice': ['عدل', 'عادل', 'قسط'],
        'knowledge': ['علم', 'عالم', 'تعلم'],
        'wisdom': ['حكمة', 'حكيم', 'حكم'],
        'faith': ['ايمان', 'آمن', 'مؤمن'],
        'righteousness': ['تقوى', 'متق', 'بر'],
        'honesty': ['صدق', 'صادق', 'صدقة'],
        'kindness': ['احسان', 'محسن', 'رحمة'],
        'humility': ['تواضع', 'متواضع', 'خشوع'],
        
        # Life Situations
        'difficulty': ['بلاء', 'محنة', 'ضر', 'كرب'],
        'success': ['فلح', 'نجح', 'فوز'],
        'wealth': ['مال', 'غنى', 'ثروة'],
        'poverty': ['فقر', 'فقير', 'مسكين'],
        'health': ['صحة', 'عافية', 'شفاء'],
        'sickness': ['مرض', 'سقم', 'داء'],
        'death': ['موت', 'وفاة', 'منية'],
        'life': ['حياة', 'حي', 'عيش'],
        
        # Relationships
        'family': ['أهل', 'عائلة', 'أسرة'],
        'parents': ['والدين', 'أب', 'أم'],
        'children': ['أطفال', 'أولاد', 'ذرية'],
        'marriage': ['زواج', 'نكاح', 'زوج'],
        'friendship': ['صداقة', 'صديق', 'خل'],
        
        # Time and Events
        'day': ['يوم', 'نهار', 'يومي'],
        'night': ['ليل', 'ليلة', 'ليلي'],
        'morning': ['صباح', 'فجر', 'صبح'],
        'evening': ['مساء', 'عشي', 'آصال'],
        'future': ['مستقبل', 'آتي', 'قادم'],
        'past': ['ماضي', 'سابق', 'قديم']
    }
    
    # Common Islamic phrases and their meanings
    ISLAMIC_PHRASES = {
        'bismillah': 'بسم الله الرحمن الرحيم',
        'alhamdulillah': 'الحمد لله',
        'subhanallah': 'سبحان الله',
        'allahu_akbar': 'الله أكبر',
        'astaghfirullah': 'أستغفر الله',
        'inshallah': 'إن شاء الله',
        'mashallah': 'ما شاء الله',
        'barakallahu_feek': 'بارك الله فيك'
    }
    
    # Topics that commonly have no direct database matches but need guidance
    GENERAL_GUIDANCE_TOPICS = [
        'depression', 'anxiety', 'stress', 'relationship problems',
        'career guidance', 'financial problems', 'parenting advice',
        'marriage counseling', 'grief counseling', 'spiritual growth',
        'character development', 'anger management', 'addiction recovery'
    ]
    
    @classmethod
    def get_arabic_terms(cls, english_concept: str) -> list:
        """Get Arabic search terms for English concept"""
        english_concept = english_concept.lower().strip()
        
        # Direct lookup
        if english_concept in cls.ENGLISH_TO_ARABIC_MAPPING:
            return cls.ENGLISH_TO_ARABIC_MAPPING[english_concept]
        
        # Partial matching
        for key, terms in cls.ENGLISH_TO_ARABIC_MAPPING.items():
            if english_concept in key or key in english_concept:
                return terms
        
        return []
    
    @classmethod
    def is_general_guidance_topic(cls, query: str) -> bool:
        """Check if query is about general guidance that may not have direct verses"""
        query_lower = query.lower()
        return any(topic in query_lower for topic in cls.GENERAL_GUIDANCE_TOPICS)