"""Weather warning system for generating safety alerts and recommendations"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum
from app.models import WeatherData, Forecast, WeatherWarning, Location

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Warning severity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class WarningType(Enum):
    """Types of weather warnings"""
    STORM = "storm"
    HEAT = "heat"
    FLOOD = "flood"
    WIND = "wind"
    AIR_QUALITY = "air_quality"


class SeverityClassifier:
    """Classifies weather conditions by severity level"""
    
    def __init__(self):
        """Initialize severity thresholds"""
        # Temperature thresholds (Celsius)
        self.heat_thresholds = {
            SeverityLevel.LOW: 30.0,
            SeverityLevel.MODERATE: 35.0,
            SeverityLevel.HIGH: 40.0,
            SeverityLevel.SEVERE: 45.0
        }
        
        self.cold_thresholds = {
            SeverityLevel.LOW: 0.0,
            SeverityLevel.MODERATE: -10.0,
            SeverityLevel.HIGH: -20.0,
            SeverityLevel.SEVERE: -30.0
        }
        
        # Wind speed thresholds (m/s)
        self.wind_thresholds = {
            SeverityLevel.LOW: 10.0,      # 36 km/h
            SeverityLevel.MODERATE: 15.0,  # 54 km/h
            SeverityLevel.HIGH: 20.0,      # 72 km/h
            SeverityLevel.SEVERE: 25.0     # 90 km/h
        }
        
        # Precipitation thresholds (mm)
        self.precipitation_thresholds = {
            SeverityLevel.LOW: 10.0,
            SeverityLevel.MODERATE: 25.0,
            SeverityLevel.HIGH: 50.0,
            SeverityLevel.SEVERE: 100.0
        }

    def classify_temperature_severity(self, temperature: float) -> Optional[SeverityLevel]:
        """Classify temperature-based severity
        
        Args:
            temperature: Temperature in Celsius
            
        Returns:
            SeverityLevel or None if no warning needed
        """
        # Check for heat warnings
        if temperature >= self.heat_thresholds[SeverityLevel.SEVERE]:
            return SeverityLevel.SEVERE
        elif temperature >= self.heat_thresholds[SeverityLevel.HIGH]:
            return SeverityLevel.HIGH
        elif temperature >= self.heat_thresholds[SeverityLevel.MODERATE]:
            return SeverityLevel.MODERATE
        elif temperature >= self.heat_thresholds[SeverityLevel.LOW]:
            return SeverityLevel.LOW
        
        # Check for cold warnings
        elif temperature <= self.cold_thresholds[SeverityLevel.SEVERE]:
            return SeverityLevel.SEVERE
        elif temperature <= self.cold_thresholds[SeverityLevel.HIGH]:
            return SeverityLevel.HIGH
        elif temperature <= self.cold_thresholds[SeverityLevel.MODERATE]:
            return SeverityLevel.MODERATE
        elif temperature <= self.cold_thresholds[SeverityLevel.LOW]:
            return SeverityLevel.LOW
        
        return None

    def classify_wind_severity(self, wind_speed: float) -> Optional[SeverityLevel]:
        """Classify wind-based severity
        
        Args:
            wind_speed: Wind speed in m/s
            
        Returns:
            SeverityLevel or None if no warning needed
        """
        if wind_speed >= self.wind_thresholds[SeverityLevel.SEVERE]:
            return SeverityLevel.SEVERE
        elif wind_speed >= self.wind_thresholds[SeverityLevel.HIGH]:
            return SeverityLevel.HIGH
        elif wind_speed >= self.wind_thresholds[SeverityLevel.MODERATE]:
            return SeverityLevel.MODERATE
        elif wind_speed >= self.wind_thresholds[SeverityLevel.LOW]:
            return SeverityLevel.LOW
        
        return None

    def classify_precipitation_severity(self, precipitation: float) -> Optional[SeverityLevel]:
        """Classify precipitation-based severity
        
        Args:
            precipitation: Precipitation in mm
            
        Returns:
            SeverityLevel or None if no warning needed
        """
        if precipitation >= self.precipitation_thresholds[SeverityLevel.SEVERE]:
            return SeverityLevel.SEVERE
        elif precipitation >= self.precipitation_thresholds[SeverityLevel.HIGH]:
            return SeverityLevel.HIGH
        elif precipitation >= self.precipitation_thresholds[SeverityLevel.MODERATE]:
            return SeverityLevel.MODERATE
        elif precipitation >= self.precipitation_thresholds[SeverityLevel.LOW]:
            return SeverityLevel.LOW
        
        return None

    def classify_overall_severity(self, conditions: WeatherData) -> SeverityLevel:
        """Classify overall severity based on all weather conditions
        
        Args:
            conditions: Current weather conditions
            
        Returns:
            Highest severity level found across all conditions
        """
        severities = []
        
        # Check temperature severity
        temp_severity = self.classify_temperature_severity(conditions.temperature)
        if temp_severity:
            severities.append(temp_severity)
        
        # Check wind severity
        wind_severity = self.classify_wind_severity(conditions.wind_speed)
        if wind_severity:
            severities.append(wind_severity)
        
        # Check precipitation severity
        precip_severity = self.classify_precipitation_severity(conditions.precipitation)
        if precip_severity:
            severities.append(precip_severity)
        
        # Return highest severity, default to LOW if any conditions warrant warnings
        if not severities:
            return SeverityLevel.LOW
        
        # Order by severity (SEVERE > HIGH > MODERATE > LOW)
        severity_order = [SeverityLevel.SEVERE, SeverityLevel.HIGH, SeverityLevel.MODERATE, SeverityLevel.LOW]
        for severity in severity_order:
            if severity in severities:
                return severity
        
        return SeverityLevel.LOW


class SafetyRecommendations:
    """Generates safety recommendations based on warning type and severity"""
    
    def __init__(self):
        """Initialize safety recommendation templates"""
        self.recommendations = {
            WarningType.HEAT: {
                SeverityLevel.LOW: [
                    "Stay hydrated by drinking plenty of water",
                    "Avoid prolonged outdoor activities during peak hours",
                    "Wear light-colored, loose-fitting clothing"
                ],
                SeverityLevel.MODERATE: [
                    "Limit outdoor activities to early morning or evening",
                    "Drink water regularly, even if not thirsty",
                    "Seek air-conditioned spaces during the hottest part of the day",
                    "Check on elderly neighbors and relatives"
                ],
                SeverityLevel.HIGH: [
                    "Avoid outdoor activities during daytime hours",
                    "Stay in air-conditioned buildings when possible",
                    "Never leave children or pets in vehicles",
                    "Watch for signs of heat exhaustion and heat stroke",
                    "Drink water every 15-20 minutes"
                ],
                SeverityLevel.SEVERE: [
                    "Stay indoors in air-conditioned spaces",
                    "Avoid all non-essential outdoor activities",
                    "Seek immediate medical attention for heat-related illness",
                    "Check on vulnerable community members frequently",
                    "Consider relocating to cooling centers if needed"
                ]
            },
            WarningType.WIND: {
                SeverityLevel.LOW: [
                    "Secure loose outdoor objects",
                    "Be cautious when driving high-profile vehicles",
                    "Avoid outdoor activities involving heights"
                ],
                SeverityLevel.MODERATE: [
                    "Secure or bring indoors all loose outdoor items",
                    "Avoid driving high-profile vehicles if possible",
                    "Stay away from trees and power lines",
                    "Postpone outdoor recreational activities"
                ],
                SeverityLevel.HIGH: [
                    "Avoid unnecessary travel",
                    "Stay indoors and away from windows",
                    "Secure outdoor furniture and decorations",
                    "Be prepared for possible power outages",
                    "Avoid areas with trees and power lines"
                ],
                SeverityLevel.SEVERE: [
                    "Stay indoors and avoid travel",
                    "Move to interior rooms away from windows",
                    "Have emergency supplies ready",
                    "Expect widespread power outages",
                    "Avoid areas with trees, power lines, and large structures"
                ]
            },
            WarningType.FLOOD: {
                SeverityLevel.LOW: [
                    "Avoid low-lying areas and underpasses",
                    "Monitor local weather updates",
                    "Prepare emergency supplies"
                ],
                SeverityLevel.MODERATE: [
                    "Avoid driving through flooded roads",
                    "Move to higher ground if in flood-prone areas",
                    "Have evacuation plan ready",
                    "Monitor emergency broadcasts"
                ],
                SeverityLevel.HIGH: [
                    "Evacuate flood-prone areas immediately",
                    "Never drive through flooded roads",
                    "Move to higher floors or higher ground",
                    "Have emergency supplies and communication ready",
                    "Follow evacuation orders from authorities"
                ],
                SeverityLevel.SEVERE: [
                    "Evacuate immediately if ordered by authorities",
                    "Move to highest available ground",
                    "Avoid all flooded areas",
                    "Have emergency communication and supplies",
                    "Do not return to evacuated areas until cleared by officials"
                ]
            },
            WarningType.STORM: {
                SeverityLevel.LOW: [
                    "Secure loose outdoor objects",
                    "Avoid outdoor activities",
                    "Monitor weather updates"
                ],
                SeverityLevel.MODERATE: [
                    "Stay indoors during the storm",
                    "Avoid using electrical appliances",
                    "Stay away from windows and doors",
                    "Have flashlights and batteries ready"
                ],
                SeverityLevel.HIGH: [
                    "Stay indoors in interior rooms",
                    "Avoid windows and electrical equipment",
                    "Have emergency supplies ready",
                    "Be prepared for power outages",
                    "Avoid travel during the storm"
                ],
                SeverityLevel.SEVERE: [
                    "Take shelter in interior rooms on lowest floor",
                    "Stay away from windows, doors, and electrical equipment",
                    "Have emergency supplies and communication ready",
                    "Expect extended power outages",
                    "Follow emergency broadcasts and evacuation orders"
                ]
            }
        }

    def get_recommendations(self, warning_type: WarningType, severity: SeverityLevel) -> List[str]:
        """Get safety recommendations for a specific warning type and severity
        
        Args:
            warning_type: Type of weather warning
            severity: Severity level of the warning
            
        Returns:
            List of safety recommendations
        """
        return self.recommendations.get(warning_type, {}).get(severity, [
            "Monitor weather conditions closely",
            "Follow guidance from local authorities",
            "Have emergency supplies ready"
        ])


class WarningGenerator:
    """Generates weather warnings based on forecasts and current conditions"""
    
    def __init__(self):
        """Initialize warning generator with classifier and recommendations"""
        self.severity_classifier = SeverityClassifier()
        self.safety_recommendations = SafetyRecommendations()

    def analyze_forecast(self, forecast: Forecast) -> List[WeatherWarning]:
        """Analyze forecast and generate appropriate warnings
        
        Args:
            forecast: Weather forecast to analyze
            
        Returns:
            List of weather warnings
        """
        warnings = []
        
        # Check temperature warnings
        temp_warnings = self._check_temperature_warnings(forecast)
        warnings.extend(temp_warnings)
        
        # Check precipitation warnings
        precip_warnings = self._check_precipitation_warnings(forecast)
        warnings.extend(precip_warnings)
        
        return warnings

    def analyze_current_conditions(self, conditions: WeatherData) -> List[WeatherWarning]:
        """Analyze current weather conditions and generate warnings
        
        Args:
            conditions: Current weather conditions
            
        Returns:
            List of weather warnings
        """
        warnings = []
        
        # Check temperature warnings
        temp_severity = self.severity_classifier.classify_temperature_severity(conditions.temperature)
        if temp_severity:
            # Only create heat warnings (cold warnings not supported by model)
            if conditions.temperature > 25:  # Heat warning
                warning = self._create_temperature_warning(
                    conditions.location, conditions.temperature, temp_severity, WarningType.HEAT
                )
                warnings.append(warning)
        
        # Check wind warnings
        wind_severity = self.severity_classifier.classify_wind_severity(conditions.wind_speed)
        if wind_severity:
            warning = self._create_wind_warning(conditions.location, conditions.wind_speed, wind_severity)
            warnings.append(warning)
        
        # Check precipitation warnings
        precip_severity = self.severity_classifier.classify_precipitation_severity(conditions.precipitation)
        if precip_severity:
            warning = self._create_precipitation_warning(
                conditions.location, conditions.precipitation, precip_severity
            )
            warnings.append(warning)
        
        return warnings

    def _check_temperature_warnings(self, forecast: Forecast) -> List[WeatherWarning]:
        """Check for temperature-based warnings in forecast
        
        Args:
            forecast: Weather forecast
            
        Returns:
            List of temperature warnings
        """
        warnings = []
        
        # Check high temperature
        high_severity = self.severity_classifier.classify_temperature_severity(forecast.predicted_temperature_high)
        if high_severity and forecast.predicted_temperature_high > 25:
            warning = self._create_temperature_warning(
                forecast.location, forecast.predicted_temperature_high, high_severity, WarningType.HEAT
            )
            warnings.append(warning)
        
        # Note: Cold warnings not supported by model, only heat warnings
        
        return warnings

    def _check_precipitation_warnings(self, forecast: Forecast) -> List[WeatherWarning]:
        """Check for precipitation-based warnings in forecast
        
        Args:
            forecast: Weather forecast
            
        Returns:
            List of precipitation warnings
        """
        warnings = []
        
        # Estimate precipitation amount from probability
        # This is a simplified calculation - in production, use actual precipitation forecasts
        estimated_precipitation = forecast.precipitation_probability * 50  # mm
        
        precip_severity = self.severity_classifier.classify_precipitation_severity(estimated_precipitation)
        if precip_severity:
            warning = self._create_precipitation_warning(
                forecast.location, estimated_precipitation, precip_severity
            )
            warnings.append(warning)
        
        return warnings

    def _create_temperature_warning(self, location: Location, temperature: float, 
                                  severity: SeverityLevel, warning_type: WarningType) -> WeatherWarning:
        """Create a temperature-based warning
        
        Args:
            location: Location for the warning
            temperature: Temperature value
            severity: Severity level
            warning_type: Type of temperature warning (HEAT or COLD)
            
        Returns:
            WeatherWarning object
        """
        warning_id = str(uuid.uuid4())
        now = datetime.now()
        
        if warning_type == WarningType.HEAT:
            title = f"{severity.value.title()} Heat Warning"
            description = f"High temperatures of {temperature:.1f}°C expected. Heat-related health risks possible."
        else:
            # Fallback for unsupported temperature warning types
            title = f"{severity.value.title()} Temperature Warning"
            description = f"Extreme temperatures of {temperature:.1f}°C expected. Weather-related health risks possible."
        
        recommendations = self.safety_recommendations.get_recommendations(warning_type, severity)
        
        return WeatherWarning(
            warning_id=warning_id,
            location=location,
            warning_type=warning_type.value,
            severity=severity.value,
            title=title,
            description=description,
            safety_recommendations=recommendations,
            start_time=now,
            end_time=now + timedelta(hours=24),
            issued_at=now
        )

    def _create_wind_warning(self, location: Location, wind_speed: float, 
                           severity: SeverityLevel) -> WeatherWarning:
        """Create a wind-based warning
        
        Args:
            location: Location for the warning
            wind_speed: Wind speed in m/s
            severity: Severity level
            
        Returns:
            WeatherWarning object
        """
        warning_id = str(uuid.uuid4())
        now = datetime.now()
        
        title = f"{severity.value.title()} Wind Warning"
        description = f"High winds of {wind_speed:.1f} m/s ({wind_speed * 3.6:.1f} km/h) expected. Travel and outdoor activities may be affected."
        
        recommendations = self.safety_recommendations.get_recommendations(WarningType.WIND, severity)
        
        return WeatherWarning(
            warning_id=warning_id,
            location=location,
            warning_type=WarningType.WIND.value,
            severity=severity.value,
            title=title,
            description=description,
            safety_recommendations=recommendations,
            start_time=now,
            end_time=now + timedelta(hours=12),
            issued_at=now
        )

    def _create_precipitation_warning(self, location: Location, precipitation: float, 
                                    severity: SeverityLevel) -> WeatherWarning:
        """Create a precipitation-based warning
        
        Args:
            location: Location for the warning
            precipitation: Precipitation amount in mm
            severity: Severity level
            
        Returns:
            WeatherWarning object
        """
        warning_id = str(uuid.uuid4())
        now = datetime.now()
        
        title = f"{severity.value.title()} Flood Warning"
        description = f"Heavy precipitation of {precipitation:.1f}mm expected. Flooding possible in low-lying areas."
        
        recommendations = self.safety_recommendations.get_recommendations(WarningType.FLOOD, severity)
        
        return WeatherWarning(
            warning_id=warning_id,
            location=location,
            warning_type=WarningType.FLOOD.value,
            severity=severity.value,
            title=title,
            description=description,
            safety_recommendations=recommendations,
            start_time=now,
            end_time=now + timedelta(hours=24),
            issued_at=now
        )

    def classify_severity(self, conditions: WeatherData) -> SeverityLevel:
        """Classify overall severity of weather conditions
        
        Args:
            conditions: Weather conditions to classify
            
        Returns:
            Overall severity level
        """
        return self.severity_classifier.classify_overall_severity(conditions)

    def generate_recommendations(self, warning: WeatherWarning) -> List[str]:
        """Generate safety recommendations for a warning
        
        Args:
            warning: Weather warning
            
        Returns:
            List of safety recommendations
        """
        try:
            warning_type = WarningType(warning.warning_type)
            severity = SeverityLevel(warning.severity)
            return self.safety_recommendations.get_recommendations(warning_type, severity)
        except ValueError:
            # Fallback for unknown warning types or severities
            return [
                "Monitor weather conditions closely",
                "Follow guidance from local authorities",
                "Have emergency supplies ready"
            ]