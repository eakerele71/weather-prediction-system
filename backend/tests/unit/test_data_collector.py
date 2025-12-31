"""Unit tests for data collector service"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.data_collector import (
    WeatherDataCollector,
    APIClient,
    DataValidator
)
from app.models import Location, WeatherData


class TestAPIClient:
    """Tests for APIClient"""

    def test_api_client_initialization(self):
        """Test APIClient initialization"""
        client = APIClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.timeout == 10
        assert client.base_url == "https://api.openweathermap.org/data/2.5"

    def test_api_client_custom_timeout(self):
        """Test APIClient with custom timeout"""
        client = APIClient(api_key="test_key", timeout=30)
        assert client.timeout == 30

    @pytest.mark.asyncio
    async def test_fetch_current_weather_success(self):
        """Test successful weather data fetch"""
        client = APIClient(api_key="test_key")
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        mock_response = {
            "main": {"temp": 15.5, "humidity": 65, "pressure": 1013},
            "wind": {"speed": 5.2, "deg": 180},
            "clouds": {"all": 40},
            "weather": [{"main": "Cloudy"}],
            "rain": {"1h": 0}
        }

        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_get.return_value = mock_response_obj

            result = await client.fetch_current_weather(location)
            assert result is not None
            assert result["main"]["temp"] == 15.5

    @pytest.mark.asyncio
    async def test_fetch_current_weather_no_api_key(self):
        """Test fetch with no API key"""
        client = APIClient(api_key=None)
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        result = await client.fetch_current_weather(location)
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_forecast_success(self):
        """Test successful forecast fetch"""
        client = APIClient(api_key="test_key")
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        mock_response = {"list": []}

        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_get.return_value = mock_response_obj

            result = await client.fetch_forecast(location)
            assert result is not None


class TestDataValidator:
    """Tests for DataValidator"""

    def test_validate_valid_data(self):
        """Test validation of valid weather data"""
        valid_data = {
            "main": {"temp": 15.5, "humidity": 65, "pressure": 1013},
            "wind": {"speed": 5.2, "deg": 180},
            "clouds": {"all": 40},
            "weather": [{"main": "Cloudy"}]
        }

        is_valid, error = DataValidator.validate_data(valid_data)
        assert is_valid is True
        assert error is None

    def test_validate_empty_data(self):
        """Test validation of empty data"""
        is_valid, error = DataValidator.validate_data({})
        assert is_valid is False
        assert error is not None

    def test_validate_missing_main_data(self):
        """Test validation with missing main data"""
        invalid_data = {
            "wind": {"speed": 5.2, "deg": 180},
            "clouds": {"all": 40},
            "weather": [{"main": "Cloudy"}]
        }

        is_valid, error = DataValidator.validate_data(invalid_data)
        assert is_valid is False
        assert "main" in error.lower()

    def test_validate_missing_temperature(self):
        """Test validation with missing temperature"""
        invalid_data = {
            "main": {"humidity": 65, "pressure": 1013},
            "wind": {"speed": 5.2, "deg": 180},
            "clouds": {"all": 40},
            "weather": [{"main": "Cloudy"}]
        }

        is_valid, error = DataValidator.validate_data(invalid_data)
        assert is_valid is False
        assert "temperature" in error.lower()

    def test_validate_invalid_temperature_too_high(self):
        """Test validation with temperature too high"""
        invalid_data = {
            "main": {"temp": 61, "humidity": 65, "pressure": 1013},
            "wind": {"speed": 5.2, "deg": 180},
            "clouds": {"all": 40},
            "weather": [{"main": "Cloudy"}]
        }

        is_valid, error = DataValidator.validate_data(invalid_data)
        assert is_valid is False
        assert "temperature" in error.lower()

    def test_validate_invalid_humidity(self):
        """Test validation with invalid humidity"""
        invalid_data = {
            "main": {"temp": 15.5, "humidity": 101, "pressure": 1013},
            "wind": {"speed": 5.2, "deg": 180},
            "clouds": {"all": 40},
            "weather": [{"main": "Cloudy"}]
        }

        is_valid, error = DataValidator.validate_data(invalid_data)
        assert is_valid is False
        assert "humidity" in error.lower()

    def test_validate_invalid_wind_speed(self):
        """Test validation with invalid wind speed"""
        invalid_data = {
            "main": {"temp": 15.5, "humidity": 65, "pressure": 1013},
            "wind": {"speed": 151, "deg": 180},
            "clouds": {"all": 40},
            "weather": [{"main": "Cloudy"}]
        }

        is_valid, error = DataValidator.validate_data(invalid_data)
        assert is_valid is False
        assert "wind" in error.lower()


class TestWeatherDataCollector:
    """Tests for WeatherDataCollector"""

    def test_collector_initialization(self):
        """Test WeatherDataCollector initialization"""
        collector = WeatherDataCollector()
        assert collector.api_client is not None
        assert collector.validator is not None
        assert collector.retry_attempts == 3

    def test_collector_with_custom_api_client(self):
        """Test WeatherDataCollector with custom API client"""
        api_client = APIClient(api_key="custom_key")
        collector = WeatherDataCollector(api_client=api_client)
        assert collector.api_client == api_client

    @pytest.mark.asyncio
    async def test_fetch_weather_data_success(self):
        """Test successful weather data fetch"""
        collector = WeatherDataCollector()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        mock_response = {
            "main": {"temp": 15.5, "humidity": 65, "pressure": 1013},
            "wind": {"speed": 5.2, "deg": 180},
            "clouds": {"all": 40},
            "weather": [{"main": "Cloudy"}],
            "rain": {"1h": 0}
        }

        with patch.object(collector.api_client, 'fetch_current_weather', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_response

            result = await collector.fetch_weather_data(location)
            assert result is not None
            assert isinstance(result, WeatherData)
            assert result.temperature == 15.5
            assert result.humidity == 65

    @pytest.mark.asyncio
    async def test_fetch_weather_data_failure(self):
        """Test weather data fetch failure"""
        collector = WeatherDataCollector()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        with patch.object(collector.api_client, 'fetch_current_weather', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = None

            result = await collector.fetch_weather_data(location)
            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_weather_data_with_retry(self):
        """Test weather data fetch with retry logic"""
        collector = WeatherDataCollector()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        mock_response = {
            "main": {"temp": 15.5, "humidity": 65, "pressure": 1013},
            "wind": {"speed": 5.2, "deg": 180},
            "clouds": {"all": 40},
            "weather": [{"main": "Cloudy"}],
            "rain": {"1h": 0}
        }

        call_count = 0

        async def mock_fetch(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                return None
            return mock_response

        with patch.object(collector.api_client, 'fetch_current_weather', side_effect=mock_fetch):
            result = await collector.fetch_weather_data(location)
            assert result is not None
            assert call_count == 2  # Should have retried once

    @pytest.mark.asyncio
    async def test_collect_for_multiple_locations(self):
        """Test collecting data for multiple locations"""
        collector = WeatherDataCollector()
        locations = [
            Location(latitude=47.6062, longitude=-122.3321, city="Seattle", country="USA"),
            Location(latitude=34.0522, longitude=-118.2437, city="Los Angeles", country="USA"),
        ]

        mock_response = {
            "main": {"temp": 15.5, "humidity": 65, "pressure": 1013},
            "wind": {"speed": 5.2, "deg": 180},
            "clouds": {"all": 40},
            "weather": [{"main": "Cloudy"}],
            "rain": {"1h": 0}
        }

        with patch.object(collector.api_client, 'fetch_current_weather', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_response

            results = await collector.collect_for_locations(locations)
            assert len(results) == 2
            assert all(isinstance(r, WeatherData) for r in results)

    def test_parse_weather_data(self):
        """Test parsing raw API response to WeatherData"""
        collector = WeatherDataCollector()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        raw_data = {
            "main": {"temp": 15.5, "humidity": 65, "pressure": 1013},
            "wind": {"speed": 5.2, "deg": 180},
            "clouds": {"all": 40},
            "weather": [{"main": "Cloudy"}],
            "rain": {"1h": 2.5}
        }

        weather_data = collector._parse_weather_data(raw_data, location)
        assert weather_data.temperature == 15.5
        assert weather_data.humidity == 65
        assert weather_data.pressure == 1013
        assert weather_data.wind_speed == 5.2
        assert weather_data.wind_direction == 180
        assert weather_data.cloud_cover == 40
        assert weather_data.precipitation == 2.5
        assert weather_data.weather_condition == "Cloudy"

    def test_validate_weather_data(self):
        """Test validation of WeatherData object"""
        collector = WeatherDataCollector()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        weather_data = WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=15.5,
            humidity=65,
            pressure=1013,
            wind_speed=5.2,
            wind_direction=180,
            precipitation=0,
            cloud_cover=40,
            weather_condition="Cloudy"
        )

        is_valid, error = collector.validate_data(weather_data)
        assert is_valid is True
        assert error is None

    def test_validate_weather_data_invalid_temperature(self):
        """Test validation of WeatherData with invalid temperature"""
        collector = WeatherDataCollector()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        # Pydantic validation happens during model creation, so we expect an error
        with pytest.raises(Exception):  # ValidationError
            weather_data = WeatherData(
                location=location,
                timestamp=datetime.now(),
                temperature=61,  # Invalid
                humidity=65,
                pressure=1013,
                wind_speed=5.2,
                wind_direction=180,
                precipitation=0,
                cloud_cover=40,
                weather_condition="Hot"
            )
