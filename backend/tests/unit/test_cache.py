"""Unit tests for caching layer"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
from app.services.cache import WeatherCache, CachedWeatherDataCollector
from app.models import WeatherData, Location


@pytest.fixture
def sample_location():
    """Sample location for testing"""
    return Location(
        latitude=47.6062,
        longitude=-122.3321,
        city="Seattle",
        country="United States"
    )


@pytest.fixture
def sample_weather_data(sample_location):
    """Sample weather data for testing"""
    return WeatherData(
        location=sample_location,
        timestamp=datetime.now(),
        temperature=15.5,
        humidity=65.0,
        pressure=1013.25,
        wind_speed=5.2,
        wind_direction=180.0,
        precipitation=0.0,
        cloud_cover=40.0,
        weather_condition="Partly Cloudy"
    )


class TestWeatherCache:
    """Test WeatherCache class"""

    def test_cache_initialization(self):
        """Test cache initializes with correct TTL"""
        cache = WeatherCache(ttl_minutes=30)
        assert cache.ttl_minutes == 30

    def test_cache_key_generation(self, sample_location):
        """Test cache key is generated correctly"""
        cache = WeatherCache()
        key = cache._get_cache_key(sample_location)
        assert isinstance(key, str)
        assert "47.6062" in key
        assert "-122.3321" in key

    def test_cache_set_and_get(self, sample_location, sample_weather_data):
        """Test setting and getting cached data"""
        cache = WeatherCache()
        
        # Set data
        cache.set(sample_location, sample_weather_data)
        
        # Get data
        retrieved = cache.get(sample_location)
        assert retrieved is not None
        assert retrieved.temperature == sample_weather_data.temperature
        assert retrieved.location.city == "Seattle"

    def test_cache_miss(self, sample_location):
        """Test cache miss returns None"""
        cache = WeatherCache()
        retrieved = cache.get(sample_location)
        assert retrieved is None

    def test_cache_expiration(self, sample_location, sample_weather_data):
        """Test cached data expires after TTL"""
        cache = WeatherCache(ttl_minutes=0)  # Immediate expiration
        
        # Set data
        cache.set(sample_location, sample_weather_data)
        
        # Data should be expired immediately
        retrieved = cache.get(sample_location)
        assert retrieved is None

    def test_cache_clear(self, sample_location, sample_weather_data):
        """Test clearing cache"""
        cache = WeatherCache()
        
        # Add data
        cache.set(sample_location, sample_weather_data)
        assert cache.get(sample_location) is not None
        
        # Clear cache
        cache.clear()
        assert cache.get(sample_location) is None

    def test_cache_stats(self, sample_location, sample_weather_data):
        """Test cache statistics"""
        cache = WeatherCache()
        
        # Empty cache
        stats = cache.get_cache_stats()
        assert stats["total_entries"] == 0
        
        # Add data
        cache.set(sample_location, sample_weather_data)
        stats = cache.get_cache_stats()
        assert stats["total_entries"] == 1
        assert stats["active_entries"] == 1

    def test_clear_expired(self, sample_location, sample_weather_data):
        """Test clearing expired entries"""
        cache = WeatherCache(ttl_minutes=0)
        
        # Add data that will expire immediately
        cache.set(sample_location, sample_weather_data)
        
        # Clear expired
        removed = cache.clear_expired()
        assert removed == 1
        assert cache.get(sample_location) is None


class TestCachedWeatherDataCollector:
    """Test CachedWeatherDataCollector class"""

    @pytest.mark.asyncio
    async def test_fetch_with_successful_api_call(self, sample_location, sample_weather_data):
        """Test fetching data when API call succeeds"""
        # Mock collector that returns data
        mock_collector = Mock()
        mock_collector.fetch_weather_data = AsyncMock(return_value=sample_weather_data)
        
        cached_collector = CachedWeatherDataCollector(mock_collector)
        
        # Fetch data
        data = await cached_collector.fetch_weather_data(sample_location)
        
        assert data is not None
        assert data.temperature == sample_weather_data.temperature
        
        # Verify data was cached
        cached = cached_collector.get_cached_data(sample_location)
        assert cached is not None

    @pytest.mark.asyncio
    async def test_fallback_to_cache_on_api_failure(self, sample_location, sample_weather_data):
        """Test falling back to cache when API fails"""
        # Mock collector that fails
        mock_collector = Mock()
        mock_collector.fetch_weather_data = AsyncMock(return_value=None)
        
        cache = WeatherCache()
        cached_collector = CachedWeatherDataCollector(mock_collector, cache)
        
        # Pre-populate cache
        cache.set(sample_location, sample_weather_data)
        
        # Fetch data (API will fail, should use cache)
        data = await cached_collector.fetch_weather_data(sample_location)
        
        assert data is not None
        assert data.temperature == sample_weather_data.temperature

    @pytest.mark.asyncio
    async def test_no_fallback_when_cache_empty(self, sample_location):
        """Test returns None when API fails and cache is empty"""
        # Mock collector that fails
        mock_collector = Mock()
        mock_collector.fetch_weather_data = AsyncMock(return_value=None)
        
        cached_collector = CachedWeatherDataCollector(mock_collector)
        
        # Fetch data (API will fail, cache is empty)
        data = await cached_collector.fetch_weather_data(sample_location)
        
        assert data is None

    @pytest.mark.asyncio
    async def test_fallback_on_exception(self, sample_location, sample_weather_data):
        """Test falling back to cache when exception occurs"""
        # Mock collector that raises exception
        mock_collector = Mock()
        mock_collector.fetch_weather_data = AsyncMock(side_effect=Exception("API Error"))
        
        cache = WeatherCache()
        cached_collector = CachedWeatherDataCollector(mock_collector, cache)
        
        # Pre-populate cache
        cache.set(sample_location, sample_weather_data)
        
        # Fetch data (exception will occur, should use cache)
        data = await cached_collector.fetch_weather_data(sample_location)
        
        assert data is not None
        assert data.temperature == sample_weather_data.temperature

    @pytest.mark.asyncio
    async def test_disable_fallback(self, sample_location, sample_weather_data):
        """Test disabling cache fallback"""
        # Mock collector that fails
        mock_collector = Mock()
        mock_collector.fetch_weather_data = AsyncMock(return_value=None)
        
        cache = WeatherCache()
        cached_collector = CachedWeatherDataCollector(mock_collector, cache)
        
        # Pre-populate cache
        cache.set(sample_location, sample_weather_data)
        
        # Disable fallback
        cached_collector.disable_fallback()
        
        # Fetch data (API will fail, fallback disabled, should return None)
        data = await cached_collector.fetch_weather_data(sample_location)
        
        assert data is None

    @pytest.mark.asyncio
    async def test_enable_fallback(self, sample_location, sample_weather_data):
        """Test enabling cache fallback"""
        # Mock collector that fails
        mock_collector = Mock()
        mock_collector.fetch_weather_data = AsyncMock(return_value=None)
        
        cache = WeatherCache()
        cached_collector = CachedWeatherDataCollector(mock_collector, cache)
        
        # Pre-populate cache
        cache.set(sample_location, sample_weather_data)
        
        # Disable then enable fallback
        cached_collector.disable_fallback()
        cached_collector.enable_fallback()
        
        # Fetch data (API will fail, fallback enabled, should use cache)
        data = await cached_collector.fetch_weather_data(sample_location)
        
        assert data is not None

    def test_get_cached_data_directly(self, sample_location, sample_weather_data):
        """Test getting cached data without fetch"""
        mock_collector = Mock()
        cache = WeatherCache()
        cached_collector = CachedWeatherDataCollector(mock_collector, cache)
        
        # Pre-populate cache
        cache.set(sample_location, sample_weather_data)
        
        # Get cached data directly
        data = cached_collector.get_cached_data(sample_location)
        
        assert data is not None
        assert data.temperature == sample_weather_data.temperature

    def test_clear_cache(self, sample_location, sample_weather_data):
        """Test clearing cache through collector"""
        mock_collector = Mock()
        cache = WeatherCache()
        cached_collector = CachedWeatherDataCollector(mock_collector, cache)
        
        # Pre-populate cache
        cache.set(sample_location, sample_weather_data)
        
        # Clear cache
        cached_collector.clear_cache()
        
        # Verify cache is empty
        data = cached_collector.get_cached_data(sample_location)
        assert data is None

    def test_get_cache_stats(self, sample_location, sample_weather_data):
        """Test getting cache statistics"""
        mock_collector = Mock()
        cache = WeatherCache()
        cached_collector = CachedWeatherDataCollector(mock_collector, cache)
        
        # Pre-populate cache
        cache.set(sample_location, sample_weather_data)
        
        # Get stats
        stats = cached_collector.get_cache_stats()
        
        assert stats["total_entries"] == 1
        assert stats["active_entries"] == 1
