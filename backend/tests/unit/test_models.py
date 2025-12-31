"""Unit tests for data models"""
import pytest
from datetime import datetime, date, timedelta
from pydantic import ValidationError
from app.models import (
    Location, WeatherData, Forecast, AccuracyMetrics,
    WeatherWarning, UserLocation, ChartData
)


class TestLocation:
    """Tests for Location model"""

    def test_valid_location(self):
        """Test creating a valid location"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        assert location.latitude == 47.6062
        assert location.longitude == -122.3321
        assert location.city == "Seattle"

    def test_invalid_latitude_too_high(self):
        """Test that latitude > 90 is rejected"""
        with pytest.raises(ValidationError):
            Location(
                latitude=91,
                longitude=-122.3321,
                city="Seattle",
                country="United States"
            )

    def test_invalid_latitude_too_low(self):
        """Test that latitude < -90 is rejected"""
        with pytest.raises(ValidationError):
            Location(
                latitude=-91,
                longitude=-122.3321,
                city="Seattle",
                country="United States"
            )

    def test_invalid_longitude_too_high(self):
        """Test that longitude > 180 is rejected"""
        with pytest.raises(ValidationError):
            Location(
                latitude=47.6062,
                longitude=181,
                city="Seattle",
                country="United States"
            )

    def test_empty_city_name(self):
        """Test that empty city name is rejected"""
        with pytest.raises(ValidationError):
            Location(
                latitude=47.6062,
                longitude=-122.3321,
                city="",
                country="United States"
            )


class TestWeatherData:
    """Tests for WeatherData model"""

    def test_valid_weather_data(self):
        """Test creating valid weather data"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        weather = WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=15.5,
            humidity=65,
            pressure=1013.25,
            wind_speed=5.2,
            wind_direction=180,
            precipitation=0.0,
            cloud_cover=40,
            weather_condition="Partly Cloudy"
        )
        assert weather.temperature == 15.5
        assert weather.humidity == 65

    def test_invalid_temperature_too_high(self):
        """Test that temperature > 60°C is rejected"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        with pytest.raises(ValidationError):
            WeatherData(
                location=location,
                timestamp=datetime.now(),
                temperature=61,
                humidity=65,
                pressure=1013.25,
                wind_speed=5.2,
                wind_direction=180,
                precipitation=0.0,
                cloud_cover=40,
                weather_condition="Hot"
            )

    def test_invalid_temperature_too_low(self):
        """Test that temperature < -100°C is rejected"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        with pytest.raises(ValidationError):
            WeatherData(
                location=location,
                timestamp=datetime.now(),
                temperature=-101,
                humidity=65,
                pressure=1013.25,
                wind_speed=5.2,
                wind_direction=180,
                precipitation=0.0,
                cloud_cover=40,
                weather_condition="Cold"
            )

    def test_invalid_humidity_too_high(self):
        """Test that humidity > 100 is rejected"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        with pytest.raises(ValidationError):
            WeatherData(
                location=location,
                timestamp=datetime.now(),
                temperature=15.5,
                humidity=101,
                pressure=1013.25,
                wind_speed=5.2,
                wind_direction=180,
                precipitation=0.0,
                cloud_cover=40,
                weather_condition="Humid"
            )

    def test_invalid_wind_speed_too_high(self):
        """Test that wind speed > 150 m/s is rejected"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        with pytest.raises(ValidationError):
            WeatherData(
                location=location,
                timestamp=datetime.now(),
                temperature=15.5,
                humidity=65,
                pressure=1013.25,
                wind_speed=151,
                wind_direction=180,
                precipitation=0.0,
                cloud_cover=40,
                weather_condition="Windy"
            )


class TestForecast:
    """Tests for Forecast model"""

    def test_valid_forecast(self):
        """Test creating a valid forecast"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        forecast = Forecast(
            location=location,
            forecast_date=date.today(),
            predicted_temperature_high=18.0,
            predicted_temperature_low=12.0,
            precipitation_probability=0.3,
            weather_condition="Partly Cloudy",
            confidence_score=0.85,
            generated_at=datetime.now()
        )
        assert forecast.confidence_score == 0.85
        assert forecast.precipitation_probability == 0.3

    def test_invalid_confidence_score_too_high(self):
        """Test that confidence score > 1 is rejected"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        with pytest.raises(ValidationError):
            Forecast(
                location=location,
                forecast_date=date.today(),
                predicted_temperature_high=18.0,
                predicted_temperature_low=12.0,
                precipitation_probability=0.3,
                weather_condition="Partly Cloudy",
                confidence_score=1.1,
                generated_at=datetime.now()
            )

    def test_invalid_high_temp_less_than_low(self):
        """Test that high temp < low temp is rejected"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        with pytest.raises(ValidationError):
            Forecast(
                location=location,
                forecast_date=date.today(),
                predicted_temperature_high=10.0,
                predicted_temperature_low=15.0,
                precipitation_probability=0.3,
                weather_condition="Partly Cloudy",
                confidence_score=0.85,
                generated_at=datetime.now()
            )


class TestAccuracyMetrics:
    """Tests for AccuracyMetrics model"""

    def test_valid_accuracy_metrics(self):
        """Test creating valid accuracy metrics"""
        location = Location(
            latitude=40.7128,
            longitude=-74.0060,
            city='New York',
            country='USA'
        )
        
        metrics = AccuracyMetrics(
            location=location,
            overall_accuracy=0.82,
            temperature_mae=2.5,
            temperature_rmse=3.2,
            precipitation_accuracy=0.78,
            condition_accuracy=0.85,
            total_predictions=50,
            evaluation_period_days=7
        )
        assert metrics.overall_accuracy == 0.82
        assert metrics.temperature_mae == 2.5
        assert metrics.condition_accuracy == 0.85
        assert metrics.total_predictions == 50

    def test_invalid_overall_accuracy_too_high(self):
        """Test that overall accuracy > 1 is rejected"""
        with pytest.raises(ValidationError):
            AccuracyMetrics(
                date=date.today(),
                temperature_mae=2.5,
                temperature_rmse=3.2,
                precipitation_accuracy=0.78,
                overall_accuracy=1.1
            )

    def test_invalid_negative_mae(self):
        """Test that negative MAE is rejected"""
        with pytest.raises(ValidationError):
            AccuracyMetrics(
                date=date.today(),
                temperature_mae=-2.5,
                temperature_rmse=3.2,
                precipitation_accuracy=0.78,
                overall_accuracy=0.82
            )


class TestWeatherWarning:
    """Tests for WeatherWarning model"""

    def test_valid_warning(self):
        """Test creating a valid weather warning"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=6)
        
        warning = WeatherWarning(
            warning_id="WARN-2024-01-15-001",
            location=location,
            warning_type="storm",
            severity="high",
            title="Severe Thunderstorm Warning",
            description="Severe thunderstorms expected",
            safety_recommendations=["Stay indoors", "Avoid driving"],
            start_time=start_time,
            end_time=end_time,
            issued_at=datetime.now()
        )
        assert warning.severity == "high"
        assert warning.warning_type == "storm"

    def test_invalid_severity(self):
        """Test that invalid severity is rejected"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=6)
        
        with pytest.raises(ValidationError):
            WeatherWarning(
                warning_id="WARN-2024-01-15-001",
                location=location,
                warning_type="storm",
                severity="critical",  # Invalid
                title="Severe Thunderstorm Warning",
                description="Severe thunderstorms expected",
                safety_recommendations=["Stay indoors"],
                start_time=start_time,
                end_time=end_time,
                issued_at=datetime.now()
            )

    def test_invalid_warning_type(self):
        """Test that invalid warning type is rejected"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=6)
        
        with pytest.raises(ValidationError):
            WeatherWarning(
                warning_id="WARN-2024-01-15-001",
                location=location,
                warning_type="earthquake",  # Invalid
                severity="high",
                title="Severe Thunderstorm Warning",
                description="Severe thunderstorms expected",
                safety_recommendations=["Stay indoors"],
                start_time=start_time,
                end_time=end_time,
                issued_at=datetime.now()
            )

    def test_invalid_end_time_before_start(self):
        """Test that end time before start time is rejected"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        start_time = datetime.now()
        end_time = start_time - timedelta(hours=1)  # Before start
        
        with pytest.raises(ValidationError):
            WeatherWarning(
                warning_id="WARN-2024-01-15-001",
                location=location,
                warning_type="storm",
                severity="high",
                title="Severe Thunderstorm Warning",
                description="Severe thunderstorms expected",
                safety_recommendations=["Stay indoors"],
                start_time=start_time,
                end_time=end_time,
                issued_at=datetime.now()
            )


class TestUserLocation:
    """Tests for UserLocation model"""

    def test_valid_user_location(self):
        """Test creating a valid user location"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        user_loc = UserLocation(
            user_id="user123",
            location=location,
            is_favorite=True,
            added_at=datetime.now()
        )
        assert user_loc.user_id == "user123"
        assert user_loc.is_favorite is True

    def test_empty_user_id(self):
        """Test that empty user ID is rejected"""
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )
        with pytest.raises(ValidationError):
            UserLocation(
                user_id="",
                location=location,
                is_favorite=True,
                added_at=datetime.now()
            )


class TestChartData:
    """Tests for ChartData model"""

    def test_valid_chart_data(self):
        """Test creating valid chart data"""
        chart = ChartData(
            labels=["2024-01-15", "2024-01-16", "2024-01-17"],
            datasets=[
                {
                    "label": "Temperature",
                    "data": [15.5, 16.2, 14.8],
                    "color": "#0066CC"
                }
            ]
        )
        assert len(chart.labels) == 3
        assert len(chart.datasets) == 1

    def test_empty_labels(self):
        """Test that empty labels are allowed"""
        chart = ChartData(
            labels=[],
            datasets=[]
        )
        assert len(chart.labels) == 0
