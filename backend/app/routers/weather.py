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
import pycountry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["weather"])

# Initialize services (in production, use dependency injection)
predictor = WeatherPredictor()
data_collector = WeatherDataCollector()
warning_generator = WarningGenerator()


def normalize_country_name(value: str) -> Optional[str]:
    if value is None:
        return None

    stripped = value.strip()
    if not stripped:
        return None

    lowered = stripped.lower()
    aliases = {
        "uk": "united kingdom",
        "u.k.": "united kingdom",
        "usa": "united states",
        "u.s.a.": "united states",
        "us": "united states",
        "u.s.": "united states",
        "uae": "united arab emirates",
    }

    lookup_value = aliases.get(lowered, stripped)

    try:
        country = pycountry.countries.lookup(lookup_value)
        return country.name
    except LookupError:
        return None


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
            
            # Handle 404 specifically
            if response.status_code == 404:
                logger.info(f"Location not found: {city}")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                location_data = data[0]
                
                # Validate that we have valid coordinates (real geographic location)
                lat = location_data.get("lat")
                lon = location_data.get("lon")
                
                if lat is None or lon is None:
                    logger.warning(f"Location '{city}' has no coordinates")
                    return None
                
                # Ensure coordinates are valid ranges
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    logger.warning(f"Invalid coordinates for '{city}': lat={lat}, lon={lon}")
                    return None
                
                return {
                    "lat": lat,
                    "lon": lon,
                    "city": location_data.get("name", city),
                    "country": location_data.get("country", country or "Unknown")
                }
            
            # Empty result array means location not found
            logger.info(f"No results found for location: {city}")
            return None
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during geocoding: {e.response.status_code} - {e}")
        return None
    except httpx.TimeoutException:
        logger.error(f"Timeout while geocoding: {city}")
        return None
    except Exception as e:
        logger.error(f"Geocoding error for '{city}': {e}")
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
            
            # Handle 404 specifically
            if response.status_code == 404:
                logger.warning(f"Weather not found for coordinates: {lat}, {lon}")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            # Validate response has coordinates (ensures it's real geographic data)
            if "coord" in data and "lat" in data["coord"] and "lon" in data["coord"]:
                return data
            else:
                logger.warning(f"Weather data missing coordinates for {lat}, {lon}")
                return None
                
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching weather: {e.response.status_code} - {e}")
        return None
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching weather for {lat}, {lon}")
        return None
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
        normalized_country = normalize_country_name(city)
        if not normalized_country:
            raise HTTPException(
                status_code=404,
                detail=f"Country not found: '{city}'. Please enter a valid country name."
            )

        # Geocode the city
        geo_data = await geocode_city(normalized_country)
        
        if not geo_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Weather location not found for country: '{normalized_country}'. Please enter a valid country name."
            )
        
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
        
        # Fallback to predictor if API fails (but location was valid)
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
        normalized_country = normalize_country_name(city)
        if not normalized_country:
            raise HTTPException(
                status_code=404,
                detail=f"Country not found: '{city}'. Please enter a valid country name."
            )

        # Geocode the country
        geo_data = await geocode_city(normalized_country)
        
        if not geo_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Weather location not found for country: '{normalized_country}'. Please enter a valid country name."
            )
        
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
        
        # API call failed but location was valid - return error
        raise HTTPException(
            status_code=503, 
            detail=f"Weather service temporarily unavailable for {city}. Please try again."
        )
        
    except HTTPException:
        raise
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
        normalized_country = normalize_country_name(city)
        if not normalized_country:
            raise HTTPException(
                status_code=404,
                detail=f"Country not found: '{city}'. Please enter a valid country name."
            )

        # Geocode the country
        geo_data = await geocode_city(normalized_country)
        
        if not geo_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Weather location not found for country: '{normalized_country}'. Please enter a valid country name."
            )
        
        location = Location(
            latitude=geo_data["lat"],
            longitude=geo_data["lon"],
            city=geo_data["city"],
            country=geo_data["country"]
        )
        
        # Get forecasts to analyze for warnings
        forecasts = predictor.predict(location, days=7)
        
        # Generate warnings from forecasts
        warnings = []
        for forecast in forecasts:
            forecast_warnings = warning_generator.analyze_forecast([forecast])
            warnings.extend(forecast_warnings)
        
        return warnings
        
    except HTTPException:
        raise
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


@router.get("/hourly/{city}")
async def get_hourly_forecast(
    city: str,
    country: Optional[str] = Query(None, description="Country name"),
    hours: int = Query(24, ge=1, le=48, description="Number of hours to forecast")
):
    """
    Get hourly weather forecast for a location (up to 48 hours)
    
    Args:
        city: City name
        country: Optional country name
        hours: Number of hours to return (1-48)
        
    Returns:
        List of hourly forecast data
    """
    try:
        normalized_country = normalize_country_name(city)
        if not normalized_country:
            raise HTTPException(
                status_code=404,
                detail=f"Country not found: '{city}'. Please enter a valid country name."
            )

        # Geocode the country
        geo_data = await geocode_city(normalized_country)
        
        if not geo_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Weather location not found for country: '{normalized_country}'. Please enter a valid country name."
            )
        
        location = Location(
            latitude=geo_data["lat"],
            longitude=geo_data["lon"],
            city=geo_data["city"],
            country=geo_data["country"]
        )
        
        # Fetch forecast data (contains 3-hour intervals for 5 days)
        api_data = await fetch_forecast_from_api(geo_data["lat"], geo_data["lon"])
        
        if not api_data or "list" not in api_data:
            raise HTTPException(status_code=500, detail="Failed to fetch hourly forecast")
        
        hourly_data = []
        now = datetime.now()
        
        for item in api_data.get("list", [])[:hours // 3 + 1]:  # API returns 3-hour intervals
            dt = datetime.fromtimestamp(item["dt"])
            
            # Skip past hours
            if dt < now:
                continue
            
            main = item.get("main", {})
            wind = item.get("wind", {})
            clouds = item.get("clouds", {})
            weather = item.get("weather", [{}])[0]
            rain = item.get("rain", {})
            
            hourly_item = {
                "datetime": dt.isoformat(),
                "timestamp": item["dt"],
                "temperature": main.get("temp", 0),
                "feels_like": main.get("feels_like", 0),
                "humidity": main.get("humidity", 0),
                "pressure": main.get("pressure", 1013),
                "wind_speed": wind.get("speed", 0),
                "wind_direction": wind.get("deg", 0),
                "wind_gust": wind.get("gust", 0),
                "clouds": clouds.get("all", 0),
                "precipitation_probability": item.get("pop", 0),
                "rain_volume": rain.get("3h", 0),
                "weather_condition": weather.get("main", "Unknown"),
                "weather_description": weather.get("description", ""),
                "weather_icon": weather.get("icon", "01d"),
                "visibility": item.get("visibility", 10000)
            }
            hourly_data.append(hourly_item)
            
            if len(hourly_data) >= hours // 3:
                break
        
        return {
            "location": location,
            "hourly": hourly_data,
            "timezone": api_data.get("city", {}).get("timezone", 0),
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching hourly forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching hourly forecast: {str(e)}")
