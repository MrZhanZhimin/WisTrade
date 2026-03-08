"""
Data caching layer for market data
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DataCache:
    """
    File-based cache for market data
    
    Reduces API calls to data providers and improves performance.
    """
    
    def __init__(self, cache_dir: str = "data/cache", max_age_hours: int = 6):
        """
        Initialize data cache
        
        Args:
            cache_dir: Directory for cache files
            max_age_hours: Maximum age of cached data in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_age = timedelta(hours=max_age_hours)
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache key hash"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path"""
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached data
        
        Args:
            key: Cache key
        
        Returns:
            Cached data or None if expired/not found
        """
        try:
            cache_path = self._get_cache_path(key)
            
            if not cache_path.exists():
                return None
            
            # Read cache file
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if expired
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.max_age:
                logger.debug(f"Cache expired for key: {key}")
                cache_path.unlink()  # Delete expired cache
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return cache_data['data']
            
        except Exception as e:
            logger.error(f"Error reading cache for {key}: {e}")
            return None
    
    def set(self, key: str, data: Any) -> bool:
        """
        Set cached data
        
        Args:
            key: Cache key
            data: Data to cache
        
        Returns:
            True if successful
        """
        try:
            cache_path = self._get_cache_path(key)
            
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'key': key,
                'data': data,
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.debug(f"Cache set for key: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete cached data
        
        Args:
            key: Cache key
        
        Returns:
            True if deleted
        """
        try:
            cache_path = self._get_cache_path(key)
            
            if cache_path.exists():
                cache_path.unlink()
                logger.debug(f"Cache deleted for key: {key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting cache for {key}: {e}")
            return False
    
    def clear_expired(self) -> int:
        """
        Clear all expired cache entries
        
        Returns:
            Number of entries cleared
        """
        try:
            cleared = 0
            
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cache_data['timestamp'])
                    if datetime.now() - cached_time > self.max_age:
                        cache_file.unlink()
                        cleared += 1
                        
                except Exception:
                    # If we can't read it, delete it
                    cache_file.unlink()
                    cleared += 1
            
            logger.info(f"Cleared {cleared} expired cache entries")
            return cleared
            
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
            return 0
    
    def clear_all(self) -> int:
        """
        Clear all cache entries
        
        Returns:
            Number of entries cleared
        """
        try:
            cleared = 0
            
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                cleared += 1
            
            logger.info(f"Cleared all {cleared} cache entries")
            return cleared
            
        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        try:
            total_files = len(list(self.cache_dir.glob("*.json")))
            total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
            
            return {
                'total_entries': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'cache_dir': str(self.cache_dir),
                'max_age_hours': self.max_age.total_seconds() / 3600,
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
