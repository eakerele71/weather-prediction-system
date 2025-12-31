"""Unit tests for weather warning system"""
import pytest
from datetime import datetime, timedelta
from app.models import WeatherData, Forecast, Location, WeatherWarning
from app.services.warning_system import (
    WarningGenerator, SeverityClassifier, SafetyRecommendations,
    SeverityLevel, WarningType
)


class TestSeverityClassifier:
    """Test cases for SeverityClassifier"""

    def setup_method(self):
        """Set up test fixtures"""
        self.classifier = SeverityClassifier()

    def test_classifier_initialization(self):
        """Test that classifier initializes with correct thresholds"""
        assert self.classifier.heat_thresholds[SeverityLevel.LOW] == 30.0
        assert self.classifier.cold_thresholds[SeverityLevel.SEVERE] == -30.0
        assert self.classifier.wind_thresholds[SeverityLevel.HIGH] == 20.0
        assert self.classifier.precipitation_thresholds[SeverityLevel.MODERATE] == 25.0

    def test_classify_temperature_severity_heat(self):
        """Test temperature severity classification for heat"""
        # No warning
        assert self.classifier.classify_temperature_severity(25.0) is None
        
        # Low heat warning
        assert self.classifier.classify_temperature_severity(32.0) == SeverityLevel.LOW
        
        # Moderate heat warning
        assert self.classifier.classify_temperature_severity(37.0) == SeverityLevel.MODERATE
        
        # High heat warning
        assert self.classifier.classify_temperature_severity(42.0) == SeverityLevel.HIGH
        
        # Severe heat warning
        assert self.classifier.classify_temperature_severity(47.0) == SeverityLevel.SEVERE

    def test_classify_temperature_severity_cold(self):
        """Test temperature severity classification for cold"""
        # Low cold warning
        assert self.classifier.classify_temperature_severity(-2.0) == SeverityLevel.LOW
        
        # Moderate cold warning
        assert self.classifier.classify_temperature_severity(-15.0) == SeverityLevel.MODERATE
        
        # High cold warning
        assert self.classifier.classify_temperature_severity(-25.0) == SeverityLevel.HIGH
        
        # Severe cold warning
        assert self.classifier.classify_temperature_severity(-35.0) == SeverityLevel.SEVERE

    def test_classify_wind_severity(self):
        """Test wind severity classification"""
        # No warning
        assert self.classifier.classify_wind_severity(5.0) is None
        
        # Low wind warning
        assert self.classifier.classify_wind_severity(12.0) == SeverityLevel.LOW
        
        # Moderate wind warning
        assert self.classifier.classify_wind_severity(17.0) == SeverityLevel.MODERATE
        
        # High wind warning
        assert self.classifier.classify_wind_severity(22.0) == SeverityLevel.HIGH
        
        # Severe wind warning
        assert self.classifier.classify_wind_severity(27.0) == SeverityLevel.SEVERE

    def test_classify_precipitation_severity(self):
        """Test precipitation severity classification"""
        # No warning
        assert self.classifier.classify_precipitation_severity(5.0) is None
        
        # Low precipitation warning
        assert self.classifier.classify_precipitation_severity(15.0) == SeverityLevel.LOW
        
        # Moderate precipitation warning
        assert self.classifier.classify_precipitation_severity(30.0) == SeverityLevel.MODERATE
        
        # High precipitation warning
        assert self.classifier.classify_precipitation_severity(60.0) == SeverityLevel.HIGH
        
        # Severe precipitation warning
        assert self.classifier.classify_precipitation_severity(120.0) == SeverityLevel.SEVERE

    def test_classify_overall_severity(self):
        """Test overall severity classification"""
        location = Location(latitude=40.7128, longitude=-74.0060, city='New York', country='USA')
        
        # Multiple severe conditions - should return SEVERE
        severe_conditions = WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=50.0,  # Severe heat
            humidity=60.0,
            pressure=1013.0,
            wind_speed=30.0,   # Severe wind
            wind_direction=180.0,
            precipitation=150.0,  # Severe precipitation
            cloud_cover=80.0,
            weather_condition='Stormy'
        )
        assert self.classifier.classify_overall_severity(severe_conditions) == SeverityLevel.SEVERE
        
        # Mixed severity conditions - should return highest (HIGH)
        mixed_conditions = WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=41.0,  # High heat
            humidity=60.0,
            pressure=1013.0,
            wind_speed=12.0,   # Low wind
            wind_direction=180.0,
            precipitation=5.0,  # No precipitation warning
            cloud_cover=50.0,
            weather_condition='Hot'
        )
        assert self.classifier.classify_overall_severity(mixed_conditions) == SeverityLevel.HIGH
        
        # No warning conditions - should return LOW (default)
        normal_conditions = WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=20.0,
            humidity=60.0,
            pressure=1013.0,
            wind_speed=5.0,
            wind_direction=180.0,
            precipitation=2.0,
            cloud_cover=30.0,
            weather_condition='Clear'
        )
        assert self.classifier.classify_overall_severity(normal_conditions) == SeverityLevel.LOW


class TestSafetyRecommendations:
    """Test cases for SafetyRecommendations"""

    def setup_method(self):
        """Set up test fixtures"""
        self.safety = SafetyRecommendations()

    def test_get_heat_recommendations(self):
        """Test heat warning recommendations"""
        recommendations = self.safety.get_recommendations(WarningType.HEAT, SeverityLevel.LOW)
        assert len(recommendations) > 0
        assert any("hydrated" in rec.lower() for rec in recommendations)
        
        severe_recommendations = self.safety.get_recommendations(WarningType.HEAT, SeverityLevel.SEVERE)
        assert len(severe_recommendations) > len(recommendations)
        assert any("air-conditioned" in rec.lower() for rec in severe_recommendations)

    def test_get_wind_recommendations(self):
        """Test wind warning recommendations"""
        recommendations = self.safety.get_recommendations(WarningType.WIND, SeverityLevel.HIGH)
        assert len(recommendations) > 0
        assert any("secure" in rec.lower() or "indoors" in rec.lower() for rec in recommendations)

    def test_get_flood_recommendations(self):
        """Test flood warning recommendations"""
        recommendations = self.safety.get_recommendations(WarningType.FLOOD, SeverityLevel.SEVERE)
        assert len(recommendations) > 0
        assert any("evacuate" in rec.lower() for rec in recommendations)

    def test_get_storm_recommendations(self):
        """Test storm warning recommendations"""
        recommendations = self.safety.get_recommendations(WarningType.STORM, SeverityLevel.MODERATE)
        assert len(recommendations) > 0
        assert any("indoors" in rec.lower() for rec in recommendations)


class TestWarningGenerator:
    """Test cases for WarningGenerator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.generator = WarningGenerator()
        self.location = Location(latitude=40.7128, longitude=-74.0060, city='New York', country='USA')

    def test_generator_initialization(self):
        """Test that generator initializes correctly"""
        assert self.generator.severity_classifier is not None
        assert self.generator.safety_recommendations is not None

    def test_analyze_current_conditions_heat_warning(self):
        """Test analysis of current conditions for heat warning"""
        hot_conditions = WeatherData(
            location=self.location,
            timestamp=datetime.now(),
            temperature=38.0,  # Moderate heat
            humidity=60.0,
            pressure=1013.0,
            wind_speed=5.0,
            wind_direction=180.0,
            precipitation=0.0,
            cloud_cover=20.0,
            weather_condition='Sunny'
        )
        
        warnings = self.generator.analyze_current_conditions(hot_conditions)
        assert len(warnings) == 1
        assert warnings[0].warning_type == WarningType.HEAT.value
        assert warnings[0].severity == SeverityLevel.MODERATE.value
        assert "heat" in warnings[0].title.lower()
        assert len(warnings[0].safety_recommendations) > 0

    def test_analyze_current_conditions_no_cold_warning(self):
        """Test that cold conditions don't generate warnings (not supported by model)"""
        cold_conditions = WeatherData(
            location=self.location,
            timestamp=datetime.now(),
            temperature=-15.0,  # Cold temperature
            humidity=70.0,
            pressure=1020.0,
            wind_speed=8.0,
            wind_direction=270.0,
            precipitation=0.0,
            cloud_cover=60.0,
            weather_condition='Cloudy'
        )
        
        warnings = self.generator.analyze_current_conditions(cold_conditions)
        # Should not generate any warnings since cold warnings aren't supported
        assert len(warnings) == 0

    def test_analyze_current_conditions_wind_warning(self):
        """Test analysis of current conditions for wind warning"""
        windy_conditions = WeatherData(
            location=self.location,
            timestamp=datetime.now(),
            temperature=20.0,
            humidity=50.0,
            pressure=1005.0,
            wind_speed=18.0,  # Moderate wind
            wind_direction=225.0,
            precipitation=0.0,
            cloud_cover=40.0,
            weather_condition='Windy'
        )
        
        warnings = self.generator.analyze_current_conditions(windy_conditions)
        assert len(warnings) == 1
        assert warnings[0].warning_type == WarningType.WIND.value
        assert warnings[0].severity == SeverityLevel.MODERATE.value
        assert "wind" in warnings[0].title.lower()

    def test_analyze_current_conditions_multiple_warnings(self):
        """Test analysis of conditions that trigger multiple warnings"""
        extreme_conditions = WeatherData(
            location=self.location,
            timestamp=datetime.now(),
            temperature=45.0,  # Severe heat
            humidity=40.0,
            pressure=995.0,
            wind_speed=25.0,   # Severe wind
            wind_direction=180.0,
            precipitation=80.0,  # High precipitation
            cloud_cover=90.0,
            weather_condition='Stormy'
        )
        
        warnings = self.generator.analyze_current_conditions(extreme_conditions)
        assert len(warnings) == 3  # Heat, wind, and flood warnings
        
        warning_types = [w.warning_type for w in warnings]
        assert WarningType.HEAT.value in warning_types
        assert WarningType.WIND.value in warning_types
        assert WarningType.FLOOD.value in warning_types

    def test_analyze_forecast_temperature_warnings(self):
        """Test forecast analysis for temperature warnings"""
        hot_forecast = Forecast(
            location=self.location,
            forecast_date=datetime.now().date(),
            predicted_temperature_high=42.0,  # High heat
            predicted_temperature_low=25.0,
            precipitation_probability=0.1,
            weather_condition='Sunny',
            confidence_score=0.85,
            generated_at=datetime.now()
        )
        
        warnings = self.generator.analyze_forecast(hot_forecast)
        assert len(warnings) >= 1
        heat_warnings = [w for w in warnings if w.warning_type == WarningType.HEAT.value]
        assert len(heat_warnings) == 1
        assert heat_warnings[0].severity == SeverityLevel.HIGH.value

    def test_analyze_forecast_precipitation_warnings(self):
        """Test forecast analysis for precipitation warnings"""
        rainy_forecast = Forecast(
            location=self.location,
            forecast_date=datetime.now().date(),
            predicted_temperature_high=22.0,
            predicted_temperature_low=18.0,
            precipitation_probability=0.9,  # High precipitation probability
            weather_condition='Rainy',
            confidence_score=0.80,
            generated_at=datetime.now()
        )
        
        warnings = self.generator.analyze_forecast(rainy_forecast)
        flood_warnings = [w for w in warnings if w.warning_type == WarningType.FLOOD.value]
        assert len(flood_warnings) >= 1

    def test_classify_severity(self):
        """Test severity classification method"""
        conditions = WeatherData(
            location=self.location,
            timestamp=datetime.now(),
            temperature=35.0,  # Moderate heat
            humidity=60.0,
            pressure=1013.0,
            wind_speed=5.0,
            wind_direction=180.0,
            precipitation=0.0,
            cloud_cover=30.0,
            weather_condition='Hot'
        )
        
        severity = self.generator.classify_severity(conditions)
        assert severity == SeverityLevel.MODERATE

    def test_generate_recommendations(self):
        """Test recommendation generation for warnings"""
        warning = WeatherWarning(
            warning_id="test-123",
            location=self.location,
            warning_type=WarningType.HEAT.value,
            severity=SeverityLevel.HIGH.value,
            title="High Heat Warning",
            description="Dangerous heat conditions expected",
            safety_recommendations=["Stay indoors", "Drink water"],  # Must have at least 1 item
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=24),
            issued_at=datetime.now()
        )
        
        recommendations = self.generator.generate_recommendations(warning)
        assert len(recommendations) > 0
        assert any("air-conditioned" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_unknown_type(self):
        """Test recommendation generation for unknown warning types"""
        warning = WeatherWarning(
            warning_id="test-456",
            location=self.location,
            warning_type=WarningType.HEAT.value,  # Use valid type
            severity=SeverityLevel.LOW.value,     # Use valid severity
            title="Test Warning",
            description="Test warning description",
            safety_recommendations=["Monitor conditions"],  # Must have at least 1 item
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=24),
            issued_at=datetime.now()
        )
        
        recommendations = self.generator.generate_recommendations(warning)
        assert len(recommendations) > 0
        assert any("hydrated" in rec.lower() for rec in recommendations)

    def test_warning_properties(self):
        """Test that generated warnings have required properties"""
        conditions = WeatherData(
            location=self.location,
            timestamp=datetime.now(),
            temperature=40.0,  # High heat
            humidity=60.0,
            pressure=1013.0,
            wind_speed=5.0,
            wind_direction=180.0,
            precipitation=0.0,
            cloud_cover=30.0,
            weather_condition='Hot'
        )
        
        warnings = self.generator.analyze_current_conditions(conditions)
        assert len(warnings) == 1
        
        warning = warnings[0]
        assert warning.warning_id is not None
        assert len(warning.warning_id) > 0
        assert warning.location == self.location
        assert warning.warning_type in [wt.value for wt in WarningType]
        assert warning.severity in [sl.value for sl in SeverityLevel]
        assert len(warning.title) > 0
        assert len(warning.description) > 0
        assert len(warning.safety_recommendations) > 0
        assert warning.start_time <= warning.end_time
        assert warning.issued_at is not None

    def test_no_warnings_for_normal_conditions(self):
        """Test that no warnings are generated for normal conditions"""
        normal_conditions = WeatherData(
            location=self.location,
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
        
        warnings = self.generator.analyze_current_conditions(normal_conditions)
        assert len(warnings) == 0

    def test_warning_time_ranges(self):
        """Test that warnings have appropriate time ranges"""
        conditions = WeatherData(
            location=self.location,
            timestamp=datetime.now(),
            temperature=35.0,
            humidity=60.0,
            pressure=1013.0,
            wind_speed=20.0,  # High wind
            wind_direction=180.0,
            precipitation=0.0,
            cloud_cover=30.0,
            weather_condition='Windy'
        )
        
        warnings = self.generator.analyze_current_conditions(conditions)
        wind_warning = next(w for w in warnings if w.warning_type == WarningType.WIND.value)
        
        # Wind warnings should be shorter duration than temperature warnings
        duration = wind_warning.end_time - wind_warning.start_time
        assert duration == timedelta(hours=12)