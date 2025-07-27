import json
import time
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

class CacheService:
    """Simple in-memory cache service for performance optimization"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = 3600  # 1 hour default TTL
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments"""
        key_data = f"{prefix}:{':'.join(map(str, args))}"
        if kwargs:
            key_data += f":{json.dumps(kwargs, sort_keys=True)}"
        
        # Hash long keys to keep them manageable
        if len(key_data) > 100:
            return f"{prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"
        
        return key_data
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            return None
        
        cache_entry = self._cache[key]
        
        # Check if expired
        if cache_entry['expires_at'] < time.time():
            del self._cache[key]
            return None
        
        # Update access time
        cache_entry['accessed_at'] = time.time()
        
        return cache_entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        if ttl is None:
            ttl = self._default_ttl
        
        self._cache[key] = {
            'value': value,
            'created_at': time.time(),
            'accessed_at': time.time(),
            'expires_at': time.time() + ttl
        }
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry['expires_at'] < current_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        total_entries = len(self._cache)
        expired_entries = sum(
            1 for entry in self._cache.values()
            if entry['expires_at'] < current_time
        )
        
        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_entries,
            'expired_entries': expired_entries,
            'memory_usage_mb': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        try:
            import sys
            total_size = sys.getsizeof(self._cache)
            for key, entry in self._cache.items():
                total_size += sys.getsizeof(key)
                total_size += sys.getsizeof(entry)
                total_size += sys.getsizeof(entry['value'])
            
            return total_size / (1024 * 1024)  # Convert to MB
        except:
            return 0.0
    
    # Decorator for caching function results
    def cached(self, prefix: str, ttl: Optional[int] = None):
        """Decorator to cache function results"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator

# Global cache instance
cache = CacheService()

class SEOAnalysisCache:
    """Specialized cache for SEO analysis results"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.analysis_ttl = 1800  # 30 minutes for analysis results
        self.domain_info_ttl = 3600  # 1 hour for domain info
        self.backlinks_ttl = 7200  # 2 hours for backlinks
    
    def get_analysis_result(self, domain: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result"""
        key = self.cache._generate_key('analysis', domain, analysis_type)
        return self.cache.get(key)
    
    def set_analysis_result(self, domain: str, analysis_type: str, result: Dict[str, Any]) -> None:
        """Cache analysis result"""
        key = self.cache._generate_key('analysis', domain, analysis_type)
        self.cache.set(key, result, self.analysis_ttl)
    
    def get_domain_info(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get cached domain information"""
        key = self.cache._generate_key('domain_info', domain)
        return self.cache.get(key)
    
    def set_domain_info(self, domain: str, info: Dict[str, Any]) -> None:
        """Cache domain information"""
        key = self.cache._generate_key('domain_info', domain)
        self.cache.set(key, info, self.domain_info_ttl)
    
    def get_backlinks(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get cached backlinks"""
        key = self.cache._generate_key('backlinks', domain)
        return self.cache.get(key)
    
    def set_backlinks(self, domain: str, backlinks: Dict[str, Any]) -> None:
        """Cache backlinks"""
        key = self.cache._generate_key('backlinks', domain)
        self.cache.set(key, backlinks, self.backlinks_ttl)
    
    def invalidate_domain(self, domain: str) -> None:
        """Invalidate all cached data for a domain"""
        # This is a simple implementation - in production you'd want more sophisticated invalidation
        keys_to_delete = []
        for key in self.cache._cache.keys():
            if domain in key:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            self.cache.delete(key)

# Global SEO analysis cache
seo_cache = SEOAnalysisCache(cache)

