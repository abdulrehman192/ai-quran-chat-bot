import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class CacheManager:
    """Simple file-based cache for frequent queries"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, query_hash: str) -> str:
        """Get cache file path for query"""
        return os.path.join(self.cache_dir, f"{query_hash}.json")
    
    def _hash_query(self, query: str, language: str) -> str:
        """Create hash for query caching"""
        import hashlib
        combined = f"{query.lower().strip()}_{language}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, query: str, language: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired"""
        try:
            query_hash = self._hash_query(query, language)
            cache_path = self._get_cache_path(query_hash)
            
            if not os.path.exists(cache_path):
                return None
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Check if cache is still valid
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                os.remove(cache_path)  # Remove expired cache
                return None
            
            return cached_data['response']
            
        except Exception:
            return None
    
    def set(self, query: str, language: str, response: Dict[str, Any]):
        """Cache response"""
        try:
            query_hash = self._hash_query(query, language)
            cache_path = self._get_cache_path(query_hash)
            
            cache_data = {
                'query': query,
                'language': language,
                'response': response,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            # Silently fail cache writes
            pass