"""Caching layer for weather data with fallback support"""
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.models import WeatherData, Location

logger = logging.getLogger(__name__)


class WeatherCache:
    """In-memory cache for weather data with TTL support"""

    def __init__(self, ttl_minutes: int = 30):
        """Initialize weather cache
        
        Args:
            ttl_minutes: Time-to-live for cached data in minutes
        """
        self.ttl_minutes = ttl_minutes
        self._cache: Dict[str, tuple[WeatherData, datetime]] = {}
        logger.info(f"Weather cache initialized with TTL={ttl_minutes} minutes")

    def _get_cache_key(self, location: Location) -> str:
        """Generate cache key for a location
        
        Args:
            location: Location object
            
        Returns:
            Cache key string
        """
        return f"{location.latitude:.4f},{location.longitude:.4f}"

    def get(self, location: Location) -> Optional[WeatherData]:
        """Get cached weather data for a location
        
        Args:
            location: Location to retrieve data for
            
        Returns:
            Cached WeatherData or None if not found or expired
        """
        key = self._get_cache_key(location)
        
        if key not in self._cache:
            logger.debug(f"Cache miss for {location.city}")
            return None

        data, cached_at = self._cache[key]
        age = datetime.now() - cached_at

        if age > timedelta(minutes=self.ttl_minutes):
            logger.debug(f"Cache expired for {location.city} (age: {age})")
            del self._cache[key]
            return None

        logger.info(f"Cache hit for {location.city} (age: {age})")
        return data

    def set(self, location: Location, data: WeatherData) -> None:
        """Store weather data in cache
        
        Args:
            location: Location for the data
            data: WeatherData to cache
        """
        key = self._get_cache_key(location)
        self._cache[key] = (data, datetime.now())
        logger.debug(f"Cached weather data for {location.city}")

    def clear(self) -> None:
        """Clear all cached data"""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cleared {count} cached entries")

    def clear_expired(self) -> int:
        """Remove expired entries from cache
        
        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired_keys = []

        for key, (data, cached_at) in self._cache.items():
            age = now - cached_at
            if age > timedelta(minutes=self.ttl_minutes):
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info(f"Removed {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    def get_cache_stats(self) -> dict:
        """Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        now = datetime.now()
        total_entries = len(self._cache)
        expired_count = 0

        for data, cached_at in self._cache.values():
            age = now - cached_at
            if age > timedelta(minutes=self.ttl_minutes):
                expired_count += 1

        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_count,
            "expired_entries": expired_count,
            "ttl_minutes": self.ttl_minutes
        }


class CachedWeatherDataCollector:
    """Weather data collector with caching and fallback support"""

    def __init__(self, collector, cache: Optional[WeatherCache] = None):
        """Initialize cached data collector
        
        Args:
            collector: WeatherDataCollector instance
            cache: WeatherCache instance (creates new if not provided)
        """
        self.collector = collector
        self.cache = cache or WeatherCache()
        self.fallback_enabled = True
        logger.info("Cached weather data collector initialized")

    async def fetch_weather_data(
        self, 
        location: Location, 
        use_cache: bool = True
    ) -> Optional[WeatherData]:
        """Fetch weather data with caching and fallback
        
        Args:
            location: Location to fetch weather for
            use_cache: Whether to use cached data as fallback
            
        Returns:
            WeatherData object or None if all attempts fail
        """
        # Try to fetch fresh data
        try:
            data = await self.collector.fetch_weather_data(location)
            
            if data is not None:
                # Successfully fetched fresh data - cache it
                self.cache.set(location, data)
                logger.info(f"Fetched and cached fresh data for {location.city}")
                return data
            
            # Fetch failed - try cache fallback
            if use_cache and self.fallback_enabled:
                cached_data = self.cache.get(location)
                if cached_data is not None:
                    logger.warning(
                        f"External API unavailable for {location.city}, "
                        f"using cached data"
                    )
                    return cached_data
                else:
                    logger.error(
                        f"External API unavailable and no cached data for {location.city}"
                    )
                    return None
            
            return None

        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            
            # On exception, try cache fallback
            if use_cache and self.fallback_enabled:
                cached_data = self.cache.get(location)
                if cached_data is not None:
                    logger.warning(
                        f"Exception during fetch for {location.city}, "
                        f"using cached data: {e}"
                    )
                    return cached_data
            
            return None

    def get_cached_data(self, location: Location) -> Optional[WeatherData]:
        """Get cached data without attempting fresh fetch
        
        Args:
            location: Location to retrieve cached data for
            
        Returns:
            Cached WeatherData or None
        """
        return self.cache.get(location)

    def enable_fallback(self) -> None:
        """Enable cache fallback"""
        self.fallback_enabled = True
        logger.info("Cache fallback enabled")

    def disable_fallback(self) -> None:
        """Disable cache fallback"""
        self.fallback_enabled = False
        logger.info("Cache fallback disabled")

    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.cache.clear()

    def get_cache_stats(self) -> dict:
        """Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        return self.cache.get_cache_stats()
