from typing import List, Dict, Optional, Tuple
from database.connection import DatabaseManager


class QuranQueries:
    def __init__(self):
        self.db = DatabaseManager()
    
    def search_verses(self, keyword: str, language: str = "en") -> List[Dict]:
        """Search for verses containing keyword with English fallback"""
        try:
            if language == "en":
                # For English queries, search in Arabic text and provide translation
                query = """
                SELECT q.ayatId, q.ayatNumber, q.arabicText, q.urduTranslation, 
                       s.name_en, s.name_ar, q.surahId, q.withoutAerab
                FROM quran q
                JOIN surah s ON q.surahId = s.id
                WHERE q.arabicText LIKE ? OR q.withoutAerab LIKE ? OR s.name_en LIKE ?
                ORDER BY q.surahId, q.ayatNumber
                LIMIT 10
                """
                keyword_pattern = f"%{keyword}%"
                params = (keyword_pattern, keyword_pattern, keyword_pattern)
                
            elif language == "ur":
                query = """
                SELECT q.ayatId, q.ayatNumber, q.arabicText, q.urduTranslation, 
                       s.name_en, s.name_ar, q.surahId
                FROM quran q
                JOIN surah s ON q.surahId = s.id
                WHERE q.urduTranslation LIKE ? OR q.arabicText LIKE ?
                ORDER BY q.surahId, q.ayatNumber
                LIMIT 10
                """
                keyword_pattern = f"%{keyword}%"
                params = (keyword_pattern, keyword_pattern)
                
            else:  # Arabic
                query = """
                SELECT q.ayatId, q.ayatNumber, q.arabicText, q.urduTranslation, 
                       s.name_en, s.name_ar, q.surahId
                FROM quran q
                JOIN surah s ON q.surahId = s.id
                WHERE q.arabicText LIKE ?
                ORDER BY q.surahId, q.ayatNumber
                LIMIT 10
                """
                keyword_pattern = f"%{keyword}%"
                params = (keyword_pattern,)
            
            results = self.db.execute_query(query, params)
            return [dict(row) for row in results]
            
        except Exception as e:
            print(f"Error searching verses: {e}")
            return []
    
    def search_verses_by_topic(self, topic: str, language: str = "en") -> List[Dict]:
        """Search verses by topic using semantic keywords"""
        topic_keywords = {
            'patience': ['صبر', 'صابر', 'اصبر'],
            'forgiveness': ['غفر', 'غفور', 'تواب'],
            'mercy': ['رحم', 'رحيم', 'رحمن'],
            'guidance': ['هدى', 'هداية', 'مهتد'],
            'peace': ['سلام', 'سكينة', 'أمن'],
            'knowledge': ['علم', 'عالم', 'تعلم'],
            'prayer': ['صبح', 'مساء', 'ذكر', 'سجود'],
            'charity': ['صدقة', 'زكاة', 'انفق'],
            'faith': ['ايمان', 'آمن', 'مؤمن'],
            'hope': ['رجاء', 'أمل', 'طمع']
        }
        
        keywords = topic_keywords.get(topic.lower(), [topic])
        all_verses = []
        
        for keyword in keywords:
            verses = self.search_verses(keyword, language)
            all_verses.extend(verses)
        
        # Remove duplicates based on ayatId
        unique_verses = {v['ayatId']: v for v in all_verses}.values()
        return list(unique_verses)[:5]
    
    def get_surah_info(self, surah_id: int) -> Optional[Dict]:
        """Get surah information"""
        query = "SELECT * FROM surah WHERE id = ?"
        result = self.db.execute_query(query, (surah_id,))
        return dict(result[0]) if result else None
    
    def get_all_surahs(self) -> List[Dict]:
        """Get all surah information"""
        query = "SELECT * FROM surah ORDER BY id"
        return [dict(row) for row in self.db.execute_query(query)]
    
    def get_surah_verses(self, surah_id: int, limit: int = 10) -> List[Dict]:
        """Get verses from a specific surah"""
        query = """
        SELECT q.ayatId, q.ayatNumber, q.arabicText, q.urduTranslation, 
               s.name_en, s.name_ar, q.surahId
        FROM quran q
        JOIN surah s ON q.surahId = s.id
        WHERE q.surahId = ?
        ORDER BY q.ayatNumber
        LIMIT ?
        """
        return [dict(row) for row in self.db.execute_query(query, (surah_id, limit))]
    
    def search_duas(self, category: str = None) -> List[Dict]:
        """Search duas by category or get all"""
        if category:
            query = "SELECT * FROM dua WHERE surah LIKE ? OR aya LIKE ? LIMIT 5"
            params = (f"%{category}%", f"%{category}%")
        else:
            query = "SELECT * FROM dua LIMIT 10"
            params = ()
            
        return [dict(row) for row in self.db.execute_query(query, params)]
    
    def get_random_dua(self) -> Optional[Dict]:
        """Get a random dua"""
        query = "SELECT * FROM dua ORDER BY RANDOM() LIMIT 1"
        result = self.db.execute_query(query)
        return dict(result[0]) if result else None
    
    def get_allah_names(self, search_term: str = None) -> List[Dict]:
        """Get Allah's names with optional search"""
        if search_term:
            query = """
            SELECT * FROM allah_names 
            WHERE english LIKE ? OR englishMeaning LIKE ? OR urduMeaning LIKE ? OR arabic LIKE ?
            LIMIT 10
            """
            pattern = f"%{search_term}%"
            params = (pattern, pattern, pattern, pattern)
        else:
            query = "SELECT * FROM allah_names LIMIT 20"
            params = ()
            
        return [dict(row) for row in self.db.execute_query(query, params)]
    
    def get_random_allah_name(self) -> Optional[Dict]:
        """Get a random Allah's name"""
        query = "SELECT * FROM allah_names ORDER BY RANDOM() LIMIT 1"
        result = self.db.execute_query(query)
        return dict(result[0]) if result else None
    
    def get_kalmas(self) -> List[Dict]:
        """Get all Kalmas"""
        query = "SELECT * FROM kalmas ORDER BY id"
        return [dict(row) for row in self.db.execute_query(query)]
    
    def get_juz_info(self, juz_number: int = None) -> List[Dict]:
        """Get Juz (Para) information"""
        if juz_number:
            query = "SELECT * FROM juz WHERE no = ?"
            params = (juz_number,)
        else:
            query = "SELECT * FROM juz ORDER BY no"
            params = ()
        
        return [dict(row) for row in self.db.execute_query(query, params)]
    
    def get_sample_verses(self, count: int = 5) -> List[Dict]:
        """Get random sample verses for educational purposes"""
        query = """
        SELECT q.ayatId, q.ayatNumber, q.arabicText, q.urduTranslation, 
               s.name_en, s.name_ar, q.surahId
        FROM quran q
        JOIN surah s ON q.surahId = s.id
        ORDER BY RANDOM()
        LIMIT ?
        """
        return [dict(row) for row in self.db.execute_query(query, (count,))]
    
    def get_verse_by_reference(self, surah_id: int, verse_number: int) -> Optional[Dict]:
        """Get specific verse by surah and verse number"""
        query = """
        SELECT q.ayatId, q.ayatNumber, q.arabicText, q.urduTranslation, 
               s.name_en, s.name_ar, q.surahId
        FROM quran q
        JOIN surah s ON q.surahId = s.id
        WHERE q.surahId = ? AND q.ayatNumber = ?
        """
        result = self.db.execute_query(query, (surah_id, verse_number))
        return dict(result[0]) if result else None
    
    def search_by_surah_name(self, surah_name: str) -> Optional[Dict]:
        """Search surah by name (English or Arabic)"""
        query = """
        SELECT * FROM surah 
        WHERE name_en LIKE ? OR name_ar LIKE ?
        LIMIT 1
        """
        pattern = f"%{surah_name}%"
        result = self.db.execute_query(query, (pattern, pattern))
        return dict(result[0]) if result else None
    
    def get_favorites(self, table_name: str) -> List[Dict]:
        """Get favorite items from any table"""
        valid_tables = ['quran', 'allah_names', 'dua', 'surah', 'juz', 'tasbih']
        if table_name not in valid_tables:
            return []
        
        if table_name == 'quran':
            query = f"""
            SELECT q.*, s.name_en, s.name_ar 
            FROM {table_name} q
            JOIN surah s ON q.surahId = s.id
            WHERE q.favourite = 1
            """
        else:
            query = f"SELECT * FROM {table_name} WHERE favorite = 1 OR favourite = 1"
        
        return [dict(row) for row in self.db.execute_query(query)]