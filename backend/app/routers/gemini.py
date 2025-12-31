"""Gemini LLM integration API endpoints"""
from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from pydantic import BaseModel
from app.models import Location, WeatherData, Forecast
from app.services import GeminiClient, WeatherContext, WeatherPredictor

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
        # Create location
        location = Location(
            latitude=0.0,
            longitude=0.0,
            city=request.city,
            country=request.country or "Unknown"
        )
        
        # Get current weather (simulated)
        current_weather = WeatherData(
            location=location,
            timestamp=__import__('datetime').datetime.now(),
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
            "generated_at": __import__('datetime').datetime.now()
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
            location = Location(
                latitude=0.0,
                longitude=0.0,
                city=request.city,
                country=request.country or "Unknown"
            )
            context.location = location
            
            # Get current weather
            current_weather = WeatherData(
                location=location,
                timestamp=__import__('datetime').datetime.now(),
                temperature=15.0,
                humidity=65.0,
                pressure=1013.25,
                wind_speed=5.0,
                wind_direction=180.0,
                precipitation=0.0,
                cloud_cover=40.0,
                weather_condition="Partly Cloudy"
            )
            context.current_weather = current_weather
            
            # Get forecasts
            forecasts = predictor.predict(location, days=7)
            context.forecasts = forecasts
        
        # Get answer
        answer = gemini_client.answer_question(request.question, context)
        
        return {
            "question": request.question,
            "answer": answer,
            "context_provided": bool(request.city),
            "generated_at": __import__('datetime').datetime.now()
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
        # Create location
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
            "generated_at": __import__('datetime').datetime.now()
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
