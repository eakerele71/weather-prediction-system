"""Weather and forecast API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from app.models import Forecast, WeatherData, Location, WeatherWarning
from app.services import (
    WeatherPredictor,
    WeatherDataCollector,
    WarningGenerator
)

router = APIRouter(prefix="/api/v1", tags=["weather"])

# Initialize services (in production, use dependency injection)
predictor = WeatherPredictor()
data_collector = WeatherDataCollector()
warning_generator = WarningGenerator()


@router.get("/forecast/{city}", response_model=List[Forecast])
async def get_forecast(
    city: str,
    country: Optional[str] = Query(None, description="Country name"),
    days: int = Query(7, ge=1, le=14, description="Number of days to forecast")
):
    """
    Get weather forecast for a location
    
    Args:
        city: City name
        country: Optional country name
        days: Number of days to forecast (1-14)
        
    Returns:
        List of forecast objects
    """
    try:
        # Create location (in production, geocode the city name)
        location = Location(
            latitude=0.0,  # Placeholder - would geocode in production
            longitude=0.0,
            city=city,
            country=country or "Unknown"
        )
        
        # Generate forecast
        forecasts = predictor.predict(location, days=days)
        
        if not forecasts:
            raise HTTPException(status_code=404, detail=f"No forecast available for {city}")
        
        return forecasts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")


@router.get("/current/{city}", response_model=WeatherData)
async def get_current_weather(
    city: str,
    country: Optional[str] = Query(None, description="Country name")
):
    """
    Get current weather conditions for a location
    
    Args:
        city: City name
        country: Optional country name
        
    Returns:
        Current weather data
    """
    try:
        # Create location
        location = Location(
            latitude=0.0,  # Placeholder
            longitude=0.0,
            city=city,
            country=country or "Unknown"
        )
        
        # Fetch current weather (simulated for now)
        # In production, this would call data_collector.fetch_weather_data(location)
        current_weather = WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=15.0,
            humidity=65.0,
            pressure=1013.25,
            wind_speed=5.0,
            wind_direction=180.0,
            precipitation=0.0,
            cloud_cover=40.0,
            weather_condition="Partly Cloudy"
        )
        
        return current_weather
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching current weather: {str(e)}")


@router.get("/warnings/{city}", response_model=List[WeatherWarning])
async def get_weather_warnings(
    city: str,
    country: Optional[str] = Query(None, description="Country name")
):
    """
    Get active weather warnings for a location
    
    Args:
        city: City name
        country: Optional country name
        
    Returns:
        List of active weather warnings
    """
    try:
        # Create location
        location = Location(
            latitude=0.0,
            longitude=0.0,
            city=city,
            country=country or "Unknown"
        )
        
        # Get forecasts to analyze for warnings
        forecasts = predictor.predict(location, days=7)
        
        # Generate warnings from forecasts
        warnings = []
        for forecast in forecasts:
            forecast_warnings = warning_generator.analyze_forecast([forecast])
            warnings.extend(forecast_warnings)
        
        return warnings
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching warnings: {str(e)}")


@router.get("/forecast/coordinates", response_model=List[Forecast])
async def get_forecast_by_coordinates(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    days: int = Query(7, ge=1, le=14, description="Number of days to forecast")
):
    """
    Get weather forecast by coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        days: Number of days to forecast
        
    Returns:
        List of forecast objects
    """
    try:
        # Create location
        location = Location(
            latitude=lat,
            longitude=lon,
            city="Unknown",  # Would reverse geocode in production
            country="Unknown"
        )
        
        # Generate forecast
        forecasts = predictor.predict(location, days=days)
        
        if not forecasts:
            raise HTTPException(status_code=404, detail="No forecast available for coordinates")
        
        return forecasts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")
