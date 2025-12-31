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


class ExplainDayRequest(BaseModel):
    """Request model for day-specific prediction explanation"""
    city: str
    date: str
    condition: str
    temp_high: float
    temp_low: float
    precipitation_probability: float
    confidence_score: float = 0.85
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


@router.post("/explain-day")
async def explain_day_prediction(request: ExplainDayRequest):
    """
    Get AI-generated explanation for a specific day's weather prediction
    
    Args:
        request: Day prediction details
        
    Returns:
        Natural language explanation of why this prediction was made
    """
    try:
        # Build a detailed prompt for the day's prediction
        prompt = f"""Explain the weather prediction for {request.city} on {request.date}.

Predicted Conditions:
- Weather: {request.condition}
- High Temperature: {request.temp_high:.1f}°C
- Low Temperature: {request.temp_low:.1f}°C
- Precipitation Probability: {request.precipitation_probability * 100:.0f}%
- Prediction Confidence: {request.confidence_score * 100:.0f}%

Please provide a detailed but easy-to-understand explanation that covers:

1. **Why this weather is predicted**: Explain the meteorological factors (pressure systems, fronts, seasonal patterns) that typically cause these conditions.

2. **Temperature Analysis**: Why the high and low temperatures are expected at these levels, and what factors influence the daily temperature range.

3. **Precipitation Assessment**: What atmospheric conditions lead to the predicted precipitation probability.

4. **Practical Advice**: What activities are suitable for this weather, and any precautions to take.

5. **Confidence Explanation**: What factors affect the prediction confidence level.

Keep the explanation informative but accessible to non-meteorologists. Use clear, friendly language."""

        # Try to call Gemini API
        try:
            import google.generativeai as genai
            
            if settings.gemini_api_key:
                genai.configure(api_key=settings.gemini_api_key)
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                
                if response.text:
                    # Clean up the response
                    explanation = response.text.strip()
                    explanation = explanation.replace('**', '').replace('*', '')
                    
                    return {
                        "city": request.city,
                        "date": request.date,
                        "explanation": explanation,
                        "generated_at": datetime.now()
                    }
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
        
        # Fallback explanation if API fails
        explanation = generate_fallback_day_explanation(request)
        
        return {
            "city": request.city,
            "date": request.date,
            "explanation": explanation,
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error generating day explanation: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")


def generate_fallback_day_explanation(request: ExplainDayRequest) -> str:
    """Generate a fallback explanation when Gemini API is unavailable"""
    
    condition = request.condition.lower()
    temp_high = request.temp_high
    temp_low = request.temp_low
    precip_prob = request.precipitation_probability * 100
    confidence = request.confidence_score * 100
    temp_range = temp_high - temp_low
    
    explanation = f"Weather Prediction Analysis for {request.city}\n\n"
    
    # Condition explanation
    explanation += "Why This Weather Is Predicted:\n"
    if 'clear' in condition or 'sunny' in condition:
        explanation += "Clear skies are typically associated with high-pressure systems dominating the region. These systems suppress cloud formation and create stable atmospheric conditions.\n\n"
    elif 'cloud' in condition:
        explanation += "Cloudy conditions often occur when moisture-laden air masses move into the area. Mid-level clouds form as air rises and cools, though not enough to produce significant precipitation.\n\n"
    elif 'rain' in condition or 'drizzle' in condition:
        explanation += "Rainy conditions are predicted due to an approaching low-pressure system or frontal boundary. As warm, moist air rises over cooler air, it condenses and forms precipitation.\n\n"
    elif 'storm' in condition or 'thunder' in condition:
        explanation += "Stormy conditions develop when there's significant atmospheric instability. Warm, humid air rises rapidly, creating towering clouds capable of producing thunder, lightning, and heavy rain.\n\n"
    elif 'snow' in condition:
        explanation += "Snow is expected as temperatures remain below freezing while moisture moves through the area. Precipitation forms as ice crystals in the clouds and falls as snow.\n\n"
    else:
        explanation += f"The predicted {condition} conditions are based on current atmospheric patterns and historical weather data for this region and time of year.\n\n"
    
    # Temperature analysis
    explanation += "Temperature Analysis:\n"
    if temp_high > 30:
        explanation += f"The high of {temp_high:.0f}°C indicates warm conditions, likely due to strong solar heating and warm air mass influence. "
    elif temp_high > 20:
        explanation += f"The high of {temp_high:.0f}°C represents comfortable temperatures typical for this season. "
    elif temp_high > 10:
        explanation += f"The high of {temp_high:.0f}°C suggests mild conditions with moderate solar heating. "
    else:
        explanation += f"The high of {temp_high:.0f}°C indicates cool conditions, possibly due to cold air mass influence. "
    
    if temp_range > 15:
        explanation += f"The large temperature swing of {temp_range:.0f}°C suggests clear skies allowing significant nighttime cooling.\n\n"
    elif temp_range > 8:
        explanation += f"The moderate temperature range of {temp_range:.0f}°C is typical for partly cloudy conditions.\n\n"
    else:
        explanation += f"The small temperature variation of {temp_range:.0f}°C suggests cloud cover limiting both daytime heating and nighttime cooling.\n\n"
    
    # Precipitation assessment
    explanation += "Precipitation Assessment:\n"
    if precip_prob > 70:
        explanation += f"The high precipitation probability ({precip_prob:.0f}%) indicates strong confidence in wet weather. An active weather system is likely moving through the area.\n\n"
    elif precip_prob > 40:
        explanation += f"The moderate precipitation chance ({precip_prob:.0f}%) suggests some atmospheric instability. Scattered showers are possible, especially during peak heating hours.\n\n"
    elif precip_prob > 20:
        explanation += f"The low precipitation probability ({precip_prob:.0f}%) indicates mostly dry conditions, though isolated light showers cannot be ruled out.\n\n"
    else:
        explanation += f"The very low precipitation chance ({precip_prob:.0f}%) suggests stable, dry atmospheric conditions with minimal moisture available.\n\n"
    
    # Practical advice
    explanation += "Practical Advice:\n"
    if precip_prob > 50:
        explanation += "Carry an umbrella or rain jacket. Consider indoor alternatives for outdoor plans. "
    if temp_high > 30:
        explanation += "Stay hydrated and seek shade during peak sun hours. Wear light, breathable clothing. "
    elif temp_low < 5:
        explanation += "Dress warmly in layers, especially for morning and evening activities. "
    if 'storm' in condition:
        explanation += "Avoid outdoor activities during storms. Stay away from tall objects and open areas. "
    explanation += "\n\n"
    
    # Confidence explanation
    explanation += "Prediction Confidence:\n"
    if confidence >= 80:
        explanation += f"The high confidence level ({confidence:.0f}%) indicates stable atmospheric patterns that are well-understood and predictable. The forecast is highly reliable."
    elif confidence >= 60:
        explanation += f"The moderate confidence level ({confidence:.0f}%) reflects some uncertainty in the atmospheric setup. While the general trend is reliable, specific timing and intensity may vary."
    else:
        explanation += f"The lower confidence level ({confidence:.0f}%) suggests a complex weather pattern with multiple possible outcomes. Check for forecast updates closer to the date."
    
    return explanation


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
