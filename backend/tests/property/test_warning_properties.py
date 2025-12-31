"""
Property-based tests for Weather Warning System.

Feature: weather-prediction-system
Properties: 29, 30
"""

from datetime import datetime, timedelta, date
from hypothesis import given, strategies as st, settings
import pytest
from app.models import Location, WeatherData, Forecast, WeatherWarning
from app.services.warning_system import WarningGenerator, SeverityLevel, WarningType


# Custom strategies for generating test data
@st.composite
def location_strategy(draw):
    """Generate valid Location objects."""
    return Location(
        latitude=draw(st.floats(min_value=-90, max_value=90)),
        longitude=draw(st.floats(min_value=-180, max_value=180)),
        city=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))),
        country=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))))
    )


@st.composite
def weather_data_strategy(draw, location=None):
    """Generate valid WeatherData objects."""
    if location is None:
        location = draw(location_strategy())
    
    return WeatherData(
        location=location,
        timestamp=draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime.now())),
        temperature=draw(st.floats(min_value=-50, max_value=60)),
        humidity=draw(st.floats(min_value=0, max_value=100)),
        pressure=draw(st.floats(min_value=900, max_value=1100)),
        wind_speed=draw(st.floats(min_value=0, max_value=50)),
        wind_direction=draw(st.floats(min_value=0, max_value=360)),
        precipitation=draw(st.floats(min_value=0, max_value=200)),
        cloud_cover=draw(st.floats(min_value=0, max_value=100)),
        weather_condition=draw(st.sampled_from(['Clear', 'Rainy', 'Cloudy', 'Snowy', 'Stormy']))
    )


@st.composite
def forecast_strategy(draw, location=None):
    """Generate valid Forecast objects."""
    if location is None:
        location = draw(location_strategy())
    
    # Generate low temperature first, then high temperature >= low temperature
    temp_low = draw(st.floats(min_value=-50, max_value=50))
    temp_high = draw(st.floats(min_value=temp_low, max_value=max(temp_low + 20, 60)))
    
    return Forecast(
        location=location,
        forecast_date=draw(st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31))),
        predicted_temperature_high=temp_high,
        predicted_temperature_low=temp_low,
        precipitation_probability=draw(st.floats(min_value=0, max_value=1)),
        weather_condition=draw(st.sampled_from(['Clear', 'Rainy', 'Cloudy', 'Snowy', 'Stormy'])),
        confidence_score=draw(st.floats(min_value=0, max_value=1)),
        generated_at=draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime.now()))
    )


# Feature: weather-prediction-system, Property 29: Weather Warning Generation
def test_warning_generation_for_severe_conditions():
    """For any forecast with severe weather conditions, the Warning_Generator should create appropriate weather warnings with correct severity levels."""
    generator = WarningGenerator()
    location = Location(latitude=40.7128, longitude=-74.0060, city='New York', country='USA')
    
    # Test severe heat conditions
    severe_heat_conditions = WeatherData(
        location=location,
        timestamp=datetime.now(),
        temperature=47.0,  # Severe heat
        humidity=60.0,
        pressure=1013.0,
        wind_speed=5.0,
        wind_direction=180.0,
        precipitation=0.0,
        cloud_cover=30.0,
        weather_condition='Sunny'
    )
    
    warnings = generator.analyze_current_conditions(severe_heat_conditions)
    
    # Should generate at least one warning
    assert len(warnings) >= 1
    
    # Should have a heat warning with severe severity
    heat_warnings = [w for w in warnings if w.warning_type == WarningType.HEAT.value]
    assert len(heat_warnings) >= 1
    assert heat_warnings[0].severity == SeverityLevel.SEVERE.value
    
    # Warning should have proper structure
    warning = heat_warnings[0]
    assert warning.warning_id is not None
    assert len(warning.warning_id) > 0
    assert warning.location == location
    assert len(warning.title) > 0
    assert len(warning.description) > 0
    assert len(warning.safety_recommendations) > 0
    assert warning.start_time <= warning.end_time
    assert warning.issued_at is not None


# Feature: weather-prediction-system, Property 29: Weather Warning Generation
def test_warning_generation_for_severe_wind():
    """For any conditions with severe wind, the Warning_Generator should create wind warnings with correct severity."""
    generator = WarningGenerator()
    location = Location(latitude=51.5074, longitude=-0.1278, city='London', country='UK')
    
    # Test severe wind conditions
    severe_wind_conditions = WeatherData(
        location=location,
        timestamp=datetime.now(),
        temperature=20.0,
        humidity=60.0,
        pressure=995.0,
        wind_speed=28.0,  # Severe wind
        wind_direction=270.0,
        precipitation=0.0,
        cloud_cover=70.0,
        weather_condition='Windy'
    )
    
    warnings = generator.analyze_current_conditions(severe_wind_conditions)
    
    # Should generate at least one warning
    assert len(warnings) >= 1
    
    # Should have a wind warning with severe severity
    wind_warnings = [w for w in warnings if w.warning_type == WarningType.WIND.value]
    assert len(wind_warnings) >= 1
    assert wind_warnings[0].severity == SeverityLevel.SEVERE.value


# Feature: weather-prediction-system, Property 29: Weather Warning Generation
def test_warning_generation_for_severe_precipitation():
    """For any conditions with severe precipitation, the Warning_Generator should create flood warnings."""
    generator = WarningGenerator()
    location = Location(latitude=35.6762, longitude=139.6503, city='Tokyo', country='Japan')
    
    # Test severe precipitation conditions
    severe_precip_conditions = WeatherData(
        location=location,
        timestamp=datetime.now(),
        temperature=22.0,
        humidity=90.0,
        pressure=1005.0,
        wind_speed=8.0,
        wind_direction=180.0,
        precipitation=120.0,  # Severe precipitation
        cloud_cover=95.0,
        weather_condition='Stormy'
    )
    
    warnings = generator.analyze_current_conditions(severe_precip_conditions)
    
    # Should generate at least one warning
    assert len(warnings) >= 1
    
    # Should have a flood warning with severe severity
    flood_warnings = [w for w in warnings if w.warning_type == WarningType.FLOOD.value]
    assert len(flood_warnings) >= 1
    assert flood_warnings[0].severity == SeverityLevel.SEVERE.value


# Feature: weather-prediction-system, Property 29: Weather Warning Generation
@given(st.floats(min_value=30, max_value=60))
@settings(max_examples=10, deadline=None)
def test_heat_warning_generation_property(temperature):
    """For any temperature above heat thresholds, appropriate heat warnings should be generated."""
    generator = WarningGenerator()
    location = Location(latitude=37.7749, longitude=-122.4194, city='San Francisco', country='USA')
    
    conditions = WeatherData(
        location=location,
        timestamp=datetime.now(),
        temperature=temperature,
        humidity=60.0,
        pressure=1013.0,
        wind_speed=5.0,
        wind_direction=180.0,
        precipitation=0.0,
        cloud_cover=30.0,
        weather_condition='Sunny'
    )
    
    warnings = generator.analyze_current_conditions(conditions)
    
    # Should generate heat warnings for temperatures above threshold
    heat_warnings = [w for w in warnings if w.warning_type == WarningType.HEAT.value]
    assert len(heat_warnings) >= 1
    
    # Verify warning properties
    warning = heat_warnings[0]
    assert warning.severity in [sl.value for sl in SeverityLevel]
    assert "heat" in warning.title.lower()
    assert len(warning.safety_recommendations) > 0


# Feature: weather-prediction-system, Property 29: Weather Warning Generation
@given(st.floats(min_value=10, max_value=50))
@settings(max_examples=10, deadline=None)
def test_wind_warning_generation_property(wind_speed):
    """For any wind speed above thresholds, appropriate wind warnings should be generated."""
    generator = WarningGenerator()
    location = Location(latitude=48.8566, longitude=2.3522, city='Paris', country='France')
    
    conditions = WeatherData(
        location=location,
        timestamp=datetime.now(),
        temperature=20.0,
        humidity=60.0,
        pressure=1013.0,
        wind_speed=wind_speed,
        wind_direction=225.0,
        precipitation=0.0,
        cloud_cover=40.0,
        weather_condition='Windy'
    )
    
    warnings = generator.analyze_current_conditions(conditions)
    
    # Should generate wind warnings for wind speeds above threshold
    wind_warnings = [w for w in warnings if w.warning_type == WarningType.WIND.value]
    assert len(wind_warnings) >= 1
    
    # Verify warning properties
    warning = wind_warnings[0]
    assert warning.severity in [sl.value for sl in SeverityLevel]
    assert "wind" in warning.title.lower()
    assert len(warning.safety_recommendations) > 0


# Feature: weather-prediction-system, Property 30: Warning Safety Recommendations
def test_heat_warning_safety_recommendations():
    """For any heat warning generated, it should include at least one safety recommendation appropriate to the warning type."""
    generator = WarningGenerator()
    location = Location(latitude=33.4484, longitude=-112.0740, city='Phoenix', country='USA')
    
    # Generate heat warning
    hot_conditions = WeatherData(
        location=location,
        timestamp=datetime.now(),
        temperature=42.0,  # High heat
        humidity=30.0,
        pressure=1013.0,
        wind_speed=5.0,
        wind_direction=180.0,
        precipitation=0.0,
        cloud_cover=10.0,
        weather_condition='Sunny'
    )
    
    warnings = generator.analyze_current_conditions(hot_conditions)
    heat_warnings = [w for w in warnings if w.warning_type == WarningType.HEAT.value]
    
    assert len(heat_warnings) >= 1
    warning = heat_warnings[0]
    
    # Should have safety recommendations
    assert len(warning.safety_recommendations) > 0
    
    # Recommendations should be appropriate for heat warnings
    recommendations_text = ' '.join(warning.safety_recommendations).lower()
    heat_keywords = ['water', 'hydrated', 'air-conditioned', 'indoors', 'shade', 'cool']
    assert any(keyword in recommendations_text for keyword in heat_keywords)


# Feature: weather-prediction-system, Property 30: Warning Safety Recommendations
def test_wind_warning_safety_recommendations():
    """For any wind warning generated, it should include appropriate safety recommendations."""
    generator = WarningGenerator()
    location = Location(latitude=41.8781, longitude=-87.6298, city='Chicago', country='USA')
    
    # Generate wind warning
    windy_conditions = WeatherData(
        location=location,
        timestamp=datetime.now(),
        temperature=15.0,
        humidity=60.0,
        pressure=1005.0,
        wind_speed=22.0,  # High wind
        wind_direction=270.0,
        precipitation=0.0,
        cloud_cover=60.0,
        weather_condition='Windy'
    )
    
    warnings = generator.analyze_current_conditions(windy_conditions)
    wind_warnings = [w for w in warnings if w.warning_type == WarningType.WIND.value]
    
    assert len(wind_warnings) >= 1
    warning = wind_warnings[0]
    
    # Should have safety recommendations
    assert len(warning.safety_recommendations) > 0
    
    # Recommendations should be appropriate for wind warnings
    recommendations_text = ' '.join(warning.safety_recommendations).lower()
    wind_keywords = ['secure', 'indoors', 'travel', 'windows', 'objects', 'trees']
    assert any(keyword in recommendations_text for keyword in wind_keywords)


# Feature: weather-prediction-system, Property 30: Warning Safety Recommendations
def test_flood_warning_safety_recommendations():
    """For any flood warning generated, it should include appropriate safety recommendations."""
    generator = WarningGenerator()
    location = Location(latitude=29.7604, longitude=-95.3698, city='Houston', country='USA')
    
    # Generate flood warning
    flood_conditions = WeatherData(
        location=location,
        timestamp=datetime.now(),
        temperature=25.0,
        humidity=95.0,
        pressure=1000.0,
        wind_speed=10.0,
        wind_direction=180.0,
        precipitation=75.0,  # High precipitation
        cloud_cover=100.0,
        weather_condition='Stormy'
    )
    
    warnings = generator.analyze_current_conditions(flood_conditions)
    flood_warnings = [w for w in warnings if w.warning_type == WarningType.FLOOD.value]
    
    assert len(flood_warnings) >= 1
    warning = flood_warnings[0]
    
    # Should have safety recommendations
    assert len(warning.safety_recommendations) > 0
    
    # Recommendations should be appropriate for flood warnings
    recommendations_text = ' '.join(warning.safety_recommendations).lower()
    flood_keywords = ['evacuate', 'higher ground', 'flooded', 'roads', 'water', 'emergency']
    assert any(keyword in recommendations_text for keyword in flood_keywords)


# Feature: weather-prediction-system, Property 30: Warning Safety Recommendations
@given(weather_data_strategy())
@settings(max_examples=5, deadline=None)
def test_all_warnings_have_recommendations_property(conditions):
    """For any weather conditions that generate warnings, all warnings should have safety recommendations."""
    generator = WarningGenerator()
    
    warnings = generator.analyze_current_conditions(conditions)
    
    # All generated warnings should have safety recommendations
    for warning in warnings:
        assert len(warning.safety_recommendations) > 0
        assert all(isinstance(rec, str) and len(rec) > 0 for rec in warning.safety_recommendations)


# Feature: weather-prediction-system, Property 29: Weather Warning Generation
@given(forecast_strategy())
@settings(max_examples=5, deadline=None)
def test_forecast_warning_generation_property(forecast):
    """For any forecast, warning generation should produce valid warnings when conditions warrant them."""
    generator = WarningGenerator()
    
    warnings = generator.analyze_forecast(forecast)
    
    # All generated warnings should be valid
    for warning in warnings:
        assert warning.warning_id is not None
        assert len(warning.warning_id) > 0
        assert warning.location == forecast.location
        assert warning.warning_type in [wt.value for wt in WarningType]
        assert warning.severity in [sl.value for sl in SeverityLevel]
        assert len(warning.title) > 0
        assert len(warning.description) > 0
        assert len(warning.safety_recommendations) > 0
        assert warning.start_time <= warning.end_time
        assert warning.issued_at is not None


# Feature: weather-prediction-system, Property 29: Weather Warning Generation
def test_no_warnings_for_normal_conditions():
    """For normal weather conditions, no warnings should be generated."""
    generator = WarningGenerator()
    location = Location(latitude=40.7128, longitude=-74.0060, city='New York', country='USA')
    
    # Normal conditions - no extreme values
    normal_conditions = WeatherData(
        location=location,
        timestamp=datetime.now(),
        temperature=22.0,  # Normal temperature
        humidity=60.0,
        pressure=1013.0,
        wind_speed=5.0,    # Normal wind
        wind_direction=180.0,
        precipitation=2.0,  # Light precipitation
        cloud_cover=40.0,
        weather_condition='Partly Cloudy'
    )
    
    warnings = generator.analyze_current_conditions(normal_conditions)
    
    # Should not generate any warnings for normal conditions
    assert len(warnings) == 0


# Feature: weather-prediction-system, Property 29: Weather Warning Generation
def test_warning_severity_consistency():
    """For any conditions, warning severity should be consistent with the severity of the conditions."""
    generator = WarningGenerator()
    location = Location(latitude=25.7617, longitude=-80.1918, city='Miami', country='USA')
    
    # Test different severity levels
    test_cases = [
        (32.0, SeverityLevel.LOW),     # Low heat
        (37.0, SeverityLevel.MODERATE), # Moderate heat
        (42.0, SeverityLevel.HIGH),     # High heat
        (47.0, SeverityLevel.SEVERE)    # Severe heat
    ]
    
    for temperature, expected_severity in test_cases:
        conditions = WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=temperature,
            humidity=60.0,
            pressure=1013.0,
            wind_speed=5.0,
            wind_direction=180.0,
            precipitation=0.0,
            cloud_cover=30.0,
            weather_condition='Sunny'
        )
        
        warnings = generator.analyze_current_conditions(conditions)
        heat_warnings = [w for w in warnings if w.warning_type == WarningType.HEAT.value]
        
        if len(heat_warnings) > 0:
            assert heat_warnings[0].severity == expected_severity.value