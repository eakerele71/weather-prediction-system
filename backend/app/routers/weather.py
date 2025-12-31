"""Weather and forecast API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
import httpx
from app.models import Forecast, WeatherData, Location, WeatherWarning
from app.services import (
    WeatherPredictor,
    WeatherDataCollector,
    WarningGenerator
)
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["weather"])

# Initialize services (in production, use dependency injection)
predictor = WeatherPredictor()
data_collector = WeatherDataCollector()
warning_generator = WarningGenerator()


async def geocode_city(city: str, country: Optional[str] = None) -> Optional[dict]:
    """Convert city name to coordinates using OpenWeather Geocoding API
    
    Args:
        city: City name
        country: Optional country code (e.g., 'US', 'UK')
        
    Returns:
        Dict with lat, lon, city, country or None if not found
    """
    if not settings.openweather_api_key:
        logger.warning("OpenWeather API key not configured")
        return None
    
    query = f"{city},{country}" if country else city
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": query,
        "limit": 1,
        "appid": settings.openweather_api_key
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return {
                    "lat": data[0]["lat"],
                    "lon": data[0]["lon"],
                    "city": data[0].get("name", city),
                    "country": data[0].get("country", country or "Unknown")
                }
            return None
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        return None


async def fetch_current_weather_from_api(lat: float, lon: float) -> Optional[dict]:
    """Fetch current weather from OpenWeather API
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Weather data dict or None
    """
    if not settings.openweather_api_key:
        return None
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.openweather_api_key,
        "units": "metric"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return None


async def fetch_forecast_from_api(lat: float, lon: float) -> Optional[dict]:
    """Fetch 5-day forecast from OpenWeather API
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Forecast data dict or None
    """
    if not settings.openweather_api_key:
        return None
    
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.openweather_api_key,
        "units": "metric"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Forecast API error: {e}")
        return None


def parse_forecast_data(api_data: dict, location: Location, days: int) -> List[Forecast]:
    """Parse OpenWeather forecast API response into Forecast objects
    
    Args:
        api_data: Raw API response
        location: Location object
        days: Number of days to return
        
    Returns:
        List of Forecast objects
    """
    forecasts = []
    daily_data = {}
    
    # Group forecast data by date
    for item in api_data.get("list", []):
        dt = datetime.fromtimestamp(item["dt"])
        date_key = dt.date()
        
        if date_key not in daily_data:
            daily_data[date_key] = {
                "temps": [],
                "conditions": [],
                "precipitation_probs": [],
                "timestamps": []
            }
        
        daily_data[date_key]["temps"].append(item["main"]["temp"])
        daily_data[date_key]["conditions"].append(item["weather"][0]["main"])
        daily_data[date_key]["precipitation_probs"].append(item.get("pop", 0))
        daily_data[date_key]["timestamps"].append(dt)
    
    # Create Forecast objects for each day
    for forecast_date in sorted(daily_data.keys())[:days]:
        day_data = daily_data[forecast_date]
        temps = day_data["temps"]
        conditions = day_data["conditions"]
        probs = day_data["precipitation_probs"]
        
        # Get most common condition
        most_common_condition = max(set(conditions), key=conditions.count)
        
        forecast = Forecast(
            location=location,
            forecast_date=forecast_date,
            predicted_temperature_high=max(temps),
            predicted_temperature_low=min(temps),
            precipitation_probability=sum(probs) / len(probs) if probs else 0,
            weather_condition=most_common_condition,
            confidence_score=0.85,  # Default confidence
            generated_at=datetime.now()
        )
        forecasts.append(forecast)
    
    return forecasts


@router.get("/forecast/{city}", response_model=List[Forecast])
async def get_forecast(
    city: str,
    country: Optional[str] = Query(None, description="Country name"),
    days: int = Query(7, ge=1, le=14, description="Number of days to forecast")
):
    """
    Get weather forecast for a location
    """
    try:
        # Geocode the city
        geo_data = await geocode_city(city, country)
        
        if geo_data:
            location = Location(
                latitude=geo_data["lat"],
                longitude=geo_data["lon"],
                city=geo_data["city"],
                country=geo_data["country"]
            )
            
            # Fetch real forecast from API
            api_data = await fetch_forecast_from_api(geo_data["lat"], geo_data["lon"])
            
            if api_data:
                forecasts = parse_forecast_data(api_data, location, days)
                if forecasts:
                    return forecasts
        
        # Fallback to predictor if API fails
        location = Location(
            latitude=0.0,
            longitude=0.0,
            city=city,
            country=country or "Unknown"
        )
        forecasts = predictor.predict(location, days=days)
        
        if not forecasts:
            raise HTTPException(status_code=404, detail=f"No forecast available for {city}")
        
        return forecasts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")


@router.get("/current/{city}", response_model=WeatherData)
async def get_current_weather(
    city: str,
    country: Optional[str] = Query(None, description="Country name")
):
    """
    Get current weather conditions for a location
    """
    try:
        # Geocode the city
        geo_data = await geocode_city(city, country)
        
        if geo_data:
            location = Location(
                latitude=geo_data["lat"],
                longitude=geo_data["lon"],
                city=geo_data["city"],
                country=geo_data["country"]
            )
            
            # Fetch real weather from API
            api_data = await fetch_current_weather_from_api(geo_data["lat"], geo_data["lon"])
            
            if api_data:
                main = api_data.get("main", {})
                wind = api_data.get("wind", {})
                clouds = api_data.get("clouds", {})
                weather = api_data.get("weather", [{}])[0]
                rain = api_data.get("rain", {})
                
                return WeatherData(
                    location=location,
                    timestamp=datetime.now(),
                    temperature=main.get("temp", 0),
                    humidity=main.get("humidity", 0),
                    pressure=main.get("pressure", 1013.25),
                    wind_speed=wind.get("speed", 0),
                    wind_direction=wind.get("deg", 0),
                    precipitation=rain.get("1h", 0),
                    cloud_cover=clouds.get("all", 0),
                    weather_condition=weather.get("main", "Unknown")
                )
        
        # Fallback to simulated data if API fails
        location = Location(
            latitude=0.0,
            longitude=0.0,
            city=city,
            country=country or "Unknown"
        )
        
        return WeatherData(
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
        
    except Exception as e:
        logger.error(f"Error fetching current weather: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching current weather: {str(e)}")


@router.get("/warnings/{city}", response_model=List[WeatherWarning])
async def get_weather_warnings(
    city: str,
    country: Optional[str] = Query(None, description="Country name")
):
    """
    Get active weather warnings for a location
    """
    try:
        # Geocode the city
        geo_data = await geocode_city(city, country)
        
        if geo_data:
            location = Location(
                latitude=geo_data["lat"],
                longitude=geo_data["lon"],
                city=geo_data["city"],
                country=geo_data["country"]
            )
        else:
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
        logger.error(f"Error fetching warnings: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching warnings: {str(e)}")


@router.get("/forecast/coordinates", response_model=List[Forecast])
async def get_forecast_by_coordinates(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    days: int = Query(7, ge=1, le=14, description="Number of days to forecast")
):
    """
    Get weather forecast by coordinates
    """
    try:
        location = Location(
            latitude=lat,
            longitude=lon,
            city="Unknown",
            country="Unknown"
        )
        
        # Fetch real forecast from API
        api_data = await fetch_forecast_from_api(lat, lon)
        
        if api_data:
            forecasts = parse_forecast_data(api_data, location, days)
            if forecasts:
                return forecasts
        
        # Fallback to predictor
        forecasts = predictor.predict(location, days=days)
        
        if not forecasts:
            raise HTTPException(status_code=404, detail="No forecast available for coordinates")
        
        return forecasts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")
