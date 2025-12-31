"""Gemini LLM integration API endpoints"""
from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import httpx
from app.models import Location, WeatherData, Forecast
from app.services import GeminiClient, WeatherContext, WeatherPredictor
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/gemini", tags=["gemini"])

# Initialize services
gemini_client = GeminiClient()
predictor = WeatherPredictor()


class ExplainRequest(BaseModel):
    """Request model for weather explanation"""
    city: str
    country: Optional[str] = None


class ChatRequest(BaseModel):
    """Request model for chat/question answering"""
    question: str
    city: Optional[str] = None
    country: Optional[str] = None


async def get_real_weather_data(city: str, country: Optional[str] = None) -> tuple[Optional[Location], Optional[WeatherData]]:
    """Fetch real weather data for a city
    
    Returns:
        Tuple of (Location, WeatherData) or (None, None) if failed
    """
    if not settings.openweather_api_key:
        return None, None
    
    try:
        # Geocode city
        query = f"{city},{country}" if country else city
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {"q": query, "limit": 1, "appid": settings.openweather_api_key}
        
        async with httpx.AsyncClient(timeout=10) as client:
            geo_response = await client.get(geo_url, params=geo_params)
            geo_data = geo_response.json()
            
            if not geo_data:
                return None, None
            
            lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
            location = Location(
                latitude=lat,
                longitude=lon,
                city=geo_data[0].get("name", city),
                country=geo_data[0].get("country", country or "Unknown")
            )
            
            # Fetch weather
            weather_url = "https://api.openweathermap.org/data/2.5/weather"
            weather_params = {"lat": lat, "lon": lon, "appid": settings.openweather_api_key, "units": "metric"}
            
            weather_response = await client.get(weather_url, params=weather_params)
            api_data = weather_response.json()
            
            main = api_data.get("main", {})
            wind = api_data.get("wind", {})
            clouds = api_data.get("clouds", {})
            weather = api_data.get("weather", [{}])[0]
            rain = api_data.get("rain", {})
            
            weather_data = WeatherData(
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
            
            return location, weather_data
            
    except Exception as e:
        logger.error(f"Error fetching real weather data: {e}")
        return None, None


@router.post("/explain")
async def explain_weather(request: ExplainRequest):
    """
    Get natural language explanation of weather patterns
    
    Args:
        request: Explanation request with location
        
    Returns:
        Natural language weather explanation
    """
    try:
        # Try to get real weather data
        location, current_weather = await get_real_weather_data(request.city, request.country)
        
        if not location or not current_weather:
            # Fallback to simulated data
            location = Location(
                latitude=0.0,
                longitude=0.0,
                city=request.city,
                country=request.country or "Unknown"
            )
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
        
        # Get forecast
        forecasts = predictor.predict(location, days=7)
        
        if not forecasts:
            raise HTTPException(status_code=404, detail="No forecast available")
        
        # Generate explanation
        explanation = gemini_client.explain_weather_pattern(
            current_weather,
            forecasts[0]
        )
        
        return {
            "location": location,
            "explanation": explanation,
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")


@router.post("/chat")
async def chat_with_gemini(request: ChatRequest):
    """
    Ask questions about weather using natural language
    
    Args:
        request: Chat request with question and optional location
        
    Returns:
        Natural language answer
    """
    try:
        # Build context
        context = WeatherContext()
        
        if request.city:
            # Try to get real weather data
            location, current_weather = await get_real_weather_data(request.city, request.country)
            
            if location and current_weather:
                context.location = location
                context.current_weather = current_weather
            else:
                # Fallback
                location = Location(
                    latitude=0.0,
                    longitude=0.0,
                    city=request.city,
                    country=request.country or "Unknown"
                )
                context.location = location
                context.current_weather = WeatherData(
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
            
            # Get forecasts
            forecasts = predictor.predict(context.location, days=7)
            context.forecasts = forecasts
        
        # Get answer
        answer = gemini_client.answer_question(request.question, context)
        
        return {
            "question": request.question,
            "answer": answer,
            "context_provided": bool(request.city),
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.get("/summary/{city}")
async def get_forecast_summary(
    city: str,
    country: Optional[str] = None
):
    """
    Get natural language forecast summary
    
    Args:
        city: City name
        country: Optional country name
        
    Returns:
        Natural language forecast summary
    """
    try:
        # Try to get real location
        location, _ = await get_real_weather_data(city, country)
        
        if not location:
            location = Location(
                latitude=0.0,
                longitude=0.0,
                city=city,
                country=country or "Unknown"
            )
        
        # Get forecasts
        forecasts = predictor.predict(location, days=7)
        
        if not forecasts:
            raise HTTPException(status_code=404, detail=f"No forecast available for {city}")
        
        # Generate summary
        summary = gemini_client.generate_forecast_summary(forecasts)
        
        return {
            "location": location,
            "summary": summary,
            "forecast_days": len(forecasts),
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@router.get("/status")
async def get_gemini_status():
    """
    Get Gemini integration status
    
    Returns:
        Status information about Gemini client
    """
    try:
        info = gemini_client.get_client_info()
        rate_limit_status = gemini_client.handle_rate_limit()
        
        return {
            "client_info": info,
            "rate_limit": rate_limit_status,
            "status": "operational" if info['api_key_configured'] else "limited"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")
