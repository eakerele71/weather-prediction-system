"""Property-based tests for data validation"""
from hypothesis import given, strategies as st
from datetime import datetime, date, timedelta
from pydantic import ValidationError
from app.models import (
    Location, WeatherData, Forecast, AccuracyMetrics,
    WeatherWarning, UserLocation
)


# Custom strategies for generating valid data

def location_strategy():
    """Strategy for generating valid Location objects"""
    return st.builds(
        Location,
        latitude=st.floats(min_value=-90, max_value=90),
        longitude=st.floats(min_value=-180, max_value=180),
        city=st.text(min_size=1, max_size=255),
        country=st.text(min_size=1, max_size=100)
    )


def weather_data_strategy():
    """Strategy for generating valid WeatherData objects"""
    return st.builds(
        WeatherData,
        location=location_strategy(),
        timestamp=st.datetimes(),
        temperature=st.floats(min_value=-100, max_value=60),
        humidity=st.floats(min_value=0, max_value=100),
        pressure=st.floats(min_value=1, max_value=1100),
        wind_speed=st.floats(min_value=0, max_value=150),
        wind_direction=st.floats(min_value=0, max_value=360),
        precipitation=st.floats(min_value=0, max_value=1000),
        cloud_cover=st.floats(min_value=0, max_value=100),
        weather_condition=st.text(min_size=1, max_size=100)
    )


def forecast_strategy():
    """Strategy for generating valid Forecast objects"""
    # Generate high and low temperatures separately to ensure high >= low
    temps = st.tuples(
        st.floats(min_value=-100, max_value=60),
        st.floats(min_value=-100, max_value=60)
    ).map(lambda t: (max(t[0], t[1]), min(t[0], t[1])))
    
    return st.builds(
        Forecast,
        location=location_strategy(),
        forecast_date=st.dates(),
        predicted_temperature_high=st.just(0),  # Will be replaced
        predicted_temperature_low=st.just(0),   # Will be replaced
        precipitation_probability=st.floats(min_value=0, max_value=1),
        weather_condition=st.text(min_size=1, max_size=100),
        confidence_score=st.floats(min_value=0, max_value=1),
        generated_at=st.datetimes()
    ).flatmap(lambda f: temps.map(lambda t: Forecast(
        location=f.location,
        forecast_date=f.forecast_date,
        predicted_temperature_high=t[0],
        predicted_temperature_low=t[1],
        precipitation_probability=f.precipitation_probability,
        weather_condition=f.weather_condition,
        confidence_score=f.confidence_score,
        generated_at=f.generated_at
    )))


# Feature: weather-prediction-system, Property 1: Data Collection Validation
@given(weather_data_strategy())
def test_valid_weather_data_passes_validation(weather_data):
    """For any valid weather data, validation should pass and all fields should be preserved"""
    # Verify all fields are present and correct
    assert weather_data.location is not None
    assert weather_data.timestamp is not None
    assert -100 <= weather_data.temperature <= 60
    assert 0 <= weather_data.humidity <= 100
    assert weather_data.pressure > 0
    assert 0 <= weather_data.wind_speed <= 150
    assert 0 <= weather_data.wind_direction <= 360
    assert weather_data.precipitation >= 0
    assert 0 <= weather_data.cloud_cover <= 100
    assert len(weather_data.weather_condition) > 0


@given(st.floats(min_value=61, max_value=200))
def test_invalid_temperature_too_high_rejected(temp):
    """For any temperature > 60°C, validation should fail"""
    location = Location(
        latitude=0,
        longitude=0,
        city="Test",
        country="Test"
    )
    try:
        WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=temp,
            humidity=50,
            pressure=1013,
            wind_speed=5,
            wind_direction=180,
            precipitation=0,
            cloud_cover=50,
            weather_condition="Hot"
        )
        # If we get here, the validation failed to reject invalid data
        assert False, f"Temperature {temp} should have been rejected"
    except ValidationError:
        # Expected behavior
        pass


@given(st.floats(max_value=-101, min_value=-300))
def test_invalid_temperature_too_low_rejected(temp):
    """For any temperature < -100°C, validation should fail"""
    location = Location(
        latitude=0,
        longitude=0,
        city="Test",
        country="Test"
    )
    try:
        WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=temp,
            humidity=50,
            pressure=1013,
            wind_speed=5,
            wind_direction=180,
            precipitation=0,
            cloud_cover=50,
            weather_condition="Cold"
        )
        # If we get here, the validation failed to reject invalid data
        assert False, f"Temperature {temp} should have been rejected"
    except ValidationError:
        # Expected behavior
        pass


@given(st.floats(min_value=101, max_value=200))
def test_invalid_humidity_too_high_rejected(humidity):
    """For any humidity > 100%, validation should fail"""
    location = Location(
        latitude=0,
        longitude=0,
        city="Test",
        country="Test"
    )
    try:
        WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=15,
            humidity=humidity,
            pressure=1013,
            wind_speed=5,
            wind_direction=180,
            precipitation=0,
            cloud_cover=50,
            weather_condition="Humid"
        )
        # If we get here, the validation failed to reject invalid data
        assert False, f"Humidity {humidity} should have been rejected"
    except ValidationError:
        # Expected behavior
        pass


@given(st.floats(min_value=151, max_value=300))
def test_invalid_wind_speed_too_high_rejected(wind_speed):
    """For any wind speed > 150 m/s, validation should fail"""
    location = Location(
        latitude=0,
        longitude=0,
        city="Test",
        country="Test"
    )
    try:
        WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=15,
            humidity=50,
            pressure=1013,
            wind_speed=wind_speed,
            wind_direction=180,
            precipitation=0,
            cloud_cover=50,
            weather_condition="Windy"
        )
        # If we get here, the validation failed to reject invalid data
        assert False, f"Wind speed {wind_speed} should have been rejected"
    except ValidationError:
        # Expected behavior
        pass


@given(forecast_strategy())
def test_valid_forecast_passes_validation(forecast):
    """For any valid forecast, validation should pass and all fields should be preserved"""
    # Verify all fields are present and correct
    assert forecast.location is not None
    assert forecast.forecast_date is not None
    assert forecast.predicted_temperature_high >= forecast.predicted_temperature_low
    assert 0 <= forecast.precipitation_probability <= 1
    assert 0 <= forecast.confidence_score <= 1
    assert len(forecast.weather_condition) > 0


@given(st.floats(min_value=1.1, max_value=2.0))
def test_invalid_confidence_score_too_high_rejected(confidence):
    """For any confidence score > 1, validation should fail"""
    location = Location(
        latitude=0,
        longitude=0,
        city="Test",
        country="Test"
    )
    try:
        Forecast(
            location=location,
            forecast_date=date.today(),
            predicted_temperature_high=20,
            predicted_temperature_low=10,
            precipitation_probability=0.5,
            weather_condition="Sunny",
            confidence_score=confidence,
            generated_at=datetime.now()
        )
        # If we get here, the validation failed to reject invalid data
        assert False, f"Confidence score {confidence} should have been rejected"
    except ValidationError:
        # Expected behavior
        pass


@given(st.builds(
    AccuracyMetrics,
    location=st.one_of(st.none(), st.builds(
        Location,
        latitude=st.floats(min_value=-90, max_value=90),
        longitude=st.floats(min_value=-180, max_value=180),
        city=st.text(min_size=1, max_size=50),
        country=st.text(min_size=1, max_size=50)
    )),
    overall_accuracy=st.floats(min_value=0, max_value=1),
    temperature_mae=st.floats(min_value=0, max_value=100),
    temperature_rmse=st.floats(min_value=0, max_value=100),
    precipitation_accuracy=st.floats(min_value=0, max_value=1),
    condition_accuracy=st.floats(min_value=0, max_value=1),
    total_predictions=st.integers(min_value=0, max_value=1000),
    evaluation_period_days=st.integers(min_value=1, max_value=365)
))
def test_valid_accuracy_metrics_passes_validation(metrics):
    """For any valid accuracy metrics, validation should pass"""
    assert metrics.calculated_at is not None
    assert metrics.temperature_mae >= 0
    assert metrics.temperature_rmse >= 0
    assert 0 <= metrics.precipitation_accuracy <= 1
    assert 0 <= metrics.overall_accuracy <= 1
    assert 0 <= metrics.condition_accuracy <= 1
    assert metrics.total_predictions >= 0
    assert metrics.evaluation_period_days >= 1


@given(st.floats(min_value=1.1, max_value=2.0))
def test_invalid_overall_accuracy_too_high_rejected(accuracy):
    """For any overall accuracy > 1, validation should fail"""
    try:
        AccuracyMetrics(
            date=date.today(),
            temperature_mae=2.5,
            temperature_rmse=3.2,
            precipitation_accuracy=0.78,
            overall_accuracy=accuracy
        )
        # If we get here, the validation failed to reject invalid data
        assert False, f"Overall accuracy {accuracy} should have been rejected"
    except ValidationError:
        # Expected behavior
        pass


@given(st.datetimes().flatmap(lambda start: st.builds(
    WeatherWarning,
    warning_id=st.text(min_size=1, max_size=100),
    location=location_strategy(),
    warning_type=st.sampled_from(['storm', 'heat', 'flood', 'wind', 'air_quality']),
    severity=st.sampled_from(['low', 'moderate', 'high', 'severe']),
    title=st.text(min_size=1, max_size=255),
    description=st.text(min_size=1),
    safety_recommendations=st.lists(st.text(min_size=1), min_size=1),
    start_time=st.just(start),
    end_time=st.datetimes(min_value=start + timedelta(seconds=1)),
    issued_at=st.datetimes()
)))
def test_valid_warning_passes_validation(warning):
    """For any valid weather warning, validation should pass"""
    assert warning.warning_id is not None
    assert warning.location is not None
    assert warning.warning_type in ['storm', 'heat', 'flood', 'wind', 'air_quality']
    assert warning.severity in ['low', 'moderate', 'high', 'severe']
    assert len(warning.title) > 0
    assert len(warning.description) > 0
    assert len(warning.safety_recommendations) > 0
    assert warning.end_time > warning.start_time


@given(st.text(min_size=1))
def test_invalid_warning_type_rejected(invalid_type):
    """For any invalid warning type, validation should fail"""
    valid_types = {'storm', 'heat', 'flood', 'wind', 'air_quality'}
    if invalid_type not in valid_types:
        location = Location(
            latitude=0,
            longitude=0,
            city="Test",
            country="Test"
        )
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        try:
            WeatherWarning(
                warning_id="TEST-001",
                location=location,
                warning_type=invalid_type,
                severity="high",
                title="Test Warning",
                description="Test description",
                safety_recommendations=["Stay safe"],
                start_time=start_time,
                end_time=end_time,
                issued_at=datetime.now()
            )
            # If we get here, the validation failed to reject invalid data
            assert False, f"Warning type {invalid_type} should have been rejected"
        except ValidationError:
            # Expected behavior
            pass
