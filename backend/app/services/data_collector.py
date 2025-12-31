"""Data collection service for fetching weather data from external APIs"""
import asyncio
import logging
from typing import Optional, List
from datetime import datetime, timedelta
import httpx
from app.models import WeatherData, Location
from app.config import settings

logger = logging.getLogger(__name__)


class APIClient:
    """HTTP client for external weather APIs"""

    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        """Initialize API client
        
        Args:
            api_key: API key for weather service
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or settings.openweather_api_key
        self.timeout = timeout
        self.base_url = "https://api.openweathermap.org/data/2.5"

    async def fetch_current_weather(self, location: Location) -> Optional[dict]:
        """Fetch current weather data from OpenWeatherMap API
        
        Args:
            location: Location to fetch weather for
            
        Returns:
            Weather data dict or None if request fails
        """
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not configured")
            return None

        url = f"{self.base_url}/weather"
        params = {
            "lat": location.latitude,
            "lon": location.longitude,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching weather data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching weather data: {e}")
            return None

    async def fetch_forecast(self, location: Location) -> Optional[dict]:
        """Fetch weather forecast from OpenWeatherMap API
        
        Args:
            location: Location to fetch forecast for
            
        Returns:
            Forecast data dict or None if request fails
        """
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not configured")
            return None

        url = f"{self.base_url}/forecast"
        params = {
            "lat": location.latitude,
            "lon": location.longitude,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching forecast data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching forecast data: {e}")
            return None


class DataValidator:
    """Validates weather data for completeness and correctness"""

    REQUIRED_FIELDS = {
        'temp', 'humidity', 'pressure', 'wind_speed',
        'wind_deg', 'clouds', 'weather'
    }

    @staticmethod
    def validate_data(data: dict) -> tuple[bool, Optional[str]]:
        """Validate weather data from API response
        
        Args:
            data: Raw weather data from API
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not data:
            return False, "Data is empty"

        # Check for required fields
        main_data = data.get('main', {})
        wind_data = data.get('wind', {})
        clouds_data = data.get('clouds', {})
        weather_data = data.get('weather', [])

        if not main_data:
            return False, "Missing main weather data"

        if 'temp' not in main_data:
            return False, "Missing temperature data"

        if 'humidity' not in main_data:
            return False, "Missing humidity data"

        if 'pressure' not in main_data:
            return False, "Missing pressure data"

        if 'speed' not in wind_data:
            return False, "Missing wind speed data"

        if 'deg' not in wind_data:
            return False, "Missing wind direction data"

        if 'all' not in clouds_data:
            return False, "Missing cloud cover data"

        if not weather_data or 'main' not in weather_data[0]:
            return False, "Missing weather condition data"

        # Validate value ranges
        temp = main_data.get('temp')
        if temp is None or temp < -100 or temp > 60:
            return False, f"Invalid temperature: {temp}"

        humidity = main_data.get('humidity')
        if humidity is None or humidity < 0 or humidity > 100:
            return False, f"Invalid humidity: {humidity}"

        wind_speed = wind_data.get('speed')
        if wind_speed is None or wind_speed < 0 or wind_speed > 150:
            return False, f"Invalid wind speed: {wind_speed}"

        return True, None


class WeatherDataCollector:
    """Main service for collecting weather data"""

    def __init__(self, api_client: Optional[APIClient] = None):
        """Initialize data collector
        
        Args:
            api_client: API client instance (creates new if not provided)
        """
        self.api_client = api_client or APIClient()
        self.validator = DataValidator()
        self.retry_attempts = 3
        self.retry_delay = 1  # seconds

    async def fetch_weather_data(self, location: Location) -> Optional[WeatherData]:
        """Fetch and validate weather data for a location with retry logic
        
        Args:
            location: Location to fetch weather for
            
        Returns:
            WeatherData object or None if fetch fails
        """
        for attempt in range(self.retry_attempts):
            try:
                raw_data = await self.api_client.fetch_current_weather(location)

                if raw_data is None:
                    if attempt < self.retry_attempts - 1:
                        delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Retrying in {delay}s (attempt {attempt + 1}/{self.retry_attempts})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        logger.error("Failed to fetch weather data after all retries")
                        return None

                # Validate data
                is_valid, error_msg = self.validator.validate_data(raw_data)
                if not is_valid:
                    logger.error(f"Data validation failed: {error_msg}")
                    if attempt < self.retry_attempts - 1:
                        delay = self.retry_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    else:
                        return None

                # Convert to WeatherData model
                weather_data = self._parse_weather_data(raw_data, location)
                logger.info(f"Successfully collected weather data for {location.city}")
                return weather_data

            except Exception as e:
                logger.error(f"Error during data collection (attempt {attempt + 1}): {e}")
                if attempt < self.retry_attempts - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    return None

        return None

    def _parse_weather_data(self, raw_data: dict, location: Location) -> WeatherData:
        """Parse raw API response into WeatherData model
        
        Args:
            raw_data: Raw weather data from API
            location: Location object
            
        Returns:
            WeatherData object
        """
        main = raw_data.get('main', {})
        wind = raw_data.get('wind', {})
        clouds = raw_data.get('clouds', {})
        weather = raw_data.get('weather', [{}])[0]

        return WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=main.get('temp', 0),
            humidity=main.get('humidity', 0),
            pressure=main.get('pressure', 0),
            wind_speed=wind.get('speed', 0),
            wind_direction=wind.get('deg', 0),
            precipitation=raw_data.get('rain', {}).get('1h', 0),
            cloud_cover=clouds.get('all', 0),
            weather_condition=weather.get('main', 'Unknown')
        )

    async def collect_for_locations(self, locations: List[Location]) -> List[WeatherData]:
        """Collect weather data for multiple locations concurrently
        
        Args:
            locations: List of locations to collect data for
            
        Returns:
            List of successfully collected WeatherData objects
        """
        tasks = [self.fetch_weather_data(loc) for loc in locations]
        results = await asyncio.gather(*tasks)
        return [data for data in results if data is not None]

    def validate_data(self, data: WeatherData) -> tuple[bool, Optional[str]]:
        """Validate WeatherData object
        
        Args:
            data: WeatherData to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Pydantic validation happens automatically during model creation
            # This method is for additional business logic validation
            if data.temperature < -100 or data.temperature > 60:
                return False, "Temperature out of valid range"

            if data.humidity < 0 or data.humidity > 100:
                return False, "Humidity out of valid range"

            if data.wind_speed < 0 or data.wind_speed > 150:
                return False, "Wind speed out of valid range"

            return True, None
        except Exception as e:
            return False, str(e)
