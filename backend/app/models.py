"""Core data models for the Weather Prediction System"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# Pydantic models for API validation and serialization

class Location(BaseModel):
    """Geographic location model"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    city: str = Field(..., min_length=1, max_length=255, description="City name")
    country: str = Field(..., min_length=1, max_length=100, description="Country name")

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 47.6062,
                "longitude": -122.3321,
                "city": "Seattle",
                "country": "United States"
            }
        }


class WeatherData(BaseModel):
    """Weather observation data model"""
    location: Location
    timestamp: datetime
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    pressure: float = Field(..., gt=0, description="Atmospheric pressure in hPa")
    wind_speed: float = Field(..., ge=0, description="Wind speed in m/s")
    wind_direction: float = Field(..., ge=0, le=360, description="Wind direction in degrees")
    precipitation: float = Field(..., ge=0, description="Precipitation in mm")
    cloud_cover: float = Field(..., ge=0, le=100, description="Cloud cover percentage")
    weather_condition: str = Field(..., min_length=1, max_length=100, description="Weather condition")

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        """Validate temperature is within reasonable range"""
        if v < -100 or v > 60:
            raise ValueError('Temperature must be between -100°C and 60°C')
        return v

    @field_validator('wind_speed')
    @classmethod
    def validate_wind_speed(cls, v):
        """Validate wind speed is within reasonable range"""
        if v > 150:  # Hurricane force winds
            raise ValueError('Wind speed must be less than 150 m/s')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "location": {
                    "latitude": 47.6062,
                    "longitude": -122.3321,
                    "city": "Seattle",
                    "country": "United States"
                },
                "timestamp": "2024-01-15T10:30:00Z",
                "temperature": 15.5,
                "humidity": 65,
                "pressure": 1013.25,
                "wind_speed": 5.2,
                "wind_direction": 180,
                "precipitation": 0.0,
                "cloud_cover": 40,
                "weather_condition": "Partly Cloudy"
            }
        }


class Forecast(BaseModel):
    """Weather forecast model"""
    location: Location
    forecast_date: date
    predicted_temperature_high: float = Field(..., description="Predicted high temperature in Celsius")
    predicted_temperature_low: float = Field(..., description="Predicted low temperature in Celsius")
    precipitation_probability: float = Field(..., ge=0, le=1, description="Precipitation probability 0-1")
    weather_condition: str = Field(..., min_length=1, max_length=100, description="Predicted weather condition")
    confidence_score: float = Field(..., ge=0, le=1, description="Prediction confidence 0-1")
    generated_at: datetime

    @field_validator('predicted_temperature_high', 'predicted_temperature_low')
    @classmethod
    def validate_temperatures(cls, v):
        """Validate forecast temperatures"""
        if v < -100 or v > 60:
            raise ValueError('Temperature must be between -100°C and 60°C')
        return v

    @model_validator(mode='after')
    def validate_high_greater_than_low(self):
        """Ensure high temperature is greater than low"""
        if self.predicted_temperature_high < self.predicted_temperature_low:
            raise ValueError('High temperature must be greater than or equal to low temperature')
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "location": {
                    "latitude": 47.6062,
                    "longitude": -122.3321,
                    "city": "Seattle",
                    "country": "United States"
                },
                "forecast_date": "2024-01-16",
                "predicted_temperature_high": 18.0,
                "predicted_temperature_low": 12.0,
                "precipitation_probability": 0.3,
                "weather_condition": "Partly Cloudy",
                "confidence_score": 0.85,
                "generated_at": "2024-01-15T10:30:00Z"
            }
        }


class AccuracyMetrics(BaseModel):
    """Prediction accuracy metrics model"""
    location: Optional[Location] = None
    overall_accuracy: float = Field(..., ge=0, le=1, description="Overall accuracy 0-1")
    temperature_mae: float = Field(..., ge=0, description="Mean Absolute Error for temperature")
    temperature_rmse: float = Field(..., ge=0, description="Root Mean Square Error for temperature")
    precipitation_accuracy: float = Field(..., ge=0, le=1, description="Precipitation accuracy 0-1")
    condition_accuracy: float = Field(..., ge=0, le=1, description="Weather condition accuracy 0-1")
    total_predictions: int = Field(..., ge=0, description="Total number of predictions evaluated")
    evaluation_period_days: int = Field(..., ge=1, description="Number of days evaluated")
    calculated_at: datetime = Field(default_factory=datetime.now, description="When metrics were calculated")

    class Config:
        json_schema_extra = {
            "example": {
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "city": "New York",
                    "country": "USA"
                },
                "overall_accuracy": 0.82,
                "temperature_mae": 2.5,
                "temperature_rmse": 3.2,
                "precipitation_accuracy": 0.78,
                "condition_accuracy": 0.85,
                "total_predictions": 50,
                "evaluation_period_days": 7,
                "calculated_at": "2024-01-15T10:30:00"
            }
        }


class WeatherWarning(BaseModel):
    """Weather warning and alert model"""
    warning_id: str = Field(..., min_length=1, description="Unique warning identifier")
    location: Location
    warning_type: str = Field(..., description="Warning type: storm, heat, flood, wind, air_quality")
    severity: str = Field(..., description="Severity level: low, moderate, high, severe")
    title: str = Field(..., min_length=1, max_length=255, description="Warning title")
    description: str = Field(..., min_length=1, description="Warning description")
    safety_recommendations: List[str] = Field(..., min_length=1, description="Safety recommendations")
    start_time: datetime
    end_time: datetime
    issued_at: datetime

    @model_validator(mode='after')
    def validate_end_time(self):
        """Ensure end time is after start time"""
        if self.end_time <= self.start_time:
            raise ValueError('End time must be after start time')
        return self

    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        """Validate severity level"""
        valid_severities = {'low', 'moderate', 'high', 'severe'}
        if v not in valid_severities:
            raise ValueError(f'Severity must be one of {valid_severities}')
        return v

    @field_validator('warning_type')
    @classmethod
    def validate_warning_type(cls, v):
        """Validate warning type"""
        valid_types = {'storm', 'heat', 'flood', 'wind', 'air_quality'}
        if v not in valid_types:
            raise ValueError(f'Warning type must be one of {valid_types}')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "warning_id": "WARN-2024-01-15-001",
                "location": {
                    "latitude": 47.6062,
                    "longitude": -122.3321,
                    "city": "Seattle",
                    "country": "United States"
                },
                "warning_type": "storm",
                "severity": "high",
                "title": "Severe Thunderstorm Warning",
                "description": "Severe thunderstorms expected with heavy rain and strong winds",
                "safety_recommendations": [
                    "Stay indoors",
                    "Avoid driving",
                    "Keep emergency supplies ready"
                ],
                "start_time": "2024-01-15T14:00:00Z",
                "end_time": "2024-01-15T20:00:00Z",
                "issued_at": "2024-01-15T13:30:00Z"
            }
        }


class UserLocation(BaseModel):
    """User favorite location model"""
    user_id: str = Field(..., min_length=1, description="User identifier")
    location: Location
    is_favorite: bool = Field(default=False, description="Whether location is marked as favorite")
    added_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "location": {
                    "latitude": 47.6062,
                    "longitude": -122.3321,
                    "city": "Seattle",
                    "country": "United States"
                },
                "is_favorite": True,
                "added_at": "2024-01-15T10:30:00Z"
            }
        }


class ChartData(BaseModel):
    """Chart data for frontend visualization"""
    labels: List[str] = Field(..., description="X-axis labels")
    datasets: List[dict] = Field(..., description="Data series for chart")

    class Config:
        json_schema_extra = {
            "example": {
                "labels": ["2024-01-15", "2024-01-16", "2024-01-17"],
                "datasets": [
                    {
                        "label": "Temperature",
                        "data": [15.5, 16.2, 14.8],
                        "color": "#0066CC"
                    }
                ]
            }
        }
